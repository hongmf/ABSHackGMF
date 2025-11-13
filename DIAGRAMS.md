# Architecture Flow Diagrams

## 1. Complete System Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        Users[👥 End Users]
        Streamlit[Streamlit Web Application]
        Dashboard[📊 Dashboard Tab]
        Comparison[📈 Company Comparison]
        Geographic[🗺️ Geographic Analysis]
        Metrics[📉 Detailed Metrics]
        AIAssistant[🤖 AI Assistant Tab]
    end
    
    subgraph "AI Integration Layer"
        Bedrock[AWS Bedrock<br/>Claude 3.5 Sonnet]
        KB[Knowledge Base<br/>A7EOGV6BHS]
    end
    
    subgraph "LangGraph Orchestration Layer"
        Orchestrator[LangGraph Orchestrator]
        
        subgraph "State Graph"
            Classifier[classify_query Node<br/>Keyword Scoring]
            Router{Conditional Router}
        end
        
        subgraph "Agent Nodes"
            ABSAgent[abs_ee_agent Node<br/>Auto Loans]
            Form424Agent[424h_agent Node<br/>Prospectus]
            Form10DAgent[10d_agent Node<br/>Distributions]
            NoAgent[no_agent Node<br/>Fallback]
        end
        
        State[AgentState<br/>• messages<br/>• query<br/>• data_type<br/>• visualizations<br/>• explanation]
    end
    
    subgraph "Data Access Layer"
        DBHandler[DynamoDBHandler<br/>CRUD Operations]
        S3Manager[S3 Multi-Source Manager<br/>Cross-Bucket Ops]
        Extractor[Data Extractor<br/>SEC Parser]
    end
    
    subgraph "AWS Infrastructure"
        DynamoDB[(DynamoDB<br/>AutoLoanMetrics)]
        S3ABS[S3: abs-ee]
        S3_424H[S3: 424h-prospectus]
        S3_10D[S3: 10-d]
        IAM[IAM Roles<br/>Access Control]
    end
    
    Users -->|HTTP| Streamlit
    Streamlit --> Dashboard
    Streamlit --> Comparison
    Streamlit --> Geographic
    Streamlit --> Metrics
    Streamlit --> AIAssistant
    
    AIAssistant -->|Query| Bedrock
    Bedrock --> KB
    AIAssistant -->|Visualize| Orchestrator
    
    Orchestrator --> Classifier
    Classifier --> Router
    Router -->|abs-ee| ABSAgent
    Router -->|424h| Form424Agent
    Router -->|10-d| Form10DAgent
    Router -->|unknown| NoAgent
    
    State -.->|State Updates| Classifier
    State -.->|State Updates| ABSAgent
    State -.->|State Updates| Form424Agent
    State -.->|State Updates| Form10DAgent
    
    ABSAgent --> DBHandler
    Form424Agent --> DBHandler
    Form10DAgent --> DBHandler
    
    ABSAgent --> S3Manager
    Form424Agent --> S3Manager
    Form10DAgent --> S3Manager
    
    DBHandler --> DynamoDB
    S3Manager --> S3ABS
    S3Manager --> S3_424H
    S3Manager --> S3_10D
    
    Extractor --> DynamoDB
    Extractor --> S3ABS
    Extractor --> S3_424H
    Extractor --> S3_10D
    
    IAM -.->|Permissions| DynamoDB
    IAM -.->|Permissions| S3ABS
    IAM -.->|Permissions| S3_424H
    IAM -.->|Permissions| S3_10D
    
    style Users fill:#e1f5ff
    style Orchestrator fill:#ffe1e1
    style DynamoDB fill:#fff4e1
    style S3ABS fill:#e1ffe1
    style S3_424H fill:#e1ffe1
    style S3_10D fill:#e1ffe1
