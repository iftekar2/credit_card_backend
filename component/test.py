# import json
# from scrapegraphai.graphs import SmartScraperGraph

# prompt = """
# Analyze the webpage text and extract EVERY SINGLE detail about the credit card into a clean, comprehensive, fully expanded JSON object.

# Do NOT summarize, abbreviate, or merge items into general lists. Extract every numerical limit, date, restriction, and brand mentioned on the page using the following target structure:

# 1. CARD BASICS:
#    - "card_name": Exact full card name
#    - "issuer": Issuing bank
#    - "network": Card network
#    - "annual_fee": Full details including intro waiver terms or pricing conditions
#    - "apr_details": APR ranges, variable status, and intro APR if applicable
#    - "foreign_transaction_fee": Exact fee amount or percentage

# 2. WELCOME OFFER:
#    - "bonus_amount": Points, cash, or miles offered
#    - "spend_requirement": Exact spend required to unlock bonus
#    - "timeframe": Time period given
#    - "offer_expiration": Expiration date or urgency notes
#    - "eligibility_rules": Any explicit restrictions on past cardholders

# 3. REWARD MULTIPLIERS (List EVERY multiplier explicitly):
#    - Category name, multiplier rate (5x, 3x, 2x, 1x), specific inclusions/exclusions

# 4. STATEMENT CREDITS & DIRECT BENEFITS (List EVERY credit explicitly):
#    - Credit name, dollar amount, renewal frequency, terms

# 5. PARTNER PERKS & PROMOTIONS (List ALL partners individually):
#    - Partner name, exact offer details, expiration dates, valuation notes

# 6. POINT TRANSFER PARTNERS (List EVERY partner individually):
#    - Airline Partners: List all individual airline loyalty program names
#    - Hotel Partners: List all individual hotel loyalty program names

# 7. INSURANCE & TRAVEL PROTECTIONS (List EVERY insurance policy explicitly):
#    - Benefit name, exact coverage limit, covered conditions

# 8. ADDITIONAL FEATURES:
#    - Pay Over Time options, concierges, security monitoring, digital wallet support

# Return ONLY a valid, raw JSON object.
# """

# graph_config = {
#     "llm": {
#         "model": "ollama/qwen3:8b",
#         "temperature": 0,
#         "format": "json",
#         "base_url": "http://localhost:11434",
#         "model_tokens": 8192
#     },
#     "embeddings": {
#         "model": "ollama/qwen3-embedding:4b",
#         "base_url": "http://localhost:11434"
#     }
# }

# smart_scraper_graph = SmartScraperGraph(
#     prompt=prompt,
#     source="https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred?CELL=6TKX",
#     config=graph_config
# )

# result = smart_scraper_graph.run()

# if isinstance(result, str):
#     parsed = json.loads(result)
#     print(json.dumps(parsed, indent=4))
# else:
#     print(json.dumps(result, indent=4))







# import requests
# from bs4 import BeautifulSoup
# import json
# from langchain_community.llms import Ollama

# # 1. Fetch clean text directly (takes ~1 second)
# url = "https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred?CELL=6TKX"
# headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
# response = requests.get(url, headers=headers)

# soup = BeautifulSoup(response.text, "html.parser")
# # Remove script/style tags to clean up noise
# for script in soup(["script", "style"]):
#     script.extract()
# clean_text = soup.get_text(separator="\n", strip=True)

# # 2. Build the strict extraction prompt using raw text
# prompt = f"""
# Below is raw text scraped directly from a credit card product page.
# Analyze the text and extract EVERY SINGLE detail into a valid JSON object.

# STRICT INSTRUCTIONS:
# - Use ONLY the provided text. Do not invent fees, credits, or benefits.
# - Extract EVERY transfer partner listed under "Airline Travel Partners" and "Hotel Travel Partners".
# - Extract EVERY reward rate (5x, 3x, 2x, 1x) with exact categories.
# - Return ONLY valid JSON.

# TEXT CONTENT:
# {clean_text}
# """

# # 3. Call local Ollama model directly
# llm = Ollama(
#     model="qwen3:8b",
#     base_url="http://localhost:11434",
#     temperature=0,
#     format="json"
# )

