import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import json
import jsonschema  # Assuming jsonschema is installed (pip install jsonschema)

# Import the class and models to be tested
from agents.narrative_architect import ChiefNarrativeArchitectAgent
from database.models import TaskInput, TaskOutput

# --- Mock Data ---

MOCK_CREATIVE_BRIEF = {
    "project_overview": {
        "title": "Digital Transformation Initiative",
        "type": "corporate",
        "description": "Modernizing our business processes through technology adoption",
        "key_themes": ["modern", "professional", "innovative"]
    },
    "objectives": {
        "primary_goal": "Present our digital transformation strategy to senior leadership",
        "secondary_goals": ["Secure budget approval", "Align stakeholders"],
        "success_metrics": ["Board approval", "Resource allocation"]
    },
    "target_audience": {
        "primary_audience": "Senior executives and board members",
        "audience_characteristics": {
            "demographics": "C-level executives, 45-65 years old",
            "motivations": "Business growth and competitive advantage"
        }
    },
    "creative_strategy": {
        "tone_of_voice": "Professional, confident, and visionary",
        "key_messages": [
            "Digital transformation is essential for competitive advantage",
            "Our proposed strategy addresses key business challenges",
            "Expected ROI justifies the investment"
        ],
        "creative_approach": "Data-driven storytelling with clear business case"
    }
}

MOCK_VISUAL_EXPLORATIONS = {
    "visual_themes": [
        {
            "theme_name": "The Direct Voice",
            "design_philosophy": "Clean, professional approach that builds trust",
            "color_and_typography": "Corporate blue with professional sans-serif",
            "layout_and_graphics": "Structured layouts with clear hierarchy"
        },
        {
            "theme_name": "The Innovation Edge",
            "design_philosophy": "Modern, forward-thinking visual language",
            "color_and_typography": "Dynamic colors with contemporary typography",
            "layout_and_graphics": "Asymmetrical layouts with bold elements"
        },
        {
            "theme_name": "The Disruptor",
            "design_philosophy": "Bold, unconventional approach",
            "color_and_typography": "High contrast with dramatic typography",
            "layout_and_graphics": "Minimalist with powerful negative space"
        }
    ],
    "style_direction": "Professional yet innovative presentation design",
    "color_palette": ["#1E40AF", "#64748B", "#F8FAFC"],
    "typography": {
        "primary_font": "Inter",
        "font_scale": "Professional scale system"
    }
}

MOCK_AI_RESPONSE_CONTENT = """
{
  "strategic_choice": {
    "chosen_theme_name": "The Direct Voice",
    "chosen_narrative_framework": "Problem-Solution-Benefit",
    "reasoning": "The Direct Voice theme aligns with the professional audience, and Problem-Solution-Benefit provides a clear logical flow.",
    "rejected_options": [
      {
        "option_type": "Visual Theme",
        "option_name": "The Innovation Edge",
        "reason_for_rejection": "Too abstract for a senior leadership presentation."
      }
    ]
  },
  "presentation_blueprint": [
    {
      "slide_number": 1,
      "logic_unit_purpose": "Opening & Establishing Credibility",
      "layout": "Title_Slide",
      "elements": {
        "title": "Digital Transformation Initiative",
        "subtitle": "A Strategic Imperative"
      },
      "speaker_notes": {
        "speech": "Welcome, today we discuss our digital transformation.",
        "guide_note": "Set the stage."
      }
    },
    {
      "slide_number": 2,
      "logic_unit_purpose": "Defining the Problem/Opportunity",
      "layout": "Content_With_Chart",
      "elements": {
        "title": "The Challenge and Opportunity",
        "bullet_points": ["Outdated systems", "Market shifts", "Growth potential"],
        "visual_placeholder": "Market trend chart"
      },
      "speaker_notes": {
        "speech": "Our current systems are not keeping pace with market demands.",
        "guide_note": "Highlight urgency."
      }
    }
  ]
}
"""

MOCK_AI_RAW_RESPONSE = {
    "content": MOCK_AI_RESPONSE_CONTENT,
    "model": "mock-ai-model",
    "provider": "mock-ai-provider",
    "usage": {"total_tokens": 1500}
}

