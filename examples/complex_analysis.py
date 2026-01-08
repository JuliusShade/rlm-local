"""
Complex Analysis Example
Demonstrates RLM with a complex question that SHOULD trigger recursive decomposition
"""

import sys
sys.path.insert(0, "../src")

from src.rlm import RLMController


def main():
    print("=" * 80)
    print("COMPLEX ANALYSIS EXAMPLE")
    print("=" * 80)
    print("\nThis example demonstrates a complex question that should be")
    print("recursively decomposed into simpler sub-questions.\n")

    # Create controller
    controller = RLMController()

    # Complex question
    task = """
    Analyze the following Python code and identify potential issues,
    suggest improvements, and explain the design patterns used:

    class UserManager:
        def __init__(self):
            self.db = Database()

        def create_user(self, name, email):
            user = {"name": name, "email": email}
            self.db.save(user)
            self.send_welcome_email(email)
            self.log_creation(name)

        def send_welcome_email(self, email):
            # Email sending logic
            pass

        def log_creation(self, name):
            print(f"User {name} created")
    """

    # Run RLM
    result = controller.run(task)

    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    if result.recursion_tree:
        print(f"Root complexity: {result.recursion_tree.complexity}")
        print(f"Number of sub-questions: {len(result.recursion_tree.sub_questions)}")
        print(f"Total recursion nodes: {count_nodes(result.recursion_tree)}")
        print(f"Max depth reached: {get_max_depth(result.recursion_tree)}")

    print(f"Final confidence score: {result.critique.score if result.critique else 'N/A'}")


def count_nodes(node) -> int:
    """Count total nodes in recursion tree"""
    if not node:
        return 0
    count = 1
    for child in node.children:
        count += count_nodes(child)
    return count


def get_max_depth(node, current_max=0) -> int:
    """Get maximum depth in recursion tree"""
    if not node:
        return current_max
    current_max = max(current_max, node.depth)
    for child in node.children:
        current_max = max(current_max, get_max_depth(child, current_max))
    return current_max


if __name__ == "__main__":
    main()
