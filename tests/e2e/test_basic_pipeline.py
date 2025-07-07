# tests/e2e/test_basic_pipeline.py
import pytest
import asyncio
import os
import json
from unittest.mock import AsyncMock, patch

# Import database manager and models
from database.connection import db_manager
from database.models import JobStatus, TaskStatus, TaskInput, TaskOutput

# Import agents
from agents.creative_director import CreativeDirectorAgent
from agents.visual_director import VisualDirectorAgent
from agents.narrative_architect import ChiefNarrativeArchitectAgent

# For schema validation
from jsonschema import validate

# --- Fixtures ---

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function", autouse=True)
async def setup_test_env():
    """Setup test environment with database connection."""
    # Use existing Docker database
    os.environ['POSTGRES_DB'] = 'helix'
    os.environ['POSTGRES_USER'] = 'helix_user'
    os.environ['POSTGRES_PASSWORD'] = 'helix_secure_password_2024'
    os.environ['POSTGRES_HOST'] = 'localhost'
    os.environ['POSTGRES_PORT'] = '5432'
    
    # Force db_manager to rebuild connection URL with new env vars
    db_manager.pool = None
    db_manager.connection_url = db_manager._build_connection_url()
    
    # Connect to database
    await db_manager.connect()
    
    yield
    
    # Cleanup after test
    if db_manager.pool:
        # Clear test data
        await db_manager.execute("DELETE FROM artifacts WHERE task_id IN (SELECT id FROM tasks WHERE job_id > 100000)")
        await db_manager.execute("DELETE FROM tasks WHERE job_id > 100000")
        await db_manager.execute("DELETE FROM jobs WHERE id > 100000")

@pytest.fixture(autouse=True)
def mock_base_agent_methods():
    """Mock BaseAgent methods that interact with database."""
    with patch('sdk.agent_sdk.BaseAgent.log_system_event', new_callable=AsyncMock):
        with patch('sdk.agent_sdk.BaseAgent.get_agent_prompt', new_callable=AsyncMock) as mock_prompt:
            # Return default prompts for each agent
            async def get_prompt_for_agent(self):
                if self.agent_id == "AGENT_1":
                    return "You are a Creative Director AI agent."
                elif self.agent_id == "AGENT_2":
                    return "You are a Visual Director AI agent."
                elif self.agent_id == "AGENT_3":
                    return "You are a Chief Narrative Architect AI agent."
                return "Default prompt"
            
            mock_prompt.side_effect = get_prompt_for_agent
            yield

# --- Basic Tests ---

