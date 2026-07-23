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
        "You are an information extraction assistant. Extract credit card details "
        "from the provided context and respond ONLY with a valid JSON object. "
        "Do not include any explanation or extra text outside the JSON.\n\n"
        "Use the following keys:\n"
        '- "card_name": string or null\n'
        '- "issuer": string or null\n'
        '- "card_type": string or null\n'
        '- "annual_fee": number or null\n'
        '- "credit_score_min": number or null\n'
        '- "credit_score_max": number or null\n'
        '- "signup_bonus_value": string or null\n'
        '- "signup_bonus_requirements": string or null\n'
        '- "reward_categories": array of objects [{"category": str, "multiplier": float}] or null\n'
        '- "perks": array of strings or null\n\n'
        "Context:\n" + context
    )

    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
        format="json"
    )

    return response["message"]["content"]