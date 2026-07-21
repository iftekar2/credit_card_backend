import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions


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
    return ollama_ef([text])[0]


processed_chunks = chunked_documents(documents)


def generate_embedding(processed_chunks): 
    for doc in processed_chunks:
        print("===== Generating embedding ====")
        doc["embedding"] = get_embedding(doc["text"])
        print(f"Generated embedding for {doc['id']}", doc["embedding"])


def save_embedding_to_db(processed_chunks):
    ids = []
    documents = []
    embeddings = []

    for doc in processed_chunks:
        print("===== Inserting chunks into db ====")
        ids.append(doc["id"])
        documents.append(doc["text"])
        embeddings.append(get_embedding(doc["text"]))

    collection.upsert(ids=ids, documents=documents, embeddings=embeddings)
