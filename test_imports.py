print("Attempting imports...")

try:
    print("Importing core...")
    import core
    print("✓ core imported")

    print("\nImporting core.llm...")
    import core.llm
    print("✓ core.llm imported")

    print("\nImporting core.llm.base...")
    import core.llm.base
    print("✓ core.llm.base imported")
    
    print("\nImporting BaseLLMClient...")
    from core.llm.base import BaseLLMClient
    print("✓ BaseLLMClient imported")
    
    print("\nImporting DeepSeekClient...")
    from core.llm.deepseek_client import DeepSeekClient
    print("✓ DeepSeekClient imported")
    
    print("\nAll imports successful!")

except ImportError as e:
    print(f"\nError importing: {str(e)}")
    print(f"Module name: {e.name}")
    if e.path:
        print(f"Module path: {e.path}")
    if hasattr(e, "msg"):
        print(f"Message: {e.msg}")
