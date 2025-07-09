"""
Concept Alchemist / Visual Philosopher Agent for Project HELIX v2.0
AGENT_2: Transforms creative briefs into visual theme explorations through philosophical inquiry
"""

import structlog
import json
from typing import Dict, Any, List, Optional

from src.sdk.agent_sdk import BaseAgent
from src.database.models import TaskInput, TaskOutput
from src.ai_clients.client_factory import AIClientFactory

logger = structlog.get_logger(__name__)


class VisualDirectorAgent(BaseAgent):
    """
    AGENT_2: Concept Alchemist / Visual Philosopher
    
    Transforms structured creative briefs into visual theme explorations through
    philosophical inquiry, creating three distinct visual approaches that represent
    different strategic perspectives and creative worldviews.
    """
    
    def __init__(self):
        super().__init__("AGENT_2")
    
    async def process_task(self, task_input: TaskInput) -> TaskOutput:
        """
        Process creative brief and create visual theme explorations
        
        Input: creative_brief artifact from AGENT_1
        Output: Three visual themes with philosophical foundations
        """
        try:
            logger.info("Processing visual theme exploration request", 
                       agent_id=self.agent_id,
                       artifact_count=len(task_input.artifacts))
            
            # Get creative brief artifact from AGENT_1
            artifacts = await self.get_artifacts(task_input.artifacts)
            if "creative_brief" not in artifacts:
                raise ValueError("Required creative_brief artifact not found")
            
            creative_brief = artifacts["creative_brief"]["payload"]
            
            # Get agent prompt from database (P3: Externalized Cognition)
            system_prompt = await self.get_agent_prompt()
            if not system_prompt:
                raise ValueError("No prompt found for AGENT_2 in database - violates P3 principle")
            
            # Generate visual explorations using AI-first approach
            visual_explorations = await self._generate_visual_explorations(
                creative_brief, system_prompt
            )
            
            # Log successful processing
            style_direction = visual_explorations.get("style_direction", {})
            style_summary = (
                style_direction.get("primary_style", "unknown") if isinstance(style_direction, dict)
                else str(style_direction)[:50]
            )
            
            await self.log_system_event(
                "INFO", 
                "Visual explorations generated successfully",
                {
                    "visual_themes_count": len(visual_explorations.get("visual_themes", [])),
                    "style_direction": style_summary
                }
            )
            
            return TaskOutput(
                schema_id="VisualExplorations_v1.0",
                payload=visual_explorations
            )
            
        except Exception as e:
            logger.error("Failed to process visual explorations", 
                        agent_id=self.agent_id, error=str(e))
            
            await self.log_system_event(
                "ERROR",
                f"Visual explorations generation failed: {str(e)}"
            )
            
            raise
    
    async def _generate_visual_explorations(self, creative_brief: Dict[str, Any], system_prompt: str) -> Dict[str, Any]:
        """
        Generate visual theme explorations from creative brief
        Uses AI-first approach with template fallback (AGENT_1 pattern)
        """
        
        try:
            # Try AI generation first (AGENT_1 pattern)
            ai_response = await self._generate_with_ai(creative_brief, system_prompt)
            if ai_response:
                return ai_response
                
        except Exception as e:
            logger.warning("AI generation failed, falling back to template", error=str(e))
        
        # Fallback to template-based generation (AGENT_1 pattern)
        return await self._generate_template_visual_explorations(creative_brief)
    
    async def _generate_with_ai(self, creative_brief: Dict[str, Any], system_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate visual explorations using AI model (AGENT_1 architecture)
        """
        try:
            # Create AI client
            ai_client = AIClientFactory.create_client()
            
            # Enhanced system prompt for JSON output matching schema exactly
            enhanced_prompt = f"""{system_prompt}

CRITICAL: You must respond with VALID JSON only. Do not include any text before or after the JSON.
The JSON must follow this EXACT structure to match VisualExplorations_v1.0 schema:

{{
  "visual_themes": [
    {{
      "name": "string",
      "description": "string",
      "mood": "string",
      "inspiration": "string"
    }}
  ],
  "style_direction": {{
    "primary_style": "string",
    "visual_language": "string",
    "aesthetic_principles": ["string"]
  }},
  "color_palette": {{
    "primary_colors": ["#HEXCODE"],
    "secondary_colors": ["#HEXCODE"],
    "accent_colors": ["#HEXCODE"],
    "color_psychology": "string"
  }},
  "typography": {{
    "primary_font": "string",
    "secondary_font": "string", 
    "font_hierarchy": "string",
    "readability_notes": "string"
  }},
  "layout_principles": {{
    "grid_system": "string",
    "spacing_system": "string",
    "responsive_approach": "string"
  }},
  "visual_elements": {{
    "icons_style": "string",
    "imagery_style": "string",
    "graphic_elements": ["string"]
  }}
}}

Remember: Follow your concept alchemy process internally, but output ONLY the final JSON result that exactly matches this schema."""
            
            # Prepare creative materials for the prompt
            creative_materials = {
                "creative_brief": creative_brief
            }
            
            # Convert to JSON string for prompt
            materials_json = json.dumps(creative_materials, ensure_ascii=False, indent=2)
            
            # Generate response
            response = await ai_client.generate_response(
                system_prompt=enhanced_prompt,
                user_input=f"CREATIVE_MATERIALS:\n\n{materials_json}",
                temperature=0.7,
                max_tokens=3000
            )
            
            content = response["content"].strip()
            
            # Parse JSON response (AGENT_1 pattern)
            return self._parse_ai_response(content, response)
                
        except Exception as e:
            logger.error("AI generation failed", error=str(e))
            raise

    def _parse_ai_response(self, content: str, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse AI response with markdown cleanup (AGENT_1 pattern)
        """
        try:
            # Remove markdown formatting (AGENT_1 pattern)
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            # Parse JSON
            visual_explorations = json.loads(content.strip())
            
            # Add metadata (AGENT_1 pattern)
            if "metadata" not in visual_explorations:
                visual_explorations["metadata"] = {}
                
            visual_explorations["metadata"].update({
                "created_by": "AGENT_2",
                "version": "1.0",
                "ai_model": response.get("model", "unknown"),
                "ai_provider": response.get("provider", "unknown"),
                "tokens_used": response.get("usage", {}).get("total_tokens", 0),
                "processing_notes": f"AI-generated visual explorations"
            })
            
            logger.info("AI visual explorations generated successfully",
                       model=response.get("model"),
                       tokens=response.get("usage", {}).get("total_tokens", 0))
            
            return visual_explorations
            
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse AI response as JSON", 
                          content_preview=content[:200],
                          error=str(e))
            return None
    
    async def _generate_template_visual_explorations(self, creative_brief: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate visual explorations using template-based approach (fallback)
        """
        
        # Extract key information from creative brief
        project_overview = creative_brief.get("project_overview", {})
        objectives = creative_brief.get("objectives", {})
        target_audience = creative_brief.get("target_audience", {})
        creative_strategy = creative_brief.get("creative_strategy", {})
        
        # Create three visual themes using template-based approach
        visual_themes = self._create_template_visual_themes(creative_brief)
        
        # Template visual explorations matching schema exactly
        visual_explorations = {
            "visual_themes": visual_themes,
            "style_direction": {
                "primary_style": f"Template-generated {project_overview.get('type', 'general')} design",
                "visual_language": f"{creative_strategy.get('tone_of_voice', 'professional')} and modern",
                "aesthetic_principles": [
                    "Clean and professional presentation",
                    "Consistent visual hierarchy", 
                    "Accessibility-focused design"
                ]
            },
            "color_palette": {
                "primary_colors": ["#2563EB", "#1E40AF"],
                "secondary_colors": ["#64748B", "#374151"],
                "accent_colors": ["#F8FAFC", "#E5E7EB"],
                "color_psychology": "Professional blue conveys trust and reliability, while neutral grays provide balance"
            },
            "typography": {
                "primary_font": "Inter",
                "secondary_font": "Inter",
                "font_hierarchy": "Clear hierarchy with 1.2 ratio scale",
                "readability_notes": "Optimized for screen reading with high contrast"
            },
            "layout_principles": {
                "grid_system": "12-column responsive grid system",
                "spacing_system": "8px baseline grid with consistent margins",
                "responsive_approach": "Mobile-first design with progressive enhancement"
            },
            "visual_elements": {
                "icons_style": "Modern, minimal line icons with consistent stroke weight",
                "imagery_style": "Clean, professional photography with consistent filter treatment",
                "graphic_elements": [
                    "Subtle gradients",
                    "Clean geometric shapes",
                    "Consistent border radius"
                ]
            },
            "metadata": {
                "created_by": "AGENT_2",
                "version": "1.0",
                "ai_model": "template_fallback",
                "confidence_score": self._calculate_template_confidence(creative_brief),
                "processing_notes": f"Template-generated visual explorations from creative brief"
            }
        }
        
        return visual_explorations
    
    def _create_template_visual_themes(self, creative_brief: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create three template visual themes representing different philosophical approaches
        """
        project_overview = creative_brief.get("project_overview", {})
        creative_strategy = creative_brief.get("creative_strategy", {})
        themes = project_overview.get("key_themes", [])
        tone = creative_strategy.get("tone_of_voice", "professional")
        
        # Theme 1: Faithful Interpretation (直接演绎) - Schema compliant
        theme1 = {
            "name": "The Direct Voice",
            "description": "【忠实演绎】This theme directly amplifies the core metaphors and messaging from the creative brief. It takes the most literal and straightforward approach to visual representation, ensuring maximum clarity and immediate recognition. Layout follows conventional best practices with clear hierarchy.",
            "mood": f"Professional and {tone}, emphasizing clarity and trustworthiness",
            "inspiration": "Classic corporate design principles with modern refinement, inspired by leading tech companies"
        }
        
        # Theme 2: Abstract Translation (抽象转译) - Schema compliant
        theme2 = {
            "name": "The Conceptual Bridge", 
            "description": "【抽象转译】This theme strips away literal interpretations to focus on the emotional core and functional purpose. It translates the underlying feelings and objectives into a fresh visual language with asymmetrical layouts, organic shapes and flowing lines.",
            "mood": f"Warm and approachable while maintaining {tone} credibility",
            "inspiration": "Scandinavian design philosophy meets modern digital interfaces, drawing from natural forms"
        }
        
        # Theme 3: Contrarian Challenge (逆向挑战) - Schema compliant
        theme3 = {
            "name": "The Bold Disruption",
            "description": "【逆向挑战】This theme challenges conventional assumptions about the project requirements. It creates a deliberately provocative visual system with dramatic layouts, stark contrasts and bold geometric shapes using negative space as a primary design element.",
            "mood": f"Bold and confident, challenging {tone} expectations with striking visual impact",
            "inspiration": "Swiss typography meets contemporary art galleries, influenced by minimalist architecture"
        }
        
        return [theme1, theme2, theme3]
    
    def _calculate_template_confidence(self, creative_brief: Dict[str, Any]) -> float:
        """Calculate confidence score for template generation"""
        required_sections = ["project_overview", "objectives", "target_audience", "creative_strategy"]
        present_sections = sum(1 for section in required_sections if section in creative_brief)
        
        base_confidence = 0.6  # Lower than AI confidence
        completeness_bonus = (present_sections / len(required_sections)) * 0.2
        
        return min(base_confidence + completeness_bonus, 0.85)
    
    


# Example usage for testing
async def test_visual_director():
    """Test function for the Visual Director Agent"""
    agent = VisualDirectorAgent()
    
    # Mock creative brief from AGENT_1
    mock_creative_brief = {
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
    
    # Test input with mock artifact
    test_input = TaskInput(
        artifacts=[{"name": "creative_brief", "source_task_id": 101}],
        params={}
    )
    
    try:
        # Mock the get_artifacts method for testing
        async def mock_get_artifacts(refs):
            return {
                "creative_brief": {
                    "payload": mock_creative_brief,
                    "schema_id": "CreativeBrief_v1.0"
                }
            }
        
        agent.get_artifacts = mock_get_artifacts
        
        result = await agent.process_task(test_input)
        print("Visual Explorations Generated:")
        print(f"Schema: {result.schema_id}")
        print(f"Visual Themes Count: {len(result.payload['visual_themes'])}")
        style_dir = result.payload['style_direction']
        style_summary = style_dir.get('primary_style', str(style_dir)[:50]) if isinstance(style_dir, dict) else str(style_dir)[:50]
        print(f"Style Direction: {style_summary}...")
        print(f"Color Palette: {result.payload['color_palette']}")
        for i, theme in enumerate(result.payload['visual_themes']):
            print(f"Theme {i+1}: {theme['name']}")
        
        return result
        
    except Exception as e:
        print(f"Test failed: {e}")
        return None


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_visual_director())