"""
Tests for Chief Principles Auditor Agent (AGENT_4)
Based on AGENT_1-3 testing experience and zen-mcp best practices
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.agents.chief_auditor import ChiefPrinciplesAuditorAgent
from src.database.models import TaskInput, TaskOutput, ArtifactReference


@pytest.fixture
async def agent():
    """Create agent instance with mocked dependencies"""
    agent = ChiefPrinciplesAuditorAgent()
    agent.db_manager = AsyncMock()
    return agent


@pytest.fixture
def mock_task_input():
    """Create mock task input with required artifacts"""
    return TaskInput(
        artifacts=[
            ArtifactReference(name="presentation_blueprint", source_task_id=103),
            ArtifactReference(name="creative_brief", source_task_id=101),
            ArtifactReference(name="visual_explorations", source_task_id=102)
        ],
        params={}
    )


@pytest.fixture
def mock_presentation_blueprint():
    """Mock presentation blueprint for testing"""
    return {
        "strategic_choice": {
            "chosen_theme_name": "Professional Consulting Theme",
            "chosen_narrative_framework": "Problem-Solution Framework",
            "reasoning": "This combination aligns with the professional audience and analytical approach needed.",
            "rejected_options": [
                {
                    "option_type": "Visual Theme",
                    "option_name": "Creative Startup Theme", 
                    "reason_for_rejection": "Too casual for the executive audience"
                }
            ]
        },
        "presentation_blueprint": [
            {
                "slide_number": 1,
                "logic_unit_purpose": "Introduction and agenda setting",
                "layout": "Title_Slide",
                "elements": {
                    "title": "Digital Transformation Strategy",
                    "subtitle": "Roadmap for Success"
                },
                "speaker_notes": {
                    "speech": "Welcome to our digital transformation presentation",
                    "guide_note": "Establish credibility early"
                }
            },
            {
                "slide_number": 2,
                "logic_unit_purpose": "Problem identification",
                "layout": "Content_With_Chart",
                "elements": {
                    "title": "Current Challenges Limit Growth Potential",
                    "content": "Legacy systems create bottlenecks"
                },
                "speaker_notes": {
                    "speech": "Our analysis shows three critical challenges",
                    "guide_note": "Emphasize urgency"
                }
            }
        ]
    }


@pytest.fixture
def mock_creative_brief():
    """Mock creative brief for testing"""
    return {
        "purpose": "Secure executive approval for digital transformation initiative",
        "target_audience": "C-suite executives and board members",
        "desired_feeling": "Confident about the strategic direction and ROI",
        "key_messages": ["Urgency for change", "Clear ROI", "Proven methodology"]
    }


@pytest.fixture
def mock_visual_explorations():
    """Mock visual explorations for testing"""
    return {
        "selected_theme": {
            "name": "Professional Consulting Theme",
            "color_palette": ["#1f2937", "#3b82f6", "#f3f4f6"],
            "typography": {"primary": "Inter", "secondary": "Source Sans Pro"}
        }
    }


class TestChiefPrinciplesAuditorAgent:
    """Test suite for Chief Principles Auditor Agent"""

    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = ChiefPrinciplesAuditorAgent()
        assert agent.agent_id == "AGENT_4"
        assert agent.ai_client_factory is not None

    @pytest.mark.asyncio
    async def test_process_task_success(self, agent, mock_task_input, 
                                      mock_presentation_blueprint,
                                      mock_creative_brief,
                                      mock_visual_explorations):
        """Test successful task processing"""
        # Setup mocks
        agent.get_artifacts = AsyncMock(return_value={
            "presentation_blueprint": mock_presentation_blueprint,
            "creative_brief": mock_creative_brief,
            "visual_explorations": mock_visual_explorations
        })
        
        # Process task
        result = await agent.process_task(mock_task_input)
        
        # Assertions
        assert isinstance(result, TaskOutput)
        assert result.schema_id == "AuditReport_v1.0"
        assert "audit_passed" in result.payload
        assert "summary" in result.payload
        assert "metadata" in result.payload

    @pytest.mark.asyncio
    async def test_process_task_missing_blueprint(self, agent, mock_task_input):
        """Test handling of missing presentation blueprint"""
        # Setup mock with missing blueprint
        agent.get_artifacts = AsyncMock(return_value={
            "creative_brief": {"purpose": "test"},
            "visual_explorations": {"theme": "test"}
        })
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="Presentation blueprint artifact is required"):
            await agent.process_task(mock_task_input)

    @pytest.mark.asyncio
    async def test_ai_generation_fallback_to_template(self, agent,
                                                    mock_presentation_blueprint,
                                                    mock_creative_brief,
                                                    mock_visual_explorations):
        """Test AI failure fallback to template audit"""
        # Mock AI client to fail
        mock_ai_client = AsyncMock()
        mock_ai_client.generate_completion.side_effect = Exception("AI service unavailable")
        agent.ai_client_factory.get_client = AsyncMock(return_value=mock_ai_client)
        
        # Generate audit report
        result = await agent._generate_audit_report(
            mock_presentation_blueprint, mock_creative_brief, mock_visual_explorations
        )
        
        # Should fallback to template
        assert result["metadata"]["auditor_notes"] == "Template-based audit due to AI processing failure"
        assert result["metadata"]["confidence_level"] == 0.75  # Template confidence

    def test_socratic_judge_prompt_structure(self, agent):
        """Test the Socratic judge prompt is properly structured"""
        prompt = agent._build_socratic_judge_prompt()
        
        # Check for key components
        assert "Chief Principles Auditor" in prompt
        assert "Phase 1: Constitutional Review" in prompt
        assert "Phase 2: Protocol Compliance Assessment" in prompt
        assert "Phase 3: Systematic Cross-Examination" in prompt
        assert "A-PYR-01" in prompt  # Pyramid Principle
        assert "A-NARR-02" in prompt  # Narrative Flow
        assert "A-STR-03" in prompt  # Structural Integrity
        assert "A-AUD-04" in prompt  # Audience Alignment

    def test_audit_context_building(self, agent, mock_presentation_blueprint,
                                  mock_creative_brief, mock_visual_explorations):
        """Test audit context is properly built"""
        context = agent._build_audit_context(
            mock_presentation_blueprint, mock_creative_brief, mock_visual_explorations
        )
        
        # Should contain all required sections
        assert "PROJECT CONSTITUTION" in context
        assert "VISUAL CONTEXT" in context
        assert "PRESENTATION BLUEPRINT TO AUDIT" in context
        assert "constitutional alignment" in context.lower()

    def test_parse_ai_response_valid_json(self, agent):
        """Test parsing valid AI response"""
        valid_response = """{
            "audit_passed": false,
            "summary": {
                "errors_found": 1,
                "warnings_found": 2,
                "overall_score": 75
            },
            "errors": [],
            "warnings": []
        }"""
        
        result = agent._parse_ai_response(valid_response)
        
        assert result is not None
        assert result["audit_passed"] is False
        assert result["summary"]["overall_score"] == 75
        assert "metadata" in result
        assert result["metadata"]["created_by"] == "AGENT_4"

    def test_parse_ai_response_with_markdown(self, agent):
        """Test parsing AI response with markdown formatting"""
        markdown_response = """```json
        {
            "audit_passed": true,
            "summary": {"errors_found": 0, "warnings_found": 0, "overall_score": 95},
            "errors": [],
            "warnings": []
        }
        ```"""
        
        result = agent._parse_ai_response(markdown_response)
        
        assert result is not None
        assert result["audit_passed"] is True
        assert result["summary"]["overall_score"] == 95

    def test_parse_ai_response_invalid_json(self, agent):
        """Test handling invalid JSON response"""
        invalid_response = "This is not valid JSON {invalid}"
        
        result = agent._parse_ai_response(invalid_response)
        
        assert result is None

    def test_template_audit_basic_structure(self, agent, mock_presentation_blueprint,
                                          mock_creative_brief, mock_visual_explorations):
        """Test template audit generates proper structure"""
        result = agent._generate_template_audit(
            mock_presentation_blueprint, mock_creative_brief, mock_visual_explorations
        )
        
        # Check required fields
        assert "audit_passed" in result
        assert "summary" in result
        assert "errors" in result  
        assert "warnings" in result
        assert "protocol_compliance" in result
        assert "recommendations" in result
        assert "metadata" in result
        
        # Check metadata
        assert result["metadata"]["created_by"] == "AGENT_4"
        assert "protocols_referenced" in result["metadata"]
        assert result["metadata"]["confidence_level"] == 0.75

    def test_template_audit_insufficient_slides(self, agent, mock_creative_brief,
                                              mock_visual_explorations):
        """Test template audit detects insufficient slides"""
        insufficient_blueprint = {
            "strategic_choice": {"chosen_theme_name": "Test"},
            "presentation_blueprint": [{"slide_number": 1}]  # Only 1 slide
        }
        
        result = agent._generate_template_audit(
            insufficient_blueprint, mock_creative_brief, mock_visual_explorations
        )
        
        # Should detect error
        assert result["audit_passed"] is False
        assert result["summary"]["errors_found"] > 0
        
        # Should have specific error about insufficient slides
        errors = result["errors"]
        assert any("insufficient slides" in error["message"].lower() for error in errors)

    def test_confidence_score_calculation(self, agent):
        """Test confidence score calculation logic"""
        # Test with minimal data
        minimal_data = {"presentation_blueprint": [{"slide": 1}]}
        confidence = agent._calculate_confidence_score(minimal_data)
        assert 0.6 <= confidence <= 0.85
        
        # Test with substantial data
        substantial_data = {"presentation_blueprint": [{"slide": i} for i in range(1, 12)]}
        confidence = agent._calculate_confidence_score(substantial_data)
        assert confidence >= 0.75

    @pytest.mark.asyncio
    async def test_ai_client_error_handling(self, agent, mock_presentation_blueprint,
                                          mock_creative_brief, mock_visual_explorations):
        """Test proper error handling when AI client fails"""
        # Mock AI client factory to return failing client
        mock_ai_client = AsyncMock()
        mock_ai_client.generate_completion.side_effect = ConnectionError("Network error")
        agent.ai_client_factory.get_client = AsyncMock(return_value=mock_ai_client)
        
        # Should not raise exception, should fallback to template
        result = await agent._generate_with_ai(
            mock_presentation_blueprint, mock_creative_brief, mock_visual_explorations
        )
        
        assert result is None  # AI generation failed, returns None for fallback

    def test_protocol_compliance_structure(self, agent, mock_presentation_blueprint,
                                         mock_creative_brief, mock_visual_explorations):
        """Test protocol compliance structure in template audit"""
        result = agent._generate_template_audit(
            mock_presentation_blueprint, mock_creative_brief, mock_visual_explorations
        )
        
        protocol_compliance = result["protocol_compliance"]
        
        # Check all required protocols
        assert "pyramid_principle" in protocol_compliance
        assert "narrative_flow" in protocol_compliance
        assert "structural_integrity" in protocol_compliance
        assert "audience_alignment" in protocol_compliance
        
        # Check each protocol has required fields
        for protocol in protocol_compliance.values():
            assert "overall_score" in protocol
            assert isinstance(protocol["overall_score"], int)
            assert 0 <= protocol["overall_score"] <= 100


# Integration test
@pytest.mark.asyncio
async def test_full_audit_workflow():
    """Integration test for full audit workflow"""
    agent = ChiefPrinciplesAuditorAgent()
    agent.db_manager = AsyncMock()
    
    # Mock artifacts
    mock_blueprint = {
        "strategic_choice": {
            "chosen_theme_name": "Professional Theme",
            "reasoning": "Aligns with executive audience"
        },
        "presentation_blueprint": [
            {"slide_number": 1, "elements": {"title": "Executive Summary"}},
            {"slide_number": 2, "elements": {"title": "Problem Analysis"}},
            {"slide_number": 3, "elements": {"title": "Recommended Solution"}}
        ]
    }
    
    agent.get_artifacts = AsyncMock(return_value={
        "presentation_blueprint": mock_blueprint,
        "creative_brief": {"purpose": "test", "target_audience": "executives"},
        "visual_explorations": {"theme": "professional"}
    })
    
    task_input = TaskInput(
        artifacts=[
            ArtifactReference(name="presentation_blueprint", source_task_id=103),
            ArtifactReference(name="creative_brief", source_task_id=101),
            ArtifactReference(name="visual_explorations", source_task_id=102)
        ],
        params={}
    )
    
    # Process task
    result = await agent.process_task(task_input)
    
    # Verify complete workflow
    assert isinstance(result, TaskOutput)
    assert result.schema_id == "AuditReport_v1.0"
    
    payload = result.payload
    assert isinstance(payload["audit_passed"], bool)
    assert "summary" in payload
    assert "errors" in payload
    assert "warnings" in payload
    assert "metadata" in payload
    assert payload["metadata"]["created_by"] == "AGENT_4"


# Additional test cases based on zen-mcp recommendations
class TestChiefAuditorEnhanced:
    """Enhanced test cases for zen-mcp issues found"""

    @pytest.mark.asyncio
    async def test_ai_client_factory_failure(self, agent, mock_task_input,
                                           mock_presentation_blueprint,
                                           mock_creative_brief, 
                                           mock_visual_explorations):
        """Test AI client factory failure handling"""
        # Mock AI client factory to return None
        agent.ai_client_factory.get_client = AsyncMock(return_value=None)
        
        # Setup artifacts
        agent.get_artifacts = AsyncMock(return_value={
            "presentation_blueprint": mock_presentation_blueprint,
            "creative_brief": mock_creative_brief,
            "visual_explorations": mock_visual_explorations
        })
        
        # Should not raise exception, should use template fallback
        result = await agent.process_task(mock_task_input)
        
        assert isinstance(result, TaskOutput)
        assert result.payload["metadata"]["auditor_notes"] == "Template-based audit due to AI processing failure"

    @pytest.mark.asyncio 
    async def test_partial_artifacts_missing_creative_brief(self, agent):
        """Test behavior when creative brief is missing"""
        task_input = TaskInput(
            artifacts=[
                ArtifactReference(name="presentation_blueprint", source_task_id=103),
                ArtifactReference(name="visual_explorations", source_task_id=102)
            ],
            params={}
        )
        
        agent.get_artifacts = AsyncMock(return_value={
            "presentation_blueprint": {"presentation_blueprint": [{"slide_number": 1}]},
            "visual_explorations": {"selected_theme": "Professional"}
        })
        
        # Should work but with reduced quality warning
        result = await agent.process_task(task_input)
        assert isinstance(result, TaskOutput)

    def test_action_title_detection_edge_cases(self, agent):
        """Test enhanced action title detection"""
        # Test cases for improved logic
        test_blueprint = {
            "presentation_blueprint": [
                {"slide_number": 1, "elements": {"title": "Overview of Market Trends"}},  # Topic indicator
                {"slide_number": 2, "elements": {"title": "What We Need to Know"}},       # Topic indicator  
                {"slide_number": 3, "elements": {"title": "Background Information"}},     # Topic indicator
                {"slide_number": 4, "elements": {"title": "Revenue Will Increase by 20%"}}, # Action indicator
                {"slide_number": 5, "elements": {"title": "Market Growth Shows Promise"}}   # Action indicator
            ]
        }
        
        result = agent._generate_template_audit(
            test_blueprint, {"purpose": "test"}, {"theme": "test"}
        )
        
        # Should detect 3 weak titles (Overview, What, Background)
        warnings = result["warnings"]
        action_title_warnings = [w for w in warnings if w["type"] == "POTENTIAL_VIOLATION_OF_ACTION_TITLE"]
        assert len(action_title_warnings) > 0

    def test_protocol_compliance_consistency(self, agent, mock_presentation_blueprint,
                                           mock_creative_brief, mock_visual_explorations):
        """Test protocol compliance structure consistency"""
        # Test template audit
        template_result = agent._generate_template_audit(
            mock_presentation_blueprint, mock_creative_brief, mock_visual_explorations
        )
        
        assert "protocol_compliance" in template_result
        protocol_compliance = template_result["protocol_compliance"]
        
        # Check all required protocols
        required_protocols = ["pyramid_principle", "narrative_flow", "structural_integrity", "audience_alignment"]
        for protocol in required_protocols:
            assert protocol in protocol_compliance
            assert "overall_score" in protocol_compliance[protocol]
            assert isinstance(protocol_compliance[protocol]["overall_score"], int)

    def test_enhanced_input_validation(self, agent):
        """Test enhanced input validation logic"""
        # Test missing presentation_blueprint array
        task_input = TaskInput(
            artifacts=[ArtifactReference(name="presentation_blueprint", source_task_id=103)],
            params={}
        )
        
        agent.get_artifacts = AsyncMock(return_value={
            "presentation_blueprint": {"strategic_choice": "something"}  # Missing presentation_blueprint array
        })
        
        with pytest.raises(ValueError, match="must contain 'presentation_blueprint' array"):
            await agent.process_task(task_input)