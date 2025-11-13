# 🚗 Start Streamlit Dashboard

## Quick Start

Since PyArrow is now installed, you can run the app:

```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
source venv/bin/activate
streamlit run app.py
```

Or use the run script:

```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
./run_app.sh
```

## The app will:

1. Connect to your DynamoDB table `AutoLoanMetrics`
2. Load your auto loan metrics data
3. Open in your browser at **http://localhost:8501**

## Features Available:

- 📈 **Dashboard**: Overview with key metrics and charts
- 🔍 **Company Comparison**: Side-by-side comparison of Ford Credit vs GM FINANCIAL
- 🗺️ **Geographic Analysis**: State-by-state breakdown
- 📊 **Detailed Metrics**: Full data table with CSV download
- 💬 **AI Assistant**: Placeholder for Bedrock integration

## If you see "No data found":

Make sure you've processed your SEC filings:
```bash
python src/pipeline.py --s3-bucket abs-ee
```

Enjoy exploring your auto loan metrics! 🎉

