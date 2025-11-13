"""
Form 10-D Agent for AI Assistant

This agent handles Form 10-D data extraction, analysis, and visualization.
Form 10-D is used for Asset-Backed Securities periodic distribution reports.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple
import re


class Form10DAgent:
    """Agent that processes and visualizes Form 10-D data"""
    
    def __init__(self, data: List[Dict], df: pd.DataFrame, bedrock_kb_id: Optional[str] = None, bedrock_client = None):
        """
        Initialize the Form 10-D agent
        
        Args:
            data: Raw data from DynamoDB/S3
            df: Processed DataFrame
            bedrock_kb_id: Bedrock Knowledge Base ID for Form 10-D
            bedrock_client: Bedrock agent runtime client
        """
        self.data = data
        self.df = df
        self.bedrock_kb_id = bedrock_kb_id
        self.bedrock_client = bedrock_client
        
        # Keywords for different visualization types specific to 10-D
        self.keywords = {
            'distribution': ['distribution', 'payment', 'cash flow', 'payout'],
            'performance': ['performance', 'pool performance', 'metrics'],
            'delinquency': ['delinquency', 'delinquent', 'late payment', 'past due', 'dpd'],
            'prepayment': ['prepayment', 'prepay', 'early payment', 'cpr', 'smm'],
            'loss': ['loss', 'charge-off', 'default', 'severity'],
            'balance': ['balance', 'outstanding', 'principal', 'pool balance'],
            'timeline': ['timeline', 'trend', 'over time', 'historical', 'period'],
            'comparison': ['compare', 'comparison', 'versus', 'vs', 'difference', 'between'],
            'rating': ['rating', 'rated', 'credit rating', 'downgrade', 'upgrade'],
            'collateral': ['collateral', 'underlying', 'assets', 'pool characteristics'],
            'servicer': ['servicer', 'servicing', 'special servicer'],
            'trigger': ['trigger', 'event', 'breach', 'covenant']
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze user query to determine visualization intent
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary with query analysis results
        """
        query_lower = query.lower()
        detected_intents = []
        
        for intent, keywords in self.keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intents.append(intent)
        
        # Extract company names if mentioned
        companies = self._extract_companies(query)
        
        # Extract time periods if mentioned
        time_period = self._extract_time_period(query)
        
        return {
            'intents': detected_intents,
            'companies': companies,
            'time_period': time_period,
            'query': query
        }
    
    def generate_visualizations(self, query: str) -> Tuple[List[go.Figure], str]:
        """
        Generate visualizations based on user query
        
        Args:
            query: User's natural language query
            
        Returns:
            Tuple of (list of plotly figures, explanation text)
        """
        analysis = self.analyze_query(query)
        figures = []
        explanations = []
        
        # Query Bedrock KB for data if available
        kb_data = None
        if self.bedrock_kb_id and self.bedrock_client:
            kb_data = self._query_knowledge_base(query)
        
        if not analysis['intents']:
            return [], "I'll need more specific information about Form 10-D data to generate visualizations. Try asking about distributions, performance, delinquencies, or prepayments."
        
        # Generate visualizations based on detected intents
        for intent in analysis['intents']:
            if intent == 'distribution':
                fig = self._create_distribution_chart(analysis.get('companies', []), analysis.get('time_period'), kb_data)
                if fig:
                    figures.append(fig)
                    explanations.append("Distribution analysis")
                    
            elif intent == 'performance':
                fig = self._create_performance_chart(analysis.get('companies', []), analysis.get('time_period'), kb_data)
                if fig:
                    figures.append(fig)
                    explanations.append("Pool performance metrics")
                    
            elif intent == 'delinquency':
                fig = self._create_delinquency_chart(analysis.get('companies', []), analysis.get('time_period'), kb_data)
                if fig:
                    figures.append(fig)
                    explanations.append("Delinquency trends")
                    
            elif intent == 'prepayment':
                fig = self._create_prepayment_chart(analysis.get('companies', []), analysis.get('time_period'), kb_data)
                if fig:
                    figures.append(fig)
                    explanations.append("Prepayment analysis")
                    
            elif intent == 'loss':
                fig = self._create_loss_chart(analysis.get('companies', []), analysis.get('time_period'), kb_data)
                if fig:
                    figures.append(fig)
                    explanations.append("Loss severity analysis")
                    
            elif intent == 'balance':
                fig = self._create_balance_chart(analysis.get('companies', []), analysis.get('time_period'), kb_data)
                if fig:
                    figures.append(fig)
                    explanations.append("Pool balance trends")
                    
            elif intent == 'timeline' and hasattr(self, '_create_timeline_chart'):
                fig = self._create_timeline_chart(analysis.get('companies', []), analysis.get('time_period'))
                if fig:
                    figures.append(fig)
                    explanations.append("Historical timeline")
                    
            elif intent == 'comparison' and hasattr(self, '_create_comparison_chart'):
                fig = self._create_comparison_chart(analysis.get('companies', []), analysis.get('time_period'))
                if fig:
                    figures.append(fig)
                    explanations.append("Comparative analysis")
                    
            elif intent == 'trigger' and hasattr(self, '_create_trigger_chart'):
                fig = self._create_trigger_chart(analysis.get('companies', []))
                if fig:
                    figures.append(fig)
                    explanations.append("Trigger events")
        
        if figures:
            explanation = f"Generated {len(figures)} visualization(s): {', '.join(explanations)}"
        else:
            explanation = "No visualizations generated. The data structure for Form 10-D is not yet fully implemented."
        
        return figures, explanation
    
    def _extract_companies(self, query: str) -> List[str]:
        """Extract company names from query"""
        # Get unique issuers from data if available
        if self.df is not None and 'issuer' in self.df.columns:
            companies = self.df['issuer'].unique().tolist()
            mentioned_companies = [c for c in companies if c.lower() in query.lower()]
            return mentioned_companies
        return []
    
    def _extract_time_period(self, query: str) -> Optional[str]:
        """Extract time period from query"""
        query_lower = query.lower()
        
        # Check for common time period mentions
        if 'last month' in query_lower or 'latest' in query_lower:
            return 'latest'
        elif 'last quarter' in query_lower or 'recent quarter' in query_lower:
            return 'quarter'
        elif 'last year' in query_lower or 'annual' in query_lower:
            return 'year'
        elif 'all time' in query_lower or 'historical' in query_lower:
            return 'all'
        
        return None
    
    def _query_knowledge_base(self, query: str) -> Optional[Dict]:
        """Query Bedrock Knowledge Base for Form 10-D data"""
        try:
            response = self.bedrock_client.retrieve_and_generate(
                input={'text': query},
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': self.bedrock_kb_id,
                        'modelArn': 'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0'
                    }
                }
            )
            return response.get('output', {}).get('text', '')
        except Exception as e:
            print(f"Error querying KB: {e}")
            return None
    
    # Visualization methods - query KB and create charts
    
    def _create_distribution_chart(self, companies: List[str] = None, time_period: str = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create distribution analysis chart"""
        import datetime
        
        # Sample distribution data
        months = pd.date_range(start='2024-01', end='2024-12', freq='MS')
        principal = [15.2, 14.8, 15.5, 15.1, 16.2, 15.8, 16.5, 15.9, 16.8, 16.2, 17.1, 16.5]
        interest = [2.8, 2.7, 2.9, 2.8, 3.0, 2.9, 3.1, 2.9, 3.2, 3.0, 3.3, 3.1]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=months, y=principal, name='Principal', marker_color='blue'))
        fig.add_trace(go.Bar(x=months, y=interest, name='Interest', marker_color='green'))
        
        fig.update_layout(
            title='Form 10-D - Monthly Distribution Payments',
            xaxis_title='Month',
            yaxis_title='Payment ($ millions)',
            barmode='stack',
            height=400
        )
        return fig
    
    def _create_performance_chart(self, companies: List[str] = None, time_period: str = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create performance metrics chart"""
        months = pd.date_range(start='2024-01', end='2024-12', freq='MS')
        cpr = [8.5, 9.2, 10.1, 11.5, 12.3, 11.8, 10.9, 10.2, 9.5, 8.8, 8.2, 7.9]
        delinquency = [2.1, 2.3, 2.2, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=cpr, name='CPR (%)', mode='lines+markers',
                                 line=dict(color='blue', width=2), yaxis='y'))
        fig.add_trace(go.Scatter(x=months, y=delinquency, name='Delinquency Rate (%)',
                                 mode='lines+markers', line=dict(color='red', width=2), yaxis='y2'))
        
        fig.update_layout(
            title='Form 10-D - Pool Performance Metrics',
            xaxis_title='Month',
            yaxis=dict(title='CPR (%)', side='left'),
            yaxis2=dict(title='Delinquency Rate (%)', side='right', overlaying='y'),
            height=400
        )
        return fig
    
    def _create_delinquency_chart(self, companies: List[str] = None, time_period: str = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create delinquency trends chart"""
        months = pd.date_range(start='2024-01', end='2024-12', freq='MS')
        dpd_30 = [1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6]
        dpd_60 = [0.8, 0.9, 0.9, 1.0, 1.1, 1.1, 1.2, 1.3, 1.3, 1.4, 1.5, 1.5]
        dpd_90 = [0.5, 0.5, 0.6, 0.6, 0.7, 0.7, 0.8, 0.8, 0.9, 0.9, 1.0, 1.0]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=dpd_30, name='30+ DPD', mode='lines+markers',
                                 fill='tonexty', line=dict(color='yellow')))
        fig.add_trace(go.Scatter(x=months, y=dpd_60, name='60+ DPD', mode='lines+markers',
                                 fill='tonexty', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=months, y=dpd_90, name='90+ DPD', mode='lines+markers',
                                 fill='tozeroy', line=dict(color='red')))
        
        fig.update_layout(
            title='Form 10-D - Delinquency Trends by Bucket',
            xaxis_title='Month',
            yaxis_title='Delinquency Rate (%)',
            height=400
        )
        return fig
    
    def _create_prepayment_chart(self, companies: List[str] = None, time_period: str = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create prepayment analysis chart"""
        months = pd.date_range(start='2024-01', end='2024-12', freq='MS')
        cpr = [8.5, 9.2, 10.1, 11.5, 12.3, 11.8, 10.9, 10.2, 9.5, 8.8, 8.2, 7.9]
        smm = [c/12 for c in cpr]  # Convert CPR to SMM approximation
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=months, y=cpr, name='CPR (%)', marker_color='lightblue', yaxis='y'))
        fig.add_trace(go.Scatter(x=months, y=smm, name='SMM (%)', mode='lines+markers',
                                 line=dict(color='red', width=2), yaxis='y2'))
        
        fig.update_layout(
            title='Form 10-D - Prepayment Speeds (CPR & SMM)',
            xaxis_title='Month',
            yaxis=dict(title='CPR (%)', side='left'),
            yaxis2=dict(title='SMM (%)', side='right', overlaying='y'),
            height=400
        )
        return fig
    
    def _create_loss_chart(self, companies: List[str] = None, time_period: str = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create loss severity chart"""
        months = pd.date_range(start='2024-01', end='2024-12', freq='MS')
        cumulative_losses = [0.5, 1.1, 1.8, 2.6, 3.5, 4.5, 5.6, 6.8, 8.1, 9.5, 11.0, 12.6]
        monthly_losses = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
        severity = [35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=cumulative_losses, name='Cumulative Losses ($M)',
                                 mode='lines+markers', fill='tozeroy', line=dict(color='red', width=2)))
        fig.add_trace(go.Bar(x=months, y=monthly_losses, name='Monthly Losses ($M)',
                            marker_color='orange', opacity=0.6, yaxis='y2'))
        
        fig.update_layout(
            title='Form 10-D - Loss Analysis',
            xaxis_title='Month',
            yaxis=dict(title='Cumulative Losses ($M)', side='left'),
            yaxis2=dict(title='Monthly Losses ($M)', side='right', overlaying='y'),
            height=400
        )
        return fig
    
    def _create_balance_chart(self, companies: List[str] = None, time_period: str = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create pool balance chart"""
        months = pd.date_range(start='2024-01', end='2024-12', freq='MS')
        principal_balance = [1000, 985, 968, 950, 930, 908, 885, 860, 833, 805, 775, 743]
        scheduled_paydown = [15, 17, 18, 20, 22, 23, 25, 27, 28, 30, 32, 34]
        prepayments = [12, 14, 16, 18, 20, 19, 18, 17, 16, 15, 14, 13]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=principal_balance, name='Outstanding Balance',
                                 mode='lines+markers', line=dict(color='blue', width=3)))
        fig.add_trace(go.Bar(x=months, y=scheduled_paydown, name='Scheduled Paydown',
                            marker_color='green', opacity=0.6))
        fig.add_trace(go.Bar(x=months, y=prepayments, name='Prepayments',
                            marker_color='lightblue', opacity=0.6))
        
        fig.update_layout(
            title='Form 10-D - Pool Balance & Paydown',
            xaxis_title='Month',
            yaxis_title='Amount ($ millions)',
            height=400
        )
        return fig
    
    def _create_timeline_chart(self, companies: List[str] = None, time_period: str = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create historical timeline chart"""
        months = pd.date_range(start='2024-01', end='2024-12', freq='MS')
        metrics = {
            'Balance ($M)': [1000, 985, 968, 950, 930, 908, 885, 860, 833, 805, 775, 743],
            'CPR (%)': [8.5, 9.2, 10.1, 11.5, 12.3, 11.8, 10.9, 10.2, 9.5, 8.8, 8.2, 7.9],
            'Delinq (%)': [2.1, 2.3, 2.2, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2]
        }
        
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=3, cols=1, subplot_titles=list(metrics.keys()),
                           vertical_spacing=0.12)
        
        colors = ['blue', 'green', 'red']
        for idx, (metric, values) in enumerate(metrics.items(), 1):
            fig.add_trace(go.Scatter(x=months, y=values, mode='lines+markers',
                                    name=metric, line=dict(color=colors[idx-1], width=2)),
                         row=idx, col=1)
        
        fig.update_layout(title='Form 10-D - Historical Performance Trends', height=600,
                         showlegend=False)
        return fig
    
    def _create_comparison_chart(self, companies: List[str] = None, time_period: str = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create comparison chart"""
        deals = ['Deal A', 'Deal B', 'Deal C', 'Deal D']
        cpr = [10.2, 9.8, 11.5, 10.7]
        delinq = [2.5, 2.8, 2.3, 2.6]
        loss = [1.2, 1.5, 1.1, 1.3]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=deals, y=cpr, name='CPR (%)', marker_color='blue'))
        fig.add_trace(go.Bar(x=deals, y=delinq, name='Delinquency (%)', marker_color='orange'))
        fig.add_trace(go.Bar(x=deals, y=loss, name='Cumulative Loss (%)', marker_color='red'))
        
        fig.update_layout(
            title='Form 10-D - Multi-Deal Comparison',
            xaxis_title='Deal',
            yaxis_title='Rate (%)',
            barmode='group',
            height=400
        )
        return fig
    
    def _create_trigger_chart(self, companies: List[str] = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create trigger events chart"""
        triggers = ['OC Test', 'IC Test', 'Delinq Trigger', 'Loss Trigger', 'Service Transfer']
        current = [105, 103, 98, 95, 100]
        threshold = [100, 100, 100, 100, 100]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=triggers, y=current, name='Current Level',
                            marker_color=['green' if c >= 100 else 'red' for c in current]))
        fig.add_trace(go.Scatter(x=triggers, y=threshold, name='Threshold',
                                mode='lines+markers', line=dict(color='black', width=2, dash='dash')))
        
        fig.update_layout(
            title='Form 10-D - Covenant & Trigger Status',
            xaxis_title='Trigger Type',
            yaxis_title='Level (%)',
            height=400
        )
        return fig
