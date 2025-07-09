"""
Workflow engine for Project HELIX v2.0
Manages workflow definitions and agent execution order
"""

import json
import os
from typing import Dict, List, Optional, Set
import structlog

logger = structlog.get_logger(__name__)


class WorkflowEngine:
    """
    Manages workflow definitions and determines agent execution order
    Based on workflows.json configuration
    """
    
    def __init__(self):
        logger.debug("Creating new WorkflowEngine instance", instance_id=id(self))
        self.workflows: Dict = {}
        self.agent_definitions: Dict[str, Dict] = {}
        self.execution_order: List[str] = []
        self.agent_dependencies: Dict[str, List[str]] = {}
        
    async def load_workflows(self, workflow_file: str = "workflows.json"):
        """Load workflow definitions from JSON file"""
        logger.debug("Loading workflows", instance_id=id(self))
        try:
            workflow_path = os.path.join(os.getcwd(), workflow_file)
            
            with open(workflow_path, 'r') as f:
                self.workflows = json.load(f)
            
            # Parse agent definitions
            for agent in self.workflows.get("agents", []):
                agent_id = agent["id"]
                self.agent_definitions[agent_id] = agent
                
                # Build dependency mapping
                input_artifacts = agent.get("input_artifacts", [])
                self.agent_dependencies[agent_id] = input_artifacts
            
            # Store execution order
            self.execution_order = self.workflows.get("execution_order", [])
            
            logger.info("Workflow definitions loaded successfully", 
                       agents_count=len(self.agent_definitions),
                       execution_order=self.execution_order)
                       
        except FileNotFoundError:
            logger.error("Workflow file not found", file=workflow_file)
            raise
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in workflow file", error=str(e))
            raise
        except Exception as e:
            logger.error("Failed to load workflow definitions", error=str(e))
            raise
    
    def get_first_agent(self) -> str:
        """Get the first agent in the execution order"""
        if not self.execution_order:
            raise ValueError("No execution order defined")
        return self.execution_order[0]
    
    def get_next_agents(self, current_agent_id: str) -> List[str]:
        """
        Get the next agents that should run after the current agent completes
        Based on execution order and dependency requirements
        """
        logger.debug("Getting next agents", current_agent=current_agent_id)
        logger.debug("Current execution order", execution_order=self.execution_order)
        
        try:
            current_index = self.execution_order.index(current_agent_id)
            logger.debug("Found agent in execution order", 
                        agent_id=current_agent_id, index=current_index)
            
            # If this is the last agent in the sequence, return empty list
            if current_index >= len(self.execution_order) - 1:
                logger.debug("This is the last agent in sequence", agent_id=current_agent_id)
                return []
            
            # Return the next agent in sequence
            # In the future, this could be expanded to support parallel execution
            next_agent = self.execution_order[current_index + 1]
            logger.debug("Next agent determined", next_agent=next_agent)
            return [next_agent]
            
        except ValueError:
            logger.warning("Agent not found in execution order", agent_id=current_agent_id)
            logger.debug("Available agents in execution order", agents=self.execution_order)
            return []
    
    def get_agent_input_artifacts(self, agent_id: str) -> List[str]:
        """Get the list of input artifacts required by an agent"""
        agent_def = self.agent_definitions.get(agent_id, {})
        return agent_def.get("input_artifacts", [])
    
    def get_agent_output_artifact(self, agent_id: str) -> Optional[str]:
        """Get the output artifact name produced by an agent"""
        agent_def = self.agent_definitions.get(agent_id, {})
        return agent_def.get("output_artifact")
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict]:
        """Get complete agent information"""
        return self.agent_definitions.get(agent_id)
    
    def validate_workflow(self) -> bool:
        """Validate the workflow configuration for consistency"""
        try:
            # Check that all agents in execution order are defined
            for agent_id in self.execution_order:
                if agent_id not in self.agent_definitions:
                    logger.error("Agent in execution order not defined", agent_id=agent_id)
                    return False
            
            # Check artifact dependencies
            available_artifacts: Set[str] = set()
            
            for agent_id in self.execution_order:
                agent_def = self.agent_definitions[agent_id]
                
                # Check if required input artifacts are available
                required_artifacts = agent_def.get("input_artifacts", [])
                for artifact in required_artifacts:
                    if artifact not in available_artifacts:
                        logger.error("Required artifact not available", 
                                   agent_id=agent_id, artifact=artifact)
                        return False
                
                # Add this agent's output to available artifacts
                output_artifact = agent_def.get("output_artifact")
                if output_artifact:
                    available_artifacts.add(output_artifact)
            
            logger.info("Workflow validation passed")
            return True
            
        except Exception as e:
            logger.error("Workflow validation failed", error=str(e))
            return False
    
    def get_workflow_summary(self) -> Dict:
        """Get a summary of the current workflow configuration"""
        return {
            "workflow_version": self.workflows.get("workflow_version"),
            "description": self.workflows.get("description"),
            "agents_count": len(self.agent_definitions),
            "execution_order": self.execution_order,
            "agents": [
                {
                    "id": agent_id,
                    "name": agent_def.get("name"),
                    "description": agent_def.get("description"),
                    "input_artifacts": agent_def.get("input_artifacts", []),
                    "output_artifact": agent_def.get("output_artifact")
                }
                for agent_id, agent_def in self.agent_definitions.items()
            ]
        }
    
    def supports_parallel_execution(self) -> bool:
        """Check if the current workflow supports parallel agent execution"""
        # For now, we only support sequential execution
        # This could be expanded in the future based on dependency analysis
        return False
    
    def get_failure_handling_config(self) -> Dict:
        """Get failure handling configuration"""
        return self.workflows.get("failure_handling", {
            "max_retries": 3,
            "retry_delay_seconds": 30,
            "escalation_agent": "AGENT_5"
        })