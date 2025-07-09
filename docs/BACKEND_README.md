# Project HELIX Backend Agent Development Guide

**版本:** 2.1 (DeepSeek优化版)  
**状态:** Agent开发指南  
**对齐:** README.md v2.0 开发者就绪版

---

## 1. 简介与范围 (Introduction & Scope)

### 1.1 文档目的

本文档是Project HELIX后端工程师开发Agent的主要技术指南。它基于项目的核心设计原则，提供架构模式、最佳实践和具体实现细节，确保Agent开发的一致性、可维护性，并与项目基础原则保持对齐。

### 1.2 目标受众与前提条件

**目标受众:** 后端工程师、Agent开发者、系统架构师
**技术前提:** Python 3.10+、异步编程基础、数据库事务概念
**项目前提:** 请先阅读 [README.md](README.md) 了解Project HELIX的整体愿景和架构

### 1.3 后端技术栈概览

| 组件 | 技术选型 | 用途 |
|------|----------|------|
| **Agent框架** | 自定义asyncio脚本 | 状态驱动的Agent执行引擎 |
| **API服务** | FastAPI + Pydantic | Agent任务创建与状态查询 |
| **数据持久化** | PostgreSQL + asyncpg | 状态管理与事务保证 |
| **AI模型交互** | 直接使用供应商SDK | 保证对Prompt的完全控制 |

## 2. Project HELIX核心原则在后端开发中的体现 (Core Principles P1-P7)

> **重要:** 以下原则的权威定义位于主 [README.md](README.md)。本节解释这些原则在后端开发中的具体实现。

### 2.1 P1: 代理架构 (Agentic Architecture)

**原则:** 系统由高度专业化、角色明确的自主AI代理组成

**后端实现:**
```python
# agents/base.py
class BaseAgent:
    def __init__(self, agent_id: str, db_manager):
        self.agent_id = agent_id
        self.db_manager = db_manager
    
    async def execute_task(self, task_id: int) -> bool:
        """每个Agent必须实现的核心执行方法"""
        task = await self.get_task(task_id)
        try:
            result = await self.process(task.input_data)
            await self.save_output_and_complete_task(task_id, result)
            return True
        except Exception as e:
            await self.mark_task_failed(task_id, str(e))
            return False
    
    async def process(self, input_data: dict) -> dict:
        """子类必须实现的核心业务逻辑"""
        raise NotImplementedError()
```

### 2.2 P2: 持久化状态接口 (Persistent State Interfaces)

**原则:** Agent间通信必须通过中心化、持久化的状态数据库进行

**后端实现:**
```python
# ✅ 正确：通过数据库通信
async def pass_artifact_to_next_agent(self, artifact_data: dict, next_agent: str):
    async with self.db_manager.transaction() as conn:
        await conn.execute("""
            INSERT INTO tasks (agent_id, input_data, status) 
            VALUES ($1, $2, 'PENDING')
        """, next_agent, json.dumps(artifact_data))

# ❌ 错误：直接调用其他Agent
# await other_agent.process_directly(data)  # 违反P2原则
```

### 2.3 P3: 外部化认知 (Externalized Cognition)

**原则:** Agent的核心逻辑(Prompt)必须与执行引擎分离，外部存储并版本控制

**后端实现:**
```python
class CreativeDirector(BaseAgent):
    async def get_prompt(self, version: str = "latest") -> str:
        """从数据库获取外部化的Prompt"""
        async with self.db_manager.get_connection() as conn:
            result = await conn.fetchrow("""
                SELECT prompt_text FROM agent_prompts 
                WHERE agent_id = $1 AND version = $2
            """, self.agent_id, version)
            return result['prompt_text']
    
    async def process(self, input_data: dict) -> dict:
        prompt = await self.get_prompt()
        # 使用外部化的prompt进行AI调用
        return await self.call_ai_model(prompt, input_data)
```

### 2.4 P4: 幂等与可恢复性 (Idempotence & Recoverability)

**原则:** 每个任务步骤必须幂等，任何失败都可以从已知良好状态恢复

**后端实现:**
```python
async def process_with_idempotence(self, task_id: int):
    # 检查任务是否已完成（幂等性保证）
    task = await self.get_task(task_id)
    if task.status == 'COMPLETED':
        return task.output_data
    
    # 实现具体的幂等处理逻辑
    result = await self.do_actual_work(task.input_data)
    
    # 原子性更新状态
    async with self.db_manager.transaction() as conn:
        await conn.execute("""
            UPDATE tasks SET status = 'COMPLETED', output_data = $1 
            WHERE id = $2 AND status != 'COMPLETED'
        """, json.dumps(result), task_id)
```

### 2.5 P5: 基于历史的自我改进 (History-Based Self-Improvement)

**原则:** 系统自我优化基于完整、可靠、持久化的任务历史

