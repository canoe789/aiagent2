# tests/e2e/test_helix_pipeline.py
import pytest
import httpx
import asyncio
import os
import json
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

# Import the FastAPI app instance
from api.main import app 

# Import database manager and models
from database.connection import db_manager
from database.models import JobStatus, TaskStatus, Job, Task, Artifact, TaskInput, TaskOutput

# Import AI client factory and agents
from ai_clients.client_factory import AIClientFactory
from agents.creative_director import CreativeDirectorAgent
from agents.visual_director import VisualDirectorAgent
from agents.narrative_architect import ChiefNarrativeArchitectAgent

# For schema validation
from jsonschema import validate, ValidationError

# --- Global Setup for Schemas ---
SCHEMAS = {}
# Adjust SCHEMA_DIR to be relative to the project root
# Assuming tests/e2e/test_helix_pipeline.py is at /workspace/Projects/aiagent/tests/e2e/
# And schemas are at /workspace/Projects/aiagent/schemas/
SCHEMA_ROOT_DIR = os.path.join(os.path.dirname(__file__), '../../schemas')

def load_schema(schema_name_with_version):
    """Loads a JSON schema from the schemas directory."""
    file_path = os.path.join(SCHEMA_ROOT_DIR, f"{schema_name_with_version}.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Schema file not found: {file_path}")
    with open(file_path, 'r') as f:
        return json.load(f)

# Load all necessary schemas for validation
SCHEMAS["CreativeBrief_v1.0"] = load_schema("CreativeBrief_v1.0")
SCHEMAS["VisualExplorations_v1.0"] = load_schema("VisualExplorations_v1.0")
SCHEMAS["PresentationBlueprint_v1.0"] = load_schema("PresentationBlueprint_v1.0")

# --- Fixtures ---

@pytest.fixture(scope="session")
def anyio_backend():
    """Required for pytest-asyncio to work with httpx."""
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """
    Fixture to set up and tear down a clean test database for the entire test session.
    This requires a PostgreSQL database named 'helix_test' to exist and be accessible.
    It drops and recreates the public schema, then runs the init.sql script.
    """
    # Override environment variables for test database
    os.environ['POSTGRES_DB'] = 'helix_test'
    os.environ['POSTGRES_USER'] = 'helix_user'
    os.environ['POSTGRES_PASSWORD'] = 'helix_secure_password_2024'
    os.environ['POSTGRES_HOST'] = 'localhost'
    os.environ['POSTGRES_PORT'] = '5432'

    # Ensure db_manager uses the test connection details
    db_manager._build_connection_url() # Rebuild URL with test env vars

    try:
        # Connect to the database
        await db_manager.connect()

        # Drop all tables and recreate schema to ensure a clean slate
        # This also drops ENUM types, so they need to be recreated before init.sql
        await db_manager.execute("""
            DROP SCHEMA public CASCADE;
            CREATE SCHEMA public;
            GRANT ALL ON SCHEMA public TO public;
            -- Re-create ENUM types as they are dropped with the schema
            CREATE TYPE job_status AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED');
            CREATE TYPE task_status AS ENUM ('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'RETRYING');
        """)
        
        # Run the init.sql script
        init_sql_path = os.path.join(os.path.dirname(__file__), '../../database/init.sql')
        with open(init_sql_path, 'r') as f:
            sql_script = f.read()
            # Filter out '\c helix;' command as it's not valid in asyncpg execute
            # Also filter out CREATE EXTENSION if it causes issues (often needs superuser)
            filtered_script_lines = [
                line for line in sql_script.splitlines() 
                if not line.strip().startswith('\\c') and not line.strip().startswith('CREATE EXTENSION')
            ]
            # Add CREATE EXTENSION back if needed, but often handled by test DB setup
            # For simplicity, we'll assume the test DB has uuid-ossp enabled or it's not strictly needed for these tests.
            
            await db_manager.execute("\n".join(filtered_script_lines))
        
        print("\nTest database initialized.")
        yield
    except Exception as e:
        pytest.fail(f"Failed to set up test database: {e}")
    finally:
        # Disconnect from the database
        if db_manager.pool:
            await db_manager.disconnect()
        print("Test database disconnected.")

