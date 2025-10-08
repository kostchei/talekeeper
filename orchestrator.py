"""The Orchestrator for the TaleKeeper Agentic Harness."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrates the perceive-plan-act-verify loop for the agent."""

    def __init__(self, api_key: str):
        """
        Initializes the Orchestrator.

        Args:
            api_key: The API key for the LLM service.
        """
        self.api_key = api_key
        # TODO: Initialize Agent, Toolbelt, KnowledgeBase, StateManager
        logger.info("Orchestrator initialized.")

    def run(self, initial_task: Optional[str] = None, single_cycle: bool = False):
        """
        Starts the main agentic loop.

        Args:
            initial_task: An optional specific task to start with.
            single_cycle: If True, runs only one full cycle.
        """
        logger.info("Starting agentic loop...")
        if single_cycle:
            logger.info("Running in single-cycle mode.")

        # TODO: Implement the main loop:
        # 1. Select task from ToDo list or use initial_task
        # 2. Gather context (Knowledge Base)
        # 3. Call Agent to create a plan
        # 4. Execute plan using Toolbelt
        # 5. Verify results
        # 6. Feed back results to agent and iterate or commit.
        print("Harness loop is not yet implemented. Exiting.")