# Quick Reference Guide

## Common Commands

### Start the Dashboard
```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
source venv/bin/activate
streamlit run app.py
```

### Process New SEC Filings
```bash
# Single file
python src/pipeline.py file.txt

# All files in S3 bucket
python src/pipeline.py --s3-bucket abs-ee

# Specific S3 prefix
python src/pipeline.py --s3-bucket abs-ee --s3-prefix 2025/
```

### Test Bedrock Connection
```bash
python test_bedrock_connection.py
```

### Find Knowledge Bases
```bash
python find_kb.py
```

---

## File Structure

```
Hackathon-2025-GMF/
├── src/                          # Core application code
│   ├── pipeline.py              # Main ETL orchestrator
│   ├── data_extractor.py        # SEC filing parser
│   ├── dynamodb_operations.py   # Database operations
│   ├── dynamodb_schema.py       # Table schema definition
│   └── s3_utils.py              # S3 helper functions
│
├── app.py                        # Streamlit dashboard (main UI)
├── requirements.txt              # Python dependencies
├── .env                          # Configuration (AWS keys, KB ID)
│
├── tests/                        # Unit tests
├── venv/                         # Virtual environment
│
└── Documentation/
    ├── README.md                 # Project overview
    ├── PROGRAM_LOGIC.md          # This file - architecture
    ├── BEDROCK_INTEGRATION.md    # AI setup guide
    ├── S3_USAGE.md              # S3 batch processing
    └── TROUBLESHOOTING.md        # Common issues
```

---

## Key Concepts

### Data Model
```
Company → Period → Metrics
   ↓         ↓         ↓
GM FINANCIAL → 2025-05 → {fico: 745, delinq: 2.1%, ...}
```

### Metric Types
- **Credit Quality**: FICO scores
- **Risk**: Delinquency rates (30+, 60+, 90+ days)
- **Performance**: Prepayment speeds (CPR/ABS)
- **Composition**: Geographic, vehicle type, loan terms

### AWS Services Used
- **S3**: File storage (SEC filings)
- **DynamoDB**: Metrics database
- **Bedrock**: AI/ML (Claude 3.5, Knowledge Base)

---

## Environment Variables

Required in `.env`:
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# S3 Bucket
S3_BUCKET_NAME=abs-ee

# Bedrock (AI Assistant)
BEDROCK_KB_ID=A7EOGV6BHS
BEDROCK_REGION=us-west-2
BEDROCK_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0
```

---

## Dashboard Tabs

1. **Dashboard**: Overview with KPIs and charts
2. **Company Comparison**: GM vs Ford side-by-side
3. **Geographic Analysis**: State-level breakdown
4. **Detailed Metrics**: Full data table + CSV export
5. **AI Assistant**: Ask questions about the data

---

## API Endpoints (Internal)

### DynamoDB Operations
```python
# Get all metrics for a company
db.get_metrics_by_company("GM FINANCIAL")

# Get specific period
db.get_metrics_by_company_and_period("GM FINANCIAL", "2025-05")

# Get all data
db.scan_all_metrics()
```

### Bedrock Query
```python
# Ask question
bedrock.retrieve_and_generate(
    input={'text': "What is the average FICO score?"},
    retrieveAndGenerateConfiguration={...}
)
```

---

## Troubleshooting Quick Fixes

### "No data found in DynamoDB"
→ Run: `python src/pipeline.py --s3-bucket abs-ee`

### "Error connecting to Bedrock"
→ Check: `.env` has correct `BEDROCK_KB_ID` and `BEDROCK_REGION`

### "Session ID invalid"
→ Fixed: No sessionId parameter needed (already removed)

### "Module not found: pyarrow"
→ Run: `conda install -c conda-forge pyarrow -y`

### Streamlit not loading
→ Run: `lsof -ti:8501 | xargs kill -9` then restart

---

## Performance Tips

- Data cached for 5 minutes in Streamlit
- Use filters to reduce displayed data
- CSV export for large datasets
- Clear chat history if slow

---

## Security Notes

- ✅ Never commit `.env` to git
- ✅ Rotate AWS keys regularly
- ✅ Use IAM roles in production
- ✅ Restrict S3 bucket access

---

## URLs

- **Dashboard**: http://localhost:8501
- **DynamoDB Console**: https://console.aws.amazon.com/dynamodb/
- **Bedrock Console**: https://console.aws.amazon.com/bedrock/
- **S3 Console**: https://s3.console.aws.amazon.com/s3/buckets/abs-ee

