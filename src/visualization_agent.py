"""
Visualization Agent for AI Assistant

This agent generates visualizations based on user queries by analyzing
intent and selecting appropriate charts from Dashboard, Company Comparison,
Geographic Analysis, and Detailed Metrics tabs.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple
import re


class VisualizationAgent:
    """Agent that generates visualizations based on natural language queries"""
    
    def __init__(self, data: List[Dict], df: pd.DataFrame):
        """
        Initialize the visualization agent
        
        Args:
            data: Raw data from DynamoDB
            df: Processed DataFrame
        """
        self.data = data
        self.df = df
        
        # Keywords for different visualization types
        self.keywords = {
            'portfolio': ['portfolio', 'total', 'overall', 'balance', 'pool'],
            'fico': ['fico', 'credit score', 'credit quality'],
            'delinquency': ['delinquency', 'delinquent', 'late payment', 'past due'],
            'vehicle': ['vehicle', 'new vs used', 'car type', 'auto type'],
            'geographic': ['geography', 'geographic', 'state', 'location', 'region', 'where'],
            'loan_term': ['term', 'loan term', 'maturity', 'duration'],
            'comparison': ['compare', 'comparison', 'versus', 'vs', 'difference', 'between'],
            'interest_rate': ['interest rate', 'rate', 'apr', 'pricing'],
            'loss': ['loss', 'severity', 'charge-off'],
            'repossession': ['repossession', 'repo', 'repossessed']
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze user query to determine visualization intent
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary with visualization type and parameters
        """
        query_lower = query.lower()
        
        # Extract companies mentioned
        companies = [comp for comp in self.df['company_name'].unique() 
                    if comp.lower() in query_lower]
        
        # Determine visualization categories
        categories = []
        for category, keywords in self.keywords.items():
            if any(kw in query_lower for kw in keywords):
                categories.append(category)
        
        # Default to overview if no specific category
        if not categories:
            categories = ['portfolio']
        
        return {
            'categories': categories,
            'companies': companies if companies else list(self.df['company_name'].unique()),
            'query': query
        }
    
    def generate_visualizations(self, query: str) -> List[Tuple[str, Any]]:
        """
        Generate visualizations based on query analysis
        
        Args:
            query: User's natural language query
            
        Returns:
            List of tuples (title, plotly_figure)
        """
        analysis = self.analyze_query(query)
        visualizations = []
        
        # Filter data by mentioned companies
        df_filtered = self.df[self.df['company_name'].isin(analysis['companies'])]
        
        if df_filtered.empty:
            return visualizations
        
        categories = analysis['categories']
        
        # Portfolio/Balance visualizations
        if 'portfolio' in categories:
            viz = self._create_portfolio_balance_chart(df_filtered)
            if viz:
                visualizations.append(viz)
        
        # FICO score visualizations
        if 'fico' in categories:
            viz = self._create_fico_chart(df_filtered)
            if viz:
                visualizations.append(viz)
        
        # Delinquency visualizations
        if 'delinquency' in categories:
            viz = self._create_delinquency_chart(df_filtered)
            if viz:
                visualizations.append(viz)
        
        # Vehicle mix visualizations
        if 'vehicle' in categories:
            viz = self._create_vehicle_mix_chart(df_filtered)
            if viz:
                visualizations.append(viz)
        
        # Geographic visualizations
        if 'geographic' in categories:
            viz = self._create_geographic_chart(analysis['companies'])
            if viz:
                visualizations.append(viz)
        
        # Loan term visualizations
        if 'loan_term' in categories:
            viz = self._create_loan_term_chart(analysis['companies'])
            if viz:
                visualizations.append(viz)
        
        # Comparison visualizations
        if 'comparison' in categories and len(analysis['companies']) >= 2:
            viz = self._create_comparison_table(df_filtered, analysis['companies'])
            if viz:
                visualizations.append(viz)
        
        # Interest rate visualizations
        if 'interest_rate' in categories:
            viz = self._create_interest_rate_chart(df_filtered)
            if viz:
                visualizations.append(viz)
        
        return visualizations
    
    def _create_portfolio_balance_chart(self, df: pd.DataFrame) -> Optional[Tuple[str, Any]]:
        """Create portfolio balance bar chart"""
        if df.empty:
            return None
        
        fig = px.bar(
            df.groupby('company_name')['total_pool_balance'].sum().reset_index(),
            x='company_name',
            y='total_pool_balance',
            title='Total Pool Balance by Company',
            labels={'total_pool_balance': 'Balance ($)', 'company_name': 'Company'},
            color='company_name'
        )
        fig.update_layout(showlegend=False, height=400)
        return ("Total Pool Balance by Company", fig)
    
    def _create_fico_chart(self, df: pd.DataFrame) -> Optional[Tuple[str, Any]]:
        """Create FICO score comparison chart"""
        if df.empty:
            return None
        
        fig = px.bar(
            df,
            x='company_name',
            y='average_fico_score',
            color='reporting_period',
            title='Average FICO Score by Company',
            labels={'average_fico_score': 'FICO Score', 'company_name': 'Company'},
            barmode='group'
        )
        fig.update_layout(height=400)
        return ("Average FICO Score by Company", fig)
    
    def _create_delinquency_chart(self, df: pd.DataFrame) -> Optional[Tuple[str, Any]]:
        """Create delinquency rates chart"""
        if df.empty:
            return None
        
        fig = go.Figure()
        for company in df['company_name'].unique():
            company_data = df[df['company_name'] == company]
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
            barmode='group',
            height=400
        )
        return ("Delinquency Rates by Company", fig)
    
    def _create_vehicle_mix_chart(self, df: pd.DataFrame) -> Optional[Tuple[str, Any]]:
        """Create vehicle mix chart"""
        if df.empty:
            return None
        
        fig = go.Figure()
        for company in df['company_name'].unique():
            company_data = df[df['company_name'] == company]
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
            barmode='group',
            height=400
        )
        return ("Vehicle Mix (New vs Used)", fig)
    
    def _create_geographic_chart(self, companies: List[str]) -> Optional[Tuple[str, Any]]:
        """Create geographic distribution chart"""
        if not companies:
            return None
        
        for company in companies:
            company_data = [item for item in self.data if item.get('company_name') == company]
            if company_data:
                latest = max(company_data, key=lambda x: x.get('reporting_period', ''))
                geo_data = latest.get('geographic_concentration', {})
                
                if geo_data:
                    geo_df = pd.DataFrame([
                        {'State': state, 'Percentage': pct}
                        for state, pct in geo_data.items()
                    ]).sort_values('Percentage', ascending=False).head(10)
                    
                    fig = px.bar(
                        geo_df,
                        x='State',
                        y='Percentage',
                        title=f'Top 10 States - {company}',
                        color='Percentage',
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(height=400)
                    return (f"Top 10 States - {company}", fig)
        
        return None
    
    def _create_loan_term_chart(self, companies: List[str]) -> Optional[Tuple[str, Any]]:
        """Create loan term distribution chart"""
        if not companies:
            return None
        
        for company in companies:
            company_data = [item for item in self.data if item.get('company_name') == company]
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
                    fig.update_layout(height=400)
                    return (f"Loan Term Distribution - {company}", fig)
        
        return None
    
    def _create_comparison_table(self, df: pd.DataFrame, companies: List[str]) -> Optional[Tuple[str, Any]]:
        """Create comparison table as a plotly table"""
        if len(companies) < 2 or df.empty:
            return None
        
        comparison_data = []
        for company in companies:
            company_df = df[df['company_name'] == company]
            if not company_df.empty:
                latest = company_df.sort_values('reporting_period').iloc[-1]
                comparison_data.append({
                    'Company': company,
                    'Total Loans': f"{latest['total_loans']:,.0f}",
                    'Pool Balance': f"${latest['total_pool_balance']:,.0f}",
                    'Avg FICO': f"{latest['average_fico_score']:.1f}",
                    'Delinq 30+': f"{latest['delinquency_30_plus_rate']:.2f}%",
                    'Delinq 60+': f"{latest['delinquency_60_plus_rate']:.2f}%",
                    'Delinq 90+': f"{latest['delinquency_90_plus_rate']:.2f}%",
                    'Avg Loan Amt': f"${latest['average_loan_amount']:,.0f}",
                    'Interest Rate': f"{latest['weighted_avg_interest_rate']:.2f}%"
                })
        
        if not comparison_data:
            return None
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Create plotly table
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(comparison_df.columns),
                fill_color='paleturquoise',
                align='left',
                font=dict(size=12, color='black')
            ),
            cells=dict(
                values=[comparison_df[col] for col in comparison_df.columns],
                fill_color='lavender',
                align='left',
                font=dict(size=11)
            )
        )])
        
        fig.update_layout(
            title='Company Comparison',
            height=300
        )
        
        return ("Company Comparison", fig)
    
    def _create_interest_rate_chart(self, df: pd.DataFrame) -> Optional[Tuple[str, Any]]:
        """Create interest rate comparison chart"""
        if df.empty:
            return None
        
        fig = px.bar(
            df,
            x='company_name',
            y='weighted_avg_interest_rate',
            color='reporting_period',
            title='Weighted Average Interest Rate by Company',
            labels={'weighted_avg_interest_rate': 'Interest Rate (%)', 'company_name': 'Company'},
            barmode='group'
        )
        fig.update_layout(height=400)
        return ("Weighted Average Interest Rate", fig)
