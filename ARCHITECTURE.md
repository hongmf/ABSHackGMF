# ABS Data Analytics Platform - System Architecture

## Executive Summary

The ABS (Asset-Backed Securities) Data Analytics Platform is an enterprise-grade solution for extracting, analyzing, and visualizing SEC filing data across multiple asset classes. Built with a modern microservices-inspired architecture, the platform leverages AI-powered agents orchestrated through LangGraph to deliver intelligent data insights.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Presentation Layer                              │
│                    (Streamlit Web Application)                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Dashboard Tab  │  Company Comparison  │  Geographic  │  AI Assistant  │
│                 │                      │  Analysis    │                 │
└────────┬────────┴──────────────────────┴──────────────┴────────────────┘
         │
         ├─────────────────────────────────────────────────────────────┐
         │                                                             │
         ▼                                                             ▼
┌─────────────────────────┐                              ┌──────────────────────┐
│   Data Loading Layer    │                              │  AI Integration      │
│                         │                              │  Layer               │
│  • Multi-Source Loader  │                              │                      │
│  • Data Transformation  │                              │  • AWS Bedrock KB    │
│  • Cache Management     │                              │  • Claude 3.5 Sonnet │
└────────┬────────────────┘                              └──────────┬───────────┘
         │                                                          │
         ▼                                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestration Layer                        │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────┐     │
│   │              State Graph Architecture                       │     │
│   │                                                             │     │
│   │   START → Classify Query → Router → Agent Nodes → END      │     │
│   │                                                             │     │
│   │   Router Logic:                                            │     │
│   │   • Keyword Scoring Algorithm                              │     │
│   │   • Data Type Classification                               │     │
│   │   • Conditional Edge Routing                               │     │
│   └─────────────────────────────────────────────────────────────┘     │
│                                                                         │
│   Agent State Management:                                              │
│   • Conversation History (LangChain Messages)                          │
│   • Query Context & Metadata                                           │
│   • Visualization Results                                              │
│   • Execution Trace                                                    │
└─────────┬───────────────────────────────────────────────────────────────┘
          │
          ├──────────────┬──────────────┬──────────────┬──────────────┐
          ▼              ▼              ▼              ▼              ▼
┌─────────────────┐ ┌──────────────┐ ┌────────────┐ ┌───────────────────┐
│ VisualizationAgent│ │Form424HAgent│ │Form10DAgent│ │  Future Agents   │
│   (ABS-EE)      │ │  (Prospectus)│ │(Distrib.)  │ │   (Extensible)    │
│                 │ │              │ │            │ │                   │
│ • Portfolio     │ │ • Offerings  │ │ • Payments │ │ • Custom Types    │
│ • FICO Scores   │ │ • Pricing    │ │ • CPR/SMM  │ │ • New SEC Forms   │
│ • Delinquencies │ │ • Structure  │ │ • Balance  │ │ • Integration     │
│ • Geography     │ │ • Ratings    │ │ • Triggers │ │                   │
└────────┬────────┘ └──────┬───────┘ └─────┬──────┘ └─────────┬─────────┘
         │                 │               │                  │
         └─────────────────┴───────────────┴──────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Data Access Layer                                │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │  DynamoDB        │  │  S3 Multi-Source │  │  Data Extraction │    │
│  │  Operations      │  │  Manager         │  │  Pipeline        │    │
│  │                  │  │                  │  │                  │    │
│  │  • CRUD Ops      │  │  • abs-ee        │  │  • SEC Parser    │    │
│  │  • Scan/Query    │  │  • 424h-prosp.   │  │  • Metrics Calc  │    │
│  │  • Batch Ops     │  │  • 10-d          │  │  • Validation    │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      AWS Infrastructure Layer                            │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  DynamoDB    │  │  S3 Buckets  │  │  Bedrock     │  │  IAM      │ │
│  │              │  │              │  │              │  │           │ │
│  │ • NoSQL DB   │  │ • Raw Data   │  │ • KB Query   │  │ • Auth    │ │
│  │ • Auto Scale │  │ • Multi-Src  │  │ • AI Models  │  │ • Perms   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Presentation Layer

