"""
Chief Narrative Architect Agent for Project HELIX v2.0
AGENT_3: Transforms creative briefs and visual themes into structured presentation blueprints
"""

import structlog
import json
from typing import Dict, Any, List, Optional

from src.sdk.agent_sdk import BaseAgent
from src.database.models import TaskInput, TaskOutput
from src.ai_clients.client_factory import AIClientFactory

logger = structlog.get_logger(__name__)


class ChiefNarrativeArchitectAgent(BaseAgent):
    """
    AGENT_3: Chief Narrative Architect / Thought Guide
    
    Transforms creative briefs and visual themes into structured presentation blueprints,
    designing cognitive journeys that guide audiences from unknown to conviction.
    Follows Socratic thinking principles and narrative architecture methodology.
    """
    
    def __init__(self):
        super().__init__("AGENT_3")
    
    async def process_task(self, task_input: TaskInput) -> TaskOutput:
        """
        Process creative brief and visual themes to create presentation blueprint
        
        Input: creative_brief and visual_explorations artifacts from AGENT_1 and AGENT_2
        Output: Structured presentation blueprint with narrative architecture
        """
        try:
            logger.info("Processing presentation blueprint generation request", 
                       agent_id=self.agent_id,
                       artifact_count=len(task_input.artifacts))
            
            # Get required artifacts from AGENT_1 and AGENT_2
            artifacts = await self.get_artifacts(task_input.artifacts)
            
            # Validate required artifacts with minimal essential checks
            self._validate_required_artifacts(artifacts)
            
            # Check for existing output (P4: Idempotency)
            existing_output = await self._check_existing_output(task_input, artifacts)
            if existing_output:
                logger.info("Task already processed successfully, returning existing output", 
                           agent_id=self.agent_id)
                return existing_output
            
            creative_brief = artifacts["creative_brief"]["payload"]
            visual_explorations = artifacts["visual_explorations"]["payload"]
            
            # Get agent prompt from database (P3: Externalized Cognition)
            system_prompt = await self.get_agent_prompt()
            if not system_prompt:
                raise ValueError("No prompt found for AGENT_3 in database - violates P3 principle")
            
            # Generate presentation blueprint using AI-first approach
            presentation_blueprint = await self._generate_presentation_blueprint(
                creative_brief, visual_explorations, system_prompt
            )
            
            # Validate output schema (P7: Self-Description and Validation)
            if not self._validate_output_schema(presentation_blueprint):
                logger.warning("Output schema validation failed, using fallback format")
                presentation_blueprint = self._ensure_schema_compliance(presentation_blueprint)
            
            # Log successful processing  
            await self.log_system_event(
                "INFO", 
                "Presentation blueprint generated successfully",
                {
                    "content_sections": len(presentation_blueprint.get("content_sections", [])),
                    "narrative_arc": presentation_blueprint.get("narrative_structure", {}).get("narrative_arc", "unknown")[:50],
                    "story_beats": len(presentation_blueprint.get("narrative_structure", {}).get("key_story_beats", []))
                }
            )
            
            return TaskOutput(
                schema_id="PresentationBlueprint_v1.0",
                payload=presentation_blueprint
            )
            
        except Exception as e:
            logger.error("Failed to process presentation blueprint generation", 
                        agent_id=self.agent_id, error=str(e))
            
            await self.log_system_event(
                "ERROR",
                f"Presentation blueprint generation failed: {str(e)}"
            )
            
            raise
    
    async def _generate_presentation_blueprint(self, creative_brief: Dict[str, Any], visual_explorations: Dict[str, Any], system_prompt: str) -> Dict[str, Any]:
        """
        Generate presentation blueprint from creative brief and visual themes
        Uses AI-first approach with template fallback (AGENT_1 pattern)
        """
        
        try:
            # Try AI generation first (AGENT_1 pattern)
            ai_response = await self._generate_with_ai(creative_brief, visual_explorations, system_prompt)
            if ai_response:
                # Force convert AI response to correct Schema format if needed
                return self._ensure_schema_compliance(ai_response)
                
        except Exception as e:
            logger.warning("AI generation failed, falling back to template", error=str(e))
        
        # Fallback to template-based generation (AGENT_1 pattern)
        return await self._generate_template_presentation_blueprint(creative_brief, visual_explorations)
    
    async def _generate_with_ai(self, creative_brief: Dict[str, Any], visual_explorations: Dict[str, Any], system_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate presentation blueprint using AI model (AGENT_1 architecture)
        """
        try:
            # Create AI client
            ai_client = AIClientFactory.create_client()
            
            # Enhanced system prompt for JSON output matching PresentationBlueprint_v1.0.json Schema
            enhanced_prompt = f"""{system_prompt}

CRITICAL: You must respond with VALID JSON only. Do not include any text before or after the JSON.
The JSON must follow this EXACT structure to match PresentationBlueprint_v1.0.json Schema:

{{
  "narrative_structure": {{
    "narrative_arc": "string - overall story progression",
    "key_story_beats": ["string", "string", "string"],
    "emotional_journey": "string - audience emotional progression", 
    "conflict_resolution": "string - how tensions are resolved"
  }},
  "content_sections": [
    {{
      "section_title": "string",
      "content_type": "string",
      "key_messages": ["string", "string"],
      "visual_treatment": "string",
      "interaction_elements": ["string", "string"]
    }}
  ],
  "storytelling_elements": {{
    "hero_journey_stage": "string",
    "narrative_devices": ["string", "string"],
    "character_personas": ["string", "string"],
    "story_themes": ["string", "string"]
  }},
  "engagement_strategy": {{
    "attention_hooks": ["string", "string"],
    "interactive_moments": ["string", "string"],
    "call_to_action_placement": "string",
    "retention_techniques": ["string", "string"]
  }},
  "metadata": {{
    "created_by": "AGENT_3",
    "version": "1.0",
    "confidence_score": 0.85,
    "processing_notes": "string"
  }}
}}

Remember: Follow the Socratic thinking methodology to design a cognitive journey for the audience."""
            
            # Prepare creative materials for the prompt
            materials = {
                "creative_brief": creative_brief,
                "visual_explorations": visual_explorations
            }
            
            # Convert to JSON string for prompt
            materials_json = json.dumps(materials, ensure_ascii=False, indent=2)
            
            # Generate response
            response = await ai_client.generate_response(
                system_prompt=enhanced_prompt,
                user_input=f"CREATIVE_MATERIALS:\n\n{materials_json}",
                temperature=0.7,
                max_tokens=4000
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
            presentation_blueprint = json.loads(content.strip())
            
            # Add metadata (AGENT_1 pattern)
            if "metadata" not in presentation_blueprint:
                presentation_blueprint["metadata"] = {}
                
            presentation_blueprint["metadata"].update({
                "created_by": "AGENT_3",
                "version": "1.0",
                "total_slides": len(presentation_blueprint.get("content_sections", [])),
                "narrative_complexity": "sophisticated",
                "target_audience_level": "intermediate",
                "presentation_style": "Socratic thought guidance",
                "confidence_score": 0.85,
                "ai_model": response.get("model", "unknown"),
                "ai_provider": response.get("provider", "unknown"),
                "tokens_used": response.get("usage", {}).get("total_tokens", 0),
                "processing_notes": f"AI-generated narrative architecture"
            })
            
            logger.info("AI presentation blueprint generated successfully",
                       model=response.get("model"),
                       tokens=response.get("usage", {}).get("total_tokens", 0))
            
            return presentation_blueprint
            
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse AI response as JSON", 
                          content_preview=content[:200],
                          error=str(e))
            return None
    
    async def _generate_template_presentation_blueprint(self, creative_brief: Dict[str, Any], visual_explorations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate presentation blueprint using template-based approach (fallback)
        """
        
        # Extract key information from creative brief
        project_title = creative_brief.get("project_overview", {}).get("title", "Project Presentation")
        primary_goal = creative_brief.get("objectives", {}).get("primary_goal", "Present project overview")
        target_audience = creative_brief.get("target_audience", {}).get("primary_audience", "Stakeholders")
        key_messages = creative_brief.get("creative_strategy", {}).get("key_messages", ["Key Message 1", "Key Message 2"])
        
        # Extract visual themes
        visual_themes = visual_explorations.get("visual_themes", [])
        primary_theme = visual_themes[0] if visual_themes else {
            "theme_name": "Professional Standard",
            "design_philosophy": "Clean, professional approach"
        }
        
        # Strategic choice (template logic)
        strategic_choice = {
            "chosen_theme_name": primary_theme.get("theme_name", "Professional Standard"),
            "chosen_narrative_framework": "Problem-Solution-Benefit",
            "reasoning": f"Selected '{primary_theme.get('theme_name')}' theme and Problem-Solution-Benefit framework as they align with the project goal of {primary_goal} for {target_audience}. This combination provides a clear logical progression that builds audience understanding systematically.",
            "rejected_options": [
                {
                    "option_type": "Visual Theme",
                    "option_name": visual_themes[1].get("theme_name") if len(visual_themes) > 1 else "Alternative Theme",
                    "reason_for_rejection": "While visually appealing, this theme might not align as well with the target audience's expectations and the professional context of the presentation."
                },
                {
                    "option_type": "Narrative Framework", 
                    "option_name": "Chronological Timeline",
                    "reason_for_rejection": "A timeline approach might focus too much on sequence rather than the logical argument structure needed to persuade the audience."
                }
            ]
        }
        
        # Generate presentation slides
        presentation_slides = self._generate_template_slides(project_title, primary_goal, key_messages, primary_theme)
        
        # Generate content that matches PresentationBlueprint_v1.0.json Schema
        presentation_blueprint = {
            "narrative_structure": {
                "narrative_arc": "Problem-Solution-Benefit framework with strategic progression",
                "key_story_beats": [
                    "Opening and credibility establishment",
                    "Problem/opportunity identification", 
                    "Strategic solution presentation",
                    "Benefits and outcomes demonstration",
                    "Call to action and next steps"
                ],
                "emotional_journey": "From awareness through understanding to conviction and action",
                "conflict_resolution": f"Addresses {target_audience} needs through systematic solution presentation"
            },
            "content_sections": self._generate_content_sections(project_title, primary_goal, key_messages),
            "storytelling_elements": {
                "hero_journey_stage": "Call to Adventure",
                "narrative_devices": [
                    "Strategic questioning",
                    "Evidence-based reasoning", 
                    "Visual metaphors",
                    "Progressive disclosure"
                ],
                "character_personas": [target_audience, "Project stakeholders", "Implementation team"],
                "story_themes": ["Innovation", "Strategic thinking", "Collaborative success"]
            },
            "engagement_strategy": {
                "attention_hooks": [
                    "Opening with compelling opportunity statement",
                    "Strategic insights that challenge assumptions",
                    "Clear benefit articulation"
                ],
                "interactive_moments": [
                    "Audience agreement checkpoints",
                    "Strategic question pauses",
                    "Next steps clarification"
                ],
                "call_to_action_placement": "Final slide with clear next steps",
                "retention_techniques": [
                    "Logical flow reinforcement",
                    "Key message repetition",
                    "Visual memory aids"
                ]
            },
            "metadata": {
                "created_by": "AGENT_3",
                "version": "1.0",
                "confidence_score": self._calculate_template_confidence(creative_brief, visual_explorations),
                "processing_notes": f"Template-generated from {len(visual_themes)} visual themes and {len(key_messages)} key messages"
            }
        }
        
        return presentation_blueprint
    
    def _generate_content_sections(self, project_title: str, primary_goal: str, key_messages: List[str]) -> List[Dict[str, Any]]:
        """Generate content sections that match Schema requirements"""
        
        content_sections = [
            {
                "section_title": "Opening & Credibility",
                "content_type": "Title_Slide",
                "key_messages": [f"Presenting {project_title}", "Strategic presentation approach"],
                "visual_treatment": "Clean, professional title layout with subtle branding",
                "interaction_elements": ["Eye contact with key stakeholders", "Confident opening statement"]
            },
            {
                "section_title": "Current Situation & Opportunity",
                "content_type": "Problem_Definition",
                "key_messages": [f"Current state: {primary_goal}", "Key challenges identification", "Market opportunity"],
                "visual_treatment": "Comparison charts showing current vs desired state",
                "interaction_elements": ["Audience agreement checkpoint", "Shared understanding confirmation"]
            },
            {
                "section_title": "Strategic Approach",
                "content_type": "Solution_Presentation",
                "key_messages": key_messages,
                "visual_treatment": "Visual hierarchy emphasizing key insights with supporting diagrams",
                "interaction_elements": ["Strategic pause after each key message", "Evidence presentation"]
            },
            {
                "section_title": "Expected Benefits & Outcomes",
                "content_type": "Value_Proposition",
                "key_messages": ["Concrete benefits demonstration", "Success metrics", "ROI justification"],
                "visual_treatment": "Impact visualizations with clear metrics and timelines",
                "interaction_elements": ["Benefits emphasis", "Stakeholder value confirmation"]
            },
            {
                "section_title": "Next Steps Forward",
                "content_type": "Call_To_Action",
                "key_messages": ["Immediate action items", "Timeline and milestones", "Collaboration opportunities"],
                "visual_treatment": "Clear action-oriented layout with timeline visualization",
                "interaction_elements": ["Direct engagement", "Commitment seeking", "Questions and clarifications"]
            }
        ]
        
        return content_sections
    
    def _generate_template_slides(self, project_title: str, primary_goal: str, key_messages: List[str], primary_theme: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate template presentation slides"""
        
        slides = []
        
        # Slide 1: Title Slide
        slides.append({
            "slide_number": 1,
            "logic_unit_purpose": "Opening & Establishing Credibility",
            "layout": "Title_Slide",
            "elements": {
                "title": project_title,
                "subtitle": "A Strategic Presentation"
            },
            "speaker_notes": {
                "speech": f"Welcome everyone. Today I'll be presenting {project_title}, where we'll explore {primary_goal}.",
                "guide_note": "Establish presence and credibility. Make eye contact with key stakeholders."
            }
        })
        
        # Slide 2: Agenda/Overview
        slides.append({
            "slide_number": 2,
            "logic_unit_purpose": "Setting Expectations & Roadmap",
            "layout": "Bullet_Points",
            "elements": {
                "title": "Today's Journey",
                "bullet_points": [
                    "Current Situation & Opportunity",
                    "Our Strategic Approach",
                    "Expected Benefits & Outcomes",
                    "Next Steps Forward"
                ]
            },
            "speaker_notes": {
                "speech": "We'll follow a logical progression starting with understanding where we are today, exploring our strategic approach, and concluding with the benefits and next steps.",
                "guide_note": "This sets expectations and gives the audience a mental roadmap. Emphasize the logical flow."
            }
        })
        
        # Slide 3: Problem/Opportunity
        slides.append({
            "slide_number": 3,
            "logic_unit_purpose": "Establishing Shared Understanding of the Challenge",
            "layout": "Content_With_Chart",
            "elements": {
                "title": "The Opportunity Before Us",
                "bullet_points": [
                    f"Current state: {primary_goal}",
                    "Key challenges we're addressing",
                    "Market opportunity and timing"
                ],
                "visual_placeholder": "Chart showing current situation vs desired future state"
            },
            "speaker_notes": {
                "speech": "Let's start by establishing our shared understanding of the current situation and the opportunity we have identified.",
                "guide_note": "This is critical - ensure everyone agrees on the problem before presenting solutions."
            }
        })
        
        # Generate slides for key messages
        for i, message in enumerate(key_messages[:3], 4):  # Max 3 message slides
            slides.append({
                "slide_number": i,
                "logic_unit_purpose": f"Key Message {i-3}: {message[:50]}...",
                "layout": "Two_Column",
                "elements": {
                    "title": f"Key Insight {i-3}",
                    "bullet_points": [
                        message,
                        "Supporting evidence",
                        "Impact on our approach"
                    ],
                    "visual_placeholder": "Supporting visual or diagram"
                },
                "speaker_notes": {
                    "speech": f"This brings us to a key insight: {message}. Let me explain why this is significant for our strategy.",
                    "guide_note": f"Emphasize the importance of this message. Pause after delivering the key point."
                }
            })
        
        # Final slide: Call to Action
        final_slide_number = len(slides) + 1
        slides.append({
            "slide_number": final_slide_number,
            "logic_unit_purpose": "Inspiring Action & Next Steps",
            "layout": "Call_To_Action",
            "elements": {
                "title": "Moving Forward Together",
                "bullet_points": [
                    "Immediate next steps",
                    "Timeline and milestones",
                    "How you can contribute"
                ]
            },
            "speaker_notes": {
                "speech": "Now that we've explored the opportunity and our approach, let's discuss how we move forward together. Here are the concrete next steps.",
                "guide_note": "End with energy and clear action items. Make it easy for people to say yes."
            }
        })
        
        return slides
    
    def _calculate_template_confidence(self, creative_brief: Dict[str, Any], visual_explorations: Dict[str, Any]) -> float:
        """Calculate confidence score for template generation"""
        required_fields = ["project_overview", "objectives", "target_audience", "creative_strategy"]
        present_fields = sum(1 for field in required_fields if field in creative_brief)
        
        base_confidence = 0.65  # Lower than AI confidence
        completeness_bonus = (present_fields / len(required_fields)) * 0.15
        
        # Bonus for having visual themes
        theme_bonus = min(len(visual_explorations.get("visual_themes", [])) * 0.05, 0.15)
        
        # Bonus for having key messages
        key_messages = creative_brief.get("creative_strategy", {}).get("key_messages", [])
        message_bonus = min(len(key_messages) * 0.02, 0.05)
        
        return min(base_confidence + completeness_bonus + theme_bonus + message_bonus, 0.84)
    
    def _ensure_schema_compliance(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Force convert AI response to PresentationBlueprint_v1.0.json Schema format
        Handles cases where AI ignores Schema instructions
        """
        # Check if AI response is already in correct format
        if all(key in ai_response for key in ['narrative_structure', 'content_sections', 'storytelling_elements', 'engagement_strategy', 'metadata']):
            return ai_response
        
        # AI returned old format - convert to new format
        logger.warning("AI returned old format, converting to Schema-compliant format")
        
        # Extract data from old format
        strategic_choice = ai_response.get('strategic_choice', {})
        presentation_blueprint = ai_response.get('presentation_blueprint', [])
        metadata = ai_response.get('metadata', {})
        
        # Convert to new Schema format
        schema_compliant = {
            "narrative_structure": {
                "narrative_arc": strategic_choice.get('chosen_narrative_framework', 'Problem-Solution-Benefit framework'),
                "key_story_beats": [
                    "Opening and credibility establishment",
                    "Problem identification and exploration",
                    "Solution presentation and benefits",
                    "Call to action and next steps"
                ],
                "emotional_journey": "From awareness through understanding to conviction and action",
                "conflict_resolution": f"Addresses audience needs through systematic presentation of solutions"
            },
            "content_sections": self._convert_slides_to_content_sections(presentation_blueprint),
            "storytelling_elements": {
                "hero_journey_stage": "Call to Adventure",
                "narrative_devices": ["Strategic questioning", "Evidence-based reasoning", "Progressive disclosure"],
                "character_personas": ["Target audience", "Project stakeholders", "Implementation team"],
                "story_themes": ["Innovation", "Problem-solving", "Positive impact"]
            },
            "engagement_strategy": {
                "attention_hooks": ["Compelling opening statement", "Strategic insights", "Clear benefits"],
                "interactive_moments": ["Audience checkpoints", "Strategic pauses", "Q&A opportunities"],
                "call_to_action_placement": "Final slide with clear next steps",
                "retention_techniques": ["Logical flow", "Key message repetition", "Visual reinforcement"]
            },
            "metadata": {
                "created_by": "AGENT_3",
                "version": "1.0",
                "confidence_score": metadata.get('confidence_score', 0.8),
                "processing_notes": f"Converted from AI old format - {metadata.get('processing_notes', 'AI generated')}"
            }
        }
        
        return schema_compliant
    
    def _validate_required_artifacts(self, artifacts: Dict[str, Any]) -> None:
        """Validate required artifacts with minimal essential checks only"""
        # Check artifact existence
        required_artifacts = ["creative_brief", "visual_explorations"]
        for artifact_name in required_artifacts:
            if artifact_name not in artifacts:
                raise ValueError(f"Required artifact '{artifact_name}' not found")
        
        # Minimal payload validation - only check if payload exists and has basic structure
        creative_brief = artifacts["creative_brief"].get("payload", {})
        visual_explorations = artifacts["visual_explorations"].get("payload", {})
        
        if not creative_brief:
            raise ValueError("creative_brief payload is empty")
        if not visual_explorations:
            raise ValueError("visual_explorations payload is empty")
        
        # Only validate critical fields that AGENT_3 actually uses
        if "project_overview" not in creative_brief:
            logger.warning("creative_brief missing project_overview - may impact quality")
        if "visual_themes" not in visual_explorations:
            logger.warning("visual_explorations missing visual_themes - may impact quality")
    
    async def _check_existing_output(self, task_input: TaskInput, artifacts: Dict[str, Any]) -> Optional[TaskOutput]:
        """Check if this task has already been processed successfully (P4: Idempotency)"""
        try:
            # Create a simple hash of input artifacts to identify identical tasks
            import hashlib
            import json
            
            # Only include essential fields for hash calculation
            hash_data = {
                "creative_brief_title": artifacts["creative_brief"]["payload"].get("project_overview", {}).get("title", ""),
                "visual_themes_count": len(artifacts["visual_explorations"]["payload"].get("visual_themes", [])),
                "agent_id": self.agent_id
            }
            
            content_hash = hashlib.sha256(
                json.dumps(hash_data, sort_keys=True).encode()
            ).hexdigest()[:16]
            
            # Check if we have recent successful output for this input combination
            # This is a simplified check - in production, you'd check the database
            # For now, we'll return None to always process (can be enhanced later)
            logger.debug("Idempotency check", content_hash=content_hash, 
                        title=hash_data["creative_brief_title"])
            
            return None  # Always process for now - can be enhanced with database lookup
            
        except Exception as e:
            logger.warning("Idempotency check failed, proceeding with processing", error=str(e))
            return None
    
    def _validate_output_schema(self, output: Dict[str, Any]) -> bool:
        """Validate output against PresentationBlueprint_v1.0 schema requirements"""
        try:
            # Check required top-level keys
            required_keys = ["narrative_structure", "content_sections", "storytelling_elements", "engagement_strategy", "metadata"]
            
            if not all(key in output for key in required_keys):
                missing_keys = [key for key in required_keys if key not in output]
                logger.warning("Output missing required keys", missing_keys=missing_keys)
                return False
            
            # Check narrative_structure structure
            narrative = output.get("narrative_structure", {})
            if not isinstance(narrative, dict):
                logger.warning("narrative_structure must be a dict")
                return False
            
            # Check content_sections is array
            sections = output.get("content_sections", [])
            if not isinstance(sections, list):
                logger.warning("content_sections must be an array")
                return False
            
            # Check metadata has required fields
            metadata = output.get("metadata", {})
            if not isinstance(metadata, dict) or "created_by" not in metadata:
                logger.warning("metadata must be dict with created_by field")
                return False
            
            logger.debug("Output schema validation passed")
            return True
            
        except Exception as e:
            logger.warning("Output schema validation error", error=str(e))
            return False
    
    def _convert_slides_to_content_sections(self, slides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert old slide format to new content_sections format"""
        content_sections = []
        
        for slide in slides:
            section = {
                "section_title": slide.get('elements', {}).get('title', f"Section {slide.get('slide_number', 1)}"),
                "content_type": slide.get('layout', 'Content_Slide'),
                "key_messages": slide.get('elements', {}).get('bullet_points', []),
                "visual_treatment": slide.get('elements', {}).get('visual_placeholder', 'Standard presentation layout'),
                "interaction_elements": [
                    slide.get('speaker_notes', {}).get('guide_note', 'Standard presentation delivery')
                ]
            }
            content_sections.append(section)
        
        return content_sections

# Example usage for testing
async def test_narrative_architect():
    """Test function for the Chief Narrative Architect Agent"""
    agent = ChiefNarrativeArchitectAgent()
    
    # Mock creative brief from AGENT_1
    mock_creative_brief = {
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
    
    # Mock visual explorations from AGENT_2
    mock_visual_explorations = {
        "visual_themes": [
            {
                "theme_name": "The Direct Voice",
                "design_philosophy": "【忠实演绎】Clean, professional approach that builds trust",
                "color_and_typography": "Corporate blue with professional sans-serif",
                "layout_and_graphics": "Structured layouts with clear hierarchy"
            },
            {
                "theme_name": "The Innovation Edge",
                "design_philosophy": "【抽象转译】Modern, forward-thinking visual language",
                "color_and_typography": "Dynamic colors with contemporary typography",
                "layout_and_graphics": "Asymmetrical layouts with bold elements"
            },
            {
                "theme_name": "The Disruptor",
                "design_philosophy": "【逆向挑战】Bold, unconventional approach",
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
    
    # Test input with mock artifacts
    test_input = TaskInput(
        artifacts=[
            {"name": "creative_brief", "source_task_id": 101},
            {"name": "visual_explorations", "source_task_id": 102}
        ],
        params={}
    )
    
    try:
        # Mock the get_artifacts method for testing
        async def mock_get_artifacts(refs):
            return {
                "creative_brief": {
                    "payload": mock_creative_brief,
                    "schema_id": "CreativeBrief_v1.0"
                },
                "visual_explorations": {
                    "payload": mock_visual_explorations,
                    "schema_id": "VisualExplorations_v1.0"
                }
            }
        
        agent.get_artifacts = mock_get_artifacts
        
        result = await agent.process_task(test_input)
        print("Presentation Blueprint Generated:")
        print(f"Schema: {result.schema_id}")
        print(f"Chosen Theme: {result.payload['strategic_choice']['chosen_theme_name']}")
        print(f"Narrative Framework: {result.payload['strategic_choice']['chosen_narrative_framework']}")
        print(f"Total Slides: {len(result.payload['presentation_blueprint'])}")
        print(f"Confidence Score: {result.payload['metadata']['confidence_score']}")
        
        return result
        
    except Exception as e:
        print(f"Test failed: {e}")
        return None


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_narrative_architect())