#!/usr/bin/env python3
"""
Project HELIX v2.0 - AGENT_1 (Creative Director) 验证测试
完整的端到端工作流验证
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
from database.models import JobCreate, TaskInput
from agents.creative_director import CreativeDirectorAgent
from api.main import app
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
        result = await db_manager.fetch_one("SELECT COUNT(*) as count FROM agent_prompts WHERE agent_id = $1", "AGENT_1")
        print(f"✅ 数据库连接成功，AGENT_1 prompts: {result['count']}")
        
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

async def test_agent1_direct_call():
    """直接测试AGENT_1的业务逻辑"""
    print("🤖 直接测试AGENT_1...")
    
    try:
        agent = CreativeDirectorAgent()
        
        # 创建测试输入
        test_input = TaskInput(
            artifacts=[],
            params={
                "chat_input": "我想创建一个现代化的咖啡店网站，要体现温馨、专业和可持续发展的理念",
                "session_id": "test_session_001"
            }
        )
        
        print(f"📝 输入内容: {test_input.params['chat_input']}")
        
        # 执行Agent处理
        result = await agent.process_task(test_input)
        
        print(f"✅ AGENT_1处理成功")
        print(f"   Schema ID: {result.schema_id}")
        print(f"   输出字段: {list(result.payload.keys())}")
        
        # 验证输出结构
        required_fields = ["project_overview", "objectives", "target_audience", "creative_strategy", "content_requirements", "metadata"]
        missing_fields = [field for field in required_fields if field not in result.payload]
        
        if missing_fields:
            print(f"⚠️  缺少必需字段: {missing_fields}")
        else:
            print("✅ 输出结构验证通过")
            
        # 显示部分输出内容
        if "project_overview" in result.payload:
            overview = result.payload["project_overview"]
            print(f"   项目标题: {overview.get('title', 'N/A')}")
            print(f"   项目类型: {overview.get('type', 'N/A')}")
            print(f"   关键主题: {overview.get('key_themes', [])}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ AGENT_1测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_job_creation_workflow():
    """测试完整的作业创建 -> 任务分配工作流"""
    print("🔄 测试完整工作流...")
    
    try:
        # 1. 创建新作业
        job_data = {
            "initial_request": {
                "chat_input": "创建一个科技创业公司的官网，主要展示AI产品",
                "session_id": "test_workflow_001"
            }
        }
        
        import json
        
        job_id = await db_manager.fetch_one("""
            INSERT INTO jobs (status, initial_request, session_id) 
            VALUES ('PENDING', $1::jsonb, $2) 
            RETURNING id
        """, json.dumps(job_data["initial_request"]), job_data["initial_request"]["session_id"])
        
        print(f"✅ 作业创建成功，Job ID: {job_id['id']}")
        
        # 2. 创建AGENT_1任务
        task_id = await db_manager.fetch_one("""
            INSERT INTO tasks (job_id, agent_id, status, input_data) 
            VALUES ($1, $2, 'PENDING', $3::jsonb) 
            RETURNING id
        """, job_id['id'], "AGENT_1", json.dumps({
            "artifacts": [],
            "params": job_data["initial_request"]
        }))
        
        print(f"✅ 任务创建成功，Task ID: {task_id['id']}")
        
        # 3. 模拟Agent工作者获取任务
        pending_task = await db_manager.fetch_one("""
            SELECT id, job_id, agent_id, input_data 
            FROM tasks 
            WHERE id = $1 AND status = 'PENDING'
        """, task_id['id'])
        
        if pending_task:
            print(f"✅ 任务获取成功: {pending_task['agent_id']}")
            
            # 4. 执行AGENT_1处理
            agent = CreativeDirectorAgent()
            
            # 解析JSONB数据
            input_data = pending_task['input_data']
            if isinstance(input_data, str):
                input_data = json.loads(input_data)
                
            task_input = TaskInput(**input_data)
            
            result = await agent.process_task(task_input)
            
            # 5. 更新任务状态和输出
            await db_manager.execute("""
                UPDATE tasks 
                SET status = 'COMPLETED', 
                    output_data = $1::jsonb,
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """, json.dumps({
                "schema_id": result.schema_id,
                "payload": result.payload
            }), task_id['id'])
            
            print(f"✅ 任务完成并保存到数据库")
            
            # 6. 验证数据库中的结果
            completed_task = await db_manager.fetch_one("""
                SELECT output_data, status, completed_at 
                FROM tasks 
                WHERE id = $1
            """, task_id['id'])
            
            if completed_task and completed_task['status'] == 'COMPLETED':
                print(f"✅ 完整工作流验证成功")
                print(f"   任务状态: {completed_task['status']}")
                print(f"   完成时间: {completed_task['completed_at']}")
                return True
            else:
                print(f"❌ 任务状态验证失败")
                return False
        else:
            print(f"❌ 任务获取失败")
            return False
            
    except Exception as e:
        print(f"❌ 工作流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_schema_validation():
    """测试JSON Schema验证"""
    print("📋 测试Schema验证...")
    
    try:
        # 读取CreativeBrief schema
        with open("schemas/CreativeBrief_v1.0.json", "r") as f:
            schema = json.load(f)
        
        print(f"✅ Schema加载成功: {schema.get('title', 'Unknown')}")
        
        # 获取AGENT_1的实际输出进行验证
        agent = CreativeDirectorAgent()
        test_input = TaskInput(
            artifacts=[],
            params={
                "chat_input": "设计一个环保主题的电商网站",
                "session_id": "schema_test"
            }
        )
        
        result = await agent.process_task(test_input)
        
        # 基本结构验证（简化版，不使用jsonschema库）
        required_fields = schema.get("required", [])
        payload = result.payload
        
        missing_fields = [field for field in required_fields if field not in payload]
        
        if missing_fields:
            print(f"❌ Schema验证失败，缺少字段: {missing_fields}")
            return False
        else:
            print(f"✅ Schema基本结构验证通过")
            
            # 检查metadata字段
            if "metadata" in payload:
                metadata = payload["metadata"]
                if metadata.get("created_by") == "AGENT_1":
                    print(f"✅ Metadata验证通过")
                else:
                    print(f"⚠️  Metadata中created_by不正确")
            
            return True
            
    except Exception as e:
        print(f"❌ Schema验证失败: {e}")
        return False

async def main():
    """运行所有验证测试"""
    print("🚀 Project HELIX v2.0 - AGENT_1 完整验证")
    print("=" * 60)
    
    tests = [
        ("数据库连接", test_database_connectivity),
        ("AGENT_1直接调用", test_agent1_direct_call),
        ("完整工作流", test_job_creation_workflow),
        ("Schema验证", test_schema_validation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 执行测试: {test_name}")
        print("-" * 40)
        
        try:
            if test_name == "AGENT_1直接调用":
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
        print("🎉 AGENT_1验证完全成功！")
        print("✅ 可以继续实现AGENT_2")
    else:
        print("⚠️  发现问题，需要修复后再继续")
    
    # 清理数据库连接
    await db_manager.disconnect()
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)