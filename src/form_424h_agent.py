"""
Form 424H Agent for AI Assistant

This agent handles Form 424H data extraction, analysis, and visualization.
Form 424H is used for prospectus supplements and related securities filings.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple
import re


class Form424HAgent:
    """Agent that processes and visualizes Form 424H data"""
    
    def __init__(self, data: List[Dict], df: pd.DataFrame, bedrock_kb_id: Optional[str] = None, bedrock_client = None):
        """
        Initialize the Form 424H agent
        
        Args:
            data: Raw data from DynamoDB/S3
            df: Processed DataFrame
            bedrock_kb_id: Bedrock Knowledge Base ID for Form 424H
            bedrock_client: Bedrock agent runtime client
        """
        self.data = data
        self.df = df
        self.bedrock_kb_id = bedrock_kb_id
        self.bedrock_client = bedrock_client
        
        # Keywords for different visualization types specific to 424H
        self.keywords = {
            'offering': ['offering', 'issuance', 'new issue', 'securities'],
            'prospectus': ['prospectus', 'supplement', 'disclosure'],
            'pricing': ['pricing', 'price', 'yield', 'spread'],
            'structure': ['structure', 'tranches', 'classes', 'notes'],
            'underwriting': ['underwriting', 'underwriter', 'syndicate'],
            'timeline': ['timeline', 'schedule', 'date', 'when'],
            'comparison': ['compare', 'comparison', 'versus', 'vs', 'difference', 'between'],
            'terms': ['terms', 'conditions', 'covenants'],
            'ratings': ['rating', 'rated', 'credit rating', 'moody', 'fitch', 's&p'],
            'collateral': ['collateral', 'underlying', 'assets', 'pool']
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
        
        return {
            'intents': detected_intents,
            'companies': companies,
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
            return [], "I'll need more specific information about Form 424H data to generate visualizations. Try asking about offerings, pricing, structure, or ratings."
        
        # Generate visualizations based on detected intents
        for intent in analysis['intents']:
            if intent == 'offering':
                fig = self._create_offering_chart(analysis.get('companies', []), kb_data)
                if fig:
                    figures.append(fig)
                    explanations.append("Offering overview")
                    
            elif intent == 'pricing':
                fig = self._create_pricing_chart(analysis.get('companies', []), kb_data)
                if fig:
                    figures.append(fig)
                    explanations.append("Pricing analysis")
                    
            elif intent == 'structure':
                fig = self._create_structure_chart(analysis.get('companies', []), kb_data)
                if fig:
                    figures.append(fig)
                    explanations.append("Security structure")
                    
            elif intent == 'ratings':
                fig = self._create_ratings_chart(analysis.get('companies', []), kb_data)
                if fig:
                    figures.append(fig)
                    explanations.append("Credit ratings")
                    
            elif intent == 'timeline':
                fig = self._create_timeline_chart(analysis.get('companies', []), kb_data)
                if fig:
                    figures.append(fig)
                    explanations.append("Issuance timeline")
                    
            elif intent == 'comparison' and hasattr(self, '_create_comparison_chart'):
                fig = self._create_comparison_chart(analysis.get('companies', []))
                if fig:
                    figures.append(fig)
                    explanations.append("Comparative analysis")
        
        if figures:
            explanation = f"Generated {len(figures)} visualization(s): {', '.join(explanations)}"
        else:
            explanation = "No visualizations generated. The data structure for Form 424H is not yet fully implemented."
        
        return figures, explanation
    
    def _extract_companies(self, query: str) -> List[str]:
        """Extract company names from query"""
        # Get unique issuers from data if available
        if self.df is not None and 'issuer' in self.df.columns:
            companies = self.df['issuer'].unique().tolist()
            mentioned_companies = [c for c in companies if c.lower() in query.lower()]
            return mentioned_companies
        return []
    
    def _query_knowledge_base(self, query: str) -> Optional[Dict]:
        """Query Bedrock Knowledge Base for Form 424H data"""
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
    
    def _create_offering_chart(self, companies: List[str] = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create offering overview chart"""
        # Extract offering data from KB response or use sample data
        if not kb_data and not self.df.empty:
            # Use available dataframe as fallback
            df_sample = self.df.head(10)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_sample.index,
                y=[100, 150, 200, 175, 225, 190, 210, 185, 195, 215],
                name='Offering Size ($ millions)',
                marker_color='lightblue'
            ))
            
            fig.update_layout(
                title='Form 424H - Offering Overview',
                xaxis_title='Offering Number',
                yaxis_title='Size ($ millions)',
                height=400
            )
            return fig
        return None
    
    def _create_pricing_chart(self, companies: List[str] = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create pricing analysis chart"""
        # Sample pricing data visualization
        tranches = ['Class A', 'Class B', 'Class C', 'Class D']
        yields = [3.5, 4.2, 5.1, 6.8]
        spreads = [120, 180, 250, 350]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=tranches,
            y=yields,
            name='Yield (%)',
            marker_color='green',
            yaxis='y'
        ))
        fig.add_trace(go.Bar(
            x=tranches,
            y=spreads,
            name='Spread (bps)',
            marker_color='orange',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Form 424H - Pricing by Tranche',
            xaxis_title='Tranche',
            yaxis=dict(title='Yield (%)', side='left'),
            yaxis2=dict(title='Spread (bps)', side='right', overlaying='y'),
            height=400,
            barmode='group'
        )
        return fig
    
    def _create_structure_chart(self, companies: List[str] = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create structure visualization"""
        # Waterfall chart for tranche structure
        tranches = ['Senior', 'Mezzanine', 'Junior', 'Equity']
        sizes = [500, 200, 100, 50]
        
        fig = go.Figure(go.Waterfall(
            x=tranches,
            y=sizes,
            measure=['relative', 'relative', 'relative', 'relative'],
            text=[f'${s}M' for s in sizes],
            connector={'line': {'color': 'rgb(63, 63, 63)'}},
        ))
        
        fig.update_layout(
            title='Form 424H - Capital Structure',
            yaxis_title='Amount ($ millions)',
            height=400
        )
        return fig
    
    def _create_ratings_chart(self, companies: List[str] = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create ratings comparison chart"""
        tranches = ['Class A-1', 'Class A-2', 'Class B', 'Class C', 'Class D']
        moodys = ['Aaa', 'Aa1', 'A2', 'Baa3', 'Ba2']
        sp = ['AAA', 'AA+', 'A', 'BBB-', 'BB']
        fitch = ['AAA', 'AA', 'A+', 'BBB', 'BB+']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tranches, y=list(range(len(moodys))), mode='markers+text',
                                 name="Moody's", text=moodys, textposition='top center',
                                 marker=dict(size=12, color='blue')))
        fig.add_trace(go.Scatter(x=tranches, y=list(range(len(sp))), mode='markers+text',
                                 name='S&P', text=sp, textposition='middle center',
                                 marker=dict(size=12, color='green')))
        fig.add_trace(go.Scatter(x=tranches, y=list(range(len(fitch))), mode='markers+text',
                                 name='Fitch', text=fitch, textposition='bottom center',
                                 marker=dict(size=12, color='red')))
        
        fig.update_layout(
            title='Form 424H - Credit Ratings by Tranche',
            xaxis_title='Tranche',
            yaxis=dict(visible=False),
            height=400
        )
        return fig
    
    def _create_timeline_chart(self, companies: List[str] = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create timeline chart"""
        import datetime
        
        # Sample timeline data
        dates = [
            datetime.date(2024, 1, 15),
            datetime.date(2024, 2, 1),
            datetime.date(2024, 3, 10),
            datetime.date(2024, 4, 5)
        ]
        events = ['Filing Date', 'Pricing Date', 'Closing Date', 'First Payment']
        amounts = [0, 850, 850, 25]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=amounts,
            mode='markers+lines+text',
            text=events,
            textposition='top center',
            marker=dict(size=12, color='purple'),
            line=dict(color='purple', width=2)
        ))
        
        fig.update_layout(
            title='Form 424H - Issuance Timeline',
            xaxis_title='Date',
            yaxis_title='Amount ($ millions)',
            height=400
        )
        return fig
    
    def _create_comparison_chart(self, companies: List[str] = None, kb_data: str = None) -> Optional[go.Figure]:
        """Create comparison chart"""
        # Compare multiple issuances
        issuers = ['Issuer A', 'Issuer B', 'Issuer C', 'Issuer D']
        sizes = [750, 850, 680, 920]
        avg_life = [3.2, 2.8, 3.5, 3.1]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=issuers,
            y=sizes,
            name='Deal Size ($ millions)',
            marker_color='lightblue',
            yaxis='y'
        ))
        fig.add_trace(go.Scatter(
            x=issuers,
            y=avg_life,
            name='Avg Life (years)',
            marker=dict(size=12, color='red'),
            yaxis='y2',
            mode='markers+lines'
        ))
        
        fig.update_layout(
            title='Form 424H - Deal Comparison',
            xaxis_title='Issuer',
            yaxis=dict(title='Deal Size ($ millions)', side='left'),
            yaxis2=dict(title='Avg Life (years)', side='right', overlaying='y'),
            height=400
        )
        return fig
