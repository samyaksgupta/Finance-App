# Finance Tracker System

A complete full-stack finance tracking system featuring a **Python (FastAPI)** backend and a **React (TypeScript)** frontend.

## 🌟 Key Features

- **Financial Records Management**: CRUD operations for income and expenses with advanced filtering.
- **Summary & Analytics**: Real-time balance calculations and category breakdowns.
- **Visual Analytics**: Interactive charts (Gauge, Pie, and Bar charts) for better financial insight.
- **Dark/Light Mode**: Seamless theme switching with a modern midnight-blue dark theme.
- **Role-Based Access Control (RBAC)**: Distinct permissions for Admin, Analyst, and Viewer.
- **Mock Data Generator**: Populate the system with 100+ records for instant testing.

## 📁 Project Structure

```text
Finance-App/
├── finance-backend/        # FastAPI Backend (Python)
├── finance-frontend/       # React Frontend (TypeScript)
├── interview/              # Technical documentation for interviews
├── README.md               # Main project documentation
└── setup.sh                # Automated setup script
```

## 🚀 Quick Setup

1. **Navigate to the project directory**:
   ```bash
   cd Finance-App
   ```

2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

## 🛠️ Running the System

To start the complete system, you need two terminal windows:

### Terminal 1: Backend
```bash
cd finance-backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Terminal 2: Frontend
```bash
cd finance-frontend
npm run dev
```

## 👥 Roles for Testing
- **Admin User** (`ID: 1`): Full access.
- **Analyst User** (`ID: 2`): View-only + Analytics.
- **Viewer User** (`ID: 3`): Basic view-only.

## 🧪 Mock Data
To seed 100 random records:
```bash
cd finance-backend
source venv/bin/activate
python3 seed_data.py
```
