import json
from scrapegraphai.graphs import SmartScraperGraph

# Define prompt with explicit instructions for exhaustive detail
prompt = """
Analyze the webpage text and extract EVERY SINGLE detail about the credit card into a clean, comprehensive, fully expanded JSON object.

Do NOT summarize, abbreviate, or merge items into general lists. Extract every numerical limit, date, restriction, and brand mentioned on the page using the following target structure:

1. CARD BASICS:
   - "card_name": Exact full card name
   - "issuer": Issuing bank
   - "network": Card network
   - "annual_fee": Full details including intro waiver terms or pricing conditions
   - "apr_details": APR ranges, variable status, and intro APR if applicable
   - "foreign_transaction_fee": Exact fee amount or percentage

2. WELCOME OFFER:
   - "bonus_amount": Points, cash, or miles offered
   - "spend_requirement": Exact spend required to unlock bonus
   - "timeframe": Time period given
   - "offer_expiration": Expiration date or urgency notes
   - "eligibility_rules": Any explicit restrictions on past cardholders

3. REWARD MULTIPLIERS (List EVERY multiplier explicitly):
   - Category name, multiplier rate (5x, 3x, 2x, 1x), specific inclusions/exclusions

4. STATEMENT CREDITS & DIRECT BENEFITS (List EVERY credit explicitly):
   - Credit name, dollar amount, renewal frequency, terms

5. PARTNER PERKS & PROMOTIONS (List ALL partners individually):
   - Partner name, exact offer details, expiration dates, valuation notes

6. POINT TRANSFER PARTNERS (List EVERY partner individually):
   - Airline Partners: List all individual airline loyalty program names
   - Hotel Partners: List all individual hotel loyalty program names

7. INSURANCE & TRAVEL PROTECTIONS (List EVERY insurance policy explicitly):
   - Benefit name, exact coverage limit, covered conditions

8. ADDITIONAL FEATURES:
   - Pay Over Time options, concierges, security monitoring, digital wallet support

Return ONLY a valid, raw JSON object.
"""

graph_config = {
    "llm": {
        "model": "ollama/qwen3:8b",
        "temperature": 0,
        "format": "json",
        "base_url": "http://localhost:11434",
        "model_tokens": 8192
    },
    "embeddings": {
        "model": "ollama/qwen3-embedding:4b",
        "base_url": "http://localhost:11434"
    }
}

smart_scraper_graph = SmartScraperGraph(
    prompt=prompt,
    source="https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred?CELL=6TKX",
    config=graph_config
)

result = smart_scraper_graph.run()

# Display formatted JSON output
if isinstance(result, str):
    parsed = json.loads(result)
    print(json.dumps(parsed, indent=4))
else:
    print(json.dumps(result, indent=4))