import asyncio 
import json
import requests
from datetime import datetime
import numpy as np
from aiokafka import AIOKafkaConsumer

from app.config.kafka import KAFKA_BOOTSTRAP_SERVERS, TOPIC_NAMES, GROUP_ID
from app.services.mongo import get_mongo_collection
from app.services.embedding import get_embedding
from .generate_prompt import generate_prompt





consumer = None

def ask_ollama(prompt: str) -> str:
    response = requests.post("http://host.docker.internal:11434/api/generate", json={
        "model": "llama3:8b",
        "prompt": prompt,
        "stream": False
    })
    if response.ok:
        return response.json().get("response", "").strip()
    else:
        print("❌ Error al contactar con Ollama:", response.text)
        return "No se pudo generar respuesta."

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

async def start_kafka():
    global consumer
    consumer = AIOKafkaConsumer(
        *TOPIC_NAMES,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest"
    )
    await consumer.start()
    asyncio.create_task(consume_messages())
    print(f"✅ Escuchando topics: {TOPIC_NAMES}")

async def stop_kafka():
    if consumer:
        await consumer.stop()
        print("🛑 Kafka detenido.")

async def consume_messages():
    async for msg in consumer:
        topic = msg.topic
        payload = msg.value

        print(f"\n📨 Mensaje de '{topic}': {json.dumps(payload, indent=2)}")

        if topic == "article.created.embedding":
            await process_article(payload)
        elif topic == "user.question.asked":
            await process_question(payload) 

async def process_article(payload):
    id = payload.get("id")
    title = payload.get("title")
    body = payload.get("body")
    if id and title and body:
        full_text = f"{title}\n\n{body}"
        embedding = get_embedding(full_text)

        await get_mongo_collection().insert_one({
            "_id": id,
            "title": title,
            "body": body,
            "embedding": embedding,
            "timestamp": datetime.utcnow()
        })
        print("✅ Artículo insertado en MongoDB con embedding.")
    else:
        print("⚠️ Artículo incompleto.")

def build_prompt_from_history(history: list[dict], context: str) -> str:
    prompt_parts = []
    for entry in history:
        role = entry["role"]
        content = entry["content"]
        if role == "user":
            prompt_parts.append(f"Usuario: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Asistente: {content}")
    prompt_parts.append(f"Contexto:\n{context}")
    prompt_parts.append("Asistente:")
    return "\n".join(prompt_parts)




async def process_question(payload):
    question = payload.get("question")
    if not question:
        print("⚠️ Pregunta vacía.")
        return

    print(f"❓ Pregunta: {question}")
    query_embedding = np.array(get_embedding(question))

    collection = get_mongo_collection()
    articles = await collection.find({"embedding": {"$exists": True}}).to_list(length=1000)

    scored = []
    for article in articles:
        art_emb = np.array(article["embedding"])
        score = cosine_similarity(query_embedding, art_emb)
        scored.append((article["_id"], article["title"], article["body"], score))

    scored.sort(key=lambda x: x[3], reverse=True)
    top_k = 3
    top_matches = scored[:top_k]

    # 🔹 Mostrar artículos seleccionados
    print("\n📚 Artículos seleccionados para el resumen condicional:")
    for i, (aid, title, body, score) in enumerate(top_matches, start=1):
        print(f"\n🔹 Artículo #{i}")
        print(f"ID: {aid}")
        print(f"Título: {title}")
        print(f"Score similitud: {score:.4f}")
        print(f"Resumen del cuerpo: {body[:200]}...")

    # 🔹 Generar resúmenes por artículo usando Ollama
    def summarize_article(title: str, body: str, question: str) -> str:
        prompt = (
            "Given the article below and the user's question, summarize the article focusing only on the parts relevant to the question.\n\n"
            f"=== ARTICLE ===\n{title}\n{body}\n\n"
            f"=== QUESTION ===\n{question}\n\n"
            "=== SUMMARY ==="
        )
        return ask_ollama(prompt)

    summaries = []
    for _, title, body, _ in top_matches:
        summary = summarize_article(title, body, question)
        summaries.append(summary)

    context = "\n\n".join(summaries)

    # 🔹 Obtener colección de memoria
    memory_collection = collection.database["memory"]
    memory_doc = await memory_collection.find_one({})
    if not memory_doc:
        memory_doc = {"history": []}
        await memory_collection.insert_one(memory_doc)

    history = memory_doc["history"]

    # 🔹 Mostrar historial de conversación
    print("\n🧠 Historial completo de conversación:")
    for i, entry in enumerate(history, start=1):
        role = entry["role"]
        content = entry["content"]
        print(f"\n{i}. {role.upper()}: {content}")

    # 🔹 Generar prompt final
    prompt = generate_prompt(context, history, question)

    print("\n📨 Enviando prompt a Ollama:\n" + prompt)
    respuesta = ask_ollama(prompt)
    print("\n🤖 Respuesta de LLaMA 3:")
    print(respuesta)

    # 🔹 Actualizar historial
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": respuesta})

    await memory_collection.update_one(
        {"_id": memory_doc["_id"]},
        {"$set": {"history": history}}
    )

 


