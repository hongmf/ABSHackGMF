"""
Agent Orchestrator

Coordinates multiple specialized agents for different data types.
Routes queries to the appropriate agent based on data type and context.
"""

from typing import List, Tuple, Any, Optional, Dict
import pandas as pd
from enum import Enum


class DataType(Enum):
    """Supported data types"""
    ABS_EE = "abs-ee"  # Auto loan data
    FORM_424H = "424h"  # Form 424h data
    FORM_10D = "10-d"  # Form 10-D data
    UNKNOWN = "unknown"


class AgentOrchestrator:
    """
    Master orchestrator that routes queries to specialized agents
    based on data type and query context
    """
    
    def __init__(self, data_sources: Dict[str, Any]):
        """
        Initialize orchestrator with available data sources
        
        Args:
            data_sources: Dict mapping data types to their data/config
                Example: {
                    'abs-ee': {'data': [...], 'df': pd.DataFrame(...)},
                    '424h': {'data': [...], 'df': pd.DataFrame(...)}
                }
        """
        self.data_sources = data_sources
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize specialized agents for each data type"""
        # Import agents dynamically to avoid circular dependencies
        from visualization_agent import VisualizationAgent
        from form_424h_agent import Form424HAgent
        from form_10d_agent import Form10DAgent
        
        # Initialize ABS-EE agent if data available
        if 'abs-ee' in self.data_sources:
            abs_ee_data = self.data_sources['abs-ee']
            self.agents[DataType.ABS_EE] = VisualizationAgent(
                data=abs_ee_data['data'],
                df=abs_ee_data['df']
            )
        
        # Initialize 424H agent if data available
        if '424h' in self.data_sources:
            form_424h_data = self.data_sources['424h']
            self.agents[DataType.FORM_424H] = Form424HAgent(
                data=form_424h_data['data'],
                df=form_424h_data['df']
            )
        
        # Initialize 10-D agent if data available
        if '10-d' in self.data_sources:
            form_10d_data = self.data_sources['10-d']
            self.agents[DataType.FORM_10D] = Form10DAgent(
                data=form_10d_data['data'],
                df=form_10d_data['df']
            )
    
    def detect_data_type(self, query: str) -> DataType:
        """
        Detect which data type the query is about
        
        Args:
            query: User's natural language query
            
        Returns:
            DataType enum indicating the relevant data type
        """
        query_lower = query.lower()
        
        # Keywords for ABS-EE (Auto Loans)
        abs_ee_keywords = [
            'auto loan', 'car loan', 'vehicle loan',
            'fico', 'delinquency', 'prepayment',
            'abs-ee', 'securitization', 'pool balance'
        ]
        
        # Keywords for 424H
        form_424h_keywords = [
            '424h', 'form 424h', '424-h',
            # Add 424h-specific keywords here
        ]
        
        # Keywords for 10-D
        form_10d_keywords = [
            '10-d', 'form 10-d', '10d', 'form 10d',
            # Add 10-D-specific keywords here
        ]
        
        # Check for 10-D first (most specific)
        if any(keyword in query_lower for keyword in form_10d_keywords):
            return DataType.FORM_10D
        
        # Check for 424H
        if any(keyword in query_lower for keyword in form_424h_keywords):
            return DataType.FORM_424H
        
        # Check for ABS-EE
        if any(keyword in query_lower for keyword in abs_ee_keywords):
            return DataType.ABS_EE
        
        # Default: check which data sources are available
        if 'abs-ee' in self.data_sources and len(self.data_sources) == 1:
            return DataType.ABS_EE
        elif '424h' in self.data_sources and len(self.data_sources) == 1:
            return DataType.FORM_424H
        elif '10-d' in self.data_sources and len(self.data_sources) == 1:
            return DataType.FORM_10D
        
        return DataType.UNKNOWN
    
    def generate_visualizations(self, query: str, data_type: Optional[DataType] = None) -> List[Tuple[str, Any]]:
        """
        Route query to appropriate agent and generate visualizations
        
        Args:
            query: User's natural language query
            data_type: Optional explicit data type (auto-detected if not provided)
            
        Returns:
            List of tuples (title, plotly_figure)
        """
        # Detect data type if not provided
        if data_type is None:
            data_type = self.detect_data_type(query)
        
        # Route to appropriate agent
        if data_type == DataType.ABS_EE and DataType.ABS_EE in self.agents:
            return self.agents[DataType.ABS_EE].generate_visualizations(query)
        
        elif data_type == DataType.FORM_424H and DataType.FORM_424H in self.agents:
            return self.agents[DataType.FORM_424H].generate_visualizations(query)
        
        else:
            # No agent available or unknown data type
            return []
    
    def get_available_data_types(self) -> List[str]:
        """Get list of available data types"""
        return [dt.value for dt in self.agents.keys()]
    
    def get_agent_info(self, data_type: DataType) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific agent
        
        Args:
            data_type: The data type/agent to get info about
            
        Returns:
            Dictionary with agent metadata or None if not available
        """
        if data_type in self.agents:
            agent = self.agents[data_type]
            return {
                'type': data_type.value,
                'available': True,
                'data_count': len(agent.data) if hasattr(agent, 'data') else 0,
                'companies': list(agent.df['company_name'].unique()) if hasattr(agent, 'df') else []
            }
        return None
    
    def generate_multi_source_comparison(self, query: str) -> List[Tuple[str, Any]]:
        """
        Generate visualizations comparing across different data types
        (e.g., comparing ABS-EE vs 424H metrics)
        
        Args:
            query: User's natural language query
            
        Returns:
            List of tuples (title, plotly_figure)
        """
        # TODO: Implement cross-data-type comparisons
        # This would combine data from multiple agents
        visualizations = []
        
        # For now, just combine results from all agents
        for data_type, agent in self.agents.items():
            viz = agent.generate_visualizations(query)
            visualizations.extend(viz)
        
        return visualizations
