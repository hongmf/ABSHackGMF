# Local Setup Guide

This guide will help you run the Hackathon-2025-GMF project locally on your machine.

## Prerequisites

- **Python 3.8 or higher** (check with `python3 --version`)
- **pip** (Python package manager)
- **AWS Account** (for DynamoDB) OR **Docker** (for local DynamoDB)

## Step-by-Step Setup

### 1. Navigate to Project Directory

```bash
cd /Users/davidawe/Desktop/GMFHACK/team-15-silence-of-the-rams/Hackathon-2025-GMF
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt when activated.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `boto3` - AWS SDK for Python
- `pandas` - Data processing
- `python-dateutil` - Date parsing
- `python-dotenv` - Environment variables
- `pytest` - Testing (optional)

### 5. Configure AWS Credentials

You have three options:

#### Option A: Environment Variables (Recommended for local testing)

```bash
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_REGION=us-east-1
```

#### Option B: AWS CLI Configuration

```bash
aws configure
```

This will prompt you for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Default output format (e.g., `json`)

#### Option C: .env File

Create a `.env` file in the project root:

```bash
cat > .env << EOF
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
EOF
```

The project uses `python-dotenv` to automatically load these variables.

### 6. (Optional) Set Up Local DynamoDB

If you don't want to use AWS DynamoDB, you can run DynamoDB locally using Docker:

```bash
docker run -p 8000:8000 amazon/dynamodb-local
```

Keep this running in a separate terminal. Then use `--endpoint-url http://localhost:8000` when running the pipeline.

## Running the Project

### Basic Usage (Single File)

Process a SEC ABS-EE filing file:

```bash
python src/pipeline.py path/to/your/file.txt
```

**Example:**
```bash
python src/pipeline.py 0001347185-25-000024.txt
```

### With Local DynamoDB

If you're using local DynamoDB (Docker):

```bash
python src/pipeline.py path/to/your/file.txt --endpoint-url http://localhost:8000
```

### Save Metrics to JSON

Extract metrics and save to a JSON file:

```bash
python src/pipeline.py path/to/your/file.txt --output-json
```

This will create a file like `metrics_GM_FINANCIAL_2025-05.json` in the same directory as your input file.

### Custom Table Name

```bash
python src/pipeline.py path/to/your/file.txt --table-name MyCustomTable
```

### Skip Table Creation

If the table already exists:

```bash
python src/pipeline.py path/to/your/file.txt --skip-table-creation
```

### Process S3 Bucket

If you have files in S3:

```bash
python src/pipeline.py --s3-bucket your-bucket-name --s3-prefix filings/
```

## Command Line Options

```bash
python src/pipeline.py [FILE_PATH] [OPTIONS]

Options:
  --s3-bucket BUCKET        Process all files from S3 bucket
  --s3-prefix PREFIX        S3 key prefix to filter files
  --table-name NAME         DynamoDB table name (default: AutoLoanMetrics)
  --region REGION           AWS region (default: us-east-1)
  --endpoint-url URL        DynamoDB endpoint (for local dev: http://localhost:8000)
  --skip-table-creation     Skip creating the table
  --output-json             Save extracted metrics to JSON file
```

## Testing Individual Modules

You can also run individual modules:

### Extract Metrics Only

```bash
python src/data_extractor.py
```

### Create DynamoDB Table

```bash
python src/dynamodb_schema.py
```

### Test DynamoDB Operations

```bash
python src/dynamodb_operations.py
```

## Expected Output

When you run the pipeline successfully, you should see:

```
================================================================================
AUTO LOAN METRICS EXTRACTION & DYNAMODB INSERTION PIPELINE
================================================================================

Step 1: Extracting data from your_file.txt
--------------------------------------------------------------------------------
[OK] Successfully extracted metrics for GM FINANCIAL
  - Reporting Period: 2025-05
  - Total Loans: 10,234
  - Total Pool Balance: $1,298,646,570.54
  - Average FICO Score: 745.32

Step 2: Initializing DynamoDB connection
--------------------------------------------------------------------------------
[OK] Connected to DynamoDB (Region: us-east-1)

Step 3: Creating DynamoDB table 'AutoLoanMetrics'
--------------------------------------------------------------------------------
[OK] Table 'AutoLoanMetrics' is ready

Step 4: Inserting data into DynamoDB
--------------------------------------------------------------------------------
[OK] Data successfully inserted into DynamoDB
  - Company: GM FINANCIAL
  - Period: 2025-05

Step 5: Verifying data insertion
--------------------------------------------------------------------------------
[OK] Data verified successfully

================================================================================
PIPELINE COMPLETED SUCCESSFULLY
================================================================================
```

## Troubleshooting

### Issue: "No module named 'boto3'"

**Solution:** Make sure you've activated your virtual environment and installed dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "Unable to locate credentials"

**Solution:** Configure AWS credentials using one of the methods in Step 5 above.

### Issue: "Table already exists"

**Solution:** Use the `--skip-table-creation` flag or delete the existing table first.

### Issue: "File not found"

**Solution:** Make sure the file path is correct. Use absolute paths if needed:
```bash
python src/pipeline.py /full/path/to/your/file.txt
```

### Issue: "XML Parse Error"

**Solution:** Verify your input file is a valid SEC ABS-EE filing with XML content.

### Issue: Local DynamoDB Connection Failed

**Solution:** Make sure Docker is running and the DynamoDB local container is active:
```bash
docker ps  # Should show amazon/dynamodb-local running
```

## Quick Test Without AWS

If you just want to test the data extraction without DynamoDB:

1. Run with `--output-json` to save metrics to a file
2. Or modify the code to skip DynamoDB steps

## Next Steps

1. Process your SEC filing files
2. Query DynamoDB to analyze the stored metrics
3. Build dashboards or reports using the extracted data
4. Set up automated processing for new filings

## Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review [QUICKSTART.md](QUICKSTART.md) for a quick reference
- Check [S3_USAGE.md](S3_USAGE.md) for S3-specific instructions