# --- Schema Definition for Validation ---
# Simplified schema for testing purposes
PRESENTATION_BLUEPRINT_FINAL_SCHEMA = {
  "type": "object",
  "properties": {
    "strategic_choice": {
      "type": "object",
      "properties": {
        "chosen_theme_name": {"type": "string"},
        "chosen_narrative_framework": {"type": "string"},
        "reasoning": {"type": "string"},
        "rejected_options": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "option_type": {"type": "string"},
              "option_name": {"type": "string"},
              "reason_for_rejection": {"type": "string"}
            },
            "required": ["option_type", "option_name", "reason_for_rejection"]
          }
        }
      },
      "required": ["chosen_theme_name", "chosen_narrative_framework", "reasoning", "rejected_options"]
    },
    "presentation_blueprint": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "slide_number": {"type": "integer", "minimum": 1},
          "logic_unit_purpose": {"type": "string"},
          "layout": {"type": "string"},
          "elements": {"type": "object"},
          "speaker_notes": {
            "type": "object",
            "properties": {
              "speech": {"type": "string"},
              "guide_note": {"type": "string"}
            },
            "required": ["speech", "guide_note"]
          }
        },
        "required": ["slide_number", "logic_unit_purpose", "layout", "elements", "speaker_notes"]
      }
    },
    "metadata": {
        "type": "object",
        "properties": {
            "created_by": {"type": "string"},
            "version": {"type": "string"},
            "total_slides": {"type": "integer"},
            "narrative_complexity": {"type": "string"},
            "target_audience_level": {"type": "string"},
            "presentation_style": {"type": "string"},
            "confidence_score": {"type": "number"},
            "ai_model": {"type": "string"},
            "processing_notes": {"type": "string"}
        },
        "required": [
            "created_by", "version", "total_slides", "narrative_complexity",
            "target_audience_level", "presentation_style", "confidence_score",
            "ai_model", "processing_notes"
        ]
    }
  },
  "required": ["strategic_choice", "presentation_blueprint", "metadata"]
}

# Helper for schema validation
def validate_presentation_blueprint_schema(data: dict):
    """Validates the given data against the PresentationBlueprint_v1.0 schema."""
    try:
        jsonschema.validate(instance=data, schema=PRESENTATION_BLUEPRINT_FINAL_SCHEMA)
    except jsonschema.ValidationError as e:
        pytest.fail(f"Schema validation failed: {e.message} at {e.path}")

# --- Pytest Fixtures ---

@pytest.fixture
def narrative_architect_agent():
    """Fixture to provide a fresh instance of the agent for each test."""
    return ChiefNarrativeArchitectAgent()

@pytest.fixture
def mock_task_input():
    """Fixture for a standard TaskInput with required artifacts."""
    return TaskInput(
        artifacts=[
            {"name": "creative_brief", "source_task_id": 101},
            {"name": "visual_explorations", "source_task_id": 102}
        ],
        params={}
    )

@pytest.fixture
def mock_get_artifacts_success():
    """Fixture for mocking get_artifacts to return valid data."""
    async def _mock_get_artifacts(refs):
        artifacts_data = {}
        for ref in refs:
            if ref.name == "creative_brief":
                artifacts_data["creative_brief"] = {
                    "payload": MOCK_CREATIVE_BRIEF,
                    "schema_id": "CreativeBrief_v1.0"
                }
            elif ref.name == "visual_explorations":
                artifacts_data["visual_explorations"] = {
                    "payload": MOCK_VISUAL_EXPLORATIONS,
                    "schema_id": "VisualExplorations_v1.0"
                }
        return artifacts_data
    return _mock_get_artifacts

@pytest.fixture
def mock_ai_client_success():
    """Fixture for mocking AIClientFactory and AIClient for successful AI response."""
    mock_ai_client = AsyncMock()
    mock_ai_client.generate_response.return_value = MOCK_AI_RAW_RESPONSE
    with patch('ai_clients.client_factory.AIClientFactory.create_client', return_value=mock_ai_client):
        yield mock_ai_client

@pytest.fixture
def mock_ai_client_failure():
    """Fixture for mocking AIClientFactory and AIClient for AI response failure."""
    mock_ai_client = AsyncMock()
    mock_ai_client.generate_response.side_effect = Exception("AI service unavailable")
    with patch('ai_clients.client_factory.AIClientFactory.create_client', return_value=mock_ai_client):
        yield mock_ai_client

@pytest.fixture
def mock_ai_client_invalid_json():
    """Fixture for mocking AIClientFactory and AIClient for AI response with invalid JSON."""
    mock_ai_client = AsyncMock()
    mock_ai_client.generate_response.return_value = {
        "content": "This is not JSON {invalid",
        "model": "mock-ai-model",
        "provider": "mock-ai-provider",
        "usage": {"total_tokens": 10}
    }
    with patch('ai_clients.client_factory.AIClientFactory.create_client', return_value=mock_ai_client):
        yield mock_ai_client

@pytest.fixture
def mock_ai_client_markdown_json():
    """Fixture for mocking AIClientFactory and AIClient for AI response with markdown JSON."""
    mock_ai_client = AsyncMock()
    mock_ai_client.generate_response.return_value = {
        "content": "```json\n" + MOCK_AI_RESPONSE_CONTENT + "\n```",
        "model": "mock-ai-model",
        "provider": "mock-ai-provider",
        "usage": {"total_tokens": 1500}
    }
    with patch('ai_clients.client_factory.AIClientFactory.create_client', return_value=mock_ai_client):
        yield mock_ai_client

