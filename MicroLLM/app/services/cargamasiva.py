import os
import json
from datetime import datetime
from embedding import get_embedding  # Asegúrate de que embedding.py está junto a este script

CARPETAS = [
    "Anthropic",
    "Artificial intelligence",
    "ia",
    "Meta",
    "Microsoft",
    "NVIDIA",
    "OpenAI",
    "Tesla"
    # Agrega más nombres si lo necesitas
]

def procesar_articulos(nombre_carpeta: str):
    base_path = os.path.join("C:\\repositorio\\WebScrapping", nombre_carpeta)
    output_path = os.path.join("C:\\repositorio\\WebScrapping", "embeddings")
    os.makedirs(output_path, exist_ok=True)

    print(f"📂 Base path: {base_path}")
    print(f"📂 Output path: {output_path}")

    if not os.path.exists(base_path):
        print(f"❌ Carpeta no encontrada: {base_path}")
        return

    archivos = [f for f in os.listdir(base_path) if f.endswith(".json")]  # <-- ahora JSON
    print(f"📄 Archivos encontrados en '{nombre_carpeta}': {len(archivos)}")

    for archivo in archivos:
        ruta_completa = os.path.join(base_path, archivo)
        print(f"🔍 Procesando archivo: {ruta_completa}")

        try:
            with open(ruta_completa, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            print("✅ JSON cargado correctamente.")

            id_ = json_data.get("id")
            title = json_data.get("title")
            body = json_data.get("body")

            if not all([id_, title, body]):
                print(f"⚠️ Datos incompletos en {archivo}. id: {id_}, title: {title}, body: {bool(body)}")
                continue

            full_text = f"{title}\n\n{body}"
            print("🧠 Generando embedding...")
            embedding = get_embedding(full_text)
            print("✅ Embedding generado.")

            timestamp = datetime.utcnow().isoformat(timespec="milliseconds") + "+00:00"

            resultado = {
                "_id": id_,
                "title": title,
                "body": body,
                "embedding": embedding,
                "timestamp": timestamp
            }

            salida_json = os.path.join(output_path, f"{id_}.json")
            with open(salida_json, "w", encoding="utf-8") as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)

            print(f"💾 Guardado en: {salida_json}")

        except Exception as e:
            print(f"❌ Error procesando {archivo} en {nombre_carpeta}: {e}")

def carga_masiva():
    print("🚀 Iniciando carga masiva...")
    for carpeta in CARPETAS:
        print(f"\n📁 Procesando carpeta: {carpeta}")
        procesar_articulos(carpeta)
    print("✅ Carga masiva completada.")

if __name__ == "__main__":
    carga_masiva()