```

## 2. Query Processing Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as AI Assistant Tab
    participant Bedrock as AWS Bedrock KB
    participant Orch as LangGraph Orchestrator
    participant State as AgentState
    participant Classify as Classifier Node
    participant Router as Conditional Router
    participant Agent as Specialized Agent
    participant Data as DynamoDB
    
    User->>UI: Enter Query
    UI->>Bedrock: RAG Query
    Bedrock->>UI: Natural Language Answer
    UI->>Orch: Request Visualizations
    Orch->>State: Initialize State
    State->>Classify: Process Query
    Classify->>Classify: Keyword Scoring<br/>(abs-ee: 2, 424h: 0, 10-d: 0)
    Classify->>State: Update data_type = "abs-ee"
    State->>Router: Route Decision
    Router->>Agent: Execute abs_ee_agent
    Agent->>Data: Load Data
    Data-->>Agent: Return Metrics
    Agent->>Agent: Generate Visualizations
    Agent->>State: Update visualizations + explanation
    State->>Orch: Return Final State
    Orch->>UI: (figures, explanation)
    UI->>User: Display Charts & Text
```

## 3. LangGraph State Machine

```mermaid
stateDiagram-v2
    [*] --> START
    START --> classify_query: Initialize State
    
    state "classify_query Node" as classify_query {
        [*] --> AnalyzeKeywords
        AnalyzeKeywords --> ScoreDataTypes
        ScoreDataTypes --> SelectBest
        SelectBest --> UpdateState
        UpdateState --> [*]
    }
    
    classify_query --> ConditionalRouter: data_type classified
    
    state ConditionalRouter <<choice>>
    ConditionalRouter --> abs_ee_agent: if data_type == "abs-ee"
    ConditionalRouter --> form_424h_agent: if data_type == "424h"
    ConditionalRouter --> form_10d_agent: if data_type == "10-d"
    ConditionalRouter --> no_agent: if data_type == "unknown"
    
    state "abs_ee_agent Node" as abs_ee_agent {
        [*] --> LoadData
        LoadData --> GenerateViz
        GenerateViz --> UpdateState2
        UpdateState2 --> [*]
    }
    
    state "424h_agent Node" as form_424h_agent {
        [*] --> LoadData424
        LoadData424 --> GenerateViz424
        GenerateViz424 --> UpdateState424
        UpdateState424 --> [*]
    }
    
    state "10d_agent Node" as form_10d_agent {
        [*] --> LoadData10D
        LoadData10D --> GenerateViz10D
        GenerateViz10D --> UpdateState10D
        UpdateState10D --> [*]
    }
    
    state "no_agent Node" as no_agent {
        [*] --> CreateError
        CreateError --> [*]
    }
    
    abs_ee_agent --> END
    form_424h_agent --> END
    form_10d_agent --> END
    no_agent --> END
    
    END --> [*]: Return State
    
    note right of classify_query
        Keyword Matching with Scoring:
        - abs-ee: auto loan, fico, delinquency
        - 424h: prospectus, offering, pricing
        - 10-d: distribution, payment, CPR
    end note
    
    note right of abs_ee_agent
        ABS-EE Capabilities:
        - Portfolio metrics
        - FICO distributions
        - Delinquency rates
        - Geographic maps
    end note
```

## 4. Data Ingestion Pipeline

```mermaid
graph LR
    subgraph "Data Sources"
        SEC[SEC EDGAR<br/>Filings]
    end
    
    subgraph "S3 Storage Layer"
        S3_ABS[S3: abs-ee]
        S3_424H[S3: 424h-prospectus]
        S3_10D[S3: 10-d]
    end
    
    subgraph "Extraction Pipeline"
        Detect[1. File Detection<br/>List S3 Objects]
        Retrieve[2. Content Retrieval<br/>Download/Stream]
        Parse[3. Parsing<br/>Regex Extraction]
        Transform[4. Transform<br/>Calculate Metrics]
        Validate[5. Quality Check<br/>Validation]
    end
    
    subgraph "Storage"
        DB[(DynamoDB<br/>AutoLoanMetrics)]
    end
    
    SEC -->|Upload| S3_ABS
    SEC --> S3_424H
    SEC --> S3_10D
    
    S3_ABS --> Detect
    S3_424H --> Detect
    S3_10D --> Detect
    
    Detect --> Retrieve
    Retrieve --> Parse
    Parse --> Transform
    Transform --> Validate
    Validate --> DB
    
    style SEC fill:#e1f5ff
    style DB fill:#fff4e1
    style S3_ABS fill:#e1ffe1
    style S3_424H fill:#e1ffe1
    style S3_10D fill:#e1ffe1
```

