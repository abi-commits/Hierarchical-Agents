"""
Core tools and utilities for the Hierarchical Agents system.
"""

from typing import Annotated, List, Dict, Optional
from pathlib import Path
from tempfile import TemporaryDirectory

from langchain_community.document_loaders import WebBaseLoader
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL


class ToolsManager:
    """Manager class for all tools used by the agent system."""
    
    def __init__(self, tavily_api_key: str):
        """Initialize tools with required API keys."""
        self.tavily = TavilySearch(max_results=3, api_key=tavily_api_key)
        self._temp_dir = TemporaryDirectory()
        self.working_dir = Path(self._temp_dir.name)
        self.repl = PythonREPL()
        
    def get_research_tools(self):
        """Get tools for research team."""
        return [self.tavily, self._create_scrap_web_tool()]
    
    def get_writing_tools(self):
        """Get tools for writing team."""
        return [self._create_write_document_tool(), self._create_edit_document_tool(), self._create_read_document_tool()]
    
    def get_note_taking_tools(self):
        """Get tools for note taking."""
        return [self._create_outline_tool(), self._create_read_document_tool()]
    
    def get_chart_tools(self):
        """Get tools for chart generation."""
        return [self._create_read_document_tool(), self._create_python_repl_tool()]

    def _create_scrap_web_tool(self):
        """Create scrap_web tool."""
        @tool
        def scrap_web(urls: List[str]) -> str:
            """Scrape the content of a webpage given its URL."""
            loader = WebBaseLoader(urls)
            docs = loader.load()
            return "\n\n".join(
                [f"Document name: {doc.metadata.get('title', '')}\n{doc.page_content}" for doc in docs]
            )
        return scrap_web

    def _create_outline_tool(self):
        """Create outline tool."""
        working_dir = self.working_dir
        
        @tool
        def create_outline(
            points: Annotated[List[str], "List of main points for the outline"],
            file_name: Annotated[str, "The name of the file to save the outline"],
        ) -> Annotated[str, "The file path where the outline is saved"]:
            """Create a text file with the given outline points."""
            with (working_dir / file_name).open("w") as f:
                for i, point in enumerate(points):
                    f.write(f"{i + 1}. {point}\n")
            return f"Outline saved to {working_dir / file_name}"
        return create_outline

    def _create_read_document_tool(self):
        """Create read document tool."""
        working_dir = self.working_dir
        
        @tool
        def read_document(
            file_name: Annotated[str, "File path to read the document from."],
            start: Annotated[Optional[int], "The start line. Default is 0"] = None,
            end: Annotated[Optional[int], "The end line. Default is None"] = None,
        ) -> str:
            """Read the specified document."""
            with (working_dir / file_name).open("r") as file:
                lines = file.readlines()
            if start is None:
                start = 0
            return "\n".join(lines[start:end])
        return read_document

    def _create_write_document_tool(self):
        """Create write document tool."""
        working_dir = self.working_dir
        
        @tool
        def write_document(
            content: Annotated[str, "Text content to be written into the document."],
            file_name: Annotated[str, "File path to save the document."],
        ) -> Annotated[str, "Path of the saved document file."]:
            """Create and save a text document."""
            with (working_dir / file_name).open("w") as file:
                file.write(content)
            return f"Document saved to {file_name}"
        return write_document

    def _create_edit_document_tool(self):
        """Create edit document tool."""
        working_dir = self.working_dir
        
        @tool
        def edit_document(
            file_name: Annotated[str, "Path of the document to be edited."],
            inserts: Annotated[
                Dict[int, str],
                "Dictionary where key is the line number (1-indexed) and value is the text to be inserted at that line.",
            ],
        ) -> Annotated[str, "Path of the edited document file."]:
            """Edit a document by inserting text at specific line numbers."""
            with (working_dir / file_name).open("r") as file:
                lines = file.readlines()

            sorted_inserts = sorted(inserts.items())

            for line_number, text in sorted_inserts:
                if 1 <= line_number <= len(lines) + 1:
                    lines.insert(line_number - 1, text + "\n")
                else:
                    return f"Error: Line number {line_number} is out of range."

            with (working_dir / file_name).open("w") as file:
                file.writelines(lines)

            return f"Document edited and saved to {file_name}"
        return edit_document

    def _create_python_repl_tool(self):
        """Create Python REPL tool."""
        repl = self.repl
        
        @tool
        def python_repl_tool(code: Annotated[str, "Python code to execute"]) -> str:
            """Execute Python code in a REPL environment."""
            try:
                results = repl.run(code)
            except BaseException as e:
                return f"Failed to execute code: {repr(e)}"
            return results
        return python_repl_tool