**后端实现:**
```python
class MetaOptimizer(BaseAgent):
    async def analyze_failure_patterns(self, agent_id: str) -> dict:
        """分析特定Agent的失败模式"""
        async with self.db_manager.get_connection() as conn:
            failures = await conn.fetch("""
                SELECT input_data, error_log, created_at 
                FROM tasks 
                WHERE agent_id = $1 AND status = 'FAILED'
                ORDER BY created_at DESC LIMIT 100
            """, agent_id)
            
        # 基于历史数据生成优化建议
        return await self.generate_optimization_proposal(failures)
```

### 2.6 P6: 统一构件引用协议 (Unified Artifact-Reference Protocol)

**原则:** 任务输入是轻量级的构件需求列表，而非庞大数据实体

**后端实现:**
```python
# 标准输入格式
input_data = {
    "artifacts": [
        {"name": "creative_brief", "source_task_id": 101},
        {"name": "visual_explorations", "source_task_id": 102}
    ],
    "params": {"session_id": "abc123"}
}

# Agent获取构件的标准方法
async def get_artifacts(self, artifact_requests: list) -> dict:
    artifacts = {}
    for req in artifact_requests:
        task = await self.get_task(req["source_task_id"])
        artifacts[req["name"]] = task.output_data
    return artifacts
```

### 2.7 P7: 构件的自描述与验证 (Artifact Self-Description and Validation)

**原则:** 每个构件必须自描述和可验证，将接口正确性从文档约定提升为运行时保证

**后端实现:**
```python
from pydantic import BaseModel, Field

class CreativeBriefArtifact(BaseModel):
    schema_id: str = "CreativeBrief_v1.0"
    payload: dict = Field(..., description="创意蓝图内容")
    
    @classmethod
    def validate_schema(cls, data: dict) -> bool:
        try:
            cls.parse_obj(data)
            return True
        except ValidationError:
            return False

async def save_output_and_complete_task(self, task_id: int, output: dict):
    # P7: 保存前验证构件Schema
    if not CreativeBriefArtifact.validate_schema(output):
        raise ValueError("输出不符合CreativeBrief_v1.0 Schema")
    
    async with self.db_manager.transaction() as conn:
        await conn.execute("""
            UPDATE tasks SET status = 'COMPLETED', output_data = $1 
            WHERE id = $2
        """, json.dumps(output), task_id)
```

## 3. Agent开发快速开始 (Getting Started with Backend Agents)

### 3.1 本地开发环境设置

```bash
# 1. 克隆项目
git clone <repo-url>
cd project-helix

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑.env文件，添加必要的API密钥

# 4. 启动数据库
docker-compose up -d postgres

# 5. 运行数据库迁移
python scripts/init_db.py
```

### 3.2 运行后端应用

```bash
# 启动编排器和Agent工作进程
python start_system.py

# 验证运行状态
curl http://localhost:8000/api/v1/health
```

## 4. Agent架构设计标准 (Agent Architecture Standards)

> **⚠️ 重要:** 所有Agent开发必须遵循统一的架构标准。详细规范请参考：[Agent架构设计标准文档](AGENT_ARCHITECTURE_STANDARDS.md)

### 4.1 架构一致性要求

所有HELIX Agent必须符合以下标准：

#### **核心架构模式**
- 继承自 `BaseAgent` 基类
- 实现标准的 `execute_task()` 方法（统一接口）
- 遵循 **AI优先 + 模板后备** 模式
- 严格的输入验证和输出Schema验证

#### **数据流兼容性**
- 使用统一的构件引用协议 (P6)
- 输出Schema与下游Agent输入需求匹配
- 完整的元数据传递机制

#### **强制检查清单**
- [ ] **P1: 代理架构** - 明确的agent_id和专业化职责
- [ ] **P2: 持久化状态** - 无内存状态，纯数据库驱动
- [ ] **P3: 外部化认知** - 从数据库获取prompt并支持版本管理
- [ ] **P4: 幂等性** - 任务可重复执行，完整错误处理
- [ ] **P5: 历史学习** - 系统事件记录
- [ ] **P6: 构件引用** - 轻量级引用，非数据实体传递
- [ ] **P7: 自描述验证** - 严格的JSON Schema验证

### 4.2 标准实现模式

