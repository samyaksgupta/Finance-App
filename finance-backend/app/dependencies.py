from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from .database import get_db
from . import crud, models

# For simplicity, we'll use a 'X-User-ID' header to simulate authentication
def get_current_user(db: Session = Depends(get_db), x_user_id: int = Header(...)):
    user = crud.get_user(db, user_id=x_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

def require_role(allowed_roles: list):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role: {current_user.role}",
            )
        return current_user
    return role_checker

# Helper dependencies
def is_admin(current_user: models.User = Depends(require_role(["admin"]))):
    return current_user

def is_analyst_or_admin(current_user: models.User = Depends(require_role(["analyst", "admin"]))):
    return current_user

def is_viewer_or_above(current_user: models.User = Depends(require_role(["viewer", "analyst", "admin"]))):
    return current_user
