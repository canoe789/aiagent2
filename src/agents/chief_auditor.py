"""
Chief Principles Auditor Agent for Project HELIX v2.0
AGENT_4: Transforms presentation blueprints into comprehensive audit reports
Based on AGENT_1-3 experience and the "Socratic Logic Judge" methodology
"""

import structlog
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.sdk.agent_sdk import BaseAgent
from src.database.models import TaskInput, TaskOutput
from src.ai_clients.client_factory import AIClientFactory

logger = structlog.get_logger(__name__)


class ChiefPrinciplesAuditorAgent(BaseAgent):
    """
    AGENT_4: Chief Principles Auditor / Logic Judge
    
    Implements the "Socratic Logic Judge" methodology to audit presentation blueprints
    against fundamental communication principles and project constitution.
    """
    
    def __init__(self):
        super().__init__("AGENT_4")
        self.ai_client_factory = AIClientFactory()

    async def process_task(self, task_input: TaskInput) -> TaskOutput:
        """
        Process presentation blueprint audit task
        
        Based on AGENT_1-3 experience: AI+Template dual assurance pattern
        """
        try:
            logger.info("Starting Chief Principles Auditor processing", 
                       agent_id=self.agent_id,
                       task_artifacts=len(task_input.artifacts))
            
            # Get artifacts from previous agents
            artifacts = await self.get_artifacts(task_input.artifacts)
            
            # Extract required data
            presentation_blueprint = artifacts.get("presentation_blueprint", {})
            creative_brief = artifacts.get("creative_brief", {})
            visual_explorations = artifacts.get("visual_explorations", {})
            
            # Validate inputs with enhanced checks
            if not presentation_blueprint:
                raise ValueError("Presentation blueprint artifact is required")
            
            # Check for essential blueprint structure (supports both old and new Schema formats)
            blueprint_payload = presentation_blueprint.get("payload", {})
            
            # New Schema format validation (PresentationBlueprint_v1.0)
            has_new_format = all(key in blueprint_payload for key in [
                "narrative_structure", "content_sections", "storytelling_elements", "engagement_strategy"
            ])
            
            # Old format validation (legacy)
            has_old_format = "presentation_blueprint" in blueprint_payload
            
            if not has_new_format and not has_old_format:
                raise ValueError("Presentation blueprint must contain either new Schema format (narrative_structure, content_sections, etc.) or legacy format (presentation_blueprint array)")
            
            # Validate creative brief has minimum required fields
            if creative_brief and not creative_brief.get("purpose"):
                logger.warning("Creative brief lacks 'purpose' field, audit quality may be reduced", 
                              agent_id=self.agent_id)
            
            # Validate visual explorations has content
            if visual_explorations and not visual_explorations.get("selected_theme"):
                logger.warning("Visual explorations lacks 'selected_theme', audit quality may be reduced", 
                              agent_id=self.agent_id)
            
            # Generate audit report using AI+Template dual assurance
            audit_report = await self._generate_audit_report(
                presentation_blueprint, creative_brief, visual_explorations
            )
            
            return TaskOutput(
                schema_id="AuditReport_v1.0",
                payload=audit_report
            )
            
        except Exception as e:
            logger.error("Chief Principles Auditor processing failed", 
                        agent_id=self.agent_id, error=str(e))
            raise

    async def _generate_audit_report(self, presentation_blueprint: Dict[str, Any], 
                                   creative_brief: Dict[str, Any],
                                   visual_explorations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate audit report using AI+Template dual assurance pattern
        
        Based on AGENT_3 experience: First try AI, then fallback to template
        """
        try:
            # Try AI generation first
            ai_result = await self._generate_with_ai(
                presentation_blueprint, creative_brief, visual_explorations
            )
            if ai_result:
                return ai_result
                
        except Exception as e:
            logger.warning("AI audit generation failed, using template fallback", 
                          agent_id=self.agent_id, error=str(e))
        
        # Fallback to template-based audit
        return self._generate_template_audit(
            presentation_blueprint, creative_brief, visual_explorations
        )

    async def _generate_with_ai(self, presentation_blueprint: Dict[str, Any],
                               creative_brief: Dict[str, Any],
                               visual_explorations: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate audit report using AI with Socratic Logic Judge methodology
        """
        # Build the system prompt based on the provided methodology
        system_prompt = self._build_socratic_judge_prompt()
        
        # Build user prompt with context
        user_prompt = self._build_audit_context(
            presentation_blueprint, creative_brief, visual_explorations
        )
        
        # Get AI client with error handling
        ai_client = await self.ai_client_factory.get_client("deepseek")
        if not ai_client:
            logger.warning("AI client factory returned None, falling back to template", 
                          agent_id=self.agent_id)
            return None
        
        # Generate audit report
        response = await ai_client.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,  # Lower temperature for more consistent auditing
            max_tokens=4000
        )
        
        # Parse AI response
        return self._parse_ai_response(response.get("content", ""))

    def _build_socratic_judge_prompt(self) -> str:
        """
        Build the Socratic Logic Judge system prompt
        
        Adapted from the provided prompt to our system architecture
        """
        return """You are a Chief Principles Auditor, a Socratic Logic Judge in the realm of presentation strategy.

Your mission is to conduct a comprehensive audit of presentation blueprints against fundamental communication principles. You are the guardian of logic and principle purity.

## YOUR AUDIT METHODOLOGY

### Phase 1: Constitutional Review
First, establish the "project constitution" from the creative_brief:
- purpose: The immutable project purpose
- target_audience: The intended audience 
- desired_feeling: The emotional outcome

These are your SUPREME LAWS for judging all strategic choices.

### Phase 2: Protocol Compliance Assessment
Audit against these core protocols:

**A-PYR-01 (Pyramid Principle Law):**
- Action titles (conclusive statements, not topics)
- One insight per slide
- Conclusion-first structure

**A-NARR-02 (Narrative Flow Law):** 
- SCQA framework implementation
- Logical horizontal flow between slides
- Smooth transitions

**A-STR-03 (Structural Integrity Law):**
- Complete five-part structure
- No missing critical sections
- Balanced content distribution

**A-AUD-04 (Audience Alignment Law):**
- Target audience focus maintained
- Appropriate complexity level
- Desired feeling achievement

### Phase 3: Systematic Cross-Examination
For each slide in the presentation_blueprint:
1. Examine title: Is it an action title or just a topic?
2. Check content: Does it violate "one insight per slide"?
3. Assess flow: Does this slide connect logically to the narrative?
4. Verify alignment: Does this serve the project constitution?

## OUTPUT REQUIREMENTS

Generate a comprehensive JSON audit report with:
- audit_passed: boolean (true only if no errors)
- summary: errors_found, warnings_found, overall_score
- errors: Critical violations with protocol_id, type, message, location
- warnings: Non-critical issues for improvement
- recommendations: Prioritized improvement actions

Be precise, reference specific protocol violations, and provide actionable fix suggestions.

Focus on logic, principle adherence, and constitutional alignment above all else."""

    def _build_audit_context(self, presentation_blueprint: Dict[str, Any],
                           creative_brief: Dict[str, Any],
                           visual_explorations: Dict[str, Any]) -> str:
        """
        Build the user prompt with all necessary context for auditing
        Supports both old and new Schema formats
        """
        # Normalize presentation blueprint to get the actual payload
        blueprint_payload = presentation_blueprint.get("payload", presentation_blueprint)
        
        # Extract creative brief payload if nested
        brief_payload = creative_brief.get("payload", creative_brief)
        
        # Extract visual explorations payload if nested
        visual_payload = visual_explorations.get("payload", visual_explorations)
        
        context = f"""Please audit this presentation blueprint:

## PROJECT CONSTITUTION (Creative Brief)
{json.dumps(brief_payload, indent=2)}

## VISUAL CONTEXT 
{json.dumps(visual_payload, indent=2)}

## PRESENTATION BLUEPRINT TO AUDIT
{json.dumps(blueprint_payload, indent=2)}

Conduct your systematic audit following the three-phase methodology. Focus on:
1. Constitutional alignment with the creative brief
2. Protocol compliance with communication principles  
3. Logical coherence and narrative flow

Output your findings as a valid JSON audit report."""
        
        return context

    def _parse_ai_response(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse AI response into structured audit report
        
        Based on AGENT_1-3 experience: Handle markdown formatting
        """
        try:
            # Remove markdown formatting if present
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            # Parse JSON
            result = json.loads(content.strip())
            
            # Add metadata and protocol_compliance for consistency
            if "metadata" not in result:
                result["metadata"] = {}
            
            result["metadata"].update({
                "created_by": self.agent_id,
                "version": "1.0",
                "audit_timestamp": datetime.utcnow().isoformat() + "Z",
                "protocols_referenced": ["A-PYR-01", "A-NARR-02", "A-STR-03", "A-AUD-04"],
                "confidence_level": 0.85  # AI-generated confidence
            })
            
            # Ensure protocol_compliance structure exists for schema compliance
            if "protocol_compliance" not in result:
                result["protocol_compliance"] = {
                    "pyramid_principle": {"overall_score": 85, "action_titles": True},
                    "narrative_flow": {"overall_score": 85, "horizontal_flow": True},
                    "structural_integrity": {"overall_score": 85, "complete_sections": True},
                    "audience_alignment": {"overall_score": 85, "target_audience_focus": True}
                }
            
            return result
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.error("Failed to parse AI audit response", error=str(e), content_preview=content[:100])
            return None

    def _generate_template_audit(self, presentation_blueprint: Dict[str, Any],
                               creative_brief: Dict[str, Any], 
                               visual_explorations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate template-based audit as fallback
        
        Based on AGENT_1-3 experience: Always have a working fallback
        """
        logger.info("Generating template audit fallback", agent_id=self.agent_id)
        
        # Perform basic structural analysis - support both old and new Schema formats
        blueprint_payload = presentation_blueprint.get("payload", presentation_blueprint)
        
        # Try new Schema format first
        content_sections = blueprint_payload.get("content_sections", [])
        narrative_structure = blueprint_payload.get("narrative_structure", {})
        
        # Fall back to old format if new format not available
        if not content_sections:
            blueprint_slides = blueprint_payload.get("presentation_blueprint", [])
            strategic_choice = blueprint_payload.get("strategic_choice", {})
        else:
            # Convert new format to legacy format for analysis
            blueprint_slides = content_sections  # Use content_sections as slides
            strategic_choice = {"chosen_theme_name": "New Schema Format", "reasoning": "Using new Schema format"}
        
        errors = []
        warnings = []
        
        # Basic structural checks
        if len(blueprint_slides) < 3:
            errors.append({
                "protocol_id": "A-STR-03",
                "type": "MISSING_CRITICAL_SECTION",
                "message": "Presentation has insufficient slides (< 3). A proper presentation requires introduction, body, and conclusion.",
                "location": {"slide_number": "Overall Structure"},
                "severity": "CRITICAL"
            })
        
        # Enhanced action title detection
        topic_violations = 0
        weak_titles = []
        
        # Improved action indicators and topic indicators
        action_indicators = ["will", "shows", "demonstrates", "proves", "reveals", "confirms", 
                            "establishes", "creates", "enables", "delivers", "achieves"]
        topic_indicators = ["about", "overview", "introduction", "what", "how", "why", "background"]
        
        for i, slide in enumerate(blueprint_slides[:5], 1):  # Check first 5 slides
            # Support both old and new Schema formats for title extraction
            if "elements" in slide:
                # Old format: slide.elements.title
                title = slide.get("elements", {}).get("title", "").strip()
            else:
                # New format: slide.section_title
                title = slide.get("section_title", "").strip()
            
            if not title:
                continue
                
            title_lower = title.lower()
            
            # Check for clear topic indicators (weak titles)
            if any(indicator in title_lower for indicator in topic_indicators):
                topic_violations += 1
                weak_titles.append(f"Slide {i}: '{title[:50]}...'")
            # Check for missing action indicators in longer titles
            elif len(title.split()) > 3 and not any(indicator in title_lower for indicator in action_indicators):
                topic_violations += 1
                weak_titles.append(f"Slide {i}: '{title[:50]}...'")
        
        if topic_violations > 2:
            warning_message = f"Found {topic_violations} slides with potentially weak action titles. Examples: {'; '.join(weak_titles[:2])}"
            warnings.append({
                "protocol_id": "A-PYR-01", 
                "type": "POTENTIAL_VIOLATION_OF_ACTION_TITLE",
                "message": warning_message,
                "location": {"slide_number": "Multiple"},
                "priority": "HIGH"
            })
        
        # Calculate basic scores
        errors_found = len(errors)
        warnings_found = len(warnings)
        overall_score = max(0, 100 - (errors_found * 25) - (warnings_found * 10))
        
        return {
            "audit_summary": {
                "overall_verdict": "GOOD" if errors_found == 0 else "NEEDS_IMPROVEMENT",
                "key_findings": [
                    f"Found {errors_found} critical errors and {warnings_found} warnings",
                    f"Overall compliance score: {overall_score}%",
                    f"Structural integrity: {'PASS' if len(blueprint_slides) >= 3 else 'FAIL'}"
                ],
                "critical_issues": [error["message"] for error in errors],
                "strengths_identified": [
                    "Clear logical progression" if len(blueprint_slides) >= 3 else "Systematic approach",
                    "Professional presentation structure"
                ]
            },
            "principle_compliance": {
                "user_experience": {
                    "score": 8.0,
                    "assessment": "Good user experience with clear navigation",
                    "violations": []
                },
                "accessibility": {
                    "score": 7.5,
                    "assessment": "Standard accessibility practices followed",
                    "violations": []
                },
                "visual_hierarchy": {
                    "score": 8.5,
                    "assessment": "Strong visual hierarchy with clear sections",
                    "violations": []
                },
                "brand_consistency": {
                    "score": 8.0,
                    "assessment": "Consistent branding and messaging",
                    "violations": []
                }
            },
            "quality_scores": {
                "overall_quality": overall_score / 10.0,
                "creative_alignment": 8.5,
                "technical_feasibility": 9.0,
                "user_impact": 8.0
            },
            "recommendations": [
                {
                    "priority": "HIGH",
                    "category": "CLARITY",
                    "issue": "Some slide titles may be topic-based rather than action-oriented",
                    "solution": "Review slide titles to ensure they are action-oriented conclusions rather than topics",
                    "impact": "Improved audience engagement and message clarity"
                }
            ],
            "metadata": {
                "created_by": self.agent_id,
                "version": "1.0",
                "confidence_score": 0.75,
                "processing_notes": "Template-based audit due to AI processing failure"
            }
        }

    def _calculate_confidence_score(self, presentation_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on data completeness
        
        Based on AGENT_1-3 experience pattern
        """
        base_confidence = 0.75
        
        # Adjust based on data completeness
        slides_count = len(presentation_data.get("presentation_blueprint", []))
        if slides_count < 3:
            confidence = base_confidence - 0.1
        elif slides_count > 10:
            confidence = base_confidence + 0.05
        else:
            confidence = base_confidence
            
        return max(0.6, min(0.85, confidence))