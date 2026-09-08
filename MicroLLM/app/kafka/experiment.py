# app/kafka/experiment.py
"""
Experimento RAG del TFG: barrido de 4 funciones de similitud x 6 valores
de top-k (24 condiciones) sobre las 25 preguntas de app/kafka/eval_dataset.py.

COMO FUNCIONA (resumen):
  1) Carga el corpus de articulos desde CORPUS_DIR (carpeta "Artificial
     intelligence"), descartando los que tienen title/body vacios.
  2) Calcula (una sola vez, con cache en disco) el embedding de
     "title + body" de cada articulo con el mismo modelo que usa la
     app (all-MiniLM-L6-v2, ver app/services/embedding.py).
  3) Para cada una de las 24 condiciones (funcion x k):
       - Para cada una de las 25 preguntas:
           a) embebe la pregunta
           b) puntua la pregunta contra todos los articulos con la
              funcion de la condicion (coseno, producto escalar,
              euclidea o Manhattan)
           c) toma los k articulos mejor puntuados (top-k)
           d) construye el contexto (titulo + cuerpo, truncado) con
              esos k articulos y arma el prompt con generate_prompt()
              (la funcion real de app/kafka/generate_prompt.py)
           e) llama al LLM real (Ollama / llama3:8b) para obtener la
              respuesta generada
           f) calcula Precision@k, Recall@k y el recíproco del rango
              (RR) comparando el top-k con el articulo gold de la
              pregunta, y la similitud respuesta-referencia (coseno
              entre el embedding de la respuesta generada y el de la
              respuesta de referencia)
       - Guarda los resultados de la condicion (fila a fila) en un CSV
         "en bruto" (una fila por pregunta x condicion), para poder
         hacer despues los tests estadisticos (Shapiro, Levene,
         Friedman, Wilcoxon) sobre las 25 observaciones de cada
         condicion.
  4) Al final, agrega los resultados por condicion (media +/- desviacion
     tipica) en un segundo CSV con el mismo formato que la Tabla 1 del
     TFG.

SIMPLIFICACIONES respecto al pipeline de produccion (documentar en el TFG):
  - Se ignora la "memoria" conversacional: se llama a generate_prompt()
    con history=[] siempre (cada pregunta es independiente). No se usa
    ni se toca la coleccion "memory" de Mongo.
  - No se resume cada articulo recuperado con el LLM antes de meterlo
    en el contexto (el pipeline en produccion sí lo hace via
    summarize_article() en consumer.py). Aqui el contexto son
    directamente los k articulos (title + body, truncados a
    MAX_CHARS_PER_ARTICLE caracteres cada uno) para poder evaluar de
    forma practica las 24 condiciones x 25 preguntas (600 llamadas al
    LLM) en un tiempo razonable. Si se quisiera replicar exactamente
    el pipeline de produccion habria que añadir ese paso de resumen
    (multiplicaria las llamadas al LLM por el numero de articulos
    recuperados en cada pregunta).
  - No requiere MongoDB: el corpus se lee directamente de los JSON en
    CORPUS_DIR, no hace falta tener cargados los articulos en Mongo
    para este experimento.

COMO EJECUTARLO:
  Desde la carpeta MicroLLM, con el entorno que tiene sentence-transformers,
  torch y requests instalados (ver requirements.txt), y con Ollama
  corriendo y accesible en OLLAMA_URL:

      cd C:\\repositorio\\Periodico\\MicroLLM
      python -m app.kafka.experiment

  Modo de prueba rapida (3 preguntas, 2 condiciones) para comprobar que
  todo funciona antes de lanzar el barrido completo:

      python -m app.kafka.experiment --test

  Si Ollama corre en otro host/puerto:

      python -m app.kafka.experiment --ollama-url http://localhost:11434/api/generate

  El script es reanudable: si se interrumpe, al volver a ejecutarlo se
  saltan las combinaciones (pregunta, funcion, k) que ya esten en el
  CSV de resultados en bruto.
"""

import argparse
import csv
import json
import os
import statistics
import sys
import time

import numpy as np
import requests

# Permite ejecutar este archivo tanto con "python -m app.kafka.experiment"
# como directamente ("python experiment.py") añadiendo la raiz de
# MicroLLM al path para que "import app...." funcione en ambos casos.
_MICROLLM_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _MICROLLM_ROOT not in sys.path:
    sys.path.insert(0, _MICROLLM_ROOT)

