# Install PyArrow - Quick Guide

PyArrow is required for Streamlit. Here are the installation options:

## Option 1: Run the Installation Script

```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
./install_pyarrow.sh
```

## Option 2: Manual Installation

### Using Conda (Recommended)
```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
source venv/bin/activate
conda install -c conda-forge pyarrow -y
```

### Using Pip
```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
source venv/bin/activate
pip install pyarrow
```

## Option 3: Use Conda Environment (Alternative)

If the venv has issues, create a new conda environment:

```bash
conda create -n autoloan python=3.10
conda activate autoloan
conda install -c conda-forge streamlit plotly pandas pyarrow
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
streamlit run app.py
```

## Verify Installation

After installing, verify it works:

```bash
source venv/bin/activate
python3 -c "import pyarrow; print('✅ PyArrow installed!')"
```

## Then Run the App

```bash
./run_app.sh
# or
streamlit run app.py
```

The app will open at http://localhost:8501

