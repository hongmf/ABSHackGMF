# Multi-Source Data Architecture

## Overview
The application now supports multiple data sources from different S3 buckets, each handled by specialized agents coordinated through an orchestrator pattern.

## Architecture Components

### 1. Data Sources (S3 Buckets)
Three separate S3 buckets are configured in `.env`:
- **S3_BUCKET_NAME1** (`abs-ee`): Auto loan ABS-EE filings
- **S3_BUCKET_NAME2** (`424h-prospectus`): Form 424H prospectus supplements
- **S3_BUCKET_NAME3** (`10-d`): Form 10-D distribution reports

### 2. Specialized Agents

#### VisualizationAgent (ABS-EE Auto Loans)
- **Location**: `src/visualization_agent.py`
- **Data Type**: Auto loan securitization (ABS-EE)
- **Capabilities**:
  - Portfolio overview charts
  - FICO score distributions
  - Delinquency trend analysis
  - Geographic distribution maps
  - Vehicle mix (new vs used)
  - Loan term analysis
  - Company comparisons
  - Interest rate trends

#### Form424HAgent (Prospectus Supplements)
- **Location**: `src/form_424h_agent.py`
- **Data Type**: Form 424H securities filings
- **Capabilities** (to be implemented):
  - Offering overview
  - Pricing analysis (spreads, yields)
  - Security structure visualization
  - Credit ratings comparison
  - Issuance timeline
  - Multi-offering comparison

#### Form10DAgent (Distribution Reports)
- **Location**: `src/form_10d_agent.py`
- **Data Type**: Form 10-D periodic reports
- **Capabilities** (to be implemented):
  - Distribution/payment analysis
  - Pool performance metrics
  - Delinquency trends over time
  - Prepayment speed (CPR, SMM)
  - Loss severity analysis
  - Pool balance trends
  - Trigger event monitoring

### 3. Agent Orchestrator
- **Location**: `src/langgraph_orchestrator.py` (using LangGraph)
- **Alternative**: `src/agent_orchestrator.py` (simple implementation)
- **Purpose**: Routes queries to the appropriate agent based on query analysis
- **Architecture**: Graph-based state management with LangGraph

#### LangGraph Implementation
The orchestrator uses a state graph with the following nodes:
- **classify_query**: Analyzes query keywords and determines data type
- **Router**: Conditional edge that routes to appropriate agent
- **Agent Nodes**: abs_ee_agent, 424h_agent, 10d_agent
- **no_agent**: Fallback for unknown queries

See [LANGGRAPH_ARCHITECTURE.md](LANGGRAPH_ARCHITECTURE.md) for detailed documentation.

#### Query Routing Examples
```python
# Routes to VisualizationAgent (ABS-EE)
"Show me auto loan delinquencies"
"What's the FICO score distribution?"
"Compare car loan performance"

# Routes to Form424HAgent
"Show me 424H offerings"
"What are the pricing details for the prospectus?"
"Display security structure"

# Routes to Form10DAgent
"Show distribution payments"
"What are the prepayment speeds?"
"Display 10-D pool performance"
```

### 4. S3 Multi-Source Manager
- **Location**: `src/s3_utils.py`
- **Class**: `MultiSourceS3Manager`
- **Purpose**: Manage file operations across multiple S3 buckets

## Data Flow

```
User Query (AI Assistant Tab)
        ↓
AgentOrchestrator.detect_data_type(query)
        ↓
    [Keyword Analysis]
        ↓
    ┌───┴───┬───────────┐
    ↓       ↓           ↓
ABS-EE   424H        10-D
Agent    Agent       Agent
    ↓       ↓           ↓
[Generate Visualizations]
    ↓       ↓           ↓
    └───┬───┴───────────┘
        ↓
Return: (figures, explanation)
        ↓
Display in Streamlit
```

## Configuration

### Environment Variables (.env)
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# S3 Buckets
S3_BUCKET_NAME1=abs-ee
S3_BUCKET_NAME2=424h-prospectus
S3_BUCKET_NAME3=10-d

# Bedrock Configuration
BEDROCK_KB_ID=your_kb_id
BEDROCK_REGION=us-west-2
BEDROCK_MODEL_ARN=your_model_arn
```

### Data Loading in app.py
```python
# Load multi-source data
data_sources = load_multi_source_data()

