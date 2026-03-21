import asyncio
from sqlalchemy.future import select
from sqlalchemy import delete
from app.database import AsyncSessionLocal
from app.models import User, Category, Receipt, ReceiptItem
from app.services.auth import AuthService # NEW: Imported to hash the password

async def seed_data():
    print("🌱 Starting database seed...")
    
    async with AsyncSessionLocal() as db:
        # 1. Check/Create Test User with HASHED PASSWORD
        result = await db.execute(select(User).where(User.email == "student@utcn.ro"))
        existing_user = result.scalars().first()
        
        if not existing_user:
            print("👤 Creating test user...")
            # We must hash the password before saving it to the database!
            hashed_pw = AuthService.get_password_hash("password123")
            test_user = User(
                email="student@utcn.ro", 
                hashed_password=hashed_pw
            )
            db.add(test_user)
            await db.commit()
            await db.refresh(test_user)
            user_id = test_user.id
            print(f"✅ Test User created with email: student@utcn.ro | password: password123")
        else:
            user_id = existing_user.id
            print(f"ℹ️ User already exists: {user_id}")

        # 2. CLEAR EXISTING DATA (To avoid Foreign Key errors)
        print("🧹 Clearing old data to avoid Foreign Key conflicts...")
        await db.execute(delete(ReceiptItem)) # Delete items first
        await db.execute(delete(Receipt))     # Then receipts
        await db.execute(delete(Category))    # Now we can safely delete categories
        
        # 3. Create the 10 English Categories
        new_categories = [
            Category(id=1, name="Transport", icon_name="directions_bus"),
            Category(id=2, name="Others", icon_name="more_horiz"),
            Category(id=3, name="Cash", icon_name="atm"),
            Category(id=4, name="Shopping", icon_name="shopping_bag"),
            Category(id=5, name="Groceries", icon_name="local_grocery_store"),
            Category(id=6, name="Dining", icon_name="restaurant"),
            Category(id=7, name="Health", icon_name="medical_services"),
            Category(id=8, name="Household", icon_name="home"),
            Category(id=9, name="Services", icon_name="build"),
            Category(id=10, name="Entertainment", icon_name="movie"),
        ]
        
        db.add_all(new_categories)
        await db.commit()
        print(f"✅ Created {len(new_categories)} English categories successfully!")

    print("\n🎉 Seeding complete! Database is clean and ready.")

if __name__ == "__main__":
    asyncio.run(seed_data())