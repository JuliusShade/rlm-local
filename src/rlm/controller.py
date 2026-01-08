"""
RLM Controller
Orchestrates the RLM pipeline
"""

from typing import Dict, Any
from src.rlm.client import OllamaClient
from src.rlm.state import RLMState, create_initial_state
from src.rlm.config import get_config
from src.rlm.stages.planner import PlannerStage
from src.rlm.stages.retriever import RetrieverStage
from src.rlm.stages.reasoner import RecursiveReasonerStage
from src.rlm.stages.critic import CriticStage
from src.utils.logging import get_logger


class RLMController:
    """
    Orchestrates the RLM pipeline.
    Runs: Planner → Retriever → RecursiveReasoner → Critic
    """

    def __init__(
        self,
        client: OllamaClient = None,
        config: Dict[str, Any] = None,
    ):
        """
        Initialize RLM controller.

        Args:
            client: Ollama client (if None, creates from config)
            config: Configuration overrides
        """
        # Get configuration
        self.config = get_config(config)

        # Create client if not provided
        if client is None:
            self.client = OllamaClient(
                base_url=self.config["ollama"]["base_url"],
                model=self.config["ollama"]["model"],
                timeout=self.config["ollama"]["timeout"],
                max_retries=self.config["ollama"]["max_retries"],
            )
        else:
            self.client = client

        # Initialize logger
        self.logger = get_logger(
            level=self.config["logging"]["level"],
            enable=self.config["logging"]["enable"],
        )

        # Initialize stages
        self.planner = PlannerStage(
            client=self.client,
            temperature=self.config["generation"]["planner_temp"],
        )

        self.retriever = RetrieverStage()

        self.reasoner = RecursiveReasonerStage(
            client=self.client,
            max_depth=self.config["rlm"]["max_recursion_depth"],
            reasoner_temp=self.config["generation"]["reasoner_temp"],
            decompose_temp=self.config["generation"]["decompose_temp"],
        )

        self.critic = CriticStage(
            client=self.client,
            temperature=self.config["generation"]["critic_temp"],
        )

    def run(self, task: str) -> RLMState:
        """
        Execute RLM pipeline on a task.

        Args:
            task: User's task/question

        Returns:
            Final RLM state with solution and critique
        """
        self.logger.info(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
        self.logger.info(f"{Colors.BOLD}RLM PIPELINE STARTING{Colors.RESET}")
        self.logger.info(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        self.logger.info(f"\nTask: {Colors.BRIGHT_WHITE}{task}{Colors.RESET}\n")

        # Create initial state
        state = create_initial_state(task)

        # Run pipeline stages
        state = self._run_stage(self.planner, state)
        state = self._run_stage(self.retriever, state)
        state = self._run_stage(self.reasoner, state)
        state = self._run_stage(self.critic, state)

        # Log final results
        self._log_final_results(state)

        return state

    def _run_stage(self, stage, state: RLMState) -> RLMState:
        """
        Run a single stage with logging.

        Args:
            stage: Stage to run
            state: Current state

        Returns:
            Updated state
        """
        self.logger.stage(stage.name, status="START")

        try:
            state = stage.execute(state)
            self.logger.stage(stage.name, status="COMPLETE")
            return state

        except Exception as e:
            self.logger.error(f"Error in {stage.name}: {e}")
            raise

    def _log_final_results(self, state: RLMState):
        """
        Log final results including recursion tree and critique.

        Args:
            state: Final state
        """
        self.logger.info(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
        self.logger.info(f"{Colors.BOLD}FINAL RESULTS{Colors.RESET}")
        self.logger.info(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")

        # Show recursion tree if enabled
        if self.config["logging"]["show_recursion_tree"] and state.recursion_tree:
            self.logger.info(f"{Colors.BOLD}Recursion Tree:{Colors.RESET}")
            self.logger.recursion_tree(state.recursion_tree)
            self.logger.info("")

        # Show solution
        self.logger.info(f"{Colors.BOLD}Solution:{Colors.RESET}")
        self.logger.info(state.solution)
        self.logger.info("")

        # Show critique
        if state.critique:
            self.logger.critique_summary(
                score=state.critique.score,
                gaps=state.critique.gaps,
                uncertainties=state.critique.uncertainties,
            )

        self.logger.info(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}\n")


# Import colors for logging
from src.utils.logging import Colors