from app.services.embedding import get_embedding  # noqa: E402
from app.kafka.generate_prompt import generate_prompt  # noqa: E402
from app.kafka.eval_dataset import EVAL_QUESTIONS  # noqa: E402


# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

CORPUS_DIR = os.environ.get(
    "CORPUS_DIR", r"C:\repositorio\Periodico\Artificial intelligence"
)
EMBEDDINGS_CACHE_PATH = os.path.join(os.path.dirname(__file__), "corpus_embeddings_cache.json")
RAW_RESULTS_PATH = os.path.join(os.path.dirname(__file__), "resultados_experimento_raw.csv")
SUMMARY_RESULTS_PATH = os.path.join(os.path.dirname(__file__), "resultados_experimento.csv")

DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3:8b")

K_VALUES = [1, 2, 3, 5, 10, 15]
MAX_CHARS_PER_ARTICLE = 800  # truncado del cuerpo de cada articulo en el contexto


# ---------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------

def load_corpus(corpus_dir: str) -> dict:
    """Carga los articulos validos (title y body no vacios) de corpus_dir.

    Devuelve un dict {article_id: {"title": str, "body": str}}.
    """
    corpus = {}
    files = [f for f in os.listdir(corpus_dir) if f.endswith(".json")]
    for fname in files:
        path = os.path.join(corpus_dir, fname)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as exc:
            print(f"WARN: no se pudo leer {fname}: {exc}")
            continue

        article_id = data.get("_id") or data.get("id")
        title = data.get("title") or ""
        body = data.get("body") or []
        body_text = " ".join(body) if isinstance(body, list) else str(body)

        if not article_id or not title.strip() or not body_text.strip():
            continue

        corpus[article_id] = {"title": title, "body": body_text}

    print(f"Corpus cargado: {len(corpus)} articulos validos de {len(files)} ficheros.")
    return corpus


def get_or_build_embeddings(corpus: dict) -> dict:
    """Devuelve {article_id: np.ndarray} usando cache en disco si existe."""
    if os.path.exists(EMBEDDINGS_CACHE_PATH):
        with open(EMBEDDINGS_CACHE_PATH, "r", encoding="utf-8") as fh:
            cached = json.load(fh)
        # Solo reutilizamos la cache si cubre exactamente los mismos articulos.
        if set(cached.keys()) == set(corpus.keys()):
            print(f"Usando embeddings cacheados ({len(cached)} articulos) desde {EMBEDDINGS_CACHE_PATH}")
            return {aid: np.array(vec, dtype=np.float32) for aid, vec in cached.items()}
        print("La cache de embeddings no coincide con el corpus actual; se recalcula.")

    print(f"Calculando embeddings para {len(corpus)} articulos (puede tardar un poco)...")
    embeddings = {}
    for i, (article_id, art) in enumerate(corpus.items(), start=1):
        full_text = f"{art['title']}\n\n{art['body']}"
        embeddings[article_id] = np.array(get_embedding(full_text), dtype=np.float32)
        if i % 25 == 0:
            print(f"  {i}/{len(corpus)} embeddings calculados...")

    with open(EMBEDDINGS_CACHE_PATH, "w", encoding="utf-8") as fh:
        json.dump({aid: vec.tolist() for aid, vec in embeddings.items()}, fh)
    print(f"Embeddings guardados en cache: {EMBEDDINGS_CACHE_PATH}")
    return embeddings


# ---------------------------------------------------------------------------
# Funciones de similitud / distancia
# ---------------------------------------------------------------------------

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def dot_product(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def manhattan_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sum(np.abs(a - b)))


# (funcion, higher_is_better)
SIMILARITY_FUNCS = {
    "coseno": (cosine_sim, True),
    "producto_escalar": (dot_product, True),
    "euclidea": (euclidean_distance, False),
    "manhattan": (manhattan_distance, False),
}


def retrieve_top_k(query_emb: np.ndarray, corpus_embeddings: dict, func, higher_is_better: bool, k: int):
    scored = [(aid, func(query_emb, emb)) for aid, emb in corpus_embeddings.items()]
    scored.sort(key=lambda x: x[1], reverse=higher_is_better)
    return scored[:k]


# ---------------------------------------------------------------------------
# Metricas de recuperacion (se asume |Rel(q)| = 1: un unico articulo gold)
# ---------------------------------------------------------------------------