@pytest.mark.asyncio
async def test_agent_1_process_task():
    """Test AGENT_1 (Creative Director) basic functionality."""
    # Create a test job
    job_id = 100001  # Use high ID to avoid conflicts
    
    # Insert test job
    await db_manager.execute(
        """
        INSERT INTO jobs (id, status, initial_request, session_id)
        VALUES ($1, $2, $3, $4)
        """,
        job_id, JobStatus.IN_PROGRESS, {"chat_input": "Test creative brief"}, "test_session"
    )
    
    # Create task input
    task_input = TaskInput(
        artifacts=[],
        params={"chat_input": "Create a presentation for a new AI product", "session_id": "test_session"}
    )
    
    # Create agent instance
    agent = CreativeDirectorAgent()
    
    # Mock AI client to avoid external API calls
    with patch('ai_clients.client_factory.AIClientFactory.create_client') as mock_factory:
        mock_client = AsyncMock()
        mock_client.generate_response.return_value = {
            "content": json.dumps({
                "project_overview": {
                    "title": "AI Product Launch",
                    "type": "presentation",
                    "description": "Launch presentation for new AI product",
                    "key_themes": ["innovation", "technology", "future"]
                },
                "objectives": {
                    "primary_goal": "Introduce new AI product to market",
                    "secondary_goals": ["Build awareness", "Generate leads"],
                    "success_metrics": ["Audience engagement", "Lead conversion"]
                },
                "target_audience": {
                    "primary_audience": "Tech professionals",
                    "audience_characteristics": {
                        "demographics": "25-45, tech-savvy",
                        "psychographics": "Innovation-focused",
                        "behavior_patterns": "Early adopters",
                        "pain_points": "Complex workflows"
                    }
                },
                "creative_strategy": {
                    "tone_of_voice": "Professional yet approachable",
                    "key_messages": ["Simplify with AI", "Future is now"],
                    "creative_approach": "Modern, clean design"
                },
                "content_requirements": {
                    "content_types": ["Slides", "Demos"],
                    "information_hierarchy": {"Primary": 1, "Secondary": 2},
                    "call_to_action": "Try our beta"
                },
                "metadata": {
                    "created_by": "AGENT_1",
                    "version": "1.0",
                    "ai_model": "test-model",
                    "confidence_score": 0.95,
                    "processing_notes": "Test generation"
                }
            }),
            "model": "test-model",
            "provider": "test",
            "usage": {"total_tokens": 100}
        }
        mock_factory.create_client.return_value = mock_client
        
        # Process task
        result = await agent.process_task(task_input)
    
    # Verify result
    assert result is not None
    assert isinstance(result, TaskOutput)
    assert result.schema_id == "CreativeBrief_v1.0"
    assert "project_overview" in result.payload
    assert result.payload["project_overview"]["title"] == "AI Product Launch"
    
    print("✅ AGENT_1 basic test passed")


@pytest.mark.asyncio
async def test_agent_2_process_task():
    """Test AGENT_2 (Visual Director) basic functionality."""
    # Create mock creative brief artifact
    creative_brief = {
        "project_overview": {
            "title": "Test Project",
            "type": "presentation",
            "description": "Test description",
            "key_themes": ["modern", "professional"]
        },
        "target_audience": {
            "primary_audience": "Business professionals"
        },
        "creative_strategy": {
            "tone_of_voice": "Professional",
            "key_messages": ["Innovation", "Quality"],
            "creative_approach": "Clean and modern"
        }
    }
    
    # Mock get_artifacts to return the creative brief
    with patch.object(VisualDirectorAgent, 'get_artifacts', new_callable=AsyncMock) as mock_get_artifacts:
        mock_get_artifacts.return_value = {
            "creative_brief": {
                "payload": creative_brief,
                "schema_id": "CreativeBrief_v1.0"
            }
        }
        
        # Create task input
        task_input = TaskInput(
            artifacts=[{"name": "creative_brief", "source_task_id": 1}],
            params={}
        )
        
        # Create agent instance
        agent = VisualDirectorAgent()
        
        # Mock AI client
        with patch('ai_clients.client_factory.AIClientFactory.create_client') as mock_factory:
            mock_client = AsyncMock()
            mock_client.generate_response.return_value = {
                "content": json.dumps({
                    "visual_themes": [
                        {
                            "theme_name": "Direct Professional",
                            "design_philosophy": "Clean and direct approach",
                            "color_and_typography": "Blue palette with sans-serif",
                            "layout_and_graphics": "Grid-based layout",
                            "key_slide_archetype": "Title with subtitle"
                        },
                        {
                            "theme_name": "Modern Innovation",
                            "design_philosophy": "Forward-thinking design",
                            "color_and_typography": "Gradient colors with modern fonts",
                            "layout_and_graphics": "Asymmetric layouts",
                            "key_slide_archetype": "Hero image with text"
                        },
                        {
                            "theme_name": "Bold Statement",
                            "design_philosophy": "High impact visuals",
                            "color_and_typography": "High contrast with bold fonts",
                            "layout_and_graphics": "Full-bleed images",
                            "key_slide_archetype": "Statement slides"
                        }
                    ],
                    "style_direction": "Professional and modern",
                    "color_palette": ["#0066CC", "#00AA44", "#FF6600"],
                    "typography": {
                        "primary_font": "Inter",
                        "font_scale": "1.25"
                    },
                    "layout_principles": ["Clear hierarchy", "Consistent spacing"],
                    "visual_elements": {
                        "iconography": "Line icons"
                    },
                    "metadata": {
                        "created_by": "AGENT_2",
                        "version": "1.0",
                        "ai_model": "test-model",
                        "design_confidence": 0.92,
                        "processing_notes": "Test generation"
                    }
                }),
                "model": "test-model",
                "provider": "test",
                "usage": {"total_tokens": 200}
            }
            mock_factory.create_client.return_value = mock_client
            
            # Process task
            result = await agent.process_task(task_input)
        
        # Verify result
        assert result is not None
        assert isinstance(result, TaskOutput)
        assert result.schema_id == "VisualExplorations_v1.0"
        assert "visual_themes" in result.payload
        assert len(result.payload["visual_themes"]) == 3
        
        print("✅ AGENT_2 basic test passed")


