import json
import os
import urllib.request
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import ollama


# load_dotenv()

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


# def ask_ollama(prompt: str, model: str = "qwen3:8b") -> str:
#     payload = {
#         "model": model,
#         "prompt": prompt,
#         "stream": False,
#     }

#     request = urllib.request.Request(
#         "http://localhost:11434/api/generate",
#         data=json.dumps(payload).encode("utf-8"),
#         headers={"Content-Type": "application/json"},
#     )

#     with urllib.request.urlopen(request, timeout=60) as response:
#         result = json.load(response)

#     return result["response"].strip()

# def load_documents_from_directory(directory_path): 
#     print("====== Loading document from directory ======")
#     documents = []
#     for filename in os.listdir(directory_path):
#         if filename.endswith(".txt"):
#             with open(
#                 os.path.join(directory_path, filename), "r", encoding="utf-8"
#             ) as file:
#                 documents.append({"id": filename, "text": file.read()})
#     return documents

# def split_text(text, chunk_size=1000, chunk_overlap=20): 
#     chunks = []
#     start = 0

#     while start < len(text): 
#         end = start + chunk_size
#         chunks.append(text[start:end])
#         start = end - chunk_overlap
#     return chunks


# directory_path = "./card_details"
# documents = load_documents_from_directory(directory_path)
# print(f"Loaded {len(documents)} documents")

# def chunked_documents(documents): 
#     chunked_documents_array = []

#     for doc in documents:
#         chunks = split_text(doc["text"])
#         print("==== Split text into chunks ====")
#         for i, chunk in enumerate(chunks): 
#             chunked_documents_array.append({"id": f"{doc['id']}_chunk{i+1}", "text": chunk})

#     return chunked_documents_array

#     # print(len(chunked_documents))

# # print(f"Split documents into {chunked_documents(documents)} chunks")

# def get_embedding(text):
#     return ollama_ef([text])[0]


# processed_chunks = chunked_documents(documents)


# def generate_embedding(processed_chunks): 
#     for doc in processed_chunks:
#         print("===== Generating embedding ====")
#         doc["embedding"] = get_embedding(doc["text"])
#         print(f"Generated embedding for {doc['id']}", doc["embedding"])


# def save_embedding_to_db(processed_chunks):
#     ids = []
#     documents = []
#     embeddings = []

#     for doc in processed_chunks:
#         print("===== Inserting chunks into db ====")
#         ids.append(doc["id"])
#         documents.append(doc["text"])
#         embeddings.append(get_embedding(doc["text"]))

#     collection.upsert(ids=ids, documents=documents, embeddings=embeddings)


def query_documents(question, n_result=2): 
    result = collection.query(query_texts=question, n_results=n_result)
    relevant_chunks = [doc for sublist in result["documents"] for doc in sublist]
    print("==== Returning relevant chunks ====")
    return relevant_chunks

def generate_response(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)
    prompt = (
        "You are an assistant for question-answering tasks. Use the following pieces of "
        "retrieved context to answer the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the answer concise."
        "\n\nContext:\n" + context + "\n\nQuestion:\n" + question
    )

    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
    )

    return response["message"]["content"]


question = "How many points are offered for this credit card?"
relevant_chunks = query_documents(question)
answer = generate_response(question, relevant_chunks)

print(answer)