"""
Writing team implementation for document creation and editing.
"""

from typing import Literal
from langchain_core.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START
from langgraph.types import Command

from .supervisor import State, SupervisorFramework
from .tools import ToolsManager


class WritingTeam:
    """Writing team that coordinates document writing, note-taking, and chart generation."""
    
    def __init__(self, llm: BaseChatModel, tools_manager: ToolsManager):
        """Initialize the writing team with agents and supervisor."""
        self.llm = llm
        self.tools_manager = tools_manager
        
        # Create individual agents
        self.doc_writer_agent = create_react_agent(
            llm,
            tools=tools_manager.get_writing_tools(),
            prompt=(
                "You can read, write and edit documents based on note-taker's outlines. "
                "Don't ask follow-up questions."
            ),
        )
        
        self.note_taking_agent = create_react_agent(
            llm,
            tools=tools_manager.get_note_taking_tools(),
            prompt=(
                "You can read documents and create outlines for the document writer. "
                "Don't ask follow-up questions."
            ),
        )
        
        self.chart_generating_agent = create_react_agent(
            llm, 
            tools=tools_manager.get_chart_tools()
        )
        
        # Create supervisor
        self.supervisor_node = SupervisorFramework.make_supervisor_node(
            llm, ["doc_writer", "note_taker", "chart_generator"]
        )
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the writing team workflow graph."""
        builder = StateGraph(State)
        builder.add_node("supervisor", self.supervisor_node)
        builder.add_node("doc_writer", self._doc_writing_node)
        builder.add_node("note_taker", self._note_taking_node)
        builder.add_node("chart_generator", self._chart_generating_node)
        
        builder.add_edge(START, "supervisor")
        return builder.compile()
    
    def _doc_writing_node(self, state: State) -> Command[Literal["supervisor"]]:
        """Node for handling document writing tasks."""
        result = self.doc_writer_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="doc_writer")
                ]
            },
            goto="supervisor",
        )
    
    def _note_taking_node(self, state: State) -> Command[Literal["supervisor"]]:
        """Node for handling note-taking and outline creation."""
        result = self.note_taking_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="note_taker")
                ]
            },
            goto="supervisor",
        )
    
    def _chart_generating_node(self, state: State) -> Command[Literal["supervisor"]]:
        """Node for handling chart and visualization generation."""
        result = self.chart_generating_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=result["messages"][-1].content, name="chart_generator"
                    )
                ]
            },
            goto="supervisor",
        )
    
    def invoke(self, messages):
        """Invoke the writing team with given messages."""
        if isinstance(messages, list):
            return self.graph.invoke({"messages": messages})
        else:
            return self.graph.invoke(messages)
