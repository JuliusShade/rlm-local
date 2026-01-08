"""
Base Stage Interface
All RLM stages inherit from this
"""

from abc import ABC, abstractmethod
from src.rlm.state import RLMState


class Stage(ABC):
    """Abstract base class for all RLM pipeline stages"""

    @abstractmethod
    def execute(self, state: RLMState) -> RLMState:
        """
        Process state and return updated state.

        Args:
            state: Current RLM state

        Returns:
            Updated RLM state
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Stage name for logging"""
        pass
