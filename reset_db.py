import asyncio
from app.database import engine
# IMPORTANT: We must import all models so SQLAlchemy knows they exist before creating tables
from app.models import Base, User, Category, Receipt, ReceiptItem

async def reset_database():
    print("⚠️ WARNING: Dropping all database tables...")
    
    async with engine.begin() as conn:
        # 1. Drop all existing tables (This deletes all old data/schemas)
        await conn.run_sync(Base.metadata.drop_all)
        print("🗑️ All tables dropped successfully.")

        # 2. Recreate all tables using the new models.py (which includes hashed_password)
        print("🏗️ Recreating tables with the latest schema...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ New tables created successfully!")

if __name__ == "__main__":
    asyncio.run(reset_database())