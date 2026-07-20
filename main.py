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

def load_documents_from_directory(directory_path): 
    print("====== Loading document from directory ======")
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            with open(
                os.path.join(directory_path, filename), "r", encoding="utf-8"
            ) as file:
                documents.append({"id": filename, "text": file.read()})
    return documents

def split_text(text, chunk_size=1000, chunk_overlap=20): 
    chunks = []
    start = 0

    while start < len(text): 
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks


directory_path = "./card_details"
documents = load_documents_from_directory(directory_path)
print(f"Loaded {len(documents)} documents")

# response = ask_ollama("How much points are offered for this card?")
# print(response)