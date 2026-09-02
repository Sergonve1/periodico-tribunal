import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
TOPIC_NAMES = ["article.created.embedding", "user.question.asked"]
GROUP_ID = "micro-llm-consumer-group-v2"
