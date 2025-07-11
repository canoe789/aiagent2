#!/usr/bin/env python3
"""
Comprehensive tests for Creative Director Agent (AGENT_1)
Generated by Flash model based on DeepSeek code review findings

Focus areas:
- Schema validation implementation
- AI integration and fallback mechanisms  
- Template generation quality
- Error handling and edge cases
"""

import pytest
import asyncio
import json
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Add project path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.creative_director import CreativeDirectorAgent
from database.models import TaskInput, TaskOutput
from ai_clients.client_factory import AIClientFactory
from ai_clients.base_client import AIModelError


class TestCreativeDirectorAgent:
    """Comprehensive test suite for Creative Director Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create a Creative Director agent instance"""
        return CreativeDirectorAgent()
    
    @pytest.fixture
    def valid_task_input(self):
        """Valid task input for testing"""
        return TaskInput(
            artifacts=[],
            params={
                "chat_input": "Create a modern e-commerce website for selling handmade jewelry. Target audience is women aged 25-45 who value artisanal crafts.",
                "session_id": "test_session_001"
            }
        )
    
    @pytest.fixture
    def complex_task_input(self):
        """Complex task input to test schema validation"""
        return TaskInput(
            artifacts=[],
            params={
                "chat_input": "Design a comprehensive financial platform that serves both retail investors and institutional clients. The platform needs to handle real-time trading, portfolio management, risk assessment, regulatory compliance (SOX, GDPR), multi-currency support, and advanced analytics. Target users include day traders, portfolio managers, compliance officers, and C-suite executives.",
                "session_id": "complex_test_001"
            }
        )

    @pytest.mark.asyncio
    async def test_schema_validation_comprehensive(self, agent, valid_task_input):
        """Test that output strictly conforms to CreativeBrief_v1.0 schema"""
        
        # Mock AI client to return valid JSON
        mock_ai_response = {
            "content": json.dumps({
                "project_overview": {
                    "title": "Artisan Jewelry E-commerce Platform",
                    "type": "ecommerce",
                    "description": "Modern online marketplace for handmade jewelry",
                    "key_themes": ["artisanal", "premium", "modern"]
                },
                "objectives": {
                    "primary_goal": "Create compelling online presence for artisan jewelry sales",
                    "secondary_goals": ["Build trust with customers", "Showcase craftsmanship"],
                    "success_metrics": ["Conversion rate", "Customer satisfaction", "Revenue growth"]
                },
                "target_audience": {
                    "primary_audience": "Women aged 25-45 interested in artisanal jewelry",
                    "audience_characteristics": {
                        "demographics": "Professional women with disposable income",
                        "psychographics": "Value uniqueness and quality",
                        "behavior_patterns": "Research before purchasing",
                        "pain_points": "Finding authentic handmade jewelry"
                    }
                },
                "creative_strategy": {
                    "tone_of_voice": "Elegant and authentic",
                    "key_messages": ["Unique handcrafted pieces", "Quality materials"],
                    "creative_approach": "Visual storytelling with product focus"
                },
                "content_requirements": {
                    "content_types": ["Product catalog", "Artist stories", "Process videos"],
                    "information_hierarchy": {
                        "primary": 1,
                        "secondary": 2,
                        "tertiary": 3
                    },
                    "call_to_action": "Shop now"
                }
            }),
            "provider": "deepseek",
            "model": "deepseek-chat",
            "usage": {"total_tokens": 150}
        }
        
        with patch.object(AIClientFactory, 'create_client') as mock_factory:
            mock_client = AsyncMock()
            mock_client.generate_response.return_value = mock_ai_response
            mock_factory.return_value = mock_client
            
            result = await agent.process_task(valid_task_input)
            
            # Validate output structure
            assert isinstance(result, TaskOutput)
            assert result.schema_id == "CreativeBrief_v1.0"
            
            # Validate required top-level sections
            required_sections = ["project_overview", "objectives", "target_audience", 
                               "creative_strategy", "content_requirements", "metadata"]
            for section in required_sections:
                assert section in result.payload, f"Missing required section: {section}"
            
            # Validate project_overview structure
            project_overview = result.payload["project_overview"]
            assert "title" in project_overview
            assert "type" in project_overview
            assert "description" in project_overview
            assert "key_themes" in project_overview
            assert isinstance(project_overview["key_themes"], list)
            
            # Validate objectives structure
            objectives = result.payload["objectives"]
            assert "primary_goal" in objectives
            assert "secondary_goals" in objectives
            assert "success_metrics" in objectives
            assert isinstance(objectives["secondary_goals"], list)
            assert isinstance(objectives["success_metrics"], list)
            
            # Validate target_audience structure
            target_audience = result.payload["target_audience"]
            assert "primary_audience" in target_audience
            assert "audience_characteristics" in target_audience
            
            audience_chars = target_audience["audience_characteristics"]
            expected_chars = ["demographics", "psychographics", "behavior_patterns", "pain_points"]
            for char in expected_chars:
                assert char in audience_chars, f"Missing audience characteristic: {char}"
            
            # Validate creative_strategy structure
            creative_strategy = result.payload["creative_strategy"]
            assert "tone_of_voice" in creative_strategy
            assert "key_messages" in creative_strategy
            assert "creative_approach" in creative_strategy
            assert isinstance(creative_strategy["key_messages"], list)
            
            # Validate content_requirements structure
            content_req = result.payload["content_requirements"]
            assert "content_types" in content_req
            assert "information_hierarchy" in content_req
            assert "call_to_action" in content_req
            assert isinstance(content_req["content_types"], list)
            
            # Validate metadata
            metadata = result.payload["metadata"]
            assert "created_by" in metadata
            assert "version" in metadata
            assert metadata["created_by"] == "AGENT_1"

    @pytest.mark.asyncio
    async def test_ai_integration_success(self, agent, valid_task_input):
        """Test successful AI model integration"""
        
        mock_ai_response = {
            "content": json.dumps({
                "project_overview": {"title": "Test Project", "type": "website", 
                                   "description": "Test", "key_themes": ["modern"]},
                "objectives": {"primary_goal": "Test goal", "secondary_goals": [], "success_metrics": []},
                "target_audience": {"primary_audience": "Test audience", 
                                  "audience_characteristics": {"demographics": "Test", "psychographics": "Test", 
                                                             "behavior_patterns": "Test", "pain_points": "Test"}},
                "creative_strategy": {"tone_of_voice": "Test", "key_messages": [], "creative_approach": "Test"},
                "content_requirements": {"content_types": [], "information_hierarchy": {"primary": 1}, "call_to_action": "Test"}
            }),
            "provider": "deepseek",
            "model": "deepseek-chat",
            "usage": {"total_tokens": 100}
        }
        
        with patch.object(AIClientFactory, 'create_client') as mock_factory:
            mock_client = AsyncMock()
            mock_client.generate_response.return_value = mock_ai_response
            mock_factory.return_value = mock_client
            
            result = await agent.process_task(valid_task_input)
            
            # Verify AI was called
            mock_client.generate_response.assert_called_once()
            
            # Verify AI metadata is present
            metadata = result.payload["metadata"]
            assert metadata["ai_model"] == "deepseek-chat"
            assert metadata["ai_provider"] == "deepseek"
            assert metadata["tokens_used"] == 100

    @pytest.mark.asyncio
    async def test_ai_fallback_mechanism(self, agent, valid_task_input):
        """Test fallback to template when AI fails"""
        
        with patch.object(AIClientFactory, 'create_client') as mock_factory:
            mock_client = AsyncMock()
            mock_client.generate_response.side_effect = AIModelError("API Error", "deepseek")
            mock_factory.return_value = mock_client
            
            result = await agent.process_task(valid_task_input)
            
            # Verify fallback was used
            metadata = result.payload["metadata"]
            assert metadata["ai_model"] == "template_fallback"
            
            # Verify structure is still valid
            assert result.schema_id == "CreativeBrief_v1.0"
            assert "project_overview" in result.payload

    @pytest.mark.asyncio
    async def test_invalid_json_handling(self, agent, valid_task_input):
        """Test handling of invalid JSON from AI"""
        
        mock_ai_response = {
            "content": "This is not valid JSON content",
            "provider": "deepseek",
            "model": "deepseek-chat",
            "usage": {"total_tokens": 50}
        }
        
        with patch.object(AIClientFactory, 'create_client') as mock_factory:
            mock_client = AsyncMock()
            mock_client.generate_response.return_value = mock_ai_response
            mock_factory.return_value = mock_client
            
            result = await agent.process_task(valid_task_input)
            
            # Should fallback to template
            metadata = result.payload["metadata"]
            assert metadata["ai_model"] == "template_fallback"

    @pytest.mark.asyncio
    async def test_markdown_json_parsing(self, agent, valid_task_input):
        """Test parsing JSON wrapped in markdown code blocks"""
        
        json_content = {
            "project_overview": {"title": "Test", "type": "website", "description": "Test", "key_themes": []},
            "objectives": {"primary_goal": "Test", "secondary_goals": [], "success_metrics": []},
            "target_audience": {"primary_audience": "Test", "audience_characteristics": {"demographics": "Test", "psychographics": "Test", "behavior_patterns": "Test", "pain_points": "Test"}},
            "creative_strategy": {"tone_of_voice": "Test", "key_messages": [], "creative_approach": "Test"},
            "content_requirements": {"content_types": [], "information_hierarchy": {"primary": 1}, "call_to_action": "Test"}
        }
        
        mock_ai_response = {
            "content": f"```json\n{json.dumps(json_content)}\n```",
            "provider": "deepseek",
            "model": "deepseek-chat",
            "usage": {"total_tokens": 80}
        }
        
        with patch.object(AIClientFactory, 'create_client') as mock_factory:
            mock_client = AsyncMock()
            mock_client.generate_response.return_value = mock_ai_response
            mock_factory.return_value = mock_client
            
            result = await agent.process_task(valid_task_input)
            
            # Should successfully parse JSON
            metadata = result.payload["metadata"]
            assert metadata["ai_model"] == "deepseek-chat"
            assert metadata["ai_provider"] == "deepseek"

    @pytest.mark.asyncio
    async def test_template_quality_validation(self, agent, valid_task_input):
        """Test quality of template fallback generation"""
        
        # Force template fallback
        with patch.object(agent, '_generate_with_ai', return_value=None):
            result = await agent.process_task(valid_task_input)
            
            # Validate template quality
            payload = result.payload
            
            # Should extract meaningful information from input
            project_overview = payload["project_overview"]
            assert "jewelry" in project_overview["title"].lower() or "handmade" in project_overview["title"].lower()
            assert project_overview["type"] == "ecommerce"
            
            # Should identify themes
            themes = project_overview["key_themes"]
            assert len(themes) > 0
            
            # Should identify audience
            target_audience = payload["target_audience"]
            assert "women" in target_audience["primary_audience"].lower()

    @pytest.mark.asyncio
    async def test_edge_cases(self, agent):
        """Test various edge cases and error conditions"""
        
        # Test empty input
        empty_input = TaskInput(artifacts=[], params={"chat_input": "", "session_id": "test"})
        result = await agent.process_task(empty_input)
        assert result.schema_id == "CreativeBrief_v1.0"
        
        # Test very long input
        long_input = TaskInput(
            artifacts=[], 
            params={
                "chat_input": "A" * 5000,  # 5000 character input
                "session_id": "test"
            }
        )
        result = await agent.process_task(long_input)
        assert result.schema_id == "CreativeBrief_v1.0"
        
        # Test missing session_id
        no_session_input = TaskInput(artifacts=[], params={"chat_input": "Test project"})
        result = await agent.process_task(no_session_input)
        assert result.schema_id == "CreativeBrief_v1.0"

    @pytest.mark.asyncio
    async def test_confidence_scoring(self, agent, valid_task_input, complex_task_input):
        """Test confidence scoring in template generation"""
        
        # Test simple input (should have higher confidence)
        with patch.object(agent, '_generate_with_ai', return_value=None):
            simple_result = await agent.process_task(valid_task_input)
            simple_confidence = simple_result.payload["metadata"]["confidence_score"]
            
            # Test complex input (should have lower confidence)
            complex_result = await agent.process_task(complex_task_input)
            complex_confidence = complex_result.payload["metadata"]["confidence_score"]
            
            # Simple input should have higher confidence than complex
            assert simple_confidence >= complex_confidence
            assert 0 <= simple_confidence <= 1
            assert 0 <= complex_confidence <= 1

    @pytest.mark.asyncio
    async def test_theme_extraction_accuracy(self, agent):
        """Test accuracy of theme extraction from various inputs"""
        
        test_cases = [
            {
                "input": "Create a modern, minimalist website for a tech startup",
                "expected_themes": ["modern", "tech"]
            },
            {
                "input": "Design a professional corporate website for a law firm",
                "expected_themes": ["professional"]
            },
            {
                "input": "Build a creative portfolio site for an artist",
                "expected_themes": ["creative"]
            },
            {
                "input": "Develop a user-friendly e-commerce platform with premium feel",
                "expected_themes": ["user-friendly", "premium"]
            }
        ]
        
        for case in test_cases:
            themes = agent._extract_themes(case["input"])
            
            # At least one expected theme should be found
            found_expected = any(expected in themes for expected in case["expected_themes"])
            assert found_expected, f"No expected themes found in: {themes} for input: {case['input']}"

    @pytest.mark.asyncio  
    async def test_project_type_identification(self, agent):
        """Test accuracy of project type identification"""
        
        test_cases = [
            ("Build a website for my company", "website"),
            ("Create an e-commerce store", "ecommerce"),
            ("Develop a mobile app", "application"),
            ("Design a portfolio", "portfolio"),
            ("Corporate business site", "corporate"),
            ("Start a blog platform", "blog")
        ]
        
        for input_text, expected_type in test_cases:
            project_type = agent._identify_project_type(input_text)
            assert project_type == expected_type, f"Expected {expected_type}, got {project_type} for: {input_text}"

    @pytest.mark.asyncio
    async def test_concurrent_processing(self, agent):
        """Test agent behavior under concurrent load"""
        
        # Create multiple task inputs
        inputs = [
            TaskInput(artifacts=[], params={"chat_input": f"Project {i}", "session_id": f"session_{i}"})
            for i in range(5)
        ]
        
        # Process concurrently
        with patch.object(agent, '_generate_with_ai', return_value=None):  # Force template mode for speed
            tasks = [agent.process_task(input_item) for input_item in inputs]
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(results) == 5
            for result in results:
                assert result.schema_id == "CreativeBrief_v1.0"
                assert "metadata" in result.payload

    def test_helper_methods(self, agent):
        """Test various helper methods in isolation"""
        
        # Test title generation
        title = agent._generate_project_title("Create a modern website for my startup company")
        assert len(title) > 0
        assert "Create a modern website for" in title
        
        # Test audience identification
        audience = agent._identify_audience("targeting young professionals and students")
        assert "young" in audience.lower() or "student" in audience.lower() or "professional" in audience.lower()
        
        # Test tone determination
        tone = agent._determine_tone("professional business website", ["professional"])
        assert "professional" in tone.lower()
        
        # Test call to action extraction
        cta = agent._extract_call_to_action("users should contact us for more information")
        assert "contact" in cta.lower()


if __name__ == "__main__":
    # Run specific tests
    pytest.main([__file__, "-v"])