# data_sources structure:
{
    'abs-ee': {
        'data': [...],  # Raw data from DynamoDB/S3
        'df': pd.DataFrame(...)  # Processed DataFrame
    },
    '424h': {
        'data': [...],
        'df': pd.DataFrame(...)
    },
    '10-d': {
        'data': [...],
        'df': pd.DataFrame(...)
    }
}

# Initialize orchestrator
orchestrator = AgentOrchestrator(data_sources)

# Generate visualizations
figures, explanation = orchestrator.generate_visualizations(user_query)
```

## Implementation Status

### ✅ Completed
- AgentOrchestrator framework
- VisualizationAgent (fully implemented for ABS-EE)
- Form424HAgent (structure with placeholders)
- Form10DAgent (structure with placeholders)
- MultiSourceS3Manager for multi-bucket operations
- Integration with AI Assistant tab in Streamlit
- Environment configuration for 3 S3 buckets

### 🔄 In Progress / To Do
- Implement 424H data extraction pipeline
- Implement 10-D data extraction pipeline
- Fill in visualization methods for 424H agent
- Fill in visualization methods for 10-D agent
- Create separate DynamoDB tables or schema for 424H and 10-D data
- Update `load_multi_source_data()` to load 424H and 10-D data from their respective sources
- Add data processing pipeline for 424H files
- Add data processing pipeline for 10-D files

## Adding New Data Sources

To add a new data source:

1. **Create Agent Class** (`src/form_xyz_agent.py`):
```python
class FormXYZAgent:
    def __init__(self, data, df):
        self.data = data
        self.df = df
        self.keywords = {...}
    
    def analyze_query(self, query):
        # Query analysis logic
        pass
    
    def generate_visualizations(self, query):
        # Return (figures, explanation)
        pass
```

2. **Update AgentOrchestrator**:
- Add to `DataType` enum
- Add keywords to `detect_data_type()`
- Add initialization in `_initialize_agents()`

3. **Add S3 Bucket to .env**:
```bash
S3_BUCKET_NAMEX=your-bucket-name
```

4. **Update Data Loading**:
- Modify `load_multi_source_data()` in `app.py`
- Add data extraction for new source

## Benefits of This Architecture

1. **Separation of Concerns**: Each agent handles its specific data type
2. **Scalability**: Easy to add new data sources and agents
3. **Maintainability**: Changes to one agent don't affect others
4. **Flexibility**: Different visualization strategies per data type
5. **Intelligent Routing**: Automatic query routing based on context
6. **Reusability**: Agents can be used independently or through orchestrator

## Testing

### Test Query Routing
```python
from agent_orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator(data_sources)

# Test detection
data_type = orchestrator.detect_data_type("Show auto loan FICO scores")
# Should return: DataType.ABS_EE

data_type = orchestrator.detect_data_type("Display 424h pricing")
# Should return: DataType.FORM_424H

data_type = orchestrator.detect_data_type("Show 10-d distributions")
# Should return: DataType.FORM_10D
```

### Test Visualization Generation
```python
# Test with actual data
figures, explanation = orchestrator.generate_visualizations(
    "Compare auto loan delinquencies across companies"
)
print(f"Generated {len(figures)} visualizations")
print(f"Explanation: {explanation}")
```

## Troubleshooting

### Issue: Agent not routing correctly
- Check keyword lists in `detect_data_type()`
- Verify query contains expected keywords
- Test with more specific queries

### Issue: No visualizations generated
- Ensure data source is loaded in `data_sources` dict
- Verify agent is initialized properly
- Check that visualization methods are implemented (not placeholders)

### Issue: S3 bucket access errors
- Verify bucket names in `.env` file
- Check AWS credentials have permissions
- Ensure buckets exist and are accessible

## Future Enhancements

1. **Machine Learning-based Query Classification**: Replace keyword matching with ML model
2. **Cross-Source Comparisons**: Enable queries that span multiple data types
3. **Real-time Data Updates**: Stream data from S3 and update visualizations live
4. **Custom Agent Configuration**: Allow users to create custom agents via UI
5. **Agent Performance Metrics**: Track which agents are most used and effective
