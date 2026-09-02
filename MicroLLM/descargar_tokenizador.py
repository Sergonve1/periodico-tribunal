from transformers import AutoTokenizer

# ⚠️ Pega tu token personal aquí
token = "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"

tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    trust_remote_code=True,
    use_auth_token=token
)

tokenizer.save_pretrained("./llama3-tokenizer")
print("✅ Tokenizador descargado correctamente en ./llama3-tokenizer")
