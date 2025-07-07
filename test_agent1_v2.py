#!/usr/bin/env python3
"""
测试AGENT_1新版本提示词（v2.0 - 创意总监/首席故事官）
"""

import asyncio
import sys
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


async def verify_new_prompt():
    """验证新提示词是否正确保存"""
    print("🔍 验证新提示词配置...")
    
    try:
        await db_manager.connect()
        
        # 查询当前活跃的AGENT_1提示词
        query = """
            SELECT version, is_active, 
                   LENGTH(prompt_text) as prompt_length,
                   LEFT(prompt_text, 200) as prompt_preview
            FROM agent_prompts 
            WHERE agent_id = $1 AND is_active = true
        """
        
        result = await db_manager.fetch_one(query, "AGENT_1")
        
        if result:
            print(f"✅ 当前活跃版本: {result['version']}")
            print(f"   提示词长度: {result['prompt_length']} 字符")
            print(f"   开头预览: {result['prompt_preview']}...")
            
            # 检查是否包含新版本的关键特征
            full_query = "SELECT prompt_text FROM agent_prompts WHERE agent_id = $1 AND is_active = true"
            full_result = await db_manager.fetch_one(full_query, "AGENT_1")
            prompt_text = full_result['prompt_text']
            
            key_features = [
                ("三幕剧思考仪式", "三幕剧"),
                ("同理心潜航", "Empathy Deep Dive"),
                ("框架的角斗场", "Framework Arena"),
                ("7种叙事框架", "对比思维模型")
            ]
            
            print("\n✨ 新版本特性验证：")
            for feature_name, search_text in key_features:
                if search_text in prompt_text:
                    print(f"   ✅ {feature_name}")
                else:
                    print(f"   ❌ {feature_name} (未找到)")
        else:
            print("❌ 未找到活跃的AGENT_1提示词")
            
        await db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


async def test_with_new_prompt():
    """使用新提示词测试AGENT_1"""
    print("\n🎨 测试新版提示词效果...")
    
    try:
        await db_manager.connect()
        
        # 创建测试输入 - 一个需要深度思考的案例
        test_cases = [
            {
                "name": "电商平台会员体系",
                "input": "我需要为一个新的电商平台设计会员体系介绍页面。平台有三个会员等级：普通会员（免费）、黄金会员（99元/年）、钻石会员（299元/年）。不同等级享受不同的优惠折扣、积分倍率和专属服务。目标用户是25-40岁的都市白领，他们追求性价比但也注重品质体验。"
            },
            {
                "name": "在线教育课程",
                "input": "设计一个Python编程入门课程的介绍页面。课程分为基础篇、进阶篇和实战篇，总共60课时。目标学员是零基础但想转行做程序员的职场人士。需要突出课程的系统性、实用性，以及我们提供的就业辅导服务。"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n📝 测试案例: {test_case['name']}")
            print(f"   输入长度: {len(test_case['input'])} 字符")
            
            # 创建Agent并处理
            agent = CreativeDirectorAgent()
            
            test_input = TaskInput(
                artifacts=[],
                params={
                    "chat_input": test_case["input"],
                    "session_id": f"test_v2_{test_case['name']}"
                }
            )
            
            # 获取当前提示词（验证是否使用v2.0）
            current_prompt = await agent.get_agent_prompt()
            if current_prompt and "三幕剧" in current_prompt:
                print("   ✅ 确认使用v2.0提示词")
            else:
                print("   ⚠️  可能未使用新版本提示词")
            
            # 处理任务
            result = await agent.process_task(test_input)
            
            print(f"   ✅ 处理成功")
            print(f"   输出Schema: {result.schema_id}")
            
            # 分析输出内容
            payload = result.payload
            print("\n   📊 输出分析：")
            
            # 检查是否有更深入的洞察
            if "project_overview" in payload:
                themes = payload["project_overview"].get("key_themes", [])
                print(f"      关键主题: {themes}")
            
            if "creative_strategy" in payload:
                tone = payload["creative_strategy"].get("tone_of_voice", "")
                approach = payload["creative_strategy"].get("creative_approach", "")
                print(f"      语气语调: {tone}")
                print(f"      创意方法: {approach[:100]}...")
            
            if "target_audience" in payload:
                audience = payload["target_audience"].get("primary_audience", "")
                print(f"      目标受众: {audience}")
        
        await db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def compare_versions():
    """对比v1.0和v2.0的输出差异"""
    print("\n📊 版本对比分析...")
    
    print("v1.0 特点：")
    print("- 简洁直接的指令")
    print("- 模板化的输出结构")
    print("- 快速响应")
    
    print("\nv2.0 特点：")
    print("- 三幕剧深度思考流程")
    print("- 7种叙事框架选择")
    print("- 更深入的用户同理心")
    print("- 框架竞争和选择机制")
    print("- 情感驱动的创意策略")
    
    print("\n💡 使用建议：")
    print("- 简单需求：可继续使用模板化实现（快速）")
    print("- 复杂需求：调用AI模型使用v2.0提示词（深度）")
    print("- 生产环境：建议先在测试环境验证v2.0效果")


async def main():
    """运行所有测试"""
    print("🚀 AGENT_1 v2.0 提示词验证测试")
    print("=" * 60)
    
    # 1. 验证新提示词
    success = await verify_new_prompt()
    if not success:
        print("❌ 提示词验证失败，退出测试")
        return
    
    # 2. 测试新提示词效果
    await test_with_new_prompt()
    
    # 3. 版本对比
    await compare_versions()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("\n📌 后续步骤：")
    print("1. 集成真实的AI模型调用（OpenAI/Anthropic）")
    print("2. 在测试环境中验证v2.0提示词的实际效果")
    print("3. 收集用户反馈并持续优化")
    print("4. 考虑为其他Agent升级提示词")


if __name__ == "__main__":
    asyncio.run(main())