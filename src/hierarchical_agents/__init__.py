"""
Hierarchical AI Agents System

A sophisticated multi-tier agent system using LangGraph for coordinating
research, writing, and visualization tasks.
"""

__version__ = "0.1.0"
__author__ = "Hierarchical Agents Project"

from .config import Config
from .supervisor import SupervisorFramework
from .research_team import ResearchTeam
from .writing_team import WritingTeam
from .hierarchical_system import HierarchicalSystem

__all__ = [
    "Config",
    "SupervisorFramework", 
    "ResearchTeam",
    "WritingTeam",
    "HierarchicalSystem",
]
