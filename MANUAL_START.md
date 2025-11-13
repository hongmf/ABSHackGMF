# Manual Start Instructions

I've attempted to start Streamlit for you in the background. Here's how to verify and use it:

## Quick Check

Open your browser and try: **http://localhost:8501**

If you see the dashboard, it's working! 🎉

## If that doesn't work, run this script:

```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
bash check_and_start.sh
```

This script will:
- Check if Streamlit is running
- Start it if not running
- Show you the URL to open

## Or start manually:

```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
source venv/bin/activate
streamlit run app.py
```

Keep the terminal open and look for:
```
Local URL: http://localhost:8501
```

## Verify it's running:

```bash
lsof -ti:8501
```

If this returns a number, Streamlit is running.

## Stop Streamlit:

```bash
kill $(lsof -ti:8501)
```

## Common Issues

**"ModuleNotFoundError: No module named 'pyarrow'"**
```bash
conda install -c conda-forge pyarrow -y
```

**Port already in use**
```bash
# Kill existing process
kill $(lsof -ti:8501)
# Or use different port
streamlit run app.py --server.port 8502
```

**Cannot see venv in prompt**
```bash
source venv/bin/activate
# You should see (venv) in your prompt
```

---

## What I did:

1. ✅ Created complete Streamlit dashboard (`app.py`)
2. ✅ Added all dependencies to `requirements.txt`
3. ✅ Created startup scripts
4. ⏳ Started Streamlit in background (may need manual verification)

The app is fully built and ready. It just needs to be started if it's not already running.
