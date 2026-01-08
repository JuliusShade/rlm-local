"""
Critic Stage
Self-evaluation and confidence scoring
"""

import re
from src.rlm.stages.base import Stage
from src.rlm.state import RLMState, Critique
from src.rlm.client import OllamaClient
from src.rlm.prompts.critic_prompts import (
    CRITIC_SYSTEM,
    get_critic_user_prompt,
)


class CriticStage(Stage):
    """Self-evaluates solution quality and assigns confidence score"""

    def __init__(self, client: OllamaClient, temperature: float = 0.3):
        """
        Initialize critic stage.

        Args:
            client: Ollama client instance
            temperature: Sampling temperature (lower for consistent scoring)
        """
        self.client = client
        self.temperature = temperature

    @property
    def name(self) -> str:
        return "Critic"

    def execute(self, state: RLMState) -> RLMState:
        """
        Evaluate solution and assign confidence score.

        Args:
            state: State with solution

        Returns:
            State with critique added
        """
        if not state.solution:
            raise ValueError("Cannot critique: no solution found in state")

        messages = [
            {"role": "system", "content": CRITIC_SYSTEM},
            {
                "role": "user",
                "content": get_critic_user_prompt(
                    task=state.task,
                    solution=state.solution,
                    plan=state.plan or "No plan available",
                ),
            },
        ]

        critique_text = self.client.chat_completion(
            messages=messages,
            temperature=self.temperature,
        )

        # Parse critique
        critique = self._parse_critique(critique_text)
        state.critique = critique
        state.metadata["stage"] = "critic_complete"

        return state

    def _parse_critique(self, text: str) -> Critique:
        """
        Parse critique text into structured Critique object.

        Args:
            text: Raw critique text from LLM

        Returns:
            Critique object
        """
        # Extract score
        score_match = re.search(r"CONFIDENCE_SCORE:\s*(\d+)", text)
        score = int(score_match.group(1)) if score_match else 50

        # Ensure score is in valid range
        score = max(0, min(100, score))

        # Extract gaps
        gaps = []
        gaps_section = re.search(r"GAPS:(.*?)(?:UNCERTAINTIES:|REASONING:|$)", text, re.DOTALL)
        if gaps_section:
            gaps_text = gaps_section.group(1)
            if "None identified" not in gaps_text and "None" not in gaps_text:
                gaps = [
                    line.strip("- ").strip()
                    for line in gaps_text.strip().split("\n")
                    if line.strip() and line.strip() != "-"
                ]

        # Extract uncertainties
        uncertainties = []
        uncertainties_section = re.search(r"UNCERTAINTIES:(.*?)(?:REASONING:|$)", text, re.DOTALL)
        if uncertainties_section:
            uncertainties_text = uncertainties_section.group(1)
            if "None identified" not in uncertainties_text and "None" not in uncertainties_text:
                uncertainties = [
                    line.strip("- ").strip()
                    for line in uncertainties_text.strip().split("\n")
                    if line.strip() and line.strip() != "-"
                ]

        # Extract reasoning
        reasoning_match = re.search(r"REASONING:(.*?)$", text, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

        return Critique(
            score=score,
            gaps=gaps,
            uncertainties=uncertainties,
            reasoning=reasoning,
        )