def precision_at_k(retrieved_ids: list, gold_id: str, k: int) -> float:
    return (1.0 if gold_id in retrieved_ids else 0.0) / k


def recall_at_k(retrieved_ids: list, gold_id: str) -> float:
    return 1.0 if gold_id in retrieved_ids else 0.0


def reciprocal_rank(retrieved_ids: list, gold_id: str) -> float:
    if gold_id in retrieved_ids:
        return 1.0 / (retrieved_ids.index(gold_id) + 1)
    return 0.0


# ---------------------------------------------------------------------------
# Contexto, prompt y llamada al LLM
# ---------------------------------------------------------------------------

def build_context(retrieved: list, corpus: dict, max_chars: int = MAX_CHARS_PER_ARTICLE) -> str:
    parts = []
    for article_id, _score in retrieved:
        art = corpus[article_id]
        body = art["body"]
        if len(body) > max_chars:
            body = body[:max_chars].rsplit(" ", 1)[0] + "..."
        parts.append(f"Title: {art['title']}\n{body}")
    return "\n\n---\n\n".join(parts)


def ask_ollama(prompt: str, ollama_url: str, model: str = OLLAMA_MODEL, retries: int = 2) -> str:
    last_error = None
    for attempt in range(retries + 1):
        try:
            response = requests.post(
                ollama_url,
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=180,
            )
            if response.ok:
                return response.json().get("response", "").strip()
            last_error = f"HTTP {response.status_code}: {response.text}"
        except Exception as exc:
            last_error = str(exc)
        print(f"  WARN: fallo al llamar a Ollama (intento {attempt + 1}/{retries + 1}): {last_error}")
        time.sleep(2)
    return f"[ERROR: no se pudo generar respuesta - {last_error}]"


# ---------------------------------------------------------------------------
# Ejecucion de una condicion (funcion, k) sobre las 25 preguntas
# ---------------------------------------------------------------------------

def run_condition(func_name: str, k: int, questions: list, corpus: dict, corpus_embeddings: dict,
                   ollama_url: str, already_done: set) -> list:
    func, higher_is_better = SIMILARITY_FUNCS[func_name]
    rows = []

    for q in questions:
        key = (q["id"], func_name, k)
        if key in already_done:
            continue

        query_emb = np.array(get_embedding(q["question"]), dtype=np.float32)
        retrieved = retrieve_top_k(query_emb, corpus_embeddings, func, higher_is_better, k)
        retrieved_ids = [aid for aid, _ in retrieved]

        context = build_context(retrieved, corpus)
        prompt = generate_prompt(context, [], q["question"])  # history=[] -> sin memoria
        generated_answer = ask_ollama(prompt, ollama_url)

        gen_emb = np.array(get_embedding(generated_answer), dtype=np.float32)
        ref_emb = np.array(get_embedding(q["reference_answer"]), dtype=np.float32)
        generation_similarity = cosine_sim(gen_emb, ref_emb)

        gold_found = q["gold_article_id"] in retrieved_ids
        rank = retrieved_ids.index(q["gold_article_id"]) + 1 if gold_found else None

        row = {
            "question_id": q["id"],
            "function": func_name,
            "k": k,
            "precision_at_k": precision_at_k(retrieved_ids, q["gold_article_id"], k),
            "recall_at_k": recall_at_k(retrieved_ids, q["gold_article_id"]),
            "reciprocal_rank": reciprocal_rank(retrieved_ids, q["gold_article_id"]),
            "generation_similarity": generation_similarity,
            "gold_found": gold_found,
            "rank": rank if rank is not None else "",
            "retrieved_ids": ";".join(retrieved_ids),
            "generated_answer": generated_answer,
        }
        rows.append(row)

        print(
            f"  [{func_name} k={k}] {q['id']}: gold_found={gold_found} "
            f"rank={rank} gen_sim={generation_similarity:.3f}"
        )

    return rows


# ---------------------------------------------------------------------------
# CSV helpers (permiten reanudar el experimento si se interrumpe)
# ---------------------------------------------------------------------------

RAW_FIELDNAMES = [
    "question_id", "function", "k", "precision_at_k", "recall_at_k",
    "reciprocal_rank", "generation_similarity", "gold_found", "rank",
    "retrieved_ids", "generated_answer",
]


def load_already_done(path: str) -> set:
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            done.add((row["question_id"], row["function"], int(row["k"])))
    return done


