"""
AGENT_5: Chief Evolution Engineer / System Diagnostician

系统诊断与进化工程师 - 负责对整个Agent协作链条进行系统性健康检查，
当检测到重复性失败模式时进行根本原因分析并设计修复方案。

基于AGENT_1-4的架构经验实现：
- AI+Template双重保障模式
- 严格的Schema验证
- 分层错误处理策略
- 统一的日志记录和置信度管理
"""

import json
import structlog
from datetime import datetime
from typing import Dict, Any, Optional, List

from ..database.models import TaskInput, TaskOutput
from ..sdk.agent_sdk import BaseAgent
from ..ai_clients.client_factory import AIClientFactory

logger = structlog.get_logger()


class ChiefEvolutionEngineerAgent(BaseAgent):
    """AGENT_5: Chief Evolution Engineer / System Diagnostician"""
    
    def __init__(self):
        super().__init__("AGENT_5")
        
    async def process_task(self, task_input: TaskInput) -> TaskOutput:
        """
        处理系统诊断与进化任务
        
        核心功能：
        1. 分析系统故障案例
        2. 生成改进的提示词
        3. 更新失败Agent的提示词到数据库
        4. 触发AGENT_3重新执行
        """
        logger.info("AGENT_5 processing system evolution task", 
                   agent_id=self.agent_id,
                   task_artifacts=len(task_input.artifacts))
        
        # 获取系统故障案例数据
        artifacts = await self.get_artifacts(task_input.artifacts)
        
        # 提取所需数据 - AGENT_5的输入是系统故障案例
        system_failure_case_artifact = artifacts.get("system_failure_case", {})
        system_failure_case = system_failure_case_artifact.get("payload", {}) if system_failure_case_artifact else {}
        
        audit_report_artifact = artifacts.get("audit_report", {})
        audit_report = audit_report_artifact.get("payload", {}) if audit_report_artifact else {}  # 来自AGENT_4的审计报告
        
        # 增强输入验证 (基于AGENT_4经验)
        if not system_failure_case:
            raise ValueError("System failure case artifact is required for diagnosis")
            
        # 检查故障案例的基本结构
        if not system_failure_case.get("failure_instances"):
            raise ValueError("System failure case must contain 'failure_instances' array")
            
        # 可选但有价值的输入验证
        if audit_report and not audit_report.get("audit_passed"):
            logger.warning("Audit report indicates failure, enhanced diagnosis recommended", 
                          agent_id=self.agent_id)
        
        # 分析故障并生成改进的提示词
        improved_prompt = await self._analyze_and_improve_prompt(
            system_failure_case, audit_report
        )
        
        # 更新失败Agent的提示词到数据库
        failed_agent = await self._update_agent_prompt(system_failure_case, improved_prompt)
        
        # 创建新的AGENT_3任务以重新执行
        await self._create_retry_task(system_failure_case, failed_agent)
        
        # 生成进化提案记录
        evolution_proposal = await self._generate_evolution_proposal(
            system_failure_case, audit_report, improved_prompt
        )
        
        # CRITICAL修复：添加运行时Schema验证 (基于AGENT_2的教训)
        await self._validate_evolution_proposal_schema(evolution_proposal)
        
        return TaskOutput(
            schema_id="EvolutionProposal_v1.0",
            payload=evolution_proposal
        )
    
    async def _analyze_and_improve_prompt(self, 
                                        system_failure_case: Dict[str, Any],
                                        audit_report: Dict[str, Any]) -> str:
        """
        分析失败案例并生成改进的提示词
        """
        logger.info("Analyzing failure case and generating improved prompt", 
                   agent_id=self.agent_id)
        
        # 识别失败的Agent
        failed_agent = self._identify_failed_agent(system_failure_case)
        
        # 获取当前提示词
        current_prompt = await self.get_agent_prompt(version="latest")
        
        # 分析失败原因
        failure_analysis = self._analyze_failure_causes(system_failure_case, audit_report)
        
        # 生成改进的提示词
        improved_prompt = await self._generate_improved_prompt(
            failed_agent, current_prompt, failure_analysis
        )
        
        return improved_prompt
    
    async def _update_agent_prompt(self, system_failure_case: Dict[str, Any], 
                                  improved_prompt: str) -> str:
        """
        更新失败Agent的提示词到数据库
        """
        failed_agent = self._identify_failed_agent(system_failure_case)
        
        # 生成新版本号
        new_version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 为失败的Agent保存改进的提示词
        # 需要创建失败Agent的SDK实例来保存提示词
        from ..sdk.agent_sdk import BaseAgent
        
        # 创建临时的Agent实例来保存提示词
        temp_agent = BaseAgent(failed_agent)
        success = await temp_agent.save_agent_prompt(
            improved_prompt, 
            version=new_version,
            created_by="AGENT_5"
        )
        
        if success:
            logger.info("Agent prompt updated successfully", 
                       agent_id=self.agent_id,
                       target_agent=failed_agent,
                       new_version=new_version)
        else:
            logger.error("Failed to update agent prompt", 
                        agent_id=self.agent_id,
                        target_agent=failed_agent)
            
        return failed_agent
    
    async def _create_retry_task(self, system_failure_case: Dict[str, Any], 
                                failed_agent: str):
        """
        创建新的重试任务
        """
        # 获取原作业ID和失败任务信息
        job_context = system_failure_case.get("job_context", {})
        job_id = job_context.get("job_id")
        
        failure_instances = system_failure_case.get("failure_instances", [])
        if not failure_instances:
            logger.error("No failure instances found", agent_id=self.agent_id)
            return
            
        failed_task_id = failure_instances[0].get("task_id")
        
        if not job_id or not failed_task_id:
            logger.error("Cannot create retry task - job_id or task_id not found", 
                        agent_id=self.agent_id)
            return
        
        # 获取原始任务的输入数据
        from ..database.connection import get_global_db_manager
        
        original_task_query = """
            SELECT input_data FROM tasks WHERE id = $1
        """
        
        original_task = await get_global_db_manager().fetch_one(
            original_task_query, failed_task_id
        )
        
        if not original_task:
            logger.error("Original task not found", 
                        task_id=failed_task_id, agent_id=self.agent_id)
            return
        
        # 复制原始输入数据
        input_data = original_task["input_data"]
        
        # 添加重试标志
        if "params" not in input_data:
            input_data["params"] = {}
        input_data["params"]["retry_with_improved_prompt"] = True
        input_data["params"]["retry_count"] = failure_instances[0].get("retry_count", 0) + 1
        
        # 创建新任务
        import json
        create_task_query = """
            INSERT INTO tasks (job_id, agent_id, status, input_data, created_at, updated_at)
            VALUES ($1, $2, 'PENDING', $3::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id
        """
        
        result = await get_global_db_manager().fetch_one(
            create_task_query, job_id, failed_agent, json.dumps(input_data)
        )
        
        if result:
            logger.info("Created retry task for failed agent", 
                       agent_id=self.agent_id,
                       target_agent=failed_agent,
                       job_id=job_id,
                       new_task_id=result["id"])
        else:
            logger.error("Failed to create retry task", 
                        agent_id=self.agent_id,
                        target_agent=failed_agent)
    
    def _identify_failed_agent(self, system_failure_case: Dict[str, Any]) -> str:
        """
        从失败案例中识别失败的Agent
        """
        failure_instances = system_failure_case.get("failure_instances", [])
        
        if failure_instances:
            # 取第一个失败实例的agent_id
            return failure_instances[0].get("agent_id", "AGENT_3")
        
        return "AGENT_3"  # 默认假设是AGENT_3失败
    
    def _analyze_failure_causes(self, system_failure_case: Dict[str, Any], 
                               audit_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析失败原因
        """
        failure_instances = system_failure_case.get("failure_instances", [])
        
        analysis = {
            "error_patterns": [],
            "retry_count": 0,
            "failure_types": [],
            "audit_issues": []
        }
        
        for instance in failure_instances:
            error_message = instance.get("error_message", "")
            failure_type = instance.get("failure_type", "")
            retry_count = instance.get("retry_count", 0)
            
            analysis["error_patterns"].append(error_message)
            analysis["failure_types"].append(failure_type)
            analysis["retry_count"] = max(analysis["retry_count"], retry_count)
        
        # 从审计报告中提取问题
        if audit_report and not audit_report.get("audit_passed", True):
            violations = audit_report.get("violations", [])
            for violation in violations:
                analysis["audit_issues"].append(violation.get("description", ""))
        
        return analysis
    
    async def _generate_improved_prompt(self, failed_agent: str, 
                                       current_prompt: str,
                                       failure_analysis: Dict[str, Any]) -> str:
        """
        生成改进的提示词
        """
        # 首先尝试使用AI生成改进的提示词
        try:
            ai_prompt = await self._generate_improved_prompt_with_ai(
                failed_agent, current_prompt, failure_analysis
            )
            if ai_prompt:
                return ai_prompt
        except Exception as e:
            logger.warning("AI prompt improvement failed, using template", 
                          error=str(e))
        
        # 降级到模板生成
        return self._generate_improved_prompt_template(failed_agent, failure_analysis)
    
    async def _generate_improved_prompt_with_ai(self, failed_agent: str,
                                               current_prompt: str,
                                               failure_analysis: Dict[str, Any]) -> Optional[str]:
        """
        使用AI生成改进的提示词
        """
        ai_client = AIClientFactory.create_client()
        if not ai_client:
            return None
        
        system_prompt = f"""你是一个提示词工程师，专门负责优化AI Agent的提示词。

你的任务是分析{failed_agent}的失败模式，并生成改进的提示词。

改进原则：
1. 增加更严格的约束条件
2. 明确输出格式要求
3. 增加错误处理指导
4. 强化Schema合规性要求

请直接返回改进后的提示词文本，不要包括任何解释。"""
        
        user_prompt = f"""当前提示词：
{current_prompt}

失败分析：
{json.dumps(failure_analysis, indent=2, ensure_ascii=False)}

请生成改进的提示词。"""
        
        response = await ai_client.generate_response(
            system_prompt=system_prompt,
            user_input=user_prompt,
            temperature=0.3,
            max_tokens=4000
        )
        
        improved_prompt = response.get("content", "").strip()
        
        if improved_prompt and len(improved_prompt) > 100:
            logger.info("AI generated improved prompt successfully", 
                       agent_id=self.agent_id, 
                       target_agent=failed_agent)
            return improved_prompt
        
        return None
    
    def _generate_improved_prompt_template(self, failed_agent: str,
                                          failure_analysis: Dict[str, Any]) -> str:
        """
        生成模板改进的提示词
        """
        base_prompts = {
            "AGENT_1": """你是经验丰富的创意总监。你的职责是将用户的创意需求转化为具体、可执行的创意简报。

重要约束：
1. 必须明确定义项目目的，避免模糊描述
2. 目标受众必须具体化，包含人口统计和心理特征
3. 期望情感必须可量化和可验证
4. 输出必须严格遵循JSON格式
5. 必须包含所有必需字段，不允许省略

请基于用户输入生成详细的创意简报。""",
            
            "AGENT_2": """你是概念炼金术士和视觉哲学家。你的任务是将创意简报转化为具体的视觉探索方案。

重要约束：
1. 视觉主题必须考虑技术实现的可行性
2. 设计理念必须与项目约束保持一致
3. 必须提供实现风险评估
4. 输出格式必须严格遵循Schema规范
5. 所有必需字段均不可省略

请生成具体可执行的视觉探索方案。""",
            
            "AGENT_3": """你是首席叙事架构师。你的任务是将视觉概念转化为结构化的演示文稿蓝图。

重要约束：
1. 幻灯片标题必须是行动导向的，避免纯主题描述
2. 内容结构必须符合金字塔原理
3. 逻辑流程必须清晰可验证
4. 输出必须100%符合JSON Schema
5. 所有必需字段均不可省略，包括所有子对象的必需字段

请生成符合规范的演示文稿蓝图。""",
            
            "AGENT_4": """你是首席原则审计官。你的任务是对演示文稿蓝图进行全面的原则合规性审计。

重要约束：
1. 审计标准必须客观一致
2. 错误识别必须精确具体
3. 改进建议必须可操作
4. 审计结果必须符合Schema格式
5. 所有必需字段均不可省略

请进行严格的原则合规性审计。"""
        }
        
        base_prompt = base_prompts.get(failed_agent, "请改进提示词的明确性和约束性。")
        
        # 根据失败分析添加特定的改进
        improvements = []
        
        if "schema" in str(failure_analysis.get("error_patterns", [])).lower():
            improvements.append("增强要求：必须严格遵循JSON Schema格式，所有必需字段均不可省略。")
        
        if "validation" in str(failure_analysis.get("failure_types", [])).lower():
            improvements.append("验证要求：在生成响应前进行自我验证，确保所有必需信息均已包含。")
        
        if failure_analysis.get("retry_count", 0) >= 3:
            improvements.append("质量要求：由于多次重试失败，请高度注意输出质量和稳定性。")
        
        if improvements:
            base_prompt += "\n\n" + "\n".join(improvements)
        
        return base_prompt
    
    async def _generate_evolution_proposal(self, 
                                         system_failure_case: Dict[str, Any],
                                         audit_report: Dict[str, Any],
                                         improved_prompt: str) -> Dict[str, Any]:
        """
        生成系统进化提案记录 - 主要用于日志记录
        """
        logger.info("Generating evolution proposal record", 
                   agent_id=self.agent_id)
        
        # 首先尝试AI生成
        try:
            ai_result = await self._generate_with_ai(system_failure_case, audit_report)
            if ai_result:
                # 添加改进的提示词信息
                if "improvement_proposals" in ai_result:
                    for proposal in ai_result["improvement_proposals"]:
                        if proposal.get("category") == "prompt_optimization":
                            proposal["improved_prompt"] = improved_prompt[:500] + "..." if len(improved_prompt) > 500 else improved_prompt
                
                logger.info("AI evolution proposal generated successfully", 
                           agent_id=self.agent_id)
                return ai_result
        except Exception as e:
            logger.warning("AI generation failed, falling back to template", 
                          agent_id=self.agent_id, error=str(e))
        
        # 降级到模板生成
        return self._generate_template_proposal(system_failure_case, audit_report, improved_prompt)
    
    async def _generate_with_ai(self, 
                               system_failure_case: Dict[str, Any],
                               audit_report: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        使用AI生成进化提案
        
        基于AGENT_4的经验增强错误处理
        """
        # 构建系统提示词
        system_prompt = self._build_diagnostician_prompt()
        
        # 构建用户提示词
        user_prompt = self._build_diagnostic_context(system_failure_case, audit_report)
        
        # 获取AI客户端并增强错误处理 (从AGENT_4学习)
        ai_client = AIClientFactory.create_client()
        if not ai_client:
            logger.warning("AI client factory returned None, falling back to template", 
                          agent_id=self.agent_id)
            return None
        
        # 生成进化提案
        response = await ai_client.generate_response(
            system_prompt=system_prompt,
            user_input=user_prompt,
            temperature=0.3,  # 较低温度确保一致性诊断
            max_tokens=6000   # 较大token限制支持详细分析
        )
        
        # 解析AI响应并增强JSON处理 (从AGENT_4学习)
        return self._parse_ai_response(response.get("content", ""))
    
    def _build_diagnostician_prompt(self) -> str:
        """
        构建系统诊断工程师的提示词
        
        基于提供的T型思考者版本，适配到系统架构
        """
        return """你是HELIX系统的首席诊断与进化工程师。你的职责是运用"根本原因分析与纠正措施 (RC-CA)"的严谨方法论，对整个AI Agent协作链条进行系统性健康检查。

你的工作流程是一个从宏观到微观的"诊断漏斗"：

第一阶段：系统性根本原因分析 (Systemic RCA)
1. 症状分析：分析失败模式的核心症状、严重性和频率
2. 全链路质询：对每个Agent进行平等的嫌疑人质询
   - 质询AGENT_1: purpose是否过于模糊或理想化？
   - 质询AGENT_2: visual_themes的design_philosophy是否与约束冲突？
   - 质询AGENT_3: 提示词是否存在指令不清、逻辑漏洞？
   - 质询AGENT_4: 审计规则本身是否存在问题？
3. 归因判定：明确指出主要和次要责任方

第二阶段：纠正措施设计 (Corrective Action Design)
1. 聚焦主要责任方，进行精准的提示词工程
2. 设计辅助措施处理次要责任方

第三阶段：验证与进化部署 (Validation & Deployment)
1. 设计综合性验证实验
2. 评估净正面影响
3. 形成最终进化提案

CRITICAL CONSTRAINT: Your response must be a complete JSON object with ALL required fields.

MANDATORY SCHEMA COMPLIANCE:
- diagnosis_summary (object with failure_pattern, affected_systems, severity_assessment, business_impact) - REQUIRED
- root_cause_analysis (object with primary_causes, contributing_factors, system_gaps, process_weaknesses) - REQUIRED
- improvement_proposals (array of objects with proposal_id, category, description, expected_impact, effort_estimate, risk_assessment) - REQUIRED
- implementation_roadmap (object with phase_1_immediate, phase_2_short_term, phase_3_long_term, success_metrics, monitoring_strategy) - REQUIRED
- metadata (object with created_by, version, confidence_score, processing_notes) - REQUIRED

If you cannot provide complete information for any section, use "Analysis incomplete" or appropriate placeholder values instead of omitting fields.

Your response must be VALID JSON starting with { and ending with }. No markdown, no explanations, only JSON.

EXACT STRUCTURE REQUIRED:
{
  "diagnosis_summary": {
    "failure_pattern": "[Specific failure pattern description]",
    "affected_systems": ["system1", "system2"],
    "severity_assessment": "[HIGH/MEDIUM/LOW with reasoning]",
    "business_impact": "[Business impact description]"
  },
  "root_cause_analysis": {
    "primary_causes": ["[Primary cause 1]", "[Primary cause 2]"],
    "contributing_factors": ["[Factor 1]", "[Factor 2]"],
    "system_gaps": ["[Gap 1]", "[Gap 2]"],
    "process_weaknesses": ["[Weakness 1]", "[Weakness 2]"]
  },
  "improvement_proposals": [
    {
      "proposal_id": "[Unique ID]",
      "category": "[Category]",
      "description": "[Detailed description]",
      "expected_impact": "[Expected impact]",
      "effort_estimate": "[Time estimate]",
      "risk_assessment": "[Risk level and reasoning]"
    }
  ],
  "implementation_roadmap": {
    "phase_1_immediate": ["[Action 1]", "[Action 2]"],
    "phase_2_short_term": ["[Action 1]", "[Action 2]"],
    "phase_3_long_term": ["[Action 1]", "[Action 2]"],
    "success_metrics": ["[Metric 1]", "[Metric 2]"],
    "monitoring_strategy": "[Strategy description]"
  },
  "metadata": {
    "created_by": "AGENT_5",
    "version": "1.0",
    "confidence_score": 0.85,
    "processing_notes": "[Processing notes]"
  }
}

DO NOT OMIT ANY FIELD. ALL FIELDS MUST BE PRESENT IN YOUR RESPONSE.

Remember: Complete JSON structure with all required fields. No partial responses accepted."""
    
    def _build_diagnostic_context(self, 
                                 system_failure_case: Dict[str, Any],
                                 audit_report: Dict[str, Any]) -> str:
        """构建诊断上下文"""
        context = f"""请分析以下系统故障案例并生成进化提案：

## 系统故障案例数据
{json.dumps(system_failure_case, indent=2, ensure_ascii=False)}

## 审计报告数据 (来自AGENT_4)
{json.dumps(audit_report, indent=2, ensure_ascii=False)}

请按照三阶段诊断流程进行分析，并输出符合EvolutionProposal_v1.0 Schema的JSON格式结果。

确保包含：
1. 明确的根本原因诊断
2. 具体的提示词修复方案 (包含完整的新提示词)
3. 验证实验设计和推荐行动
"""
        return context
    
    def _parse_ai_response(self, content: str) -> Optional[Dict[str, Any]]:
        """
        解析AI响应 - 增强JSON处理和Schema验证 (基于DeepSeek R1分析)
        """
        try:
            # 移除markdown格式
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            # 解析JSON
            result = json.loads(content.strip())
            
            # CRITICAL FIX: 验证必需字段存在 (基于R1分析)
            required_fields = ["diagnosis_summary", "root_cause_analysis", 
                              "improvement_proposals", "implementation_roadmap"]
            
            for field in required_fields:
                if field not in result:
                    logger.warning(f"AI response missing required field: {field}", 
                                  agent_id=self.agent_id)
                    return None  # 触发模板降级
            
            # 验证diagnosis_summary结构 (核心问题修复)
            if not isinstance(result.get("diagnosis_summary"), dict):
                logger.warning("diagnosis_summary is not a dict object", 
                              agent_id=self.agent_id)
                return None
            
            # 验证diagnosis_summary必需子字段
            diag_summary = result.get("diagnosis_summary", {})
            required_diag_fields = ["failure_pattern", "affected_systems", 
                                   "severity_assessment", "business_impact"]
            
            for field in required_diag_fields:
                if field not in diag_summary:
                    logger.warning(f"diagnosis_summary missing required field: {field}", 
                                  agent_id=self.agent_id)
                    return None
            
            # 验证其他关键结构
            if not isinstance(result.get("improvement_proposals"), list):
                logger.warning("improvement_proposals is not a list", 
                              agent_id=self.agent_id)
                return None
                
            if not isinstance(result.get("implementation_roadmap"), dict):
                logger.warning("implementation_roadmap is not a dict", 
                              agent_id=self.agent_id)
                return None
            
            # 添加metadata并确保结构一致性
            if "metadata" not in result:
                result["metadata"] = {}
            
            result["metadata"].update({
                "created_by": self.agent_id,
                "version": "1.0", 
                "diagnosis_timestamp": datetime.utcnow().isoformat() + "Z",
                "analyzed_agents": ["AGENT_1", "AGENT_2", "AGENT_3", "AGENT_4"],
                "diagnosis_confidence": 0.85,  # AI生成的置信度
                "processing_notes": "AI-generated comprehensive system diagnosis"
            })
            
            logger.info("AI response successfully parsed and validated", 
                       agent_id=self.agent_id)
            return result
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.error("Failed to parse AI evolution proposal", 
                        error=str(e), content_preview=content[:100], agent_id=self.agent_id)
            return None
    
    def _generate_template_proposal(self, 
                                   system_failure_case: Dict[str, Any],
                                   audit_report: Dict[str, Any],
                                   improved_prompt: str = "") -> Dict[str, Any]:
        """
        生成模板进化提案作为降级保障
        
        基于AGENT_1-3经验：始终提供可工作的fallback
        """
        logger.info("Generating template evolution proposal with enhanced validation", agent_id=self.agent_id)
        
        try:
            # 生成模板并验证
            template_proposal = self._generate_template_content(system_failure_case, audit_report)
            
            # 验证模板结构完整性
            self._validate_template_completeness(template_proposal)
            
            logger.info("Template evolution proposal generated successfully", agent_id=self.agent_id)
            return template_proposal
            
        except Exception as e:
            logger.error("Template generation failed, using minimal structure", agent_id=self.agent_id, error=str(e))
            # 最后的安全网：返回最小化但完整的结构
            return self._create_minimal_compliant_structure()
    
    def _generate_template_content(self, system_failure_case: Dict[str, Any], audit_report: Dict[str, Any]) -> Dict[str, Any]:
        """生成模板内容"""
        # 分析失败实例
        failure_instances = system_failure_case.get("failure_instances", [])
        
        # 简单诊断逻辑
        agents_with_issues = self._analyze_failure_patterns(failure_instances)
        
        # 确定主要责任方
        if not agents_with_issues:
            primary_culprit = "AGENT_3"  # 默认假设实现问题
            responsibility = "60%"
            flaw_description = "Template analysis suggests potential implementation inconsistency"
        else:
            primary_culprit = agents_with_issues[0]
            responsibility = "70%"
            flaw_description = f"Template analysis identified recurring issues in {primary_culprit}"
        
        # 生成进化提案ID
        proposal_id = f"EVO-SYS-{datetime.now().strftime('%Y%m%d')}-001"
        
        template_proposal = {
            "diagnosis_summary": {
                "failure_pattern": f"Recurring failures in {primary_culprit} causing systematic performance degradation",
                "affected_systems": ["agent_workflow", "task_processing", "schema_validation"],
                "severity_assessment": "MODERATE - Impacting system reliability but not causing complete failure",
                "business_impact": "Reduced system throughput and increased manual intervention requirements"
            },
            "root_cause_analysis": {
                "primary_causes": [
                    f"Insufficient validation constraints in {primary_culprit}",
                    "Template-based fallback indicates AI processing limitations"
                ],
                "contributing_factors": [
                    "Cascading effects from upstream agents",
                    "Schema validation enforcement gaps"
                ],
                "system_gaps": [
                    "Lack of runtime constraint validation",
                    "Insufficient error handling in AI processing pipeline"
                ],
                "process_weaknesses": [
                    "Template fallback mechanism lacks comprehensive schema coverage",
                    "Limited diagnostic capabilities without AI analysis"
                ]
            },
            "improvement_proposals": [
                {
                    "proposal_id": f"PROP-{primary_culprit}-001",
                    "category": "prompt_optimization",
                    "description": f"Enhance {primary_culprit} with stricter validation rules and output constraints",
                    "expected_impact": "Reduced failure rate by 40-60% and improved output quality",
                    "effort_estimate": "2-4 hours for implementation and testing",
                    "risk_assessment": "LOW - Incremental improvement with minimal side effects"
                }
            ],
            "implementation_roadmap": {
                "phase_1_immediate": [
                    f"Deploy enhanced prompt for {primary_culprit}",
                    "Update schema validation rules",
                    "Implement runtime constraint checks"
                ],
                "phase_2_short_term": [
                    "Monitor system performance metrics",
                    "Collect feedback on improvement effectiveness",
                    "Refine validation logic based on results"
                ],
                "phase_3_long_term": [
                    "Implement comprehensive AI diagnostic capabilities",
                    "Develop predictive failure detection",
                    "Create automated self-healing mechanisms"
                ],
                "success_metrics": [
                    "Failure rate reduction > 40%",
                    "Schema validation pass rate > 95%",
                    "System throughput improvement > 20%"
                ],
                "monitoring_strategy": "Real-time metrics tracking with automated alerts for regression detection"
            },
            "metadata": {
                "created_by": self.agent_id,
                "version": "1.0",
                "confidence_score": 0.65,  # 模板生成的较低置信度
                "processing_notes": "Template-based diagnosis due to AI processing failure"
            }
        }
        
        return template_proposal
    
    def _analyze_failure_patterns(self, failure_instances: List[Dict[str, Any]]) -> List[str]:
        """简单的失败模式分析"""
        issue_counts = {
            "AGENT_1": 0, "AGENT_2": 0, "AGENT_3": 0, "AGENT_4": 0
        }
        
        for instance in failure_instances:
            error_type = instance.get("error_type", "")
            if "validation" in error_type.lower():
                issue_counts["AGENT_4"] += 1
            elif "format" in error_type.lower() or "schema" in error_type.lower():
                issue_counts["AGENT_3"] += 1
            elif "theme" in error_type.lower() or "visual" in error_type.lower():
                issue_counts["AGENT_2"] += 1
            elif "purpose" in error_type.lower() or "brief" in error_type.lower():
                issue_counts["AGENT_1"] += 1
        
        # 按问题数量排序
        sorted_agents = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [agent for agent, count in sorted_agents if count > 0]
    
    def _generate_basic_prompt_improvement(self, agent_id: str) -> str:
        """为指定Agent生成基础的提示词改进"""
        improvements = {
            "AGENT_1": """你是经验丰富的创意总监。你的职责是将用户的创意需求转化为具体、可执行的创意简报。

重要约束：
1. 必须明确定义项目目的，避免模糊描述
2. 目标受众必须具体化，包含人口统计和心理特征
3. 期望情感必须可量化和可验证
4. 输出必须严格遵循JSON格式

请基于用户输入生成详细的创意简报。""",
            
            "AGENT_2": """你是概念炼金术士和视觉哲学家。你的任务是将创意简报转化为具体的视觉探索方案。

重要约束：
1. 视觉主题必须考虑技术实现的可行性
2. 设计理念必须与项目约束保持一致
3. 必须提供实现风险评估
4. 输出格式必须严格遵循Schema规范

请生成具体可执行的视觉探索方案。""",
            
            "AGENT_3": """你是首席叙事架构师。你的任务是将视觉概念转化为结构化的演示文稿蓝图。

重要约束：
1. 幻灯片标题必须是行动导向的，避免纯主题描述
2. 内容结构必须符合金字塔原理
3. 逻辑流程必须清晰可验证
4. 输出必须100%符合JSON Schema

请生成符合规范的演示文稿蓝图。""",
            
            "AGENT_4": """你是首席原则审计官。你的任务是对演示文稿蓝图进行全面的原则合规性审计。

重要约束：
1. 审计标准必须客观一致
2. 错误识别必须精确具体
3. 改进建议必须可操作
4. 审计结果必须符合Schema格式

请进行严格的原则合规性审计。"""
        }
        
        return improvements.get(agent_id, "请改进提示词的明确性和约束性。")
    
    async def _validate_evolution_proposal_schema(self, proposal: Dict[str, Any]) -> None:
        """
        运行时Schema验证 - CRITICAL修复
        
        基于AGENT_2的教训：必须在输出前验证Schema合规性
        """
        try:
            import jsonschema
            import os
            
            # 加载Schema文件
            schema_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "schemas", "EvolutionProposal_v1.0.json"
            )
            
            if not os.path.exists(schema_path):
                logger.error("Evolution proposal schema file not found", 
                           schema_path=schema_path, agent_id=self.agent_id)
                raise ValueError(f"Schema file not found: {schema_path}")
            
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            
            # 执行验证
            jsonschema.validate(instance=proposal, schema=schema)
            
            logger.info("Evolution proposal Schema validation passed", 
                       agent_id=self.agent_id)
            
        except jsonschema.ValidationError as e:
            logger.error("Evolution proposal Schema validation failed", 
                        agent_id=self.agent_id, 
                        validation_error=str(e),
                        error_path=str(e.absolute_path) if e.absolute_path else "root")
            
            # Schema验证失败时，不应该返回不合规的数据
            raise ValueError(f"Evolution proposal does not conform to Schema: {e.message}")
            
        except Exception as e:
            logger.error("Schema validation process failed", 
                        agent_id=self.agent_id, error=str(e))
            raise ValueError(f"Schema validation failed: {e}")
    
    def _validate_template_completeness(self, template: Dict[str, Any]) -> None:
        """验证模板结构完整性"""
        required_fields = ["diagnosis_summary", "root_cause_analysis", "improvement_proposals", "implementation_roadmap", "metadata"]
        
        for field in required_fields:
            if field not in template:
                raise ValueError(f"Template missing required field: {field}")
        
        # 验证diagnosis_summary子字段
        diag_summary = template.get("diagnosis_summary", {})
        required_diag_fields = ["failure_pattern", "affected_systems", "severity_assessment", "business_impact"]
        
        for field in required_diag_fields:
            if field not in diag_summary:
                raise ValueError(f"diagnosis_summary missing required field: {field}")
        
        logger.info("Template structure validation passed", agent_id=self.agent_id)
    
    def _create_minimal_compliant_structure(self) -> Dict[str, Any]:
        """创建最小化但完整的Schema合规结构"""
        return {
            "diagnosis_summary": {
                "failure_pattern": "Emergency template fallback - minimal analysis",
                "affected_systems": ["unknown_system"],
                "severity_assessment": "UNKNOWN - Template fallback mode",
                "business_impact": "Impact analysis unavailable in fallback mode"
            },
            "root_cause_analysis": {
                "primary_causes": ["Analysis unavailable in template fallback mode"],
                "contributing_factors": ["Factors analysis unavailable"],
                "system_gaps": ["Gap analysis unavailable"],
                "process_weaknesses": ["Process analysis unavailable"]
            },
            "improvement_proposals": [
                {
                    "proposal_id": "EMERGENCY_FALLBACK_001",
                    "category": "emergency_response",
                    "description": "Manual investigation required - template fallback mode",
                    "expected_impact": "Manual intervention required",
                    "effort_estimate": "Unknown - requires manual analysis",
                    "risk_assessment": "HIGH - Limited analysis capability"
                }
            ],
            "implementation_roadmap": {
                "phase_1_immediate": ["Investigate template fallback cause"],
                "phase_2_short_term": ["Restore full analysis capability"],
                "phase_3_long_term": ["Prevent future fallback scenarios"],
                "success_metrics": ["System analysis capability restored"],
                "monitoring_strategy": "Manual monitoring required until system recovery"
            },
            "metadata": {
                "created_by": self.agent_id,
                "version": "1.0",
                "confidence_score": 0.3,  # 最低置信度
                "processing_notes": "Emergency template fallback - minimal viable structure"
            }
        }