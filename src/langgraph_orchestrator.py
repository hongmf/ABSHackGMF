"""
LangGraph-based Agent Orchestrator

Uses LangGraph to create a stateful graph-based orchestration system
for routing queries to specialized agents and managing conversation flow.
"""

from typing import TypedDict, Annotated, Sequence, Dict, Any, List, Tuple, Optional
from typing_extensions import TypedDict
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import plotly.graph_objects as go

from visualization_agent import VisualizationAgent
from form_424h_agent import Form424HAgent
from form_10d_agent import Form10DAgent


class AgentState(TypedDict):
    """
    State object for the agent graph
    Tracks conversation history and processing results
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    data_type: str
    visualizations: List[go.Figure]
    explanation: str
    data_sources: Dict[str, Any]
    next_action: str


class LangGraphOrchestrator:
    """
    LangGraph-based orchestrator for multi-agent visualization system
    
    Graph Structure:
    START -> classify_query -> route_to_agent -> generate_viz -> END
    """
    
    def __init__(self, data_sources: Dict[str, Any], bedrock_kb_ids: Optional[Dict[str, str]] = None, bedrock_client = None):
        """
        Initialize LangGraph orchestrator
        
        Args:
            data_sources: Dictionary mapping data types to their data/dataframes
                Example: {
                    'abs-ee': {'data': [...], 'df': pd.DataFrame(...)},
                    '424h': {'data': [...], 'df': pd.DataFrame(...)},
                    '10-d': {'data': [...], 'df': pd.DataFrame(...)}
                }
            bedrock_kb_ids: Dictionary mapping data types to their Bedrock Knowledge Base IDs
                Example: {
                    'abs-ee': 'A7EOGV6BHS',
                    '424h': '83TDL5E9HV',
                    '10-d': 'O2KBJHZUJO'
                }
            bedrock_client: Bedrock agent runtime client
        """
        self.data_sources = data_sources
        self.bedrock_kb_ids = bedrock_kb_ids or {}
        self.bedrock_client = bedrock_client
        self.agents = self._initialize_agents()
        self.graph = self._build_graph()
        
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all available agents"""
        agents = {}
        
        if 'abs-ee' in self.data_sources:
            agents['abs-ee'] = VisualizationAgent(
                data=self.data_sources['abs-ee']['data'],
                df=self.data_sources['abs-ee']['df']
            )
        
        if '424h' in self.data_sources:
            agents['424h'] = Form424HAgent(
                data=self.data_sources['424h']['data'],
                df=self.data_sources['424h']['df'],
                bedrock_kb_id=self.bedrock_kb_ids.get('424h'),
                bedrock_client=self.bedrock_client
            )
        
        if '10-d' in self.data_sources:
            agents['10-d'] = Form10DAgent(
                data=self.data_sources['10-d']['data'],
                df=self.data_sources['10-d']['df'],
                bedrock_kb_id=self.bedrock_kb_ids.get('10-d'),
                bedrock_client=self.bedrock_client
            )
        
        return agents
    
    def _classify_query(self, state: AgentState) -> AgentState:
        """
        Classify the query to determine which agent should handle it
        
        Node: classify_query
        """
        query = state['query'].lower()
        
        # Keywords for each data type
        keywords = {
            'abs-ee': [
                'auto loan', 'car loan', 'vehicle loan',
                'fico', 'delinquency', 'prepayment',
                'abs-ee', 'securitization', 'pool balance'
            ],
            '424h': [
                '424h', 'form 424h', '424-h',
                'prospectus', 'offering', 'issuance',
                'pricing', 'spread', 'yield'
            ],
            '10-d': [
                '10-d', 'form 10-d', '10d', 'form 10d',
                'distribution', 'payment', 'cash flow',
                'pool performance', 'cpr', 'smm'
            ]
        }
        
        # Score each data type based on keyword matches
        scores = {}
        for data_type, kw_list in keywords.items():
            score = sum(1 for kw in kw_list if kw in query)
            if score > 0 and data_type in self.agents:
                scores[data_type] = score
        
        # Determine best match
        if scores:
            data_type = max(scores, key=scores.get)
        elif 'abs-ee' in self.agents:
            # Default to abs-ee if available
            data_type = 'abs-ee'
        else:
            data_type = 'unknown'
        
        # Update state
        state['data_type'] = data_type
        state['messages'].append(
            AIMessage(content=f"Classified query as: {data_type}")
        )
        
        return state
    
    def _route_to_agent(self, state: AgentState) -> str:
        """
        Determine which agent node to route to
        
        Router: Decides next node based on data_type
        """
        data_type = state['data_type']
        
        if data_type == 'abs-ee' and 'abs-ee' in self.agents:
            return 'abs_ee_agent'
        elif data_type == '424h' and '424h' in self.agents:
            return '424h_agent'
        elif data_type == '10-d' and '10-d' in self.agents:
            return '10d_agent'
        else:
            return 'no_agent'
    
    def _abs_ee_agent_node(self, state: AgentState) -> AgentState:
        """
        Execute ABS-EE visualization agent
        
        Node: abs_ee_agent
        """
        agent = self.agents['abs-ee']
        query = state['query']
        
        # Generate visualizations
        viz_result = agent.generate_visualizations(query)
        
        # VisualizationAgent returns List[Tuple[str, figure]]
        # Extract figures and build explanation
        if viz_result and isinstance(viz_result, list) and isinstance(viz_result[0], tuple):
            # Old format: List[Tuple[title, figure]]
            visualizations = [fig for title, fig in viz_result]
            titles = [title for title, fig in viz_result]
            explanation = f"Generated {len(visualizations)} ABS-EE visualizations: {', '.join(titles)}"
        elif isinstance(viz_result, tuple) and len(viz_result) == 2:
            # New format: Tuple[List[figure], explanation]
            visualizations, explanation = viz_result
        else:
            visualizations = []
            explanation = "No visualizations generated"
        
        # Update state
        state['visualizations'] = visualizations if visualizations else []
        state['explanation'] = explanation
        state['messages'].append(
            AIMessage(content=f"ABS-EE Agent: {explanation}")
        )
        
        return state
    
    def _424h_agent_node(self, state: AgentState) -> AgentState:
        """
        Execute Form 424H agent
        
        Node: 424h_agent
        """
        agent = self.agents['424h']
        query = state['query']
        
        # Generate visualizations
        visualizations, explanation = agent.generate_visualizations(query)
        
        # Update state
        state['visualizations'] = visualizations if visualizations else []
        state['explanation'] = explanation
        state['messages'].append(
            AIMessage(content=f"424H Agent: {explanation}")
        )
        
        return state
    
    def _10d_agent_node(self, state: AgentState) -> AgentState:
        """
        Execute Form 10-D agent
        
        Node: 10d_agent
        """
        agent = self.agents['10-d']
        query = state['query']
        
        # Generate visualizations
        visualizations, explanation = agent.generate_visualizations(query)
        
        # Update state
        state['visualizations'] = visualizations if visualizations else []
        state['explanation'] = explanation
        state['messages'].append(
            AIMessage(content=f"10-D Agent: {explanation}")
        )
        
        return state
    
    def _no_agent_node(self, state: AgentState) -> AgentState:
        """
        Handle case when no appropriate agent is found
        
        Node: no_agent
        """
        data_type = state['data_type']
        
        if data_type == 'unknown':
            explanation = "Unable to determine data type from query. Please specify whether you're asking about ABS-EE auto loans, Form 424H offerings, or Form 10-D distributions."
        else:
            explanation = f"No agent available for data type: {data_type}. This data source may not be configured yet."
        
        state['visualizations'] = []
        state['explanation'] = explanation
        state['messages'].append(
            AIMessage(content=explanation)
        )
        
        return state
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state graph
        
        Graph Flow:
        1. START -> classify_query: Analyze query and determine data type
        2. classify_query -> router: Route to appropriate agent
        3. router -> [abs_ee_agent | 424h_agent | 10d_agent | no_agent]
        4. agent_node -> END: Return results
        """
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("abs_ee_agent", self._abs_ee_agent_node)
        workflow.add_node("424h_agent", self._424h_agent_node)
        workflow.add_node("10d_agent", self._10d_agent_node)
        workflow.add_node("no_agent", self._no_agent_node)
        
        # Set entry point
        workflow.set_entry_point("classify_query")
        
        # Add conditional edges from classify_query to appropriate agent
        workflow.add_conditional_edges(
            "classify_query",
            self._route_to_agent,
            {
                "abs_ee_agent": "abs_ee_agent",
                "424h_agent": "424h_agent",
                "10d_agent": "10d_agent",
                "no_agent": "no_agent"
            }
        )
        
        # Add edges from all agent nodes to END
        workflow.add_edge("abs_ee_agent", END)
        workflow.add_edge("424h_agent", END)
        workflow.add_edge("10d_agent", END)
        workflow.add_edge("no_agent", END)
        
        # Compile the graph
        return workflow.compile()
    
    def generate_visualizations(self, query: str) -> Tuple[List[go.Figure], str]:
        """
        Generate visualizations for a user query using LangGraph orchestration
        
        Args:
            query: User's natural language query
            
        Returns:
            Tuple of (list of plotly figures, explanation text)
        """
        # Initialize state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "query": query,
            "data_type": "",
            "visualizations": [],
            "explanation": "",
            "data_sources": self.data_sources,
            "next_action": ""
        }
        
        # Execute graph
        final_state = self.graph.invoke(initial_state)
        
        # Extract results
        visualizations = final_state.get('visualizations', [])
        explanation = final_state.get('explanation', 'No explanation available')
        
        return visualizations, explanation
    
    def get_conversation_history(self, query: str) -> List[Dict[str, str]]:
        """
        Get the full conversation history for a query execution
        
        Args:
            query: User's natural language query
            
        Returns:
            List of message dictionaries with role and content
        """
        # Initialize state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "query": query,
            "data_type": "",
            "visualizations": [],
            "explanation": "",
            "data_sources": self.data_sources,
            "next_action": ""
        }
        
        # Execute graph
        final_state = self.graph.invoke(initial_state)
        
        # Extract message history
        messages = []
        for msg in final_state.get('messages', []):
            messages.append({
                'role': 'human' if isinstance(msg, HumanMessage) else 'ai',
                'content': msg.content
            })
        
        return messages
    
    def visualize_graph(self) -> str:
        """
        Generate a visualization of the graph structure (mermaid format)
        
        Returns:
            Mermaid diagram string
        """
        return """
        graph TD
            START([START]) --> classify[Classify Query]
            classify --> router{Route to Agent}
            router -->|ABS-EE| abs_ee[ABS-EE Agent]
            router -->|424H| form_424h[424H Agent]
            router -->|10-D| form_10d[10-D Agent]
            router -->|Unknown| no_agent[No Agent]
            abs_ee --> END([END])
            form_424h --> END
            form_10d --> END
            no_agent --> END
        """
