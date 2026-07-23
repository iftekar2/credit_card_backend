import chromadb
from chromadb.utils import embedding_functions
import ollama
import json


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

def query_documents(question, n_result=2): 
    result = collection.query(query_texts=question, n_results=n_result)
    relevant_chunks = [doc for sublist in result["documents"] for doc in sublist]
    print("==== Returning relevant chunks ====")
    return relevant_chunks

def generate_response(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)

    prompt = (
        "You are a structured data extraction model. Extract credit card details "
        "from the context into a single JSON object. Output strictly JSON.\n\n"
        "KEYS & EXPECTED FORMATS:\n"
        '- "card_name": string\n'
        '- "issuer": string\n'
        '- "card_type": string\n'
        '- "annual_fee": number\n'
        '- "credit_score_min": number or null\n'
        '- "credit_score_max": number or null\n'
        '- "signup_bonus_value": string\n'
        '- "signup_bonus_requirements": string\n'
        '- "reward_categories": array of objects [{"category": str, "multiplier": float}]\n'
        '- "perks": array of strings (e.g., ["No foreign transaction fees", "Trip Cancellation Insurance", "$100 Hotel Credit"]). NEVER return null for perks; if none found, return [].\n\n'
        "Rules:\n"
        "1. Look thoroughly through the context for travel protections, credits, insurance, and partner benefits.\n"
        "2. Do not invent details not present in context.\n\n"
        f"Context:\n{context}"
    )

    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
        format="json",
    )

    return response["message"]["content"]