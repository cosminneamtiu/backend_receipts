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
    
    CRITICAL: Categorize the receipt by assigning ONE integer 'category_id' from this list based on the merchant name:
    1 = Groceries (e.g., Kaufland, Mega Image, Lidl, Auchan, Profi)
    2 = Transport (e.g., OMV, Petrom, Uber, Bolt, CFR)
    3 = Utilities (e.g., Electrica, Digi, Vodafone)
    4 = Entertainment (e.g., Cinema, Steam, UNTOLD)
    5 = Health (e.g., Catena, Dr Max, Farmacia Tei)
    6 = Other (If you are completely unsure, use 6)
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
        print(f"✅ OpenAI successfully parsed the receipt from {parsed_data.merchant_name}!")
        return parsed_data
        
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        raise Exception("Failed to analyze the receipt with AI.")