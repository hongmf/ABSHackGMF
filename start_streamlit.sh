#!/bin/bash
# Start Streamlit App

cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are available
echo "Checking dependencies..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not found. Please install: pip install streamlit"
    exit 1
fi

if ! python3 -c "import pyarrow" 2>/dev/null; then
    echo "❌ PyArrow not found. Please install: conda install -c conda-forge pyarrow -y"
    exit 1
fi

echo "✅ Dependencies OK"
echo "🚀 Starting Streamlit app..."
echo ""
echo "The app will open in your browser at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

# Start Streamlit
streamlit run app.py

