# Codebase Explanation

## Overview

This is a **data extraction and storage pipeline** for processing SEC ABS-EE (Asset-Backed Securities) filings for auto loans. It extracts loan-level data from XML filings, calculates portfolio-level metrics, and stores them in AWS DynamoDB.

**Purpose**: Automate the extraction and analysis of auto loan portfolio metrics from SEC regulatory filings for companies like GM Financial, Ford, AmeriCredit, etc.

---

## Architecture

```
┌─────────────────┐
│  SEC Filing     │  (XML file in .txt format)
│  (Local/S3)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ data_extractor  │  Extract & parse XML, calculate metrics
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Metrics Dict   │  Portfolio-level statistics
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ dynamodb_ops    │  Store in DynamoDB
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DynamoDB Table │  AutoLoanMetrics
└─────────────────┘
```

---

## Module Breakdown

### 1. `data_extractor.py` - Core Data Processing

**Purpose**: Extract and parse XML data from SEC filings, then calculate portfolio-level metrics.

#### Key Components:

**`AutoLoanDataExtractor` Class**:
- **Initialization**: Can work with local files or S3 buckets
- **XML Extraction**: Finds and extracts XML content from SEC filing format
- **Asset Parsing**: Parses individual loan records from XML
- **Metrics Calculation**: Aggregates loan-level data into portfolio metrics

#### Key Methods:

1. **`extract_xml_content()`**
   - Reads file from local filesystem or S3
   - Extracts XML section between `<XML>` tags
   - Returns XML string

2. **`parse_assets()`**
   - Parses XML using ElementTree
   - Extracts all loan records (assets)
   - Returns list of dictionaries with loan data

3. **`calculate_metrics(assets)`** - **The Core Logic**
   - Takes list of individual loans
   - Calculates aggregated metrics:
     - **Portfolio Totals**: Total loans, total balance
     - **Credit Quality**: Average FICO score (weighted by balance)
     - **Delinquency Rates**: 30+, 60+, 90+ days past due
     - **Loss Metrics**: Loss severity percentage
     - **Prepayment**: CPR (annualized) and ABS (monthly) rates
     - **Distribution**: Loan terms, geographic concentration
     - **Vehicle Mix**: New vs used percentages
     - **Repossession Rate**: % of repossessed loans

4. **`extract_all_metrics()`**
   - Main entry point
   - Orchestrates parsing and calculation
   - Returns complete metrics dictionary

#### Example Metrics Calculated:

```python
{
    'company_name': 'GM FINANCIAL',
    'reporting_period': '2025-05',
    'total_loans': 10234,
    'total_pool_balance': 1298646570.54,
    'average_fico_score': 745.32,
    'delinquency_30_plus_rate': 2.45,
    'delinquency_60_plus_rate': 1.12,
    'delinquency_90_plus_rate': 0.56,
    'loss_severity_percentage': 35.20,
    'prepayment_speed_cpr': 18.50,
    'loan_term_distribution': {'0-36': 10.5, '37-48': 25.3, ...},
    'geographic_concentration': {'CA': 15.2, 'TX': 12.8, ...},
    ...
}
```

---

### 2. `dynamodb_operations.py` - Database Layer

**Purpose**: Handle all DynamoDB operations (create table, insert, query).

#### Key Components:

**`DynamoDBHandler` Class**:
- Manages DynamoDB client and resource connections
- Supports both AWS DynamoDB and local DynamoDB (for testing)
- Handles data type conversions (float → Decimal for DynamoDB)

#### Key Methods:

1. **`create_table()`**
   - Creates DynamoDB table with schema:
     - **Partition Key**: `company_name` (String)
     - **Sort Key**: `reporting_period` (String, YYYY-MM format)
   - Uses on-demand billing (PAY_PER_REQUEST)
   - Waits for table to be active

2. **`insert_metrics(metrics)`**
   - Converts Python floats to Decimal (DynamoDB requirement)
   - Inserts single metrics record
   - Uses `put_item` operation

3. **`batch_insert_metrics(metrics_list)`**
   - Batch inserts multiple records efficiently
   - Uses DynamoDB batch writer

4. **`get_metrics_by_company(company_name)`**
   - Queries all records for a company
   - Uses partition key query (efficient)

5. **`get_metrics_by_company_and_period(company_name, period)`**
   - Gets specific record using both keys
   - Uses `get_item` operation

6. **`scan_all_metrics()`**
   - Scans entire table (less efficient, use sparingly)
   - Handles pagination automatically

#### Table Schema:

```
Table: AutoLoanMetrics
├── Partition Key: company_name (String)
├── Sort Key: reporting_period (String) - Format: "YYYY-MM"
└── Attributes: All metrics fields (Numbers, Maps, Strings)
```

**Why this design?**
- Efficient queries by company
- Can query time ranges for a company
- Supports multiple companies and multiple time periods

---

### 3. `dynamodb_schema.py` - Schema Definition

**Purpose**: Define and document the DynamoDB table structure.

#### Functions:

1. **`create_auto_loan_metrics_table(dynamodb_client, table_name)`**
   - Defines table schema
   - Can be called independently to create table

2. **`get_item_schema()`**
   - Returns documentation of all item attributes
   - Useful for understanding data structure

---

### 4. `s3_utils.py` - S3 File Management

**Purpose**: Handle S3 operations for batch processing of files.

#### Key Components:

**`S3FileManager` Class**:
- Manages S3 bucket operations
- Lists, downloads, and reads files from S3

#### Key Methods:

1. **`list_sec_files(prefix, suffix)`**
   - Lists all files in S3 bucket matching criteria
   - Returns file metadata (Key, Size, LastModified)

2. **`download_file(s3_key, local_path)`**
   - Downloads file from S3 to local filesystem

3. **`get_file_content(s3_key)`**
   - Reads file content directly from S3 as string

4. **`file_exists(s3_key)`**
   - Checks if file exists in S3

---

### 5. `pipeline.py` - Orchestration Layer

**Purpose**: Main entry point that orchestrates the entire pipeline.

#### Key Functions:

1. **`run_pipeline(...)`** - Single File Processing
   - **Step 1**: Extract data using `AutoLoanDataExtractor`
   - **Step 2**: (Optional) Save metrics to JSON file
   - **Step 3**: Initialize DynamoDB handler
   - **Step 4**: Create DynamoDB table (if needed)
   - **Step 5**: Insert metrics into DynamoDB
   - **Step 6**: Verify insertion by querying back

2. **`process_s3_bucket(...)`** - Batch Processing
   - Lists all files in S3 bucket
   - Processes each file sequentially
   - Tracks success/failure counts
   - Only creates table on first file

3. **`main()`** - CLI Entry Point
   - Parses command-line arguments
   - Supports:
     - Single file mode: `python pipeline.py file.txt`
     - S3 batch mode: `python pipeline.py --s3-bucket my-bucket`
     - Various options (table name, region, local DynamoDB, etc.)

#### Command-Line Interface:

```bash
# Single file
python src/pipeline.py file.txt

# With options
python src/pipeline.py file.txt \
    --table-name MyTable \
    --region us-west-2 \
    --output-json \
    --endpoint-url http://localhost:8000  # for local DynamoDB

# Batch process S3 bucket
python src/pipeline.py --s3-bucket my-bucket --s3-prefix filings/
```

---

## Data Flow

### Single File Processing Flow:

```
1. User runs: python src/pipeline.py filing.txt
   │
   ├─> pipeline.py parses arguments
   │
   ├─> Creates AutoLoanDataExtractor(file_path='filing.txt')
   │   │
   │   ├─> extract_xml_content()
   │   │   └─> Reads file, extracts XML section
   │   │
   │   ├─> parse_assets()
   │   │   └─> Parses XML → List of loan dictionaries
   │   │
   │   └─> calculate_metrics(assets)
   │       └─> Aggregates loans → Portfolio metrics dict
   │
   ├─> Creates DynamoDBHandler(table_name='AutoLoanMetrics')
   │   │
   │   ├─> create_table() [if needed]
   │   │   └─> Creates DynamoDB table with schema
   │   │
   │   └─> insert_metrics(metrics)
   │       └─> Stores metrics in DynamoDB
   │
   └─> Verifies insertion by querying back
```

### S3 Batch Processing Flow:

```
1. User runs: python src/pipeline.py --s3-bucket my-bucket
   │
   ├─> Creates S3FileManager(bucket_name='my-bucket')
   │   └─> list_sec_files() → List of S3 keys
   │
   ├─> For each file in S3:
   │   │
   │   ├─> Creates AutoLoanDataExtractor(s3_bucket=..., s3_key=...)
   │   │   └─> extract_xml_content() reads from S3
   │   │
   │   └─> Rest of pipeline same as single file
   │
   └─> Returns summary (success/failure counts)
```

---

## Key Features

### 1. **Dual Input Support**
   - Local files: `file_path='local.txt'`
   - S3 files: `s3_bucket='bucket', s3_key='file.txt'`

### 2. **Robust Error Handling**
   - Safe type conversions (`safe_float()`, `safe_int()`)
   - Handles missing/null values gracefully
   - Try-catch blocks around critical operations

### 3. **Flexible Deployment**
   - AWS DynamoDB (production)
   - Local DynamoDB (testing/development)
   - Configurable via `--endpoint-url`

### 4. **Comprehensive Metrics**
   - 20+ calculated metrics
   - Weighted averages (FICO, interest rates)
   - Distribution analysis (geographic, loan terms)
   - Risk metrics (delinquency, loss severity)

### 5. **Batch Processing**
   - Process entire S3 buckets
   - Progress tracking
   - Error reporting

---

## Data Structures

### Input: SEC ABS-EE XML Format

