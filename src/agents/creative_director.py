"""
Creative Director Agent for Project HELIX v2.0
AGENT_1: Transforms user requirements into structured creative briefs
"""

import structlog
import json
from typing import Dict, Any

from src.sdk.agent_sdk import BaseAgent
from src.database.models import TaskInput, TaskOutput
from src.ai_clients.client_factory import AIClientFactory

logger = structlog.get_logger(__name__)


class CreativeDirectorAgent(BaseAgent):
    """
    AGENT_1: Creative Director
    
    Transforms user's natural language requirements into structured,
    detailed creative briefs with clear objectives and strategic direction.
    """
    
    def __init__(self):
        super().__init__("AGENT_1")
    
    async def process_task(self, task_input: TaskInput) -> TaskOutput:
        """
        Process user input and create a structured creative brief
        
        Input: User's chat_input and session context
        Output: Structured creative brief with objectives, audience, and strategy
        """
        try:
            # Extract user input from params
            chat_input = task_input.params.get("chat_input", "")
            session_id = task_input.params.get("session_id")
            
            logger.info("Processing creative brief request", 
                       agent_id=self.agent_id,
                       input_length=len(chat_input),
                       session_id=session_id)
            
            # Get agent prompt
            system_prompt = await self.get_agent_prompt()
            if not system_prompt:
                system_prompt = self._get_default_prompt()
            
            # For now, create a structured response based on the input
            # In a real implementation, this would call an AI model
            creative_brief = await self._generate_creative_brief(chat_input, system_prompt)
            
            # Log successful processing
            await self.log_system_event(
                "INFO", 
                "Creative brief generated successfully",
                {"input_length": len(chat_input), "output_sections": len(creative_brief)}
            )
            
            return TaskOutput(
                schema_id="CreativeBrief_v1.0",
                payload=creative_brief
            )
            
        except Exception as e:
            logger.error("Failed to process creative brief", 
                        agent_id=self.agent_id, error=str(e))
            
            await self.log_system_event(
                "ERROR",
                f"Creative brief generation failed: {str(e)}"
            )
            
            raise
    
    async def _generate_creative_brief(self, user_input: str, system_prompt: str) -> Dict[str, Any]:
        """
        Generate creative brief from user input using AI model
        Falls back to template-based response if AI fails
        """
        
        try:
            # Try to use AI model for generation
            ai_response = await self._generate_with_ai(user_input, system_prompt)
            if ai_response:
                return ai_response
                
        except Exception as e:
            logger.warning("AI generation failed, falling back to template", error=str(e))
        
        # Fallback to template-based generation
        return await self._generate_template_brief(user_input)
    
    async def _generate_with_ai(self, user_input: str, system_prompt: str) -> Dict[str, Any]:
        """
        Generate creative brief using AI model
        """
        try:
            # Create AI client
            ai_client = AIClientFactory.create_client()
            
            # Enhanced system prompt for JSON output
            enhanced_prompt = f"""{system_prompt}

CRITICAL: You must respond with VALID JSON only. Do not include any text before or after the JSON.
The JSON must follow this exact structure:

{{
  "project_overview": {{
    "title": "string",
    "type": "string",
    "description": "string", 
    "key_themes": ["string1", "string2"]
  }},
  "objectives": {{
    "primary_goal": "string",
    "secondary_goals": ["string1", "string2"],
    "success_metrics": ["string1", "string2"]
  }},
  "target_audience": {{
    "primary_audience": "string",
    "audience_characteristics": {{
      "demographics": "string",
      "psychographics": "string",
      "behavior_patterns": "string",
      "pain_points": "string"
    }}
  }},
  "creative_strategy": {{
    "tone_of_voice": "string",
    "key_messages": ["string1", "string2"],
    "creative_approach": "string"
  }},
  "content_requirements": {{
    "content_types": ["string1", "string2"],
    "information_hierarchy": {{
      "primary": 1,
      "secondary": 2,
      "tertiary": 3
    }},
    "call_to_action": "string"
  }}
}}

Remember: Follow your three-act thinking process internally, but output ONLY the final JSON result."""
            
            # Generate response
            response = await ai_client.generate_response(
                system_prompt=enhanced_prompt,
                user_input=user_input,
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response["content"].strip()
            
            # Try to parse JSON from response
            try:
                # Remove any potential markdown formatting
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                
                # Parse JSON
                creative_brief = json.loads(content)
                
                # Add metadata
                creative_brief["metadata"] = {
                    "created_by": "AGENT_1",
                    "version": "1.0",
                    "ai_model": response.get("model", "unknown"),
                    "ai_provider": response.get("provider", "unknown"),
                    "tokens_used": response.get("usage", {}).get("total_tokens", 0),
                    "processing_notes": f"AI-generated from {len(user_input)} character input"
                }
                
                logger.info("AI creative brief generated successfully",
                           model=response.get("model"),
                           tokens=response.get("usage", {}).get("total_tokens", 0))
                
                return creative_brief
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse AI response as JSON", 
                              content_preview=content[:200],
                              error=str(e))
                return None
                
        except Exception as e:
            logger.error("AI generation failed", error=str(e))
            raise
    
    async def _generate_template_brief(self, user_input: str) -> Dict[str, Any]:
        """
        Generate creative brief using template-based approach (fallback)
        """
        
        # Analyze input for key themes and requirements
        themes = self._extract_themes(user_input)
        project_type = self._identify_project_type(user_input)
        
        # Create structured creative brief
        creative_brief = {
            "project_overview": {
                "title": self._generate_project_title(user_input),
                "type": project_type,
                "description": user_input[:500] + "..." if len(user_input) > 500 else user_input,
                "key_themes": themes
            },
            "objectives": {
                "primary_goal": self._extract_primary_goal(user_input),
                "secondary_goals": self._extract_secondary_goals(user_input),
                "success_metrics": self._define_success_metrics(project_type)
            },
            "target_audience": {
                "primary_audience": self._identify_audience(user_input),
                "audience_characteristics": {
                    "demographics": self._describe_audience_characteristics(user_input),
                    "psychographics": "To be defined based on research",
                    "behavior_patterns": "To be analyzed",
                    "pain_points": "To be identified"
                }
            },
            "creative_strategy": {
                "tone_of_voice": self._determine_tone(user_input, themes),
                "key_messages": self._extract_key_messages(user_input),
                "creative_approach": self._suggest_creative_approach(project_type, themes)
            },
            "content_requirements": {
                "content_types": self._identify_content_types(project_type),
                "information_hierarchy": self._create_information_hierarchy(user_input),
                "call_to_action": self._extract_call_to_action(user_input)
            },
            "constraints_and_considerations": {
                "technical_constraints": [],
                "brand_guidelines": "To be defined",
                "accessibility_requirements": ["WCAG 2.1 AA compliance"],
                "timeline_considerations": "Standard development timeline"
            },
            "next_steps": {
                "immediate_actions": [
                    "Visual concept development",
                    "Content architecture planning",
                    "Technical feasibility assessment"
                ],
                "deliverables_expected": [
                    "Visual style exploration",
                    "Content wireframes",
                    "Technical implementation plan"
                ]
            },
            "metadata": {
                "created_by": "AGENT_1",
                "version": "1.0",
                "ai_model": "template_fallback",
                "confidence_score": self._calculate_confidence_score(user_input),
                "processing_notes": f"Template-generated from {len(user_input)} character input"
            }
        }
        
        return creative_brief
    
    def _extract_themes(self, text: str) -> list:
        """Extract key themes from user input"""
        # Simple keyword-based theme extraction
        themes = []
        text_lower = text.lower()
        
        theme_keywords = {
            "modern": ["modern", "contemporary", "sleek", "minimalist", "clean"],
            "professional": ["professional", "business", "corporate", "formal"],
            "creative": ["creative", "artistic", "innovative", "unique", "original"],
            "user-friendly": ["user-friendly", "intuitive", "easy", "simple", "accessible"],
            "premium": ["premium", "luxury", "high-end", "exclusive", "sophisticated"],
            "tech": ["technology", "digital", "tech", "software", "app", "platform"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:5]  # Limit to top 5 themes
    
    def _identify_project_type(self, text: str) -> str:
        """Identify the type of project from user input"""
        text_lower = text.lower()
        
        project_types = {
            "website": ["website", "web", "site", "landing page", "homepage"],
            "application": ["app", "application", "software", "platform", "tool"],
            "ecommerce": ["ecommerce", "store", "shop", "marketplace", "selling"],
            "portfolio": ["portfolio", "showcase", "gallery", "work", "projects"],
            "corporate": ["company", "business", "corporate", "organization"],
            "blog": ["blog", "content", "articles", "news", "publication"]
        }
        
        for project_type, keywords in project_types.items():
            if any(keyword in text_lower for keyword in keywords):
                return project_type
        
        return "general_website"
    
    def _generate_project_title(self, user_input: str) -> str:
        """Generate a project title based on user input"""
        # Extract first meaningful phrase or create generic title
        words = user_input.split()[:10]  # First 10 words
        if len(words) > 3:
            return " ".join(words[:6]) + "..."
        return "Creative Project Brief"
    
    def _extract_primary_goal(self, text: str) -> str:
        """Extract the primary goal from user input"""
        # Look for goal-indicating phrases
        goal_indicators = [
            "want to", "need to", "goal is", "aim to", "looking to",
            "hoping to", "trying to", "planning to"
        ]
        
        text_lower = text.lower()
        for indicator in goal_indicators:
            if indicator in text_lower:
                # Extract sentence containing the goal
                sentences = text.split(".")
                for sentence in sentences:
                    if indicator in sentence.lower():
                        return sentence.strip()
        
        return "Create a compelling digital presence"
    
    def _extract_secondary_goals(self, text: str) -> list:
        """Extract secondary goals from user input"""
        return [
            "Improve user engagement",
            "Increase conversion rates",
            "Enhance brand perception"
        ]
    
    def _define_success_metrics(self, project_type: str) -> list:
        """Define success metrics based on project type"""
        metrics_by_type = {
            "website": ["Page load speed < 3s", "Mobile responsiveness", "SEO optimization"],
            "ecommerce": ["Conversion rate", "Cart abandonment rate", "Revenue growth"],
            "application": ["User retention", "Feature adoption", "Performance metrics"],
            "portfolio": ["Portfolio views", "Contact form submissions", "Social shares"]
        }
        
        return metrics_by_type.get(project_type, ["User satisfaction", "Performance", "Accessibility"])
    
    def _identify_audience(self, text: str) -> str:
        """Identify target audience from user input"""
        # Simple audience identification
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["business", "professional", "company"]):
            return "Business professionals"
        elif any(word in text_lower for word in ["young", "student", "teen"]):
            return "Young adults and students"
        elif any(word in text_lower for word in ["customer", "client", "buyer"]):
            return "Potential customers"
        else:
            return "General public"
    
    def _describe_audience_characteristics(self, text: str) -> Dict[str, str]:
        """Describe audience characteristics"""
        return {
            "demographics": "To be researched",
            "psychographics": "Tech-savvy, quality-conscious",
            "behavior_patterns": "Online research before decisions",
            "pain_points": "Looking for reliable solutions",
            "motivations": "Efficiency and quality"
        }
    
    def _determine_tone(self, text: str, themes: list) -> str:
        """Determine appropriate tone of voice"""
        if "professional" in themes:
            return "Professional and trustworthy"
        elif "creative" in themes:
            return "Creative and inspiring"
        elif "modern" in themes:
            return "Contemporary and forward-thinking"
        else:
            return "Friendly and approachable"
    
    def _extract_key_messages(self, text: str) -> list:
        """Extract key messages from user input"""
        return [
            "Quality and reliability",
            "User-focused design",
            "Innovation and expertise"
        ]
    
    def _suggest_creative_approach(self, project_type: str, themes: list) -> str:
        """Suggest creative approach based on project type and themes"""
        approaches = {
            "website": "Clean, intuitive design with clear information hierarchy",
            "ecommerce": "Conversion-focused design with trust signals",
            "application": "User-centered design with intuitive workflows",
            "portfolio": "Visual storytelling with compelling case studies"
        }
        
        base_approach = approaches.get(project_type, "User-centered design approach")
        
        if "modern" in themes:
            return f"{base_approach} with contemporary aesthetic"
        elif "premium" in themes:
            return f"{base_approach} with premium visual treatment"
        else:
            return base_approach
    
    def _identify_content_types(self, project_type: str) -> list:
        """Identify required content types"""
        content_by_type = {
            "website": ["Hero section", "About", "Services", "Contact"],
            "ecommerce": ["Product catalog", "Shopping cart", "Checkout", "User account"],
            "application": ["Dashboard", "Feature pages", "Help documentation"],
            "portfolio": ["Work samples", "Case studies", "About", "Contact"]
        }
        
        return content_by_type.get(project_type, ["Homepage", "Content pages", "Contact"])
    
    def _calculate_confidence_score(self, user_input: str) -> float:
        """Calculate confidence score for template-generated brief"""
        # Base confidence for template generation
        base_confidence = 0.7
        
        # Adjust based on input length
        if len(user_input) < 50:
            confidence = base_confidence - 0.1
        elif len(user_input) > 200:
            confidence = base_confidence + 0.1
        else:
            confidence = base_confidence
        
        # Ensure within valid range
        return max(0.5, min(0.85, confidence))
    
    def _create_information_hierarchy(self, text: str) -> Dict[str, int]:
        """Create information hierarchy priority"""
        return {
            "Primary message": 1,
            "Key features/services": 2,
            "Supporting information": 3,
            "Contact/action items": 4,
            "Additional resources": 5
        }
    
    def _extract_call_to_action(self, text: str) -> str:
        """Extract or suggest call to action"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["contact", "get in touch"]):
            return "Contact us"
        elif any(word in text_lower for word in ["buy", "purchase", "order"]):
            return "Shop now"
        elif any(word in text_lower for word in ["sign up", "register", "join"]):
            return "Get started"
        else:
            return "Learn more"
    
    def _get_default_prompt(self) -> str:
        """Get default system prompt if none found in database"""
        return """You are a Creative Director. Transform user requirements into structured creative briefs with clear objectives, target audience, and key messages. Focus on understanding the user's vision and translating it into actionable creative strategy."""


# Example usage for testing
async def test_creative_director():
    """Test function for the Creative Director Agent"""
    agent = CreativeDirectorAgent()
    
    # Test input
    test_input = TaskInput(
        artifacts=[],
        params={
            "chat_input": "I want to create a modern website for my tech startup that sells AI-powered productivity tools. The site should look professional and appeal to business professionals who value efficiency.",
            "session_id": "test_session_001"
        }
    )
    
    try:
        result = await agent.process_task(test_input)
        print("Creative Brief Generated:")
        print(f"Schema: {result.schema_id}")
        print(f"Project Title: {result.payload['project_overview']['title']}")
        print(f"Themes: {result.payload['project_overview']['key_themes']}")
        print(f"Primary Goal: {result.payload['objectives']['primary_goal']}")
        
        return result
        
    except Exception as e:
        print(f"Test failed: {e}")
        return None


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_creative_director())