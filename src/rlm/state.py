"""
State Management
Defines the state schema that flows through the RLM pipeline
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class Critique(BaseModel):
    """Critique from the Critic stage"""
    score: int = Field(..., ge=0, le=100, description="Confidence score 0-100")
    gaps: List[str] = Field(default_factory=list, description="Missing information")
    uncertainties: List[str] = Field(default_factory=list, description="Areas of uncertainty")
    reasoning: str = Field(default="", description="Reasoning for the score")


class RecursionNode(BaseModel):
    """Node in the recursion tree"""
    question: str
    depth: int
    complexity: Optional[str] = None  # "SIMPLE" or "COMPLEX"
    answer: Optional[str] = None
    sub_questions: List[str] = Field(default_factory=list)
    children: List['RecursionNode'] = Field(default_factory=list)


class RLMState(BaseModel):
    """
    State that flows through the RLM pipeline.
    Each stage reads and updates this state.
    """
    # Input
    task: str = Field(..., description="Original user task")

    # Planner outputs
    plan: Optional[str] = None

    # Retriever outputs
    context: List[str] = Field(default_factory=list)

    # Reasoner outputs
    solution: Optional[str] = None
    recursion_tree: Optional[RecursionNode] = None

    # Critic outputs
    critique: Optional[Critique] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


def create_initial_state(task: str) -> RLMState:
    """
    Create initial state from user task.

    Args:
        task: User's task/question

    Returns:
        Initial RLMState
    """
    return RLMState(
        task=task,
        metadata={
            "stage": "initialized",
        }
    )
