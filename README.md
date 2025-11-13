# Hackathon-2025-GMF

Auto Loan Metrics Extraction and DynamoDB Storage System

This Python project extracts key metrics from SEC ABS-EE (Asset-Backed Securities) filings for auto loans and stores them in AWS DynamoDB. It processes data from companies like GM Financial, Ford, AmeriCredit, and others.

## Features

- **Data Extraction**: Parse SEC ABS-EE XML filings to extract loan-level data
- **Metrics Calculation**: Calculate portfolio-level metrics including:
  - Average FICO scores
  - Delinquency rates (30+, 60+, 90+ days)
  - Loss severity percentages
  - Prepayment speeds (CPR/ABS)
  - Loan term distributions
  - Geographic concentration by state
  - Vehicle type distribution (new vs used)
  - Average loan amounts and interest rates
- **DynamoDB Storage**: Automatically create tables and insert data
- **Batch Processing**: Support for processing multiple files

## Prerequisites

- Python 3.8 or higher
- AWS Account with DynamoDB access (or local DynamoDB for testing)
- AWS credentials configured

## Installation

1. Clone or navigate to the project directory:
```bash
cd Hackathon-2025-GMF
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure AWS credentials:
```bash
# Option 1: Set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# Option 2: Use AWS CLI configuration
aws configure

# Option 3: Copy .env.example to .env and edit
cp .env.example .env
# Edit .env with your credentials
```

## Usage

### Run Complete Pipeline

Process a SEC filing and insert data into DynamoDB:

```bash
python src/pipeline.py 0001347185-25-000024.txt
```

### Command Line Options

```bash
python src/pipeline.py [FILE_PATH] [OPTIONS]

Options:
  --table-name NAME          DynamoDB table name (default: AutoLoanMetrics)
  --region REGION            AWS region (default: us-east-1)
  --endpoint-url URL         DynamoDB endpoint (for local dev)
  --skip-table-creation      Skip creating the table
  --output-json              Save extracted metrics to JSON file
```

### Examples

**Process file with custom table name:**
```bash
python src/pipeline.py 0001347185-25-000024.txt --table-name MyAutoLoans
```

**Use local DynamoDB:**
```bash
python src/pipeline.py 0001347185-25-000024.txt --endpoint-url http://localhost:8000
```

**Extract metrics and save to JSON:**
```bash
python src/pipeline.py 0001347185-25-000024.txt --output-json
```

### Individual Module Usage

**Extract metrics only:**
```bash
python src/data_extractor.py
```

**Create DynamoDB table:**
```bash
python src/dynamodb_schema.py
```

**Test DynamoDB operations:**
```bash
python src/dynamodb_operations.py
```

## Project Structure

```
Hackathon-2025-GMF/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore patterns
├── .env.example                   # Environment variable template
├── 0001347185-25-000024.txt      # Sample SEC filing data
├── src/
│   ├── __init__.py               # Package initialization
│   ├── data_extractor.py         # Extract data from SEC filings
│   ├── dynamodb_schema.py        # DynamoDB table schema
│   ├── dynamodb_operations.py    # DynamoDB CRUD operations
│   └── pipeline.py               # Main pipeline orchestrator
└── tests/
    └── __init__.py               # Test package
```

## DynamoDB Table Schema

### Primary Keys
- **Partition Key**: `company_name` (String) - e.g., "GM FINANCIAL"
- **Sort Key**: `reporting_period` (String) - Format: "YYYY-MM"

### Attributes
- `total_loans`: Total number of loans
- `total_pool_balance`: Total outstanding balance
- `average_fico_score`: Weighted average FICO score
- `delinquency_30_plus_rate`: % of loans 30+ days delinquent
- `delinquency_60_plus_rate`: % of loans 60+ days delinquent
- `delinquency_90_plus_rate`: % of loans 90+ days delinquent
- `loss_severity_percentage`: Average loss severity
- `prepayment_speed_cpr`: Constant Prepayment Rate (annualized %)
- `prepayment_speed_abs`: Absolute Prepayment Speed (monthly %)
- `loan_term_distribution`: Map of term ranges to percentages
- `geographic_concentration`: Map of states to percentages
- `average_loan_amount`: Average original loan amount
- `average_remaining_term`: Average remaining months
- `weighted_avg_interest_rate`: Weighted average interest rate
- `new_vehicle_percentage`: % of new vehicles
- `used_vehicle_percentage`: % of used vehicles
- `repossession_rate`: % of repossessed loans
- `last_updated`: ISO timestamp

## Querying Data

Use AWS CLI or boto3 to query the data:

```bash
# Get all data for GM Financial
aws dynamodb query \
  --table-name AutoLoanMetrics \
  --key-condition-expression "company_name = :company" \
  --expression-attribute-values '{":company":{"S":"GM FINANCIAL"}}'

# Get specific period
aws dynamodb get-item \
  --table-name AutoLoanMetrics \
  --key '{"company_name":{"S":"GM FINANCIAL"},"reporting_period":{"S":"2025-05"}}'
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Local DynamoDB Setup

For local development, use DynamoDB Local:

```bash
# Download and run DynamoDB Local
docker run -p 8000:8000 amazon/dynamodb-local

# Use with the pipeline
python src/pipeline.py data.txt --endpoint-url http://localhost:8000
```

## Troubleshooting

**AWS Credentials Error:**
- Ensure AWS credentials are configured via environment variables, .env file, or AWS CLI
- Verify IAM permissions for DynamoDB

**XML Parsing Error:**
- Verify the input file contains valid XML in the expected SEC ABS-EE format
- Check that the file is not corrupted

**DynamoDB Connection Error:**
- Verify AWS region is correct
- Check network connectivity to AWS
- For local DynamoDB, ensure the service is running

## Sample Output

```
Company Name:              GM FINANCIAL
Reporting Period:          2025-05
Total Loans:               10,234
Total Pool Balance:        $1,298,646,570.54
Average FICO Score:        745.32
Delinquency 30+ Rate:      2.45%
Delinquency 60+ Rate:      1.12%
Delinquency 90+ Rate:      0.56%
Loss Severity:             35.20%
Prepayment Speed (CPR):    18.50%
```

## License

ISC