```python
# 标准Agent实现示例
class YourAgent(BaseAgent):
    """
    遵循标准架构模式的Agent实现
    """
    
    def __init__(self, db_manager):
        super().__init__("YOUR_AGENT_ID", db_manager)
    
    async def execute_task(self, task_id: int) -> bool:
        """标准任务执行流程（统一接口）"""
        try:
            # 1. 获取任务并解析输入
            task = await self.get_task(task_id)
            task_input = TaskInput.parse_obj(task.input_data)
            
            # 2. 获取输入构件
            artifacts = await self.get_artifacts(task_input.artifacts)
            self._validate_required_artifacts(artifacts)
            
            # 3. 获取提示词 (P3: 外部化认知)
            system_prompt = await self.get_system_prompt()
            if not system_prompt:
                raise ValueError(f"No prompt found for {self.agent_id}")
            
            # 4. 生成输出 (AI优先 + 模板后备)
            output = await self._generate_output(artifacts, system_prompt)
            
            # 5. 保存输出并完成任务
            await self.save_output_and_complete_task(task_id, output)
            
            # 6. 记录成功事件
            await self.log_system_event("INFO", "Task completed successfully")
            
            return True
            
        except Exception as e:
            logger.error("Task processing failed", error=str(e))
            await self.log_system_event("ERROR", f"Task failed: {str(e)}")
            await self.mark_task_failed(task_id, str(e))
            return False
    
    @property
    def output_schema_id(self) -> str:
        return "YourSchema_v1.0"
    
    def _validate_required_artifacts(self, artifacts: Dict[str, Any]) -> None:
        """验证必需的输入构件"""
        required = ["required_artifact_name"]
        for artifact in required:
            if artifact not in artifacts:
                raise ValueError(f"Required artifact '{artifact}' not found")
```

### 4.3 工作流配置示例

工作流定义（workflows.json）示例：

```json
{
  "workflows": {
    "creative_production": {
      "description": "创意生产工作流",
      "agents": [
        {
          "id": "AGENT_1",
          "name": "CreativeDirector",
          "input_artifacts": [],
          "output_schema": "CreativeBrief_v1.0",
          "retry_count": 3,
          "timeout": 300
        },
        {
          "id": "AGENT_2", 
          "name": "VisualDirector",
          "input_artifacts": ["creative_brief"],
          "output_schema": "VisualExplorations_v1.0",
          "retry_count": 3,
          "timeout": 600
        },
        {
          "id": "AGENT_3",
          "name": "PresentationDesigner", 
          "input_artifacts": ["creative_brief", "visual_explorations"],
          "output_schema": "PresentationBlueprint_v1.0",
          "retry_count": 2,
          "timeout": 900
        }
      ]
    }
  }
}
```

数据流兼容性验证：

```python
# 数据流兼容性矩阵
AGENT_DATA_FLOW = {
    "AGENT_1": {
        "input_artifacts": [],  # 直接处理用户chat_input
        "output_artifact": "creative_brief",
        "output_schema": "CreativeBrief_v1.0"
    },
    "AGENT_2": {
        "input_artifacts": ["creative_brief"],  # 来自AGENT_1
        "output_artifact": "visual_explorations", 
        "output_schema": "VisualExplorations_v1.0"
    },
    "AGENT_3": {
        "input_artifacts": ["creative_brief", "visual_explorations"],
        "output_artifact": "presentation_blueprint",
        "output_schema": "PresentationBlueprint_v1.0"
    }
}
```

### 4.4 快速开发指南

1. **创建Agent类** - 继承StandardAgent基类
2. **定义输出Schema** - 在schemas/目录创建JSON Schema文件
3. **实现必需方法** - 实现abstract methods
4. **编写单元测试** - 验证数据流兼容性
5. **更新工作流配置** - 在workflows.json中注册

### 4.5 质量保证

所有Agent必须通过以下验证：

- **架构一致性检查** - 符合标准架构模式
- **数据流兼容性测试** - 与上下游Agent无缝对接
- **Schema验证测试** - 输出严格符合JSON Schema
- **错误处理验证** - 正确的错误分类和处理
- **性能基准测试** - 满足响应时间要求

---

### 3.3 创建您的第一个Agent (快速示例)

```python
# agents/example_agent.py
from agents.base import BaseAgent
import json

class ExampleAgent(BaseAgent):
    def __init__(self, db_manager):
        super().__init__("EXAMPLE_AGENT", db_manager)
    
    async def process(self, input_data: dict) -> dict:
        """实现您的Agent核心逻辑"""
        artifacts = await self.get_artifacts(input_data.get("artifacts", []))
        params = input_data.get("params", {})
        
        # 您的处理逻辑
        result = {
            "schema_id": "ExampleOutput_v1.0",
            "payload": {
                "message": f"处理完成: {len(artifacts)}个构件",
                "session_id": params.get("session_id")
            }
        }
        
        return result

# 注册Agent到系统
# agents/__init__.py
from .example_agent import ExampleAgent
AVAILABLE_AGENTS = {
    "EXAMPLE_AGENT": ExampleAgent
}
```

## 4. Agent架构与生命周期 (Agent Architecture & Lifecycle)

### 4.1 Agent定义(基类/接口)

