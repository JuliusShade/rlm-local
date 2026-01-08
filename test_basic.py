"""
Basic test to verify RLM system works
"""

import sys
from pathlib import Path

# Add project root to path (current directory since test is in root)
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rlm.client import OllamaClient
from src.rlm import RLMController

def test_client():
    """Test Ollama client connection"""
    print("Testing Ollama client connection...")
    try:
        client = OllamaClient()
        client.validate_connection()
        print("[PASS] Client connection successful\n")
        return True
    except Exception as e:
        print(f"[FAIL] Client connection failed: {e}\n")
        return False

def test_simple_completion():
    """Test simple completion"""
    print("Testing simple LLM completion...")
    try:
        client = OllamaClient()
        response = client.chat_completion(
            messages=[
                {"role": "user", "content": "Say 'Hello, RLM!' and nothing else."}
            ],
            max_tokens=20
        )
        print(f"Response: {response}")
        print("[PASS] Simple completion successful\n")
        return True
    except Exception as e:
        print(f"[FAIL] Simple completion failed: {e}\n")
        return False

def test_rlm_pipeline():
    """Test full RLM pipeline with a simple question"""
    print("Testing full RLM pipeline with simple question...")
    print("(This will take a minute, the model is processing...)\n")

    try:
        # Create controller with minimal logging
        controller = RLMController(config={
            "logging": {
                "enable": False  # Disable logging for cleaner test output
            }
        })

        # Simple task
        task = "What is 2 + 2?"

        # Run
        result = controller.run(task)

        # Verify we got a solution
        assert result.solution is not None, "No solution generated"
        assert result.critique is not None, "No critique generated"
        assert result.recursion_tree is not None, "No recursion tree generated"

        print(f"Solution: {result.solution[:200]}...")
        print(f"Critique Score: {result.critique.score}/100")
        print(f"Complexity: {result.recursion_tree.complexity}")
        print("[PASS] RLM pipeline successful\n")
        return True

    except Exception as e:
        print(f"[FAIL] RLM pipeline failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*80)
    print("RLM BASIC TESTS")
    print("="*80)
    print()

    results = []

    # Run tests
    results.append(("Client Connection", test_client()))
    results.append(("Simple Completion", test_simple_completion()))
    results.append(("Full RLM Pipeline", test_rlm_pipeline()))

    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{name}: {status}")

    all_passed = all(passed for _, passed in results)
    print()
    if all_passed:
        print("[PASS] ALL TESTS PASSED")
    else:
        print("[FAIL] SOME TESTS FAILED")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
