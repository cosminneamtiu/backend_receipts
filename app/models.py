import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) # NEW: Required for Authentication
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    receipts = relationship("Receipt", back_populates="user")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    icon_name = Column(String, nullable=False)

    # Relationships
    receipts = relationship("Receipt", back_populates="category")

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    merchant_name = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String, default="RON")
    receipt_date = Column(Date, nullable=False, default=date.today)
    image_url = Column(String, nullable=False) # URL from Cloudinary/S3
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="receipts")
    category = relationship("Category", back_populates="receipts")
    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")

class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), nullable=False)
    item_name = Column(String, nullable=False)
    item_price = Column(Float, nullable=False)
    quantity = Column(Float, default=1.0)

    # Relationships
    receipt = relationship("Receipt", back_populates="items")