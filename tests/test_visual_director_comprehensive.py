#!/usr/bin/env python3
"""
Comprehensive test suite for AGENT_2 (VisualDirectorAgent)
Generated by zen-mcp flash model - focuses on schema validation, error handling, and interface compatibility
"""

import pytest
import json
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.visual_director import VisualDirectorAgent
from database.models import TaskInput, TaskOutput
from ai_clients.client_factory import AIClientFactory

# --- MOCK DATA ---

# Standard mock creative brief
MOCK_CREATIVE_BRIEF = {
    "project_overview": {
        "title": "Modern Coffee Shop Website",
        "type": "website",
        "key_themes": ["modern", "warm", "sustainable"]
    },
    "objectives": {
        "primary_goal": "Create welcoming digital presence",
        "secondary_goals": ["Increase customer engagement", "Showcase sustainability"]
    },
    "target_audience": {
        "primary_audience": "Coffee enthusiasts and professionals",
        "demographics": "Urban, 25-45 years old"
    },
    "creative_strategy": {
        "tone_of_voice": "Warm and professional",
        "key_messages": ["Quality coffee", "Sustainable practices", "Community focus"]
    },
    "content_requirements": {
        "content_types": ["Hero section", "Menu", "About", "Contact"]
    }
}

# Standard mock AI response payload (conforming to the expected schema)
MOCK_AI_RESPONSE_PAYLOAD = {
    "visual_themes": [
        {
            "theme_name": "The Direct Voice",
            "design_philosophy": "【忠实演绎】Directly amplifies core messaging.",
            "color_and_typography": "Colors: Professional blue. Typography: Clean sans-serif.",
            "layout_and_graphics": "Conventional layout. Functional graphics.",
            "key_slide_archetype": "Title slide: Clean centered layout."
        },
        {
            "theme_name": "The Conceptual Bridge",
            "design_philosophy": "【抽象转译】Focuses on emotional core and functional purpose.",
            "color_and_typography": "Colors: Warm earth tones. Typography: Modern serif.",
            "layout_and_graphics": "Asymmetrical layouts. Organic shapes.",
            "key_slide_archetype": "Content slide: Off-center text blocks."
        },
        {
            "theme_name": "The Bold Disruption",
            "design_philosophy": "【逆向挑战】Challenges conventional assumptions.",
            "color_and_typography": "Colors: High contrast. Typography: Bold, confident.",
            "layout_and_graphics": "Dramatic layouts. Stark contrasts.",
            "key_slide_archetype": "Statement slide: Large bold text."
        }
    ],
    "style_direction": "AI-generated visual direction based on modern coffee shop website.",
    "color_palette": ["#1A2B3C", "#D3D3D3", "#F5F5F5"],
    "typography": {
        "primary_font": "Roboto",
        "font_scale": "1.25 ratio"
    },
    "layout_principles": [
        "Modular grid system",
        "Emphasis on negative space",
        "Dynamic content blocks"
    ],
    "visual_elements": {
        "iconography": "Geometric, abstract icons"
    }
}

# AI client raw response format, including markdown wrapper
MOCK_AI_RAW_RESPONSE = {
    "content": "```json\n" + json.dumps(MOCK_AI_RESPONSE_PAYLOAD, ensure_ascii=False, indent=2) + "\n```",
    "model": "gpt-4",
    "provider": "openai",
    "usage": {"total_tokens": 1500}
}

# --- FIXTURES ---

@pytest.fixture
def mock_agent():
    """Fixture to create a VisualDirectorAgent with mocked dependencies."""
    agent = VisualDirectorAgent()

    # Mock BaseAgent methods
    agent.get_artifacts = AsyncMock()
    agent.get_agent_prompt = AsyncMock(return_value="Mock system prompt")
    agent.log_system_event = AsyncMock()

    return agent

