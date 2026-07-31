import os
import re
import ollama
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from supabase import create_client

try:
    from .generate_embedding import get_embedding
except ImportError:
    from generate_embedding import get_embedding

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"],
)

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name="qwen3-embedding:4b",
)

def query_documents(question: str, n_results: int = 4) -> list[str]:
    print("==== Generating embedding for query ====")
    query_embedding = get_embedding(question)

    print("==== Querying Supabase for relevant chunks ====")
    try:
        response = supabase.rpc(
            "match_chunks",
            {
                "query_embedding": query_embedding,
                "match_count": n_results,
            },
        ).execute()

        relevant_chunks = [item["raw_text"] for item in response.data]
        print(f"==== Found {len(relevant_chunks)} relevant chunks ====")
        return relevant_chunks

    except Exception as e:
        print(f"Error querying Supabase: {e}")
        return []

def _clean_json_output(raw_text: str) -> str:
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


def generate_response(question: str, relevant_chunks: list[str]) -> str:
    context = "\n\n".join(relevant_chunks)

    system_instruction = (
        "You are an expert financial data structure engine. Extract credit card details "
        "strictly from the provided text and format it into a single, valid JSON object.\n\n"
        "REQUIRED JSON SCHEMA:\n"
        "{\n"
        '  "card_name": "string (e.g., Chase Sapphire Preferred)",\n'
        '  "issuer": "string (e.g., Chase, American Express, Citi)",\n'
        '  "card_type": "string (e.g., Personal, Business)",\n'
        '  "annual_fee": number or null (numeric value only, e.g. 95, 0),\n'
        '  "credit_score_min": number or null (e.g. 670),\n'
        '  "credit_score_max": number or null (e.g. 850),\n'
        '  "signup_bonus_value": "string or null (e.g. 60,000 bonus points)",\n'
        '  "signup_bonus_requirements": "string or null (e.g. Spend $4,000 in first 3 months)",\n'
        '  "foreign_transactions": "string or null (e.g. No foreign transaction fees )",\n'
        '  "card_type": "Personal or Business",\n'
        '  "reward_categories": [\n'
        '    {"category": "string", "multiplier": float}\n'
        "  ],\n"
        '  "perks": ["string (e.g., $50 Hotel Credit, No foreign transaction fees)"]\n'
        "}\n\n"
        "CRITICAL RULES:\n"
        "1. Convert currency strings for annual_fee to raw numbers (e.g., '$95' -> 95, '$0' -> 0).\n"
        "2. Do NOT invent details not present in context.\n"
        "3. If a field is unknown or not mentioned, return null (or [] for arrays)."
    )

    user_payload = f"Context Material:\n{context}\n\nUser Question:\n{question}"

    print("Processing context with qwen3:8b...")
    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_payload},
        ],
        format="json",
        options={"temperature": 0.0, "seed": 42},
    )

    return _clean_json_output(response["message"]["content"])