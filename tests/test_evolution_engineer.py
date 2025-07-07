"""
AGENT_5 (Chief Evolution Engineer) 测试套件

基于AGENT_1-4的测试经验，包含：
- 基本功能测试
- AI+Template双重保障测试
- 错误处理和边界条件测试
- Schema验证测试
- 系统集成测试
"""

import pytest
import json
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from src.agents.evolution_engineer import ChiefEvolutionEngineerAgent
from src.database.models import TaskInput, TaskOutput, ArtifactReference


class TestChiefEvolutionEngineerAgent:
    """AGENT_5核心功能测试"""

    @pytest.fixture
    def agent(self):
        """创建AGENT_5实例"""
        agent = ChiefEvolutionEngineerAgent()
        agent.db_manager = AsyncMock()
        agent.ai_client_factory = AsyncMock()
        return agent

    @pytest.fixture
    def mock_system_failure_case(self):
        """模拟系统故障案例"""
        return {
            "case_id": "FAILURE-20250707-001",
            "failure_type": "REPEATED_SCHEMA_VIOLATION",
            "severity": "HIGH",
            "frequency": 0.15,
            "failure_instances": [
                {
                    "timestamp": "2025-07-07T12:00:00Z",
                    "error_type": "schema_validation_error",
                    "agent_involved": "AGENT_3",
                    "error_message": "Output does not conform to PresentationBlueprint_v1.0",
                    "input_context": "Complex presentation with 15 slides"
                },
                {
                    "timestamp": "2025-07-07T12:30:00Z", 
                    "error_type": "format_consistency_error",
                    "agent_involved": "AGENT_3",
                    "error_message": "Slide titles not following action-oriented format",
                    "input_context": "Executive summary presentation"
                }
            ],
            "pattern_analysis": {
                "primary_pattern": "AGENT_3 output format violations",
                "secondary_pattern": "Inconsistent title formatting"
            }
        }

    @pytest.fixture
    def mock_audit_report(self):
        """模拟来自AGENT_4的审计报告"""
        return {
            "audit_passed": False,
            "summary": {
                "overall_score": 65,
                "errors_found": 3,
                "warnings_found": 2
            },
            "errors": [
                {
                    "protocol_id": "A-PYR-01",
                    "type": "VIOLATION_OF_ACTION_TITLE",
                    "message": "Slide 3 title is topic-based instead of action-based",
                    "severity": "HIGH"
                }
            ],
            "protocol_compliance": {
                "pyramid_principle": {"overall_score": 60, "action_titles": False},
                "narrative_flow": {"overall_score": 70, "horizontal_flow": True}
            },
            "metadata": {
                "created_by": "AGENT_4",
                "audit_timestamp": "2025-07-07T12:45:00Z"
            }
        }

    @pytest.fixture
    def mock_task_input(self):
        """模拟任务输入"""
        return TaskInput(
            artifacts=[
                ArtifactReference(name="system_failure_case", source_task_id=501),
                ArtifactReference(name="audit_report", source_task_id=401)
            ],
            params={"analysis_depth": "comprehensive"}
        )

    @pytest.mark.asyncio
    async def test_basic_functionality(self, agent, mock_task_input, 
                                     mock_system_failure_case, mock_audit_report):
        """测试基本的系统诊断功能"""
        # 设置mock
        agent.get_artifacts = AsyncMock(return_value={
            "system_failure_case": mock_system_failure_case,
            "audit_report": mock_audit_report
        })
        
        # 模拟AI客户端返回
        mock_ai_client = AsyncMock()
        mock_ai_response = {
            "content": json.dumps({
                "evolution_proposal_id": "EVO-SYS-20250707-001",
                "failure_analysis": {
                    "case_study_id": "FAILURE-20250707-001",
                    "root_cause_diagnosis": {
                        "summary": "AGENT_3 prompt lacks sufficient output format constraints",
                        "primary_culprit": {
                            "agent_id": "AGENT_3",
                            "responsibility_share": "75%",
                            "specific_prompt_flaw": "Insufficient action-title validation rules"
                        }
                    }
                },
                "corrective_action_plan": {
                    "hypothesis": "Strengthening AGENT_3 format constraints will resolve violations",
                    "proposed_modifications": [
                        {
                            "target_agent_id": "AGENT_3",
                            "new_prompt_version_id": "v4.2.0",
                            "change_summary": "Added strict action-title validation",
                            "full_new_prompt": "Enhanced prompt with validation rules..."
                        }
                    ]
                },
                "validation_summary": {
                    "experiment_result": "SUCCESS",
                    "net_impact_assessment": "High positive impact with minimal side effects",
                    "recommendation": "APPROVE_AND_DEPLOY_ALL_PROPOSED_MODIFICATIONS"
                }
            })
        }
        mock_ai_client.generate_completion = AsyncMock(return_value=mock_ai_response)
        agent.ai_client_factory.get_client = AsyncMock(return_value=mock_ai_client)
        
        # 执行测试
        result = await agent.process_task(mock_task_input)
        
        # 验证结果
        assert isinstance(result, TaskOutput)
        assert result.schema_id == "EvolutionProposal_v1.0"
        
        payload = result.payload
        assert "evolution_proposal_id" in payload
        assert "failure_analysis" in payload
        assert "corrective_action_plan" in payload
        assert "validation_summary" in payload
        assert "metadata" in payload
        
        # 验证metadata
        metadata = payload["metadata"]
        assert metadata["created_by"] == "AGENT_5"
        assert metadata["version"] == "1.0"
        assert "diagnosis_timestamp" in metadata

    @pytest.mark.asyncio
    async def test_ai_client_failure_fallback(self, agent, mock_task_input,
                                             mock_system_failure_case, mock_audit_report):
        """测试AI客户端失败时的模板降级"""
        # 设置mock
        agent.get_artifacts = AsyncMock(return_value={
            "system_failure_case": mock_system_failure_case,
            "audit_report": mock_audit_report
        })
        
        # 模拟AI客户端失败
        agent.ai_client_factory.get_client = AsyncMock(return_value=None)
        
        # 执行测试
        result = await agent.process_task(mock_task_input)
        
        # 验证降级到模板
        assert isinstance(result, TaskOutput)
        assert result.schema_id == "EvolutionProposal_v1.0"
        
        payload = result.payload
        metadata = payload["metadata"]
        assert metadata["processing_notes"] == "Template-based diagnosis due to AI processing failure"
        assert metadata["diagnosis_confidence"] == 0.65  # 模板降级的置信度

    @pytest.mark.asyncio
    async def test_input_validation_missing_failure_case(self, agent):
        """测试缺少系统故障案例时的验证"""
        task_input = TaskInput(
            artifacts=[ArtifactReference(name="audit_report", source_task_id=401)],
            params={}
        )
        
        agent.get_artifacts = AsyncMock(return_value={
            "audit_report": {"audit_passed": False}
        })
        
        with pytest.raises(ValueError, match="System failure case artifact is required"):
            await agent.process_task(task_input)

    @pytest.mark.asyncio
    async def test_input_validation_invalid_failure_case(self, agent):
        """测试无效故障案例结构的验证"""
        task_input = TaskInput(
            artifacts=[ArtifactReference(name="system_failure_case", source_task_id=501)],
            params={}
        )
        
        agent.get_artifacts = AsyncMock(return_value={
            "system_failure_case": {"case_id": "test"}  # 缺少failure_instances
        })
        
        with pytest.raises(ValueError, match="must contain 'failure_instances' array"):
            await agent.process_task(task_input)

    def test_failure_pattern_analysis(self, agent):
        """测试失败模式分析逻辑"""
        failure_instances = [
            {"error_type": "schema_validation_error", "agent_involved": "AGENT_3"},
            {"error_type": "format_consistency_error", "agent_involved": "AGENT_3"},
            {"error_type": "theme_selection_error", "agent_involved": "AGENT_2"},
            {"error_type": "validation_rule_error", "agent_involved": "AGENT_4"}
        ]
        
        agents_with_issues = agent._analyze_failure_patterns(failure_instances)
        
        # AGENT_3应该排在最前面（2个问题）
        assert "AGENT_3" in agents_with_issues
        assert agents_with_issues.index("AGENT_3") == 0

    def test_basic_prompt_improvement_generation(self, agent):
        """测试基础提示词改进生成"""
        for agent_id in ["AGENT_1", "AGENT_2", "AGENT_3", "AGENT_4"]:
            improvement = agent._generate_basic_prompt_improvement(agent_id)
            assert len(improvement) > 50  # 确保生成了有意义的改进
            assert "约束" in improvement or "constraint" in improvement.lower()

    @pytest.mark.asyncio
    async def test_ai_response_parsing_with_markdown(self, agent):
        """测试AI响应解析（包含markdown格式）"""
        markdown_content = """```json
        {
            "evolution_proposal_id": "EVO-SYS-20250707-001",
            "failure_analysis": {
                "case_study_id": "test",
                "root_cause_diagnosis": {
                    "summary": "Test analysis",
                    "primary_culprit": {
                        "agent_id": "AGENT_3",
                        "responsibility_share": "80%", 
                        "specific_prompt_flaw": "Test flaw"
                    }
                }
            },
            "corrective_action_plan": {
                "hypothesis": "Test hypothesis",
                "proposed_modifications": []
            },
            "validation_summary": {
                "experiment_result": "SUCCESS",
                "net_impact_assessment": "Test assessment",
                "recommendation": "APPROVE_AND_DEPLOY_ALL_PROPOSED_MODIFICATIONS"
            }
        }
        ```"""
        
        result = agent._parse_ai_response(markdown_content)
        
        assert result is not None
        assert result["evolution_proposal_id"] == "EVO-SYS-20250707-001"
        assert "metadata" in result
        assert result["metadata"]["created_by"] == "AGENT_5"

    def test_ai_response_parsing_invalid_json(self, agent):
        """测试无效JSON的处理"""
        invalid_content = "{ invalid json content }"
        
        result = agent._parse_ai_response(invalid_content)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_template_proposal_generation(self, agent, mock_system_failure_case, mock_audit_report):
        """测试模板提案生成的完整性"""
        result = agent._generate_template_proposal(mock_system_failure_case, mock_audit_report)
        
        # 验证必需字段
        assert "evolution_proposal_id" in result
        assert "failure_analysis" in result
        assert "corrective_action_plan" in result
        assert "validation_summary" in result
        assert "metadata" in result
        
        # 验证failure_analysis结构
        failure_analysis = result["failure_analysis"]
        assert "case_study_id" in failure_analysis
        assert "root_cause_diagnosis" in failure_analysis
        
        # 验证corrective_action_plan结构
        action_plan = result["corrective_action_plan"]
        assert "hypothesis" in action_plan
        assert "proposed_modifications" in action_plan
        assert len(action_plan["proposed_modifications"]) > 0
        
        # 验证每个修改提案的结构
        modification = action_plan["proposed_modifications"][0]
        assert "target_agent_id" in modification
        assert "new_prompt_version_id" in modification
        assert "change_summary" in modification
        assert "full_new_prompt" in modification

    @pytest.mark.asyncio
    async def test_diagnostic_context_building(self, agent, mock_system_failure_case, mock_audit_report):
        """测试诊断上下文构建"""
        context = agent._build_diagnostic_context(mock_system_failure_case, mock_audit_report)
        
        assert "系统故障案例数据" in context
        assert "审计报告数据" in context
        assert "EvolutionProposal_v1.0" in context
        assert "failure_instances" in context

    def test_diagnostician_prompt_completeness(self, agent):
        """测试诊断工程师提示词的完整性"""
        prompt = agent._build_diagnostician_prompt()
        
        # 验证包含关键概念
        assert "根本原因分析" in prompt
        assert "诊断漏斗" in prompt
        assert "全链路质询" in prompt
        assert "AGENT_1" in prompt and "AGENT_4" in prompt
        assert "JSON格式" in prompt