def append_rows(path: str, rows: list):
    if not rows:
        return
    file_exists = os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=RAW_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def write_summary(raw_path: str, summary_path: str):
    """Agrega el CSV en bruto por condicion (media +/- desviacion tipica),
    con el mismo formato que la Tabla 1 del TFG."""
    if not os.path.exists(raw_path):
        print("No hay resultados en bruto todavia; no se genera resumen.")
        return

    by_condition = {}
    with open(raw_path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            key = (row["function"], int(row["k"]))
            by_condition.setdefault(key, []).append(row)

    display_names = {
        "coseno": "Coseno",
        "producto_escalar": "Producto escalar",
        "euclidea": "Euclídea",
        "manhattan": "Manhattan",
    }

    def mean_std(values):
        mean = statistics.mean(values)
        std = statistics.pstdev(values) if len(values) > 1 else 0.0
        return mean, std

    with open(summary_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Funcion", "k", "Precision@k", "Recall@k", "MRR", "Similitud_respuesta", "N"])
        for func_name in ["coseno", "producto_escalar", "euclidea", "manhattan"]:
            for k in K_VALUES:
                key = (func_name, k)
                rows = by_condition.get(key)
                if not rows:
                    continue
                precision = [float(r["precision_at_k"]) for r in rows]
                recall = [float(r["recall_at_k"]) for r in rows]
                rr = [float(r["reciprocal_rank"]) for r in rows]
                gensim = [float(r["generation_similarity"]) for r in rows]

                p_mean, p_std = mean_std(precision)
                r_mean, r_std = mean_std(recall)
                rr_mean, rr_std = mean_std(rr)
                g_mean, g_std = mean_std(gensim)

                writer.writerow([
                    display_names[func_name], k,
                    f"{p_mean:.2f} ± {p_std:.2f}",
                    f"{r_mean:.2f} ± {r_std:.2f}",
                    f"{rr_mean:.2f} ± {rr_std:.2f}",
                    f"{g_mean:.2f} ± {g_std:.2f}",
                    len(rows),
                ])

    print(f"Resumen (formato Tabla 1) guardado en: {summary_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Experimento RAG: 4 funciones x 6 valores de k")
    parser.add_argument("--test", action="store_true",
                         help="Modo de prueba rapida: 3 preguntas y 2 condiciones, para comprobar que todo funciona.")
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL,
                         help=f"URL del endpoint de generacion de Ollama (por defecto: {DEFAULT_OLLAMA_URL})")
    parser.add_argument("--corpus-dir", default=CORPUS_DIR,
                         help=f"Carpeta con los articulos JSON (por defecto: {CORPUS_DIR})")
    args = parser.parse_args()

    corpus = load_corpus(args.corpus_dir)
    corpus_embeddings = get_or_build_embeddings(corpus)

    # Comprobacion: que todos los gold_article_id del dataset existan en el corpus.
    missing = [q["id"] for q in EVAL_QUESTIONS if q["gold_article_id"] not in corpus]
    if missing:
        print(f"AVISO: {len(missing)} preguntas referencian articulos gold no encontrados en el corpus: {missing}")

    questions = EVAL_QUESTIONS
    conditions = [(func, k) for func in SIMILARITY_FUNCS for k in K_VALUES]

    if args.test:
        questions = EVAL_QUESTIONS[:3]
        conditions = [("coseno", 3), ("euclidea", 3)]
        print(f"MODO TEST: {len(questions)} preguntas x {len(conditions)} condiciones.")

    already_done = load_already_done(RAW_RESULTS_PATH)
    if already_done:
        print(f"Reanudando: {len(already_done)} combinaciones (pregunta, funcion, k) ya calculadas, se omiten.")

    total_conditions = len(conditions)
    for idx, (func_name, k) in enumerate(conditions, start=1):
        print(f"\n=== Condicion {idx}/{total_conditions}: funcion={func_name}, k={k} ===")
        rows = run_condition(func_name, k, questions, corpus, corpus_embeddings, args.ollama_url, already_done)
        append_rows(RAW_RESULTS_PATH, rows)
        for r in rows:
            already_done.add((r["question_id"], func_name, k))

    write_summary(RAW_RESULTS_PATH, SUMMARY_RESULTS_PATH)
    print("\nExperimento completo.")
    print(f"  Resultados en bruto: {RAW_RESULTS_PATH}")
    print(f"  Resumen (Tabla 1):   {SUMMARY_RESULTS_PATH}")


if __name__ == "__main__":
    main()
