# Step-by-Step: Start Streamlit App

## If you're getting "Connection Refused" errors, follow these exact steps:

### Step 1: Open Terminal
Open a **new** terminal window (Command + Space, type "Terminal")

### Step 2: Navigate to the Project
```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
```

### Step 3: Activate Virtual Environment
```bash
source venv/bin/activate
```

You should see `(venv)` appear in your prompt.

### Step 4: Test Dependencies (Important!)
```bash
python3 -c "import streamlit; print('Streamlit OK')"
python3 -c "import pyarrow; print('PyArrow OK')"
python3 -c "import plotly; print('Plotly OK')"
python3 -c "import pandas; print('Pandas OK')"
```

**If ANY of these fail:**

- For PyArrow: `conda install -c conda-forge pyarrow -y`
- For others: `pip install streamlit plotly pandas`

### Step 5: Start Streamlit
```bash
streamlit run app.py
```

### Step 6: Wait for Output
You should see:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Step 7: Open Browser
- The browser should open automatically
- If not, manually go to: http://localhost:8501

## Important Notes

1. **Keep the terminal open** - Don't close it while using the app
2. **To stop the app** - Press `Ctrl+C` in the terminal
3. **If port 8501 is busy** - Try: `streamlit run app.py --server.port 8502`

## Alternative: Use Conda Environment

If venv continues to have issues:

```bash
# Create new conda environment
conda create -n autoloan python=3.10
conda activate autoloan

# Install all dependencies
conda install -c conda-forge streamlit plotly pandas pyarrow boto3 python-dotenv

# Navigate to project
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF

# Run app
streamlit run app.py
```

## Still Not Working? Debug Steps

### Check if Streamlit is running:
```bash
ps aux | grep streamlit
```

### Check if port is open:
```bash
lsof -ti:8501
```

### Check for error logs:
Look at the terminal output when you run `streamlit run app.py` - what error messages do you see?

### Test with simple app:
Create a test file:
```bash
echo "import streamlit as st; st.write('Hello')" > test.py
streamlit run test.py
```

If this works, there might be an issue with app.py.

## Common Error Solutions

**"ModuleNotFoundError: No module named 'pyarrow'"**
```bash
conda install -c conda-forge pyarrow -y
```

**"command not found: streamlit"**
```bash
pip install streamlit
```

**"Address already in use"**
```bash
streamlit run app.py --server.port 8502
```

**"No space left on device"**
```bash
# Free up disk space, then:
pip install --no-cache-dir streamlit
```

---

## Quick Checklist

- [ ] Terminal is open
- [ ] In correct directory
- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] All dependencies installed and importable
- [ ] No other process using port 8501
- [ ] Running `streamlit run app.py`
- [ ] Waiting 5-10 seconds for startup
- [ ] Browser opened to http://localhost:8501

If you complete all these steps and still see "Connection Refused", please share the exact error message from your terminal.

