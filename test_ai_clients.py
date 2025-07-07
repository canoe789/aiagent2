#!/usr/bin/env python3
"""
测试AI客户端集成
验证DeepSeek和Gemini API连接
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, '.')

from ai_clients.client_factory import AIClientFactory, ai_client_manager


async def test_individual_clients():
    """测试各个AI客户端"""
    print("🧪 测试AI客户端连接...")
    
    # 测试DeepSeek
    print("\n🔍 测试DeepSeek客户端:")
    try:
        deepseek_client = AIClientFactory.create_client("deepseek")
        is_valid = await deepseek_client.validate_api_key()
        
        if is_valid:
            print("✅ DeepSeek API密钥有效")
            
            # 测试生成
            response = await deepseek_client.generate_response(
                system_prompt="你是一位创意总监。用简洁的中文回答。",
                user_input="为一个现代咖啡店网站设计一个简短的创意概念",
                temperature=0.7,
                max_tokens=200
            )
            
            print(f"✅ DeepSeek生成成功")
            print(f"   内容长度: {len(response['content'])} 字符")
            print(f"   令牌使用: {response['usage']}")
            print(f"   内容预览: {response['content'][:100]}...")
            
        else:
            print("❌ DeepSeek API密钥无效")
            
    except Exception as e:
        print(f"❌ DeepSeek测试失败: {e}")
    
    # 测试Gemini
    print("\n🔍 测试Gemini客户端:")
    try:
        gemini_client = AIClientFactory.create_client("gemini")
        is_valid = await gemini_client.validate_api_key()
        
        if is_valid:
            print("✅ Gemini API密钥有效")
            
            # 测试生成
            response = await gemini_client.generate_response(
                system_prompt="You are a visual director. Respond concisely in English.",
                user_input="Create a visual concept for a modern coffee shop website",
                temperature=0.7,
                max_tokens=200
            )
            
            print(f"✅ Gemini生成成功")
            print(f"   内容长度: {len(response['content'])} 字符")
            print(f"   令牌使用: {response['usage']}")
            print(f"   内容预览: {response['content'][:100]}...")
            
        else:
            print("❌ Gemini API密钥无效")
            
    except Exception as e:
        print(f"❌ Gemini测试失败: {e}")


async def test_factory_features():
    """测试工厂类功能"""
    print("\n🏭 测试AI客户端工厂功能...")
    
    # 测试provider信息
    providers = AIClientFactory.get_available_providers()
    print("\n📋 可用提供商:")
    for provider, info in providers.items():
        status = "✅ 已配置" if info["api_key_configured"] else "❌ 未配置"
        print(f"   {provider}: {info['description']} [{status}]")
        print(f"     默认模型: {info['default_model']}")
        print(f"     API密钥环境变量: {info['api_key_env_var']}")
    
    # 测试默认客户端
    print("\n🎯 测试默认客户端:")
    try:
        default_client = AIClientFactory.create_client()
        print(f"✅ 默认客户端创建成功 ({default_client.get_provider_name()})")
    except Exception as e:
        print(f"❌ 默认客户端创建失败: {e}")
    
    # 测试客户端管理器
    print("\n👔 测试客户端管理器:")
    try:
        manager = ai_client_manager
        client1 = manager.get_client("deepseek")
        client2 = manager.get_client("deepseek")  # 应该返回缓存的实例
        
        if client1 is client2:
            print("✅ 客户端缓存工作正常")
        else:
            print("⚠️ 客户端缓存可能有问题")
            
    except Exception as e:
        print(f"❌ 客户端管理器测试失败: {e}")


async def test_agent_integration():
    """测试与Agent系统的集成"""
    print("\n🤖 测试与Agent系统集成...")
    
    try:
        # 模拟AGENT_1使用AI客户端
        print("模拟AGENT_1（创意总监）使用AI生成创意蓝图...")
        
        client = AIClientFactory.create_client()
        
        # 获取AGENT_1的v2.0提示词（模拟）
        system_prompt = """你是一位顶级的创意总监，同时也是一位首席故事官。
你需要将用户需求转化为结构化的创意蓝图。
请用JSON格式回应，包含project_overview、objectives、target_audience、creative_strategy等字段。"""
        
        user_input = "我需要为一个新的在线教育平台设计主页，主要面向想学习编程的职场人士。"
        
        response = await client.generate_response(
            system_prompt=system_prompt,
            user_input=user_input,
            temperature=0.7,
            max_tokens=1000
        )
        
        print("✅ Agent-AI集成测试成功")
        print(f"   生成内容长度: {len(response['content'])} 字符")
        print(f"   使用模型: {response['model']} ({response['provider']})")
        
        # 检查是否返回了结构化内容
        content = response['content']
        if any(keyword in content.lower() for keyword in ['json', 'project', 'target', 'creative']):
            print("✅ 内容包含预期的结构化元素")
        else:
            print("⚠️ 内容可能不够结构化")
            
    except Exception as e:
        print(f"❌ Agent集成测试失败: {e}")


async def test_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理...")
    
    # 测试无效provider
    try:
        AIClientFactory.create_client("invalid_provider")
        print("❌ 应该抛出错误但没有")
    except Exception as e:
        print(f"✅ 正确处理了无效provider: {type(e).__name__}")
    
    # 测试无效API密钥
    try:
        from ai_clients.deepseek_client import DeepSeekClient
        invalid_client = DeepSeekClient("invalid_api_key")
        await invalid_client.validate_api_key()
        print("⚠️ 无效API密钥验证可能有问题")
    except Exception:
        print("✅ 正确处理了无效API密钥")


async def validate_all_providers():
    """验证所有提供商"""
    print("\n🔍 验证所有配置的提供商...")
    
    try:
        validation_results = await AIClientFactory.validate_all_providers()
        
        for provider, is_valid in validation_results.items():
            status = "✅ 有效" if is_valid else "❌ 无效"
            print(f"   {provider}: {status}")
            
        valid_count = sum(validation_results.values())
        total_count = len(validation_results)
        
        print(f"\n📊 验证摘要: {valid_count}/{total_count} 个提供商有效")
        
        return valid_count > 0
        
    except Exception as e:
        print(f"❌ 提供商验证失败: {e}")
        return False


async def main():
    """运行所有测试"""
    print("🚀 Project HELIX - AI客户端集成测试")
    print("=" * 60)
    
    # 检查环境变量
    print("🔧 检查环境配置...")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    print(f"   DeepSeek API密钥: {'✅ 已配置' if deepseek_key and deepseek_key != 'your_deepseek_api_key_here' else '❌ 未配置'}")
    print(f"   Gemini API密钥: {'✅ 已配置' if gemini_key and gemini_key != 'your_gemini_api_key_here' else '❌ 未配置'}")
    
    # 运行测试
    await validate_all_providers()
    await test_factory_features()
    await test_individual_clients()
    await test_agent_integration()
    await test_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ AI客户端集成测试完成！")
    print("\n📌 下一步:")
    print("1. 更新AGENT_1使用真实AI模型")
    print("2. 更新AGENT_2使用真实AI模型")
    print("3. 测试完整的AI驱动工作流")


if __name__ == "__main__":
    asyncio.run(main())