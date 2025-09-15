"""
Research team implementation for web search and content scraping.
"""

from typing import Literal
from langchain_core.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START
from langgraph.types import Command

from .supervisor import State, SupervisorFramework
from .tools import ToolsManager


class ResearchTeam:
    """Research team that coordinates search and web scraping agents."""
    
    def __init__(self, llm: BaseChatModel, tools_manager: ToolsManager):
        """Initialize the research team with agents and supervisor."""
        self.llm = llm
        self.tools_manager = tools_manager
        
        # Create individual agents
        self.search_agent = create_react_agent(llm, tools=[tools_manager.tavily])
        self.web_scraper_agent = create_react_agent(llm, tools=[tools_manager.scrap_web])
        
        # Create supervisor
        self.supervisor_node = SupervisorFramework.make_supervisor_node(
            llm, ["search", "web_scraper"]
        )
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the research team workflow graph."""
        builder = StateGraph(State)
        builder.add_node("supervisor", self.supervisor_node)
        builder.add_node("search", self._search_node)
        builder.add_node("web_scraper", self._web_scraper_node)
        
        builder.add_edge(START, "supervisor")
        return builder.compile()
    
    def _search_node(self, state: State) -> Command[Literal["supervisor"]]:
        """Node for handling web search requests."""
        result = self.search_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="search")
                ]
            },
            goto="supervisor",
        )
    
    def _web_scraper_node(self, state: State) -> Command[Literal["supervisor"]]:
        """Node for handling web scraping requests."""
        result = self.web_scraper_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="web_scraper")
                ]
            },
            goto="supervisor",
        )
    
    def invoke(self, messages):
        """Invoke the research team with given messages."""
        return self.graph.invoke({"messages": messages})
