from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, func  # Added func for the SUM() calculation
from typing import List
import uuid
from datetime import datetime
from sqlalchemy.orm import selectinload

# Import our database connection and models/schemas
from app.database import get_db
from app.models import Receipt, Category, User, ReceiptItem
from app.schemas import ReceiptResponse, ReceiptCreate, ReceiptUpdate
from app.services.ocr import analyze_receipt_with_openai
from app.services.s3 import upload_image_to_s3

app = FastAPI(
    title="Smart Receipt Scanner API",
    description="Backend for the Bachelor's Thesis Receipt & Finance Tracker",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "API is online and ready! 🚀"}

# ==========================================
# RECEIPT ENDPOINTS (/api/v1/receipts)
# ==========================================

@app.post("/api/v1/receipts/scan", response_model=ReceiptResponse)
async def scan_receipt(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    user_query = await db.execute(select(User).limit(1))
    test_user = user_query.scalars().first()
    if not test_user:
        raise HTTPException(status_code=400, detail="No users in database. Run seed_db.py first!")

    try:
        s3_url = await upload_image_to_s3(file)
        ai_data = await analyze_receipt_with_openai(s3_url)
        parsed_date = datetime.strptime(ai_data.receipt_date, "%Y-%m-%d").date()

        new_receipt = Receipt(
            user_id=test_user.id,
            category_id=ai_data.category_id,
            merchant_name=ai_data.merchant_name,
            total_amount=ai_data.total_amount,
            currency=ai_data.currency,
            receipt_date=parsed_date,
            image_url=s3_url
        )
        db.add(new_receipt)
        await db.flush() 

        for item in ai_data.items:
            db_item = ReceiptItem(
                receipt_id=new_receipt.id,
                item_name=item.item_name,
                item_price=item.item_price,
                quantity=item.quantity
            )
            db.add(db_item)

        await db.commit()
        
        query = select(Receipt).options(selectinload(Receipt.items)).where(Receipt.id == new_receipt.id)
        result = await db.execute(query)
        return result.scalars().first()

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/receipts", response_model=List[ReceiptResponse])
async def get_all_receipts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    query = select(Receipt).options(selectinload(Receipt.items)).order_by(Receipt.receipt_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@app.get("/api/v1/receipts/{receipt_id}", response_model=ReceiptResponse)
async def get_single_receipt(receipt_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    query = select(Receipt).options(selectinload(Receipt.items)).where(Receipt.id == receipt_id)
    result = await db.execute(query)
    receipt = result.scalars().first()
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt

@app.put("/api/v1/receipts/{receipt_id}", response_model=ReceiptResponse)
async def update_receipt(receipt_id: uuid.UUID, receipt_data: ReceiptUpdate, db: AsyncSession = Depends(get_db)):
    # 1. Fetch current receipt with items
    query = select(Receipt).options(selectinload(Receipt.items)).where(Receipt.id == receipt_id)
    result = await db.execute(query)
    db_receipt = result.scalars().first()

    if not db_receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    # 2. Update main receipt fields (exclude items from this loop)
    update_data = receipt_data.model_dump(exclude_unset=True, exclude={"items"})
    for key, value in update_data.items():
        setattr(db_receipt, key, value)

    try:
        # 3. Handle Items Update (if items list is provided)
        if receipt_data.items is not None:
            # Delete existing items for this receipt
            await db.execute(delete(ReceiptItem).where(ReceiptItem.receipt_id == receipt_id))
            
            # Add new items
            for item in receipt_data.items:
                new_item = ReceiptItem(
                    receipt_id=receipt_id,
                    item_name=item.item_name,
                    item_price=item.item_price,
                    quantity=item.quantity
                )
                db.add(new_item)

        await db.commit()
        
        # 4. Refresh and return final state
        final_query = select(Receipt).options(selectinload(Receipt.items)).where(Receipt.id == receipt_id)
        final_result = await db.execute(final_query)
        return final_result.scalars().first()

    except Exception as e:
        await db.rollback()
        print(f"Update error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/v1/receipts/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_receipt(receipt_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    query = select(Receipt).where(Receipt.id == receipt_id)
    result = await db.execute(query)
    db_receipt = result.scalars().first()

    if not db_receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    try:
        await db.delete(db_receipt)
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


# ==========================================
# STATISTICS ENDPOINTS (/api/v1/stats)
# ==========================================

@app.get("/api/v1/stats/categories")
async def get_category_stats(db: AsyncSession = Depends(get_db)):
    """
    Returns data for the Pie Chart: Grouped by category name, summed by total_amount.
    """
    # Join Receipts with Categories to get the Name + Total
    query = (
        select(
            Category.name, 
            func.sum(Receipt.total_amount).label("total"),
            Category.icon_name
        )
        .join(Receipt, Receipt.category_id == Category.id)
        .group_by(Category.name, Category.icon_name)
    )
    
    result = await db.execute(query)
    stats = result.all()
    
    # Return a clean list for Flutter to parse
    return [
        {"category": row[0], "amount": float(row[1]), "icon": row[2]} 
        for row in stats
    ]
