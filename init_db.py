import asyncio
from app.database import engine, Base
# We must import the models here so SQLAlchemy knows they exist before creating tables
from app.models import User, Category, Receipt, ReceiptItem

async def create_tables():
    print("⏳ Connecting to PostgreSQL...")
    async with engine.begin() as conn:
        print("🔨 Building tables (Users, Categories, Receipts, ReceiptItems)...")
        # This translates our Python classes into actual PostgreSQL tables
        await conn.run_sync(Base.metadata.create_all)
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(create_tables())