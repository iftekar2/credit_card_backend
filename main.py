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
        if filename.endswith(".txt"):
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

def chunked_documents(documents): 
    chunked_documents_array = []

    for doc in documents:
        chunks = split_text(doc["text"])
        print("==== Split text into chunks ====")
        for i, chunk in enumerate(chunks): 
            chunked_documents_array.append({"id": f"{doc['id']}_chunk{i+1}", "text": chunk})

    return chunked_documents_array

    # print(len(chunked_documents))

# print(f"Split documents into {chunked_documents(documents)} chunks")

def get_embedding(text): 
    payload = {
        "model": "qwen3-embedding:4b",
        "input": text,
    }

    request = urllib.request.Request(
        "http://localhost:11434/api/embeddings",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.load(response)

    return result["embedding"]


processed_chunks = chunked_documents(documents)
for doc in processed_chunks:
    print("===== Generating embedding ====")
    doc["embedding"] = get_embedding(doc["text"])
    print(f"Generated embedding for {doc['id']}:", doc["embedding"])