# result = llm.invoke(prompt)

# try:
#     parsed = json.loads(result)
#     print(json.dumps(parsed, indent=4))
# except Exception as e:
#     print("Raw Output:\n", result)








# import requests
# from bs4 import BeautifulSoup
# import json
# from scrapegraphai.graphs import SmartScraperGraph

# # Fetch page text first
# url = "https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred?CELL=6TKX"
# headers = {"User-Agent": "Mozilla/5.0"}
# html_content = requests.get(url, headers=headers).text
# soup = BeautifulSoup(html_content, "html.parser")
# text_content = soup.get_text(separator="\n", strip=True)

# graph_config = {
#     "llm": {
#         "model": "ollama/qwen3:8b",
#         "temperature": 0,
#         "format": "json",
#         "base_url": "http://localhost:11434",
#         "model_tokens": 8192
#     }
# }

# prompt = "Extract all credit card information into a structured JSON object. Extract every airline partner, hotel partner, and exact multiplier."

# # Pass raw text instead of URL to avoid chunking issues
# smart_scraper_graph = SmartScraperGraph(
#     prompt=prompt,
#     source=text_content, # Pass raw string directly!
#     config=graph_config
# )

# result = smart_scraper_graph.run()
# print(json.dumps(result, indent=4))








# import json
# import re
# import requests
# from bs4 import BeautifulSoup
# import ollama

# # 1. Fetch clean text directly
# url = "https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred?CELL=6TKX"
# headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
# response = requests.get(url, headers=headers)

# soup = BeautifulSoup(response.text, "html.parser")
# for script in soup(["script", "style", "nav", "footer"]):
#     script.extract()

# text_content = soup.get_text(separator="\n", strip=True)

# # 2. Direct system & user prompt
# system_prompt = (
#     "You are a strict data extraction engine. Extract ONLY text explicitly present in the input. "
#     "Do NOT use external knowledge, do NOT invent airline partners, and do NOT guess."
# )

# user_prompt = f"""
# Analyze the rendered webpage text below and extract EVERY credit card detail into valid JSON.

# STRICT INSTRUCTIONS:
# - GROUND TRUTH ONLY: Extract ONLY partners and numbers written in the text.
# - TRANSFER PARTNERS: Look for the sections under 'Airline Travel Partners' and 'Hotel Travel Partners' and extract every single program name explicitly listed.
# - INSURANCE: Extract exact dollar caps ($10,000, $500/day, $3,000, etc.) from the text.

# RENDERED TEXT:
# [clean_text]

# Extract into this structure:
# {{
#   "card_name": "...",
#   "issuer": "...",
#   "annual_fee": "...",
#   "welcome_bonus": {{
#     "points": "...",
#     "spend_requirement": "...",
#     "timeframe": "..."
#   }},
#   "reward_multipliers": [
#     {{"category": "...", "rate": "..."}}
#   ],
#   "statement_credits": [
#     {{"name": "...", "amount": "...", "terms": "..."}}
#   ],
#   "partner_perks": [
#     {{"partner": "...", "details": "..."}}
#   ],
#   "transfer_partners": {{
#     "airlines": ["extract", "from", "text"],
#     "hotels": ["extract", "from", "text"]
#   }},
#   "insurance_and_protections": [
#     {{"benefit": "...", "coverage_limit": "..."}}
#   ]
# }}
# """

# print("Running extraction with Ollama...")
# response = ollama.chat(
#     model="qwen3:8b",
#     messages=[
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": user_prompt}
#     ],
#     options={"temperature": 0, "num_ctx": 16384}
# )

# raw_output = response['message']['content']

# # Clean thinking tags or formatting
# cleaned = re.sub(r'<thought>.*?</thought>', '', raw_output, flags=re.DOTALL)
# start_idx = cleaned.find('{')
# end_idx = cleaned.rfind('}')
# json_str = cleaned[start_idx : end_idx + 1]

# print(json.dumps(json.loads(json_str), indent=4))

# # 3. Call Ollama directly without format="json" to prevent internal API crashes
# response = ollama.chat(
#     model="qwen3:8b",
#     messages=[
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": user_prompt}
#     ],
#     options={
#         "temperature": 0,
#         "num_ctx": 8192  # Ensure full text context fits in memory
#     }
# )