#### Streamlit Web Application (`app.py`)
- **Framework**: Streamlit 1.31.0
- **Purpose**: Interactive web interface for data visualization and analysis
- **Key Features**:
  - Multi-tab navigation (Dashboard, Comparisons, Geography, Metrics, AI Assistant)
  - Real-time data filtering and drill-down
  - Interactive Plotly visualizations
  - Responsive design with custom CSS

**Tabs**:
- **Dashboard**: Portfolio overview with key metrics
- **Company Comparison**: Side-by-side analysis across issuers
- **Geographic Analysis**: State-level heat maps and distributions
- **Detailed Metrics**: Deep-dive into specific KPIs
- **AI Assistant**: Natural language query interface with Bedrock integration

### 2. Orchestration Layer

#### LangGraph State Machine (`src/langgraph_orchestrator.py`)

**Architecture Pattern**: Graph-based State Management

```python
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]      # Conversation context
    query: str                           # User input
    data_type: str                       # Classified type
    visualizations: List[go.Figure]      # Generated charts
    explanation: str                     # Human-readable output
    data_sources: Dict[str, Any]         # Available data
    next_action: str                     # Flow control
```

**Graph Nodes**:

1. **classify_query**
   - Input: User query
   - Process: Keyword matching with weighted scoring
   - Output: Data type classification (abs-ee | 424h | 10-d | unknown)

2. **Conditional Router**
   - Decision tree based on data type
   - Routes to appropriate specialized agent
   - Fallback to no_agent for unknown types

3. **Agent Execution Nodes**
   - `abs_ee_agent`: Auto loan analysis
   - `424h_agent`: Prospectus analysis
   - `10d_agent`: Distribution report analysis
   - `no_agent`: Error handling and user guidance

**State Flow**:
```
Query → Classification → Scoring → Routing → Agent Execution → Result
```

**Benefits**:
- Stateful execution with full audit trail
- Extensible architecture (add nodes/edges easily)
- Built-in error handling and fallback logic
- Integration-ready with LangChain ecosystem

### 3. Agent Layer

#### Specialized Data Agents

##### VisualizationAgent (`src/visualization_agent.py`)
**Data Source**: ABS-EE Auto Loan Securitizations

**Capabilities**:
- Portfolio Metrics: Total balance, loan counts, weighted averages
- Credit Quality: FICO score distributions, credit tiers
- Performance: Delinquency rates (30+, 60+, 90+ days)
- Asset Mix: New vs used vehicle ratios
- Geographic Distribution: State-level analysis with heat maps
- Loan Characteristics: Term distribution, interest rate trends
- Comparative Analysis: Multi-company benchmarking

**Visualization Types**: 8 distinct chart types using Plotly

##### Form424HAgent (`src/form_424h_agent.py`)
**Data Source**: Form 424H Prospectus Supplements

**Capabilities** (Framework Ready):
- Offering details and issuance size
- Pricing analysis (spreads, yields)
- Security structure and tranches
- Credit ratings comparison
- Timeline and key dates
- Multi-offering benchmarking

##### Form10DAgent (`src/form_10d_agent.py`)
**Data Source**: Form 10-D Distribution Reports

**Capabilities** (Framework Ready):
- Distribution/payment tracking
- Pool performance metrics
- Delinquency and prepayment trends
- Loss severity analysis
- Trigger event monitoring
- Historical comparisons

### 4. Data Access Layer

#### DynamoDB Operations (`src/dynamodb_operations.py`)

**Class**: `DynamoDBHandler`

**Operations**:
- `create_table()`: Schema creation with auto-scaling
- `insert_metrics()`: Single record insertion
- `batch_insert_metrics()`: Bulk operations (25 items/batch)
- `get_metrics()`: Point queries by company/period
- `scan_all_metrics()`: Full table scan with pagination
- `query_by_company()`: Filtered queries

**Schema Design**:
```python
{
    'company_name': str,           # Partition Key
    'reporting_period': str,       # Sort Key
    'total_loans': int,
    'total_pool_balance': Decimal,
    'average_fico_score': Decimal,
    'delinquency_*_rate': Decimal,
    'prepayment_speed_*': Decimal,
    'geographic_distribution': dict,
    'fico_distribution': dict,
    # ... additional metrics
}
```

