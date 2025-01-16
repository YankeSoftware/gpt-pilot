import os
import sys

print("Python paths:")
print("\n".join(f"  {p}" for p in sys.path))
print("\nCurrent directory:", os.getcwd())

try:
    from core.cli.main import run_pythagora
    print("\n✓ Successfully imported run_pythagora")
except ImportError as e:
    print(f"\n✗ Failed to import run_pythagora: {str(e)}")
    
    try:
        print("\nTrying to import core...")
        import core
        print("✓ core imported")
        
        print("\nTrying to import core.cli...")
        import core.cli
        print("✓ core.cli imported")
        
        print("\nTrying to import core.llm...")
        import core.llm
        print("✓ core.llm imported")
        
        print("\nTrying each import from main.py...")
        
        print("\nTrying: from core.agents.orchestrator import Orchestrator")
        from core.agents.orchestrator import Orchestrator
        print("✓ Orchestrator imported")
        
        print("\nTrying: from core.cli.helpers import delete_project, init, list_projects")
        from core.cli.helpers import delete_project, init, list_projects
        print("✓ CLI helpers imported")
        
        print("\nTrying: from core.config import LLMProvider")
        from core.config import LLMProvider
        print("✓ LLMProvider imported")
        
        print("\nTrying: from core.db.session import SessionManager")
        from core.db.session import SessionManager
        print("✓ SessionManager imported")
        
        print("\nTrying: from core.llm.base import BaseLLMClient")
        from core.llm.base import BaseLLMClient
        print("✓ BaseLLMClient imported")
        
    except ImportError as inner_e:
        print(f"✗ Failed at: {str(inner_e)}")