# raw_output = response['message']['content']

# # 4. Clean extraction helper
# def extract_json_string(raw_text: str) -> str:
#     cleaned = re.sub(r'<thought>.*?</thought>', '', raw_text, flags=re.DOTALL)
#     cleaned = re.sub(r'```json\s*', '', cleaned)
#     cleaned = re.sub(r'```\s*', '', cleaned)
    
#     start_idx = cleaned.find('{')
#     end_idx = cleaned.rfind('}')
#     if start_idx != -1 and end_idx != -1:
#         return cleaned[start_idx : end_idx + 1]
#     return cleaned.strip()

# cleaned_output = extract_json_string(raw_output)

# try:
#     parsed_json = json.loads(cleaned_output)
#     print(json.dumps(parsed_json, indent=4))
# except json.JSONDecodeError as e:
#     print(f"Failed to parse JSON. Error: {e}")
#     print("\nRaw LLM Output was:\n", raw_output)







# import json
# import re
# from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright
# import ollama

# def fetch_dynamic_text(url: str) -> str:
#     """Launches Playwright to execute JavaScript and extract full rendered text."""
#     with sync_playwright() as p:
#         # Launch browser with a standard desktop user agent to avoid bot detection
#         browser = p.chromium.launch(headless=True)
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#         )
#         page = context.new_page()
        
#         print("Navigating to URL with Playwright...")
#         page.goto(url, wait_until="networkidle")  # Wait until network requests settle
        
#         # Scroll down to trigger lazy-loaded sections (like partner logos and policy text)
#         page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
#         page.wait_for_timeout(2000)  # Wait 2 seconds for JS execution
        
#         # Get full rendered HTML
#         rendered_html = page.content()
#         browser.close()
        
#     # Clean up HTML with BeautifulSoup
#     soup = BeautifulSoup(rendered_html, "html.parser")
#     for script in soup(["script", "style", "svg", "nav", "footer"]):
#         script.extract()
        
#     return soup.get_text(separator="\n", strip=True)

# # Fetch the dynamic text
# url = "https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred?CELL=6TKX"
# clean_text = fetch_dynamic_text(url)

# print(f"Successfully rendered {len(clean_text)} characters of text.")






# import json
# from scrapegraphai.graphs import SmartScraperGraph

# # Simplified prompt: Pass 1 — Raw Snippet Extraction
# prompt = """
# Scan the webpage text and extract EVERY SINGLE feature, benefit, perk, reward multiplier, fee, insurance coverage, or requirement listed for this credit card.

# Do NOT attempt to categorize, organize, or summarize the data into a complex schema.

# Output a clean, flat JSON array of objects, where every object contains exactly two keys:
# - "title": A short label identifying the feature or perk (e.g., "Annual Fee", "Apple TV Benefit", "Dining Multiplier", "Trip Cancellation Insurance").
# - "body": The verbatim or exact details, terms, limits, dates, or dollar amounts written on the page for that feature.

# EXAMPLE OUTPUT STRUCTURE:
# [
#   {
#     "title": "Welcome Bonus",
#     "body": "Earn 75,000 bonus points after you spend $4,000 on purchases in the first 3 months from account opening."
#   },
#   {
#     "title": "Annual Fee",
#     "body": "$95 annual fee."
#   },
#   {
#     "title": "Dining Multiplier",
#     "body": "Earn 3x points on dining at restaurants, including eligible delivery services, takeout, and dining out."
#   }
# ]

# Return ONLY a valid raw JSON array of these snippet objects.
# """

# graph_config = {
#     "llm": {
#         "model": "ollama/qwen3:8b",
#         "temperature": 0,
#         "format": "json",
#         "base_url": "http://localhost:11434",
#         "model_tokens": 8192
#     },
#     "embeddings": {
#         "model": "ollama/qwen3-embedding:4b",
#         "base_url": "http://localhost:11434"
#     }
# }

# smart_scraper_graph = SmartScraperGraph(
#     prompt=prompt,
#     source="https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred?CELL=6TKX",
#     config=graph_config
# )