#### S3 Multi-Source Manager (`src/s3_utils.py`)

**Classes**:
- `S3FileManager`: Single bucket operations
- `MultiSourceS3Manager`: Cross-bucket coordination

**Supported Buckets**:
```python
{
    'abs-ee': 'abs-ee',                    # Auto loans
    '424h': '424h-prospectus',             # Prospectus
    '10-d': '10-d'                         # Distributions
}
```

**Operations**:
- File listing with pagination
- Content retrieval (text/binary)
- Download to local filesystem
- Existence checks
- Metadata extraction

#### Data Extraction Pipeline (`src/data_extractor.py`)

**Class**: `AutoLoanDataExtractor`

**Process Flow**:
1. **Ingestion**: Read from S3 or local file
2. **Parsing**: Regex-based extraction of structured data
3. **Validation**: Data quality checks
4. **Transformation**: Calculate derived metrics
5. **Normalization**: Standard formats and types

**Extracted Metrics**:
- Portfolio totals and averages
- Credit score distributions
- Delinquency buckets
- Geographic breakdowns
- Vehicle characteristics
- Loan terms and rates

### 5. AWS Infrastructure Layer

#### Amazon DynamoDB
- **Table**: AutoLoanMetrics
- **Capacity**: On-demand (auto-scaling)
- **Keys**: Composite (company_name, reporting_period)
- **GSI**: Potential secondary indexes for reporting_period queries

#### Amazon S3
- **Buckets**: 3 independent data sources
- **Organization**: Flat or prefixed structure
- **Access**: IAM role-based or key-based
- **Encryption**: Server-side encryption (SSE-S3)

#### AWS Bedrock
- **Model**: Claude 3.5 Sonnet (anthropic.claude-3-5-sonnet-20241022-v2:0)
- **Knowledge Base**: A7EOGV6BHS
- **Region**: us-west-2
- **Use Case**: Natural language query answering with retrieval augmentation

## Data Flow Diagrams

### Query Processing Flow

```
┌─────────────┐
│   User      │
│   Query     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  Streamlit AI Assistant Tab                 │
│  • Capture user input                       │
│  • Display conversation history             │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  AWS Bedrock Knowledge Base Query           │
│  • Retrieve context from KB                 │
│  • Generate natural language answer         │
│  • Extract source citations                 │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  LangGraph Orchestrator                     │
│                                             │
│  1. classify_query Node                     │
│     • Analyze keywords                      │
│     • Score data types                      │
│     • Select best match                     │
│                                             │
│  2. Conditional Router                      │
│     • Evaluate data_type                    │
│     • Route to agent node                   │
│                                             │
│  3. Agent Execution                         │
│     • Load data source                      │
│     • Generate visualizations               │
│     • Create explanation                    │
│                                             │
│  4. Return Results                          │
│     • List of Plotly figures                │
│     • Human-readable explanation            │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  Streamlit Display                          │
│  • Render answer text                       │
│  • Show source citations                    │
│  • Display visualizations                   │
│  • Update conversation history              │
└─────────────────────────────────────────────┘
```

### Data Ingestion Flow

```
┌────────────────┐
│  SEC Filings   │
│  (Raw Text)    │
└───────┬────────┘
        │
        ▼
┌────────────────────────────────┐
│  S3 Storage                    │
│  • abs-ee bucket               │
│  • 424h-prospectus bucket      │
│  • 10-d bucket                 │
└───────┬────────────────────────┘
        │
        ▼
┌────────────────────────────────┐
│  Data Extraction Pipeline      │
│                                │
│  1. File Detection             │
│     • S3FileManager            │
│     • List available files     │
│                                │
│  2. Content Retrieval          │
│     • Download/stream file     │
│     • Handle encoding          │
│                                │
│  3. Parsing                    │
│     • Regex extraction         │
│     • Section identification   │
│     • Table parsing            │
│                                │
│  4. Transformation             │
│     • Calculate metrics        │
│     • Normalize formats        │
│     • Validate data            │
│                                │
│  5. Quality Assurance          │
│     • Check completeness       │
│     • Verify ranges            │
│     • Flag anomalies           │
└───────┬────────────────────────┘
        │
        ▼
┌────────────────────────────────┐
│  DynamoDB Storage              │
│  • Insert/update records       │
│  • Maintain history            │
│  • Enable querying             │
└────────────────────────────────┘
```

