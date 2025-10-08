"""Main entry point for the TaleKeeper Agentic Harness."""

import argparse
import logging
import os
from dotenv import load_dotenv
from orchestrator import Orchestrator

# Load environment variables from .env file
load_dotenv()

# Basic logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the agentic harness."""
    parser = argparse.ArgumentParser(description="Agentic harness for TaleKeeper development.")
    parser.add_argument("--task", type=str, help="Specify a single task to run.")
    parser.add_argument("--single-cycle", action="store_true", help="Run a single plan-act-verify cycle and then stop.")
    args = parser.parse_args()

    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise ValueError("CLAUDE_API_KEY environment variable not set.")

    logger.info("Initializing Agentic Harness...")
    orchestrator = Orchestrator(api_key=api_key)
    orchestrator.run(initial_task=args.task, single_cycle=args.single_cycle)

if __name__ == "__main__":
    main()