# result = smart_scraper_graph.run()

# if isinstance(result, str):
#     parsed = json.loads(result)
#     print(json.dumps(parsed, indent=4))
# else:
#     print(json.dumps(result, indent=4))
















# import json
# from scrapegraphai.graphs import SmartScraperGraph

# prompt = """
# You are a verbatim text parser. Read the webpage text and extract EVERY SINGLE detail, benefit, insurance policy, numerical term, and partner name into a flat JSON array of title/body objects.

# DO NOT summarize, DO NOT condense, and DO NOT guess. 
# The "body" value MUST be a direct or near-verbatim quote of the details from the text.

# YOU MUST EXTRACT AN OBJECT FOR EVERY SINGLE ITEM BELOW:

# 1: Card name: 
#  - Chase Sapphire Preferred® Credit Card

# 2: Card slogan: 
#  - Earn more than ever, same low annual fee.

# 3: Card Offer: 
#  - Earn 75,000 (strike through --> Meaning it was 75,000 points before now 100,000 points) 100,000 points

# 4: How to qualify for the points: 
#  - after you spend $5,000 in purchases in the first 3 months from account opening.

# 5: Annual fee: 
#  - $95 annual fee

# 6: APR: 
#  - 19.24%–27.49% variable APR.

# 7: Offer disclaimer:
#  - This credit card is unavailable to you if you currently have this card open. The new cardmember bonus may not be available to you if you previously held this card or received a new cardmember bonus for this card. We may also consider the number of cards you have opened and closed in determining your bonus eligibility.

# 8: Points title: 
#  - Sapphire Preferred® just got even better

# 9: Travel: 
#  - 5x points on Chase Travel

# 10: Dining:
#  - 3x points on dining

# 11: Gas stations, EV charging, and vacation homes: 
# 3x points on gas stations, EV charging, and vacation homes at top brands*

# 12: Streaming services and grocery: 
#  - 3x points on top streaming services and online grocery, exclusions apply

# 13: All other travel: 
#  - 2x points on all other travel

# 14: All other purchases: 
#  - 1X points on all other purchases

# 15: More reason's to love: 
#  - Now with even more to love

# 16: Hotel Credit: 
#  - $100 Chase Travel Hotel Credit Earn up to $100 in statement credits each account anniversary year for hotel stays purchased through Chase Travel*.

# 17: Global Entry or TSA: 
#  - Global Entry or TSA PreCheck® or NEXUS Application Fee credit
# Receive one statement credit of up to $120 every four years as reimbursement for the application fee charged to your card.*

# 18: Value that adds up: 

# 19: Apple TV benefit:
#  - Get a year of complimentary Apple TV when activated by December 31, 2026 - a value of $156.*

# 20: DoorDash benefits:
#  - Get a complimentary DashPass membership, a $120 value for 12 months. Enjoy $0 delivery fees and reduced service fees on eligible DoorDash orders when you activate by 12/31/27. Plus, DashPass members get a $10 promo each month ($120 annually) to save on groceries, retail orders, and more.*


# 21: 5x on Peloton purchases:
#  - Earn 5x total points on eligible Peloton equipment and accessory purchases over $150 through 12/31/27.*

# 22: 5x on Lyft rides:
#  - Earn 5x on Lyft rides through 9/30/27.*

# 23: Explore additional benefits: 
#    1: Transfer Points: 
#       - Are you a member of a frequent travel program? With Chase Sapphire Preferred®, you can transfer your points to leading frequent travel programs.

#       Airline Travel Partners: 
#       - Aer Lingus, AerClub
#       - Air Canada Aeroplan
#       - British Airways Executive Club
#       - Flying Blue AIR FRANCE KLM
#       - Iberia Plus
#       - JetBlue TrueBlue
#       - Singapore Airlines KrisFlyer
#       - Southwest Airlines Rapid Rewards®
#       - United MileagePlus®
#       - Virgin Atlantic Flying Club

#       Hotel Travel Partners: 
#       - IHG® Rewards Club
#       - Marriott Bonvoy®
#       - World of Hyatt®
#       - Wyndham Rewards®

