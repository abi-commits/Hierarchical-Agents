"""
Supervisor framework for coordinating multiple agents.
"""

from typing import List, Any
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import MessagesState, END
from langgraph.types import Command


class State(MessagesState):
    """State class for agent communication."""
    next: str


class SupervisorFramework:
    """Framework for creating supervisor nodes that coordinate multiple agents."""
    
    @staticmethod
    def make_supervisor_node(llm: BaseChatModel, members: List[str]):
        """Create a supervisor node that routes between worker agents."""
        options = ["FINISH"] + members
        system_prompt = (
            "You are a supervisor tasked with managing a conversation between the"
            f" following workers: {members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH."
        )
        
        # Create a dynamic router class
        from pydantic import BaseModel, Field
        from typing import Union
        
        class Router(BaseModel):
            """Worker to route to next, If no worker is needed, return FINISH."""
            next: str = Field(description=f"Next worker to route to. Options: {options}")

        def supervisor_node(state: State) -> Command[Any]:
            """An LLM-powered supervisor that routes to the next worker or ends the process."""
            messages = [
                {"role": "system", "content": system_prompt}
            ] + state["messages"]
            response = llm.with_structured_output(Router).invoke(messages)
            
            # Handle both dict and object response formats
            try:
                if isinstance(response, dict):
                    goto = response.get('next', "FINISH")
                else:
                    # Try to access as attribute (for Pydantic models)
                    goto = getattr(response, 'next', "FINISH")
            except Exception:
                goto = "FINISH"
                
            if goto == "FINISH":
                goto = END
            return Command(goto=goto, update={"next": goto})
        
        return supervisor_node
