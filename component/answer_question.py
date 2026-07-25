import chromadb
from chromadb.utils import embedding_functions
import ollama
import json
import re


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

def query_documents(question, n_result=4): 
    result = collection.query(query_texts=question, n_results=n_result)
    relevant_chunks = [doc for sublist in result["documents"] for doc in sublist]
    print("==== Returning relevant chunks ====")
    return relevant_chunks

def _extract_json_payload(raw_text):
    if not raw_text:
        return "{}"

    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        return match.group(0)
    return cleaned


def generate_response(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)

    system_instruction = (
        "You are a structured data extraction model. Extract credit card details "
        "from the context into a single valid JSON object. Output strictly JSON.\n\n"
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
        '- "perks": array of strings (e.g. ["No foreign transaction fees", "Trip Cancellation Insurance", "$100 Hotel Credit"]). Extract ALL travel protections, statement credits, DashPass, and insurance benefits mentioned.\n\n'
        "RULES:\n"
        "1. Look thoroughly through the provided context.\n"
        "2. Do not invent details not present in context.\n"
        "3. If perks or credit scores are not mentioned in context, return empty array [] or null."
    )

    user_payload = f"Context:\n{context}\n\nQuestion:\n{question}"

    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_payload},
        ],
        format="json",
        options={"temperature": 0, "seed": 42},
    )

    return _extract_json_payload(response["message"]["content"])