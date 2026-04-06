from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base, SessionLocal
from .routers import transactions, analytics, users
from . import crud, schemas, models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... (rest of lifespan code)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not crud.get_user_by_username(db, "admin"):
            admin = crud.create_user(db, schemas.UserCreate(
                username="admin", 
                email="admin@example.com", 
                password="adminpassword", 
                role=schemas.UserRole.ADMIN
            ))
            crud.create_user(db, schemas.UserCreate(
                username="analyst", 
                email="analyst@example.com", 
                password="analystpassword", 
                role=schemas.UserRole.ANALYST
            ))
            crud.create_user(db, schemas.UserCreate(
                username="viewer", 
                email="viewer@example.com", 
                password="viewerpassword", 
                role=schemas.UserRole.VIEWER
            ))
            crud.create_user_transaction(db, schemas.TransactionCreate(
                amount=5000.0, 
                type=schemas.TransactionType.INCOME, 
                category="Salary", 
                notes="Monthly salary"
            ), user_id=admin.id)
    finally:
        db.close()
    yield

app = FastAPI(
    title="Finance Tracker Backend",
    description="A Python-based finance tracking system with role-based access control.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Finance Tracker API",
        "docs": "/docs",
        "health": "Healthy"
    }
