"""
Structured Logging for RLM
Provides clear visibility into recursion tree and execution flow
"""

import logging
import sys
from typing import Optional
from src.rlm.state import RecursionNode


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class RLMLogger:
    """Structured logger for RLM system"""

    def __init__(self, name: str = "RLM", level: str = "INFO", enable: bool = True):
        """
        Initialize logger.

        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            enable: Enable/disable logging
        """
        self.enable = enable
        if not enable:
            return

        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers
        self.logger.handlers = []

        # Create console handler with formatting
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))

        # Simple format
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.propagate = False

    def info(self, message: str):
        """Log info message"""
        if self.enable:
            self.logger.info(message)

    def debug(self, message: str):
        """Log debug message"""
        if self.enable:
            self.logger.debug(message)

    def warning(self, message: str):
        """Log warning message"""
        if self.enable:
            self.logger.warning(f"{Colors.YELLOW}{message}{Colors.RESET}")

    def error(self, message: str):
        """Log error message"""
        if self.enable:
            self.logger.error(f"{Colors.RED}{message}{Colors.RESET}")

    def stage(self, stage_name: str, status: str = "START"):
        """
        Log stage execution.

        Args:
            stage_name: Name of the stage
            status: START or COMPLETE
        """
        if not self.enable:
            return

        # Use ASCII-safe symbols for Windows
        start_symbol = ">" if sys.platform == 'win32' else "▶"
        check_symbol = "[OK]" if sys.platform == 'win32' else "✓"

        if status == "START":
            self.info(
                f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}"
            )
            self.info(
                f"{Colors.BOLD}{Colors.CYAN}{start_symbol} {stage_name}{Colors.RESET}"
            )
            self.info(
                f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}"
            )
        else:
            self.info(
                f"{Colors.GREEN}{check_symbol} {stage_name} complete{Colors.RESET}\n"
            )

    def recursion_tree(self, node: RecursionNode, indent: int = 0):
        """
        Print recursion tree structure.

        Args:
            node: Root recursion node
            indent: Current indentation level
        """
        if not self.enable or not node:
            return

        # Use ASCII-safe tree symbols for Windows
        if sys.platform == 'win32':
            branch = "+-"
            pipe = "|"
            arrow = "->"
        else:
            branch = "├─"
            pipe = "│"
            arrow = "→"

        prefix = "  " * indent
        depth_marker = f"{Colors.DIM}[depth {node.depth}]{Colors.RESET}"

        # Print question
        if node.complexity:
            complexity_color = Colors.YELLOW if node.complexity == "COMPLEX" else Colors.GREEN
            complexity_marker = f"{complexity_color}[{node.complexity}]{Colors.RESET}"
            self.info(f"{prefix}{branch} {depth_marker} {complexity_marker} {Colors.BRIGHT_WHITE}{node.question}{Colors.RESET}")
        else:
            self.info(f"{prefix}{branch} {depth_marker} {Colors.BRIGHT_WHITE}{node.question}{Colors.RESET}")

        # Print answer if available
        if node.answer:
            # Truncate long answers
            answer_preview = node.answer[:100] + "..." if len(node.answer) > 100 else node.answer
            self.info(f"{prefix}{pipe}  {Colors.DIM}{arrow} {answer_preview}{Colors.RESET}")

        # Print children recursively
        for child in node.children:
            self.recursion_tree(child, indent + 1)

    def critique_summary(self, score: int, gaps: list, uncertainties: list):
        """
        Print critique summary.

        Args:
            score: Confidence score
            gaps: List of gaps
            uncertainties: List of uncertainties
        """
        if not self.enable:
            return

        score_color = Colors.GREEN if score >= 85 else (Colors.YELLOW if score >= 70 else Colors.RED)

        self.info(f"\n{Colors.BOLD}Critique Summary:{Colors.RESET}")
        self.info(f"  Score: {score_color}{score}/100{Colors.RESET}")

        if gaps:
            self.info(f"  {Colors.YELLOW}Gaps identified:{Colors.RESET}")
            for gap in gaps:
                self.info(f"    - {gap}")

        if uncertainties:
            self.info(f"  {Colors.YELLOW}Uncertainties:{Colors.RESET}")
            for unc in uncertainties:
                self.info(f"    - {unc}")


# Global logger instance
_global_logger: Optional[RLMLogger] = None


def get_logger(name: str = "RLM", level: str = "INFO", enable: bool = True) -> RLMLogger:
    """
    Get or create global logger instance.

    Args:
        name: Logger name
        level: Logging level
        enable: Enable/disable logging

    Returns:
        RLMLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = RLMLogger(name, level, enable)
    return _global_logger
