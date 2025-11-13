# Troubleshooting: Connection Refused Error

If you're seeing "ERR_CONNECTION_REFUSED" or "localhost refused to connect", it means Streamlit isn't running.

## Solution: Start Streamlit Manually

### Option 1: Use the Startup Script (Easiest)

```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
./start_streamlit.sh
```

This will:
- Check dependencies
- Start Streamlit
- Open in your browser automatically

### Option 2: Manual Start

```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
source venv/bin/activate
streamlit run app.py
```

### Option 3: Check if Port is Already in Use

If port 8501 is already in use, try a different port:

```bash
streamlit run app.py --server.port 8502
```

Then open: http://localhost:8502

## Verify Dependencies

Make sure everything is installed:

```bash
source venv/bin/activate
python3 -c "import streamlit; import pyarrow; import plotly; import pandas; print('✅ All OK')"
```

## Common Issues

1. **PyArrow not installed**: 
   ```bash
   conda install -c conda-forge pyarrow -y
   ```

2. **Virtual environment not activated**:
   ```bash
   source venv/bin/activate
   ```

3. **Wrong directory**:
   Make sure you're in: `/Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF`

## Expected Output

When Streamlit starts successfully, you should see:

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

The browser should open automatically, or you can manually navigate to http://localhost:8501