#    2: Partner benefits: 
#       DoorDash DashPass benefits: 
#        - Get a complimentary DashPass membership, a $120 value for 12 months. Enjoy $0 delivery fees and reduced service fees on eligible DoorDash orders when you activate by December 31, 2027.
#          Plus, DashPass members get a $10 promo each month ($120 annually) to save on groceries, retail orders, and more through December 31, 2027.

#       5x points on Lyft rides: 
#        - Earn 5x total points on Lyft rides with your Chase Sapphire Preferred card through September 30, 2027.
      
#       5x points on Peloton equipment:
#        - Earn 5x total points on eligible Peloton equipment and accessory purchases over $150 through December 31, 2027.

#    3: Travel & purchase coverage: 
#       - You're covered with built-in benefits - travel confidently & shop with confidence

#       - Trip Cancellation and Interruption Insurance: 
#          If your trip is canceled or cut short by sickness, severe weather or other covered situations, you can be reimbursed up to $10,000 per covered traveler and $20,000 per trip for your pre-paid, non-refundable travel expenses, including passenger fares, tours, and hotels.Δ

#       - Baggage Delay Insurance:
#          Reimburses you up to $100 a day for up to 5 days for essential purchases like toiletries and clothing when baggage is delayed over 6 hours.Δ

#       - Travel and Emergency Assistance: 
#          If you run into a problem while traveling away from home, this benefit provides legal and medical referrals and access to other travel and emergency assistance services. (You will be responsible for the cost of any goods or services obtained.)Δ

#       - Roadside Assistance
#          If you have a roadside emergency, call the service provider to dispatch the help you need. Roadside service fees will be billed to your card at time of dispatch.Δ

#       - Purchase Protection  
#          Covers your eligible new purchases for 120 days from the date of purchase against damage or theft up to $500 per item.Δ, ΔΔ

#       - Auto Rental Coverage 
#          Decline the rental company's collision insurance and charge the entire rental cost to your card. Coverage is primary and provides reimbursement up to $60,000 for theft and collision damage for most rental vehicles with an MSRP of $125,000 or less.Δ, ΔΔ

#       - Trip Delay Reimbursement
#          If your common carrier travel is delayed more than 12 hours or requires an overnight stay, you are covered for unreimbursed expenses, such as meals and lodging, up to $500 per covered traveler.Δ

#       - Travel Accident Insurance
#          When you pay for your air, bus, train or cruise transportation with your card, you are eligible to receive up to $500,000 in accidental death or dismemberment coverage.Δ

#       - Lost Luggage Reimbursement
#          Provides reimbursement up to $3,000 per covered traveler for the cost to repair or replace checked or carry-on baggage that is lost, damaged or stolen during a covered trip.Δ, ΔΔ

#       - Extended Warranty Protection
#          Extends the time period of the manufacturer's U.S. warranty by an additional year, on eligible warranties of three years or less, up to four years from the date of purchase.Δ

#       - NEW Emergency Evacuation and Transportation 
#          If you or a covered traveler are injured or become sick during a trip 100 miles or more from home that results in an emergency evacuation, you can be covered for medical services and transportation up to $100,000.Δ

#       - Guide to BenefitsOpens in a new window: 
#          Travel And Purchase Protection: These benefits are available when you use your card. Restrictions, limitations and exclusions apply. Most benefits are provided by unaffiliated companies who are solely responsible for the administration and claims. There are specific time limits and documentation requirements. For full coverage details, cardmembers can refer to their Guide to Benefits, provided after account opening, or call the number on the back of their card for assistance.
#          Specific limitations apply to New York residents: Auto Rental Coverage – inside the United States coverage is secondary to your personal automobile insurance. Lost Luggage Reimbursement – additionally limited to $2,000 per bag and $10,000 for all covered travelers per trip. Purchase Protection – coverage period is 90 days from the date of purchase.



#    4: No foreign transaction fees:
#       - You will pay no foreign transaction fees when you use your card for purchases made outside the United States.† For example, if you spend $5,000 internationally, you would avoid $150 in foreign transaction fees.

#    5: 24/7 access: 
#       - 24/7 Access to a Customer Service Specialist:
#          Enjoy 24/7 access to a customer service specialist from virtually anywhere in the world.

