"""
Recursive Reasoner Stage
Core RLM logic - implements true recursive reasoning
"""

import re
from typing import List, Tuple
from src.rlm.stages.base import Stage
from src.rlm.state import RLMState, RecursionNode
from src.rlm.client import OllamaClient
from src.rlm.prompts.reasoner_prompts import (
    COMPLEXITY_SYSTEM,
    get_complexity_user_prompt,
    DECOMPOSITION_SYSTEM,
    get_decomposition_user_prompt,
    DIRECT_ANSWER_SYSTEM,
    get_direct_answer_user_prompt,
    COMPOSITION_SYSTEM,
    get_composition_user_prompt,
)
from src.utils.logging import get_logger


class RecursiveReasonerStage(Stage):
    """
    Recursive reasoning stage.
    This is the heart of the RLM system - implements recursive LM calls.
    """

    def __init__(
        self,
        client: OllamaClient,
        max_depth: int = 3,
        reasoner_temp: float = 0.7,
        decompose_temp: float = 0.4,
    ):
        """
        Initialize recursive reasoner.

        Args:
            client: Ollama client instance
            max_depth: Maximum recursion depth
            reasoner_temp: Temperature for reasoning/answering
            decompose_temp: Temperature for decomposition (lower = more consistent)
        """
        self.client = client
        self.max_depth = max_depth
        self.reasoner_temp = reasoner_temp
        self.decompose_temp = decompose_temp
        self.logger = get_logger()

    @property
    def name(self) -> str:
        return "RecursiveReasoner"

    def execute(self, state: RLMState) -> RLMState:
        """
        Execute recursive reasoning on the task.

        Args:
            state: State with task and context

        Returns:
            State with solution and recursion tree
        """
        # Start recursive reasoning from the main task
        solution, tree = self._recursive_reason(
            question=state.task,
            context=state.context,
            depth=0,
        )

        state.solution = solution
        state.recursion_tree = tree
        state.metadata["stage"] = "reasoner_complete"

        return state

    def _recursive_reason(
        self,
        question: str,
        context: List[str],
        depth: int,
    ) -> Tuple[str, RecursionNode]:
        """
        Recursively solve questions by decomposing complex ones.

        This is the core RLM algorithm.

        Args:
            question: Question to answer
            context: Available context
            depth: Current recursion depth

        Returns:
            Tuple of (answer, recursion_node)
        """
        self.logger.info(f"{'  ' * depth}[depth {depth}] Processing: {question[:80]}...")

        # Create node for this question
        node = RecursionNode(
            question=question,
            depth=depth,
        )

        # Base case 1: Max depth reached
        if depth >= self.max_depth:
            self.logger.info(f"{'  ' * depth}→ Max depth reached, answering directly")
            answer = self._direct_answer(question, context)
            node.complexity = "MAX_DEPTH"
            node.answer = answer
            return answer, node

        # Base case 2: Simple question
        complexity = self._assess_complexity(question)
        node.complexity = complexity

        if complexity == "SIMPLE":
            self.logger.info(f"{'  ' * depth}→ Assessed as SIMPLE, answering directly")
            answer = self._direct_answer(question, context)
            node.answer = answer
            return answer, node

        # Recursive case: Complex question - decompose and recurse
        self.logger.info(f"{'  ' * depth}→ Assessed as COMPLEX, decomposing...")

        sub_questions = self._decompose_question(question, context)
        node.sub_questions = sub_questions

        self.logger.info(f"{'  ' * depth}→ Decomposed into {len(sub_questions)} sub-questions")

        # Recursively answer each sub-question
        sub_answers = []
        for i, sub_q in enumerate(sub_questions, 1):
            self.logger.info(f"{'  ' * depth}→ Sub-question {i}/{len(sub_questions)}")

            sub_answer, sub_node = self._recursive_reason(
                question=sub_q,
                context=context,
                depth=depth + 1,
            )

            sub_answers.append((sub_q, sub_answer))
            node.children.append(sub_node)

        # Compose sub-answers into final answer
        self.logger.info(f"{'  ' * depth}→ Composing {len(sub_answers)} sub-answers")
        final_answer = self._compose_answers(question, sub_answers)
        node.answer = final_answer

        return final_answer, node

    def _assess_complexity(self, question: str) -> str:
        """
        Assess if question is SIMPLE or COMPLEX.

        Args:
            question: Question to assess

        Returns:
            "SIMPLE" or "COMPLEX"
        """
        messages = [
            {"role": "system", "content": COMPLEXITY_SYSTEM},
            {"role": "user", "content": get_complexity_user_prompt(question)},
        ]

        response = self.client.chat_completion(
            messages=messages,
            temperature=0.3,  # Low temperature for consistent assessment
            max_tokens=10,
        )

        # Parse response (should be just "SIMPLE" or "COMPLEX")
        response_clean = response.strip().upper()

        if "COMPLEX" in response_clean:
            return "COMPLEX"
        else:
            return "SIMPLE"

    def _decompose_question(self, question: str, context: List[str]) -> List[str]:
        """
        Decompose complex question into simpler sub-questions.

        Args:
            question: Complex question to decompose
            context: Available context

        Returns:
            List of sub-questions
        """
        messages = [
            {"role": "system", "content": DECOMPOSITION_SYSTEM},
            {"role": "user", "content": get_decomposition_user_prompt(question, context)},
        ]

        response = self.client.chat_completion(
            messages=messages,
            temperature=self.decompose_temp,
        )

        # Parse sub-questions
        sub_questions = []
        for line in response.split("\n"):
            # Look for "SUB-QUESTION N:" pattern
            match = re.search(r"SUB-QUESTION\s+\d+:\s*(.+)", line, re.IGNORECASE)
            if match:
                sub_q = match.group(1).strip()
                if sub_q:
                    sub_questions.append(sub_q)

        # Fallback: if parsing failed, try to extract any numbered list
        if not sub_questions:
            for line in response.split("\n"):
                # Look for numbered items
                match = re.search(r"^\d+[\.\)]\s*(.+)", line)
                if match:
                    sub_q = match.group(1).strip()
                    if sub_q:
                        sub_questions.append(sub_q)

        # Ensure we have at least one sub-question
        if not sub_questions:
            self.logger.warning("Failed to parse sub-questions, using original question")
            sub_questions = [question]

        # Limit to 5 sub-questions max
        return sub_questions[:5]

    def _direct_answer(self, question: str, context: List[str]) -> str:
        """
        Directly answer a simple question.

        Args:
            question: Question to answer
            context: Available context

        Returns:
            Answer string
        """
        messages = [
            {"role": "system", "content": DIRECT_ANSWER_SYSTEM},
            {"role": "user", "content": get_direct_answer_user_prompt(question, context)},
        ]

        answer = self.client.chat_completion(
            messages=messages,
            temperature=self.reasoner_temp,
        )

        return answer

    def _compose_answers(
        self,
        original_question: str,
        sub_answers: List[Tuple[str, str]],
    ) -> str:
        """
        Compose sub-answers into coherent final answer.

        Args:
            original_question: Original question
            sub_answers: List of (sub_question, sub_answer) tuples

        Returns:
            Composed final answer
        """
        messages = [
            {"role": "system", "content": COMPOSITION_SYSTEM},
            {
                "role": "user",
                "content": get_composition_user_prompt(original_question, sub_answers),
            },
        ]

        composed_answer = self.client.chat_completion(
            messages=messages,
            temperature=self.reasoner_temp,
        )

        return composed_answer
