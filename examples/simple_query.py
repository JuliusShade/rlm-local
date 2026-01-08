"""
Simple Query Example
Demonstrates RLM with a simple question that should NOT trigger recursion
"""

import sys
from pathlib import Path

# Add project root to path so we can import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rlm import RLMController


def main():
    print("=" * 80)
    print("SIMPLE QUERY EXAMPLE")
    print("=" * 80)
    print("\nThis example demonstrates a simple question that should be")
    print("answered directly without recursive decomposition.\n")

    # Create controller
    controller = RLMController()

    # Simple question
    task = "Explain the difference between deep copy and shallow copy in Python."

    # Run RLM
    result = controller.run(task)

    # The logger already prints everything, but we can access the result
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print(f"Recursion depth: {result.recursion_tree.depth if result.recursion_tree else 0}")
    print(f"Complexity assessment: {result.recursion_tree.complexity if result.recursion_tree else 'N/A'}")
    print(f"Final confidence score: {result.critique.score if result.critique else 'N/A'}")


if __name__ == "__main__":
    main()
