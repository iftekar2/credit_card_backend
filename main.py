import json
import os
import urllib.request

from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions


load_dotenv()

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name="qwen3-embedding:4b",
)

chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "document_qa_collection"
collection = chroma_client.get_or_create_collection(
    name=collection_name,
    embedding_function=ollama_ef,
)


def ask_ollama(prompt: str, model: str = "qwen3:8b") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    request = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.load(response)

    return result["response"].strip()


response = ask_ollama("How much points are offered for this card?")
print(response)