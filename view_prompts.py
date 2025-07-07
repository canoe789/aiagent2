#!/usr/bin/env python3
"""
查看所有Agent的提示词配置
"""

import asyncio
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, '.')

from database.connection import db_manager


async def view_all_prompts():
    """查看数据库中所有Agent的提示词"""
    try:
        await db_manager.connect()
        
        # 查询所有agent prompts
        query = """
            SELECT agent_id, version, is_active, prompt_text, created_at
            FROM agent_prompts
            ORDER BY agent_id, version DESC
        """
        
        results = await db_manager.fetch_all(query)
        
        print("=" * 80)
        print("📋 Project HELIX - Agent提示词配置")
        print("=" * 80)
        
        current_agent = None
        for row in results:
            if row['agent_id'] != current_agent:
                print(f"\n🤖 {row['agent_id']}")
                print("-" * 60)
                current_agent = row['agent_id']
            
            status = "✅ ACTIVE" if row['is_active'] else "⚪ INACTIVE"
            print(f"\nVersion: {row['version']} [{status}]")
            print(f"Created: {row['created_at']}")
            print(f"Prompt:")
            print("-" * 40)
            # 格式化显示prompt文本
            prompt_lines = row['prompt_text'].split('\n')
            for line in prompt_lines:
                print(f"  {line}")
            print("-" * 40)
        
        # 检查编排器配置
        print("\n\n🎯 Orchestrator Configuration")
        print("=" * 80)
        
        # 编排器不在agent_prompts表中，让我们查看其配置
        print("Note: 编排器(Orchestrator)不使用提示词，而是通过以下机制运行：")
        print("1. 轮询数据库中的新作业和待处理任务")
        print("2. 根据workflows.json定义的执行顺序分配任务")
        print("3. 监控任务状态并推进工作流")
        
        await db_manager.disconnect()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


async def check_default_prompts():
    """检查代码中定义的默认提示词"""
    print("\n\n💡 代码中的默认提示词（当数据库无配置时使用）")
    print("=" * 80)
    
    # 检查各个Agent的默认提示词
    agents = [
        ("AGENT_1", "agents/creative_director.py"),
        ("AGENT_2", "agents/visual_director.py")
    ]
    
    for agent_id, file_path in agents:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 查找_get_default_prompt方法
            start = content.find('def _get_default_prompt(self)')
            if start != -1:
                # 找到return语句
                start = content.find('return """', start)
                if start != -1:
                    start += len('return """')
                    end = content.find('"""', start)
                    if end != -1:
                        default_prompt = content[start:end].strip()
                        print(f"\n{agent_id} 默认提示词:")
                        print("-" * 40)
                        print(default_prompt)
                        print("-" * 40)
        except Exception as e:
            print(f"无法读取 {agent_id} 的默认提示词: {e}")


if __name__ == "__main__":
    asyncio.run(view_all_prompts())
    asyncio.run(check_default_prompts())