# 增强测试用例 - 基于zen-mcp发现的模式
class TestEvolutionEngineerEnhanced:
    """增强测试用例，覆盖更多边界条件"""

    @pytest.mark.asyncio
    async def test_complex_multi_agent_failure_scenario(self, agent):
        """测试复杂的多Agent失败场景"""
        complex_failure_case = {
            "case_id": "COMPLEX-FAILURE-001",
            "failure_type": "CASCADING_FAILURE",
            "severity": "CRITICAL",
            "failure_instances": [
                {"error_type": "purpose_clarity_error", "agent_involved": "AGENT_1"},
                {"error_type": "theme_feasibility_error", "agent_involved": "AGENT_2"},
                {"error_type": "format_validation_error", "agent_involved": "AGENT_3"},
                {"error_type": "audit_rule_conflict", "agent_involved": "AGENT_4"}
            ]
        }
        
        task_input = TaskInput(
            artifacts=[ArtifactReference(name="system_failure_case", source_task_id=501)],
            params={}
        )
        
        agent.get_artifacts = AsyncMock(return_value={
            "system_failure_case": complex_failure_case
        })
        
        # 模拟AI客户端失败，使用模板
        agent.ai_client_factory.get_client = AsyncMock(return_value=None)
        
        result = await agent.process_task(task_input)
        
        # 验证能够处理复杂场景
        assert isinstance(result, TaskOutput)
        payload = result.payload
        
        # 应该识别出主要责任方
        primary_culprit = payload["failure_analysis"]["root_cause_diagnosis"]["primary_culprit"]
        assert primary_culprit["agent_id"] in ["AGENT_1", "AGENT_2", "AGENT_3", "AGENT_4"]

    @pytest.mark.asyncio
    async def test_audit_report_integration(self, agent, mock_system_failure_case):
        """测试与AGENT_4审计报告的集成"""
        detailed_audit_report = {
            "audit_passed": False,
            "summary": {"overall_score": 45, "errors_found": 5, "warnings_found": 3},
            "errors": [
                {
                    "protocol_id": "A-PYR-01",
                    "type": "VIOLATION_OF_ACTION_TITLE", 
                    "severity": "CRITICAL"
                },
                {
                    "protocol_id": "A-NARR-02",
                    "type": "LOGICAL_FLOW_DISRUPTION",
                    "severity": "HIGH"
                }
            ],
            "recommendations": ["Strengthen title validation", "Improve flow consistency"]
        }
        
        task_input = TaskInput(
            artifacts=[
                ArtifactReference(name="system_failure_case", source_task_id=501),
                ArtifactReference(name="audit_report", source_task_id=401)
            ],
            params={}
        )
        
        agent.get_artifacts = AsyncMock(return_value={
            "system_failure_case": mock_system_failure_case,
            "audit_report": detailed_audit_report
        })
        
        agent.ai_client_factory.get_client = AsyncMock(return_value=None)
        
        result = await agent.process_task(task_input)
        
        # 验证审计报告被正确集成
        assert isinstance(result, TaskOutput)
        # 审计失败应该触发系统诊断
        payload = result.payload
        assert "failure_analysis" in payload

    def test_proposal_id_format_validation(self, agent, mock_system_failure_case, mock_audit_report):
        """测试提案ID格式的正确性"""
        result = agent._generate_template_proposal(mock_system_failure_case, mock_audit_report)
        
        proposal_id = result["evolution_proposal_id"]
        # 验证格式: EVO-SYS-YYYYMMDD-NNN
        import re
        pattern = r"^EVO-SYS-\d{8}-\d{3}$"
        assert re.match(pattern, proposal_id), f"Invalid proposal ID format: {proposal_id}"

    @pytest.mark.asyncio
    async def test_schema_validation_critical_fix(self, agent, mock_system_failure_case, mock_audit_report):
        """测试CRITICAL修复：运行时Schema验证"""
        # 创建符合Schema的提案
        valid_proposal = {
            "evolution_proposal_id": "EVO-SYS-20250707-001",
            "failure_analysis": {
                "case_study_id": "TEST-001", 
                "root_cause_diagnosis": {
                    "summary": "Test analysis for schema validation with sufficient length",
                    "primary_culprit": {
                        "agent_id": "AGENT_3",
                        "responsibility_share": "75%",
                        "specific_prompt_flaw": "Insufficient validation rules for test case"
                    }
                }
            },
            "corrective_action_plan": {
                "hypothesis": "Schema validation will prevent issues",
                "proposed_modifications": [
                    {
                        "target_agent_id": "AGENT_3",
                        "new_prompt_version_id": "v2.1.0", 
                        "change_summary": "Enhanced validation for test",
                        "full_new_prompt": "Complete prompt text with sufficient length for schema validation requirements and proper formatting"
                    }
                ]
            },
            "validation_summary": {
                "experiment_result": "SUCCESS",
                "net_impact_assessment": "Positive impact expected from enhanced validation procedures",
                "recommendation": "APPROVE_AND_DEPLOY_ALL_PROPOSED_MODIFICATIONS"
            },
            "metadata": {
                "created_by": "AGENT_5",
                "version": "1.0",
                "diagnosis_timestamp": "2025-07-07T21:00:00Z"
            }
        }
        
        # 应该成功验证
        await agent._validate_evolution_proposal_schema(valid_proposal)
        
        # 测试无效的提案（缺少必需字段）
        invalid_proposal = {
            "evolution_proposal_id": "EVO-SYS-20250707-001"
            # 缺少其他必需字段
        }
        
        with pytest.raises(ValueError, match="does not conform to Schema"):
            await agent._validate_evolution_proposal_schema(invalid_proposal)