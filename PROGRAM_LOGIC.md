# Program Logic & Architecture

## Overview

This is an end-to-end **Auto Loan Portfolio Analytics System** that extracts SEC filing data, processes it, stores it in a database, and provides an AI-powered dashboard for analysis.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW                                   │
└─────────────────────────────────────────────────────────────────────┘

1. DATA SOURCE (S3 Bucket)
   ├── SEC ABS-EE Filings (.txt files with XML)
   ├── Companies: GM Financial, Ford Credit, etc.
   └── Contains: Loan-level data for auto portfolios
                    ↓
2. EXTRACTION PIPELINE (src/pipeline.py)
   ├── Reads files from S3 or local storage
   ├── Parses XML content
   ├── Calculates portfolio metrics
   └── Validates data
                    ↓
3. DATA PROCESSING (src/data_extractor.py)
   ├── Extract loan records
   ├── Calculate aggregated metrics:
   │   • FICO scores (average)
   │   • Delinquency rates (30+, 60+, 90+ days)
   │   • Loss severity
   │   • Prepayment speeds
   │   • Geographic distribution
   │   • Vehicle types (new vs used)
   └── Format for database insertion
                    ↓
4. DATA STORAGE (AWS DynamoDB)
   ├── Table: AutoLoanMetrics
   ├── Key: company_name + reporting_period
   └── Attributes: All calculated metrics
                    ↓
5. VISUALIZATION LAYER (Streamlit - app.py)
   ├── Dashboard tab (overview charts)
   ├── Company comparison tab
   ├── Geographic analysis tab
   ├── Detailed metrics table
   └── AI Assistant tab
                    ↓
6. AI INTELLIGENCE (AWS Bedrock)
   ├── Knowledge Base: SEC filing documentation
   ├── Model: Claude 3.5 Sonnet V2
   └── Provides: Natural language Q&A
                    ↓
7. END USER
   └── Interact via web browser (localhost:8501)
```

---

## Component Details

### 1. Data Extraction Pipeline (`src/pipeline.py`)

**Purpose**: Orchestrate the entire ETL process

**Key Functions**:

```python
def run_pipeline(file_path, table_name, region, ...):
    """
    Main pipeline for single file processing
    
    Flow:
    1. Initialize data extractor
    2. Extract XML content from file/S3
    3. Parse asset data (loans)
    4. Calculate metrics
    5. Connect to DynamoDB
    6. Create table if needed
    7. Insert metrics
    8. Verify insertion
    """

def process_s3_bucket(bucket_name, prefix, ...):
    """
    Batch processing for multiple S3 files
    
    Flow:
    1. List all .txt files in bucket
    2. For each file:
       - Run pipeline
       - Track success/failure
    3. Generate summary report
    """
```

**Execution Modes**:
- Single file: `python src/pipeline.py file.txt`
- S3 batch: `python src/pipeline.py --s3-bucket abs-ee`

---

### 2. Data Extractor (`src/data_extractor.py`)

**Purpose**: Parse SEC filings and calculate portfolio metrics

**Class Structure**:

```python
class AutoLoanDataExtractor:
    def __init__(self, file_path, s3_bucket=None, s3_key=None):
        """Initialize with file path or S3 location"""
    
    def extract_xml_content(self):
        """
        Extract XML from SEC filing format
        - Read file (local or S3)
        - Find <XML> tags
        - Extract content between tags
        """
    
    def parse_assets(self):
        """
        Parse individual loan records
        - Extract each <asset> element
        - Get loan details: FICO, balance, term, etc.
        - Store as list of dictionaries
        """
    
    def calculate_metrics(self):
        """
        Calculate portfolio-level metrics
        
        Calculations:
        - Average FICO score (weighted by balance)
        - Delinquency rates (count/total * 100)
        - Loss severity (losses/defaults * 100)
        - Prepayment speeds (CPR, ABS methods)
        - Geographic concentration by state
        - Loan term distribution
        - Vehicle type percentages
        """
