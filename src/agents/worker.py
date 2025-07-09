"""
Agent Worker for Project HELIX v2.0
Multi-agent worker that polls for tasks and processes them
"""

import asyncio
import structlog
from typing import Dict

from src.sdk.agent_sdk import AgentWorker, BaseAgent
from src.agents.creative_director import CreativeDirectorAgent
from src.agents.visual_director import VisualDirectorAgent
from src.agents.narrative_architect import ChiefNarrativeArchitectAgent
from src.agents.chief_auditor import ChiefPrinciplesAuditorAgent
from src.agents.evolution_engineer import ChiefEvolutionEngineerAgent

logger = structlog.get_logger(__name__)


# DEPRECATED: All Mock Agents replaced with real AI implementations
# Removed to fix indentation errors and clean up the codebase


async def main():
    """Main entry point for the agent worker"""
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.WriteLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Initialize agents with real AI implementations
    agents: Dict[str, BaseAgent] = {
        "AGENT_1": CreativeDirectorAgent(),
        "AGENT_2": VisualDirectorAgent(),
        "AGENT_3": ChiefNarrativeArchitectAgent(),
        "AGENT_4": ChiefPrinciplesAuditorAgent(),
        "AGENT_5": ChiefEvolutionEngineerAgent()
    }
    
    # Create and start worker
    worker = AgentWorker(agents)
    
    try:
        logger.info("Starting HELIX Agent Worker")
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())