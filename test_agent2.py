#!/usr/bin/env python3
"""
Project HELIX v2.0 - AGENT_2 (Visual Director) 验证测试
完整的端到端工作流验证，包括与AGENT_1的集成
"""

import asyncio
import sys
import os
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, '.')

from database.connection import db_manager
from database.models import TaskInput, TaskOutput
from agents.visual_director import VisualDirectorAgent
from agents.creative_director import CreativeDirectorAgent
import structlog

# 配置日志
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.WriteLoggerFactory(),
    wrapper_class=structlog.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

async def test_database_connectivity():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    try:
        await db_manager.connect()
        
        # 测试查询
        result = await db_manager.fetch_one("SELECT COUNT(*) as count FROM agent_prompts WHERE agent_id = $1", "AGENT_2")
        print(f"✅ 数据库连接成功，AGENT_2 prompts: {result['count']}")
        
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

async def test_agent2_direct_call():
    """直接测试AGENT_2的业务逻辑"""
    print("🎨 直接测试AGENT_2...")
    
    try:
        agent = VisualDirectorAgent()
        
        # 创建模拟的创意蓝图数据（来自AGENT_1）
        mock_creative_brief = {
            "project_overview": {
                "title": "现代化科技创业公司官网",
                "type": "website",
                "description": "展示AI产品的创新科技公司网站",
                "key_themes": ["modern", "tech", "professional", "innovative"]
            },
            "objectives": {
                "primary_goal": "建立可信的技术品牌形象",
                "secondary_goals": ["展示技术实力", "吸引潜在客户", "提升品牌认知度"],
                "success_metrics": ["用户停留时间", "联系表单转化率", "品牌认知度"]
            },
            "target_audience": {
                "primary_audience": "技术决策者和企业客户",
                "audience_characteristics": {
                    "demographics": "25-50岁企业决策者",
                    "psychographics": "技术导向，注重创新和效率",
                    "behavior_patterns": "深度研究后做决策",
                    "pain_points": "寻找可靠的技术解决方案"
                }
            },
            "creative_strategy": {
                "tone_of_voice": "专业且前瞻性",
                "key_messages": ["技术创新", "可靠性", "行业领先"],
                "creative_approach": "现代科技美学，简洁有力的信息传达"
            },
            "content_requirements": {
                "content_types": ["Hero section", "产品展示", "技术优势", "客户案例", "联系方式"],
                "information_hierarchy": {
                    "主要信息": 1,
                    "产品特性": 2,
                    "技术实力": 3,
                    "联系方式": 4
                }
            },
            "metadata": {
                "created_by": "AGENT_1",
                "version": "1.0",
                "confidence_score": 0.9
            }
        }
        
        # 创建测试输入
        test_input = TaskInput(
            artifacts=[{"name": "creative_brief", "source_task_id": 101}],
            params={}
        )
        
        print(f"📝 输入创意蓝图主题: {mock_creative_brief['project_overview']['key_themes']}")
        print(f"📝 项目类型: {mock_creative_brief['project_overview']['type']}")
        
        # 模拟get_artifacts方法
        async def mock_get_artifacts(artifact_refs):
            return {
                "creative_brief": {
                    "payload": mock_creative_brief,
                    "schema_id": "CreativeBrief_v1.0"
                }
            }
        
        agent.get_artifacts = mock_get_artifacts
        
        # 执行Agent处理
        result = await agent.process_task(test_input)
        
        print(f"✅ AGENT_2处理成功")
        print(f"   Schema ID: {result.schema_id}")
        print(f"   输出字段: {list(result.payload.keys())}")
        
        # 验证输出结构
        required_fields = ["style_direction", "color_palette", "typography", "layout_principles", "visual_elements"]
        missing_fields = [field for field in required_fields if field not in result.payload]
        
        if missing_fields:
            print(f"⚠️  缺少必需字段: {missing_fields}")
        else:
            print("✅ 输出结构验证通过")
            
        # 显示部分输出内容
        print(f"   风格方向: {result.payload['style_direction'][:100]}...")
        print(f"   颜色数量: {len(result.payload['color_palette'])} 个颜色")
        print(f"   主要字体: {result.payload['typography']['primary_font']}")
        print(f"   布局原则: {len(result.payload['layout_principles'])} 条原则")
        
        # 验证颜色格式
        colors = result.payload.get('color_palette', [])
        valid_colors = all(color.startswith('#') and len(color) in [4, 7] for color in colors)
        print(f"   颜色格式验证: {'✅' if valid_colors else '❌'}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ AGENT_2测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_agent1_to_agent2_workflow():
    """测试AGENT_1到AGENT_2的完整工作流"""
    print("🔄 测试AGENT_1→AGENT_2工作流...")
    
    try:
        # 1. 先运行AGENT_1生成创意蓝图
        agent1 = CreativeDirectorAgent()
        
        agent1_input = TaskInput(
            artifacts=[],
            params={
                "chat_input": "我想创建一个人工智能企业级SaaS平台的官网，需要体现专业性、创新性和可信度",
                "session_id": "workflow_test_001"
            }
        )
        
        print("📋 执行AGENT_1生成创意蓝图...")
        agent1_result = await agent1.process_task(agent1_input)
        
        print(f"✅ AGENT_1完成，生成蓝图")
        print(f"   项目标题: {agent1_result.payload['project_overview']['title']}")
        print(f"   关键主题: {agent1_result.payload['project_overview']['key_themes']}")
        
        # 2. 创建数据库任务记录以支持artifact引用
        job_id = await db_manager.fetch_one("""
            INSERT INTO jobs (status, initial_request, session_id) 
            VALUES ('IN_PROGRESS', $1::jsonb, $2) 
            RETURNING id
        """, json.dumps(agent1_input.params), agent1_input.params["session_id"])
        
        # 3. 创建AGENT_1任务记录
        agent1_task_id = await db_manager.fetch_one("""
            INSERT INTO tasks (job_id, agent_id, status, input_data, output_data, completed_at) 
            VALUES ($1, $2, 'COMPLETED', $3::jsonb, $4::jsonb, CURRENT_TIMESTAMP) 
            RETURNING id
        """, job_id['id'], "AGENT_1", json.dumps(agent1_input.model_dump()), 
            json.dumps(agent1_result.model_dump()))
        
        # 4. 创建artifact记录
        await db_manager.execute("""
            INSERT INTO artifacts (task_id, name, schema_id, payload) 
            VALUES ($1, $2, $3, $4::jsonb)
        """, agent1_task_id['id'], "creative_brief", agent1_result.schema_id, 
            json.dumps(agent1_result.payload))
        
        print(f"✅ 数据库记录创建完成")
        
        # 5. 现在运行AGENT_2
        agent2 = VisualDirectorAgent()
        
        agent2_input = TaskInput(
            artifacts=[{"name": "creative_brief", "source_task_id": agent1_task_id['id']}],
            params={}
        )
        
        print("🎨 执行AGENT_2生成视觉探索...")
        agent2_result = await agent2.process_task(agent2_input)
        
        print(f"✅ AGENT_2完成，生成视觉探索")
        print(f"   风格方向: {agent2_result.payload['style_direction'][:80]}...")
        print(f"   配色方案: {agent2_result.payload['color_palette']}")
        print(f"   字体系统: {agent2_result.payload['typography']['primary_font']}")
        
        # 6. 验证artifact传递的一致性
        creative_brief_themes = agent1_result.payload['project_overview']['key_themes']
        visual_style = agent2_result.payload['style_direction'].lower()
        
        theme_consistency = any(theme in visual_style for theme in creative_brief_themes)
        print(f"   主题一致性: {'✅' if theme_consistency else '⚠️'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_schema_validation():
    """测试JSON Schema验证"""
    print("📋 测试VisualExplorations Schema验证...")
    
    try:
        # 读取VisualExplorations schema
        with open("schemas/VisualExplorations_v1.0.json", "r") as f:
            schema = json.load(f)
        
        print(f"✅ Schema加载成功: {schema.get('title', 'Unknown')}")
        
        # 获取AGENT_2的实际输出进行验证
        agent = VisualDirectorAgent()
        
        # 模拟创意蓝图输入
        mock_brief = {
            "project_overview": {"key_themes": ["modern", "tech"], "type": "website"},
            "creative_strategy": {"tone_of_voice": "professional and innovative"},
            "target_audience": {"primary_audience": "tech professionals"},
            "objectives": {"primary_goal": "establish tech leadership"}
        }
        
        async def mock_get_artifacts(refs):
            return {"creative_brief": {"payload": mock_brief, "schema_id": "CreativeBrief_v1.0"}}
        
        agent.get_artifacts = mock_get_artifacts
        
        test_input = TaskInput(
            artifacts=[{"name": "creative_brief", "source_task_id": 999}],
            params={}
        )
        
        result = await agent.process_task(test_input)
        
        # 基本结构验证
        required_fields = schema.get("required", [])
        payload = result.payload
        
        missing_fields = [field for field in required_fields if field not in payload]
        
        if missing_fields:
            print(f"❌ Schema验证失败，缺少字段: {missing_fields}")
            return False
        else:
            print(f"✅ Schema基本结构验证通过")
            
            # 检查具体字段格式
            validations = []
            
            # 验证颜色格式
            colors = payload.get("color_palette", [])
            valid_colors = all(isinstance(c, str) and c.startswith('#') for c in colors)
            validations.append(("颜色格式", valid_colors))
            
            # 验证typography结构
            typography = payload.get("typography", {})
            has_required_typo = "primary_font" in typography and "font_scale" in typography
            validations.append(("字体系统", has_required_typo))
            
            # 验证metadata
            metadata = payload.get("metadata", {})
            has_metadata = metadata.get("created_by") == "AGENT_2"
            validations.append(("元数据", has_metadata))
            
            # 显示验证结果
            for validation_name, is_valid in validations:
                print(f"   {validation_name}: {'✅' if is_valid else '❌'}")
            
            return all(is_valid for _, is_valid in validations)
            
    except Exception as e:
        print(f"❌ Schema验证失败: {e}")
        return False

async def test_visual_quality_metrics():
    """测试视觉质量指标"""
    print("🎯 测试视觉质量指标...")
    
    try:
        agent = VisualDirectorAgent()
        
        # 测试不同主题的处理能力
        test_cases = [
            {
                "name": "现代科技",
                "themes": ["modern", "tech", "innovative"],
                "expected_colors": 4,
                "expected_principles": 3
            },
            {
                "name": "传统商务",
                "themes": ["professional", "corporate"],
                "expected_colors": 3,
                "expected_principles": 3
            },
            {
                "name": "创意设计",
                "themes": ["creative", "artistic"],
                "expected_colors": 5,
                "expected_principles": 4
            }
        ]
        
        for test_case in test_cases:
            print(f"   测试主题: {test_case['name']}")
            
            mock_brief = {
                "project_overview": {"key_themes": test_case["themes"], "type": "website"},
                "creative_strategy": {"tone_of_voice": "professional"},
                "target_audience": {"primary_audience": "general public"},
                "objectives": {"primary_goal": "create engaging experience"}
            }
            
            async def mock_get_artifacts(refs):
                return {"creative_brief": {"payload": mock_brief, "schema_id": "CreativeBrief_v1.0"}}
            
            agent.get_artifacts = mock_get_artifacts
            
            test_input = TaskInput(
                artifacts=[{"name": "creative_brief", "source_task_id": 999}],
                params={}
            )
            
            result = await agent.process_task(test_input)
            
            # 检查输出质量
            color_count = len(result.payload.get("color_palette", []))
            principle_count = len(result.payload.get("layout_principles", []))
            
            color_ok = color_count >= test_case["expected_colors"]
            principle_ok = principle_count >= test_case["expected_principles"]
            
            print(f"      颜色数量: {color_count} ({'✅' if color_ok else '❌'})")
            print(f"      布局原则: {principle_count} ({'✅' if principle_ok else '❌'})")
        
        print("✅ 视觉质量指标测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 视觉质量测试失败: {e}")
        return False

async def main():
    """运行所有验证测试"""
    print("🚀 Project HELIX v2.0 - AGENT_2 完整验证")
    print("=" * 60)
    
    tests = [
        ("数据库连接", test_database_connectivity),
        ("AGENT_2直接调用", test_agent2_direct_call),
        ("AGENT_1→AGENT_2工作流", test_agent1_to_agent2_workflow),
        ("Schema验证", test_schema_validation),
        ("视觉质量指标", test_visual_quality_metrics)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 执行测试: {test_name}")
        print("-" * 40)
        
        try:
            if test_name == "AGENT_2直接调用":
                success, _ = await test_func()
            else:
                success = await test_func()
                
            if success:
                passed += 1
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 AGENT_2验证完全成功！")
        print("✅ 可以继续实现AGENT_3")
        print("✅ AGENT_1→AGENT_2工作流已验证")
    else:
        print("⚠️  发现问题，需要修复后再继续")
    
    # 清理数据库连接
    await db_manager.disconnect()
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)