```

**Metrics Calculated**:

| Metric | Formula | Description |
|--------|---------|-------------|
| Average FICO | Σ(FICO × Balance) / Σ(Balance) | Credit quality indicator |
| Delinquency Rate | (Delinquent Loans / Total Loans) × 100 | Default risk |
| Loss Severity | (Total Losses / Defaults) × 100 | Loss given default |
| CPR | (1 - (1 - Prepay/Balance)^12) × 100 | Annualized prepayment |
| Geographic Concentration | Count by State / Total | Regional risk |

---

### 3. DynamoDB Operations (`src/dynamodb_operations.py`)

**Purpose**: Manage all database interactions

**Key Methods**:

```python
class DynamoDBHandler:
    def create_table(self, table_name):
        """
        Create DynamoDB table
        - Keys: company_name (HASH), reporting_period (RANGE)
        - Billing: PAY_PER_REQUEST
        """
    
    def insert_metrics(self, metrics):
        """
        Insert calculated metrics into table
        - Convert floats to Decimal (DynamoDB requirement)
        - Add timestamp
        - Put item
        """
    
    def get_metrics_by_company(self, company_name):
        """Query all periods for a company"""
    
    def scan_all_metrics(self):
        """Get all data (used by Streamlit)"""
```

**Table Schema**:

```
Primary Key:
  - company_name (String) - Partition Key
  - reporting_period (String) - Sort Key

Attributes:
  - total_loans (Number)
  - total_pool_balance (Number)
  - average_fico_score (Number)
  - delinquency_30_plus_rate (Number)
  - delinquency_60_plus_rate (Number)
  - delinquency_90_plus_rate (Number)
  - loss_severity_percentage (Number)
  - prepayment_speed_cpr (Number)
  - prepayment_speed_abs (Number)
  - average_loan_amount (Number)
  - weighted_avg_interest_rate (Number)
  - new_vehicle_percentage (Number)
  - used_vehicle_percentage (Number)
  - geographic_concentration (Map)
  - loan_term_distribution (Map)
  - last_updated (String)
```

---

### 4. Streamlit Dashboard (`app.py`)

**Purpose**: Interactive web interface for data visualization and analysis

**Architecture**:

```python
# 1. Configuration & Imports
import streamlit as st
import plotly, pandas, boto3

# 2. Load Environment Variables
KNOWLEDGE_BASE_ID = os.getenv('BEDROCK_KB_ID')
BEDROCK_REGION = os.getenv('BEDROCK_REGION')

# 3. Data Loading (Cached)
@st.cache_data(ttl=300)
def load_data():
    """
    Load from DynamoDB and cache for 5 minutes
    """
    db_handler = DynamoDBHandler()
    data = db_handler.scan_all_metrics()
    return convert_decimals(data)

# 4. Main Application
def main():
    # Header
    st.set_page_config(...)
    
    # Load data
    data = load_data()
    df = convert_to_dataframe(data)
    
    # Sidebar filters
    selected_companies = st.sidebar.multiselect(...)
    selected_periods = st.sidebar.multiselect(...)
    
    # Filter data
    df_filtered = df[df['company_name'].isin(selected_companies)]
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([...])
    
    # Tab 1: Dashboard
    with tab1:
        # Display KPIs
        st.metric("Total Loans", ...)
        # Create charts
        fig = px.bar(...)
        st.plotly_chart(fig)
    
    # Tab 2: Company Comparison
    with tab2:
        # Side-by-side metrics
        col1, col2 = st.columns(2)
        # Comparison charts
    
    # Tab 3: Geographic Analysis
    with tab3:
        # State-level breakdown
        # Maps and charts
    
    # Tab 4: Detailed Metrics
    with tab4:
        # Full data table
        st.dataframe(df_filtered)
        # CSV export
    
    # Tab 5: AI Assistant
    with tab5:
        # Chat interface
        # Bedrock integration (see below)
```

**Tab Breakdown**:

| Tab | Purpose | Components |
|-----|---------|------------|
| Dashboard | Overview | KPIs, trend charts, metrics cards |
| Company Comparison | Side-by-side analysis | Comparative charts, diff calculations |
| Geographic Analysis | Regional breakdown | State maps, concentration charts |
| Detailed Metrics | Raw data | Full table, CSV download |
| AI Assistant | Q&A interface | Bedrock chat, citations |

---

### 5. AI Assistant (Bedrock Integration)

**Purpose**: Natural language interface to query and understand data

**Flow**:

```
User Question
    ↓
[Streamlit UI captures input]
    ↓