@pytest.fixture
def mock_task_input():
    """Fixture for a standard TaskInput with a creative brief artifact."""
    return TaskInput(
        artifacts=[{"name": "creative_brief", "source_task_id": 101}],
        params={}
    )

# --- TESTS ---

class TestVisualDirectorAgent:
    """
    Comprehensive test suite for the VisualDirectorAgent.
    Focuses on schema validation, error handling, input validation, and interface compatibility.
    """

    @pytest.mark.asyncio
    async def test_process_task_ai_success_valid_schema(self, mock_agent, mock_task_input):
        """
        Test Case: Happy path where AI successfully generates visual explorations
                   and the output conforms to the expected schema.
        Covers: Schema validation (AI output), Interface compatibility.
        """
        # Arrange
        mock_agent.get_artifacts.return_value = {
            "creative_brief": {
                "payload": MOCK_CREATIVE_BRIEF,
                "schema_id": "CreativeBrief_v1.0"
            }
        }
        
        # Mock AI client
        with patch('ai_clients.client_factory.AIClientFactory.create_client') as mock_create_client:
            mock_ai_client = AsyncMock()
            mock_ai_client.generate_response.return_value = MOCK_AI_RAW_RESPONSE
            mock_create_client.return_value = mock_ai_client

            # Act
            result = await mock_agent.process_task(mock_task_input)

            # Assert
            assert isinstance(result, TaskOutput)
            assert result.schema_id == "VisualExplorations_v1.0"
            assert isinstance(result.payload, dict)

            # Schema validation: Check top-level keys
            expected_keys = ["visual_themes", "style_direction", "color_palette", "typography", "layout_principles", "visual_elements", "metadata"]
            for key in expected_keys:
                assert key in result.payload, f"Missing key in AI output payload: {key}"

            # Schema validation: Check visual_themes array
            assert isinstance(result.payload["visual_themes"], list)
            assert len(result.payload["visual_themes"]) == 3, "AI output must contain exactly 3 visual themes"
            for theme in result.payload["visual_themes"]:
                assert isinstance(theme, dict)
                theme_keys = ["theme_name", "design_philosophy", "color_and_typography", "layout_and_graphics", "key_slide_archetype"]
                for key in theme_keys:
                    assert key in theme, f"Missing key in visual theme: {key}"
                    assert isinstance(theme[key], str)

            # Check metadata added by agent
            assert result.payload["metadata"]["created_by"] == "AGENT_2"
            assert result.payload["metadata"]["ai_model"] == MOCK_AI_RAW_RESPONSE["model"]
            assert result.payload["metadata"]["tokens_used"] == MOCK_AI_RAW_RESPONSE["usage"]["total_tokens"]

            # Verify logging
            mock_agent.log_system_event.assert_called_with(
                "INFO",
                "Visual explorations generated successfully",
                {
                    "visual_themes_count": 3,
                    "style_direction": MOCK_AI_RESPONSE_PAYLOAD["style_direction"][:50]
                }
            )

    @pytest.mark.asyncio
    async def test_process_task_missing_creative_brief_raises_error(self, mock_agent, mock_task_input):
        """
        Test Case: Input validation - `process_task` raises ValueError if 'creative_brief' artifact is not found.
        Covers: Input validation, Error handling.
        """
        # Arrange: Mock get_artifacts to return an empty dict
        mock_agent.get_artifacts.return_value = {}

        # Act & Assert
        with pytest.raises(ValueError, match="Required creative_brief artifact not found"):
            await mock_agent.process_task(mock_task_input)

        # Verify error logging
        mock_agent.log_system_event.assert_called_with(
            "ERROR",
            "Visual explorations generation failed: Required creative_brief artifact not found"
        )

    @pytest.mark.asyncio
    async def test_process_task_ai_generation_failure_falls_back_to_template(self, mock_agent, mock_task_input):
        """
        Test Case: Error handling - AI generation fails, leading to successful fallback to template generation.
        Covers: Error handling, Fallback mechanism.
        """
        # Arrange
        mock_agent.get_artifacts.return_value = {
            "creative_brief": {
                "payload": MOCK_CREATIVE_BRIEF,
                "schema_id": "CreativeBrief_v1.0"
            }
        }
        
        # Mock AI client to simulate failure
        with patch('ai_clients.client_factory.AIClientFactory.create_client') as mock_create_client:
            mock_ai_client = AsyncMock()
            mock_ai_client.generate_response.side_effect = Exception("AI API error")
            mock_create_client.return_value = mock_ai_client

            # Act
            result = await mock_agent.process_task(mock_task_input)

            # Assert
            assert isinstance(result, TaskOutput)
            assert result.schema_id == "VisualExplorations_v1.0"
            assert isinstance(result.payload, dict)

            # Verify it's template-generated output
            assert result.payload["metadata"]["ai_model"] == "template_fallback"
            assert result.payload["metadata"]["processing_notes"].startswith("Template-generated")
            assert len(result.payload["visual_themes"]) == 3  # Template always generates 3 themes

            # Verify successful logging after fallback
            mock_agent.log_system_event.assert_called_with(
                "INFO",
                "Visual explorations generated successfully",
                {
                    "visual_themes_count": 3,
                    "style_direction": result.payload["style_direction"][:50]
                }
            )

    @pytest.mark.asyncio
    async def test_parse_ai_response_malformed_json_returns_none(self, mock_agent, mock_task_input):
        """
        Test Case: Schema validation (AI output) - AI returns malformed JSON,
                   `_parse_ai_response` should return None, triggering template fallback.
        Covers: Schema validation (AI output parsing), Error handling, Fallback mechanism.
        """
        # Arrange
        mock_agent.get_artifacts.return_value = {
            "creative_brief": {
                "payload": MOCK_CREATIVE_BRIEF,
                "schema_id": "CreativeBrief_v1.0"
            }
        }
        
        # Mock AI client to return invalid JSON
        with patch('ai_clients.client_factory.AIClientFactory.create_client') as mock_create_client:
            mock_ai_client = AsyncMock()
            mock_ai_client.generate_response.return_value = {
                "content": "```json\n{this is not valid json\n```",
                "model": "gpt-4", "provider": "openai", "usage": {"total_tokens": 100}
            }
            mock_create_client.return_value = mock_ai_client

            # Act
            result = await mock_agent.process_task(mock_task_input)

            # Assert
            assert isinstance(result, TaskOutput)
            assert result.schema_id == "VisualExplorations_v1.0"
            assert isinstance(result.payload, dict)

            # Verify it's template-generated output due to AI parsing failure
            assert result.payload["metadata"]["ai_model"] == "template_fallback"
            assert len(result.payload["visual_themes"]) == 3

    @pytest.mark.asyncio
    async def test_process_task_ai_valid_json_invalid_theme_count_no_fallback(self, mock_agent, mock_task_input):
        """
        Test Case: CRITICAL DEFECT EXPOSURE - AI returns syntactically valid JSON,
                   but the 'visual_themes' array does not contain exactly 3 items.
                   The current implementation does NOT fall back to template,
                   and returns the malformed AI output.
        Covers: Schema validation (AI output content), identifies a missing validation step.
        """
        # Arrange
        mock_agent.get_artifacts.return_value = {
            "creative_brief": {
                "payload": MOCK_CREATIVE_BRIEF,
                "schema_id": "CreativeBrief_v1.0"
            }
        }
        
        # Simulate AI returning valid JSON, but with only ONE visual theme
        malformed_ai_payload = MOCK_AI_RESPONSE_PAYLOAD.copy()
        malformed_ai_payload["visual_themes"] = [malformed_ai_payload["visual_themes"][0]]  # Only one theme
        
        with patch('ai_clients.client_factory.AIClientFactory.create_client') as mock_create_client:
            mock_ai_client = AsyncMock()
            mock_ai_client.generate_response.return_value = {
                "content": "```json\n" + json.dumps(malformed_ai_payload, ensure_ascii=False, indent=2) + "\n```",
                "model": "gpt-4-malformed", "provider": "openai", "usage": {"total_tokens": 500}
            }
            mock_create_client.return_value = mock_ai_client

            # Act
            result = await mock_agent.process_task(mock_task_input)

            # Assert
            assert isinstance(result, TaskOutput)
            assert result.schema_id == "VisualExplorations_v1.0"
            assert isinstance(result.payload, dict)

            # This assertion highlights the defect: the agent returns the AI's malformed output.
            # The prompt requires 3 themes, but the code doesn't enforce this post-parsing.
            assert len(result.payload["visual_themes"]) == 1, \
                "Expected AI output with 1 theme (simulated malformed), but got different count."
            assert result.payload["metadata"]["ai_model"] == "gpt-4-malformed", \
                "Expected AI model, but template fallback occurred unexpectedly."

            # Verify logging still indicates success, which is misleading given the malformed output
            mock_agent.log_system_event.assert_called_with(
                "INFO",
                "Visual explorations generated successfully",
                {
                    "visual_themes_count": 1,  # This log reflects the malformed count
                    "style_direction": malformed_ai_payload["style_direction"][:50]
                }
            )

    @pytest.mark.asyncio
    async def test_process_task_no_system_prompt_uses_default(self, mock_agent, mock_task_input):
        """
        Test Case: Default prompt usage - If `get_agent_prompt` returns None, the agent should use its default prompt.
        Covers: Default behavior, Robustness.
        """
        # Arrange
        mock_agent.get_artifacts.return_value = {
            "creative_brief": {
                "payload": MOCK_CREATIVE_BRIEF,
                "schema_id": "CreativeBrief_v1.0"
            }
        }
        mock_agent.get_agent_prompt.return_value = None  # Simulate no prompt from DB

        with patch('ai_clients.client_factory.AIClientFactory.create_client') as mock_create_client:
            mock_ai_client = AsyncMock()
            mock_ai_client.generate_response.return_value = MOCK_AI_RAW_RESPONSE
            mock_create_client.return_value = mock_ai_client

            # Act
            await mock_agent.process_task(mock_task_input)

            # Assert: Check that the AI client was called with the default prompt
            # The default prompt is quite long, so we check for a distinctive substring
            default_prompt_start = "Agent 2: 概念炼金术士 / 视觉哲学家 (最终完整版 V3 - 苏格拉底版)"
            call_args = mock_ai_client.generate_response.call_args
            actual_system_prompt = call_args[1]["system_prompt"]
            assert default_prompt_start in actual_system_prompt
            assert "CRITICAL: You must respond with VALID JSON only." in actual_system_prompt  # Ensure JSON instruction is appended

    @pytest.mark.asyncio
    async def test_generate_template_visual_explorations_output_schema(self, mock_agent):
        """
        Test Case: Schema validation (Template output) - Verify the template-based generation
                   always produces output conforming to the expected schema.
        Covers: Schema validation (Template output), Regression.
        """
        # Arrange: Use a minimal creative brief for template generation
        minimal_creative_brief = {
            "project_overview": {"type": "report"},
            "creative_strategy": {"tone_of_voice": "formal"}
        }

        # Act
        result_payload = await mock_agent._generate_template_visual_explorations(minimal_creative_brief)

        # Assert
        assert isinstance(result_payload, dict)

        # Schema validation: Check top-level keys
        expected_keys = ["visual_themes", "style_direction", "color_palette", "typography", "layout_principles", "visual_elements", "metadata"]
        for key in expected_keys:
            assert key in result_payload, f"Missing key in template output payload: {key}"

        # Schema validation: Check visual_themes array
        assert isinstance(result_payload["visual_themes"], list)
        assert len(result_payload["visual_themes"]) == 3, "Template output must contain exactly 3 visual themes"
        for theme in result_payload["visual_themes"]:
            assert isinstance(theme, dict)
            theme_keys = ["theme_name", "design_philosophy", "color_and_typography", "layout_and_graphics", "key_slide_archetype"]
            for key in theme_keys:
                assert key in theme, f"Missing key in template visual theme: {key}"
                assert isinstance(theme[key], str)

        # Check metadata for template
        assert result_payload["metadata"]["created_by"] == "AGENT_2"
        assert result_payload["metadata"]["ai_model"] == "template_fallback"
        assert "design_confidence" in result_payload["metadata"]
        assert 0.6 <= result_payload["metadata"]["design_confidence"] <= 0.85

    @pytest.mark.asyncio
    async def test_process_task_creative_brief_empty_payload(self, mock_agent, mock_task_input):
        """
        Test Case: Input validation - Empty creative brief payload should still work via template fallback.
        Covers: Input validation, Robustness.
        """
        # Arrange
        mock_agent.get_artifacts.return_value = {
            "creative_brief": {
                "payload": {},  # Empty brief
                "schema_id": "CreativeBrief_v1.0"
            }
        }

        with patch('ai_clients.client_factory.AIClientFactory.create_client') as mock_create_client:
            mock_ai_client = AsyncMock()
            mock_ai_client.generate_response.side_effect = Exception("AI can't handle empty brief")
            mock_create_client.return_value = mock_ai_client

            # Act
            result = await mock_agent.process_task(mock_task_input)

            # Assert
            assert isinstance(result, TaskOutput)
            assert result.schema_id == "VisualExplorations_v1.0"
            assert len(result.payload["visual_themes"]) == 3
            assert result.payload["metadata"]["ai_model"] == "template_fallback"

    def test_calculate_template_confidence_completeness(self, mock_agent):
        """
        Test Case: Template confidence calculation based on creative brief completeness.
        Covers: Template generation logic, confidence scoring.
        """
        # Test with complete brief
        complete_brief = {
            "project_overview": {"title": "Test"},
            "objectives": {"primary_goal": "Test"},
            "target_audience": {"primary_audience": "Test"},
            "creative_strategy": {"tone_of_voice": "Test"}
        }
        confidence_complete = mock_agent._calculate_template_confidence(complete_brief)
        assert 0.8 <= confidence_complete <= 0.85

        # Test with incomplete brief
        incomplete_brief = {
            "project_overview": {"title": "Test"}
        }
        confidence_incomplete = mock_agent._calculate_template_confidence(incomplete_brief)
        assert 0.6 <= confidence_incomplete < 0.8

        # Complete brief should have higher confidence
        assert confidence_complete > confidence_incomplete

    def test_parse_ai_response_with_markdown_cleanup(self, mock_agent):
        """
        Test Case: AI response parsing correctly handles markdown cleanup.
        Covers: JSON parsing, Markdown cleanup.
        """
        # Test with markdown wrapper
        content_with_markdown = "```json\n" + json.dumps(MOCK_AI_RESPONSE_PAYLOAD) + "\n```"
        response_data = {"model": "test", "provider": "test", "usage": {"total_tokens": 100}}

        result = mock_agent._parse_ai_response(content_with_markdown, response_data)

        assert result is not None
        assert "visual_themes" in result
        assert result["metadata"]["ai_model"] == "test"

    def test_parse_ai_response_no_markdown(self, mock_agent):
        """
        Test Case: AI response parsing works without markdown wrapper.
        Covers: JSON parsing flexibility.
        """
        # Test without markdown wrapper
        content_no_markdown = json.dumps(MOCK_AI_RESPONSE_PAYLOAD)
        response_data = {"model": "test", "provider": "test", "usage": {"total_tokens": 100}}

        result = mock_agent._parse_ai_response(content_no_markdown, response_data)

        assert result is not None
        assert "visual_themes" in result
        assert result["metadata"]["ai_model"] == "test"