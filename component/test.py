import json
from typing import List, Optional
from pydantic import BaseModel, Field
from scrapegraphai.graphs import SmartScraperGraph

# 1. Define structured Pydantic models for nested card details
# class WelcomeBonus(BaseModel):
#     points_or_cash: str = Field(description="The bonus amount, e.g., '75,000 points'")
#     spend_requirement: str = Field(description="Required spend amount, e.g., '$5,000'")
#     timeframe: str = Field(description="Timeframe to reach spend, e.g., 'first 3 months'")
#     offer_end_date: Optional[str] = Field(None, description="Offer end date or notice if applicable")

# class PricingAndFees(BaseModel):
#     annual_fee: str = Field(description="Annual fee amount, e.g., '$95'")
#     apr_range: str = Field(description="Regular purchase APR range, e.g., '19.24%–27.49% variable'")
#     foreign_transaction_fee: str = Field(description="Foreign transaction fee, e.g., '0%' or '$0'")

# class RewardMultiplier(BaseModel):
#     category: str = Field(description="Category name, e.g., 'Travel', 'Dining', 'Gas'")
#     multiplier: str = Field(description="E.g., '5x', '3x', '1x'")
#     notes_or_exclusions: Optional[str] = Field(None, description="E.g., 'purchased through Chase Travel'")

# class FlexibleCredit(BaseModel):
#     name: str = Field(description="Name of the credit, e.g., '$100 Chase Travel Hotel Credit'")
#     amount: str = Field(description="Dollar value or benefit frequency, e.g., '$100 annually'")
#     details: str = Field(description="Conditions to receive or use the credit")

# class PartnerPerk(BaseModel):
#     partner_name: str = Field(description="e.g., 'DoorDash', 'Lyft', 'Peloton'")
#     benefit: str = Field(description="Details of the benefit or rate")
#     expiration_date: Optional[str] = Field(None, description="Expiration date if noted")

# class TravelPartner(BaseModel):
#     partner_type: str = Field(description="'Airline' or 'Hotel'")
#     program_name: str = Field(description="Name of the loyalty program")

# class InsuranceCoverage(BaseModel):
#     benefit_name: str = Field(description="e.g., 'Trip Cancellation Insurance', 'Primary Auto Rental Coverage'")
#     max_coverage_limit: Optional[str] = Field(None, description="e.g., '$10,000 per traveler'")
#     summary: str = Field(description="Brief explanation of what is covered")

# class CreditCardDetails(BaseModel):
#     card_name: str = Field(description="Full official name of the card")
#     issuer: str = Field(description="Issuing bank, e.g., 'Chase'")
#     network: Optional[str] = Field(None, description="e.g., 'Visa', 'Mastercard', 'Amex'")
#     welcome_bonus: Optional[WelcomeBonus] = None
#     pricing_and_fees: PricingAndFees
#     reward_multipliers: List[RewardMultiplier] = Field(default_factory=list)
#     credits: List[FlexibleCredit] = Field(default_factory=list)
#     partner_perks: List[PartnerPerk] = Field(default_factory=list)
#     transfer_partners: List[TravelPartner] = Field(default_factory=list)
#     insurance_and_protections: List[InsuranceCoverage] = Field(default_factory=list)
#     other_features: List[str] = Field(default_factory=list, description="Other perks like Pay Over Time, 24/7 Concierge, Credit Journey")


# 2. ScrapeGraphAI Config
graph_config = {
    "llm": {
        "model": "ollama/qwen3:8b",
        "temperature": 0,
        "base_url": "http://localhost:11434",
        "model_tokens": 8192 # <--- Fixes the token warning
    },
    "embeddings": {
        "model": "ollama/qwen3-embedding:4b",
        "base_url": "http://localhost:11434"
    }
}

prompt = (
    "Extract all credit card information into the exact provided schema. "
    "Be precise and ensure no rewards, insurance limits, fees, or partner list items are omitted."
)

# 3. Pass the Pydantic schema into SmartScraperGraph
smart_scraper_graph = SmartScraperGraph(
    prompt=prompt,
    source="https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred?CELL=6TKX",
    # schema=CreditCardDetails,
    config=graph_config
)

result = smart_scraper_graph.run()

# 4. Print clean JSON output
print(json.dumps(result, indent=4))