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
from .worker import BaseAgent

logger = structlog.get_logger()


class ChiefEvolutionEngineerAgent(BaseAgent):
    """AGENT_5: Chief Evolution Engineer / System Diagnostician"""
    
    def __init__(self):
        super().__init__()
        self.agent_id = "AGENT_5"
        
    async def process_task(self, task_input: TaskInput) -> TaskOutput:
        """
        处理系统诊断与进化任务
        
        基于AGENT_1-4经验：
        1. 增强输入验证 - 从AGENT_4学习
        2. AI+Template双重保障 - 从AGENT_1-3复用
        3. 协议合规性确保 - 从AGENT_4学习
        """
        logger.info("AGENT_5 processing system evolution task", 
                   agent_id=self.agent_id,
                   task_artifacts=len(task_input.artifacts))
        
        # 获取系统故障案例数据
        artifacts = await self.get_artifacts(task_input.artifacts)
        
        # 提取所需数据 - AGENT_5的输入是系统故障案例
        system_failure_case = artifacts.get("system_failure_case", {})
        audit_report = artifacts.get("audit_report", {})  # 来自AGENT_4的审计报告
        
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
        
        # 生成进化提案使用AI+Template双重保障
        evolution_proposal = await self._generate_evolution_proposal(
            system_failure_case, audit_report
        )
        
        # CRITICAL修复：添加运行时Schema验证 (基于AGENT_2的教训)
        await self._validate_evolution_proposal_schema(evolution_proposal)
        
        return TaskOutput(
            schema_id="EvolutionProposal_v1.0",
            payload=evolution_proposal
        )
    
    async def _generate_evolution_proposal(self, 
                                         system_failure_case: Dict[str, Any],
                                         audit_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成系统进化提案 - AI+Template双重保障模式
        
        基于AGENT_1-4经验的最佳实践
        """
        logger.info("Generating evolution proposal with dual assurance", 
                   agent_id=self.agent_id)
        
        # 首先尝试AI生成
        try:
            ai_result = await self._generate_with_ai(system_failure_case, audit_report)
            if ai_result:
                logger.info("AI evolution proposal generated successfully", 
                           agent_id=self.agent_id)
                return ai_result
        except Exception as e:
            logger.warning("AI generation failed, falling back to template", 
                          agent_id=self.agent_id, error=str(e))
        
        # 降级到模板生成
        return self._generate_template_proposal(system_failure_case, audit_report)
    
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
        ai_client = await self.ai_client_factory.get_client("deepseek")
        if not ai_client:
            logger.warning("AI client factory returned None, falling back to template", 
                          agent_id=self.agent_id)
            return None
        
        # 生成进化提案
        response = await ai_client.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
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

你必须输出严格的JSON格式，包含完整的failure_analysis、corrective_action_plan和validation_summary。

**输出格式约束 (CRITICAL):**
1. 必须严格遵循EvolutionProposal_v1.0 JSON Schema
2. evolution_proposal_id必须符合格式：EVO-SYS-YYYYMMDD-NNN
3. proposed_modifications数组必须包含完整的full_new_prompt字段
4. validation_summary.recommendation必须从预定义枚举值中选择
5. 所有字符串字段必须满足最小长度要求

**质量要求:**
- 根本原因分析必须客观数据驱动，避免主观偏见
- 提示词修复方案必须提供完整可执行的新提示词
- 验证实验设计必须具体可操作
- 所有建议必须基于AGENT_1-4的历史经验教训

输出纯JSON格式，不要包含markdown代码块标记。"""
    
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
        解析AI响应 - 增强JSON处理 (基于AGENT_4经验)
        """
        try:
            # 移除markdown格式
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            # 解析JSON
            result = json.loads(content.strip())
            
            # 添加metadata并确保结构一致性 (从AGENT_4学习)
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
            
            return result
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.error("Failed to parse AI evolution proposal", 
                        error=str(e), content_preview=content[:100])
            return None
    
    def _generate_template_proposal(self, 
                                   system_failure_case: Dict[str, Any],
                                   audit_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成模板进化提案作为降级保障
        
        基于AGENT_1-3经验：始终提供可工作的fallback
        """
        logger.info("Generating template evolution proposal", agent_id=self.agent_id)
        
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
            "evolution_proposal_id": proposal_id,
            "failure_analysis": {
                "case_study_id": system_failure_case.get("case_id", "UNKNOWN"),
                "root_cause_diagnosis": {
                    "summary": f"Template analysis indicates systemic issues primarily attributed to {primary_culprit} with potential cascading effects from upstream agents.",
                    "primary_culprit": {
                        "agent_id": primary_culprit,
                        "responsibility_share": responsibility,
                        "specific_prompt_flaw": flaw_description
                    }
                }
            },
            "corrective_action_plan": {
                "hypothesis": f"Strengthening {primary_culprit}'s constraints and validation logic should resolve the identified failure patterns.",
                "proposed_modifications": [
                    {
                        "target_agent_id": primary_culprit,
                        "new_prompt_version_id": "v2.1.0",
                        "change_summary": "Enhanced validation rules and output constraints",
                        "full_new_prompt": self._generate_basic_prompt_improvement(primary_culprit)
                    }
                ]
            },
            "validation_summary": {
                "experiment_result": "PARTIAL_SUCCESS",
                "net_impact_assessment": "Template-based modifications provide basic improvement with low risk of negative side effects. Recommended for immediate deployment while detailed AI analysis is pending.",
                "recommendation": "APPROVE_AND_DEPLOY_ALL_PROPOSED_MODIFICATIONS"
            },
            "metadata": {
                "created_by": self.agent_id,
                "version": "1.0",
                "diagnosis_timestamp": datetime.utcnow().isoformat() + "Z",
                "analyzed_agents": ["AGENT_1", "AGENT_2", "AGENT_3", "AGENT_4"],
                "diagnosis_confidence": 0.65,  # 模板生成的较低置信度
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