@pytest.fixture(autouse=True)
def mock_base_agent_methods(narrative_architect_agent):
    """
    Automatically mock BaseAgent methods for all tests.
    This ensures isolation from actual database/prompt fetching and logging.
    """
    narrative_architect_agent.get_agent_prompt = AsyncMock(return_value="Mock system prompt.")
    narrative_architect_agent.log_system_event = AsyncMock()
    # get_artifacts is mocked per test or by specific fixtures
    yield

# --- Tests ---

@pytest.mark.asyncio
async def test_process_task_success_ai_path(narrative_architect_agent, mock_task_input, mock_get_artifacts_success, mock_ai_client_success):
    """
    Test Case: Core functionality - Happy path with successful AI generation.
    Coverage: process_task workflow, AI generation success, output schema validation.
    """
    # Arrange
    narrative_architect_agent.get_artifacts = mock_get_artifacts_success

    # Act
    result = await narrative_architect_agent.process_task(mock_task_input)

    # Assert
    assert isinstance(result, TaskOutput)
    assert result.schema_id == "PresentationBlueprint_v1.0"
    assert isinstance(result.payload, dict)

    # Validate the output payload against the expected schema
    validate_presentation_blueprint_schema(result.payload)

    # Verify specific content from AI response
    assert result.payload["strategic_choice"]["chosen_theme_name"] == "The Direct Voice"
    assert result.payload["strategic_choice"]["chosen_narrative_framework"] == "Problem-Solution-Benefit"
    assert len(result.payload["presentation_blueprint"]) == 2 # Based on MOCK_AI_RESPONSE_CONTENT
    assert result.payload["metadata"]["ai_model"] == "mock-ai-model"
    assert result.payload["metadata"]["confidence_score"] == 0.85 # Default confidence for AI path

@pytest.mark.asyncio
async def test_process_task_missing_creative_brief(narrative_architect_agent, mock_task_input):
    """
    Test Case: Input validation - Missing 'creative_brief' artifact.
    Coverage: Input validation error handling.
    """
    # Arrange
    async def mock_get_artifacts_partial(refs):
        return {
            "visual_explorations": {
                "payload": MOCK_VISUAL_EXPLORATIONS,
                "schema_id": "VisualExplorations_v1.0"
            }
        }
    narrative_architect_agent.get_artifacts = mock_get_artifacts_partial

    # Act & Assert
    with pytest.raises(ValueError, match="Required creative_brief artifact not found"):
        await narrative_architect_agent.process_task(mock_task_input)

@pytest.mark.asyncio
async def test_process_task_missing_visual_explorations(narrative_architect_agent, mock_task_input):
    """
    Test Case: Input validation - Missing 'visual_explorations' artifact.
    Coverage: Input validation error handling.
    """
    # Arrange
    async def mock_get_artifacts_partial(refs):
        return {
            "creative_brief": {
                "payload": MOCK_CREATIVE_BRIEF,
                "schema_id": "CreativeBrief_v1.0"
            }
        }
    narrative_architect_agent.get_artifacts = mock_get_artifacts_partial

    # Act & Assert
    with pytest.raises(ValueError, match="Required visual_explorations artifact not found"):
        await narrative_architect_agent.process_task(mock_task_input)

@pytest.mark.asyncio
async def test_ai_generation_failure_falls_back_to_template(narrative_architect_agent, mock_task_input, mock_get_artifacts_success, mock_ai_client_failure):
    """
    Test Case: AI integration - AI generation fails, triggering template fallback.
    Coverage: AI failure mode, template degradation.
    """
    # Arrange
    narrative_architect_agent.get_artifacts = mock_get_artifacts_success

    # Act
    result = await narrative_architect_agent.process_task(mock_task_input)

    # Assert
    assert isinstance(result, TaskOutput)
    assert result.schema_id == "PresentationBlueprint_v1.0"
    assert isinstance(result.payload, dict)

    # Validate the output payload against the expected schema
    validate_presentation_blueprint_schema(result.payload)

    # Verify that template fallback was used
    assert result.payload["metadata"]["ai_model"] == "template_fallback"
    assert result.payload["metadata"]["processing_notes"].startswith("Template-generated")
    assert result.payload["strategic_choice"]["chosen_narrative_framework"] == "Problem-Solution-Benefit"
    assert result.payload["strategic_choice"]["chosen_theme_name"] == MOCK_VISUAL_EXPLORATIONS["visual_themes"][0]["theme_name"]
    assert len(result.payload["presentation_blueprint"]) > 0
    assert result.payload["metadata"]["confidence_score"] < 0.85

