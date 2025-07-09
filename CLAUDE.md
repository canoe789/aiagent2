# **Project HELIX - AI结对编程指挥官手册**

**版本:** 1.0 (HELIX-Customized)

**优先级:** 🔥 **第一优先事项 - 每次开发对话必读**

**目标:** 指导所有与AI的协作开发，确保严格遵循 Project HELIX 的架构蓝图 (README.md)。

---

## **第一部分：强制引导与上下文 (Onboarding & Context)**

### **1.1 系统级规范强制读取 (Prerequisite: System-Level Directives)**

**⚠️ 重要指令：** 在执行任何项目级别任务之前，**必须先读取系统级别的 CLAUDE.md 文件(**`/home/canoezhang/CLAUDE.md`）。

- **双重规范遵循：** 同时遵守系统级别（通用）和本项目级别（HELIX 特定）的所有指令。
- **冲突处理原则：**
    - 文件管理、路径建议 → 优先遵循**系统级别**规范
    - 项目架构、业务逻辑 → 优先遵循本**项目级别**规范
    - 开发协作模式 → 系统级别和项目级别**结合使用**

**系统级别规范涵盖：**

- 智能文件管理系统和路径建议
- Claude AI高效开发协作指南
- zen-mcp三模型协作模式
- ART快速迭代框架 (Assume-Runtime-Test)
- Claude CLI精确工具使用
- Memory MCP和其他工具配置

**执行检查清单：**

- [ ]  已读取 `/home/canoezhang/CLAUDE.md` 系统级别规范
- [ ]  理解文件管理和路径建议规则
- [ ]  掌握zen-mcp多模型协作模式
- [ ]  了解系统级别的开发协作原则
- [ ]  确认项目特定需求和系统级别规范的结合点

### **1.2 核心文档索引与使用指南 (Knowledge Base Index & Usage Guide)**

重要： 作为AI协作助手，请将 README.md 作为本项目的唯一事实来源 (Single Source of Truth)。

### **主要文档结构**

- [**README.md**](https://www.google.com/url?sa=E&q=README.md) - **项目圣经。** 包含项目愿景、核心原则、系统架构、技术选型、核心协议和项目结构。**是所有技术决策的最终事实来源。**
- [**docs/INDEX.md**](docs/INDEX.md) - **📚 文档导航中心。** 企业级文档索引系统，包含所有项目文档的分类导航、重要性标记和快速查找路径。**查找任何文档前必看！**
- [**docs/PROJECT_PROGRESS.md**](docs/PROJECT_PROGRESS.md) - **项目航海日志。** 用于跟踪开发进度、当前状态、已完成的里程碑和下一步的优先级。
  > 🎓 **重要补充:** 包含"AGENT_1开发经验总结"，实现AGENT_3-5前**必读**！
- [**docs/BACKEND_README.md**](docs/BACKEND_README.md) - **Agent开发指南。** Project HELIX后端工程师开发Agent的主要技术指南，包含架构模式、最佳实践和具体实现细节。
- [**docs/PROCESS_MANAGEMENT.md**](docs/PROCESS_MANAGEMENT.md) - **生产环境进程管理文档。** 记录动态端口管理SOP执行、当前运行状态、监控命令和故障处理流程。
- **workflows.json** - **流程定义文件。** 描述Agent的执行顺序和依赖关系。
- **schemas/ 目录** - **构件契约。** 存放所有构件（Artifacts）的JSON Schema定义。

### **文档使用指南 (必读)**

1. **首次接手任务** → **必须**按顺序阅读：本手册 (CLAUDE.md) → docs/INDEX.md → README.md → docs/PROJECT_PROGRESS.md。
2. **查找任何文档** → **首先**访问 docs/INDEX.md 文档导航中心，使用表格化索引快速定位所需文档。
3. **开始日常任务前** → **必须**检查 docs/PROJECT_PROGRESS.md 的最新更新，了解当前项目状态。
4. **实现新Agent前** → **🔥 必须**阅读 docs/BACKEND_README.md 和 PROJECT_PROGRESS.md 中的"AGENT_1开发经验总结"！
5. **理解架构设计** → **必须**参考 README.md 的相关章节。
6. **查询历史决策** → (如果适用) 查询项目知识库或历史记录，理解特定组件的设计背景。

### **快速导航提示**

```jsx
# 文档导航中心（查找任何文档前必看）
Read: docs/INDEX.md

# 核心必读：项目架构蓝图与所有规范
Read: README.md

# Agent开发指南
Read: docs/BACKEND_README.md

# 项目进度与状态
Read: docs/PROJECT_PROGRESS.md

# 查看工作流定义
Read: workflows.json

# 查看特定构件的Schema
Read: schemas/CreativeBrief_v1.0.json
```

---

## **第二部分：核心理念与设计哲学 (Core Philosophy & Principles)**

### **2.1 HELIX 核心架构范式**

- **状态驱动与异步轮询:** 整个系统由一个自定义的 asyncio **编排器**驱动。编排器通过轮询中心数据库（PostgreSQL）中的 tasks 表来推进工作流，而非依赖消息队列。
- **PostgreSQL 作为唯一真理之源:** 系统的所有状态（作业、任务、构件）都持久化在PostgreSQL中。不存在内存状态或外部缓存（如Redis）作为主要状态存储。
- **无状态代理 (Stateless Agents):** 所有Agent都是无状态的工作者，它们从数据库接收任务，执行逻辑，并将结果写回数据库。

### **2.2 角色定位与协作模式**

- **人类开发者 = 领航员 (Navigator):** 负责架构决策、任务分解、上下文提供、代码审查和质量把控。
- **Claude AI = 驾驶员 (Driver):** 负责根据领航员提供的精确指令和上下文，生成符合架构规范和编码标准的代码。

---

## **第三部分：架构蓝图与技术规范 (Blueprint & Technical Specs)**

### **3.1 技术栈速查 (Tech Stack Quick-Reference)**

- **后端框架:** **FastAPI** (用于API入口)
- **核心逻辑:** **自定义 Python asyncio 脚本** (用于编排器和Agents)
- **数据验证:** **Pydantic**
- **数据库:** **PostgreSQL**
- **异步DB驱动:** **asyncpg**
- **AI模型交互:** **直接使用供应商SDK (e.g., openai, anthropic)**

### **3.2 核心数据模型 (Core Data Models)**

参考 README.md 第4.4节的数据库核心Schema定义，主要包括 jobs, tasks, agent_prompts 表。

### **3.3 API契约 (API Contracts)**

API的请求和响应体**必须**使用Pydantic模型进行定义和验证。

Generated python

```jsx
      # 示例：api/schemas.py
from pydantic import BaseModel, Field

class CreateJobRequest(BaseModel):
    chat_input: str = Field(..., min_length=10, description="用户的原始创意需求")
    session_id: str | None = None

class JobResponse(BaseModel):
    job_id: int
    status: str
```

### **3.4 Agent任务指令单格式 (Agent Task DTOs)**

Agent的输入输出**必须**遵循README.md中定义的统一接口协议，并在代码中通过Python的TypedDict或Pydantic模型来体现。

Generated python

```jsx
      # 示例：sdk/schemas.py
from typing import TypedDict, List, Dict, Any

class ArtifactReference(TypedDict):
    name: str
    source_task_id: int

class TaskInputData(TypedDict):
    artifacts: List[ArtifactReference]
    params: Dict[str, Any]

class TaskOutputData(TypedDict):
    schema_id: str
    payload: Dict[str, Any]
```

---

## **第四部分：标准作业程序 (Standard Operating Procedure - SOP)**

### **4.1 AI结对编程四步标准流程**

1. **任务分解 (Task Decomposition):** 
    - **负责人:** **人类开发者 (领航员)**
    - **描述:** 将一个功能点（Epic）分解为原子化的微任务。为确保 Pydantic 模型与 JSON Schema 文件 100% 同步，所有新数据构件的定义**必须**采纳 "**Pydantic优先**" 的原则。
        
        ```jsx
        ## 示例：实现一个新的数据构件
        - [ ] 1. **Pydantic优先:** 在 `sdk/schemas.py` 或相关模块中，使用 Pydantic 定义新的数据模型，并添加所有必要的验证规则。
        - [ ] 2. **自动生成Schema:** (由AI执行) 编写或调用一个脚本，利用 `YourModel.model_json_schema()` 方法，从Pydantic模型自动生成或更新对应的 `schemas/YourModel_v1.0.json` 文件。
        - [ ] 3. **集成与使用:** 在项目的其他部分（如Agent逻辑、API端点）中使用新定义的Pydantic模型。
        ```
        
2. **上下文打包 (Context Packaging):** 人类开发者使用标准模板，为AI提供完整、无歧义的上下文。为尊重AI的上下文窗口限制并提高处理效率，打包上下文时**必须**遵循以下原则：
    - **核心优先:** 优先提供与任务直接相关的**核心定义**、**类名**、**函数签名**和**类型提示**。
    - **按需提供细节:** 只有当函数的**内部实现**是本次任务修改的关键时，才提供完整的代码片段。
    - **避免冗余:** 对于稳定且无需修改的通用库（如 agent_sdk.py 的大部分内容），只需在提示中假定其存在并可调用即可，无需粘贴完整代码。
3. **代码生成与整合 (Code Generation & Integration):** AI生成代码，AI开发者审查、集成并处理依赖。由**Claude AI（驾驶员）** 生成代码，并由**人类开发者（领航员）** 负责审查、集成和处理依赖。任务粒度异常处理协议：
    - **AI职责:** 如果AI根据任务描述，判断其实现无法在 **50-70行** 代码的建议限制内完成，AI**必须**停止生成代码。
    - **AI标准回应:** AI应立即向领航员回应，使用以下标准话术：
        
        "此任务可能需要超过建议的代码行数限制，请确认是否继续，或请提供更细粒度的任务分解。"
        
    - **领航员决策:** 领航员根据AI的反馈，决定是授权单次超限（并回复"请继续"），还是重新分解任务。
4. **测试反馈循环 (Testing & Feedback Loop):** 运行测试，将失败信息作为新上下文，请求AI修正，直至通过。
    - **领航员**运行相关测试（单元测试、集成测试、静态分析）。
    - 若测试失败，**领航员**将完整的错误信息、失败的测试用例和相关代码片段，作为新的上下文打包。
    - **领航员**向AI发出修正指令，例如："测试失败，请根据以下错误信息修正之前的代码。"
    - 循环此过程，直至所有相关测试通过。

### **4.2 上下文打包模板 (Context Packaging Template)**

Generated plaintext

```jsx
### INSTRUCTION ###
[清晰、精确、原子化的任务描述。例如：请为 `CreativeDirectorAgent` 类实现 `run` 方法，该方法需要异步执行，并使用 Pydantic 模型 `CreativeBriefInput` 来验证输入参数。]

### README.md QUOTE ###
[从README.md中摘录最相关的核心原则或架构规范。例如："P7: 构件的自描述与验证 (Artifact Self-Description and Validation): 每个构件（Artifact）必须是自描述和可验证的..."]

### TECHNICAL SPEC SNIPPET ###
[粘贴最直接相关的技术规范。例如：`input_data` 和 `output_data` 的协议定义，或目标函数的签名。]
# 示例:
# from sdk.agent_sdk import BaseAgent
# class CreativeDirectorAgent(BaseAgent):
#     async def run(self, inputs: CreativeBriefInput) -> CreativeBriefOutput:
#         # TODO: Implement logic here

### RELEVANT CODE SNIPPETS ###
[根据"上下文经济性原则"，仅粘贴最核心、最相关的现有代码片段。如果无，则注明 "N/A"。]
```

---

### **4.3 特殊流程：处理工作流定义变更**

当开发任务涉及**新增、删除或重排 Agent** 时，该任务的分解清单中**必须**包含一个明确的步骤，用于处理对核心工作流定义的修改。

```jsx
## 示例：引入新的 AGENT_6 (UX Writer)
- [ ] 1. 在 `agents/ux_writer.py` 文件中实现 `UXWriterAgent` 的核心逻辑。
- [ ] 2. ... (其他相关任务，如定义其构件Schema等) ...
- [ ] 3. **【工作流变更】提议对 `workflows.json` 的修改内容，以将 `AGENT_6` 插入到 `AGENT_3` 和 `AGENT_4` 之间。**
```

**AI 职责:** 在执行此类任务时，AI应在最后一步明确产出对 workflows.json 的建议修改方案，通常是以一个清晰的 diff 或完整的 JSON 对象形式提供。

## **第五部分：质量保证与治理 (Quality Assurance & Governance)**

### **5.1 强制检查清单 (Post-Generation Checklist)**

### ✅ **代码质量检查**

- 是否符合 **Python 3.10+** 语法和类型提示 (Type Hinting)？
- 是否遵循 **PEP 8** 代码风格指南？
- 是否使用了 **Pydantic** 模型进行数据输入/输出的定义和验证？
- 是否包含适当的 try...except 错误处理？
- 所有数据库交互是否**严格通过 agent_sdk.py** 中的函数进行？

### ✅ **架构一致性检查**

- 文件路径是否符合 README.md 第7节定义的项目结构？
- 命名是否遵循项目约定 (e.g., ClassName, variable_name)？
- 是否正确实现了基于 asyncio 的异步操作 (async/await)？
- 是否遵循了 README.md 中定义的"构件引用协议"？

### **5.2 禁止行为清单 (Prohibited Actions)**

- **绝对禁止:**
    - 绕过 agent_sdk.py 直接执行数据库查询。
    - 在Agent内部维护可变的状态（必须是无状态的）。
    - 一次性生成超过50-70行的复杂函数或类。
    - **在收到可能超限的复杂任务时，不发出警告而直接生成超长代码。**
    - 忽略 README.md 中定义的任何核心原则。
    - **硬编码网络端口号（严格禁止）。**
- **需要谨慎:**
    - 引入新的第三方依赖库 (必须在提示中明确提出并说明理由)。
    - 修改共享的SDK或核心协议 (必须作为一个独立的、明确的任务来执行)。

---

## **第六部分：动态端口管理标准操作规程 (Dynamic Port Management SOP)**

**重要说明:** 本节为**强制执行**的AI操作规程。在共享开发环境中，网络端口管理是系统可靠性的关键。

### **6.1 核心指令与背景 (Core Directive & Context)**

#### **主要目标**
在共享虚拟机环境中，通过动态分配端口可靠启动HELIX系统的所有网络服务。

#### **环境约束**
- **共享资源:** 网络端口是有限的共享资源，端口冲突是常态。
- **严格禁止:** 硬编码端口号。所有服务监听端口必须动态分配。
- **P4原则:** 必须实现幂等性和可恢复性，支持自动重试和故障恢复。

### **6.2 核心工具：端口发现脚本 (Core Tool: Port Discovery)**

#### **工具路径:** `./scripts/find-port.sh`

#### **工具职责:**
- 在指定范围内扫描并返回单个可用TCP端口号
- 支持服务类型分片（API: 8000-8099, Orchestrator: 8100-8199, Worker: 8200-8299）
- 随机化端口选择以减少竞态条件

#### **使用方法:**
```bash
# 查找API服务端口
./scripts/find-port.sh  # 默认API范围 8000-8099

# 查找特定服务类型端口
./scripts/find-port.sh 8100 8199 orchestrator

# 查找自定义范围端口
./scripts/find-port.sh 8000 9000 api
```

#### **工具验证:**
如果 `./scripts/find-port.sh` 不存在，**必须立即创建**：

```bash
#!/bin/bash
# Dynamic Port Discovery for HELIX System

START_PORT=${1:-8000}
END_PORT=${2:-9000}
MAX_ATTEMPTS=50
SERVICE_TYPE=${3:-"api"}

# Service-specific port ranges (only if no explicit range provided)
if [ -z "$1" ] && [ -z "$2" ]; then
    case $SERVICE_TYPE in
        "api")
            START_PORT=8000
            END_PORT=8099
            ;;
        "orchestrator")
            START_PORT=8100
            END_PORT=8199
            ;;
        "worker")
            START_PORT=8200
            END_PORT=8299
            ;;
    esac
fi

for (( i=0; i<MAX_ATTEMPTS; i++ )); do
    PORT=$(( RANDOM % (END_PORT - START_PORT + 1) + START_PORT ))
    
    if ! ss -tulpn | grep -q ":$PORT " && \
       ! netstat -tuln 2>/dev/null | grep -q ":$PORT " && \
       ! lsof -i :$PORT >/dev/null 2>&1; then
        echo $PORT
        exit 0
    fi
    sleep 0.02
done

echo "Error: Could not find available port in range $START_PORT-$END_PORT" >&2
exit 1
```

### **6.3 标准启动工作流 (Mandatory Launch Sequence)**

当AI需要启动任何HELIX网络服务时，**必须严格按以下步骤执行**：

#### **步骤1: 工具验证**
```bash
# 检查端口发现脚本
if [ ! -f "./scripts/find-port.sh" ]; then
    echo "ERROR: Port discovery script missing"
    exit 1
fi

# 确保执行权限
chmod +x ./scripts/find-port.sh
```

#### **步骤2: 端口发现**
```bash
# 发现可用端口
AVAILABLE_PORT=$(./scripts/find-port.sh)

# 验证输出
if [[ ! "$AVAILABLE_PORT" =~ ^[0-9]+$ ]]; then
    echo "ERROR: Invalid port number: $AVAILABLE_PORT"
    exit 1
fi

echo "Discovered available port: $AVAILABLE_PORT"
```

#### **步骤3: 配置更新**
```bash
# 确保环境文件存在
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# 更新端口配置（示例：API_PORT）
sed -i "s/^API_PORT=.*/API_PORT=${AVAILABLE_PORT}/" .env

# 验证更新
grep "API_PORT=${AVAILABLE_PORT}" .env
```

#### **步骤4: 服务启动**
```bash
# 使用项目标准启动命令
python start_system.py
# 或
python scripts/start-with-dynamic-ports.py
```

#### **步骤5: 启动确认**
```bash
# 等待服务就绪（必要时）
sleep 2

# 验证服务健康状态
curl -f "http://localhost:${AVAILABLE_PORT}/api/v1/health" || exit 1

echo "SUCCESS: HELIX service is running on port ${AVAILABLE_PORT}"
echo "Frontend: http://localhost:${AVAILABLE_PORT}"
echo "API Docs: http://localhost:${AVAILABLE_PORT}/docs"
```

### **6.4 故障恢复协议 (Contingency Protocol)**

#### **"Address already in use" 错误处理**

如果步骤4失败并出现端口冲突错误，**不要终止操作**。这是可恢复的竞态条件。

**自动恢复流程:**
```bash
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "Attempt $((RETRY_COUNT + 1)) of $MAX_RETRIES"
    
    # 重新发现端口
    AVAILABLE_PORT=$(./scripts/find-port.sh)
    
    # 更新配置
    sed -i "s/^API_PORT=.*/API_PORT=${AVAILABLE_PORT}/" .env
    
    # 尝试启动
    if python start_system.py; then
        echo "SUCCESS: Service started on port ${AVAILABLE_PORT}"
        break
    else
        echo "RETRY: Port conflict detected, trying again..."
        RETRY_COUNT=$((RETRY_COUNT + 1))
        sleep 1
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: Failed to start service after $MAX_RETRIES attempts"
    exit 1
fi
```

### **6.5 特殊配置要求 (Special Configuration Requirements)**

#### **数据库端口策略**
- **PostgreSQL端口必须保持固定** (默认5432)
- 不对数据库端口使用动态分配
- 原因：数据库连接稳定性和配置复杂性

#### **多服务协调**
当启动多个服务时：
```bash
# 为不同服务分配不同范围的端口
API_PORT=$(./scripts/find-port.sh 8000 8099 api)
ORCHESTRATOR_PORT=$(./scripts/find-port.sh 8100 8199 orchestrator)
WORKER_PORT=$(./scripts/find-port.sh 8200 8299 worker)

# 更新各自的环境变量
sed -i "s/^API_PORT=.*/API_PORT=${API_PORT}/" .env
sed -i "s/^ORCHESTRATOR_PORT=.*/ORCHESTRATOR_PORT=${ORCHESTRATOR_PORT}/" .env
sed -i "s/^WORKER_PORT=.*/WORKER_PORT=${WORKER_PORT}/" .env
```

#### **Docker环境处理**
对于Docker部署，使用预配置的动态配置：
```bash
# 使用动态端口Docker配置
docker-compose -f config/docker-compose.dynamic.yml up -d

# 访问稳定的反向代理端点
echo "Docker deployment accessible at: http://localhost:8080"
```

### **6.6 AI执行检查清单 (AI Execution Checklist)**

在执行任何端口相关任务时，AI必须验证：

- [ ] **工具存在性检查:** `./scripts/find-port.sh` 已存在且可执行
- [ ] **端口发现验证:** 脚本返回有效的数字端口
- [ ] **配置文件更新:** `.env` 文件已正确更新端口配置
- [ ] **服务启动验证:** 服务成功启动并响应健康检查
- [ ] **最终报告:** 明确报告最终使用的端口号
- [ ] **错误处理:** 实现了竞态条件的自动重试机制

### **6.7 强制报告格式 (Mandatory Reporting Format)**

服务成功启动后，AI必须提供标准化报告：

```
✅ HELIX SYSTEM STARTUP REPORT
==================================================
🌐 API Server: http://localhost:8023
📚 API Documentation: http://localhost:8023/docs
🔍 Health Check: http://localhost:8023/api/v1/health
📊 Database: localhost:5432 (Fixed)
==================================================
🕒 Startup Time: 15.3 seconds
🔄 Port Discovery Attempts: 1
✨ Status: All services operational
```

**故障报告格式:**
```
❌ HELIX SYSTEM STARTUP FAILED
==================================================
🚨 Error: [具体错误信息]
🔄 Retry Attempts: 3/3
💡 Suggested Action: [建议的解决步骤]
📋 Debug Info: [端口扫描结果等]
==================================================
```

---

## **第七部分：SSH安全与系统完整性保护 (SSH Safety & System Integrity)**

**重要说明:** 本节为**强制执行**的系统安全规程。在共享开发环境中，SSH连接安全是系统可用性的生命线。

### **7.1 SSH锁定风险防护协议 (SSH Lockout Prevention Protocol)**

#### **核心原则**
- **SSH端口22绝对保护:** 任何自动化脚本都不得操作端口22相关进程
- **进程终止前验证:** 所有 `kill`/`pkill` 命令必须经过SSH安全检查
- **白名单机制:** 只允许终止明确标识的HELIX相关进程
- **影响评估:** 任何系统操作前必须评估对SSH连接的潜在影响

#### **强制安全检查清单 (Mandatory Safety Checklist)**

在执行任何进程管理命令前，AI必须验证：

- [ ] **SSH服务状态检查:** `netstat -tuln | grep :22` 确认SSH服务正常运行
- [ ] **进程精确匹配:** 使用完整进程名而非模糊匹配模式
- [ ] **PID精确验证:** 优先使用具体PID而非进程名模式匹配
- [ ] **影响范围评估:** 确认操作仅影响HELIX应用，不涉及系统关键服务
- [ ] **回滚方案准备:** 确保操作可逆，有明确的恢复步骤

#### **安全的进程管理命令规范**

**✅ 推荐的安全命令:**
```bash
# 1. 优先使用具体PID (最安全)
kill -TERM 30022

# 2. 精确匹配HELIX进程
pkill -f "python.*start_system.py.*aiagent"

# 3. 限定工作目录的进程查找
ps aux | grep "/home/canoezhang/Projects/aiagent.*python.*start_system.py" | grep -v grep
```

**❌ 禁止的危险命令:**
```bash
# 危险：过于宽泛的Python进程匹配
pkill python
pkill -f python

# 危险：批量终止未验证的进程
kill -9 $(ps aux | grep python | awk '{print $2}')

# 危险：使用通配符的进程匹配
pkill -f "python.*"
```

### **7.2 SSH安全集成到动态端口管理SOP**

#### **增强的步骤4: 服务启动 (SSH-Safe Version)**
```bash
# === SSH安全检查 ===
echo "Performing SSH safety verification..."
if ! netstat -tuln | grep -q ":22 "; then
    echo "🚨 CRITICAL: SSH service not detected on port 22"
    echo "🛑 ABORT: Cannot proceed with system operations without SSH safety"
    exit 1
fi
echo "✅ SSH service confirmed active on port 22"

# === 安全启动 ===
python start_system.py
```

#### **增强的紧急恢复协议 (SSH-Safe Emergency Recovery)**
```bash
#!/bin/bash
# HELIX Emergency Recovery with SSH Protection

echo "🔒 Initiating SSH-Safe Emergency Recovery..."

# === 第一步：SSH安全检查 ===
echo "Step 1: Verifying SSH service integrity..."
SSH_CHECK=$(netstat -tuln | grep ":22 " | wc -l)
if [ "$SSH_CHECK" -eq 0 ]; then
    echo "🚨 CRITICAL: SSH service not running on port 22"
    echo "🛠️  Manual intervention required - DO NOT PROCEED"
    echo "   → Check SSH daemon: systemctl status sshd"
    echo "   → Manual restart: sudo systemctl restart sshd"
    exit 1
fi
echo "✅ SSH service confirmed safe"

# === 第二步：精确HELIX进程识别 ===
echo "Step 2: Identifying HELIX processes safely..."
HELIX_PIDS=$(ps aux | grep -E "/home/canoezhang/Projects/aiagent.*python.*start_system.py" | grep -v grep | awk '{print $2}')

if [ -n "$HELIX_PIDS" ]; then
    echo "📋 Found HELIX processes: $HELIX_PIDS"
    echo "🔍 Verifying each process..."
    
    for PID in $HELIX_PIDS; do
        PROC_CMD=$(ps -p "$PID" -o cmd= 2>/dev/null)
        if echo "$PROC_CMD" | grep -q "start_system.py"; then
            echo "✅ Verified HELIX process $PID: $PROC_CMD"
            echo "🛑 Gracefully terminating process $PID..."
            kill -TERM "$PID"
        else
            echo "⚠️  Skipping non-HELIX process $PID"
        fi
    done
else
    echo "ℹ️  No HELIX processes found running"
fi

# === 第三步：端口清理与重启 ===
echo "Step 3: Port cleanup and restart..."
./scripts/find-port.sh
./scripts/quick-start-demo.sh

echo "✅ SSH-Safe Emergency Recovery completed"
```

### **7.3 AI执行强制协议 (AI Mandatory Protocol)**

#### **进程管理任务的AI检查清单**

当AI需要执行任何涉及进程管理的任务时，**必须严格按以下顺序执行**：

1. **SSH安全声明:** 明确声明"执行SSH安全检查"
2. **安全验证:** 运行 `netstat -tuln | grep :22` 确认SSH服务状态
3. **精确识别:** 使用完整路径和进程名精确识别目标进程
4. **影响评估:** 评估操作对系统关键服务的影响
5. **安全执行:** 使用推荐的安全命令执行操作
6. **结果验证:** 确认操作成功且SSH服务依然正常

#### **AI标准安全报告格式**

```
🔒 SSH SAFETY VERIFICATION REPORT
==================================================
✅ SSH Status: Active on port 22
🎯 Target Process: PID 30022 (python start_system.py)
🔍 Verification: Process confirmed as HELIX application  
⚡ Action: Graceful termination (SIGTERM)
✅ Result: Process terminated successfully
✅ SSH Status Post-Action: Still active on port 22
==================================================
```

### **7.4 系统级安全工具集成**

#### **创建专用安全脚本: `scripts/ssh-safe-manager.sh`**

```bash
#!/bin/bash
# HELIX SSH-Safe Process Manager
# Prevents accidental SSH service termination

SSH_SAFETY_CHECK() {
    if ! netstat -tuln | grep -q ":22 "; then
        echo "🚨 CRITICAL: SSH not running on port 22"
        return 1
    fi
    echo "✅ SSH service verified active"
    return 0
}

SAFE_KILL_HELIX() {
    local TARGET_PID=$1
    
    # 验证SSH安全
    SSH_SAFETY_CHECK || {
        echo "🛑 ABORT: Cannot proceed without SSH safety"
        exit 1
    }
    
    # 验证PID
    if [ -z "$TARGET_PID" ]; then
        echo "❌ Usage: SAFE_KILL_HELIX <PID>"
        return 1
    fi
    
    # 验证这是HELIX进程
    local PROC_CMD=$(ps -p "$TARGET_PID" -o cmd= 2>/dev/null)
    if echo "$PROC_CMD" | grep -q "start_system.py"; then
        echo "✅ Verified HELIX process $TARGET_PID"
        echo "🛑 Safely terminating..."
        kill -TERM "$TARGET_PID"
        
        # 再次验证SSH安全
        SSH_SAFETY_CHECK || {
            echo "🚨 WARNING: SSH status changed after operation!"
            return 1
        }
        
        echo "✅ Operation completed safely"
    else
        echo "❌ ERROR: PID $TARGET_PID is not a HELIX process"
        echo "   Process: $PROC_CMD"
        return 1
    fi
}

# 导出函数以供其他脚本使用
export -f SSH_SAFETY_CHECK SAFE_KILL_HELIX
```

---

## **第八部分：AI驱动问题检测与响应SOP (AI-Driven Problem Detection & Response SOP)**

**重要说明:** 基于四模型协作分析HELIX项目的NULL处理bug经验，建立了一套信号驱动的自动化问题检测和响应系统。

### **8.1 问题分类与信号映射 (Problem Classification & Signal Mapping)**

基于四模型分析（Gemini thinkdeep + Flash codereview + Flash chat + DeepSeek thinkdeep）识别的关键问题类型：

#### **技术债务类问题**
1. **NULL语义处理错误** - SQL三值逻辑理解缺失
2. **字段职责混乱** - error_log同时承担错误记录和状态标记  
3. **架构模式落后** - 轮询替代事件驱动的性能问题
4. **状态机设计不当** - 缺乏明确的任务生命周期管理

#### **运维可靠性问题**
5. **并发竞态条件** - 多实例处理导致数据不一致
6. **资源泄漏风险** - 无限循环导致系统资源耗尽
7. **监控盲区** - 僵尸任务、重复处理无法及时发现
8. **故障恢复机制缺失** - 缺乏熔断器、重试机制

#### **系统工程问题**
9. **可观测性不足** - 缺乏结构化日志、指标、追踪
10. **测试覆盖盲区** - SQL边界条件、并发场景未覆盖
11. **错误分类混乱** - 业务错误vs系统错误处理一致化
12. **性能隐患** - LIKE查询、全表扫描等性能陷阱

### **8.2 信号检测脚本集 (Signal Detection Scripts)**

AI可以根据具体情况自动调用以下专用检测和处理脚本：

#### **检测脚本 (Detection Scripts)**

| 脚本名称 | 用途 | 触发条件 | 输出格式 |
|---------|------|----------|----------|
| `scripts/detect-zombie-tasks.sh` | 检测僵尸任务 | 用户报告重复处理问题 | JSON: zombie_tasks数组 |
| `scripts/check-system-health.sh` | 系统健康检查 | 定期检查或性能问题 | JSON: 完整健康报告 |
| `scripts/analyze-performance-issues.sh` | 性能瓶颈分析 | 响应时间慢/资源使用高 | JSON: 性能分析报告 |
| `scripts/check-api-compliance.sh` | API接口规范检查 | API问题报告/上线前检查 | JSON: 完整合规性报告 |

#### **修复脚本 (Fix Scripts)**

| 脚本名称 | 用途 | 使用场景 | 安全级别 |
|---------|------|----------|----------|
| `scripts/fix-zombie-tasks.sh` | 修复僵尸任务 | 检测到僵尸任务后 | SSH安全 |
| `scripts/emergency-recovery.sh` | 紧急恢复 | 系统无响应/严重故障 | SSH安全 + 强制模式 |

### **8.3 AI自动调用决策树 (AI Auto-Invocation Decision Tree)**

当用户报告以下问题时，AI应自动调用相应脚本：

```
用户报告: "任务一直在重复处理"
├── 自动调用: ./scripts/detect-zombie-tasks.sh
├── 如果检测到僵尸任务
│   ├── 询问用户: 修复方式 (mark_zombie/force_complete/restart_job)
│   └── 执行: ./scripts/fix-zombie-tasks.sh [task_id] [action]
└── 如果未检测到
    └── 调用: ./scripts/check-system-health.sh --format json

用户报告: "系统响应很慢"
├── 自动调用: ./scripts/analyze-performance-issues.sh
├── 分析结果如包含慢查询
│   └── 建议: 优化LIKE查询和索引
└── 分析结果如包含资源耗尽
    └── 调用: ./scripts/check-system-health.sh

用户报告: "系统完全卡死"
├── 询问确认: 是否需要紧急重启
├── 如果确认
│   └── 执行: ./scripts/emergency-recovery.sh --action restart
└── 如果不确认
    └── 执行: ./scripts/check-system-health.sh

用户报告: "API接口有问题" / "上线前检查"
├── 自动调用: ./scripts/check-api-compliance.sh --format json
├── 如果发现CRITICAL级别问题
│   ├── 立即报告: 安全风险或语法错误
│   └── 建议: 修复后再次检查
├── 如果发现HIGH级别问题
│   ├── 报告: 需要尽快修复的问题
│   └── 提供: 具体修复建议
└── 如果仅有MEDIUM/LOW问题
    └── 提供: 改进建议清单
```

### **8.4 脚本调用示例 (Script Invocation Examples)**

#### **示例1: 检测和修复僵尸任务**
```bash
# AI自动调用检测
./scripts/detect-zombie-tasks.sh 5 3

# 如果发现僵尸任务，AI根据用户选择执行修复
./scripts/fix-zombie-tasks.sh 109039 mark_zombie
```

#### **示例2: 系统健康检查**
```bash
# 获取JSON格式的健康报告
./scripts/check-system-health.sh --format json

# 设置自定义阈值
./scripts/check-system-health.sh --threshold-cpu 90 --threshold-memory 85
```

#### **示例3: 性能问题分析**
```bash
# 分析过去60分钟的性能问题
./scripts/analyze-performance-issues.sh --time-window 60

# 设置慢查询阈值为1秒
./scripts/analyze-performance-issues.sh --slow-query-threshold 1000
```

#### **示例4: 紧急恢复**
```bash
# 安全重启系统
./scripts/emergency-recovery.sh --action restart

# 强制模式（用于卡死情况）
./scripts/emergency-recovery.sh --action restart --force

# 仅清理不重启
./scripts/emergency-recovery.sh --action cleanup
```

#### **示例5: API接口规范检查**
```bash
# 完整API合规性检查（JSON格式）
./scripts/check-api-compliance.sh --format json

# 仅检查严重问题
./scripts/check-api-compliance.sh --severity critical

# 人类可读格式报告
./scripts/check-api-compliance.sh --format human

# 指定API端点
./scripts/check-api-compliance.sh --host localhost --port 8043
```

### **8.5 AI行为准则 (AI Behavior Guidelines)**

#### **自动执行 (Auto-Execute)**
- 只读检测脚本（detect-*, check-*, analyze-*）
- 系统状态查询
- 健康检查报告

#### **询问确认 (Ask Confirmation)**
- 修复操作（fix-zombie-tasks.sh）
- 系统重启（emergency-recovery.sh --action restart）
- 数据库清理操作

#### **必须人工授权 (Require Human Authorization)**
- 强制模式操作（--force标志）
- 删除数据操作
- 改变系统配置

### **8.6 输出解读指南 (Output Interpretation Guide)**

#### **僵尸任务检测输出**
```json
{
  "zombie_tasks": [
    {
      "task_id": 109039,
      "agent_id": "AGENT_2", 
      "processing_count": 5,
      "severity": "P1"
    }
  ]
}
```
**AI应解读为**: "发现任务109039被AGENT_2重复处理5次，这是P1级别的僵尸任务问题"

#### **系统健康检查输出**
```json
{
  "overall_status": "warning",
  "alerts": ["High CPU usage: 85%"],
  "system": {"cpu_usage": 85, "memory_usage": 65}
}
```
**AI应解读为**: "系统状态警告，CPU使用率85%超过阈值，需要注意资源使用"

### **8.7 脚本维护 (Script Maintenance)**

#### **权限设置**
```bash
# 确保所有检测脚本可执行
chmod +x scripts/detect-*.sh scripts/check-*.sh scripts/analyze-*.sh

# 确保修复脚本可执行但需谨慎使用
chmod +x scripts/fix-*.sh scripts/emergency-*.sh
```

#### **日志记录**
所有脚本都会在stderr输出人类可读的日志，在stdout输出JSON格式的结果，便于AI解析和用户查看。

---

## **第九部分：项目管理与多AI协作 (Project Management & Multi-AI Collaboration)**

**重要说明:** 为确保项目进度连续性和多AI协作的一致性，以下规范为**强制执行**。

### **7.1 开发任务全周期规范 (Full Lifecycle Protocol)**

### **🔍 开发任务前置检查 (Pre-Task Checklist)**

- [ ]  **读取 PROJECT_PROGRESS.md:** 了解项目当前状态、最近的变更和下一步的优先级。
- [ ]  **参考 README.md:** 再次确认任务相关部分的架构蓝图和设计原则。
- [ ]  **(如果适用) 查询历史决策:** 检索相关组件的历史设计讨论和实现细节。
- [ ]  **进行任务规划:** 使用思维导图或列表，对即将执行的任务进行充分的规划和风险评估。

### **📝 开发任务后置更新 (Post-Task Checklist)**

- [ ]  **更新 PROJECT_PROGRESS.md:** 任务完成后，**必须**在此文件中记录重要进展和里程碑的完成状态。
- [ ]  **(如果适用) 同步知识库:** 将新的技术决策、架构变更或重要组件的状态记录到项目知识库中。
- [ ]  **验证系统完整性:** 确保所做变更不影响现有架构的一致性，并通过相关测试。

### **7.2 多AI协作协议 (Multi-AI Collaboration Protocol)**

### **数据一致性原则**

- **PROJECT_PROGRESS.md 作为状态快照:** 任何AI开始工作前，都应视此文件为项目当前状态的快照。
- **强制同步机制:** 所有影响项目范围或进度的重要变更，**必须**在任务结束时反映在 PROJECT_PROGRESS.md 的更新中。
- **决策可追溯性:** 所有重大的技术决策都应被固化到 README.md 的更新中，确保可追溯。

### **标准协作流程**

```jsx
1. 新AI会话接手任务:
   → 读取 PROJECT_PROGRESS.md 了解整体状态。
   → 读取 README.md 了解架构蓝图。
   → (如果适用) 查询知识库获取详细组件信息。
   → 进行任务规划。

2. 开发过程中:
   → 严格遵循 README.md 和本手册定义的架构模式和代码约定。
   → 保持与已有组件的接口兼容性。

3. 任务完成后:
   → 运行相关测试确保系统稳定性。
   → 更新 PROJECT_PROGRESS.md 记录进展。
```

### **冲突解决机制**

- **优先级顺序:** README.md (架构与规范) > PROJECT_PROGRESS.md (当前状态与优先级) > 代码注释 (具体实现细节)。
- **争议解决:** 当实现与 README.md 冲突时，必须以 README.md 为准。如有必要，应先发起一个修改 README.md 的任务。

### **7.3 项目管理目标**

- **进度透明化:** 任何协作者能在5分钟内通过阅读文档了解项目全貌。
- **决策可追溯:** 所有核心架构决策都记录在 README.md 的版本历史中。
- **协作高效化:** 多AI协作的开销（用于同步上下文的时间）应低于总开发时间的10%。

---

## **第十部分：文档管理与目录结构规范 (Documentation & Directory Standards)**

### **10.1 文档导航系统**

Project HELIX 采用企业级文档管理系统，所有文档查找都应从 **docs/INDEX.md** 开始：

- **📚 docs/INDEX.md** - 文档导航中心，包含：
  - 表格化的文档分类（快速开始、架构设计、开发指南等）
  - 重要性标记（🔥必读、⭐重要、🚨关键）
  - 受众和技能要求说明
  - 快速查找路径

### **10.2 临时文件管理规范**

项目使用标准化的 tmp/ 目录结构管理所有临时文件：

```
tmp/
├── debug/          # 🐛 调试脚本
├── utilities/      # 🛠️ 工具脚本
├── tests/          # 🧪 临时测试
├── logs/           # 📋 日志文件
└── archives/       # 📦 归档文件
```

**重要规则：**
- ✅ 所有临时文件必须放入 tmp/ 相应子目录
- ✅ tmp/ 目录已添加到 .gitignore，不会污染版本控制
- ✅ 定期清理过期文件，保持目录整洁
- ❌ 禁止在项目根目录存放临时文件

### **10.3 文档更新协议**

当添加新文档或功能时：
1. **更新 docs/INDEX.md** - 添加新文档链接和描述
2. **更新 PROJECT_PROGRESS.md** - 记录开发进展
3. **更新 CLAUDE.md** - 如有新的AI协作规范

---

## **第十一部分：技术债务管理与渐进式改进 (Technical Debt Management & Progressive Enhancement)**

### **11.1 技术债务管理策略**

基于Project HELIX分布式系统失败案例的深度复盘，建立以下技术债务管理体系：

#### **债务分类与优先级**
| 债务类型 | 优先级 | 处理策略 | 时间分配 |
|----------|--------|----------|----------|
| **P0-系统稳定性** | 🔴 极高 | 立即修复 | 发现即处理 |
| **P1-性能瓶颈** | 🟠 高 | Sprint内解决 | 20%开发时间 |
| **P2-代码质量** | 🟡 中 | 渐进式改进 | 10%开发时间 |
| **P3-技术升级** | 🟢 低 | 长期规划 | 季度评估 |

#### **技术债务清单管理**
```yaml
# 在 docs/TECHNICAL_DEBT.yaml 中维护
technical_debts:
  - id: TD-001
    type: P1-性能瓶颈
    description: "PostgreSQL查询缺少索引导致Agent轮询缓慢"
    impact: "任务分配延迟3-5秒"
    effort: "2小时"
    solution: "添加 (status, agent_id) 复合索引"
    status: "待处理"
```

#### **童子军原则实施**
- **规则**: 每次修改代码时，让它比你发现时更好
- **实践**: 
  - 发现冗余代码 → 立即删除
  - 发现命名不当 → 立即重命名
  - 发现缺少注释 → 立即补充
- **限制**: 单次改动不超过20行，避免引入新风险

### **11.2 渐进式改进路径**

#### **短期改进（1-2 Sprints）**
```bash
# 1. 数据库优化
- [ ] 添加缺失索引
- [ ] 优化慢查询（>100ms）
- [ ] 实施连接池（PgBouncer）

# 2. 监控基础设施
- [ ] 结构化日志（JSON格式）
- [ ] 基础业务指标（Prometheus）
- [ ] 简单告警规则

# 3. 容器化
- [ ] Docker镜像标准化
- [ ] Docker Compose开发环境
- [ ] 环境变量管理
```

#### **中期改进（3-6个月）**
```bash
# 1. 代码质量提升
- [ ] 测试覆盖率达到80%
- [ ] API文档自动生成
- [ ] 代码审查流程标准化

# 2. 运维能力增强
- [ ] 自动化部署脚本
- [ ] 蓝绿部署支持
- [ ] 数据库备份自动化

# 3. 性能优化
- [ ] 缓存层引入（Redis）
- [ ] 异步任务队列
- [ ] API响应时间优化
```

#### **长期演进（6个月+）**
```bash
# 1. 架构演进评估
- [ ] 微服务拆分可行性分析
- [ ] 事件驱动架构探索
- [ ] 多租户支持设计

# 2. 扩展性准备
- [ ] 水平扩展方案设计
- [ ] 分布式事务处理
- [ ] 全球部署考虑
```

### **11.3 技术选型决策框架**

基于失败经验总结的决策框架：

#### **技术引入评估矩阵**
```
评估维度（每项1-5分）：
1. 业务价值匹配度
2. 团队技能匹配度
3. 运维复杂度（反向）
4. 社区成熟度
5. 迁移成本（反向）

决策规则：
- 总分 >= 20：强烈推荐
- 总分 15-19：谨慎引入
- 总分 < 15：不建议引入
```

#### **技术债务偿还ROI计算**
```
ROI = (预期收益 - 实施成本) / 实施成本

其中：
- 预期收益 = 性能提升价值 + 维护成本降低 + 开发效率提升
- 实施成本 = 开发时间 + 测试时间 + 部署风险 + 学习成本

ROI > 2：高优先级
ROI 1-2：中优先级
ROI < 1：低优先级
```

### **11.4 失败模式预防清单**

基于Project HELIX经验教训：

#### **开发阶段检查**
- [ ] Schema定义与代码实现一致性验证
- [ ] 数据库事务边界清晰定义
- [ ] 并发控制机制（锁、隔离级别）
- [ ] 错误处理与降级策略
- [ ] 资源清理（连接、文件句柄）

#### **部署阶段检查**
- [ ] SSH安全验证脚本
- [ ] 端口冲突检测
- [ ] 进程唯一性保证
- [ ] 日志轮转配置
- [ ] 监控指标验证

#### **运维阶段检查**
- [ ] 僵尸任务检测（每小时）
- [ ] 资源使用监控（CPU/内存/磁盘）
- [ ] 数据库连接池状态
- [ ] API响应时间趋势
- [ ] 错误日志分析

### **11.5 知识传承机制**

#### **经验文档化**
- **失败案例记录**: 在 `docs/POSTMORTEM/` 目录记录每个重大故障
- **最佳实践总结**: 在 `docs/BEST_PRACTICES/` 目录积累成功经验
- **架构决策记录**: 在 `docs/ADR/` (Architecture Decision Records) 记录重要决策

#### **定期复盘会议**
- **频率**: 每月一次技术债务评审
- **参与者**: 全体开发团队 + AI助手
- **产出**: 更新技术债务清单和优先级

---

**⚡ 记住：本手册是 Project HELIX 成功的生命线，每次AI协作都必须参考！**