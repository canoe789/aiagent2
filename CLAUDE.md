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
- [**PROJECT_PROGRESS.md**](https://www.google.com/url?sa=E&q=PROJECT_PROGRESS.md) - **项目航海日志。** 用于跟踪开发进度、当前状态、已完成的里程碑和下一步的优先级。
  > 🎓 **重要补充:** 包含"AGENT_1开发经验总结"，实现AGENT_3-5前**必读**！
- **workflows.json** - **流程定义文件。** 描述Agent的执行顺序和依赖关系。
- **schemas/ 目录** - **构件契约。** 存放所有构件（Artifacts）的JSON Schema定义。

### **文档使用指南 (必读)**

1. **首次接手任务** → **必须**按顺序阅读：本手册 (CLAUDE.md) → README.md → PROJECT_PROGRESS.md。
2. **开始日常任务前** → **必须**检查 PROJECT_PROGRESS.md 的最新更新，了解当前项目状态。
3. **实现新Agent前** → **🔥 必须**阅读 PROJECT_PROGRESS.md 中的"AGENT_1开发经验总结"！
4. **理解架构设计** → **必须**参考 README.md 的相关章节。
5. **查询历史决策** → (如果适用) 查询项目知识库或历史记录，理解特定组件的设计背景。

### **快速导航提示**

```jsx
      # 核心必读：项目架构蓝图与所有规范
Read: /path/to/project-helix/README.md

# 查看工作流定义
Read: /path/to/project-helix/workflows.json

# 查看特定构件的Schema
Read: /path/to/project-helix/schemas/CreativeBrief_v1.1.json
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
- **需要谨慎:**
    - 引入新的第三方依赖库 (必须在提示中明确提出并说明理由)。
    - 修改共享的SDK或核心协议 (必须作为一个独立的、明确的任务来执行)。

---

## **第六部分：项目管理与多AI协作 (Project Management & Multi-AI Collaboration)**

**重要说明:** 为确保项目进度连续性和多AI协作的一致性，以下规范为**强制执行**。

### **6.1 开发任务全周期规范 (Full Lifecycle Protocol)**

### **🔍 开发任务前置检查 (Pre-Task Checklist)**

- [ ]  **读取 PROJECT_PROGRESS.md:** 了解项目当前状态、最近的变更和下一步的优先级。
- [ ]  **参考 README.md:** 再次确认任务相关部分的架构蓝图和设计原则。
- [ ]  **(如果适用) 查询历史决策:** 检索相关组件的历史设计讨论和实现细节。
- [ ]  **进行任务规划:** 使用思维导图或列表，对即将执行的任务进行充分的规划和风险评估。

### **📝 开发任务后置更新 (Post-Task Checklist)**

- [ ]  **更新 PROJECT_PROGRESS.md:** 任务完成后，**必须**在此文件中记录重要进展和里程碑的完成状态。
- [ ]  **(如果适用) 同步知识库:** 将新的技术决策、架构变更或重要组件的状态记录到项目知识库中。
- [ ]  **验证系统完整性:** 确保所做变更不影响现有架构的一致性，并通过相关测试。

### **6.2 多AI协作协议 (Multi-AI Collaboration Protocol)**

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

### **6.3 项目管理目标**

- **进度透明化:** 任何协作者能在5分钟内通过阅读文档了解项目全貌。
- **决策可追溯:** 所有核心架构决策都记录在 README.md 的版本历史中。
- **协作高效化:** 多AI协作的开销（用于同步上下文的时间）应低于总开发时间的10%。

---

**⚡ 记住：本手册是 Project HELIX 成功的生命线，每次AI协作都必须参考！**