#    6: Spend Instantly: 
#       - Apply for a card, use it the same day:
#          Receive instant access to your card by adding it to a digital wallet, like Apple Pay®, Google Pay™ or Samsung Pay. Find out how at chase.com/digital/spend-instantlyOpens in a new window.

#    7: Credit Journey: 
#       - Stay informed and alert with Chase Credit Journey: 
#          Chase Credit Journey® is so much more than a free credit score. By enrolling in identity monitoring, you can receive alerts* when your information is found on the dark web or in a data breach. And, if your data is stolen, assistance is available to you.

#       - A personal concierge to assist you at every step: G
#          et a direct line to assistance that's assigned to you round-the-clock. They'll help you prepare for every step in the process and keep you informed.

#       - Coverage for select out-of-pocket costs: 
#          If identity theft happens, you may be covered for certain expenses.

#       - Assistance if you lose your wallet: 
#          Get help if you lose any of your credit cards, your ID or other important documents, no matter where you are in the world.

#       - And, it's free for everyone!
#          For more information or to enroll in Chase Credit Journey, please click hereOpens in a new window

# Delivery of alerts may be delayed for various reasons including technology failures and capacity limitations.

#    8: Chase Pay Over Time: 
#       Chase Pay Over Time* lets eligible Chase customers break up credit card purchases into budget friendly payments. There are two potential ways to pay over time:
      
#       - After purchase (formerly My Chase Plan®): 
#          Pay off an eligible purchase you've already made of $100 or more* in smaller, equal monthly payments. No Interest- just a fixed monthly fee† with plan durations that range from 3-24 months. Start a plan by selecting an eligible purchase with the "Pay Over Time" option next to the transaction amount in your credit card activity.

#       - At checkout: 
#          Chase Credit card members may have the option to create a payment plan at checkout on Amazon.com. Orders totaling $50 or more* using your eligible Chase credit card at Amazon.com could be eligible for Chase Pay Over Time. You will be able to view Chase Pay Over Time plan options (including the fixed APR and durations) at checkout.

#       - Keep in mind: 
#          Even though you may have an eligible card, access to Chase Pay Over Time is not guaranteed. Your ability to create a Chase Pay Over Time plan is based on a variety of factors, such as your creditworthiness, credit limit and account behavior, and may change from time to time.
#          For more information on Chase Pay Over Time features, please visit chase.com/chasepayovertimeOpens in a new window.



# OUTPUT FORMAT (This is just an example):
# Return ONLY a valid JSON array of objects:
# {
#   "Now with even more to love": [
#     {
#       "title": "$100 Chase Travel Hotel Credit",
#       "body": "Earn up to $100 in statement credits each account anniversary year for hotel stays purchased through Chase Travel.*"
#     },
#     {
#       "title": "Global Entry or TSA PreCheck® or NEXUS Application Fee credit",
#       "body": "Receive one statement credit of up to $120 every four years as reimbursement for the application fee charged to your card.*"
#     }
#   ]
# }
# ]
# """

# graph_config = {
#     "llm": {
#         "model": "ollama/qwen3:8b",
#         "temperature": 0,
#         "format": "json",
#         "base_url": "http://localhost:11434",
#         "model_tokens": 16384  # Increased to prevent truncation on long prompts
#     },
#     "embeddings": {
#         "model": "ollama/qwen3-embedding:4b",
#         "base_url": "http://localhost:11434"
#     }
# }

# smart_scraper_graph = SmartScraperGraph(
#     prompt=prompt,
#     source="https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred?CELL=6TKX",
#     config=graph_config
# )

# result = smart_scraper_graph.run()

# if isinstance(result, str):
#     parsed = json.loads(result)
#     print(json.dumps(parsed, indent=4))
# else:
#     print(json.dumps(result, indent=4))









import json
from scrapegraphai.graphs import SmartScraperGraph

# Keep the prompt concise — DO NOT paste raw text into this variable
prompt = "Extract all credit card details, rewards, and benefits into a structured JSON format."

graph_config = {
    "llm": {
        "model": "ollama/qwen3:8b",
        "temperature": 0,
        "format": "json",
        "base_url": "http://localhost:11434"
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
print(result)