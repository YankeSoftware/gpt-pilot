import asyncio
from core.config import LLMConfig, LLMProvider
from core.llm.convo import Convo
from core.llm.deepseek_client import DeepSeekClient
from core.llm.request_log import LLMRequestStatus

async def test_basic_chat():
    print("\nTest 1: Basic chat")
    print("-" * 40)
    config = LLMConfig(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        api_key="sk-aaa0a2708abf436dbe5d420bd36d68f5",
        base_url="https://api.deepseek.com/v1/chat/completions",
        temperature=0.7,
        extra={
            "max_tokens": 8192,
            "top_p": 0.95
        }
    )
    
    client = DeepSeekClient(config)
    convo = Convo()
    convo.user("Tell me a short joke about Python programming.")
    
    try:
        response, request_log = await client(convo)
        request_log.status = LLMRequestStatus.SUCCESS
        print(f"Response: {response}")
        print(f"Tokens used: {request_log.completion_tokens}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

async def test_system_message():
    print("\nTest 2: System message")
    print("-" * 40)
    config = LLMConfig(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        api_key="sk-aaa0a2708abf436dbe5d420bd36d68f5",
        base_url="https://api.deepseek.com/v1/chat/completions",
        temperature=0.7
    )
    
    client = DeepSeekClient(config)
    convo = Convo()
    convo.system("You are a helpful programming teacher who explains concepts clearly and concisely.")
    convo.user("Explain what a Python decorator is.")
    
    try:
        response, request_log = await client(convo)
        request_log.status = LLMRequestStatus.SUCCESS
        print(f"Response: {response}")
        print(f"Tokens used: {request_log.completion_tokens}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

async def test_conversation_memory():
    print("\nTest 3: Conversation memory")
    print("-" * 40)
    config = LLMConfig(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        api_key="sk-aaa0a2708abf436dbe5d420bd36d68f5",
        base_url="https://api.deepseek.com/v1/chat/completions",
        temperature=0.7
    )
    
    client = DeepSeekClient(config)
    convo = Convo()
    
    try:
        # First message
        convo.user("What's the capital of France?")
        response1, log1 = await client(convo)
        log1.status = LLMRequestStatus.SUCCESS
        print(f"First response: {response1}")
        
        # Follow-up question using previous context
        convo.user("What's the population of that city?")
        response2, log2 = await client(convo)
        log2.status = LLMRequestStatus.SUCCESS
        print(f"Follow-up response: {response2}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

async def test_json_mode():
    print("\nTest 4: JSON mode")
    print("-" * 40)
    config = LLMConfig(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        api_key="sk-aaa0a2708abf436dbe5d420bd36d68f5",
        base_url="https://api.deepseek.com/v1/chat/completions",
        temperature=0.7
    )
    
    client = DeepSeekClient(config)
    convo = Convo()
    convo.user("Return information about Python in JSON format with fields: name, creator, year_created, and key_features")
    
    try:
        response, request_log = await client(convo, json_mode=True)
        request_log.status = LLMRequestStatus.SUCCESS
        print(f"JSON Response: {response}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

async def run_all_tests():
    """Run all integration tests."""
    try:
        test_results = await asyncio.gather(
            test_basic_chat(),
            test_system_message(),
            test_conversation_memory(),
            test_json_mode(),
            return_exceptions=True
        )
        
        all_passed = all(
            result is True if not isinstance(result, Exception) else False 
            for result in test_results
        )
        
        if all_passed:
            print("\nAll tests passed successfully!")
        else:
            print("\nSome tests failed.")
            
        return all_passed
    except Exception as e:
        print(f"\nTests failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)