## Technology Stack

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.8+ | Core development language |
| Web Framework | Streamlit | 1.31.0 | UI and dashboard |
| Orchestration | LangGraph | 0.2.0+ | Agent coordination |
| AI Framework | LangChain | 0.3.0+ | LLM integration |
| Visualization | Plotly | 5.18.0 | Interactive charts |
| Data Processing | Pandas | 2.2.3 | Data manipulation |
| AWS SDK | Boto3 | 1.35.36 | AWS service integration |

### AWS Services
| Service | Usage | Configuration |
|---------|-------|---------------|
| DynamoDB | Metrics storage | On-demand capacity |
| S3 | Raw data storage | 3 buckets, multi-region |
| Bedrock | AI/LLM services | Claude 3.5 Sonnet |
| Knowledge Base | RAG for queries | A7EOGV6BHS |
| IAM | Authentication | Role-based access |

### Development Tools
| Tool | Purpose |
|------|---------|
| Git | Version control |
| pytest | Unit testing |
| python-dotenv | Configuration management |
| VS Code | Development environment |

## Security Architecture

### Authentication & Authorization
- **AWS IAM**: Role-based access control
- **Access Keys**: Stored in `.env` (local), AWS Secrets Manager (production)
- **Least Privilege**: Minimal permissions per service

### Data Security
- **Encryption at Rest**: S3 and DynamoDB server-side encryption
- **Encryption in Transit**: HTTPS for all API calls
- **Secrets Management**: Environment variables, no hardcoded credentials

### Network Security
- **API Gateway**: (Future) Rate limiting and throttling
- **VPC**: (Future) Private subnet deployment for sensitive workloads

## Scalability & Performance

### Horizontal Scaling
- **DynamoDB**: Auto-scaling with on-demand capacity
- **S3**: Virtually unlimited storage
- **Stateless Architecture**: Enables load balancing across instances

### Performance Optimization
- **Caching**: Streamlit `@st.cache_data` for expensive operations
- **Batch Processing**: DynamoDB batch writes (25 items)
- **Lazy Loading**: Load data only when needed
- **Pagination**: Handle large result sets incrementally

### Monitoring & Observability
- **LangGraph State**: Built-in execution tracing
- **CloudWatch**: (Recommended) AWS service metrics
- **Application Logs**: Structured logging for debugging
- **Error Tracking**: Exception handling at each layer

## Deployment Architecture

### Development Environment
```
Local Machine
├── Python Virtual Environment
├── Streamlit Dev Server (port 8501)
├── AWS Credentials (local .env)
└── Git Repository (branch: David)
```

### Production Deployment Options

#### Option 1: AWS EC2 + Docker
```
EC2 Instance (t3.medium)
├── Docker Container
│   ├── Python Runtime
│   ├── Streamlit App
│   └── Application Code
├── Security Group (port 8501)
├── IAM Instance Profile
└── CloudWatch Logs
```

#### Option 2: AWS ECS Fargate
```
ECS Cluster
├── Task Definition
│   ├── Container Image
│   └── Environment Variables
├── Service (Auto Scaling)
├── Application Load Balancer
└── CloudWatch Monitoring
```

#### Option 3: Streamlit Cloud
```
Streamlit Cloud
├── GitHub Integration
├── Automatic Deployments
├── Secrets Management
└── Custom Domain (optional)
```

## Extension Points

### Adding New Data Sources

1. **Create Agent** (`src/new_agent.py`)
2. **Update LangGraph**:
   - Add node in `_build_graph()`
   - Update router logic
   - Add keywords to classifier
3. **Configure S3**: Add bucket to `.env`
4. **Update Data Loader**: Modify `load_multi_source_data()`

### Adding New Visualizations

1. **Update Agent**: Add `_create_*_chart()` method
2. **Update Keywords**: Add triggers in `analyze_query()`
3. **Test**: Verify routing and rendering

