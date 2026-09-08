# app/kafka/experiment_v2.py
"""
Experimento RAG v2 del TFG (version "dificil"): mismo barrido de 4 funciones
de similitud x 6 valores de top-k (24 condiciones) que experiment.py, pero
con un diseno pensado para que aparezcan diferencias reales entre valores de
k y entre funciones de similitud/distancia, cosa que no ocurria en el primer
experimento.

QUE CAMBIA RESPECTO A experiment.py (v1):

  1) CORPUS TROCEADO EN PARRAFOS, NO EN ARTICULOS ENTEROS.
     En vez de embeber "titulo + cuerpo completo" de cada articulo (v1),
     aqui cada articulo se trocea en pasajes a nivel de parrafo (funcion
     chunk_body). Esto multiplica el numero de "documentos" recuperables
     (de ~67 articulos en v1 a mas de 10.000 pasajes aqui) y aumenta la
     variabilidad de longitud/norma de los embeddings, que es precisamente
     lo que permite que coseno, producto escalar, euclidea y Manhattan
     puedan discrepar en el ranking (con vectores de norma muy parecida,
     las cuatro funciones ordenan igual).

  2) CORPUS AMPLIADO A 8 CARPETAS, DEDUPLICADO POR ID.
     v1 solo usaba "Artificial intelligence". Aqui se cargan tambien
     Anthropic, ia, Meta, Microsoft, NVIDIA, OpenAI y Tesla. Como el mismo
     articulo aparece a veces en varias carpetas (mismo _id), se
     deduplica por id antes de trocear.

  3) PREGUNTAS "DIFICILES" Y MULTI-HOP (ver eval_dataset_v2.py).
     La mitad de las preguntas son de un solo pasaje relevante pero
     parafraseadas (no copian el vocabulario del articulo), elegidas de
     grupos tematicos con varios articulos muy similares (distractores).
     La otra mitad son multi-hop: requieren combinar 2-3 articulos
     distintos (|Rel(q)| > 1), por lo que Recall@k ya no puede saturar en
     k=1 automaticamente.

  4) METRICAS DE RECUPERACION GENERALIZADAS A |Rel(q)| >= 1.
     La relevancia se define a nivel de ARTICULO (Rel(q) = conjunto de
     gold_ids de la pregunta), pero la recuperacion es a nivel de PASAJE.
     Un pasaje recuperado "cuenta" como acierto si el articulo del que
     proviene esta en Rel(q).
       Precision@k(q) = (num. de los k pasajes recuperados cuyo articulo
                          esta en Rel(q)) / k
       Recall@k(q)    = (num. de articulos DISTINTOS de Rel(q) que
                          aparecen entre los articulos de los k pasajes
                          recuperados) / |Rel(q)|
       RR(q)          = 1 / (posicion del primer pasaje recuperado cuyo
                              articulo esta en Rel(q))  [0 si no aparece
                              ninguno en el top-k]
     Con |Rel(q)| = 1 estas formulas coinciden exactamente con las de v1.

COMO EJECUTARLO (igual que v1):

    cd C:\\repositorio\\Periodico\\MicroLLM
    python -m app.kafka.experiment_v2 --test      # prueba rapida
    python -m app.kafka.experiment_v2             # experimento completo

  Variables de entorno opcionales: CORPUS_ROOT (por defecto
  C:\\repositorio\\Periodico), OLLAMA_URL, OLLAMA_MODEL.

  El script es reanudable igual que v1 (se apoya en
  resultados_experimento_v2_raw.csv).
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

_MICROLLM_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _MICROLLM_ROOT not in sys.path:
    sys.path.insert(0, _MICROLLM_ROOT)

from app.services.embedding import get_embedding  # noqa: E402
from app.kafka.generate_prompt import generate_prompt  # noqa: E402
from app.kafka.eval_dataset_v2 import EVAL_DATASET_V2  # noqa: E402


# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

CORPUS_ROOT = os.environ.get("CORPUS_ROOT", r"C:\repositorio\Periodico")
CORPUS_FOLDERS = [
    "Anthropic", "Artificial intelligence", "ia", "Meta",
    "Microsoft", "NVIDIA", "OpenAI", "Tesla",
]

EMBEDDINGS_CACHE_PATH = os.path.join(os.path.dirname(__file__), "corpus_v2_embeddings_cache.json")
RAW_RESULTS_PATH = os.path.join(os.path.dirname(__file__), "resultados_experimento_v2_raw.csv")
SUMMARY_RESULTS_PATH = os.path.join(os.path.dirname(__file__), "resultados_experimento_v2.csv")

DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3:8b")

K_VALUES = [1, 2, 3, 5, 10, 15]
MIN_CHARS_PER_CHUNK = 200  # tamano minimo aproximado de cada pasaje/parrafo


# ---------------------------------------------------------------------------
# Corpus: carga multi-carpeta + deduplicacion + troceado en parrafos
# ---------------------------------------------------------------------------

def chunk_body(body_text: str, min_chars: int = MIN_CHARS_PER_CHUNK) -> list:
    """Trocea el cuerpo de un articulo en pasajes a nivel de parrafo.

    Los parrafos (separados por saltos de linea) se van concatenando hasta
    alcanzar min_chars caracteres, para evitar pasajes demasiado cortos
    (p.ej. una sola frase suelta) que aportarian poca senal semantica.
    """
    raw_parts = [p.strip() for p in body_text.split("\n") if p.strip()]
    chunks = []
    buf = ""
    for part in raw_parts:
        buf = (buf + " " + part).strip() if buf else part
        if len(buf) >= min_chars:
            chunks.append(buf)
            buf = ""
    if buf:
        if chunks and len(buf) < 80:
            chunks[-1] = chunks[-1] + " " + buf
        else:
            chunks.append(buf)
    return chunks


def load_corpus_v2(corpus_root: str, folders: list) -> dict:
    """Carga y deduplica articulos de todas las carpetas indicadas.

    Devuelve {article_id: {"title": str, "body": str, "chunks": [str, ...]}}.
    Un mismo articulo (mismo _id/id) puede aparecer en varias carpetas
    tematicas del repositorio; solo se conserva una copia.
    """
    seen = {}
    total_files = 0
    dup_count = 0
    for folder in folders:
        d = os.path.join(corpus_root, folder)
        if not os.path.isdir(d):
            print(f"AVISO: no existe la carpeta {d}, se omite.")
            continue
        for fname in os.listdir(d):
            if not fname.endswith(".json"):
                continue
            total_files += 1
            path = os.path.join(d, fname)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except Exception:
                continue

            article_id = data.get("_id") or data.get("id")
            title = (data.get("title") or "").strip()
            body = data.get("body")
            body_text = "\n".join(str(b) for b in body if b) if isinstance(body, list) else str(body or "")
            body_text = body_text.strip()

            if not article_id or not title or not body_text:
                continue
            if article_id in seen:
                dup_count += 1
                continue

            seen[article_id] = {
                "title": title,
                "body": body_text,
                "chunks": chunk_body(body_text),
            }

    n_chunks = sum(len(a["chunks"]) for a in seen.values())
    print(
        f"Corpus v2 cargado: {len(seen)} articulos unicos "
        f"({total_files} ficheros escaneados, {dup_count} duplicados entre carpetas), "
        f"{n_chunks} pasajes totales."
    )
    return seen


def build_passages(corpus: dict) -> dict:
    """Aplana el corpus a nivel de pasaje: {passage_id: {"article_id", "title", "text"}}."""
    passages = {}
    for article_id, art in corpus.items():
        for i, chunk in enumerate(art["chunks"]):
            passage_id = f"{article_id}::{i}"
            passages[passage_id] = {
                "article_id": article_id,
                "title": art["title"],
                "text": chunk,
            }
    return passages


def get_or_build_embeddings(passages: dict) -> dict:
    """Devuelve {passage_id: np.ndarray}, usando cache en disco si existe."""
    if os.path.exists(EMBEDDINGS_CACHE_PATH):
        with open(EMBEDDINGS_CACHE_PATH, "r", encoding="utf-8") as fh:
            cached = json.load(fh)
        if set(cached.keys()) == set(passages.keys()):
            print(f"Usando embeddings cacheados ({len(cached)} pasajes) desde {EMBEDDINGS_CACHE_PATH}")
            return {pid: np.array(vec, dtype=np.float32) for pid, vec in cached.items()}
        print("La cache de embeddings no coincide con el corpus actual; se recalcula.")

    print(f"Calculando embeddings para {len(passages)} pasajes (puede tardar varios minutos)...")
    embeddings = {}
    for i, (passage_id, p) in enumerate(passages.items(), start=1):
        full_text = f"{p['title']}\n\n{p['text']}"
        embeddings[passage_id] = np.array(get_embedding(full_text), dtype=np.float32)
        if i % 500 == 0:
            print(f"  {i}/{len(passages)} embeddings calculados...")

    with open(EMBEDDINGS_CACHE_PATH, "w", encoding="utf-8") as fh:
        json.dump({pid: vec.tolist() for pid, vec in embeddings.items()}, fh)
    print(f"Embeddings guardados en cache: {EMBEDDINGS_CACHE_PATH}")
    return embeddings


# ---------------------------------------------------------------------------
# Funciones de similitud / distancia (identicas a v1)
# ---------------------------------------------------------------------------

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def dot_product(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def manhattan_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sum(np.abs(a - b)))


SIMILARITY_FUNCS = {
    "coseno": (cosine_sim, True),
    "producto_escalar": (dot_product, True),
    "euclidea": (euclidean_distance, False),
    "manhattan": (manhattan_distance, False),
}


def retrieve_top_k(query_emb: np.ndarray, passage_embeddings: dict, func, higher_is_better: bool, k: int):
    scored = [(pid, func(query_emb, emb)) for pid, emb in passage_embeddings.items()]
    scored.sort(key=lambda x: x[1], reverse=higher_is_better)
    return scored[:k]


# ---------------------------------------------------------------------------
# Metricas de recuperacion generalizadas a |Rel(q)| >= 1
# ---------------------------------------------------------------------------

def precision_at_k(retrieved_article_ids: list, gold_ids: set, k: int) -> float:
    hits = sum(1 for aid in retrieved_article_ids if aid in gold_ids)
    return hits / k


def recall_at_k(retrieved_article_ids: list, gold_ids: set) -> float:
    found = {aid for aid in retrieved_article_ids if aid in gold_ids}
    return len(found) / len(gold_ids)


def reciprocal_rank(retrieved_article_ids: list, gold_ids: set) -> float:
    for i, aid in enumerate(retrieved_article_ids):
        if aid in gold_ids:
            return 1.0 / (i + 1)
    return 0.0


# ---------------------------------------------------------------------------
# Contexto, prompt y llamada al LLM
# ---------------------------------------------------------------------------

def build_context(retrieved: list, passages: dict) -> str:
    parts = []
    for passage_id, _score in retrieved:
        p = passages[passage_id]
        parts.append(f"Title: {p['title']}\n{p['text']}")
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
# Ejecucion de una condicion (funcion, k) sobre las 40 preguntas
# ---------------------------------------------------------------------------

def run_condition(func_name: str, k: int, questions: list, passages: dict, passage_embeddings: dict,
                   ollama_url: str, already_done: set) -> list:
    func, higher_is_better = SIMILARITY_FUNCS[func_name]
    rows = []

    for q in questions:
        key = (q["id"], func_name, k)
        if key in already_done:
            continue

        gold_ids = set(q["gold_ids"])

        query_emb = np.array(get_embedding(q["question"]), dtype=np.float32)
        retrieved = retrieve_top_k(query_emb, passage_embeddings, func, higher_is_better, k)
        retrieved_passage_ids = [pid for pid, _ in retrieved]
        retrieved_article_ids = [passages[pid]["article_id"] for pid in retrieved_passage_ids]

        context = build_context(retrieved, passages)
        prompt = generate_prompt(context, [], q["question"])  # history=[] -> sin memoria
        generated_answer = ask_ollama(prompt, ollama_url)

        gen_emb = np.array(get_embedding(generated_answer), dtype=np.float32)
        ref_emb = np.array(get_embedding(q["reference_answer"]), dtype=np.float32)
        generation_similarity = cosine_sim(gen_emb, ref_emb)

        found_gold_articles = {aid for aid in retrieved_article_ids if aid in gold_ids}
        rank = None
        for i, aid in enumerate(retrieved_article_ids):
            if aid in gold_ids:
                rank = i + 1
                break

        row = {
            "question_id": q["id"],
            "hop_type": q["hop_type"],
            "n_gold": len(gold_ids),
            "function": func_name,
            "k": k,
            "precision_at_k": precision_at_k(retrieved_article_ids, gold_ids, k),
            "recall_at_k": recall_at_k(retrieved_article_ids, gold_ids),
            "reciprocal_rank": reciprocal_rank(retrieved_article_ids, gold_ids),
            "generation_similarity": generation_similarity,
            "n_gold_found": len(found_gold_articles),
            "gold_found": len(found_gold_articles) > 0,
            "rank": rank if rank is not None else "",
            "retrieved_article_ids": ";".join(retrieved_article_ids),
            "generated_answer": generated_answer,
        }
        rows.append(row)

        print(
            f"  [{func_name} k={k}] {q['id']} ({q['hop_type']}, |Rel|={len(gold_ids)}): "
            f"found={len(found_gold_articles)}/{len(gold_ids)} rank={rank} gen_sim={generation_similarity:.3f}"
        )

    return rows


# ---------------------------------------------------------------------------
# CSV helpers (reanudable, igual que v1)
# ---------------------------------------------------------------------------

RAW_FIELDNAMES = [
    "question_id", "hop_type", "n_gold", "function", "k", "precision_at_k", "recall_at_k",
    "reciprocal_rank", "generation_similarity", "n_gold_found", "gold_found", "rank",
    "retrieved_article_ids", "generated_answer",
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
    parser = argparse.ArgumentParser(description="Experimento RAG v2: 4 funciones x 6 valores de k, corpus troceado")
    parser.add_argument("--test", action="store_true",
                         help="Modo de prueba rapida: 3 preguntas y 2 condiciones.")
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL,
                         help=f"URL del endpoint de generacion de Ollama (por defecto: {DEFAULT_OLLAMA_URL})")
    parser.add_argument("--corpus-root", default=CORPUS_ROOT,
                         help=f"Carpeta raiz del repositorio (por defecto: {CORPUS_ROOT})")
    args = parser.parse_args()

    corpus = load_corpus_v2(args.corpus_root, CORPUS_FOLDERS)
    passages = build_passages(corpus)
    passage_embeddings = get_or_build_embeddings(passages)

    # Comprobacion: que todos los gold_ids del dataset existan en el corpus.
    all_article_ids = set(corpus.keys())
    missing = []
    for q in EVAL_DATASET_V2:
        for gid in q["gold_ids"]:
            if gid not in all_article_ids:
                missing.append((q["id"], gid))
    if missing:
        print(f"AVISO: {len(missing)} referencias a gold_ids no encontradas en el corpus: {missing}")

    questions = EVAL_DATASET_V2
    conditions = [(func, k) for func in SIMILARITY_FUNCS for k in K_VALUES]

    if args.test:
        questions = EVAL_DATASET_V2[:3]
        conditions = [("coseno", 3), ("euclidea", 3)]
        print(f"MODO TEST: {len(questions)} preguntas x {len(conditions)} condiciones.")

    already_done = load_already_done(RAW_RESULTS_PATH)
    if already_done:
        print(f"Reanudando: {len(already_done)} combinaciones (pregunta, funcion, k) ya calculadas, se omiten.")

    total_conditions = len(conditions)
    for idx, (func_name, k) in enumerate(conditions, start=1):
        print(f"\n=== Condicion {idx}/{total_conditions}: funcion={func_name}, k={k} ===")
        rows = run_condition(func_name, k, questions, passages, passage_embeddings, args.ollama_url, already_done)
        append_rows(RAW_RESULTS_PATH, rows)
        for r in rows:
            already_done.add((r["question_id"], func_name, k))

    write_summary(RAW_RESULTS_PATH, SUMMARY_RESULTS_PATH)
    print("\nExperimento v2 completo.")
    print(f"  Resultados en bruto: {RAW_RESULTS_PATH}")
    print(f"  Resumen (Tabla 1):   {SUMMARY_RESULTS_PATH}")


if __name__ == "__main__":
    main()
