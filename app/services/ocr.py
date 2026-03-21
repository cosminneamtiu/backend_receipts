# app/services/ocr.py
import os
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Initialize the async OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# We define exactly what we want OpenAI to return
class ParsedItem(BaseModel):
    item_name: str
    item_price: float
    quantity: float

class ParsedReceipt(BaseModel):
    merchant_name: str
    total_amount: float
    currency: str
    receipt_date: str # Format: YYYY-MM-DD
    category_id: int
    items: List[ParsedItem]

async def analyze_receipt_with_openai(image_url: str) -> ParsedReceipt:
    print("🧠 Sending image to OpenAI for analysis...")
    
    prompt = """
    You are an expert accountant AI. Analyze the provided receipt image.
    Extract the merchant name, total amount, currency (default to RON if not specified), and the date (format strictly as YYYY-MM-DD).
    Also extract the line items (name, price, quantity).
    
    CRITICAL: Categorize the receipt by assigning ONE integer 'category_id' from this exact list based on the merchant name and items:
    
    1 = Transport (e.g., OMV, Petrom, Rompetrol, Uber, Bolt, CFR, Metro)
    2 = Others (e.g., Miscellaneous items that do not fit anywhere else)
    3 = Cash (e.g., ATM Withdrawals - rarely used for physical receipts)
    4 = Shopping (e.g., Zara, H&M, Nike, Emag, Altex, Mall stores)
    5 = Groceries (e.g., Kaufland, Mega Image, Lidl, Auchan, Carrefour, Profi)
    6 = Dining (e.g., McDonald's, KFC, Starbucks, local restaurants, bars, cafes)
    7 = Health (e.g., Catena, Dr Max, Farmacia Tei, Regina Maria, Dentists)
    8 = Household (e.g., Dedeman, IKEA, Leroy Merlin, Hornbach, cleaning supplies)
    9 = Services (e.g., Electrica, Digi, Vodafone, Haircuts, Car repairs, Subscriptions)
    10 = Entertainment (e.g., Cinema City, Steam, UNTOLD, Concert tickets, Museums)
    
    Look at the merchant name and the items purchased to make your best logical guess. If completely unsure, use 2 (Others).
    """

    try:
        # We use gpt-4o-mini because it's insanely fast and cheap for testing
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-mini", 
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            # This forces the AI to return data that matches our Python class!
            response_format=ParsedReceipt, 
        )
        
        parsed_data = response.choices[0].message.parsed
        print(f"✅ OpenAI successfully parsed the receipt from {parsed_data.merchant_name}! Assigned Category ID: {parsed_data.category_id}")
        return parsed_data
        
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        raise Exception("Failed to analyze the receipt with AI.")