```python
# agents/base.py
from abc import ABC, abstractmethod
import asyncio
import json
import logging

class BaseAgent(ABC):
    def __init__(self, agent_id: str, db_manager):
        self.agent_id = agent_id
        self.db_manager = db_manager
        self.logger = logging.getLogger(f"agent.{agent_id}")
    
    @abstractmethod
    async def process(self, input_data: dict) -> dict:
        """子类必须实现的核心业务逻辑"""
        pass
    
    async def get_task(self, task_id: int):
        """获取任务详情"""
        async with self.db_manager.get_connection() as conn:
            return await conn.fetchrow(
                "SELECT * FROM tasks WHERE id = $1", task_id
            )
    
    async def get_artifacts(self, artifact_requests: list) -> dict:
        """批量获取构件(解决N+1问题)"""
        if not artifact_requests:
            return {}
        
        task_ids = [req["source_task_id"] for req in artifact_requests]
        async with self.db_manager.get_connection() as conn:
            tasks = await conn.fetch(
                "SELECT id, output_data FROM tasks WHERE id = ANY($1)",
                task_ids
            )
        
        artifacts = {}
        for req in artifact_requests:
            for task in tasks:
                if task['id'] == req["source_task_id"]:
                    artifacts[req["name"]] = json.loads(task['output_data'])
                    break
        
        return artifacts
```

### 4.2 Agent注册与发现

```python
# agents/__init__.py
from .creative_director import CreativeDirector
from .visual_director import VisualDirector
# ... 其他Agent导入

AVAILABLE_AGENTS = {
    "AGENT_1": CreativeDirector,
    "AGENT_2": VisualDirector,
    # ... 其他Agent
}

def create_agent(agent_id: str, db_manager):
    """Agent工厂方法"""
    agent_class = AVAILABLE_AGENTS.get(agent_id)
    if not agent_class:
        raise ValueError(f"未知的Agent ID: {agent_id}")
    return agent_class(db_manager)
```

### 4.3 Agent生命周期

```python
# orchestrator/agent_worker.py
class AgentWorker:
    def __init__(self, agent_id: str, db_manager):
        self.agent = create_agent(agent_id, db_manager)
        self.running = True
    
    async def run(self):
        """Agent工作循环"""
        while self.running:
            try:
                # 1. 获取待处理任务
                task = await self.claim_next_task()
                if task:
                    # 2. 执行任务
                    await self.agent.execute_task(task['id'])
                else:
                    # 3. 没有任务时短暂休眠
                    await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Agent执行错误: {e}")
                await asyncio.sleep(5)  # 错误后等待重试
```

## 5. Agent通信与交互 (Agent Communication & Interaction)

### 5.1 Agent间通信模式

Project HELIX采用**异步状态驱动**的通信模式：

```python
# ✅ 推荐：通过数据库状态驱动
async def create_next_task(self, output_data: dict, next_agent_id: str):
    async with self.db_manager.transaction() as conn:
        await conn.execute("""
            INSERT INTO tasks (agent_id, input_data, status, job_id)
            VALUES ($1, $2, 'PENDING', $3)
        """, next_agent_id, json.dumps(output_data), self.current_job_id)

# ❌ 避免：直接调用其他Agent
# await other_agent.process_directly(data)
```

### 5.2 统一构件引用协议实现(P6)

**数据模型定义:**
```python
# schemas/task_io.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ArtifactReference(BaseModel):
    name: str = Field(..., description="构件名称")
    source_task_id: int = Field(..., description="构件来源任务ID")

class TaskInput(BaseModel):
    artifacts: List[ArtifactReference] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)

class TaskOutput(BaseModel):
    schema_id: str = Field(..., description="输出Schema标识")
    payload: Dict[str, Any] = Field(..., description="实际数据载荷")
```

**常用构件类型:**
```python
# schemas/artifacts.py
class CreativeBrief(BaseModel):
    schema_id: str = "CreativeBrief_v1.0"
    title: str
    narrative: str
    target_audience: str
    key_messages: List[str]

class VisualExplorations(BaseModel):
    schema_id: str = "VisualExplorations_v1.0"
    concepts: List[Dict[str, Any]]
    selected_concept_id: Optional[str]
```

### 5.3 构件自描述与验证(P7)

**Schema定义与强制执行:**
```python
# 在Agent中使用
async def save_output_and_complete_task(self, task_id: int, output: dict):
    # P7: 运行时Schema验证
    schema_id = output.get("schema_id")
    if not self.validate_output_schema(schema_id, output):
        raise ValueError(f"输出不符合{schema_id}规范")
    
    async with self.db_manager.transaction() as conn:
        await conn.execute("""
            UPDATE tasks SET 
                status = 'COMPLETED', 
                output_data = $1,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = $2
        """, json.dumps(output), task_id)

def validate_output_schema(self, schema_id: str, data: dict) -> bool:
    """根据schema_id验证数据结构"""
    schema_registry = {
        "CreativeBrief_v1.0": CreativeBrief,
        "VisualExplorations_v1.0": VisualExplorations,
    }
    
    schema_class = schema_registry.get(schema_id)
    if not schema_class:
        return False
    
    try:
        schema_class.parse_obj(data)
        return True
    except ValidationError as e:
        self.logger.error(f"Schema验证失败: {e}")
        return False
```