[Create Bedrock client]
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
    ↓
[Call RetrieveAndGenerate API]
response = bedrock_agent_runtime.retrieve_and_generate(
    input={'text': question},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'A7EOGV6BHS',
            'modelArn': 'arn:aws:bedrock:us-west-2::.../claude-3-5-sonnet...',
            'retrievalConfiguration': {
                'vectorSearchConfiguration': {
                    'numberOfResults': 5  # Top 5 documents
                }
            }
        }
    }
)
    ↓
[Bedrock Process]
1. Vector search in Knowledge Base
2. Retrieve 5 most relevant documents
3. Pass to Claude 3.5 Sonnet
4. Generate answer with context
5. Return answer + citations
    ↓
[Display in Streamlit]
- Show answer
- Show sources (if available)
- Add to conversation history
```

**Prompt Template**:

```
You are an expert financial analyst specializing in auto loan portfolios 
and SEC filings.

Use the following context from the knowledge base to answer the question. 
Be specific with numbers, cite data accurately, and provide clear explanations.

Context: $search_results$
Question: $query$

Provide a detailed, professional answer:
```

**Key Features**:
- ✅ Conversational interface
- ✅ Source citations
- ✅ Context-aware responses
- ✅ No session management (stateless)

---

## Data Flow Example

### Complete Journey of One SEC Filing

```
1. FILE UPLOAD
   📄 "0001347185-25-000024.txt" uploaded to S3 bucket "abs-ee"

2. PIPELINE TRIGGER
   $ python src/pipeline.py --s3-bucket abs-ee
   
3. FILE PROCESSING
   - S3FileManager downloads file
   - AutoLoanDataExtractor reads content
   - Finds <XML>...</XML> tags
   - Extracts 10,234 loan records

4. METRIC CALCULATION
   Raw Data:
   - Loan 1: FICO 720, Balance $25,000, Status: Current
   - Loan 2: FICO 680, Balance $18,000, Status: 30+ Delinquent
   - ... (10,234 total)
   
   Calculated:
   - Average FICO: 745.32 (weighted)
   - Total Balance: $1,298,646,570.54
   - Delinquency Rate: 2.1%
   - Loss Severity: 0.8%

5. DATABASE INSERTION
   DynamoDB Item:
   {
     "company_name": "GM FINANCIAL",
     "reporting_period": "2025-05",
     "total_loans": 10234,
     "average_fico_score": 745.32,
     "delinquency_30_plus_rate": 2.1,
     ...
   }

6. VISUALIZATION
   Streamlit loads data:
   - Dashboard shows 10,234 total loans
   - FICO score displayed: 745
   - Chart shows GM vs Ford comparison

7. AI QUERY
   User asks: "What is GM Financial's FICO score?"
   
   Bedrock:
   - Searches Knowledge Base
   - Finds relevant SEC filing docs
   - Generates: "GM Financial's average FICO score is 745.32,
                 indicating strong credit quality..."
```

---

## Key Design Decisions

### 1. **Why DynamoDB?**
- ✅ Serverless (no management)
- ✅ Fast key-value lookups
- ✅ Pay-per-request pricing
- ✅ Perfect for company+period queries

### 2. **Why Streamlit?**
- ✅ Rapid development
- ✅ Python-native
- ✅ Built-in caching
- ✅ Interactive widgets

### 3. **Why Bedrock Knowledge Base?**
- ✅ RAG (Retrieval Augmented Generation)
- ✅ Source attribution
- ✅ No prompt engineering needed
- ✅ Managed vector search

### 4. **Why Claude 3.5 Sonnet?**
- ✅ Latest stable model
- ✅ Strong financial reasoning
- ✅ Long context window
- ✅ Citation support

---

## Error Handling

### Pipeline Level
```python
try:
    extractor = AutoLoanDataExtractor(file_path)
    metrics = extractor.calculate_metrics()
except Exception as e:
    print(f"Error processing {file_path}: {e}")
    continue  # Continue with next file
```

### Dashboard Level
```python
try:
    data = load_data()
except Exception as e:
    st.error("Could not load data from DynamoDB")
    return
```

### Bedrock Level
```python
try:
    response = bedrock_agent_runtime.retrieve_and_generate(...)