### Integrating LLM-based Classification

```python
from langchain_openai import ChatOpenAI

def _classify_query(self, state):
    llm = ChatOpenAI()
    prompt = f"""Classify this query into one of:
    - abs-ee (auto loans)
    - 424h (prospectus)
    - 10-d (distributions)
    
    Query: {state['query']}
    Return only the data type."""
    
    response = llm.invoke(prompt)
    state['data_type'] = response.content.strip()
    return state
```

## Best Practices & Standards

### Code Quality
- **PEP 8**: Python style guide compliance
- **Type Hints**: Use for function signatures
- **Docstrings**: Document all classes and public methods
- **Error Handling**: Try-except with specific exceptions

### Testing Strategy
- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test full user workflows
- **Data Validation**: Verify extraction accuracy

### Configuration Management
- **Environment Variables**: All configuration in `.env`
- **No Hardcoding**: Avoid embedded credentials or URLs
- **Version Control**: `.env.example` in repo, `.env` in `.gitignore`

### Documentation
- **README**: Setup and quick start
- **Architecture Docs**: This document
- **API Documentation**: Inline docstrings
- **Runbooks**: Operational procedures

## Performance Benchmarks

### Current Performance (Development)
- **Page Load**: ~2-3 seconds
- **Data Query**: ~500ms (DynamoDB scan)
- **Visualization Generation**: ~1-2 seconds
- **AI Query**: ~3-5 seconds (Bedrock + LangGraph)

### Optimization Targets (Production)
- **Page Load**: <1 second
- **Data Query**: <200ms (with caching)
- **Visualization**: <500ms
- **AI Query**: <2 seconds

## Disaster Recovery & Business Continuity

### Backup Strategy
- **DynamoDB**: Point-in-time recovery (PITR)
- **S3**: Versioning enabled on all buckets
- **Code**: Git repository with multiple remotes
- **Configuration**: `.env` backups in secure location

### Recovery Procedures
1. **Database Failure**: Restore from DynamoDB PITR
2. **Data Corruption**: Revert S3 object versions
3. **Application Failure**: Rollback to previous Git commit
4. **Region Failure**: Multi-region deployment (future)

## Compliance & Governance

### Data Privacy
- **SEC Data**: Public domain, no PII
- **User Queries**: Not persisted beyond session
- **Audit Logs**: Track access patterns

### Regulatory Considerations
- **SEC Compliance**: Accurate data representation
- **Data Retention**: Follow organizational policies
- **Access Control**: Audit trail for sensitive operations

## Future Roadmap

### Phase 1: Foundation (Complete)
- ✅ Multi-agent architecture
- ✅ LangGraph orchestration
- ✅ Three data sources (ABS-EE, 424H, 10-D)
- ✅ Basic visualizations

### Phase 2: Enhancement (Q1 2026)
- [ ] Implement 424H data extraction
- [ ] Implement 10-D data extraction
- [ ] LLM-based query classification
- [ ] Advanced visualizations (predictive analytics)

### Phase 3: Scale (Q2 2026)
- [ ] Real-time data streaming
- [ ] Multi-user support with authentication
- [ ] API layer (REST/GraphQL)
- [ ] Mobile-responsive UI

### Phase 4: Intelligence (Q3 2026)
- [ ] Anomaly detection
- [ ] Predictive modeling
- [ ] Natural language report generation
- [ ] Automated alerts and notifications

## Conclusion

The ABS Data Analytics Platform represents a modern, scalable approach to financial data analysis. By leveraging graph-based orchestration, specialized AI agents, and cloud-native AWS services, the platform delivers intelligent insights across multiple asset classes while maintaining flexibility for future enhancements.

The architecture is designed for:
- **Modularity**: Independent agents and clear separation of concerns
- **Scalability**: Cloud-native components with auto-scaling
- **Maintainability**: Clean code structure with comprehensive documentation
- **Extensibility**: Easy addition of new data sources and agents
- **Reliability**: Error handling and fallback mechanisms at every layer

---

**Document Version**: 1.0  
**Last Updated**: November 13, 2025  
**Author**: AI Assistant  
**Repository**: ABSHackGMF (DavidAwe00/David)