### 5.4 与外部服务交互

```python
# agents/mixins/ai_mixin.py
class AIModelMixin:
    async def call_openai(self, prompt: str, input_data: dict) -> dict:
        """标准的AI模型调用接口"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": json.dumps(input_data)}
                ]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            self.logger.error(f"AI模型调用失败: {e}")
            raise
```

## 6. Agent状态管理与数据持久化 (Agent State Management & Data Persistence)

### 6.1 Agent状态管理原则

1. **单一真理源:** 所有状态必须持久化到PostgreSQL
2. **事务原子性:** 状态变更必须在事务中完成
3. **并发安全:** 使用数据库锁避免竞态条件

### 6.2 PostgreSQL使用模式

**连接管理:**
```python
# database/manager.py
import asyncpg
from contextlib import asynccontextmanager

class DatabaseManager:
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.pool = None
    
    async def init_pool(self):
        self.pool = await asyncpg.create_pool(
            self.connection_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
    
    @asynccontextmanager
    async def get_connection(self):
        async with self.pool.acquire() as conn:
            yield conn
    
    @asynccontextmanager
    async def transaction(self):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn
```

### 6.3 事务管理(P5)

```python
async def update_task_with_retry(self, task_id: int, status: str, output_data: dict = None):
    """带重试机制的事务更新"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with self.db_manager.transaction() as conn:
                # 使用FOR UPDATE防止并发修改
                task = await conn.fetchrow(
                    "SELECT * FROM tasks WHERE id = $1 FOR UPDATE", 
                    task_id
                )
                
                if not task:
                    raise ValueError(f"任务{task_id}不存在")
                
                # 原子性更新
                await conn.execute("""
                    UPDATE tasks SET 
                        status = $1, 
                        output_data = $2,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = $3
                """, status, json.dumps(output_data) if output_data else None, task_id)
                
                return True
                
        except asyncpg.exceptions.DeadlockDetectedError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # 指数退避
```

### 6.4 Agent常用数据访问模式

```python
class AgentDataAccess:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    async def claim_next_task(self, agent_id: str):
        """声明下一个待处理任务(防止竞态)"""
        async with self.db_manager.transaction() as conn:
            task = await conn.fetchrow("""
                SELECT * FROM tasks 
                WHERE agent_id = $1 AND status = 'PENDING'
                ORDER BY created_at ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            """, agent_id)
            
            if task:
                await conn.execute("""
                    UPDATE tasks 
                    SET status = 'IN_PROGRESS', started_at = CURRENT_TIMESTAMP 
                    WHERE id = $1
                """, task['id'])
            
            return task
    
    async def get_job_context(self, job_id: int) -> dict:
        """获取作业的完整上下文"""
        async with self.db_manager.get_connection() as conn:
            job = await conn.fetchrow(
                "SELECT * FROM jobs WHERE id = $1", job_id
            )
            tasks = await conn.fetch(
                "SELECT * FROM tasks WHERE job_id = $1 ORDER BY created_at", 
                job_id
            )
            
            return {
                "job": dict(job),
                "tasks": [dict(task) for task in tasks],
                "completed_artifacts": [
                    json.loads(task['output_data']) 
                    for task in tasks 
                    if task['status'] == 'COMPLETED' and task['output_data']
                ]
            }
```

## 7. 外部化认知(P3) - Prompt管理 (Externalized Cognition - Prompt Management)

### 7.1 Prompt存储与检索

```python
# database/schema.sql
CREATE TABLE agent_prompts (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL DEFAULT 'latest',
    prompt_text TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(agent_id, version)
);

# Agent中的使用
class CreativeDirector(BaseAgent):
    async def get_system_prompt(self, version: str = "latest") -> str:
        async with self.db_manager.get_connection() as conn:
            result = await conn.fetchrow("""
                SELECT prompt_text FROM agent_prompts 
                WHERE agent_id = $1 AND version = $2 AND is_active = true
            """, self.agent_id, version)
            
            if not result:
                raise ValueError(f"未找到{self.agent_id}的{version}版本Prompt")
            
            return result['prompt_text']
```

### 7.2 Prompt版本控制与模板策略

