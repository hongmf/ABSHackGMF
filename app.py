"""
Streamlit Dashboard for Auto Loan Metrics Analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from decimal import Decimal
from dotenv import load_dotenv
import boto3
import json
import uuid
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dynamodb_operations import DynamoDBHandler
from langgraph_orchestrator import LangGraphOrchestrator

# Load environment variables
load_dotenv()

# S3 Configuration
S3_BUCKET_ABS_EE = os.getenv('S3_BUCKET_NAME1', 'abs-ee')
S3_BUCKET_424H = os.getenv('S3_BUCKET_NAME2', '424h-prospectus')
S3_BUCKET_10D = os.getenv('S3_BUCKET_NAME3', '10-d')

# Bedrock Configuration
KNOWLEDGE_BASE_ID = os.getenv('BEDROCK_KB_ID', 'A7EOGV6BHS')
KNOWLEDGE_BASE_ID_424H = os.getenv('BEDROCK_KB_ID_424H', '83TDL5E9HV')
KNOWLEDGE_BASE_ID_10D = os.getenv('BEDROCK_KB_ID_10D', 'O2KBJHZUJO')
BEDROCK_REGION = os.getenv('BEDROCK_REGION', 'us-west-2')
MODEL_ARN = os.getenv('BEDROCK_MODEL_ARN', 'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0')

# Page configuration
st.set_page_config(
    page_title="Auto Loan Metrics Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load all data from DynamoDB"""
    try:
        db_handler = DynamoDBHandler()
        all_data = db_handler.scan_all_metrics()
        
        # Convert Decimal to float for JSON serialization
        def convert_decimals(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            return obj
        
        converted_data = [convert_decimals(item) for item in all_data]
        return converted_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return []


@st.cache_data(ttl=300)
def load_multi_source_data():
    """Load data from multiple sources for agent orchestrator"""
    data_sources = {}
    
    # Load ABS-EE data (current implementation)
    try:
        db_handler = DynamoDBHandler()
        abs_ee_data = db_handler.scan_all_metrics()
        
        def convert_decimals(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            return obj
        
        converted_data = [convert_decimals(item) for item in abs_ee_data]
        df = convert_to_dataframe(converted_data)
        
        data_sources['abs-ee'] = {
            'data': converted_data,
            'df': df
        }
    except Exception as e:
        st.warning(f"Could not load ABS-EE data: {e}")
    
    # TODO: Load 424H data when available
    # data_sources['424h'] = {'data': [...], 'df': pd.DataFrame(...)}
    
    # TODO: Load 10-D data when available
    # data_sources['10-d'] = {'data': [...], 'df': pd.DataFrame(...)}
    
    return data_sources


def convert_to_dataframe(data):
    """Convert DynamoDB data to pandas DataFrame"""
    if not data:
        return pd.DataFrame()
    
    # Flatten nested structures for main dataframe
    df_data = []
    for item in data:
        row = {
            'company_name': item.get('company_name', ''),
            'reporting_period': item.get('reporting_period', ''),
            'total_loans': item.get('total_loans', 0),
            'total_pool_balance': item.get('total_pool_balance', 0),
            'average_fico_score': item.get('average_fico_score', 0),
            'delinquency_30_plus_rate': item.get('delinquency_30_plus_rate', 0),
            'delinquency_60_plus_rate': item.get('delinquency_60_plus_rate', 0),
            'delinquency_90_plus_rate': item.get('delinquency_90_plus_rate', 0),
            'loss_severity_percentage': item.get('loss_severity_percentage', 0),
            'prepayment_speed_cpr': item.get('prepayment_speed_cpr', 0),
            'prepayment_speed_abs': item.get('prepayment_speed_abs', 0),
            'average_loan_amount': item.get('average_loan_amount', 0),
            'average_remaining_term': item.get('average_remaining_term', 0),
            'weighted_avg_interest_rate': item.get('weighted_avg_interest_rate', 0),
            'new_vehicle_percentage': item.get('new_vehicle_percentage', 0),
            'used_vehicle_percentage': item.get('used_vehicle_percentage', 0),
            'repossession_rate': item.get('repossession_rate', 0),
            'last_updated': item.get('last_updated', '')
        }
        df_data.append(row)
    
    return pd.DataFrame(df_data)


def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<h1 class="main-header">🚗 Auto Loan Metrics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading data from DynamoDB..."):
        data = load_data()
    
    if not data:
        st.warning("No data found in DynamoDB. Please process some SEC filings first.")
        st.info("Run: `python src/pipeline.py --s3-bucket abs-ee` to process files")
        return
    
    # Convert to DataFrame
    df = convert_to_dataframe(data)
    
    # Sidebar filters
    st.sidebar.header("📊 Filters")
    
    # Company filter
    companies = sorted(df['company_name'].unique().tolist())
    selected_companies = st.sidebar.multiselect(
        "Select Companies",
        companies,
        default=companies if len(companies) <= 2 else companies[:2]
    )
    
    # Period filter
    periods = sorted(df['reporting_period'].unique().tolist())
    selected_periods = st.sidebar.multiselect(
        "Select Reporting Periods",
        periods,
        default=periods
    )
    
    # Filter data
    if selected_companies:
        df_filtered = df[df['company_name'].isin(selected_companies)]
    else:
        df_filtered = df
    
    if selected_periods:
        df_filtered = df_filtered[df_filtered['reporting_period'].isin(selected_periods)]
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Dashboard", 
        "🔍 Company Comparison", 
        "🗺️ Geographic Analysis",
        "📊 Detailed Metrics",
        "💬 AI Assistant"
    ])
    
    # Tab 1: Dashboard
    with tab1:
        st.header("Portfolio Overview")
        
        if df_filtered.empty:
            st.warning("No data matches the selected filters.")
        else:
            # Key metrics cards
            col1, col2, col3, col4 = st.columns(4)
            
            total_loans = df_filtered['total_loans'].sum()
            total_balance = df_filtered['total_pool_balance'].sum()
            avg_fico = (df_filtered['average_fico_score'] * df_filtered['total_pool_balance']).sum() / df_filtered['total_pool_balance'].sum() if df_filtered['total_pool_balance'].sum() > 0 else 0
            avg_delinquency = df_filtered['delinquency_30_plus_rate'].mean()
            
            with col1:
                st.metric("Total Loans", f"{total_loans:,.0f}")
            with col2:
                st.metric("Total Pool Balance", f"${total_balance:,.0f}")
            with col3:
                st.metric("Weighted Avg FICO", f"{avg_fico:.1f}")
            with col4:
                st.metric("Avg Delinquency 30+", f"{avg_delinquency:.2f}%")
            
            st.markdown("---")
            
            # Charts row 1
            col1, col2 = st.columns(2)
            
            with col1:
                # Portfolio balance by company
                fig = px.bar(
                    df_filtered.groupby('company_name')['total_pool_balance'].sum().reset_index(),
                    x='company_name',
                    y='total_pool_balance',
                    title='Total Pool Balance by Company',
                    labels={'total_pool_balance': 'Balance ($)', 'company_name': 'Company'},
                    color='company_name'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # FICO scores comparison
                fig = px.bar(
                    df_filtered,
                    x='company_name',
                    y='average_fico_score',
                    color='reporting_period',
                    title='Average FICO Score by Company',
                    labels={'average_fico_score': 'FICO Score', 'company_name': 'Company'},
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Charts row 2
            col1, col2 = st.columns(2)
            
            with col1:
                # Delinquency rates
                fig = go.Figure()
                for company in df_filtered['company_name'].unique():
                    company_data = df_filtered[df_filtered['company_name'] == company]
                    if not company_data.empty:
                        fig.add_trace(go.Bar(
                            name=f'{company} - 30+',
                            x=[company],
                            y=[company_data['delinquency_30_plus_rate'].iloc[0]],
                            marker_color='orange'
                        ))
                        fig.add_trace(go.Bar(
                            name=f'{company} - 60+',
                            x=[company],
                            y=[company_data['delinquency_60_plus_rate'].iloc[0]],
                            marker_color='red'
                        ))
                        fig.add_trace(go.Bar(
                            name=f'{company} - 90+',
                            x=[company],
                            y=[company_data['delinquency_90_plus_rate'].iloc[0]],
                            marker_color='darkred'
                        ))
                
                fig.update_layout(
                    title='Delinquency Rates by Company',
                    xaxis_title='Company',
                    yaxis_title='Delinquency Rate (%)',
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Vehicle mix
                fig = go.Figure()
                for company in df_filtered['company_name'].unique():
                    company_data = df_filtered[df_filtered['company_name'] == company]
                    if not company_data.empty:
                        latest = company_data.iloc[0]
                        fig.add_trace(go.Bar(
                            name=company,
                            x=['New Vehicles', 'Used Vehicles'],
                            y=[latest['new_vehicle_percentage'], latest['used_vehicle_percentage']],
                            text=[f"{latest['new_vehicle_percentage']:.1f}%", 
                                  f"{latest['used_vehicle_percentage']:.1f}%"],
                            textposition='auto'
                        ))
                
                fig.update_layout(
                    title='Vehicle Mix (New vs Used)',
                    xaxis_title='Vehicle Type',
                    yaxis_title='Percentage (%)',
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Loan term distribution
            st.subheader("Loan Term Distribution")
            for company in df_filtered['company_name'].unique():
                company_data = [item for item in data if item.get('company_name') == company]
                if company_data:
                    latest = max(company_data, key=lambda x: x.get('reporting_period', ''))
                    term_dist = latest.get('loan_term_distribution', {})
                    
                    if term_dist:
                        term_df = pd.DataFrame([
                            {'Term Range': term, 'Percentage': pct}
                            for term, pct in term_dist.items()
                        ])
                        
                        fig = px.bar(
                            term_df,
                            x='Term Range',
                            y='Percentage',
                            title=f'Loan Term Distribution - {company}',
                            color='Percentage',
                            color_continuous_scale='Greens'
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Company Comparison
    with tab2:
        st.header("Company Comparison")
        
        if len(selected_companies) < 2:
            st.info("Select at least 2 companies in the sidebar to compare.")
        else:
            comparison_data = []
            for company in selected_companies:
                company_df = df_filtered[df_filtered['company_name'] == company]
                if not company_df.empty:
                    latest = company_df.sort_values('reporting_period').iloc[-1]
                    comparison_data.append({
                        'Company': company,
                        'Total Loans': latest['total_loans'],
                        'Pool Balance ($)': latest['total_pool_balance'],
                        'Avg FICO': latest['average_fico_score'],
                        'Delinquency 30+ (%)': latest['delinquency_30_plus_rate'],
                        'Delinquency 60+ (%)': latest['delinquency_60_plus_rate'],
                        'Delinquency 90+ (%)': latest['delinquency_90_plus_rate'],
                        'Loss Severity (%)': latest['loss_severity_percentage'],
                        'Avg Loan Amount ($)': latest['average_loan_amount'],
                        'Interest Rate (%)': latest['weighted_avg_interest_rate'],
                        'New Vehicles (%)': latest['new_vehicle_percentage'],
                        'Repossession Rate (%)': latest['repossession_rate']
                    })
            
            if comparison_data:
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True)
                
                # Visual comparison
                metrics_to_compare = ['Avg FICO', 'Delinquency 30+ (%)', 'Pool Balance ($)', 'Interest Rate (%)']
                
                for metric in metrics_to_compare:
                    fig = px.bar(
                        comparison_df,
                        x='Company',
                        y=metric,
                        title=f'{metric} Comparison',
                        color='Company'
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: Geographic Analysis
    with tab3:
        st.header("Geographic Distribution")
        
        if not selected_companies:
            st.info("Select a company in the sidebar to view geographic distribution.")
        else:
            for company in selected_companies:
                company_data = [item for item in data if item.get('company_name') == company]
                if company_data:
                    latest = max(company_data, key=lambda x: x.get('reporting_period', ''))
                    geo_data = latest.get('geographic_concentration', {})
                    
                    if geo_data:
                        st.subheader(f"{company} - Geographic Concentration")
                        
                        # Convert to DataFrame
                        geo_df = pd.DataFrame([
                            {'State': state, 'Percentage': pct}
                            for state, pct in geo_data.items()
                        ]).sort_values('Percentage', ascending=False)
                        
                        # Top 10 states
                        top_states = geo_df.head(10)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            fig = px.bar(
                                top_states,
                                x='State',
                                y='Percentage',
                                title=f'Top 10 States - {company}',
                                color='Percentage',
                                color_continuous_scale='Blues'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            fig = px.pie(
                                top_states,
                                values='Percentage',
                                names='State',
                                title=f'Top 10 States Distribution - {company}'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Full table
                        st.dataframe(geo_df, use_container_width=True)
    
    # Tab 4: Detailed Metrics
    with tab4:
        st.header("Detailed Metrics Table")
        
        if df_filtered.empty:
            st.warning("No data matches the selected filters.")
        else:
            # Display full dataframe
            st.dataframe(df_filtered, use_container_width=True)
            
            # Download button
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="auto_loan_metrics.csv",
                mime="text/csv"
            )
    
    # Tab 5: AI Assistant - Bedrock Knowledge Base Integration
    with tab5:
        st.header("🤖 AI Assistant - Powered by AWS Bedrock")
        st.info("Ask questions about auto loan metrics. Answers are generated from the Bedrock Knowledge Base.")
        
        # Initialize session state for conversation history
        if 'kb_messages' not in st.session_state:
            st.session_state.kb_messages = []
        if 'kb_session_id' not in st.session_state:
            st.session_state.kb_session_id = str(uuid.uuid4())
        
        # Display conversation history
        for message in st.session_state.kb_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("sources"):
                    with st.expander("📚 View Sources"):
                        for i, source in enumerate(message["sources"], 1):
                            st.caption(f"{i}. {source}")
                
                # Display visualization count for assistant messages
                if message["role"] == "assistant" and message.get("visualizations", 0) > 0:
                    st.caption(f"📊 {message['visualizations']} visualization(s) generated")
        
        # Chat input
        if question := st.chat_input("Ask about auto loan metrics, SEC filings, or financial analysis..."):
            # Display user message
            st.session_state.kb_messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            
            # Get AI response from Bedrock Knowledge Base
            with st.chat_message("assistant"):
                with st.spinner("🔍 Searching knowledge base..."):
                    try:
                        # Initialize Bedrock client
                        bedrock_agent_runtime = boto3.client(
                            'bedrock-agent-runtime', 
                            region_name=BEDROCK_REGION
                        )
                        
                        # Query Knowledge Base with RetrieveAndGenerate (without sessionId to avoid validation issues)
                        response = bedrock_agent_runtime.retrieve_and_generate(
                            input={
                                'text': question
                            },
                            retrieveAndGenerateConfiguration={
                                'type': 'KNOWLEDGE_BASE',
                                'knowledgeBaseConfiguration': {
                                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                                    'modelArn': MODEL_ARN,
                                    'retrievalConfiguration': {
                                        'vectorSearchConfiguration': {
                                            'numberOfResults': 5
                                        }
                                    },
                                    'generationConfiguration': {
                                        'promptTemplate': {
                                            'textPromptTemplate': '''You are an expert financial analyst specializing in auto loan portfolios and SEC filings. 

Use the following context from the knowledge base to answer the question. Be specific with numbers, cite data accurately, and provide clear explanations.

Context: $search_results$

Question: $query$

Provide a detailed, professional answer:'''
                                        },
                                        'inferenceConfig': {
                                            'textInferenceConfig': {
                                                'temperature': 0.7,
                                                'maxTokens': 2000,
                                                'topP': 0.9
                                            }
                                        }
                                    }
                                }
                            }
                        )
                        
                        # Extract answer
                        answer = response['output']['text']
                        
                        # Extract sources/citations
                        sources = []
                        citations = response.get('citations', [])
                        for citation in citations:
                            for reference in citation.get('retrievedReferences', []):
                                location = reference.get('location', {})
                                s3_location = location.get('s3Location', {})
                                uri = s3_location.get('uri', '')
                                if uri:
                                    # Clean up S3 URI for display
                                    source_name = uri.split('/')[-1] if '/' in uri else uri
                                    sources.append(source_name)
                        
                        # Remove duplicates
                        sources = list(set(sources))
                        
                        # Display answer
                        st.markdown(answer)
                        
                        # Display sources if available
                        if sources:
                            with st.expander("📚 View Sources"):
                                st.caption("Answer generated from the following sources:")
                                for i, source in enumerate(sources, 1):
                                    st.caption(f"{i}. {source}")
                        
                        # Generate visualizations based on query using LangGraph orchestrator
                        st.markdown("---")
                        st.markdown("### 📊 Related Visualizations")
                        
                        # Load multi-source data for orchestrator
                        data_sources = load_multi_source_data()
                        
                        if data_sources:
                            # Prepare Bedrock KB IDs
                            bedrock_kb_ids = {
                                'abs-ee': KNOWLEDGE_BASE_ID,
                                '424h': KNOWLEDGE_BASE_ID_424H,
                                '10-d': KNOWLEDGE_BASE_ID_10D
                            }
                            
                            # Initialize Bedrock client
                            bedrock_agent_runtime = boto3.client(
                                'bedrock-agent-runtime',
                                region_name=BEDROCK_REGION
                            )
                            
                            orchestrator = LangGraphOrchestrator(
                                data_sources, 
                                bedrock_kb_ids=bedrock_kb_ids,
                                bedrock_client=bedrock_agent_runtime
                            )
                            visualizations, explanation = orchestrator.generate_visualizations(question)
                            
                            if visualizations:
                                st.caption(explanation)
                                for fig in visualizations:
                                    st.plotly_chart(fig, use_container_width=True, key=f"viz_{uuid.uuid4()}")
                            else:
                                st.info(f"💡 {explanation}")
                        else:
                            st.warning("No data sources available for visualization.")
                        
                        # Save to conversation history
                        st.session_state.kb_messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                            "visualizations": len(visualizations)
                        })
                        
                    except Exception as e:
                        error_msg = f"⚠️ Error connecting to Bedrock Knowledge Base: {str(e)}"
                        st.error(error_msg)
                        st.info("Please check:\n- AWS credentials are configured\n- Bedrock permissions are granted\n- Knowledge Base ID is correct")
                        
                        st.session_state.kb_messages.append({
                            "role": "assistant",
                            "content": error_msg,
                            "sources": [],
                            "visualizations": 0
                        })
        
        # Sidebar controls in columns
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.kb_messages = []
                st.session_state.kb_session_id = str(uuid.uuid4())
                st.rerun()
        
        with col2:
            if st.button("ℹ️ KB Info", use_container_width=True):
                st.info(f"""
                **Knowledge Base Configuration:**
                - KB ID: `{KNOWLEDGE_BASE_ID}`
                - Region: `{BEDROCK_REGION}`
                - Model: Claude 3 Sonnet
                """)
        
        with col3:
            if st.button("💡 Examples", use_container_width=True):
                st.markdown("""
                **Try asking:**
                - Show me the portfolio balance by company
                - Compare FICO scores between companies
                - What are the delinquency rates?
                - Show vehicle mix for GM Financial
                - Display geographic distribution
                - Compare interest rates across companies
                """)
        
        # Show sample data context
        if not st.session_state.kb_messages:
            st.markdown("---")
            st.markdown("### 💬 Sample Questions to Get Started")
            st.info("💡 The AI Assistant now generates relevant visualizations automatically based on your questions!")
            
            sample_questions = [
                "Show me the total pool balance by company",
                "Compare FICO scores between GM Financial and Ford Credit",
                "What are the delinquency rates and show me a chart?",
                "Display the geographic distribution of loans",
                "Show vehicle mix (new vs used) for all companies",
                "Compare interest rates across companies with visualization"
            ]
            
            for sq in sample_questions:
                st.markdown(f"- {sq}")


if __name__ == "__main__":
    main()

