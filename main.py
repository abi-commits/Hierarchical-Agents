#!/usr/bin/env python3
"""
Main entry point for the Hierarchical Agents system.

This script demonstrates how to use the hierarchical agent system
for complex tasks requiring both research and writing capabilities.
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from hierarchical_agents import HierarchicalSystem, Config


def main():
    """Main function demonstrating the hierarchical agent system."""
    print("🤖 Initializing Hierarchical AI Agents System...")
    
    try:
        # Initialize the system
        config = Config()
        system = HierarchicalSystem(config)
        
        print("✅ System initialized successfully!")
        print("\n" + "="*60)
        print("🚀 Running example: Research AI agents and write a report")
        print("="*60 + "\n")
        
        # Example task that requires both research and writing
        user_input = "Research AI agents and write a brief report about them."
        
        # Run the system and stream results
        for step in system.run(user_input):
            print(f"📝 Step: {step}")
            print("-" * 40)
        
        print("\n✅ Task completed successfully!")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please ensure your .env file contains valid API keys for:")
        print("- GROQ_API_KEY")
        print("- TAVILY_API_KEY")
        return 1
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return 1
    
    return 0


def demo_individual_teams():
    """Demonstrate individual team capabilities."""
    print("\n" + "="*60)
    print("🧪 Team Capability Demonstration")
    print("="*60 + "\n")
    
    try:
        config = Config()
        system = HierarchicalSystem(config)
        
        # Test research team
        print("🔍 Testing Research Team:")
        research_result = system.research_team.invoke([("user", "What is machine learning?")])
        print(f"Research result: {research_result['messages'][-1].content[:200]}...")
        
        print("\n📝 Testing Writing Team:")
        writing_result = system.writing_team.invoke([("user", "Create an outline for an AI report")])
        print(f"Writing result: {writing_result['messages'][-1].content[:200]}...")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")


if __name__ == "__main__":
    exit_code = main()
    
    # Uncomment to run team demos
    # demo_individual_teams()
    
    sys.exit(exit_code)
