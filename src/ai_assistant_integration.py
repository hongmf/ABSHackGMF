"""
AI Assistant Integration Module

Provides easy integration of the visualization agent with AI Assistant panel.
Handles data loading, query processing, and response formatting.
"""

import pandas as pd
import json
from typing import Dict, List, Any, Optional
from .ai_assistant_viz_agent import AIAssistantVizAgent
from .dynamodb_loader import load_dynamodb_table
from .s3_data_loader import load_s3_file
import os

class AIAssistantIntegration:
    """Integration layer for AI Assistant visualization capabilities"""
    
    def __init__(self):
        self.current_agent = None
        self.current_data_source = None
        self.available_data_sources = self._discover_data_sources()
    
    def _discover_data_sources(self) -> Dict[str, List[str]]:
        """Discover available data sources"""
        sources = {
            'dynamodb_tables': [],
            's3_files': [],
            'local_files': []
        }
        
        try:
            # Try to discover DynamoDB tables
            from .dynamodb_loader import list_dynamodb_tables
            sources['dynamodb_tables'] = list_dynamodb_tables()
        except:
            pass
        
        try:
            # Try to discover S3 files
            from .s3_data_loader import list_s3_folders, list_s3_files
            folders = list_s3_folders()
            for folder in folders[:3]:  # Limit to first 3 folders
                files = list_s3_files(folder)
                sources['s3_files'].extend(files[:5])  # Limit to 5 files per folder
        except:
            pass
        
        # Check for local CSV files
        if os.path.exists('scripts/Delinquency_prediction_dataset.csv'):
            sources['local_files'].append('scripts/Delinquency_prediction_dataset.csv')
        
        return sources
    
    def load_data(self, source_type: str, source_name: str) -> bool:
        """
        Load data from specified source
        
        Args:
            source_type: 'dynamodb', 's3', or 'local'
            source_name: Name of the table/file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if source_type == 'dynamodb':
                df = load_dynamodb_table(source_name)
            elif source_type == 's3':
                df = load_s3_file(source_name)
            elif source_type == 'local':
                df = pd.read_csv(source_name)
            else:
                return False
            
            self.current_agent = AIAssistantVizAgent(df)
            self.current_data_source = f"{source_type}: {source_name}"
            return True
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def load_default_data(self) -> bool:
        """Load default dataset"""
        try:
            df = pd.read_csv('scripts/Delinquency_prediction_dataset.csv')
            self.current_agent = AIAssistantVizAgent(df)
            self.current_data_source = "Default: Delinquency_prediction_dataset.csv"
            return True
        except Exception as e:
            print(f"Error loading default data: {str(e)}")
            return False
    
    def process_visualization_request(self, user_query: str) -> Dict[str, Any]:
        """
        Process user's visualization request
        
        Args:
            user_query: User's natural language query
            
        Returns:
            Comprehensive response with visualizations and metadata
        """
        if not self.current_agent:
            # Try to load default data
            if not self.load_default_data():
                return {
                    'error': 'No data available. Please load a dataset first.',
                    'available_sources': self.available_data_sources
                }
        
        try:
            # Generate comprehensive visualizations
            results = self.current_agent.generate_comprehensive_visualizations(user_query)
            
            # Add metadata
            results['data_source'] = self.current_data_source
            results['available_sources'] = self.available_data_sources
            
            # Generate summary response
            results['summary'] = self._generate_summary_response(results, user_query)
            
            return results
            
        except Exception as e:
            return {
                'error': f'Error generating visualizations: {str(e)}',
                'data_source': self.current_data_source
            }
    
    def _generate_summary_response(self, results: Dict[str, Any], user_query: str) -> str:
        """Generate a summary response for the user"""
        data_overview = results['data_overview']
        num_visualizations = len(results['visualizations'])
        
        summary = f"""📊 **Visualization Analysis Complete**

**Data Source:** {self.current_data_source}
**Dataset Size:** {data_overview['shape'][0]} rows × {data_overview['shape'][1]} columns
**Generated Visualizations:** {num_visualizations}

**Available Columns:**
- Numeric: {', '.join(data_overview['numeric_columns'][:5])}{'...' if len(data_overview['numeric_columns']) > 5 else ''}
- Categorical: {', '.join(data_overview['categorical_columns'][:5])}{'...' if len(data_overview['categorical_columns']) > 5 else ''}

**Visualizations Generated:**"""
        
        for viz in results['visualizations']:
            summary += f"\n- {viz['title']}: {viz['description']}"
        
        if results['prediction_available'] and any(word in user_query.lower() for word in ['predict', 'forecast', 'future', 'trend']):
            summary += "\n\n🔮 **Prediction Analysis:** Time series forecasting available for numeric variables."
        
        summary += f"\n\n💡 **Insights:** The data shows {data_overview['shape'][0]} records with {len(data_overview['numeric_columns'])} numeric variables suitable for analysis."
        
        return summary
    
    def get_data_info(self) -> Dict[str, Any]:
        """Get information about currently loaded data"""
        if not self.current_agent:
            return {
                'loaded': False,
                'available_sources': self.available_data_sources
            }
        
        return {
            'loaded': True,
            'data_source': self.current_data_source,
            'data_overview': self.current_agent._get_data_overview(),
            'available_sources': self.available_data_sources
        }
    
    def switch_data_source(self, source_type: str, source_name: str) -> Dict[str, Any]:
        """Switch to a different data source"""
        success = self.load_data(source_type, source_name)
        
        if success:
            return {
                'success': True,
                'message': f'Successfully loaded {source_type}: {source_name}',
                'data_info': self.get_data_info()
            }
        else:
            return {
                'success': False,
                'message': f'Failed to load {source_type}: {source_name}',
                'available_sources': self.available_data_sources
            }

# Global instance for easy access
ai_assistant = AIAssistantIntegration()

def process_viz_request(user_query: str) -> Dict[str, Any]:
    """
    Main entry point for AI Assistant visualization requests
    
    Args:
        user_query: User's visualization request
        
    Returns:
        Complete response with visualizations and metadata
    """
    return ai_assistant.process_visualization_request(user_query)

def load_data_source(source_type: str, source_name: str) -> Dict[str, Any]:
    """Load a specific data source"""
    return ai_assistant.switch_data_source(source_type, source_name)

def get_current_data_info() -> Dict[str, Any]:
    """Get information about currently loaded data"""
    return ai_assistant.get_data_info()