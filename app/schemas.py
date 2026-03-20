from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

# ---------------------------------------
# CATEGORY SCHEMAS
# ---------------------------------------
class CategoryBase(BaseModel):
    name: str
    icon_name: str

class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------
# RECEIPT ITEM SCHEMAS
# ---------------------------------------
class ReceiptItemBase(BaseModel):
    item_name: str
    item_price: float
    quantity: float = 1.0

class ReceiptItemCreate(ReceiptItemBase):
    pass

class ReceiptItemResponse(ReceiptItemBase):
    id: UUID
    receipt_id: UUID
    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------
# RECEIPT UPDATE SCHEMA
# ---------------------------------------
# Placed here so it can "see" ReceiptItemCreate
class ReceiptUpdate(BaseModel):
    merchant_name: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    receipt_date: Optional[date] = None
    category_id: Optional[int] = None
    items: Optional[List[ReceiptItemCreate]] = None 
    
    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------
# RECEIPT SCHEMAS
# ---------------------------------------
class ReceiptBase(BaseModel):
    merchant_name: str
    total_amount: float
    currency: str = "RON"
    receipt_date: date
    image_url: str

class ReceiptCreate(ReceiptBase):
    category_id: int
    user_id: UUID
    items: Optional[List[ReceiptItemCreate]] = []

class ReceiptResponse(ReceiptBase):
    id: UUID
    category_id: int
    user_id: UUID
    created_at: datetime
    items: List[ReceiptItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)