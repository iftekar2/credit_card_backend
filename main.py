from component.answer_question import query_documents, generate_response
import json
from supabase import create_client
import os
from dotenv import load_dotenv


load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"],
)


def save_data_to_database(card_data: dict, table_name: str = "embedded_data"): 
    payload = {
        "card_name": card_data.get("card_name"),
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
    }

    try:
        response = supabase.table(table_name).insert(payload).execute()
        print("\n Successfully saved card to Supabase!")
        return response.data
    except Exception as e:
        print(f"\n Error saving to Supabase: {e}")
        return None

def main():
    question = "Can you tell me the card name, issuer, card type, card type, annual fee, credit card minimum, signup bonus," \
    "signup bonus requirement, reward category, perks?"
    relevant_chunks = query_documents(question)
    raw_json_str = generate_response(question, relevant_chunks)

    try:
        card_data = json.loads(raw_json_str)

        print("\n=== Extracted Card Data ===")
        print(f"Card Name:     {card_data.get('card_name')}")
        print(f"Issuer:        {card_data.get('issuer')}")
        print(f"Card Type:     {card_data.get('card_type')}")
        print(f"Annual Fee:    ${card_data.get('annual_fee')}")
        print(
            f"Credit Score:  {card_data.get('credit_score_min')} - {card_data.get('credit_score_max')}"
        )
        print(f"Bonus Value:   {card_data.get('signup_bonus_value')}")
        print(f"Bonus Req:     {card_data.get('signup_bonus_requirements')}")
        print(
            f"Categories:    {json.dumps(card_data.get('reward_categories'), indent=2)}"
        )
        print(f"Perks:         {card_data.get('perks')}")

        save_data_to_database(card_data, table_name="embedded_data")

    except json.JSONDecodeError:
        print("Failed to parse response as JSON. Raw output was:")
        print(raw_json_str)

if __name__ == "__main__": 
    main()