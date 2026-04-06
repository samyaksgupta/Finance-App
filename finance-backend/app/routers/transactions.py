from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .. import crud, schemas, dependencies
from ..database import get_db

from fastapi.responses import StreamingResponse
import io
import csv

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/", response_model=List[schemas.Transaction])
def read_transactions(
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    type: Optional[schemas.TransactionType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.is_viewer_or_above)
):
    """
    View financial records. (Viewer, Analyst, Admin)
    """
    # If not admin, restrict to own transactions
    user_id = None if current_user.role == "admin" else current_user.id
    
    return crud.get_transactions(
        db, user_id=user_id, skip=skip, limit=limit, 
        category=category, type=type, start_date=start_date, end_date=end_date,
        search=search
    )

@router.get("/export/csv")
def export_transactions_csv(
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.is_viewer_or_above)
):
    """
    Export all transactions to a CSV file. (Viewer, Analyst, Admin)
    """
    user_id = None if current_user.role == "admin" else current_user.id
    transactions = crud.get_transactions(db, user_id=user_id, limit=1000)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Amount", "Type", "Category", "Date", "Notes"])
    
    for t in transactions:
        writer.writerow([t.id, t.amount, t.type, t.category, t.date, t.notes])
    
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=transactions.csv"})

@router.post("/", response_model=schemas.Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.is_admin)
):
    """
    Create a new record. (Admin only)
    """
    return crud.create_user_transaction(db=db, transaction=transaction, user_id=current_user.id)

@router.get("/{transaction_id}", response_model=schemas.Transaction)
def read_transaction(
    transaction_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.is_viewer_or_above)
):
    """
    View a specific record. (Viewer, Analyst, Admin)
    """
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Ownership check
    if current_user.role != "admin" and db_transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this transaction")
        
    return db_transaction

@router.put("/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(
    transaction_id: int, 
    transaction: schemas.TransactionUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.is_admin)
):
    """
    Update a record. (Admin only)
    """
    db_transaction = crud.update_transaction(db, transaction_id=transaction_id, transaction=transaction)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.delete("/{transaction_id}", response_model=schemas.Transaction)
def delete_transaction(
    transaction_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.is_admin)
):
    """
    Delete a record. (Admin only)
    """
    db_transaction = crud.delete_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction
