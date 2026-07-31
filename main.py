from component.answer_question import query_documents, generate_response
import json
from supabase import create_client
import os
from dotenv import load_dotenv
import re


load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"],
)


def normalize_card_name(name: str) -> str:
    if not name:
        return ""

    cleaned = re.sub(r"[®™©]", "", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned.title()

def save_data_to_database(card_data: dict, table_name: str = "credit_cards"):
    clean_name = normalize_card_name(card_data.get("card_name"))

    payload = {
        "card_name": clean_name,
        "issuer": card_data.get("issuer"),
        "card_type": card_data.get("card_type"),
        "annual_fee": card_data.get("annual_fee"),
        "credit_score_min": card_data.get("credit_score_min"),
        "credit_score_max": card_data.get("credit_score_max"),
        "signup_bonus_value": card_data.get("signup_bonus_value"),
        "signup_bonus_requirements": card_data.get(
            "signup_bonus_requirements"
        ),
        "reward_categories": card_data.get("reward_categories") or [],
        "perks": card_data.get("perks") or [],
        "foreign_transactions": card_data.get("foreign_transactions"),
        "card_type": card_data.get("card_type"),
    }

    try:
        response = (
            supabase.table(table_name)
            .upsert(payload, on_conflict="card_name")
            .execute()
        )
        print(f"\n Successfully saved/updated '{clean_name}' in Supabase!")
        return response.data
    except Exception as e:
        print(f"\n Error saving to Supabase: {e}")
        return None

def main():
    question = (
        "Extract the card name, issuer, card type, annual fee, credit score requirements, "
        "signup bonus details, reward categories, and key perks."
    )
    
    relevant_chunks = query_documents(question)
    
    if not relevant_chunks:
        print("No relevant text chunks found in Supabase.")
        return

    raw_json_str = generate_response(question, relevant_chunks)

    try:
        card_data = json.loads(raw_json_str)

        print("\n=== Extracted Structured Card Data ===")
        print(f"Card Name:     {card_data.get('card_name')}")
        print(f"Issuer:        {card_data.get('issuer')}")
        print(f"Card Type:     {card_data.get('card_type')}")
        print(f"Annual Fee:    ${card_data.get('annual_fee')}")
        print(f"Credit Score:  {card_data.get('credit_score_min')} - {card_data.get('credit_score_max')}")
        print(f"Bonus Value:   {card_data.get('signup_bonus_value')}")
        print(f"Bonus Req:     {card_data.get('signup_bonus_requirements')}")
        print(f"Categories:    {json.dumps(card_data.get('reward_categories'), indent=2)}")
        print(f"Perks:         {json.dumps(card_data.get('perks'), indent=2)}")
        print(f"foreign_transactions: {card_data.get('foreign_transactions')}")
        print(f"card_type: {card_data.get('card_type')}")

        save_data_to_database(card_data, table_name="credit_cards")

    except json.JSONDecodeError:
        print("Failed to parse response as JSON. Raw output was:")
        print(raw_json_str)


if __name__ == "__main__":
    main()