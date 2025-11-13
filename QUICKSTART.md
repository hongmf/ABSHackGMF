# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies
```bash
cd C:\Hackathon2025\Hackathon-2025-GMF
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

**Option A - Environment Variables (Easiest):**
```bash
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_REGION=us-east-1
```

**Option B - AWS CLI:**
```bash
aws configure
```

**Option C - .env File:**
```bash
copy .env.example .env
# Edit .env with your credentials
```

## Run the Pipeline

### Basic Usage
```bash
python src/pipeline.py 0001347185-25-000024.txt
```

This will:
1. Extract metrics from the SEC filing
2. Create DynamoDB table (if needed)
3. Insert data into DynamoDB
4. Verify the insertion

## Expected Output

```
================================================================================
AUTO LOAN METRICS EXTRACTION & DYNAMODB INSERTION PIPELINE
================================================================================

Step 1: Extracting data from 0001347185-25-000024.txt
--------------------------------------------------------------------------------
Parsing assets from XML...
Found 10,234 loans
Calculating metrics...

✓ Successfully extracted metrics for GM FINANCIAL
  - Reporting Period: 2025-05
  - Total Loans: 10,234
  - Total Pool Balance: $1,298,646,570.54
  - Average FICO Score: 745.32

Step 2: Initializing DynamoDB connection
--------------------------------------------------------------------------------
✓ Connected to DynamoDB (Region: us-east-1)

Step 3: Creating DynamoDB table 'AutoLoanMetrics'
--------------------------------------------------------------------------------
✓ Table 'AutoLoanMetrics' is ready

Step 4: Inserting data into DynamoDB
--------------------------------------------------------------------------------
✓ Data successfully inserted into DynamoDB
  - Company: GM FINANCIAL
  - Period: 2025-05

Step 5: Verifying data insertion
--------------------------------------------------------------------------------
✓ Data verified successfully

================================================================================
PIPELINE COMPLETED SUCCESSFULLY
================================================================================
```

## Key Metrics Extracted

The pipeline extracts and calculates:

- **Company Name**: Originator (e.g., GM FINANCIAL)
- **Average FICO Score**: Weighted by loan balance
- **Delinquency Rates**: 30+, 60+, 90+ days past due
- **Loss Severity**: Percentage loss on charged-off loans
- **Prepayment Speeds**: CPR (annualized) and ABS (monthly)
- **Loan Term Distribution**: Percentage by term range
- **Geographic Concentration**: Percentage by state
- **Vehicle Mix**: New vs Used percentages
- **Portfolio Metrics**: Average loan amount, remaining term, interest rate

## DynamoDB Table Structure

**Table Name:** AutoLoanMetrics

**Keys:**
- Partition Key: `company_name` (e.g., "GM FINANCIAL")
- Sort Key: `reporting_period` (e.g., "2025-05")

**Query Examples:**

```bash
# Get all periods for GM Financial
aws dynamodb query \
  --table-name AutoLoanMetrics \
  --key-condition-expression "company_name = :c" \
  --expression-attribute-values '{":c":{"S":"GM FINANCIAL"}}'

# Get specific company and period
aws dynamodb get-item \
  --table-name AutoLoanMetrics \
  --key '{"company_name":{"S":"GM FINANCIAL"},"reporting_period":{"S":"2025-05"}}'
```

## Advanced Options

### Save Metrics to JSON File
```bash
python src/pipeline.py 0001347185-25-000024.txt --output-json
```

### Use Custom Table Name
```bash
python src/pipeline.py 0001347185-25-000024.txt --table-name MyTable
```

### Use Local DynamoDB (for testing)
```bash
# Start local DynamoDB
docker run -p 8000:8000 amazon/dynamodb-local

# Run pipeline against local DB
python src/pipeline.py 0001347185-25-000024.txt --endpoint-url http://localhost:8000
```

### Use Different AWS Region
```bash
python src/pipeline.py 0001347185-25-000024.txt --region us-west-2
```

## Troubleshooting

### Issue: AWS Credentials Not Found
**Solution:** Set AWS credentials using one of the methods in step 2 above

### Issue: Table Already Exists
**Solution:** Use `--skip-table-creation` flag or delete the existing table

### Issue: File Not Found
**Solution:** Ensure the data file path is correct relative to your current directory

### Issue: XML Parse Error
**Solution:** Verify the input file is a valid SEC ABS-EE filing with XML content

## Next Steps

1. Process additional SEC filings for other companies (Ford, AmeriCredit)
2. Query the DynamoDB table to analyze trends
3. Build dashboards or reports using the stored data
4. Set up automated processing for new filings

## Module Documentation

Each module can be run independently:

- **data_extractor.py**: Extract and calculate metrics
- **dynamodb_schema.py**: View table schema
- **dynamodb_operations.py**: Test CRUD operations
- **pipeline.py**: Full end-to-end pipeline

## Support

For issues or questions:
1. Check the full [README.md](README.md)
2. Review error messages carefully
3. Verify AWS credentials and permissions
4. Ensure input file is in correct format
