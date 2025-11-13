#!/bin/bash
# Check if Streamlit is running and start it if not

cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF

echo "Checking if Streamlit is running..."

# Check if port 8501 is in use
if lsof -ti:8501 > /dev/null 2>&1; then
    echo "✅ Streamlit is already running!"
    echo "🌐 Open your browser: http://localhost:8501"
    echo ""
    echo "Process info:"
    ps aux | grep streamlit | grep -v grep
else
    echo "⏳ Streamlit not running. Starting it now..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check dependencies
    echo "Checking dependencies..."
    python3 -c "import streamlit, pyarrow, plotly, pandas" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "❌ Missing dependencies. Please install:"
        echo "   conda install -c conda-forge pyarrow -y"
        echo "   pip install streamlit plotly pandas"
        exit 1
    fi
    
    echo "✅ Dependencies OK"
    echo "🚀 Starting Streamlit..."
    
    # Start Streamlit in background
    nohup streamlit run app.py > streamlit.log 2>&1 &
    
    # Wait a bit for it to start
    sleep 5
    
    # Check if it started
    if lsof -ti:8501 > /dev/null 2>&1; then
        echo "✅ Streamlit started successfully!"
        echo "🌐 Open your browser: http://localhost:8501"
        echo ""
        echo "Log file: streamlit.log"
    else
        echo "❌ Failed to start. Check streamlit.log for errors:"
        tail -20 streamlit.log
        exit 1
    fi
fi

echo ""
echo "To stop Streamlit:"
echo "  kill \$(lsof -ti:8501)"

