def generate_prompt(context: str, history: list[dict], question: str) -> str:
    prompt_parts = []

    prompt_parts.append(
        "You are a senior analyst specialized in artificial intelligence.\n"
        "Your task is to respond in English, using a professional and technical tone,\n"
        "based strictly on the information provided in the following news articles.\n"
        "Do not fabricate information. If the context does not contain enough details to answer,\n"
        "clearly state that the information is insufficient.\n"
    )

    prompt_parts.append("\n=== REFERENCE ARTICLES ===")
    prompt_parts.append(context)

    prompt_parts.append("\n=== PREVIOUS CONVERSATION ===")
    for entry in history[-5:]: 
        role = entry["role"]
        content = entry["content"]
        label = "User" if role == "user" else "Assistant"
        prompt_parts.append(f"{label}: {content}")

    prompt_parts.append("\n=== CURRENT QUESTION ===")
    prompt_parts.append(f"User: {question}")
    prompt_parts.append("Assistant:")

    return "\n".join(prompt_parts)
