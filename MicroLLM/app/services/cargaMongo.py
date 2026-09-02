import os
import json
import random
from pymongo import MongoClient
from datetime import datetime, timedelta

# Ruta base
DIRECTORIO_RAIZ = r"C:\repositorio\WebScrapping"

# Carpetas específicas a procesar
CARPETAS_OBJETIVO = [
    "Anthropic",
    "Artificial intelligence",
    "ia",
    "Meta",
    "Microsoft",
    "NVIDIA",
    "OpenAI",
    "Tesla"
]

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27018/")
db = client["Newspaper"]
coleccion = db["article"]

# Formato esperado del campo "creation" y "publication"
FORMATO_FECHA = "%B %d %Y %I:%M %p"

def generar_fecha_aleatoria():
    """Devuelve una fecha aleatoria entre 2022 y 2024 como datetime"""
    inicio = datetime(2022, 1, 1)
    fin = datetime(2024, 12, 31)
    delta = fin - inicio
    fecha_aleatoria = inicio + timedelta(days=random.randint(0, delta.days),
                                         hours=random.randint(0, 23),
                                         minutes=random.randint(0, 59))
    return fecha_aleatoria

def convertir_o_generar_fecha(campo, doc):
    if campo in doc and isinstance(doc[campo], str):
        try:
            return datetime.strptime(doc[campo], FORMATO_FECHA)
        except ValueError as e:
            print(f"⚠️ Formato incorrecto en '{campo}': {doc[campo]} ({e})")
    # Si no existe o está mal formateado, se genera
    return generar_fecha_aleatoria()

def procesar_documento(doc):
    if "id" in doc:
        doc["_id"] = doc.pop("id")

    doc["creation"] = convertir_o_generar_fecha("creation", doc)
    doc["publication"] = convertir_o_generar_fecha("publication", doc)

    return doc

def cargar_documentos():
    for nombre_carpeta in CARPETAS_OBJETIVO:
        ruta_carpeta = os.path.join(DIRECTORIO_RAIZ, nombre_carpeta)
        if not os.path.isdir(ruta_carpeta):
            print(f"⚠️ Carpeta no encontrada: {ruta_carpeta}")
            continue
        print(f"📁 Procesando: {ruta_carpeta}")

        for archivo in os.listdir(ruta_carpeta):
            if archivo.endswith(".json"):
                ruta_archivo = os.path.join(ruta_carpeta, archivo)
                with open(ruta_archivo, encoding="utf-8") as f:
                    try:
                        datos = json.load(f)
                        if isinstance(datos, dict):
                            documentos = [procesar_documento(datos)]
                        elif isinstance(datos, list):
                            documentos = [procesar_documento(d) for d in datos]
                        else:
                            continue
                        coleccion.insert_many(documentos)
                        print(f"✅ Insertados {len(documentos)} documentos desde {ruta_archivo}")
                    except Exception as e:
                        print(f"❌ Error en {ruta_archivo}: {e}")

if __name__ == "__main__":
    cargar_documentos()