@pytest.mark.asyncio
async def test_ai_response_invalid_json_falls_back_to_template(narrative_architect_agent, mock_task_input, mock_get_artifacts_success, mock_ai_client_invalid_json):
    """
    Test Case: AI output parsing - AI returns invalid JSON.
    Coverage: JSON parsing error handling, template degradation.
    """
    # Arrange
    narrative_architect_agent.get_artifacts = mock_get_artifacts_success

    # Act
    result = await narrative_architect_agent.process_task(mock_task_input)

    # Assert
    assert isinstance(result, TaskOutput)
    assert result.schema_id == "PresentationBlueprint_v1.0"
    assert isinstance(result.payload, dict)

    # Validate the output payload
    validate_presentation_blueprint_schema(result.payload)

    # Verify that template fallback was used
    assert result.payload["metadata"]["ai_model"] == "template_fallback"
    assert result.payload["metadata"]["processing_notes"].startswith("Template-generated")
    assert result.payload["metadata"]["confidence_score"] < 0.85

@pytest.mark.asyncio
async def test_ai_response_with_markdown_backticks(narrative_architect_agent, mock_task_input, mock_get_artifacts_success, mock_ai_client_markdown_json):
    """
    Test Case: AI output parsing - AI response includes markdown backticks.
    Coverage: Markdown cleanup, JSON parsing.
    """
    # Arrange
    narrative_architect_agent.get_artifacts = mock_get_artifacts_success

    # Act
    result = await narrative_architect_agent.process_task(mock_task_input)

    # Assert
    assert isinstance(result, TaskOutput)
    assert result.schema_id == "PresentationBlueprint_v1.0"
    assert isinstance(result.payload, dict)

    # Validate the output payload
    validate_presentation_blueprint_schema(result.payload)

    # Verify that AI generation was successful and not a fallback
    assert result.payload["metadata"]["ai_model"] == "mock-ai-model"
    assert result.payload["metadata"]["processing_notes"] == "AI-generated narrative architecture"
    assert result.payload["strategic_choice"]["chosen_theme_name"] == "The Direct Voice"
    assert len(result.payload["presentation_blueprint"]) == 2

@pytest.mark.asyncio
async def test_template_generation_with_minimal_inputs(narrative_architect_agent, mock_task_input, mock_ai_client_failure):
    """
    Test Case: Template generation - Minimal input data.
    Coverage: Template generation robustness, confidence calculation.
    """
    # Arrange
    minimal_creative_brief = {
        "project_overview": {"title": "Minimal Project"},
        "objectives": {"primary_goal": "Achieve minimal goal"},
        "target_audience": {"primary_audience": "Anyone"},
        "creative_strategy": {"key_messages": []}
    }
    minimal_visual_explorations = {
        "visual_themes": []
    }

    async def mock_get_artifacts_minimal(refs):
        return {
            "creative_brief": {"payload": minimal_creative_brief, "schema_id": "CreativeBrief_v1.0"},
            "visual_explorations": {"payload": minimal_visual_explorations, "schema_id": "VisualExplorations_v1.0"}
        }
    narrative_architect_agent.get_artifacts = mock_get_artifacts_minimal

    # Act
    result = await narrative_architect_agent.process_task(mock_task_input)

    # Assert
    assert isinstance(result, TaskOutput)
    assert result.schema_id == "PresentationBlueprint_v1.0"
    assert isinstance(result.payload, dict)

    # Validate the output payload
    validate_presentation_blueprint_schema(result.payload)

    # Verify template fallback was used
    assert result.payload["metadata"]["ai_model"] == "template_fallback"
    assert result.payload["strategic_choice"]["chosen_theme_name"] == "Professional Standard"
    assert result.payload["strategic_choice"]["chosen_narrative_framework"] == "Problem-Solution-Benefit"
    assert len(result.payload["presentation_blueprint"]) == 4  # Title, Agenda, Problem, CTA
    # Expected confidence: 0.65 + 0.15 = 0.80
    assert result.payload["metadata"]["confidence_score"] == pytest.approx(0.80)

@pytest.mark.asyncio
async def test_get_agent_prompt_fallback_to_default(narrative_architect_agent, mock_task_input, mock_get_artifacts_success, mock_ai_client_success):
    """
    Test Case: Prompt management - get_agent_prompt returns None, fallback to default.
    Coverage: Default prompt usage.
    """
    # Arrange
    narrative_architect_agent.get_artifacts = mock_get_artifacts_success
    narrative_architect_agent.get_agent_prompt = AsyncMock(return_value=None)

    # Act
    result = await narrative_architect_agent.process_task(mock_task_input)

    # Assert
    assert isinstance(result, TaskOutput)
    assert result.schema_id == "PresentationBlueprint_v1.0"
    narrative_architect_agent.get_agent_prompt.assert_called_once()