```python
# prompts/manager.py
class PromptManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    async def create_prompt_version(self, agent_id: str, prompt_text: str, 
                                   version: str = None) -> str:
        """创建新的Prompt版本"""
        if not version:
            version = await self.generate_version_number(agent_id)
        
        async with self.db_manager.transaction() as conn:
            await conn.execute("""
                INSERT INTO agent_prompts (agent_id, version, prompt_text)
                VALUES ($1, $2, $3)
            """, agent_id, version, prompt_text)
            
            # 更新latest版本
            await conn.execute("""
                UPDATE agent_prompts 
                SET version = 'latest' 
                WHERE agent_id = $1 AND version = $2
            """, agent_id, version)
        
        return version
    
    async def rollback_prompt(self, agent_id: str, target_version: str):
        """回滚到指定版本"""
        async with self.db_manager.transaction() as conn:
            # 验证目标版本存在
            exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM agent_prompts 
                    WHERE agent_id = $1 AND version = $2
                )
            """, agent_id, target_version)
            
            if not exists:
                raise ValueError(f"版本{target_version}不存在")
            
            # 更新latest指向
            await conn.execute("""
                UPDATE agent_prompts 
                SET version = 'latest'
                WHERE agent_id = $1 AND version = $2
            """, agent_id, target_version)
```

### 7.3 Prompt注入到Agent逻辑

```python
class TemplatedAgent(BaseAgent):
    async def process_with_template(self, input_data: dict) -> dict:
        """使用模板化Prompt处理"""
        # 获取外部化的Prompt模板
        prompt_template = await self.get_system_prompt()
        
        # 注入上下文变量
        context = await self.build_context(input_data)
        final_prompt = self.render_prompt(prompt_template, context)
        
        # 调用AI模型
        return await self.call_ai_model(final_prompt, input_data)
    
    def render_prompt(self, template: str, context: dict) -> str:
        """渲染Prompt模板"""
        from jinja2 import Template
        jinja_template = Template(template)
        return jinja_template.render(**context)
    
    async def build_context(self, input_data: dict) -> dict:
        """构建Prompt上下文"""
        artifacts = await self.get_artifacts(input_data.get("artifacts", []))
        return {
            "artifacts": artifacts,
            "params": input_data.get("params", {}),
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat()
        }
```

## 8. 错误处理、日志和可观测性 (Error Handling, Logging, and Observability)

### 8.1 错误分类标准

Project HELIX 采用标准化的错误分类系统：

```python
from enum import Enum

class ErrorType(Enum):
    # 业务错误 - 不重试
    VALIDATION_ERROR = "validation_error"      # Schema验证失败
    BUSINESS_LOGIC_ERROR = "business_error"    # 业务逻辑错误
    
    # 系统错误 - 可重试
    AI_MODEL_ERROR = "ai_model_error"          # AI模型调用失败
    DATABASE_ERROR = "database_error"          # 数据库连接/查询失败
    NETWORK_ERROR = "network_error"            # 网络连接失败
    
    # 资源错误 - 部分可重试
    TIMEOUT_ERROR = "timeout_error"            # 执行超时
    RESOURCE_LIMIT_ERROR = "resource_error"    # 资源限制
    
    # 系统级错误 - 需要人工干预
    CONFIGURATION_ERROR = "config_error"       # 配置错误
    UNKNOWN_ERROR = "unknown_error"            # 未知错误

class ErrorSeverity(Enum):
    LOW = "low"              # 不影响业务流程
    MEDIUM = "medium"        # 影响单个任务
    HIGH = "high"            # 影响整个作业
    CRITICAL = "critical"    # 影响系统稳定性
```

### 8.2 Agent标准错误处理模式

```python
class RobustAgent(BaseAgent):
    async def execute_task(self, task_id: int) -> bool:
        """带完整错误处理的任务执行"""
        try:
            # 标记任务开始
            await self.mark_task_in_progress(task_id)
            
            # 执行核心逻辑
            task = await self.get_task(task_id)
            result = await self.process(task.input_data)
            
            # 成功完成
            await self.save_output_and_complete_task(task_id, result)
            self.logger.info("任务执行成功", extra={"task_id": task_id})
            return True
            
        except ValidationError as e:
            # Schema验证错误 - 不重试
            await self.mark_task_failed(task_id, f"数据验证错误: {e}", retryable=False)
            return False
            
        except AIModelError as e:
            # AI模型错误 - 可重试
            await self.mark_task_failed(task_id, f"AI模型错误: {e}", retryable=True)
            return False
            
        except Exception as e:
            # 未知错误 - 记录详细信息
            self.logger.error("未知错误", extra={
                "task_id": task_id,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            await self.mark_task_failed(task_id, f"系统错误: {e}", retryable=True)
            return False
    
    async def mark_task_failed(self, task_id: int, error_msg: str, retryable: bool = True):
        """标记任务失败并更新重试计数"""
        async with self.db_manager.transaction() as conn:
            task = await conn.fetchrow("SELECT retry_count FROM tasks WHERE id = $1", task_id)
            new_retry_count = task['retry_count'] + 1
            
            # 判断是否应该重试
            if retryable and new_retry_count < 3:
                new_status = 'PENDING'  # 重新进入队列
            else:
                new_status = 'FAILED'   # 最终失败
            
            await conn.execute("""
                UPDATE tasks SET 
                    status = $1, 
                    error_log = $2, 
                    retry_count = $3,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $4
            """, new_status, error_msg, new_retry_count, task_id)
```

