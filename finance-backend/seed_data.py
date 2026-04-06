import random
from datetime import datetime, timedelta
from app.database import SessionLocal
from app import crud, schemas, models

def seed_100_records():
    db = SessionLocal()
    admin = crud.get_user_by_username(db, "admin")
    if not admin:
        print("Admin user not found. Please run the app once first.")
        return

    categories = {
        "income": ["Salary", "Freelance", "Investment", "Gift"],
        "expense": ["Rent", "Food", "Travel", "Entertainment", "Utilities", "Health", "Shopping"]
    }

    print(f"Seeding 100 records for user: {admin.username}...")

    for _ in range(100):
        t_type = random.choice(["income", "expense"])
        category = random.choice(categories[t_type])
        
        # Random amount
        if t_type == "income":
            amount = round(random.uniform(500, 5000), 2)
        else:
            amount = round(random.uniform(10, 500), 2)
            
        # Random date within the last 6 months
        days_ago = random.randint(0, 180)
        date = datetime.utcnow() - timedelta(days=days_ago)
        
        notes = f"Mock {t_type} for {category}"
        
        transaction = schemas.TransactionCreate(
            amount=amount,
            type=t_type,
            category=category,
            date=date,
            notes=notes
        )
        crud.create_user_transaction(db, transaction, admin.id)

    print("✅ Successfully seeded 100 records!")
    db.close()

if __name__ == "__main__":
    seed_100_records()
