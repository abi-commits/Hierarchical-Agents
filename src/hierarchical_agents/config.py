"""
Configuration management for the Hierarchical Agents system.
"""

import os
from typing import Optional
from pydantic import SecretStr
from dotenv import load_dotenv


class Config:
    """Configuration class for managing API keys and environment settings."""
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        load_dotenv()
        
        # API Keys
        self.openai_api_key = SecretStr(os.getenv("OPENAI_API_KEY", ""))
        self.tavily_api_key = SecretStr(os.getenv("TAVILY_API_KEY", ""))
        self.groq_api_key = SecretStr(os.getenv("GROQ_API_KEY", ""))
        
        # Environment settings
        os.environ["USER_AGENT"] = "HierarchicalAgents/1.0"
        
        # Model configuration
        self.default_model = "llama-3.3-70b-versatile"
        self.temperature = 0
        self.recursion_limit = 150
        
    def validate(self) -> bool:
        """Validate that required API keys are available."""
        required_keys = [self.groq_api_key, self.tavily_api_key]
        return all(key.get_secret_value() for key in required_keys)
    
    def get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key if available."""
        return self.openai_api_key.get_secret_value() if self.openai_api_key.get_secret_value() else None
    
    def get_groq_key(self) -> Optional[str]:
        """Get Groq API key if available."""
        return self.groq_api_key.get_secret_value() if self.groq_api_key.get_secret_value() else None
    
    def get_tavily_key(self) -> Optional[str]:
        """Get Tavily API key if available."""
        return self.tavily_api_key.get_secret_value() if self.tavily_api_key.get_secret_value() else None
