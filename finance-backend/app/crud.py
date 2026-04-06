from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from datetime import datetime
from typing import Optional, List

# Transaction CRUD
def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def get_transactions(
    db: Session, 
    user_id: Optional[int] = None, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None
):
    query = db.query(models.Transaction)
    if user_id:
        query = query.filter(models.Transaction.user_id == user_id)
    if category:
        query = query.filter(models.Transaction.category == category)
    if type:
        query = query.filter(models.Transaction.type == type)
    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.date <= end_date)
    if search:
        query = query.filter(models.Transaction.notes.ilike(f"%{search}%"))
    
    return query.offset(skip).limit(limit).all()

def create_user_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    db_transaction = models.Transaction(**transaction.model_dump(), user_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionUpdate):
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction:
        return None
    
    update_data = transaction.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int):
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # In a real app, hash the password
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=fake_hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Analytics logic
def get_financial_summary(db: Session, user_id: Optional[int] = None):
    # Base query for transactions
    query = db.query(models.Transaction)
    if user_id:
        query = query.filter(models.Transaction.user_id == user_id)
    
    all_transactions = query.all()
    
    income = sum(t.amount for t in all_transactions if t.type == "income")
    expenses = sum(t.amount for t in all_transactions if t.type == "expense")
    
    # Category breakdown using SQL grouping for efficiency
    breakdown_query = db.query(
        models.Transaction.category,
        func.sum(models.Transaction.amount).label('total')
    )
    if user_id:
        breakdown_query = breakdown_query.filter(models.Transaction.user_id == user_id)
    
    category_totals = breakdown_query.group_by(models.Transaction.category).all()
    
    # Recent activity
    recent = query.order_by(models.Transaction.date.desc()).limit(5).all()
    
    return {
        "total_income": income,
        "total_expenses": expenses,
        "current_balance": income - expenses,
        "category_breakdown": [{"category": c, "total": t} for c, t in category_totals],
        "recent_activity": recent
    }
