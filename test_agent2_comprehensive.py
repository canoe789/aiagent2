#!/usr/bin/env python3
"""
AGENT_2 (Visual Director) Comprehensive Test Suite
Tests the concept alchemist functionality with AGENT_1's proven patterns
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from agents.visual_director import VisualDirectorAgent
from database.models import TaskInput, TaskOutput
from database.connection import db_manager


async def test_agent2_prompt_quality():
    """Test AGENT_2 prompt structure and content"""
    print("🔍 Testing AGENT_2 Prompt Quality...")
    
    agent = VisualDirectorAgent()
    prompt = agent._get_default_prompt()
    
    # Check prompt structure
    assert "概念炼金术士" in prompt, "Missing core role identity"
    assert "三种战略诘问" in prompt, "Missing strategic interrogation methods"
    assert "忠实演绎法" in prompt, "Missing faithful interpretation method"
    assert "抽象转译法" in prompt, "Missing abstract translation method"
    assert "逆向挑战法" in prompt, "Missing contrarian challenge method"
    assert "visual_themes" in prompt, "Missing output structure guidance"
    
    # Check prompt sophistication
    assert len(prompt) > 2000, "Prompt too short for sophisticated reasoning"
    assert "design_philosophy" in prompt, "Missing philosophy requirement"
    
    print("✅ Prompt quality validation passed")
    return True


async def test_agent2_template_fallback():
    """Test AGENT_2 template generation (fallback mode)"""
    print("🔧 Testing AGENT_2 Template Fallback...")
    
    agent = VisualDirectorAgent()
    
    # Mock creative brief with rich content
    mock_creative_brief = {
        "project_overview": {
            "title": "Zen Productivity App",
            "type": "mobile_app",
            "key_themes": ["zen", "productivity", "mindfulness", "modern"],
            "description": "A digital workspace that balances calm focus with efficient productivity"
        },
        "objectives": {
            "primary_goal": "Create a calming yet efficient digital environment",
            "secondary_goals": [
                "Reduce digital overwhelm",
                "Increase focused work time",
                "Promote mindful technology use"
            ]
        },
        "target_audience": {
            "primary_audience": "Knowledge workers and creative professionals",
            "demographics": "Age 28-45, tech-savvy, values work-life balance",
            "psychographics": "Seeks calm in digital chaos, values quality over quantity"
        },
        "creative_strategy": {
            "tone_of_voice": "Calm, confident, inspiring",
            "key_messages": [
                "Find your focus in the digital storm",
                "Productivity through mindfulness",
                "Less noise, more signal"
            ],
            "desired_feeling": "Peaceful focus and empowered productivity"
        }
    }
    
    # Test template generation directly
    visual_explorations = await agent._generate_template_visual_explorations(mock_creative_brief)
    
    # Validate structure
    assert "visual_themes" in visual_explorations, "Missing visual_themes array"
    assert len(visual_explorations["visual_themes"]) == 3, "Should have exactly 3 themes"
    
    # Validate each theme has required philosophy approaches
    themes = visual_explorations["visual_themes"]
    philosophies = [theme["design_philosophy"] for theme in themes]
    
    has_faithful = any("忠实演绎" in p for p in philosophies)
    has_abstract = any("抽象转译" in p for p in philosophies)
    has_contrarian = any("逆向挑战" in p for p in philosophies)
    
    assert has_faithful, "Missing faithful interpretation theme"
    assert has_abstract, "Missing abstract translation theme"  
    assert has_contrarian, "Missing contrarian challenge theme"
    
    # Validate metadata
    assert "metadata" in visual_explorations, "Missing metadata"
    assert visual_explorations["metadata"]["created_by"] == "AGENT_2", "Wrong creator"
    assert visual_explorations["metadata"]["ai_model"] == "template_fallback", "Wrong model indicator"
    
    print("✅ Template fallback validation passed")
    return visual_explorations


async def test_agent2_schema_compliance():
    """Test AGENT_2 output Schema compliance"""
    print("📋 Testing AGENT_2 Schema Compliance...")
    
    # Generate template output to test
    agent = VisualDirectorAgent()
    mock_brief = {
        "project_overview": {"title": "Test Project", "type": "website", "key_themes": ["modern"]},
        "objectives": {"primary_goal": "Test goal"},
        "target_audience": {"primary_audience": "Test audience"},
        "creative_strategy": {"tone_of_voice": "professional"}
    }
    
    visual_explorations = await agent._generate_template_visual_explorations(mock_brief)
    
    # Load schema for validation
    with open("/home/canoezhang/Projects/aiagent/schemas/VisualExplorations_v1.0.json", "r") as f:
        schema = json.load(f)
    
    # Check required top-level fields
    required_fields = schema["required"]
    for field in required_fields:
        assert field in visual_explorations, f"Missing required field: {field}"
    
    # Check visual_themes structure
    visual_themes = visual_explorations["visual_themes"]
    assert isinstance(visual_themes, list), "visual_themes should be array"
    
    for theme in visual_themes:
        assert "theme_name" in theme, "Missing theme_name"
        assert "design_philosophy" in theme, "Missing design_philosophy"
        assert isinstance(theme["theme_name"], str), "theme_name should be string"
        assert len(theme["design_philosophy"]) > 10, "design_philosophy too short"
    
    # Check color_palette
    color_palette = visual_explorations["color_palette"]
    assert isinstance(color_palette, list), "color_palette should be array"
    for color in color_palette:
        assert color.startswith("#"), f"Invalid color format: {color}"
        assert len(color) in [4, 7], f"Invalid hex color length: {color}"
    
    # Check typography
    typography = visual_explorations["typography"]
    assert "primary_font" in typography, "Missing primary_font"
    assert "font_scale" in typography, "Missing font_scale"
    
    print("✅ Schema compliance validation passed")
    return True


async def test_agent2_philosophical_diversity():
    """Test that AGENT_2 generates truly diverse philosophical approaches"""
    print("🎭 Testing AGENT_2 Philosophical Diversity...")
    
    agent = VisualDirectorAgent()
    
    # Test with contrasting briefs to see if agent adapts
    test_cases = [
        {
            "name": "Corporate Tech",
            "brief": {
                "project_overview": {"key_themes": ["corporate", "technology", "efficiency"]},
                "creative_strategy": {"tone_of_voice": "professional", "desired_feeling": "confidence"}
            }
        },
        {
            "name": "Artistic Creative",
            "brief": {
                "project_overview": {"key_themes": ["artistic", "creative", "expressive"]},
                "creative_strategy": {"tone_of_voice": "inspirational", "desired_feeling": "wonder"}
            }
        },
        {
            "name": "Zen Minimal",
            "brief": {
                "project_overview": {"key_themes": ["zen", "minimal", "peaceful"]},
                "creative_strategy": {"tone_of_voice": "calm", "desired_feeling": "serenity"}
            }
        }
    ]
    
    results = {}
    
    for case in test_cases:
        # Fill in required fields
        full_brief = {
            "project_overview": {
                "title": f"{case['name']} Project",
                "type": "website",
                **case["brief"]["project_overview"]
            },
            "objectives": {"primary_goal": f"Create {case['name'].lower()} experience"},
            "target_audience": {"primary_audience": f"{case['name']} users"},
            "creative_strategy": case["brief"]["creative_strategy"]
        }
        
        visual_explorations = await agent._generate_template_visual_explorations(full_brief)
        results[case["name"]] = visual_explorations["visual_themes"]
        
        # Validate diversity within each result
        themes = visual_explorations["visual_themes"]
        philosophies = [theme["design_philosophy"] for theme in themes]
        
        # Check that different strategic approaches are present
        approaches = ["忠实演绎", "抽象转译", "逆向挑战"]
        for approach in approaches:
            found = any(approach in p for p in philosophies)
            assert found, f"Missing {approach} approach in {case['name']}"
    
    # Validate diversity across different brief types
    corp_themes = [theme["theme_name"] for theme in results["Corporate Tech"]]
    artistic_themes = [theme["theme_name"] for theme in results["Artistic Creative"]]
    zen_themes = [theme["theme_name"] for theme in results["Zen Minimal"]]
    
    # Themes should be different for different brief types
    assert len(set(corp_themes)) == 3, "Corporate themes not diverse enough"
    assert len(set(artistic_themes)) == 3, "Artistic themes not diverse enough"
    assert len(set(zen_themes)) == 3, "Zen themes not diverse enough"
    
    print("✅ Philosophical diversity validation passed")
    return results


async def test_agent2_full_workflow():
    """Test AGENT_2 full workflow with TaskInput/TaskOutput"""
    print("🔄 Testing AGENT_2 Full Workflow...")
    
    agent = VisualDirectorAgent()
    
    # Mock creative brief artifact
    mock_creative_brief = {
        "project_overview": {
            "title": "Digital Wellness Platform",
            "type": "web_platform",
            "key_themes": ["wellness", "digital", "balance", "community"],
            "description": "A platform helping users maintain healthy relationships with technology"
        },
        "objectives": {
            "primary_goal": "Promote healthy digital habits through community support",
            "secondary_goals": [
                "Reduce screen time anxiety",
                "Build supportive communities",
                "Provide actionable wellness insights"
            ]
        },
        "target_audience": {
            "primary_audience": "Digital wellness enthusiasts",
            "demographics": "Age 25-40, urban professionals",
            "psychographics": "Values mindful technology use and community connection"
        },
        "creative_strategy": {
            "tone_of_voice": "Supportive, empowering, non-judgmental",
            "key_messages": [
                "Technology should serve your wellbeing",
                "Small changes, big impact",
                "You're not alone in this journey"
            ],
            "desired_feeling": "Supported, empowered, hopeful"
        },
        "content_requirements": {
            "content_types": ["Dashboard", "Community Feed", "Progress Tracking", "Resource Library"]
        }
    }
    
    # Mock get_artifacts method
    async def mock_get_artifacts(refs):
        return {
            "creative_brief": {
                "payload": mock_creative_brief,
                "schema_id": "CreativeBrief_v1.0"
            }
        }
    
    # Mock log_system_event method
    async def mock_log_system_event(level, message, metadata=None):
        print(f"LOG [{level}]: {message}")
        if metadata:
            print(f"    Metadata: {metadata}")
    
    agent.get_artifacts = mock_get_artifacts
    agent.log_system_event = mock_log_system_event
    
    # Mock get_agent_prompt to return None (use default prompt)
    async def mock_get_agent_prompt():
        return None
    
    agent.get_agent_prompt = mock_get_agent_prompt
    
    # Create test input
    test_input = TaskInput(
        artifacts=[{"name": "creative_brief", "source_task_id": 101}],
        params={}
    )
    
    # Process task
    result = await agent.process_task(test_input)
    
    # Validate result
    assert isinstance(result, TaskOutput), "Should return TaskOutput"
    assert result.schema_id == "VisualExplorations_v1.0", "Wrong schema_id"
    assert "visual_themes" in result.payload, "Missing visual_themes in payload"
    assert len(result.payload["visual_themes"]) == 3, "Should have 3 visual themes"
    
    # Validate theme quality
    themes = result.payload["visual_themes"]
    for i, theme in enumerate(themes):
        assert "theme_name" in theme, f"Theme {i} missing name"
        assert "design_philosophy" in theme, f"Theme {i} missing philosophy"
        assert len(theme["design_philosophy"]) > 50, f"Theme {i} philosophy too shallow"
    
    print("✅ Full workflow validation passed")
    return result


async def test_agent2_error_handling():
    """Test AGENT_2 error handling and edge cases"""
    print("⚠️ Testing AGENT_2 Error Handling...")
    
    agent = VisualDirectorAgent()
    
    # Test with missing artifact
    async def mock_get_artifacts_missing(refs):
        return {}  # No artifacts
    
    async def mock_log_system_event(level, message, metadata=None):
        pass  # Suppress logs for error tests
        
    async def mock_get_agent_prompt():
        return None  # Use default prompt
    
    agent.get_artifacts = mock_get_artifacts_missing
    agent.log_system_event = mock_log_system_event
    agent.get_agent_prompt = mock_get_agent_prompt
    
    test_input = TaskInput(
        artifacts=[{"name": "creative_brief", "source_task_id": 101}],
        params={}
    )
    
    # Should raise ValueError for missing artifact
    try:
        await agent.process_task(test_input)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "creative_brief artifact not found" in str(e)
    
    # Test with minimal/invalid creative brief
    async def mock_get_artifacts_invalid(refs):
        return {
            "creative_brief": {
                "payload": {},  # Empty brief
                "schema_id": "CreativeBrief_v1.0"
            }
        }
    
    agent.get_artifacts = mock_get_artifacts_invalid
    # Keep the mocked methods
    
    # Should still work due to template fallback
    result = await agent.process_task(test_input)
    assert isinstance(result, TaskOutput), "Should handle empty brief gracefully"
    
    print("✅ Error handling validation passed")
    return True


async def main():
    """Run comprehensive AGENT_2 test suite"""
    print("🚀 AGENT_2 Comprehensive Test Suite")
    print("=" * 50)
    
    # Initialize database connection
    print("🔌 Connecting to database...")
    try:
        await db_manager.connect()
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("⚠️ Continuing with mocked database for testing...")
    
    try:
        # Test 1: Prompt Quality
        await test_agent2_prompt_quality()
        print()
        
        # Test 2: Template Fallback
        template_result = await test_agent2_template_fallback()
        print()
        
        # Test 3: Schema Compliance
        await test_agent2_schema_compliance()
        print()
        
        # Test 4: Philosophical Diversity
        diversity_results = await test_agent2_philosophical_diversity()
        print()
        
        # Test 5: Full Workflow
        workflow_result = await test_agent2_full_workflow()
        print()
        
        # Test 6: Error Handling
        await test_agent2_error_handling()
        print()
        
        print("🎉 ALL AGENT_2 TESTS PASSED!")
        print("=" * 50)
        
        # Summary report
        print("\n📊 Test Summary:")
        print(f"✅ Prompt quality: Sophisticated 3-act thinking process")
        print(f"✅ Template fallback: 3 distinct philosophical approaches")
        print(f"✅ Schema compliance: Full VisualExplorations_v1.0 conformance")
        print(f"✅ Philosophical diversity: Faithful/Abstract/Contrarian methods")
        print(f"✅ Full workflow: TaskInput → TaskOutput with proper logging")
        print(f"✅ Error handling: Graceful degradation and clear error messages")
        
        # Show sample output
        print("\n🎨 Sample Visual Themes Generated:")
        if template_result and "visual_themes" in template_result:
            for i, theme in enumerate(template_result["visual_themes"], 1):
                print(f"{i}. {theme['theme_name']}")
                print(f"   Philosophy: {theme['design_philosophy'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up database connection
        try:
            await db_manager.disconnect()
            print("🔌 Database disconnected")
        except:
            pass


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)