except Exception as e:
    st.error(f"Error connecting to Bedrock: {e}")
    st.info("Check AWS credentials and permissions")
```

---

## Configuration Management

### Environment Variables (`.env`)
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# S3
S3_BUCKET_NAME=abs-ee

# Bedrock
BEDROCK_KB_ID=A7EOGV6BHS
BEDROCK_REGION=us-west-2
BEDROCK_MODEL_ARN=arn:aws:bedrock:us-west-2::.../claude-3-5-sonnet...
```

### Loading Configuration
```python
from dotenv import load_dotenv
import os

load_dotenv()

KB_ID = os.getenv('BEDROCK_KB_ID')
REGION = os.getenv('BEDROCK_REGION')
```

---

## Performance Optimizations

### 1. **Streamlit Caching**
```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    # Expensive DynamoDB scan
    return db_handler.scan_all_metrics()
```

### 2. **DynamoDB Batch Operations**
```python
# Instead of multiple get_item calls
response = table.query(
    KeyConditionExpression=Key('company_name').eq('GM FINANCIAL')
)
```

### 3. **S3 Pagination**
```python
paginator = s3_client.get_paginator('list_objects_v2')
for page in paginator.paginate(Bucket=bucket_name):
    # Process page by page
```

### 4. **Decimal Conversion**
```python
# Convert once after loading
def convert_decimals(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    # Recursive for nested structures
```

---

## Security Considerations

### 1. **AWS Credentials**
- ✅ Stored in `.env` (not committed to git)
- ✅ `.gitignore` includes `.env`
- ✅ Use IAM roles in production

### 2. **Data Access**
- ✅ DynamoDB: Restricted by IAM
- ✅ S3: Bucket policies enforce access
- ✅ Bedrock: Model access per user

### 3. **API Keys**
- ⚠️ Never hardcode
- ✅ Use environment variables
- ✅ Rotate regularly

---

## Scaling Considerations

### Current Setup
- Single user (localhost)
- Small dataset (~10 companies, ~50 periods)
- Manual pipeline execution

### Production Scaling
1. **Deploy Streamlit**: AWS ECS/EC2 or Streamlit Cloud
2. **Automate Pipeline**: Lambda + EventBridge (schedule)
3. **Increase Throughput**: DynamoDB provisioned capacity
4. **Add Caching**: ElastiCache/Redis for Streamlit
5. **Multi-user**: Add authentication (AWS Cognito)

---

## Monitoring & Logging

### Pipeline Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Processing file: {filename}")
logger.error(f"Failed to parse: {error}")
```

### CloudWatch (Production)
- Lambda execution logs
- DynamoDB performance metrics
- Bedrock API usage
- S3 access logs

---

## Testing Strategy

### Unit Tests (`tests/`)
```python
def test_calculate_fico_score():
    loans = [
        {'fico': 700, 'balance': 10000},
        {'fico': 800, 'balance': 20000}
    ]
    avg = calculate_weighted_fico(loans)
    assert avg == 766.67
```

### Integration Tests
```python
def test_pipeline_end_to_end():
    # Run pipeline on test file
    result = run_pipeline('test_file.txt')
    # Verify DynamoDB insertion
    assert result['status'] == 'success'
```

---

## Future Enhancements

### Planned Features
1. **Real-time Processing**: Stream S3 events to Lambda
2. **Advanced Analytics**: Predictive modeling with SageMaker
3. **Alerting**: SNS notifications for anomalies
4. **Export**: Generate PDF reports
5. **Multi-tenant**: Support multiple organizations
6. **API**: REST API for programmatic access
7. **Mobile**: React Native app

---

## Summary

This system provides a complete **data pipeline → storage → visualization → AI intelligence** solution for auto loan portfolio analysis. It combines:

- 📊 **ETL**: Extract SEC filings, transform to metrics, load to DynamoDB
- 🎨 **Visualization**: Interactive Streamlit dashboard
- 🤖 **AI**: Natural language querying with Bedrock
- ☁️ **Cloud**: Serverless AWS architecture
- 🔒 **Security**: Environment-based credential management

**Total Components**: 7 Python modules, 1 web app, 2 AWS services, 1 AI model
**Lines of Code**: ~2,500 (excluding dependencies)
**Time to Insight**: < 30 seconds from question to answer

