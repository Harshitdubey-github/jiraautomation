#!/bin/bash

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js 14 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv backend/venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source backend/venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start backend server in the background
echo "Starting backend server..."
cd backend
python -m uvicorn main:app --reload &
BACKEND_PID=$!
cd ..

# Start frontend development server
echo "Starting frontend development server..."
cd frontend
npm start

# Kill backend server when frontend is stopped
kill $BACKEND_PID 