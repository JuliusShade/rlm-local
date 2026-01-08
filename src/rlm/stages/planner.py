"""
Planner Stage
Task decomposition and planning
"""

from src.rlm.stages.base import Stage
from src.rlm.state import RLMState
from src.rlm.client import OllamaClient
from src.rlm.prompts.planner_prompts import (
    PLANNER_SYSTEM,
    get_planner_user_prompt,
)


class PlannerStage(Stage):
    """Decomposes task into structured plan"""

    def __init__(self, client: OllamaClient, temperature: float = 0.5):
        """
        Initialize planner stage.

        Args:
            client: Ollama client instance
            temperature: Sampling temperature (lower for more deterministic planning)
        """
        self.client = client
        self.temperature = temperature

    @property
    def name(self) -> str:
        return "Planner"

    def execute(self, state: RLMState) -> RLMState:
        """
        Create structured plan from task.

        Args:
            state: Current state with task

        Returns:
            State with plan added
        """
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": get_planner_user_prompt(state.task)},
        ]

        plan = self.client.chat_completion(
            messages=messages,
            temperature=self.temperature,
        )

        state.plan = plan
        state.metadata["stage"] = "planner_complete"

        return state
