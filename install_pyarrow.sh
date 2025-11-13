#!/bin/bash
# Install PyArrow for Streamlit

cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
source venv/bin/activate

echo "Installing PyArrow..."

# Try method 1: pip with pre-built wheel
echo "Method 1: Trying pip with pre-built wheel..."
pip install --only-binary :all: pyarrow 2>&1 | tail -3

# Check if it worked
if python3 -c "import pyarrow" 2>/dev/null; then
    echo "✅ SUCCESS! PyArrow installed via pip"
    exit 0
fi

# Try method 2: conda
echo "Method 2: Trying conda..."
conda install -c conda-forge pyarrow -y 2>&1 | tail -5

# Check if it worked
if python3 -c "import pyarrow" 2>/dev/null; then
    echo "✅ SUCCESS! PyArrow installed via conda"
    exit 0
fi

# Try method 3: pip without build isolation
echo "Method 3: Trying pip without build isolation..."
pip install pyarrow --no-build-isolation 2>&1 | tail -5

# Final check
if python3 -c "import pyarrow" 2>/dev/null; then
    echo "✅ SUCCESS! PyArrow installed"
    exit 0
else
    echo "❌ Could not install PyArrow automatically"
    echo "Please try manually:"
    echo "  conda install -c conda-forge pyarrow -y"
    exit 1
fi

