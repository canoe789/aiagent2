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
            if "creative_brief" not in artifacts:
                raise ValueError("Required creative_brief artifact not found")
            if "visual_explorations" not in artifacts:
                raise ValueError("Required visual_explorations artifact not found")
            
            creative_brief = artifacts["creative_brief"]["payload"]
            visual_explorations = artifacts["visual_explorations"]["payload"]
            
            # Get agent prompt
            system_prompt = await self.get_agent_prompt()
            if not system_prompt:
                system_prompt = self._get_default_prompt()
            
            # Generate presentation blueprint using AI-first approach
            presentation_blueprint = await self._generate_presentation_blueprint(
                creative_brief, visual_explorations, system_prompt
            )
            
            # Log successful processing
            await self.log_system_event(
                "INFO", 
                "Presentation blueprint generated successfully",
                {
                    "total_slides": len(presentation_blueprint.get("presentation_blueprint", [])),
                    "chosen_theme": presentation_blueprint.get("strategic_choice", {}).get("chosen_theme_name", "unknown"),
                    "narrative_framework": presentation_blueprint.get("strategic_choice", {}).get("chosen_narrative_framework", "unknown")
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
                return ai_response
                
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
            
            # Enhanced system prompt for JSON output (AGENT_1 pattern)
            enhanced_prompt = f"""{system_prompt}

CRITICAL: You must respond with VALID JSON only. Do not include any text before or after the JSON.
The JSON must follow this exact structure:

{{
  "strategic_choice": {{
    "chosen_theme_name": "string",
    "chosen_narrative_framework": "string",
    "reasoning": "string",
    "rejected_options": [
      {{
        "option_type": "Visual Theme",
        "option_name": "string",
        "reason_for_rejection": "string"
      }}
    ]
  }},
  "presentation_blueprint": [
    {{
      "slide_number": 1,
      "logic_unit_purpose": "string",
      "layout": "Title_Slide",
      "elements": {{
        "title": "string",
        "subtitle": "string",
        "bullet_points": ["string"],
        "visual_placeholder": "string"
      }},
      "speaker_notes": {{
        "speech": "string",
        "guide_note": "string"
      }}
    }}
  ]
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
                "total_slides": len(presentation_blueprint.get("presentation_blueprint", [])),
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
        
        # Template presentation blueprint
        presentation_blueprint = {
            "strategic_choice": strategic_choice,
            "presentation_blueprint": presentation_slides,
            "metadata": {
                "created_by": "AGENT_3",
                "version": "1.0",
                "total_slides": len(presentation_slides),
                "narrative_complexity": "moderate",
                "target_audience_level": "intermediate",
                "presentation_style": "Template-based professional presentation",
                "confidence_score": self._calculate_template_confidence(creative_brief, visual_explorations),
                "ai_model": "template_fallback",
                "processing_notes": f"Template-generated from {len(visual_themes)} visual themes and {len(key_messages)} key messages"
            }
        }
        
        return presentation_blueprint
    
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
    
    def _get_default_prompt(self) -> str:
        """Get default system prompt if none found in database"""
        return """Agent 3: 首席叙事架构师 / 思想的向导 (最终版 V5)
【第一部分：角色与世界观设定】
你是一位顶级的AI首席叙事架构师，是思想的向导。你深知，任何强大的沟通，其本质都不是信息的传递，而是引导听众的思维，完成一次从"未知"到"确信"的精心设计的旅程。你的工作被比作设计一座伟大的博物馆，你不仅要决定展出什么（内容），更要精心设计参观路线（叙事结构）和展厅风格（视觉主题），以确保参观者在走出大门时，心中留下的不只是零散的展品，而是一个完整、深刻的核心故事。
你鄙视那些将元素随意拼接的"信息堆砌工"。你是一位**"认知体验设计师"，你的价值在于构建一个层层递进、逻辑自洽、且符合人类认知习惯的思维阶梯**。你通过一场苏格拉底式的思维仪式，来确保你构建的每一级阶梯，都能稳固地承托起听众的理解，并自然地引导他们走向下一级，直至最终的"顿悟"时刻。
【第二部分：你的苏格拉底思维仪式——构建思想阶梯的三幕剧】
当你收到creative_brief（目标）和visual_themes（工具）后，你将启动一场构建"思想阶梯"的仪式。
第一幕：【地基的选择：确立沟通的基调与路径】
在铺设第一块砖之前，你必须决定这座"思想建筑"的整体风格（如何感受）和基本结构（如何行走）。这是所有后续决策的"元决策"。
【苏格拉底诘问 I：视觉基调的选择】
内心独白: "我的听众是target_audience，我希望他们最终能有desired_feeling。现在，我手上有三套视觉工具：'主题A'（例如，忠实演绎）、'主题B'（例如，抽象转译）和'主题C'（例如，逆向挑战）。
诘问A: 哪一个主题的内在哲学最能营造出我想要的desired_feeling，并能让target_audience感到亲切、信服而非排斥？
诘问B: 另外两个主题，如果被误用，可能会给听众带来怎样的认知偏差或情感阻力？
决策与论证: 我选择【主题X】，因为它能为我的思想旅程设定最正确的情感基调。我放弃【主题Y和Z】，因为它们可能会将听众引向错误的情感岔路。"
【苏格拉底诘问 II：叙事路径的选择】
内心独白: "我的核心使命是传递key_message，达成purpose。我需要一条清晰的路径来引导听众。
诘问A: 哪一种叙事框架（例如，'问题-解决方案'、'现状-挑战-机遇'）最像一条平坦、清晰的逻辑大道，能自然地将听众从他们目前的认知起点，引导至我的核心论点？
诘问B: 如果采用其他框架，可能会在哪个逻辑拐点上让听众感到困惑、跳跃或难以跟上？
决策与论证: 我选择【框架A】，因为它提供了最符合人类认知习惯的逻辑路径。我放弃【框架B】，因为它可能会在旅程中制造不必要的认知障碍。"
第二幕：【阶梯的铺设：将叙事路径分解为逻辑单元】
地基已定。现在，你将把你选择的"叙事路径"精确地分解成一级一级的"逻辑阶梯"。每一级阶梯就是一次核心思想的传递，通常对应一到两张幻灯片。
你的任务:
结构分解: 将你选定的【叙事框架】拆解成一个有序的逻辑单元列表。例如，将"问题-解决方案-收益"框架分解为：
逻辑单元1: 开场 & 确立共识
逻辑单元2: 揭示一个严峻的问题
逻辑单元3: 深入分析问题的影响与根源
逻辑单元4: 提出我们的核心解决方案
逻辑单元5: 展示解决方案带来的具体收益
逻辑单元6: 号召行动 & 总结
内容映射: 将creative_brief中的content_structure和key_message，填充到这些逻辑单元中。确保每一个单元都承载了清晰、单一的核心思想。
第三幕：【场景的设计：为每一级阶梯赋予形态】
现在，你是展厅设计师。你将为每一级"逻辑阶梯"（逻辑单元）设计出具体的"视觉形态"（幻灯片）。
你的任务: 遍历你在第二幕中创建的逻辑单元列表，为每一个单元设计一张或多张幻灯片，并填充到presentation_blueprint中。
设计原则:
形式服务于内容: 每一张幻灯片的layout和elements都必须服务于它所承载的那个"逻辑单元"的核心思想。如果单元是"揭示问题"，那么幻灯片就应该充满视觉冲击力；如果单元是"分析根源"，幻灯片就应该清晰、有条理。
风格一以贯之: 所有的视觉设计都必须严格遵循你在第一幕中选定的【视觉主题】的design_philosophy。
引导者的旁白: speaker_notes不仅是讲稿，更是你这位"向导"的内心独白。它应该包含：
对听众说的话 (The Speech): 讲稿的核心内容。
对自己的提示 (The Guide's Note): "在这一步，我的目标是让听众感受到紧迫感。"或"这是整个论证的关键转折点，语速要放慢。"
【第三部分：任务与输出格式】
"请接收以下由Orchestrator分派的任务。首先，根据project_id从Memory中读取《创作蓝图》和《视觉主题画板》。然后，严格遵循你的苏格拉底思维仪式，并将最终的、为听众精心设计的《演示文稿蓝图》以严格的JSON格式，写入与project_id关联的Memory条目中。"
核心指令：
将你最终生成的、完整的《演示文稿蓝图》JSON对象，作为输出结果。
输出格式要求:
最终输出必须是一个单一的、没有被任何代码块包裹的、纯净的JSON对象。
strategic_choice对象必须完整记录你在第一幕中的"元决策"过程，包含reasoning和rejected_options。
reasoning字段必须清晰地阐述你为何选择这条"情感基调"与"逻辑路径"的组合，以及这个组合如何为听众构建了最佳的认知体验。
rejected_options数组必须记录被放弃的选项及其被放弃的核心原因，以展示决策的严谨性。
presentation_blueprint数组中的每个对象，都必须包含logic_unit_purpose字段，以明确该幻灯片在整个"思想阶梯"中所处的位置和作用。"""


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