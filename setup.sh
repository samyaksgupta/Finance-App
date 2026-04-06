#!/bin/bash

# Finance Tracker System - Setup Script

echo "🚀 Starting Finance Tracker System setup..."

# 1. Backend Setup
echo "📂 Setting up Backend..."
cd finance-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# 2. Frontend Setup
echo "📂 Setting up Frontend..."
cd finance-frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "To run the system:"
echo "1. Start Backend: cd finance-backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "2. Start Frontend: cd finance-frontend && npm run dev"
echo ""
echo "API Documentation will be at: http://127.0.0.1:8000/docs"
echo "Frontend will be at: http://localhost:5173"
