"""
Complete hierarchical system that coordinates research and writing teams.
"""

from typing import Literal
from langchain_core.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph, START
from langgraph.types import Command

from .supervisor import State, SupervisorFramework
from .research_team import ResearchTeam
from .writing_team import WritingTeam
from .tools import ToolsManager
from .config import Config


class HierarchicalSystem:
    """Complete hierarchical agent system coordinating research and writing teams."""
    
    def __init__(self, config: Config = None):
        """Initialize the complete hierarchical system."""
        if config is None:
            config = Config()
        
        self.config = config
        
        # Validate configuration
        if not config.validate():
            raise ValueError("Missing required API keys. Please check your .env file.")
        
        # Initialize LLM
        from langchain_groq import ChatGroq
        self.llm = ChatGroq(
            model=config.default_model, 
            temperature=config.temperature, 
            api_key=config.get_groq_key()
        )
        
        # Initialize tools manager
        self.tools_manager = ToolsManager(config.get_tavily_key())
        
        # Initialize teams
        self.research_team = ResearchTeam(self.llm, self.tools_manager)
        self.writing_team = WritingTeam(self.llm, self.tools_manager)
        
        # Create super supervisor
        self.supervisor_node = SupervisorFramework.make_supervisor_node(
            self.llm, ["research_team", "writer_team"]
        )
        
        # Build the complete system graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the complete hierarchical system graph."""
        builder = StateGraph(State)
        builder.add_node("supervisor", self.supervisor_node)
        builder.add_node("research_team", self._call_research_team)
        builder.add_node("writer_team", self._call_writer_team)
        
        builder.add_edge(START, "supervisor")
        return builder.compile()
    
    def _call_research_team(self, state: State) -> Command[Literal["supervisor"]]:
        """Delegate tasks to the research team and return results to super supervisor."""
        response = self.research_team.invoke(state["messages"][-1:])
        return Command(
            update={
                "messages": [
                    HumanMessage(content=response["messages"][-1].content, name="research_team")
                ]
            },
            goto="supervisor",
        )
    
    def _call_writer_team(self, state: State) -> Command[Literal["supervisor"]]:
        """Delegate tasks to the writing team and return results to super supervisor."""
        response = self.writing_team.invoke(state["messages"][-1:])
        return Command(
            update={
                "messages": [
                    HumanMessage(content=response["messages"][-1].content, name="writer_team")
                ]
            },
            goto="supervisor",
        )
    
    def run(self, user_input: str, recursion_limit: int = None):
        """Run the hierarchical system with user input."""
        if recursion_limit is None:
            recursion_limit = self.config.recursion_limit
        
        return self.graph.stream(
            {"messages": [("user", user_input)]},
            {"recursion_limit": recursion_limit}
        )
    
    def run_sync(self, user_input: str, recursion_limit: int = None):
        """Run the hierarchical system synchronously and return final result."""
        if recursion_limit is None:
            recursion_limit = self.config.recursion_limit
        
        result = self.graph.invoke(
            {"messages": [("user", user_input)]},
            {"recursion_limit": recursion_limit}
        )
        return result