### 8.2 结构化日志最佳实践

```python
import structlog

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

class LoggingAgent(BaseAgent):
    def __init__(self, agent_id: str, db_manager):
        super().__init__(agent_id, db_manager)
        self.logger = structlog.get_logger(agent_id)
    
    async def process(self, input_data: dict) -> dict:
        # 记录处理开始
        self.logger.info("开始处理任务", 
                        input_size=len(str(input_data)),
                        artifacts_count=len(input_data.get("artifacts", [])))
        
        try:
            result = await self.do_actual_processing(input_data)
            
            # 记录成功结果
            self.logger.info("任务处理完成",
                           output_schema=result.get("schema_id"),
                           processing_time=self.get_processing_time())
            
            return result
            
        except Exception as e:
            # 记录错误详情
            self.logger.error("任务处理失败",
                            error_type=type(e).__name__,
                            error_message=str(e),
                            input_summary=self.summarize_input(input_data))
            raise
```

### 8.3 Agent关键指标

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 业务指标
task_counter = Counter('agent_tasks_total', 'Agent处理任务总数', ['agent_id', 'status'])
task_duration = Histogram('agent_task_duration_seconds', 'Agent任务处理时间', ['agent_id'])
active_tasks = Gauge('agent_active_tasks', '当前活跃任务数', ['agent_id'])

class MetricsAgent(BaseAgent):
    async def execute_task(self, task_id: int) -> bool:
        start_time = time.time()
        active_tasks.labels(agent_id=self.agent_id).inc()
        
        try:
            result = await super().execute_task(task_id)
            status = 'success' if result else 'failure'
            
        except Exception:
            status = 'error'
            raise
            
        finally:
            # 记录指标
            task_counter.labels(agent_id=self.agent_id, status=status).inc()
            task_duration.labels(agent_id=self.agent_id).observe(time.time() - start_time)
            active_tasks.labels(agent_id=self.agent_id).dec()
```

## 9. 开发工作流与最佳实践 (Development Workflow & Best Practices)

### 9.1 代码风格与检查

```bash
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.flake8]
max-line-length = 88
exclude = [".venv", "migrations"]
```

### 9.2 Agent测试策略

**单元测试:**
```python
# tests/agents/test_creative_director.py
import pytest
from unittest.mock import AsyncMock
from agents.creative_director import CreativeDirector

@pytest.fixture
async def agent():
    db_manager = AsyncMock()
    return CreativeDirector(db_manager)

@pytest.mark.asyncio
async def test_creative_director_process(agent):
    input_data = {
        "artifacts": [],
        "params": {"chat_input": "创建登录页面", "session_id": "test123"}
    }
    
    result = await agent.process(input_data)
    
    assert result["schema_id"] == "CreativeBrief_v1.0"
    assert "title" in result["payload"]
    assert "narrative" in result["payload"]
```

**集成测试:**
```python
# tests/integration/test_agent_workflow.py
@pytest.mark.asyncio
async def test_complete_agent_workflow(db_manager):
    # 创建初始作业
    job_id = await create_test_job(db_manager, "创建产品展示页面")
    
    # 执行AGENT_1
    agent1 = CreativeDirector(db_manager)
    task1 = await get_pending_task(db_manager, "AGENT_1")
    await agent1.execute_task(task1['id'])
    
    # 验证AGENT_1输出
    completed_task = await get_task(db_manager, task1['id'])
    assert completed_task['status'] == 'COMPLETED'
    output = json.loads(completed_task['output_data'])
    assert output['schema_id'] == 'CreativeBrief_v1.0'
```

### 9.3 asyncio并发考虑

```python
# 正确的并发模式
class ConcurrentAgent(BaseAgent):
    async def process_batch(self, task_ids: List[int]):
        """并发处理多个任务"""
        semaphore = asyncio.Semaphore(5)  # 限制并发数
        
        async def process_single(task_id):
            async with semaphore:
                return await self.execute_task(task_id)
        
        # 并发执行但限制数量
        results = await asyncio.gather(
            *[process_single(task_id) for task_id in task_ids],
            return_exceptions=True
        )
        
        return results
```

### 9.4 常见陷阱与避免方法

**陷阱1: 违反P2原则 - Agent直接通信**
```python
# ❌ 错误做法
await other_agent.process_directly(data)

# ✅ 正确做法
await self.create_task_for_agent("AGENT_2", data)
```

**陷阱2: 忘记事务保护**
```python
# ❌ 错误做法
await conn.execute("UPDATE tasks SET status = 'COMPLETED' WHERE id = $1", task_id)
await conn.execute("INSERT INTO artifacts ...", artifact_data)