## 5. Agent Architecture

```mermaid
graph TB
    Orchestrator[LangGraph Orchestrator<br/>Query Router]
    
    subgraph "VisualizationAgent (ABS-EE)"
        ABSCore[Agent Core<br/>Query Analysis]
        
        subgraph "Visualization Capabilities"
            Portfolio[Portfolio Overview<br/>Total Balance, Loans]
            FICO[FICO Distribution<br/>Credit Quality]
            Delinq[Delinquency Analysis<br/>30+, 60+, 90+ DPD]
            Geo[Geographic Maps<br/>State-level Heatmap]
            Vehicle[Vehicle Mix<br/>New vs Used]
            Compare[Company Comparison<br/>Multi-issuer]
            LoanTerm[Loan Term Analysis<br/>Duration Distribution]
            Interest[Interest Rate Trends<br/>Pricing Analysis]
        end
        
        ABSData[(ABS-EE Data<br/>DynamoDB)]
    end
    
    subgraph "Form424HAgent"
        F424Core[Agent Core<br/>Query Analysis]
        
        subgraph "424H Capabilities"
            Offering[Offering Details<br/>Size, Type, Timing]
            Pricing[Pricing Analysis<br/>Spreads, Yields]
            Structure[Security Structure<br/>Tranches, Classes]
            Ratings[Credit Ratings<br/>Agency Comparison]
            Timeline[Timeline<br/>Key Dates]
            Comp424[Multi-Offering<br/>Comparison]
        end
        
        F424Data[(424H Data<br/>DynamoDB)]
    end
    
    subgraph "Form10DAgent"
        F10DCore[Agent Core<br/>Query Analysis]
        
        subgraph "10-D Capabilities"
            Dist[Distribution Payments<br/>Cash Flow]
            Perf[Pool Performance<br/>KPI Metrics]
            Prepay[Prepayment Speed<br/>CPR, SMM]
            Loss[Loss Severity<br/>Charge-offs]
            Balance[Pool Balance<br/>Outstanding Principal]
            Triggers[Trigger Events<br/>Covenant Breaches]
        end
        
        F10DData[(10-D Data<br/>DynamoDB)]
    end
    
    Orchestrator --> ABSCore
    Orchestrator --> F424Core
    Orchestrator --> F10DCore
    
    ABSCore --> Portfolio
    ABSCore --> FICO
    ABSCore --> Delinq
    ABSCore --> Geo
    ABSCore --> Vehicle
    ABSCore --> Compare
    ABSCore --> LoanTerm
    ABSCore --> Interest
    
    F424Core --> Offering
    F424Core --> Pricing
    F424Core --> Structure
    F424Core --> Ratings
    F424Core --> Timeline
    F424Core --> Comp424
    
    F10DCore --> Dist
    F10DCore --> Perf
    F10DCore --> Prepay
    F10DCore --> Loss
    F10DCore --> Balance
    F10DCore --> Triggers
    
    ABSCore -.-> ABSData
    F424Core -.-> F424Data
    F10DCore -.-> F10DData
    
    style Orchestrator fill:#ffe1e1
    style ABSData fill:#fff4e1
    style F424Data fill:#fff4e1
    style F10DData fill:#fff4e1
```

## 6. Deployment Architecture

