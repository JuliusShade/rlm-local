"""
Code Refactoring Example
Software engineering specific use case showing recursion tree
"""

import sys
sys.path.insert(0, "../src")

from src.rlm import RLMController
import json


def main():
    print("=" * 80)
    print("CODE REFACTORING EXAMPLE")
    print("=" * 80)
    print("\nThis example demonstrates refactoring a class to follow SOLID principles.")
    print("Shows how RLM recursively breaks down the refactoring task.\n")

    # Create controller
    controller = RLMController()

    # Refactoring task
    task = """
    Refactor this UserManager class to follow SOLID principles.
    Provide the refactored code with clear separation of concerns:

    class UserManager:
        def __init__(self):
            self.db = Database()

        def create_user(self, name, email):
            user = {"name": name, "email": email}
            self.db.save(user)
            self.send_welcome_email(email)
            self.log_creation(name)

        def send_welcome_email(self, email):
            smtp_server = "smtp.gmail.com"
            # Send email via SMTP
            pass

        def log_creation(self, name):
            with open("users.log", "a") as f:
                f.write(f"User {name} created\\n")
    """

    # Run RLM
    result = controller.run(task)

    # Save detailed output to JSON
    output_file = "refactoring_output.json"
    save_result_to_json(result, output_file)

    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    if result.recursion_tree:
        print(f"Complexity: {result.recursion_tree.complexity}")
        print(f"Recursion depth: {get_max_depth(result.recursion_tree)}")
        print(f"Total LM calls made: {count_nodes(result.recursion_tree)}")

        print(f"\nSub-questions identified:")
        for i, sq in enumerate(result.recursion_tree.sub_questions, 1):
            print(f"  {i}. {sq}")

    if result.critique:
        print(f"\nConfidence Score: {result.critique.score}/100")
        if result.critique.gaps:
            print(f"Gaps: {', '.join(result.critique.gaps)}")

    print(f"\nDetailed output saved to: {output_file}")


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


def save_result_to_json(result, filename: str):
    """Save result to JSON file"""
    output = {
        "task": result.task,
        "plan": result.plan,
        "solution": result.solution,
        "critique": {
            "score": result.critique.score if result.critique else None,
            "gaps": result.critique.gaps if result.critique else [],
            "uncertainties": result.critique.uncertainties if result.critique else [],
            "reasoning": result.critique.reasoning if result.critique else "",
        },
        "recursion_summary": {
            "max_depth": get_max_depth(result.recursion_tree) if result.recursion_tree else 0,
            "total_nodes": count_nodes(result.recursion_tree) if result.recursion_tree else 0,
        }
    }

    with open(filename, "w") as f:
        json.dump(output, f, indent=2)


if __name__ == "__main__":
    main()
