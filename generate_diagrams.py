"""
System Architecture Diagram Generator

Generates visual diagrams for the ABS Data Analytics Platform architecture
using various diagram tools and formats.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.storage import S3, SimpleStorageServiceS3 as S3Bucket
from diagrams.aws.database import Dynamodb
from diagrams.aws.ml import SagemakerModel
from diagrams.aws.security import IAM
from diagrams.programming.language import Python
from diagrams.onprem.client import Users
from diagrams.custom import Custom
import os


def generate_system_architecture():
    """Generate complete system architecture diagram"""
    
    graph_attr = {
        "fontsize": "16",
        "bgcolor": "white",
        "pad": "0.5"
    }
    
    with Diagram(
        "ABS Data Analytics Platform - System Architecture",
        filename="architecture_system",
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=graph_attr
    ):
        users = Users("End Users")
        
        with Cluster("Presentation Layer"):
            streamlit = Python("Streamlit\nWeb App")
            dashboard = Python("Dashboard UI")
            ai_assistant = Python("AI Assistant")
            
        with Cluster("AI Integration Layer"):
            bedrock = SagemakerModel("AWS Bedrock\nClaude 3.5")
            knowledge_base = SagemakerModel("Knowledge Base")
            
        with Cluster("LangGraph Orchestration Layer"):
            orchestrator = Python("LangGraph\nOrchestrator")
            
            with Cluster("State Graph"):
                classifier = Python("Query\nClassifier")
                router = Python("Conditional\nRouter")
                
            with Cluster("Agent Nodes"):
                abs_agent = Python("ABS-EE\nAgent")
                form424_agent = Python("424H\nAgent")
                form10d_agent = Python("10-D\nAgent")
        
        with Cluster("Data Access Layer"):
            dynamodb_handler = Python("DynamoDB\nHandler")
            s3_manager = Python("S3 Multi-Source\nManager")
            extractor = Python("Data\nExtractor")
        
        with Cluster("AWS Infrastructure"):
            dynamodb = Dynamodb("DynamoDB\nAutoLoanMetrics")
            
            with Cluster("S3 Data Sources"):
                s3_abs = S3Bucket("abs-ee\nBucket")
                s3_424h = S3Bucket("424h-prospectus\nBucket")
                s3_10d = S3Bucket("10-d\nBucket")
            
            iam = IAM("IAM\nAccess Control")
        
        # User flow
        users >> Edge(label="HTTP") >> streamlit
        streamlit >> dashboard
        streamlit >> ai_assistant
        
        # AI Assistant flow
        ai_assistant >> Edge(label="Query") >> bedrock
        bedrock >> knowledge_base
        ai_assistant >> Edge(label="Visualize") >> orchestrator
        
        # Orchestrator flow
        orchestrator >> classifier >> router
        router >> Edge(label="ABS-EE") >> abs_agent
        router >> Edge(label="424H") >> form424_agent
        router >> Edge(label="10-D") >> form10d_agent
        
        # Agent to data access
        abs_agent >> dynamodb_handler
        form424_agent >> dynamodb_handler
        form10d_agent >> dynamodb_handler
        
        abs_agent >> s3_manager
        form424_agent >> s3_manager
        form10d_agent >> s3_manager
        
        # Data access to AWS
        dynamodb_handler >> dynamodb
        s3_manager >> s3_abs
        s3_manager >> s3_424h
        s3_manager >> s3_10d
        
        extractor >> dynamodb
        extractor >> s3_abs
        extractor >> s3_424h
        extractor >> s3_10d
        
        # Security
        iam >> dynamodb
        iam >> s3_abs


def generate_query_flow():
    """Generate query processing flow diagram"""
    
    with Diagram(
        "Query Processing Flow",
        filename="architecture_query_flow",
        outformat="png",
        show=False,
        direction="TB"
    ):
        user = Users("User")
        
        with Cluster("User Interface"):
            ui = Python("AI Assistant\nTab")
            
        with Cluster("AI Layer"):
            bedrock = SagemakerModel("Bedrock\nKnowledge Base")
            
        with Cluster("LangGraph Orchestration"):
            with Cluster("State Management"):
                state = Python("Agent State")
                
            classify = Python("1. Classify\nQuery")
            route = Python("2. Route\nDecision")
            
            with Cluster("Agent Execution"):
                agent1 = Python("ABS-EE\nAgent")
                agent2 = Python("424H\nAgent")
                agent3 = Python("10-D\nAgent")
                no_agent = Python("No Agent\nFallback")
        
        with Cluster("Data Layer"):
            data = Dynamodb("DynamoDB")
            
        with Cluster("Results"):
            viz = Python("Visualizations")
            explain = Python("Explanation")
        
        # Flow
        user >> Edge(label="Query") >> ui
        ui >> Edge(label="RAG Query") >> bedrock
        bedrock >> Edge(label="Answer") >> ui
        ui >> Edge(label="Viz Request") >> state
        state >> classify
        classify >> Edge(label="Scored") >> route
        
        route >> Edge(label="auto loan") >> agent1
        route >> Edge(label="prospectus") >> agent2
        route >> Edge(label="distribution") >> agent3
        route >> Edge(label="unknown") >> no_agent
        
        agent1 >> data
        agent2 >> data
        agent3 >> data
        
        agent1 >> viz
        agent2 >> viz
        agent3 >> viz
        no_agent >> explain
        
        viz >> Edge(label="Display") >> ui
        explain >> Edge(label="Display") >> ui


def generate_data_ingestion_flow():
    """Generate data ingestion pipeline diagram"""
    
    with Diagram(
        "Data Ingestion Pipeline",
        filename="architecture_data_ingestion",
        outformat="png",
        show=False,
        direction="LR"
    ):
        with Cluster("Data Sources"):
            sec = Users("SEC\nFilings")
            
        with Cluster("S3 Storage"):
            s3_abs = S3Bucket("abs-ee")
            s3_424h = S3Bucket("424h-prospectus")
            s3_10d = S3Bucket("10-d")
        
        with Cluster("Extraction Pipeline"):
            detect = Python("1. File\nDetection")
            retrieve = Python("2. Content\nRetrieval")
            parse = Python("3. Parsing &\nExtraction")
            transform = Python("4. Transform &\nCalculate")
            validate = Python("5. Quality\nAssurance")
        
        with Cluster("Storage"):
            dynamodb = Dynamodb("DynamoDB\nMetrics")
        
        # Flow
        sec >> Edge(label="Upload") >> s3_abs
        sec >> s3_424h
        sec >> s3_10d
        
        s3_abs >> detect
        s3_424h >> detect
        s3_10d >> detect
        
        detect >> retrieve >> parse >> transform >> validate >> dynamodb


def generate_langgraph_state_machine():
    """Generate LangGraph state machine diagram"""
    
    with Diagram(
        "LangGraph State Machine",
        filename="architecture_langgraph_state",
        outformat="png",
        show=False,
        direction="TB"
    ):
        with Cluster("Entry Point"):
            start = Python("START")
            
        with Cluster("Classification"):
            classify = Python("classify_query\nNode")
            
        with Cluster("Routing Logic"):
            router = Python("Conditional\nRouter")
            
        with Cluster("Agent Execution Nodes"):
            abs_ee = Python("abs_ee_agent\nNode")
            form_424h = Python("424h_agent\nNode")
            form_10d = Python("10d_agent\nNode")
            no_agent = Python("no_agent\nNode")
            
        with Cluster("Exit Point"):
            end = Python("END")
        
        with Cluster("State Object"):
            state = Python("AgentState\n• messages\n• query\n• data_type\n• visualizations\n• explanation")
        
        # Flow
        start >> Edge(label="initial state") >> classify
        classify >> Edge(label="classified") >> router
        
        router >> Edge(label="abs-ee") >> abs_ee
        router >> Edge(label="424h") >> form_424h
        router >> Edge(label="10-d") >> form_10d
        router >> Edge(label="unknown") >> no_agent
        
        abs_ee >> Edge(label="results") >> end
        form_424h >> end
        form_10d >> end
        no_agent >> end
        
        # State connections
        state >> Edge(style="dashed", color="gray") >> classify
        state >> Edge(style="dashed", color="gray") >> abs_ee
        state >> Edge(style="dashed", color="gray") >> form_424h
        state >> Edge(style="dashed", color="gray") >> form_10d


def generate_agent_architecture():
    """Generate specialized agent architecture diagram"""
    
    with Diagram(
        "Specialized Agent Architecture",
        filename="architecture_agents",
        outformat="png",
        show=False,
        direction="TB"
    ):
        orchestrator = Python("LangGraph\nOrchestrator")
        
        with Cluster("VisualizationAgent (ABS-EE)"):
            abs_agent = Python("Agent Core")
            
            with Cluster("Capabilities"):
                portfolio = Python("Portfolio\nMetrics")
                fico = Python("FICO\nDistribution")
                delinq = Python("Delinquency\nAnalysis")
                geo = Python("Geographic\nMaps")
                vehicle = Python("Vehicle\nMix")
                compare = Python("Company\nComparison")
            
            abs_data = Dynamodb("ABS-EE\nData")
        
        with Cluster("Form424HAgent"):
            form424_agent = Python("Agent Core")
            
            with Cluster("Capabilities"):
                offering = Python("Offering\nDetails")
                pricing = Python("Pricing\nAnalysis")
                structure = Python("Security\nStructure")
                ratings = Python("Credit\nRatings")
            
            form424_data = Dynamodb("424H\nData")
        
        with Cluster("Form10DAgent"):
            form10d_agent = Python("Agent Core")
            
            with Cluster("Capabilities"):
                dist = Python("Distribution\nPayments")
                perf = Python("Pool\nPerformance")
                prepay = Python("Prepayment\nSpeed")
                loss = Python("Loss\nSeverity")
            
            form10d_data = Dynamodb("10-D\nData")
        
        # Connections
        orchestrator >> abs_agent
        orchestrator >> form424_agent
        orchestrator >> form10d_agent
        
        abs_agent >> portfolio
        abs_agent >> fico
        abs_agent >> delinq
        abs_agent >> geo
        abs_agent >> vehicle
        abs_agent >> compare
        
        form424_agent >> offering
        form424_agent >> pricing
        form424_agent >> structure
        form424_agent >> ratings
        
        form10d_agent >> dist
        form10d_agent >> perf
        form10d_agent >> prepay
        form10d_agent >> loss
        
        abs_agent >> abs_data
        form424_agent >> form424_data
        form10d_agent >> form10d_data


def generate_deployment_architecture():
    """Generate deployment options diagram"""
    
    with Diagram(
        "Deployment Architecture Options",
        filename="architecture_deployment",
        outformat="png",
        show=False,
        direction="LR"
    ):
        users = Users("Users")
        
        with Cluster("Option 1: EC2 + Docker"):
            ec2 = Python("EC2 Instance\nt3.medium")
            docker = Python("Docker\nContainer")
            
        with Cluster("Option 2: ECS Fargate"):
            ecs = Python("ECS Service\nAuto Scaling")
            alb = Python("Application\nLoad Balancer")
            
        with Cluster("Option 3: Streamlit Cloud"):
            streamlit_cloud = Python("Streamlit\nCloud")
        
        with Cluster("Shared Infrastructure"):
            dynamodb = Dynamodb("DynamoDB")
            s3 = S3("S3 Buckets")
            bedrock = SagemakerModel("Bedrock")
        
        users >> ec2 >> docker
        users >> alb >> ecs
        users >> streamlit_cloud
        
        docker >> dynamodb
        docker >> s3
        docker >> bedrock
        
        ecs >> dynamodb
        ecs >> s3
        ecs >> bedrock
        
        streamlit_cloud >> dynamodb
        streamlit_cloud >> s3
        streamlit_cloud >> bedrock


if __name__ == "__main__":
    print("Generating architecture diagrams...")
    print("\n1. System Architecture...")
    generate_system_architecture()
    print("   ✓ architecture_system.png created")
    
    print("\n2. Query Processing Flow...")
    generate_query_flow()
    print("   ✓ architecture_query_flow.png created")
    
    print("\n3. Data Ingestion Pipeline...")
    generate_data_ingestion_flow()
    print("   ✓ architecture_data_ingestion.png created")
    
    print("\n4. LangGraph State Machine...")
    generate_langgraph_state_machine()
    print("   ✓ architecture_langgraph_state.png created")
    
    print("\n5. Agent Architecture...")
    generate_agent_architecture()
    print("   ✓ architecture_agents.png created")
    
    print("\n6. Deployment Options...")
    generate_deployment_architecture()
    print("   ✓ architecture_deployment.png created")
    
    print("\n✅ All diagrams generated successfully!")
    print("📁 Check the current directory for PNG files.")
