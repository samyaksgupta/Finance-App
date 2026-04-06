# Finance Tracker Backend

A Python-based finance tracking system built with FastAPI, SQLAlchemy, and Pydantic.

## Features

- **Financial Records Management**: CRUD for income and expenses with advanced filtering (category, type, date range).
- **Analytics & Summaries**: Real-time balance calculation, category breakdown, and monthly totals.
- **Role-Based Access Control (RBAC)**:
  - **Viewer**: View records and summaries.
  - **Analyst**: View detailed insights and analytics.
  - **Admin**: Full control (create, update, delete records, manage users).
- **Robust Validation**: Strict input validation using Pydantic.
- **Auto-Documentation**: Built-in Swagger UI and Redoc.

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Database**: SQLite (SQLAlchemy supported)

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Navigate to the project directory:
   ```bash
   cd finance-backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Documentation

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **Redoc**: `http://127.0.0.1:8000/redoc`

## API Usage & Roles

The system simulates authentication via the `X-User-ID` header.

### Seed Users (Available on startup):

1. **Admin**: `X-User-ID: 1`
2. **Analyst**: `X-User-ID: 2`
3. **Viewer**: `X-User-ID: 3`

### Example Request

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/transactions/' \
  -H 'accept: application/json' \
  -H 'X-User-ID: 1'
```

## Project Structure

```text
finance-backend/
├── app/
│   ├── main.py          # App initialization & Routing
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations logic
│   ├── database.py      # DB configuration
│   ├── dependencies.py  # RBAC and Auth logic
│   └── routers/         # Endpoint definitions
├── requirements.txt
└── README.md
```

## Logic Highlights

- **Dynamic Summaries**: Instead of static fields, summaries are calculated on-the-fly using SQL aggregation.
- **Permission Middleware**: `require_role` dependency ensures that security logic is decoupled from business logic.
- **Surgical Updates**: CRUD operations support partial updates (`PATCH`-style via `PUT` with `exclude_unset`).
