#!/usr/bin/env python3
"""
HELIX 脏数据清理工具
安全地清理指定Job的所有相关数据，恢复系统一致性
"""

import asyncio
import asyncpg
import sys
import os
from typing import Optional

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'helix'),
    'user': os.getenv('POSTGRES_USER', 'helix_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
}

async def cleanup_job_data(job_id: int, dry_run: bool = True) -> bool:
    """
    清理指定Job的所有相关数据
    
    Args:
        job_id: 要清理的Job ID
        dry_run: 是否为试运行模式（只显示将要删除的数据，不实际删除）
    
    Returns:
        bool: 清理是否成功
    """
    try:
        # 连接数据库
        conn = await asyncpg.connect(**DB_CONFIG)
        
        print(f"🔍 分析Job {job_id}的数据状态...")
        
        # 查询Job基本信息
        job_info = await conn.fetchrow('SELECT id, status, initial_request FROM jobs WHERE id = $1', job_id)
        if not job_info:
            print(f"❌ Job {job_id} 不存在")
            return False
            
        print(f"📋 Job {job_id} 状态: {job_info['status']}")
        print(f"📝 请求内容: {job_info['initial_request'][:100]}...")
        
        # 查询相关Tasks
        tasks = await conn.fetch('SELECT id, agent_id, status, error_log FROM tasks WHERE job_id = $1', job_id)
        print(f"\n📊 相关Tasks数量: {len(tasks)}")
        for task in tasks:
            error_preview = task['error_log'][:50] + '...' if task['error_log'] else 'None'
            print(f"  Task {task['id']} ({task['agent_id']}): {task['status']} - Error: {error_preview}")
        
        # 查询相关Artifacts
        task_ids = [task['id'] for task in tasks]
        if task_ids:
            artifacts = await conn.fetch('SELECT id, task_id, name, schema_id FROM artifacts WHERE task_id = ANY($1)', task_ids)
            print(f"\n🗃️  相关Artifacts数量: {len(artifacts)}")
            for artifact in artifacts:
                print(f"  Artifact {artifact['id']} (Task {artifact['task_id']}): {artifact['name']} - {artifact['schema_id']}")
        else:
            artifacts = []
            print(f"\n🗃️  相关Artifacts数量: 0")
        
        if dry_run:
            print(f"\n🧪 试运行模式 - 以下数据将被删除:")
            print(f"  - Job {job_id}: 1条记录")
            print(f"  - Tasks: {len(tasks)}条记录")
            print(f"  - Artifacts: {len(artifacts)}条记录")
            print(f"\n💡 要执行实际清理，请使用: --execute 参数")
            return True
        
        # 实际执行清理
        print(f"\n🚨 开始清理Job {job_id}的所有数据...")
        
        async with conn.transaction():
            # 删除Artifacts (必须先删除，因为有外键约束)
            if artifacts:
                artifact_ids = [art['id'] for art in artifacts]
                deleted_artifacts = await conn.execute('DELETE FROM artifacts WHERE id = ANY($1)', artifact_ids)
                print(f"✅ 已删除 {len(artifacts)} 个Artifacts")
            
            # 删除Tasks
            if tasks:
                task_ids = [task['id'] for task in tasks]
                deleted_tasks = await conn.execute('DELETE FROM tasks WHERE id = ANY($1)', task_ids)
                print(f"✅ 已删除 {len(tasks)} 个Tasks")
            
            # 删除Job
            deleted_job = await conn.execute('DELETE FROM jobs WHERE id = $1', job_id)
            print(f"✅ 已删除Job {job_id}")
        
        print(f"\n🎉 Job {job_id} 数据清理完成!")
        
        # 验证清理结果
        remaining_job = await conn.fetchrow('SELECT id FROM jobs WHERE id = $1', job_id)
        remaining_tasks = await conn.fetch('SELECT id FROM tasks WHERE job_id = $1', job_id)
        
        if remaining_job or remaining_tasks:
            print(f"⚠️  警告: 仍有残留数据")
            return False
        else:
            print(f"✅ 验证完成: 所有相关数据已彻底清理")
            return True
            
    except Exception as e:
        print(f"❌ 清理过程中发生错误: {e}")
        return False
    finally:
        await conn.close()

async def list_problematic_jobs() -> None:
    """列出可能有问题的Jobs"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        print("🔍 扫描可能存在问题的Jobs...")
        
        # 查找状态为in_progress但有错误Tasks的Jobs
        query = """
        SELECT DISTINCT j.id, j.status, j.initial_request, 
               COUNT(t.id) as task_count,
               COUNT(CASE WHEN t.status = 'FAILED' THEN 1 END) as failed_tasks,
               COUNT(CASE WHEN t.error_log IS NOT NULL THEN 1 END) as error_tasks
        FROM jobs j
        LEFT JOIN tasks t ON j.id = t.job_id
        WHERE j.status = 'IN_PROGRESS'
        GROUP BY j.id, j.status, j.initial_request
        HAVING COUNT(CASE WHEN t.status = 'FAILED' THEN 1 END) > 0 
            OR COUNT(CASE WHEN t.error_log IS NOT NULL THEN 1 END) > 0
        ORDER BY j.id DESC
        """
        
        problematic_jobs = await conn.fetch(query)
        
        if not problematic_jobs:
            print("✅ 没有发现问题的Jobs")
            return
        
        print(f"\n⚠️  发现 {len(problematic_jobs)} 个可能有问题的Jobs:")
        print("-" * 80)
        
        for job in problematic_jobs:
            print(f"Job {job['id']}: {job['status']}")
            print(f"  请求: {job['initial_request'][:60]}...")
            print(f"  Tasks总数: {job['task_count']}, 失败: {job['failed_tasks']}, 有错误: {job['error_tasks']}")
            print()
            
    except Exception as e:
        print(f"❌ 扫描过程中发生错误: {e}")
    finally:
        await conn.close()

async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("HELIX 脏数据清理工具")
        print("\n用法:")
        print("  python cleanup_dirty_data.py scan                    # 扫描问题Jobs")
        print("  python cleanup_dirty_data.py cleanup <job_id>        # 试运行清理")
        print("  python cleanup_dirty_data.py cleanup <job_id> --execute  # 实际执行清理")
        print("\n示例:")
        print("  python cleanup_dirty_data.py scan")
        print("  python cleanup_dirty_data.py cleanup 4")
        print("  python cleanup_dirty_data.py cleanup 4 --execute")
        return
    
    command = sys.argv[1]
    
    if command == "scan":
        await list_problematic_jobs()
    elif command == "cleanup":
        if len(sys.argv) < 3:
            print("❌ 错误: 请指定要清理的Job ID")
            return
        
        try:
            job_id = int(sys.argv[2])
        except ValueError:
            print("❌ 错误: Job ID 必须是数字")
            return
        
        dry_run = "--execute" not in sys.argv
        success = await cleanup_job_data(job_id, dry_run)
        
        if success and not dry_run:
            print(f"\n🎯 Job {job_id} 清理完成!")
            print("💡 建议重新启动HELIX系统以确保完全恢复")
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    asyncio.run(main())