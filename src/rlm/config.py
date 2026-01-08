"""
RLM Configuration
Default settings for the RLM system
"""

from typing import Dict, Any


DEFAULT_CONFIG: Dict[str, Any] = {
    # Ollama connection settings
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5-coder:14b",
        "timeout": 120,
        "max_retries": 3,
    },

    # RLM behavior settings
    "rlm": {
        "max_recursion_depth": 3,  # Max depth for recursive question decomposition
        "complexity_threshold": "auto",  # Let LM decide if simple/complex
    },

    # LLM generation parameters
    "generation": {
        "planner_temp": 0.5,      # Lower for more deterministic planning
        "reasoner_temp": 0.7,     # Moderate for balanced reasoning
        "decompose_temp": 0.4,    # Lower for consistent decomposition
        "critic_temp": 0.3,       # Lowest for consistent scoring
        "max_tokens": 2048,
    },

    # Logging settings
    "logging": {
        "enable": True,
        "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
        "show_recursion_tree": True,
    },
}


def get_config(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get configuration with optional overrides.

    Args:
        overrides: Dictionary of config values to override

    Returns:
        Merged configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()

    if overrides:
        # Deep merge overrides
        for key, value in overrides.items():
            if isinstance(value, dict) and key in config:
                config[key].update(value)
            else:
                config[key] = value

    return config
