# AGENT_5 提示词优化实现文档

## 实现概述

根据用户需求，AGENT_5已从单纯的"诊断报告生成器"升级为"提示词优化器"，现在能够：

1. **分析失败案例**：识别失败的Agent和失败原因
2. **生成改进提示词**：基于失败分析生成优化的提示词
3. **更新数据库**：将新版本提示词保存到agent_prompts表
4. **触发重试**：创建新的任务让失败的Agent使用改进后的提示词重试

## 核心变更

### 1. AGENT_5 处理流程重构

```python
async def process_task(self, task_input: TaskInput) -> TaskOutput:
    """
    处理系统诊断与进化任务
    
    核心功能：
    1. 分析系统故障案例
    2. 生成改进的提示词
    3. 更新失败Agent的提示词到数据库
    4. 触发AGENT_3重新执行
    """
    # 分析故障并生成改进的提示词
    improved_prompt = await self._analyze_and_improve_prompt(
        system_failure_case, audit_report
    )
    
    # 更新失败Agent的提示词到数据库
    failed_agent = await self._update_agent_prompt(system_failure_case, improved_prompt)
    
    # 创建新的AGENT_3任务以重新执行
    await self._create_retry_task(system_failure_case, failed_agent)
```

### 2. 提示词版本管理

在 `agent_sdk.py` 中实现了完整的版本管理：

```python
async def get_agent_prompt(self, version: str = "v0") -> Optional[str]:
    """
    获取Agent提示词
    
    版本策略：
    - "v0": 基础版本，新任务默认使用
    - "latest": 最新活跃版本
    - 具体版本: 如 "v20240115_123456"
    """
```

#### 关键特性：
- **默认使用v0**：新任务默认加载v0版本，确保稳定性
- **版本回滚**：支持回滚到任意历史版本
- **版本清理**：可清理过期版本，保留关键版本

### 3. 智能重试机制

```python
async def _create_retry_task(self, system_failure_case: Dict[str, Any], 
                            failed_agent: str):
    """
    创建重试任务
    
    特点：
    1. 复制原始任务的输入数据
    2. 添加retry_with_improved_prompt标志
    3. 增加retry_count计数
    """
```

## 工作流程

```
用户请求 → AGENT_1 → AGENT_2 → AGENT_3（失败）
                                    ↓
                                AGENT_5（诊断）
                                    ↓
                            生成改进的提示词
                                    ↓
                            更新到数据库(新版本)
                                    ↓
                            创建新的AGENT_3任务
                                    ↓
                            AGENT_3（使用新提示词重试）
                                    ↓
                                AGENT_4（审计）
```

## 数据库结构

### agent_prompts 表
```sql
- agent_id: Agent标识
- version: 版本号（v0, v20240115_123456等）
- prompt_text: 提示词内容
- is_active: 是否为活跃版本
- created_by: 创建者（system, AGENT_5等）
- created_at: 创建时间
```

### 版本管理规则
1. v0永远不是活跃版本（基础版本）
2. 同时只能有一个活跃版本（除v0外）
3. AGENT_5创建的版本自动成为活跃版本

## 使用示例

### 1. 检查提示词版本
```sql
SELECT version, is_active, created_by, created_at 
FROM agent_prompts 
WHERE agent_id = 'AGENT_3' 
ORDER BY created_at DESC;
```

### 2. 查看重试任务
```sql
SELECT id, agent_id, status, 
       input_data->'params'->>'retry_with_improved_prompt' as retry_flag,
       input_data->'params'->>'retry_count' as retry_count
FROM tasks 
WHERE job_id = $1 AND agent_id = 'AGENT_3';
```

## 配置建议

1. **初始化v0版本**：为每个Agent创建稳定的v0基础版本
2. **监控重试次数**：避免无限重试，建议最多重试5次
3. **定期清理**：清理过期的提示词版本，保留v0和最近的几个版本

## 未来优化方向

1. **A/B测试**：同时运行多个版本，选择最优
2. **自动回滚**：失败率上升时自动回滚到稳定版本
3. **版本对比**：可视化展示版本差异
4. **性能指标**：跟踪每个版本的成功率