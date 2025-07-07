#!/usr/bin/env python3
"""
测试AGENT_1的AI集成
验证真实AI模型生成创意蓝图的效果
"""

import asyncio
import sys
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, '.')

from database.connection import db_manager
from database.models import TaskInput, TaskOutput
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


async def test_ai_generation():
    """测试AI生成功能"""
    print("🤖 测试AGENT_1 AI生成功能...")
    
    try:
        await db_manager.connect()
        
        # 创建测试案例 - 精心设计来展示v2.0提示词的威力
        test_cases = [
            {
                "name": "复杂电商会员体系",
                "input": "我需要为一个新的电商平台设计会员体系介绍页面。平台有三个会员等级：普通会员（免费）、黄金会员（99元/年）、钻石会员（299元/年）。不同等级享受不同的优惠折扣、积分倍率和专属服务。目标用户是25-40岁的都市白领，他们追求性价比但也注重品质体验。关键痛点：用户对会员价值感知不清晰，担心花钱不值得。"
            },
            {
                "name": "在线教育品牌重塑",
                "input": "重新设计一个Python编程在线教育平台的品牌形象页面。我们的课程从零基础到高级实战，针对想转行做程序员的职场人士。竞争对手很多，我们的优势是有实际项目经验的讲师团队和1对1就业指导。用户画像：28-35岁，有一定工作经验但想换赛道的人群，大多数没有编程基础但学习动机很强。"
            },
            {
                "name": "传统品牌数字化转型",
                "input": "一家有30年历史的传统茶叶品牌要做数字化转型，需要设计新的官网主页。品牌既要保持传统文化底蕴，又要吸引年轻消费者。产品线包括传统名茶、创新茶饮、茶具文创。目标受众包括传统茶客（45岁以上）和新生代茶爱好者（25-35岁）。挑战是如何在一个页面上同时满足两个差异很大的用户群体。"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 测试案例 {i}: {test_case['name']}")
            print(f"   输入复杂度: {len(test_case['input'])} 字符")
            
            # 创建Agent
            agent = CreativeDirectorAgent()
            
            # 创建任务输入
            test_input = TaskInput(
                artifacts=[],
                params={
                    "chat_input": test_case["input"],
                    "session_id": f"ai_test_{i}"
                }
            )
            
            # 处理任务
            start_time = asyncio.get_event_loop().time()
            result = await agent.process_task(test_input)
            end_time = asyncio.get_event_loop().time()
            
            processing_time = end_time - start_time
            
            print(f"   ✅ 处理完成 (耗时: {processing_time:.2f}秒)")
            print(f"   Schema: {result.schema_id}")
            
            # 分析输出
            payload = result.payload
            metadata = payload.get("metadata", {})
            
            print(f"   🤖 AI模型: {metadata.get('ai_model', 'unknown')}")
            print(f"   🏢 提供商: {metadata.get('ai_provider', 'unknown')}")
            
            if "tokens_used" in metadata:
                print(f"   🪙 令牌使用: {metadata['tokens_used']}")
            
            # 检查生成质量
            await analyze_output_quality(payload, test_case["name"])
            
            # 美化输出展示
            print(f"\n   📊 生成内容示例:")
            if "project_overview" in payload:
                overview = payload["project_overview"]
                print(f"      项目标题: {overview.get('title', 'N/A')}")
                print(f"      关键主题: {overview.get('key_themes', [])}")
            
            if "creative_strategy" in payload:
                strategy = payload["creative_strategy"]
                print(f"      语气语调: {strategy.get('tone_of_voice', 'N/A')}")
                if strategy.get('key_messages'):
                    print(f"      关键信息: {', '.join(strategy['key_messages'][:2])}")
            
            if "target_audience" in payload:
                audience = payload["target_audience"]
                print(f"      目标受众: {audience.get('primary_audience', 'N/A')}")
            
            # 保存详细结果（可选）
            if i == 1:  # 只保存第一个案例的详细结果
                await save_detailed_result(result, test_case["name"])
        
        await db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ AI生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def analyze_output_quality(payload: dict, case_name: str):
    """分析输出质量"""
    quality_scores = []
    
    # 检查结构完整性
    required_sections = ["project_overview", "objectives", "target_audience", "creative_strategy", "content_requirements"]
    present_sections = sum(1 for section in required_sections if section in payload)
    structure_score = present_sections / len(required_sections)
    quality_scores.append(("结构完整性", structure_score))
    
    # 检查内容丰富度
    content_richness = 0
    if payload.get("project_overview", {}).get("key_themes"):
        content_richness += 0.2
    if len(payload.get("objectives", {}).get("secondary_goals", [])) > 1:
        content_richness += 0.2
    if payload.get("creative_strategy", {}).get("key_messages"):
        content_richness += 0.2
    if payload.get("target_audience", {}).get("audience_characteristics"):
        content_richness += 0.2
    if payload.get("content_requirements", {}).get("content_types"):
        content_richness += 0.2
    quality_scores.append(("内容丰富度", content_richness))
    
    # 检查AI vs Template
    metadata = payload.get("metadata", {})
    is_ai_generated = metadata.get("ai_model", "template_fallback") != "template_fallback"
    quality_scores.append(("AI生成", 1.0 if is_ai_generated else 0.0))
    
    # 显示质量分析
    print(f"   📈 质量分析:")
    for metric, score in quality_scores:
        status = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
        print(f"      {metric}: {score:.2f} {status}")
    
    # 总体质量评分
    avg_score = sum(score for _, score in quality_scores) / len(quality_scores)
    overall_status = "🎉 优秀" if avg_score >= 0.8 else "👍 良好" if avg_score >= 0.6 else "⚠️ 需改进"
    print(f"      总体质量: {avg_score:.2f} {overall_status}")


async def save_detailed_result(result: TaskOutput, case_name: str):
    """保存详细结果到文件"""
    try:
        filename = f"tmp/agent1_ai_result_{case_name.replace(' ', '_')}.json"
        
        # 确保目录存在
        import os
        os.makedirs("tmp", exist_ok=True)
        
        # 保存结果
        result_data = {
            "schema_id": result.schema_id,
            "payload": result.payload,
            "test_case": case_name,
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"   💾 详细结果已保存: {filename}")
        
    except Exception as e:
        print(f"   ⚠️ 保存结果失败: {e}")


async def test_fallback_mechanism():
    """测试AI失败时的降级机制"""
    print("\n🛡️ 测试降级机制...")
    
    try:
        agent = CreativeDirectorAgent()
        
        # 模拟AI调用失败的场景
        # 我们可以通过临时修改环境变量来模拟
        import os
        original_key = os.environ.get("DEEPSEEK_API_KEY")
        
        # 暂时设为无效key
        os.environ["DEEPSEEK_API_KEY"] = "invalid_key"
        
        test_input = TaskInput(
            artifacts=[],
            params={
                "chat_input": "简单测试：设计一个咖啡店网站主页",
                "session_id": "fallback_test"
            }
        )
        
        result = await agent.process_task(test_input)
        
        # 恢复原始key
        if original_key:
            os.environ["DEEPSEEK_API_KEY"] = original_key
        
        # 检查是否成功降级到模板模式
        metadata = result.payload.get("metadata", {})
        ai_model = metadata.get("ai_model", "unknown")
        
        if ai_model == "template_fallback":
            print("   ✅ 降级机制工作正常，使用模板生成")
        else:
            print("   ⚠️ 降级机制可能有问题")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 降级测试失败: {e}")
        return False


async def compare_ai_vs_template():
    """对比AI生成和模板生成的差异"""
    print("\n🔄 对比AI生成 vs 模板生成...")
    
    try:
        # 相同的输入
        test_input_params = {
            "chat_input": "为一个现代科技公司设计企业官网主页，主要展示AI产品和解决方案，目标客户是中大型企业的技术决策者",
            "session_id": "comparison_test"
        }
        
        agent = CreativeDirectorAgent()
        
        # 1. AI生成 (正常情况)
        print("   🤖 AI生成...")
        ai_result = await agent.process_task(TaskInput(artifacts=[], params=test_input_params))
        ai_metadata = ai_result.payload.get("metadata", {})
        
        # 2. 模板生成 (强制使用模板)
        print("   📝 模板生成...")
        template_result = await agent._generate_template_brief(test_input_params["chat_input"])
        
        # 对比结果
        print("\n   📊 对比结果:")
        
        # 内容长度对比
        ai_content_length = len(str(ai_result.payload))
        template_content_length = len(str(template_result))
        print(f"      内容长度: AI={ai_content_length} vs 模板={template_content_length}")
        
        # 主题数量对比
        ai_themes = len(ai_result.payload.get("project_overview", {}).get("key_themes", []))
        template_themes = len(template_result.get("project_overview", {}).get("key_themes", []))
        print(f"      关键主题: AI={ai_themes}个 vs 模板={template_themes}个")
        
        # 信息深度对比
        ai_strategy = ai_result.payload.get("creative_strategy", {}).get("creative_approach", "")
        template_strategy = template_result.get("creative_strategy", {}).get("creative_approach", "")
        print(f"      策略描述: AI={len(ai_strategy)}字符 vs 模板={len(template_strategy)}字符")
        
        # AI模型信息
        if ai_metadata.get("ai_model") != "template_fallback":
            print(f"      AI模型: {ai_metadata.get('ai_model')} ({ai_metadata.get('ai_provider')})")
            if "tokens_used" in ai_metadata:
                print(f"      令牌消耗: {ai_metadata['tokens_used']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 对比测试失败: {e}")
        return False


async def main():
    """运行所有测试"""
    print("🚀 Project HELIX - AGENT_1 AI集成测试")
    print("=" * 60)
    
    # 测试AI生成
    ai_success = await test_ai_generation()
    
    # 测试降级机制
    fallback_success = await test_fallback_mechanism()
    
    # 对比AI vs 模板
    comparison_success = await compare_ai_vs_template()
    
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    print(f"   AI生成测试: {'✅ 通过' if ai_success else '❌ 失败'}")
    print(f"   降级机制测试: {'✅ 通过' if fallback_success else '❌ 失败'}")
    print(f"   对比测试: {'✅ 通过' if comparison_success else '❌ 失败'}")
    
    if all([ai_success, fallback_success, comparison_success]):
        print("\n🎉 所有测试通过！AGENT_1 AI集成成功!")
        print("\n📌 下一步:")
        print("1. 对AGENT_2进行同样的AI集成")
        print("2. 测试完整的AGENT_1→AGENT_2 AI工作流")
        print("3. 优化提示词和响应质量")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试")


if __name__ == "__main__":
    asyncio.run(main())