```mermaid
graph TB
    Users[👥 End Users]
    
    subgraph "Deployment Options"
        subgraph "Option 1: EC2 + Docker"
            EC2[EC2 Instance<br/>t3.medium]
            Docker[Docker Container<br/>Streamlit App]
            SG1[Security Group<br/>Port 8501]
        end
        
        subgraph "Option 2: ECS Fargate"
            ALB[Application<br/>Load Balancer]
            ECS[ECS Service<br/>Auto Scaling]
            Task[Fargate Task<br/>Serverless]
        end
        
        subgraph "Option 3: Streamlit Cloud"
            STCloud[Streamlit Cloud<br/>Managed Hosting]
            GitHub[GitHub Integration<br/>Auto Deploy]
        end
    end
    
    subgraph "Shared AWS Infrastructure"
        DDB[(DynamoDB<br/>On-Demand)]
        S3ABS[S3: abs-ee]
        S3_424[S3: 424h-prospectus]
        S3_10D[S3: 10-d]
        Bedrock[AWS Bedrock<br/>Claude 3.5]
        IAM[IAM Roles]
    end
    
    Users -->|HTTPS| EC2
    Users -->|HTTPS| ALB
    Users -->|HTTPS| STCloud
    
    EC2 --> SG1
    SG1 --> Docker
    
    ALB --> ECS
    ECS --> Task
    
    STCloud --> GitHub
    
    Docker --> DDB
    Docker --> S3ABS
    Docker --> S3_424
    Docker --> S3_10D
    Docker --> Bedrock
    
    Task --> DDB
    Task --> S3ABS
    Task --> S3_424
    Task --> S3_10D
    Task --> Bedrock
    
    STCloud --> DDB
    STCloud --> S3ABS
    STCloud --> S3_424
    STCloud --> S3_10D
    STCloud --> Bedrock
    
    IAM -.->|Permissions| DDB
    IAM -.->|Permissions| S3ABS
    IAM -.->|Permissions| S3_424
    IAM -.->|Permissions| S3_10D
    IAM -.->|Permissions| Bedrock
    
    style Users fill:#e1f5ff
    style DDB fill:#fff4e1
    style S3ABS fill:#e1ffe1
    style S3_424 fill:#e1ffe1
    style S3_10D fill:#e1ffe1
    style Bedrock fill:#ffe1f5
```

## 7. Technology Stack

```mermaid
graph LR
    subgraph "Frontend"
        Streamlit[Streamlit 1.31.0<br/>Web Framework]
        Plotly[Plotly 5.18.0<br/>Visualizations]
    end
    
    subgraph "Orchestration"
        LangGraph[LangGraph 0.2.0+<br/>State Graphs]
        LangChain[LangChain 0.3.0+<br/>AI Framework]
    end
    
    subgraph "Data Processing"
        Pandas[Pandas 2.2.3<br/>Data Manipulation]
        Python[Python 3.8+<br/>Core Language]
    end
    
    subgraph "AWS Services"
        Boto3[Boto3 1.35.36<br/>AWS SDK]
        DynamoDB[DynamoDB<br/>NoSQL Database]
        S3[S3<br/>Object Storage]
        Bedrock[Bedrock<br/>AI/ML Services]
    end
    
    Streamlit --> Plotly
    Streamlit --> LangGraph
    LangGraph --> LangChain
    LangGraph --> Pandas
    Pandas --> Python
    Python --> Boto3
    Boto3 --> DynamoDB
    Boto3 --> S3
    Boto3 --> Bedrock
    
    style Streamlit fill:#e1f5ff
    style LangGraph fill:#ffe1e1
    style DynamoDB fill:#fff4e1
```

---

## How to View These Diagrams

### In GitHub
These Mermaid diagrams render automatically in GitHub markdown files.

### In VS Code
Install the "Markdown Preview Mermaid Support" extension:
```
code --install-extension bierner.markdown-mermaid
```

### Export as Images
Use Mermaid Live Editor: https://mermaid.live/
1. Copy diagram code
2. Paste into editor
3. Export as PNG/SVG

### In Documentation Sites
Most documentation platforms (GitBook, MkDocs, Docusaurus) support Mermaid natively.