@pytest.mark.asyncio
async def test_agent_3_process_task():
    """Test AGENT_3 (Chief Narrative Architect) basic functionality."""
    # Create mock artifacts
    creative_brief = {
        "project_overview": {"title": "Test Project"},
        "objectives": {"primary_goal": "Test goal"},
        "target_audience": {"primary_audience": "Test audience"}
    }
    
    visual_explorations = {
        "visual_themes": [
            {"theme_name": "Theme A"},
            {"theme_name": "Theme B"},
            {"theme_name": "Theme C"}
        ]
    }
    
    # Mock get_artifacts
    with patch.object(ChiefNarrativeArchitectAgent, 'get_artifacts', new_callable=AsyncMock) as mock_get_artifacts:
        mock_get_artifacts.return_value = {
            "creative_brief": {"payload": creative_brief, "schema_id": "CreativeBrief_v1.0"},
            "visual_explorations": {"payload": visual_explorations, "schema_id": "VisualExplorations_v1.0"}
        }
        
        # Create task input
        task_input = TaskInput(
            artifacts=[
                {"name": "creative_brief", "source_task_id": 1},
                {"name": "visual_explorations", "source_task_id": 2}
            ],
            params={}
        )
        
        # Create agent instance
        agent = ChiefNarrativeArchitectAgent()
        
        # Mock AI client
        with patch('ai_clients.client_factory.AIClientFactory.create_client') as mock_factory:
            mock_client = AsyncMock()
            mock_client.generate_response.return_value = {
                "content": json.dumps({
                    "strategic_choice": {
                        "chosen_theme_name": "Theme A",
                        "chosen_narrative_framework": "Problem-Solution-Benefit",
                        "reasoning": "Best fits the audience",
                        "rejected_options": []
                    },
                    "presentation_blueprint": [
                        {
                            "slide_number": 1,
                            "logic_unit_purpose": "Introduction",
                            "layout": "Title_Slide",
                            "elements": {"title": "Welcome"},
                            "speaker_notes": {"speech": "Hello", "guide_note": "Warm greeting"}
                        }
                    ],
                    "metadata": {
                        "created_by": "AGENT_3",
                        "version": "1.0",
                        "total_slides": 1,
                        "narrative_complexity": "moderate",
                        "target_audience_level": "intermediate",
                        "presentation_style": "professional",
                        "confidence_score": 0.9,
                        "ai_model": "test-model",
                        "processing_notes": "Test generation"
                    }
                }),
                "model": "test-model",
                "provider": "test",
                "usage": {"total_tokens": 300}
            }
            mock_factory.create_client.return_value = mock_client
            
            # Process task
            result = await agent.process_task(task_input)
        
        # Verify result
        assert result is not None
        assert isinstance(result, TaskOutput)
        assert result.schema_id == "PresentationBlueprint_v1.0"
        assert "strategic_choice" in result.payload
        assert "presentation_blueprint" in result.payload
        
        print("✅ AGENT_3 basic test passed")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])