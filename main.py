from component.answer_question import query_documents, generate_response
import json


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

    except json.JSONDecodeError:
        print("Failed to parse response as JSON. Raw output was:")
        print(raw_json_str)
        # print(answer)

if __name__ == "__main__": 
    main()