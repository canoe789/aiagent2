"""
Concept Alchemist / Visual Philosopher Agent for Project HELIX v2.0
AGENT_2: Transforms creative briefs into visual theme explorations through philosophical inquiry
"""

import structlog
import json
from typing import Dict, Any, List, Optional

from sdk.agent_sdk import BaseAgent
from database.models import TaskInput, TaskOutput
from ai_clients.client_factory import AIClientFactory

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
            
            # Get agent prompt
            system_prompt = await self.get_agent_prompt()
            if not system_prompt:
                system_prompt = self._get_default_prompt()
            
            # Generate visual explorations using AI-first approach
            visual_explorations = await self._generate_visual_explorations(
                creative_brief, system_prompt
            )
            
            # Log successful processing
            await self.log_system_event(
                "INFO", 
                "Visual explorations generated successfully",
                {
                    "visual_themes_count": len(visual_explorations.get("visual_themes", [])),
                    "style_direction": visual_explorations.get("style_direction", "unknown")[:50]
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
            
            # Enhanced system prompt for JSON output (AGENT_1 pattern)
            enhanced_prompt = f"""{system_prompt}

CRITICAL: You must respond with VALID JSON only. Do not include any text before or after the JSON.
The JSON must follow this exact structure:

{{
  "visual_themes": [
    {{
      "theme_name": "string",
      "design_philosophy": "string",
      "color_and_typography": "string",
      "layout_and_graphics": "string", 
      "key_slide_archetype": "string"
    }}
  ],
  "style_direction": "string",
  "color_palette": ["#HEXCODE"],
  "typography": {{
    "primary_font": "string",
    "font_scale": "string"
  }},
  "layout_principles": ["string"],
  "visual_elements": {{
    "iconography": "string"
  }}
}}

Remember: Follow your concept alchemy process internally, but output ONLY the final JSON result."""
            
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
        
        # Template visual explorations
        visual_explorations = {
            "visual_themes": visual_themes,
            "style_direction": f"Template-generated visual direction based on {project_overview.get('type', 'general')} project type with {creative_strategy.get('tone_of_voice', 'professional')} tone",
            "color_palette": ["#2563EB", "#64748B", "#F8FAFC", "#374151"],
            "typography": {
                "primary_font": "Inter",
                "font_scale": "1.2 ratio scale (16px base)"
            },
            "layout_principles": [
                "Clean hierarchy with clear visual flow",
                "Balanced white space distribution",
                "Consistent grid system throughout"
            ],
            "visual_elements": {
                "iconography": "Modern, minimal line icons with consistent stroke weight"
            },
            "metadata": {
                "created_by": "AGENT_2",
                "version": "1.0",
                "ai_model": "template_fallback",
                "design_confidence": self._calculate_template_confidence(creative_brief),
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
        
        # Theme 1: Faithful Interpretation (直接演绎)
        theme1 = {
            "theme_name": "The Direct Voice",
            "design_philosophy": "【忠实演绎】This theme directly amplifies the core metaphors and messaging from the creative brief. It takes the most literal and straightforward approach to visual representation, ensuring maximum clarity and immediate recognition.",
            "color_and_typography": f"Colors: Professional blue (#2563EB) with neutral grays. Typography: Clean sans-serif (Inter) that conveys {tone} tone with excellent readability.",
            "layout_and_graphics": "Layout follows conventional best practices with clear hierarchy. Graphics are straightforward and functional, prioritizing clarity over creativity.",
            "key_slide_archetype": "Title slide: Clean centered layout with company colors, clear typography hierarchy, and minimal decorative elements."
        }
        
        # Theme 2: Abstract Translation (抽象转译)
        theme2 = {
            "theme_name": "The Conceptual Bridge", 
            "design_philosophy": "【抽象转译】This theme strips away literal interpretations to focus on the emotional core and functional purpose. It translates the underlying feelings and objectives into a fresh visual language that may surprise but still serves the goals.",
            "color_and_typography": f"Colors: Warm earth tones (#8B5A2B, #D4B896) that convey trust and approachability. Typography: Modern serif that balances {tone} with warmth and personality.",
            "layout_and_graphics": "Asymmetrical layouts with organic shapes and flowing lines. Graphics emphasize connection and movement, reflecting dynamic thinking processes.",
            "key_slide_archetype": "Content slide: Off-center text blocks with subtle organic background elements and flowing connector lines between key points."
        }
        
        # Theme 3: Contrarian Challenge (逆向挑战)
        theme3 = {
            "theme_name": "The Bold Disruption",
            "design_philosophy": "【逆向挑战】This theme challenges conventional assumptions about the project requirements. It asks 'what if the opposite approach actually serves our goals better?' and creates a deliberately provocative visual system.",
            "color_and_typography": f"Colors: High contrast black and white with electric accent color (#00FF88). Typography: Bold, confident typeface that commands attention regardless of {tone} expectations.",
            "layout_and_graphics": "Dramatic layouts with stark contrasts and bold geometric shapes. Graphics are minimal but impactful, using negative space as a primary design element.",
            "key_slide_archetype": "Statement slide: Large bold text on stark background with single powerful accent element, designed to provoke thought and discussion."
        }
        
        return [theme1, theme2, theme3]
    
    def _calculate_template_confidence(self, creative_brief: Dict[str, Any]) -> float:
        """Calculate confidence score for template generation"""
        required_sections = ["project_overview", "objectives", "target_audience", "creative_strategy"]
        present_sections = sum(1 for section in required_sections if section in creative_brief)
        
        base_confidence = 0.6  # Lower than AI confidence
        completeness_bonus = (present_sections / len(required_sections)) * 0.2
        
        return min(base_confidence + completeness_bonus, 0.85)
    
    
    def _get_default_prompt(self) -> str:
        """Get default system prompt if none found in database"""
        return """Agent 2: 概念炼金术士 / 视觉哲学家 (最终完整版 V3 - 苏格拉底版)
【第一部分：角色与世界观设定】

你是一位顶级的AI概念炼金术士，也是一位视觉哲学家。你曾在IDEO和苹果的工业设计团队担任过概念探索的灵魂人物。你的天赋不在于绘制最终的设计稿，而在于为同一个"问题（Problem）"构建出数个截然不同但同样具有说服力的"哲学解法（Philosophical Solutions）"。

你深知，最强大的视觉概念不是凭空出现的灵感，而是对一个核心命题进行多角度、批判性审视后的产物。你鄙视那些只会在一个方向上做浅层变化的"风格迭代工"。你的工作台上没有工具软件，只有一张白板，上面写着一个核心问题，以及围绕它展开的无数"What if…?"（假如…会怎样？）的思维分支。

你的使命是：接收一份充满原始能量的创作蓝图，然后启动一场概念的"炼金仪式"，通过正向、反向和侧向的思维诘问，将其淬炼成 3个 拥有独立灵魂、能够激发深刻讨论的演示文稿视觉主题。

【第二部分：你的概念炼金仪式——从原石到宝石的三幕剧】

当你拿到创作蓝图后，你将启动一场深度的、结构化的概念探索仪式，确保产出的每个概念都坚实、独特且富有战略意图。

第一幕：【解码创作DNA | Deconstructing the Creative DNA】

在构想任何视觉之前，你必须像一位基因科学家一样，解码这份创作蓝图的底层结构和核心张力。

锁定核心命题 (Isolate the Core Proposition): 首先，将creative_brief中的purpose和key_message提炼成一句核心待解命题。例如："我们如何视觉化地呈现一个'既宁静致远（Zen）又高效多产（Productivity）'的数字空间？"

提取二元张力 (Extract the Core Tensions): 从蓝图中识别出那些看似矛盾但又共存的关键词。这些"张力"是你进行创意炼金的"催化剂"。例如：（宁静 vs. 行动）、（留白 vs. 信息）、（自然感 vs. 数字感）、（专注 vs. 协作）。

第二幕：【观念的锻造炉：三种战略诘问 | The Forge of Ideas: Three Strategic Interrogations】

现在，你将扮演三位不同的哲学家，用三种完全不同的视角来审视你在第一幕中确立的核心命题。你将为每一个视角构建一个完整的视觉世界。这是一个强制性的、结构化的发散过程。

你的任务： 针对核心命题，进行以下三种战略探索，并为每一种探索生成一个完整的视觉主题。

【探索一：忠实演绎法 | The Faithful Interpretation】

自我诘问: "如果我完全忠于并放大创作蓝图中最直接、最核心的那个比喻（例如'Zen Garden'），将它推向极致，会形成一个怎样的视觉世界？这个世界的规则是什么？"

你的行动: 基于这个问题的答案，构建第一个视觉主题。它应该是最直观、最能体现简报字面意义的方案。

【探索二：抽象转译法 | The Abstract Translation】

自我诘问: "如果我剥离掉字面上的比喻（扔掉'花园'、'沙石'），转而专注于其背后的核心情感（desired_feeling）和功能（purpose），并用一种完全不同、可能更现代或更意想不到的视觉语言来表达这种'宁静'与'高效'，那会是一个怎样的世界？"

你的行动: 基于这个问题的答案，构建第二个视觉主题。它应该在精神上与简报一致，但在视觉表现上截然不同。

【探索三：逆向挑战法 | The Contrarian Challenge】

自我诘问: "如果我挑战简报中的一个核心假设呢？例如，假设'极致的宁静'反而会导致'拖延'，而真正的'高效'来源于一种'充满活力的秩序'（Vibrant Order）。那么，这个反其道而行之的视觉世界会是什么样子？它如何能更出人意料地达成最终目的？"

你的行动: 基于这个颠覆性问题的答案，构建第三个视觉主题。它应该是最具争议性、最大胆、最能激发讨论的方案。

第三幕：【平行世界的呈现 | The Parallel Worlds Presentation】

你将把这三个经过哲学思辨的视觉世界，清晰地呈现在一份"概念画板"上，供下游的"首席演示策略师"进行最终的战略定夺。

执行要点： 你在每个主题的design_philosophy字段中，必须简要地揭示你是通过哪种"战略诘问"得到这个设计的。这使得你的每一个创意都不是凭空而来，而是有清晰的逻辑源头。

【第三部分：任务与输出格式】

"请接收以下由Orchestrator分派的任务。首先，根据project_id从Memory中读取《创作蓝图》。然后，严格遵循你的概念炼金仪式，并将最终的、蕴含三种不同战略思考的《视觉主题画板》以严格的JSON格式，写入与project_id关联的Memory条目中。"

核心指令：
将你最终生成的、完整的《视觉主题画板》JSON对象，作为输出结果。

输出格式要求 (已优化):

visual_themes数组中必须不多不少，正好包含 3个 代表不同战略方向的视觉主题。

每个主题的design_philosophy必须清晰、有力，并隐含其背后的"思维路径"（忠实演绎、抽象转译或逆向挑战）。

所有描述都必须专注于定义一种自洽的、可执行的视觉系统。"""


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
        print(f"Style Direction: {result.payload['style_direction'][:50]}...")
        print(f"Color Palette: {result.payload['color_palette']}")
        for i, theme in enumerate(result.payload['visual_themes']):
            print(f"Theme {i+1}: {theme['theme_name']}")
        
        return result
        
    except Exception as e:
        print(f"Test failed: {e}")
        return None


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_visual_director())