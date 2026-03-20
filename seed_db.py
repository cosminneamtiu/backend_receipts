import asyncio
from sqlalchemy.future import select
from sqlalchemy import delete
from app.database import AsyncSessionLocal
from app.models import User, Category

async def seed_data():
    print("🌱 Starting database seed...")
    
    async with AsyncSessionLocal() as db:
        # 1. Check/Create Test User
        result = await db.execute(select(User).limit(1))
        existing_user = result.scalars().first()
        
        if not existing_user:
            print("👤 Creating test user...")
            test_user = User(email="student@utcn.ro")
            db.add(test_user)
            await db.commit()
            await db.refresh(test_user)
            user_id = test_user.id
            print(f"✅ Test User created: {user_id}")
        else:
            user_id = existing_user.id
            print(f"ℹ️ User already exists: {user_id}")

        # 2. Update Categories to match the "Revolut-style" list
        print("🏷️ Updating categories to English financial standards...")
        
        # We delete old categories to avoid ID conflicts and stale data
        # Note: If you have many receipts already, this might fail due to FK constraints.
        # In a dev environment, it's usually best to wipe and re-seed.
        await db.execute(delete(Category))
        
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
        print(f"✅ Created {len(new_categories)} categories successfully!")

    print("\n🎉 Seeding complete! Your Pie Chart categories are now synced.")

if __name__ == "__main__":
    asyncio.run(seed_data())