from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas, dependencies
from ..database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary", response_model=schemas.FinancialSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.is_viewer_or_above)
):
    """
    Get financial summary. (Viewer, Analyst, Admin)
    """
    # If not admin, restrict to own summary
    user_id = None if current_user.role == "admin" else current_user.id
    return crud.get_financial_summary(db, user_id=user_id)

@router.get("/detailed-insights")
def get_insights(
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.is_analyst_or_admin)
):
    """
    Get detailed financial insights. (Analyst, Admin only)
    """
    summary = get_summary(db, current_user)
    
    # Simple analyst logic: suggest saving if balance is positive
    savings_advice = "Your balance is positive. Consider investing!" if summary["current_balance"] > 0 else "Your expenses are high. Review your categories."
    
    return {
        "summary": summary,
        "analyst_notes": savings_advice,
        "insight_level": "Detailed Analysis"
    }