```xml
<XML>
  <assets>
    <originatorName>GM FINANCIAL</originatorName>
    <reportingPeriodEndingDate>05-31-2025</reportingPeriodEndingDate>
    <obligorCreditScore>750</obligorCreditScore>
    <reportingPeriodActualEndBalanceAmount>25000.00</reportingPeriodActualEndBalanceAmount>
    <currentDelinquencyStatus>0</currentDelinquencyStatus>
    <originalLoanTerm>60</originalLoanTerm>
    <obligorGeographicLocation>CA</obligorGeographicLocation>
    ...
  </assets>
  ...
</XML>
```

### Output: Metrics Dictionary

```python
{
    'company_name': str,              # e.g., "GM FINANCIAL"
    'reporting_period': str,          # "YYYY-MM" format
    'total_loans': int,
    'total_pool_balance': float,
    'average_fico_score': float,
    'delinquency_30_plus_rate': float,  # percentage
    'delinquency_60_plus_rate': float,
    'delinquency_90_plus_rate': float,
    'loss_severity_percentage': float,
    'prepayment_speed_cpr': float,     # annualized %
    'prepayment_speed_abs': float,     # monthly %
    'loan_term_distribution': {        # percentages
        '0-36': float,
        '37-48': float,
        ...
    },
    'geographic_concentration': {      # percentages by state
        'CA': float,
        'TX': float,
        ...
    },
    'average_loan_amount': float,
    'average_remaining_term': float,   # months
    'weighted_avg_interest_rate': float,  # percentage
    'new_vehicle_percentage': float,
    'used_vehicle_percentage': float,
    'repossession_rate': float,
    'last_updated': str                # ISO timestamp
}
```

### Storage: DynamoDB Item

Same structure as metrics dictionary, but:
- Floats converted to Decimal
- Stored with keys: `company_name` (PK) + `reporting_period` (SK)

---

## Usage Examples

### Example 1: Process Local File

```python
from src.data_extractor import AutoLoanDataExtractor
from src.dynamodb_operations import DynamoDBHandler

# Extract metrics
extractor = AutoLoanDataExtractor('filing.txt')
metrics = extractor.extract_all_metrics()

# Store in DynamoDB
db = DynamoDBHandler(table_name='AutoLoanMetrics')
db.create_table()
db.insert_metrics(metrics)
```

### Example 2: Query Data

```python
from src.dynamodb_operations import DynamoDBHandler

db = DynamoDBHandler()

# Get all periods for GM Financial
all_periods = db.get_metrics_by_company('GM FINANCIAL')

# Get specific period
may_2025 = db.get_metrics_by_company_and_period('GM FINANCIAL', '2025-05')
```

### Example 3: Batch Process S3

```python
from src.pipeline import process_s3_bucket

results = process_s3_bucket(
    s3_bucket='my-sec-filings',
    s3_prefix='2025/',
    table_name='AutoLoanMetrics'
)

print(f"Processed {results['success']}/{results['total']} files")
```

---

## Design Decisions

### 1. **Why DynamoDB?**
   - NoSQL database good for time-series data
   - Efficient queries by company and time period
   - Serverless, scales automatically
   - Pay-per-request billing

### 2. **Why Composite Key (company_name + reporting_period)?**
   - Allows efficient queries by company
   - Can query time ranges for trend analysis
   - Natural partitioning by company

### 3. **Why Weighted Averages?**
   - FICO scores weighted by balance (larger loans matter more)
   - Interest rates weighted by balance (portfolio-level rate)
   - More accurate than simple averages

### 4. **Why Separate Modules?**
   - **Separation of concerns**: Extraction, storage, orchestration
   - **Reusability**: Can use modules independently
   - **Testability**: Each module can be tested separately
   - **Maintainability**: Clear responsibilities

---

## Extending the Codebase

### Add New Metrics

1. Add calculation in `data_extractor.py` → `calculate_metrics()`
2. Add field to metrics dictionary
3. DynamoDB will automatically store it (schema-less)

### Add New Data Source

1. Create new extractor class (similar to `AutoLoanDataExtractor`)
2. Implement `extract_all_metrics()` method
3. Use same metrics format
4. Works with existing pipeline

### Add New Storage Backend

1. Create new handler class (similar to `DynamoDBHandler`)
2. Implement `insert_metrics()` and query methods
3. Update `pipeline.py` to support it

---

## Testing

### Test Data Extraction

```bash
python src/data_extractor.py
```

### Test DynamoDB Operations

```bash
python src/dynamodb_operations.py
```

### Test Full Pipeline

```bash
python src/pipeline.py test_file.txt --output-json
```

---

## Dependencies

- **boto3**: AWS SDK for Python (DynamoDB, S3)
- **pandas**: Data processing (currently minimal usage)
- **python-dateutil**: Date parsing
- **python-dotenv**: Environment variable management

---

## Summary

This codebase is a **complete ETL pipeline** for auto loan data:

1. **Extract**: Parse XML from SEC filings (local or S3)
2. **Transform**: Calculate portfolio-level metrics from loan-level data
3. **Load**: Store metrics in DynamoDB for querying and analysis

The architecture is modular, allowing each component to be used independently or together via the pipeline orchestrator.