# ✅ 正确做法
async with self.db_manager.transaction() as conn:
    await conn.execute("UPDATE tasks SET status = 'COMPLETED' WHERE id = $1", task_id)
    await conn.execute("INSERT INTO artifacts ...", artifact_data)
```

**陷阱3: 硬编码Prompt内容**
```python
# ❌ 错误做法
prompt = "你是一个创意总监，请..."

# ✅ 正确做法
prompt = await self.get_system_prompt()
```

## 10. 附录与进阶阅读 (Appendix & Further Reading)

### 10.1 相关文档链接

- **[主 README.md](README.md)** - 项目整体架构与愿景
- **[API 文档](http://localhost:8000/docs)** - FastAPI自动生成的接口文档
- **[数据库Schema](database/schema.sql)** - 完整的数据库表结构
- **[工作流配置](workflows.json)** - Agent执行顺序定义

### 10.2 开发资源

- **PostgreSQL异步编程:** [asyncpg文档](https://magicstack.github.io/asyncpg/)
- **FastAPI最佳实践:** [FastAPI官方指南](https://fastapi.tiangolo.com/)
- **Pydantic数据验证:** [Pydantic文档](https://docs.pydantic.dev/)
- **结构化日志:** [structlog文档](https://www.structlog.org/)

### 10.3 故障排查快速参考

#### 常见问题诊断流程图

```
问题报告: "任务一直卡在PENDING状态"
├── 检查编排器状态: SELECT * FROM jobs WHERE status = 'RUNNING' LIMIT 5;
├── 检查Agent工作进程: ps aux | grep start_system.py
├── 检查任务队列: SELECT agent_id, COUNT(*) FROM tasks WHERE status = 'PENDING' GROUP BY agent_id;
└── 如果队列正常但无进展 → 检查Agent实现的execute_task()方法

问题报告: "任务重复执行"
├── 检查僵尸任务: SELECT id, agent_id, retry_count FROM tasks WHERE status = 'IN_PROGRESS' AND updated_at < NOW() - INTERVAL '1 hour';
├── 检查幂等性实现: Agent的execute_task()是否正确处理重复调用
└── 临时修复: UPDATE tasks SET status = 'FAILED' WHERE id = <zombie_task_id>;

问题报告: "AI模型调用失败"
├── 检查API密钥: 环境变量 OPENAI_API_KEY 是否正确
├── 检查网络连接: curl -I https://api.openai.com/v1/models
├── 检查模型调用代码: 是否正确处理超时和重试
└── 检查错误日志: 查看具体的异常堆栈
```

#### SQL查询快速参考

```sql
-- 查看Agent状态
SELECT agent_id, status, COUNT(*) 
FROM tasks 
GROUP BY agent_id, status;

-- 检查失败任务
SELECT id, agent_id, error_log, retry_count 
FROM tasks 
WHERE status = 'FAILED' 
ORDER BY created_at DESC LIMIT 10;

-- 检查僵尸任务
SELECT id, agent_id, status, created_at, updated_at
FROM tasks 
WHERE status = 'IN_PROGRESS' 
AND updated_at < NOW() - INTERVAL '1 hour';

-- 重启失败任务
UPDATE tasks 
SET status = 'PENDING', retry_count = 0 
WHERE status = 'FAILED' AND id = <task_id>;

-- 检查任务执行时间分布
SELECT agent_id, 
       AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration,
       COUNT(*) as total_tasks
FROM tasks 
WHERE status = 'COMPLETED' 
AND completed_at IS NOT NULL 
GROUP BY agent_id;
```

#### 性能监控查询

```sql
-- 检查慢查询任务
SELECT id, agent_id, 
       EXTRACT(EPOCH FROM (completed_at - started_at)) as duration
FROM tasks 
WHERE status = 'COMPLETED' 
AND EXTRACT(EPOCH FROM (completed_at - started_at)) > 300
ORDER BY duration DESC;

-- 检查数据库连接数
SELECT datname, usename, COUNT(*) as connection_count
FROM pg_stat_activity 
GROUP BY datname, usename;
```

---

**🎯 开发提醒:**
- 严格遵循P1-P7核心原则
- 所有Agent间通信必须通过数据库
- 实现前先验证Schema定义
- 使用事务保护所有状态变更
- 详细记录结构化日志

**📋 版本历史**

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 2.1 | 2025-07-09 | **DeepSeek优化版本** - 统一方法命名(execute_task)，增加工作流配置示例，添加错误分类标准，扩展故障排查指南 |
| 2.0 | 2025-07-09 | 重构为Agent开发指南，对齐README.md v2.0，删除冗余技术工程 |
| 1.0 | 2025-07-09 | 初始版本（已废弃） |

---

**⚡ 记住：本文档是Agent开发的实用指南，专注于让您快速、正确地构建符合Project HELIX架构原则的后端Agent！**