@pytest.fixture(autouse=True)
async def clear_tables_after_each_test():
    """
    Clears data from tables after each test to ensure isolation.
    This runs after each test function. Agent prompts are not cleared as they are static defaults.
    """
    yield
    # Ensure we are connected
    if not db_manager.pool:
        await db_manager.connect()

    async with db_manager.transaction() as conn:
        # Delete from tables that are modified by tests, in reverse dependency order
        await conn.execute("DELETE FROM artifacts;")
        await conn.execute("DELETE FROM tasks;")
        await conn.execute("DELETE FROM jobs;")
        await conn.execute("DELETE FROM system_logs;") # Clear system logs generated during tests
        
        # Reset sequences for auto-incrementing IDs
        await conn.execute("ALTER SEQUENCE jobs_id_seq RESTART WITH 1;")
        await conn.execute("ALTER SEQUENCE tasks_id_seq RESTART WITH 1;")
        await conn.execute("ALTER SEQUENCE artifacts_id_seq RESTART WITH 1;")
        await conn.execute("ALTER SEQUENCE system_logs_id_seq RESTART WITH 1;")
        print("Tables cleared and sequences reset.")


@pytest.fixture
async def client():
    """FastAPI test client using httpx."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_ai_client(mocker):
    """
    Mocks the AIClientFactory to return a mock AI client.
    The generate_response method of this mock client can be configured per test.
    """
    mock_client_instance = AsyncMock()
    mocker.patch.object(AIClientFactory, 'create_client', return_value=mock_client_instance)
    return mock_client_instance

@pytest.fixture(autouse=True)
def mock_base_agent_logging(mocker):
    """
    Mocks BaseAgent's log_system_event to prevent actual DB writes for logs
    during tests, focusing on core pipeline logic.
    get_agent_prompt and get_artifacts are allowed to use the real DB.
    """
    # Patching the method on the BaseAgent class directly
    mocker.patch('sdk.agent_sdk.BaseAgent.log_system_event', new_callable=AsyncMock)

# --- Helper for Orchestrator Simulation ---
async def simulate_agent_processing(job_id: int, agent_id: str, db_manager):
    """
    Simulates the AgentWorker processing a single task for a given agent.
    This involves:
    1. Fetching the PENDING task for the agent_id and job_id.
    2. Instantiating the correct agent.
    3. Calling the agent's process_task method.
    4. Updating the task status and saving artifacts.
    5. Validating the output against its schema.
    6. Updating the job status if the task fails.
    """
    # 1. Fetch the PENDING task
    task_record = await db_manager.fetch_one(
        "SELECT * FROM tasks WHERE job_id = $1 AND agent_id = $2 AND status = 'PENDING'",
        job_id, agent_id
    )
    if not task_record:
        # If no pending task, it means the previous step might have failed or logic is off
        raise ValueError(f"No PENDING task found for job_id={job_id}, agent_id={agent_id}. "
                         f"Current tasks for job {job_id}: {await db_manager.fetch_all('SELECT id, agent_id, status FROM tasks WHERE job_id = $1', job_id)}")

    task = Task.model_validate(task_record)
    
    # Convert raw input_data dict from DB to TaskInput Pydantic model for agent
    task_input_for_agent = TaskInput.model_validate(task.input_data)

    # 2. Instantiate the correct agent
    agent_map = {
        "AGENT_1": CreativeDirectorAgent,
        "AGENT_2": VisualDirectorAgent,
        "AGENT_3": ChiefNarrativeArchitectAgent,
    }
    agent_instance = agent_map.get(agent_id)()

    try:
        # Update task status to IN_PROGRESS
        await db_manager.execute(
            "UPDATE tasks SET status = $1, started_at = CURRENT_TIMESTAMP WHERE id = $2",
            TaskStatus.IN_PROGRESS, task.id
        )
        
        # Process the task
        task_output: TaskOutput = await agent_instance.process_task(task_input=task_input_for_agent)

        # 5. Validate the output against its schema
        schema_id = task_output.schema_id
        if schema_id not in SCHEMAS:
            raise ValueError(f"Unknown schema_id: {schema_id}. Please ensure schema is loaded.")
        
        validate(instance=task_output.payload, schema=SCHEMAS[schema_id])
        print(f"Schema validation passed for {schema_id} from {agent_id}.")

        # 4. Update task status to COMPLETED and save output/artifact
        async with db_manager.transaction() as conn:
            await conn.execute(
                "UPDATE tasks SET status = $1, output_data = $2, completed_at = CURRENT_TIMESTAMP WHERE id = $3",
                TaskStatus.COMPLETED, json.dumps(task_output.model_dump()), task.id # Use model_dump() for dict
            )
            # Save artifact. Artifact name is typically schema_id without version, lowercased.
            artifact_name = schema_id.split('_')[0].lower()
            await conn.execute(
                "INSERT INTO artifacts (task_id, name, schema_id, payload) VALUES ($1, $2, $3, $4)",
                task.id, artifact_name, schema_id, task_output.payload
            )
        print(f"Agent {agent_id} task {task.id} completed and artifact '{artifact_name}' saved.")

    except Exception as e:
        error_message = str(e)
        # Update task status to FAILED
        await db_manager.execute(
            "UPDATE tasks SET status = $1, error_log = $2, completed_at = CURRENT_TIMESTAMP WHERE id = $3",
            TaskStatus.FAILED, error_message, task.id
        )
        # 6. Update job status to FAILED if any task fails
        await db_manager.execute(
            "UPDATE jobs SET status = $1, error_message = $2, completed_at = CURRENT_TIMESTAMP WHERE id = $3",
            JobStatus.FAILED, f"Pipeline failed at {agent_id}: {error_message}", job_id
        )
        print(f"Agent {agent_id} task {task.id} FAILED: {error_message}. Job {job_id} marked FAILED.")
        raise # Re-raise to fail the pytest test

# --- Test Cases ---

@pytest.mark.asyncio
async def test_e2e_happy_path_a1_a2_a3_pipeline(client, mock_ai_client, mock_base_agent_logging, setup_test_database):
    """
    E2E Happy Path: User input -> CreativeBrief (A1) -> VisualExplorations (A2) -> PresentationBlueprint (A3)
    Verifies complete data flow, schema validation at each step, and job completion.
    """
    # Arrange: Mock AI responses for each agent's successful generation
    # These are simplified mocks, real AI would generate more complex output
    mock_ai_client.generate_response.side_effect = [
        { # A1 Creative Director response
            "content": json.dumps({
                "project_overview": {"title": "AI Productivity Suite Launch", "type": "application", "description": "Develop a new AI-powered productivity suite for business professionals.", "key_themes": ["modern", "professional", "tech"]},
                "objectives": {"primary_goal": "Launch a market-leading AI productivity tool.", "secondary_goals": ["Achieve 10k users in Q1"], "success_metrics": ["User acquisition rate"]},
                "target_audience": {"primary_audience": "Business professionals", "audience_characteristics": {"demographics": "25-55, urban", "psychographics": "Value efficiency", "behavior_patterns": "Early adopters", "pain_points": "Information overload"}},
                "creative_strategy": {"tone_of_voice": "Authoritative", "key_messages": ["Unleash your team's potential"], "creative_approach": "Sleek, minimalist design"},
                "content_requirements": {"content_types": ["Homepage", "Features"], "information_hierarchy": {"Primary": 1}, "call_to_action": "Request a Demo"},
                "metadata": {"created_by": "AGENT_1", "version": "1.0", "ai_model": "mock-ai-model-1", "confidence_score": 0.95, "processing_notes": "AI-generated brief"}
            }),
            "model": "mock-ai-model-1", "provider": "mock-provider-1", "usage": {"total_tokens": 500}
        },
        { # A2 Visual Director response
            "content": json.dumps({
                "visual_themes": [
                    {"theme_name": "The Direct Voice", "design_philosophy": "【忠实演绎】Clean, professional approach.", "color_and_typography": "Corporate blue (#2563EB) with Inter.", "layout_and_graphics": "Structured layouts.", "key_slide_archetype": "Title slide: Clean centered layout."},
                    {"theme_name": "The Conceptual Bridge", "design_philosophy": "【抽象转译】Modern, forward-thinking visual language.", "color_and_typography": "Dynamic colors (#FF6B6B) with Montserrat.", "layout_and_graphics": "Asymmetrical layouts.", "key_slide_archetype": "Content slide: Off-center text blocks."},
                    {"theme_name": "The Bold Disruption", "design_philosophy": "【逆向挑战】Bold, unconventional approach.", "color_and_typography": "High contrast B&W with electric accent (#00FF88).", "layout_and_graphics": "Dramatic layouts.", "key_slide_archetype": "Statement slide: Large bold text."}
                ],
                "style_direction": "Professional yet innovative presentation design",
                "color_palette": ["#2563EB", "#64748B", "#F8FAFC"],
                "typography": {"primary_font": "Inter", "font_scale": "1.2 ratio scale"},
                "layout_principles": ["Clean hierarchy", "Balanced white space"],
                "visual_elements": {"iconography": "Modern, minimal line icons"},
                "metadata": {"created_by": "AGENT_2", "version": "1.0", "ai_model": "mock-ai-model-2", "design_confidence": 0.92, "processing_notes": "AI-generated visual explorations"}
            }),
            "model": "mock-ai-model-2", "provider": "mock-provider-2", "usage": {"total_tokens": 800}
        },
        { # A3 Chief Narrative Architect response
            "content": json.dumps({
                "strategic_choice": {
                    "chosen_theme_name": "The Direct Voice",
                    "chosen_narrative_framework": "Problem-Solution-Benefit",
                    "reasoning": "The 'Direct Voice' theme aligns perfectly with the professional audience and the need for clear, data-driven communication. The Problem-Solution-Benefit framework provides a logical and persuasive journey.",
                    "rejected_options": [{"option_type": "Visual Theme", "option_name": "The Conceptual Bridge", "reason_for_rejection": "Too abstract for a direct business presentation."}]
                },
                "presentation_blueprint": [
                    {"slide_number": 1, "logic_unit_purpose": "Introduction and Problem Statement", "layout": "Title_Slide", "elements": {"title": "Unlocking Productivity with AI", "subtitle": "A Strategic Vision"}, "speaker_notes": {"speech": "Good morning, everyone.", "guide_note": "Set a confident tone."}},
                    {"slide_number": 2, "logic_unit_purpose": "Solution Overview", "layout": "Bullet_Points", "elements": {"title": "Our AI Productivity Suite", "bullet_points": ["Intelligent Automation", "Real-time Analytics"]}, "speaker_notes": {"speech": "Our suite offers core pillars.", "guide_note": "Highlight key benefits."}}
                ],
                "metadata": {"created_by": "AGENT_3", "version": "1.0", "total_slides": 2, "narrative_complexity": "sophisticated", "target_audience_level": "intermediate", "presentation_style": "Socratic thought guidance", "confidence_score": 0.85, "ai_model": "mock-ai-model-3", "ai_provider": "mock-provider-3", "tokens_used": 1200, "processing_notes": "AI-generated presentation blueprint"}
            }),
            "model": "mock-ai-model-3", "provider": "mock-provider-3", "usage": {"total_tokens": 1200}
        }
    ]

    # Act: Create a job via API
    user_input = "I need a presentation blueprint for a new AI productivity tool targeting business professionals. It should be modern and professional."
    session_id = "e2e_test_session_001_happy_path"
    create_job_payload = {"chat_input": user_input, "session_id": session_id}
    response = await client.post("/api/v1/jobs", json=create_job_payload)
    assert response.status_code == 200
    job_response = response.json()
    job_id = job_response["job_id"]
    assert job_response["status"] == JobStatus.PENDING.value
    print(f"\nJob {job_id} created.")

    # Manually create the initial AGENT_1 task (simulating orchestrator's first step)
    initial_task_input_data = {"artifacts": [], "params": {"chat_input": user_input, "session_id": session_id}}
    await db_manager.execute(
        """
        INSERT INTO tasks (job_id, agent_id, status, input_data)
        VALUES ($1, $2, $3, $4)
        RETURNING id
        """,
        job_id, "AGENT_1", TaskStatus.PENDING, initial_task_input_data
    )
    print(f"Initial AGENT_1 task created for job {job_id}.")

    # Simulate AGENT_1 processing
    await simulate_agent_processing(job_id, "AGENT_1", db_manager)

    # Assert AGENT_1 output and AGENT_2 task creation
    job_after_a1 = Job.model_validate(await db_manager.fetch_one("SELECT * FROM jobs WHERE id = $1", job_id))
    assert job_after_a1.status == JobStatus.IN_PROGRESS # Job should be in progress
    
    a1_task = Task.model_validate(await db_manager.fetch_one("SELECT * FROM tasks WHERE job_id = $1 AND agent_id = 'AGENT_1'", job_id))
    assert a1_task.status == TaskStatus.COMPLETED
    assert a1_task.output_data is not None
    
    a1_artifact = await db_manager.fetch_one("SELECT * FROM artifacts WHERE task_id = $1 AND name = 'creativebrief'", a1_task.id)
    assert a1_artifact is not None
    assert a1_artifact["schema_id"] == "CreativeBrief_v1.0"
    # Schema validation is already done inside simulate_agent_processing
    print(f"AGENT_1 completed. CreativeBrief artifact generated and validated.")

    # Manually create AGENT_2 task (simulating orchestrator)
    a2_task_input_data = {
        "artifacts": [{"name": "creative_brief", "source_task_id": a1_task.id}],
        "params": {}
    }
    await db_manager.execute(
        """
        INSERT INTO tasks (job_id, agent_id, status, input_data)
        VALUES ($1, $2, $3, $4)
        RETURNING id
        """,
        job_id, "AGENT_2", TaskStatus.PENDING, a2_task_input_data
    )
    print(f"AGENT_2 task created for job {job_id}.")

    # Simulate AGENT_2 processing
    await simulate_agent_processing(job_id, "AGENT_2", db_manager)

    # Assert AGENT_2 output and AGENT_3 task creation
    a2_task = Task.model_validate(await db_manager.fetch_one("SELECT * FROM tasks WHERE job_id = $1 AND agent_id = 'AGENT_2'", job_id))
    assert a2_task.status == TaskStatus.COMPLETED
    assert a2_task.output_data is not None

    a2_artifact = await db_manager.fetch_one("SELECT * FROM artifacts WHERE task_id = $1 AND name = 'visualexplorations'", a2_task.id)
    assert a2_artifact is not None
    assert a2_artifact["schema_id"] == "VisualExplorations_v1.0"
    # Schema validation is already done inside simulate_agent_processing
    print(f"AGENT_2 completed. VisualExplorations artifact generated and validated.")

    # Manually create AGENT_3 task (simulating orchestrator)
    a3_task_input_data = {
        "artifacts": [
            {"name": "creative_brief", "source_task_id": a1_task.id},
            {"name": "visual_explorations", "source_task_id": a2_task.id}
        ],
        "params": {}
    }
    await db_manager.execute(
        """
        INSERT INTO tasks (job_id, agent_id, status, input_data)
        VALUES ($1, $2, $3, $4)
        RETURNING id
        """,
        job_id, "AGENT_3", TaskStatus.PENDING, a3_task_input_data
    )
    print(f"AGENT_3 task created for job {job_id}.")

    # Simulate AGENT_3 processing
    await simulate_agent_processing(job_id, "AGENT_3", db_manager)

    # Assert AGENT_3 output and job completion
    a3_task = Task.model_validate(await db_manager.fetch_one("SELECT * FROM tasks WHERE job_id = $1 AND agent_id = 'AGENT_3'", job_id))
    assert a3_task.status == TaskStatus.COMPLETED
    assert a3_task.output_data is not None

    a3_artifact = await db_manager.fetch_one("SELECT * FROM artifacts WHERE task_id = $1 AND name = 'presentationblueprint'", a3_task.id)
    assert a3_artifact is not None
    assert a3_artifact["schema_id"] == "PresentationBlueprint_v1.0"
    # Schema validation is already done inside simulate_agent_processing
    print(f"AGENT_3 completed. PresentationBlueprint artifact generated and validated.")

    # Manually update job status to COMPLETED (since we don't have orchestrator)
    await db_manager.execute(
        "UPDATE jobs SET status = $1, completed_at = CURRENT_TIMESTAMP WHERE id = $2",
        JobStatus.COMPLETED, job_id
    )

    # Final check on job status
    final_job = Job.model_validate(await db_manager.fetch_one("SELECT * FROM jobs WHERE id = $1", job_id))
    assert final_job.status == JobStatus.COMPLETED
    assert final_job.completed_at is not None
    print(f"Job {job_id} successfully completed.")

    # Golden Path Test (manual verification step)
    print("\n--- Golden Path Output (for manual verification) ---")
    print(json.dumps(a3_artifact["payload"], indent=2, ensure_ascii=False))
    print("----------------------------------------------------")


@pytest.mark.asyncio
async def test_e2e_ai_failure_fallback_a1(client, mock_ai_client, mock_base_agent_logging, setup_test_database):
    """
    E2E AI Failure Recovery: Simulate AI failure for AGENT_1, verify template fallback.
    A2 and A3 should then proceed with AI generation (as their mocks are reset for each test).
    """
    # Arrange: Mock AI response for A1 to raise an exception, subsequent calls succeed.
    mock_ai_client.generate_response.side_effect = [
        Exception("Mock AI service unavailable for AGENT_1"), # A1 fails AI
        { # A2 response (successful)
            "content": json.dumps({
                "visual_themes": [
                    {"theme_name": "Template Theme 1", "design_philosophy": "Clean, professional approach.", "color_and_typography": "Corporate blue (#2563EB) with Inter.", "layout_and_graphics": "Structured layouts.", "key_slide_archetype": "Title slide: Clean centered layout."},
                    {"theme_name": "Template Theme 2", "design_philosophy": "Modern, forward-thinking visual language.", "color_and_typography": "Dynamic colors (#FF6B6B) with Montserrat.", "layout_and_graphics": "Asymmetrical layouts.", "key_slide_archetype": "Content slide: Off-center text blocks."},
                    {"theme_name": "Template Theme 3", "design_philosophy": "Bold, unconventional approach.", "color_and_typography": "High contrast B&W with electric accent (#00FF88).", "layout_and_graphics": "Dramatic layouts.", "key_slide_archetype": "Statement slide: Large bold text."}
                ],
                "style_direction": "Clean and modern",
                "color_palette": ["#ABCDEF", "#123456"],
                "typography": {"primary_font": "Roboto", "font_scale": "Modular"},
                "layout_principles": ["Grid-based"],
                "visual_elements": {"iconography": "Line icons"},
                "metadata": {"created_by": "AGENT_2", "version": "1.0", "ai_model": "mock-ai-model-2", "design_confidence": 0.9, "processing_notes": "AI-generated visual explorations"}
            }),
            "model": "mock-ai-model-2", "provider": "mock-provider-2", "usage": {"total_tokens": 500}
        },
        { # A3 response (successful)
            "content": json.dumps({
                "strategic_choice": {
                    "chosen_theme_name": "Template Theme 1",
                    "chosen_narrative_framework": "Problem-Solution-Benefit",
                    "reasoning": "Template-based reasoning.",
                    "rejected_options": []
                },
                "presentation_blueprint": [
                    {"slide_number": 1, "logic_unit_purpose": "Intro", "layout": "Title_Slide", "elements": {"title": "Title"}, "speaker_notes": {"speech": "...", "guide_note": "..."}}
                ],
                "metadata": {"created_by": "AGENT_3", "version": "1.0", "total_slides": 1, "narrative_complexity": "moderate", "target_audience_level": "intermediate", "presentation_style": "Template-based professional presentation", "confidence_score": 0.84, "ai_model": "mock-ai-model-3", "processing_notes": "AI-generated presentation blueprint"}
            }),
            "model": "mock-ai-model-3", "provider": "mock-provider-3", "usage": {"total_tokens": 500}
        }
    ]

    # Act: Create a job via API
    user_input = "I need a simple website for my small business."
    session_id = "e2e_test_session_002_ai_fail"
    create_job_payload = {"chat_input": user_input, "session_id": session_id}
    response = await client.post("/api/v1/jobs", json=create_job_payload)
    assert response.status_code == 200
    job_response = response.json()
    job_id = job_response["job_id"]

    # Manually create the initial AGENT_1 task
    initial_task_input_data = {"artifacts": [], "params": {"chat_input": user_input, "session_id": session_id}}
    await db_manager.execute(
        """
        INSERT INTO tasks (job_id, agent_id, status, input_data)
        VALUES ($1, $2, $3, $4)
        RETURNING id
        """,
        job_id, "AGENT_1", TaskStatus.PENDING, initial_task_input_data
    )

    # Simulate AGENT_1 processing, expect it to fall back
    await simulate_agent_processing(job_id, "AGENT_1", db_manager)

    # Assert AGENT_1 output indicates template fallback
    a1_task = Task.model_validate(await db_manager.fetch_one("SELECT * FROM tasks WHERE job_id = $1 AND agent_id = 'AGENT_1'", job_id))
    assert a1_task.status == TaskStatus.COMPLETED
    assert a1_task.output_data is not None
    assert a1_task.output_data["metadata"]["ai_model"] == "template_fallback"
    validate(instance=a1_task.output_data, schema=SCHEMAS["CreativeBrief_v1.0"]) # Still validates against schema

    print(f"AGENT_1 fell back to template and completed for job {job_id}.")


@pytest.mark.asyncio 
async def test_e2e_schema_validation_basic(client, mock_ai_client, mock_base_agent_logging, setup_test_database):
    """
    E2E Schema Validation: Test that valid AI output passes schema validation.
    This is a basic test to ensure the schema validation mechanism works.
    """
    # Arrange: Mock valid AI response for A1
    mock_ai_client.generate_response.side_effect = [
        {
            "content": json.dumps({
                "project_overview": {"title": "Test Project", "type": "website", "description": "A test project.", "key_themes": ["simple"]},
                "objectives": {"primary_goal": "Test goal", "secondary_goals": [], "success_metrics": []},
                "target_audience": {"primary_audience": "Test audience", "audience_characteristics": {"demographics": "Test demographics"}},
                "creative_strategy": {"tone_of_voice": "Test tone", "key_messages": [], "creative_approach": "Test approach"},
                "content_requirements": {"content_types": [], "information_hierarchy": {}},
                "metadata": {"created_by": "AGENT_1", "version": "1.0", "ai_model": "test-model", "confidence_score": 0.9, "processing_notes": "Test"}
            }),
            "model": "test-model", "provider": "test-provider", "usage": {"total_tokens": 100}
        }
    ]

    # Act: Create a job and process AGENT_1
    user_input = "Simple test project"
    session_id = "e2e_test_session_schema_basic"
    create_job_payload = {"chat_input": user_input, "session_id": session_id}
    response = await client.post("/api/v1/jobs", json=create_job_payload)
    job_id = response.json()["job_id"]

    # Create AGENT_1 task
    initial_task_input_data = {"artifacts": [], "params": {"chat_input": user_input, "session_id": session_id}}
    await db_manager.execute(
        "INSERT INTO tasks (job_id, agent_id, status, input_data) VALUES ($1, $2, $3, $4)",
        job_id, "AGENT_1", TaskStatus.PENDING, initial_task_input_data
    )

    # Process AGENT_1
    await simulate_agent_processing(job_id, "AGENT_1", db_manager)

    # Assert: Task completed successfully
    a1_task = Task.model_validate(await db_manager.fetch_one("SELECT * FROM tasks WHERE job_id = $1 AND agent_id = 'AGENT_1'", job_id))
    assert a1_task.status == TaskStatus.COMPLETED
    assert a1_task.output_data is not None
    
    # The schema validation happens inside simulate_agent_processing, so if we reach here, it passed
    print(f"Schema validation test passed for job {job_id}")