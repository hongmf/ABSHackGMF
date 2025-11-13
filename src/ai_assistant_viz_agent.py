"""
AI Assistant Visualization Agent

Mimics all visualization methods from streamlit_viz_app.py to provide
comprehensive plotting capabilities in the AI Assistant panel.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from typing import Dict, List, Any, Optional, Tuple, Union
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib backend for non-interactive use
import matplotlib
matplotlib.use('Agg')

class AIAssistantVizAgent:
    """Comprehensive visualization agent for AI Assistant panel"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with DataFrame"""
        self.df = self._safe_numeric_conversion(df)
        self.numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = self.df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    def _safe_numeric_conversion(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to numeric where possible"""
        df_copy = df.copy()
        for col in df_copy.columns:
            if df_copy[col].dtype == 'object':
                try:
                    df_copy[col] = pd.to_numeric(df_copy[col], errors='ignore')
                except:
                    pass
        return df_copy
    
    def generate_comprehensive_visualizations(self, user_query: str = "") -> Dict[str, Any]:
        """
        Generate comprehensive visualizations mimicking streamlit_viz_app.py
        
        Returns:
            Dictionary with visualization results and metadata
        """
        results = {
            'data_overview': self._get_data_overview(),
            'visualizations': [],
            'prediction_available': self._check_prediction_capability(),
            'user_query': user_query
        }
        
        # Generate core 2x2 grid plots
        core_plots = self._generate_core_plots()
        if core_plots:
            results['visualizations'].extend(core_plots)
        
        # Generate relationship analysis
        relationship_plots = self._generate_relationship_plots()
        if relationship_plots:
            results['visualizations'].extend(relationship_plots)
        
        # Generate payment history timeline if applicable
        timeline_plot = self._generate_payment_timeline()
        if timeline_plot:
            results['visualizations'].append(timeline_plot)
        
        # Generate correlation heatmap
        correlation_plot = self._generate_correlation_heatmap()
        if correlation_plot:
            results['visualizations'].append(correlation_plot)
        
        # Generate time series prediction if requested
        if any(word in user_query.lower() for word in ['predict', 'forecast', 'future', 'trend']):
            prediction_plot = self._generate_prediction_plot()
            if prediction_plot:
                results['visualizations'].append(prediction_plot)
        
        return results
    
    def _get_data_overview(self) -> Dict[str, Any]:
        """Get data overview information"""
        return {
            'shape': self.df.shape,
            'numeric_columns': self.numeric_cols,
            'categorical_columns': self.categorical_cols,
            'sample_data': self.df.head().to_dict('records'),
            'missing_values': self.df.isnull().sum().to_dict()
        }
    
    def _generate_core_plots(self) -> List[Dict[str, Any]]:
        """Generate 2x2 grid of core plots"""
        plots = []
        
        # Create matplotlib figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Credit Score Distribution or first numeric column
        if 'Credit_Score' in self.df.columns:
            self.df['Credit_Score'].hist(bins=20, ax=ax1, color='skyblue', alpha=0.7)
            ax1.set_title('Credit Score Distribution')
            ax1.set_xlabel('Credit Score')
            ax1.set_ylabel('Frequency')
        elif self.numeric_cols:
            col = self.numeric_cols[0]
            self.df[col].hist(bins=20, ax=ax1, color='skyblue', alpha=0.7)
            ax1.set_title(f'{col} Distribution')
            ax1.set_xlabel(col)
            ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Employment Status or first categorical column
        if 'Employment_Status' in self.df.columns:
            self.df['Employment_Status'].value_counts().plot(kind='bar', ax=ax2, color='lightcoral')
            ax2.set_title('Employment Status Distribution')
            ax2.set_xlabel('Employment Status')
            ax2.set_ylabel('Count')
        elif self.categorical_cols:
            col = self.categorical_cols[0]
            self.df[col].value_counts().head(10).plot(kind='bar', ax=ax2, color='lightcoral')
            ax2.set_title(f'{col} Distribution')
            ax2.set_xlabel(col)
            ax2.set_ylabel('Count')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Income Distribution or second numeric column
        if 'Income' in self.df.columns:
            self.df['Income'].hist(bins=20, ax=ax3, color='lightgreen', alpha=0.7)
            ax3.set_title('Income Distribution')
            ax3.set_xlabel('Income')
            ax3.set_ylabel('Frequency')
        elif len(self.numeric_cols) > 1:
            col = self.numeric_cols[1]
            self.df[col].hist(bins=20, ax=ax3, color='lightgreen', alpha=0.7)
            ax3.set_title(f'{col} Distribution')
            ax3.set_xlabel(col)
            ax3.set_ylabel('Frequency')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Scatter plot or Age distribution
        if 'Income' in self.df.columns and 'Credit_Score' in self.df.columns:
            ax4.scatter(self.df['Income'], self.df['Credit_Score'], alpha=0.6, color='purple')
            ax4.set_title('Income vs Credit Score')
            ax4.set_xlabel('Income')
            ax4.set_ylabel('Credit Score')
        elif 'Age' in self.df.columns:
            self.df['Age'].hist(bins=15, ax=ax4, color='orange', alpha=0.7)
            ax4.set_title('Age Distribution')
            ax4.set_xlabel('Age')
            ax4.set_ylabel('Frequency')
        elif len(self.numeric_cols) >= 2:
            ax4.scatter(self.df[self.numeric_cols[0]], self.df[self.numeric_cols[1]], alpha=0.6, color='purple')
            ax4.set_title(f'{self.numeric_cols[0]} vs {self.numeric_cols[1]}')
            ax4.set_xlabel(self.numeric_cols[0])
            ax4.set_ylabel(self.numeric_cols[1])
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Convert to base64 for display
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        plots.append({
            'title': 'Core Data Analysis (2x2 Grid)',
            'type': 'matplotlib',
            'image_base64': img_base64,
            'description': 'Distribution analysis of key variables'
        })
        
        return plots
    
    def _generate_relationship_plots(self) -> List[Dict[str, Any]]:
        """Generate relationship analysis plots"""
        if len(self.numeric_cols) < 2:
            return []
        
        plots = []
        fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Scatter plot 1: Age vs Income or first two numeric columns
        if 'Age' in self.df.columns and 'Income' in self.df.columns:
            ax_left.scatter(self.df['Age'], self.df['Income'], alpha=0.6, color='green')
            ax_left.set_title('Age vs Income')
            ax_left.set_xlabel('Age')
            ax_left.set_ylabel('Income')
        else:
            col1, col2 = self.numeric_cols[0], self.numeric_cols[1]
            ax_left.scatter(self.df[col1], self.df[col2], alpha=0.6, color='green')
            ax_left.set_title(f'{col1} vs {col2}')
            ax_left.set_xlabel(col1)
            ax_left.set_ylabel(col2)
        ax_left.grid(True, alpha=0.3)
        
        # Scatter plot 2: Credit Utilization vs Loan Balance or other numeric columns
        if 'Credit_Utilization' in self.df.columns and 'Loan_Balance' in self.df.columns:
            ax_right.scatter(self.df['Credit_Utilization'], self.df['Loan_Balance'], alpha=0.6, color='red')
            ax_right.set_title('Credit Utilization vs Loan Balance')
            ax_right.set_xlabel('Credit Utilization')
            ax_right.set_ylabel('Loan Balance')
        elif len(self.numeric_cols) >= 4:
            col1, col2 = self.numeric_cols[2], self.numeric_cols[3]
            ax_right.scatter(self.df[col1], self.df[col2], alpha=0.6, color='red')
            ax_right.set_title(f'{col1} vs {col2}')
            ax_right.set_xlabel(col1)
            ax_right.set_ylabel(col2)
        elif len(self.numeric_cols) >= 3:
            col1, col2 = self.numeric_cols[0], self.numeric_cols[2]
            ax_right.scatter(self.df[col1], self.df[col2], alpha=0.6, color='red')
            ax_right.set_title(f'{col1} vs {col2}')
            ax_right.set_xlabel(col1)
            ax_right.set_ylabel(col2)
        ax_right.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        plots.append({
            'title': 'Relationship Analysis',
            'type': 'matplotlib',
            'image_base64': img_base64,
            'description': 'Scatter plots showing relationships between variables'
        })
        
        return plots
    
    def _generate_payment_timeline(self) -> Optional[Dict[str, Any]]:
        """Generate payment history timeline"""
        month_cols = [col for col in self.df.columns if col.startswith('Month_')]
        if not month_cols:
            return None
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Calculate payment status percentages over time
        payment_data = []
        for month in month_cols:
            status_counts = self.df[month].value_counts(normalize=True) * 100
            payment_data.append(status_counts)
        
        payment_df = pd.DataFrame(payment_data, index=month_cols).fillna(0)
        
        # Stacked area plot
        ax.stackplot(range(len(month_cols)), 
                   payment_df.get('On-time', [0]*len(month_cols)),
                   payment_df.get('Late', [0]*len(month_cols)),
                   payment_df.get('Missed', [0]*len(month_cols)),
                   labels=['On-time', 'Late', 'Missed'],
                   colors=['green', 'orange', 'red'],
                   alpha=0.7)
        
        ax.set_title('Payment Status Over Time (%)', fontsize=16)
        ax.set_xlabel('Month')
        ax.set_ylabel('Percentage')
        ax.set_xticks(range(len(month_cols)))
        ax.set_xticklabels(month_cols, rotation=45)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return {
            'title': 'Payment History Timeline',
            'type': 'matplotlib',
            'image_base64': img_base64,
            'description': 'Payment status trends over time'
        }
    
    def _generate_correlation_heatmap(self) -> Optional[Dict[str, Any]]:
        """Generate correlation matrix heatmap"""
        if len(self.numeric_cols) <= 1:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 8))
        correlation_matrix = self.df[self.numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax, fmt='.2f')
        ax.set_title('Correlation Matrix')
        
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return {
            'title': 'Correlation Matrix',
            'type': 'matplotlib',
            'image_base64': img_base64,
            'description': 'Correlation between numeric variables'
        }
    
    def _generate_prediction_plot(self) -> Optional[Dict[str, Any]]:
        """Generate time series prediction plot"""
        if not self.numeric_cols:
            return None
        
        try:
            # Simple trend prediction using linear regression
            target_col = self.numeric_cols[0]
            if len(self.df) < 10:
                return None
            
            # Create time index
            x = np.arange(len(self.df))
            y = self.df[target_col].fillna(self.df[target_col].mean())
            
            # Fit linear trend
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            
            # Predict future values
            future_x = np.arange(len(self.df), len(self.df) + 10)
            future_y = p(future_x)
            
            # Plot
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(x, y, 'o-', label='Historical Data', color='blue')
            ax.plot(future_x, future_y, 's-', label='Predictions', color='red')
            ax.plot(x, p(x), '--', label='Trend Line', color='green')
            
            ax.set_title(f'Time Series Prediction: {target_col}')
            ax.set_xlabel('Time Period')
            ax.set_ylabel(target_col)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return {
                'title': f'Time Series Prediction: {target_col}',
                'type': 'matplotlib',
                'image_base64': img_base64,
                'description': f'Linear trend prediction for {target_col}',
                'model_info': {
                    'model_used': 'Linear Regression',
                    'prediction_steps': 10,
                    'target_variable': target_col
                }
            }
        except Exception as e:
            return None
    
    def _check_prediction_capability(self) -> bool:
        """Check if prediction is possible with current data"""
        return len(self.numeric_cols) > 0 and len(self.df) >= 10
    
    def generate_plotly_visualizations(self) -> List[Dict[str, Any]]:
        """Generate interactive Plotly visualizations"""
        plots = []
        
        # Distribution plot
        if self.numeric_cols:
            fig = px.histogram(
                self.df, 
                x=self.numeric_cols[0], 
                title=f'{self.numeric_cols[0]} Distribution',
                nbins=20
            )
            plots.append({
                'title': f'{self.numeric_cols[0]} Distribution',
                'type': 'plotly',
                'figure': fig,
                'description': f'Interactive histogram of {self.numeric_cols[0]}'
            })
        
        # Scatter plot
        if len(self.numeric_cols) >= 2:
            fig = px.scatter(
                self.df,
                x=self.numeric_cols[0],
                y=self.numeric_cols[1],
                title=f'{self.numeric_cols[0]} vs {self.numeric_cols[1]}'
            )
            plots.append({
                'title': f'{self.numeric_cols[0]} vs {self.numeric_cols[1]}',
                'type': 'plotly',
                'figure': fig,
                'description': f'Interactive scatter plot'
            })
        
        # Box plot
        if self.categorical_cols and self.numeric_cols:
            fig = px.box(
                self.df,
                x=self.categorical_cols[0],
                y=self.numeric_cols[0],
                title=f'{self.numeric_cols[0]} by {self.categorical_cols[0]}'
            )
            plots.append({
                'title': f'{self.numeric_cols[0]} by {self.categorical_cols[0]}',
                'type': 'plotly',
                'figure': fig,
                'description': f'Box plot showing distribution by category'
            })
        
        return plots

def create_visualization_agent(df: pd.DataFrame) -> AIAssistantVizAgent:
    """Factory function to create visualization agent"""
    return AIAssistantVizAgent(df)