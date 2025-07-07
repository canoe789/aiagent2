# **Project HELIX: AI 驱动的自动化创意生产系统 - README (v2.0)**

**文档版本:** 2.0 (开发者就绪版)

**状态:** 开发就绪 (Ready for Development)

## **1. 概述与愿景 (Overview & Vision)**

### **1.1 项目使命**

Project HELIX 的使命是构建一个端到端的自动化系统，能够将用户的自然语言创意需求，转化为经过质量验证、符合工程标准、并具备视觉美感的前端代码。它旨在模拟一个高效、协作、且具备自我进化能力的顶尖数字创意团队。

### **1.2 问题陈述**

传统的从创意到代码的流程涉及多个角色，沟通成本高、周期长。此外，流程中任何环节的暂时性故障（如API超时、服务崩溃）都可能导致整个任务的永久性失败，造成巨大的沉没成本。

### **1.3 核心愿景**

我们旨在创建一个**"创意即代码"**的范式。HELIX 系统将自主完成从概念深化、视觉设计、代码生成、质量保证到最终交付的全过程。更重要的是，系统必须具备从失败中学习的能力，通过分析不合格的产出，递归地优化其自身的生产流程，从而实现持续的、自动化的性能提升。这一切都必须建立在一个健壮、可恢复、可观测的架构之上。

## **2. 核心设计原则 (Core Design Principles)**

所有系统组件的设计与实现都必须严格遵守以下原则：

- **P1: 代理架构 (Agentic Architecture):** 系统由一系列高度专业化、角色明确的自主 AI 代理（Agent）组成。
- **P2: 持久化状态接口 (Persistent State Interfaces):** 所有代理之间的通信必须通过一个中心化的、持久化的状态数据库进行。代理之间严禁直接调用。
- **P3: 外部化认知 (Externalized Cognition):** 代理的核心逻辑（即 Prompt）必须与执行引擎分离，存储于外部数据库中，并进行版本控制。
- **P4: 幂等与可恢复性 (Idempotence & Recoverability):** 系统的每个任务步骤必须设计为幂等的。任何失败的步骤都可以从上一个已知良好状态无缝恢复和重试（Retry）。
- **P5: 基于历史的自我改进 (History-Based Self-Improvement):** 系统的自我优化能力必须建立在完整、可靠、持久化的任务历史之上。
- **P6: 统一构件引用协议 (Unified Artifact-Reference Protocol):** 任务的输入是轻量级的"构件需求列表"，而非庞大的数据实体。
- **P7: 构件的自描述与验证 (Artifact Self-Description and Validation):** 每个构件（Artifact）必须是自描述和可验证的，将接口正确性从"文档约定"提升为"运行时保证"。

## **3. 系统架构 (System Architecture)**

### **3.1 架构范式：状态驱动的编排 (State-Driven Orchestration)**

HELIX 系统的核心是一个围绕中心状态数据库（PostgreSQL）构建的、由编排器驱动的异步工作流系统。

### **3.2 架构图**

```jsx
      graph TD
    subgraph Central State Database (PostgreSQL)
        DB[(作业与任务表 Jobs / Tasks)]
    end

    subgraph Orchestrator / Scheduler
        O[编排器]
    end

    subgraph Decoupled Agents (Stateless Workers)
        A1(AGENT_1: Creative)
        A2(AGENT_2: Visual)
        A3(AGENT_3: Frontend)
        A4(AGENT_4: QAQC)
        A5(AGENT_5: Meta-Optimizer)
    end

    User -- 1. 创建作业 (Job) --> DB
    O -- 2. 轮询新作业/任务 --> DB
    O -- 3. 分配任务 --> A1
    A1 -- 4. 读取任务输入 (引用) --> DB
    A1 -- 5. 写入任务输出 (构件) --> DB
    
    O -- (循环) --> A2
    A2 -- (同上) --> DB
    
    O -- (循环) --> A3
    A3 -- (同上) --> DB

    O -- (循环) --> A4
    A4 -- (同上, 写入验证结果) --> DB

    DB -- 6. 若验证失败，通知 --> O
    O -- 7. 分配优化任务 --> A5
    A5 -- 8. 读取完整的作业历史 --> DB
    A5 -- 9. 将优化后的Prompt写入Prompts表 --> DB

    style DB fill:#dbf4ff,stroke:#0077b6,stroke-width:2px;
    classDef agent fill:#cde4ff,stroke:#5a67d8,stroke-width:2px;
    class A1,A2,A3,A4,A5 agent;
```

### **3.3 代理角色与职责 (Agent Roles & Responsibilities)**

系统中的每个代理都是一个拥有明确使命的专家：

- **AGENT_1: 创意总监 (Creative Director):** 将用户模糊的自然语言需求，转化为结构化的、充满故事性的**《创作蓝图》**。
- **AGENT_2: 视觉总监 (Visual Director):** 基于《创作蓝图》，构想并产出多个风格迥异的**《视觉概念》**。
- **AGENT_3: 前端工程师 (Frontend Engineer):** 融合《创作蓝图》与选定的《视觉概念》，生成最终的 **HTML 和 CSS 代码**。
- **AGENT_4: 质量保证机器人 (QAQC Bot):** 对生成的代码进行自动化验证，输出一份**《验证报告》**。
- **AGENT_5: 元优化师 (Meta-Optimizer):** 分析失败的作业历史，诊断根本原因，并提出**《系统优化提案》**以改进其他代理的未来表现。

## **4. 技术实现与规范 (Technical Implementation & Specifications)**

本章节详细阐述了为实现上述架构而制定的技术选型、核心协议、数据结构和开发规范。

### **4.1 最终技术选型 (Final Technology Stack)**

| 组件 (Component) | **最终选型 (Final Choice)** | **核心理由 (Core Rationale)** |
| --- | --- | --- |
| **1. 核心编排器与代理框架** | **自定义 Python asyncio 脚本** | **架构一致性高于一切。** PRD明确定义了"状态驱动的轮询"模型，asyncio 是该模型最纯粹、最直接的实现，避免了不必要的依赖和复杂性。 |
| **2. 数据库交互** | **asyncpg 或 SQLAlchemy Core** | **追求精确与性能。** 避免使用重量级ORM，直接、高性能地控制SQL，完全符合我们简单的数据库操作需求。 |
| **3. AI模型交互** | **直接使用模型供应商SDK (如 openai)** | **保证完全的控制力与透明度。** 遵循P3原则，避免 LangChain 等框架引入的抽象层，确保对Prompt的绝对控制。 |
| **4. 作业创建API** | **FastAPI** | **选择正确，无需更改。** 轻量、高性能，与Pydantic的无缝集成为入口数据验证提供了完美的支持。 |
| **5. 数据库** | **PostgreSQL** | **选择正确，无需更改。** PRD中明确规定，其JSONB字段和事务能力是系统架构的基石。 |
| **6. 部署方案** | **Docker Compose -> Kubernetes** | **选择正确，无需更改。** 从本地开发到生产环境伸缩的理想路径，完美契合"因需而生"的演进策略。 |

### **4.2 核心协议与数据结构**

### **4.2.1 统一接口协议**

- **input_data 协议 (任务输入)**Generated json
    
    ```jsx
          {
      "artifacts": [
        { "name": "string", "source_task_id": "integer" }
      ],
      "params": {}
    }
    ```
    
- **output_data 协议 (任务输出/构件)**Generated json
    
    ```jsx
          {
      "schema_id": "string",
      "payload": {}
    }
    ```
    

### **4.2.2 数据库核心 Schema**

- **jobs 表:** id, status, initial_request, created_at, updated_at
- **tasks 表:** id, job_id, agent_id, status, input_data, output_data, error_log, retry_count
- **agent_prompts 表:** id, agent_id, version, prompt_text, created_at

### **4.3 代理开发框架 (SDK) 与治理**

(注：以下仅展示代理的核心 I/O 结构，具体实现依赖于 SDK)

### **4.3.1 SDK 核心要求**

- **批量构件获取:** sdk.get_artifacts() 必须实现批量查询，解决 N+1 问题。
- **生命周期验证:** sdk.save_output() 必须在写入前验证 Schema。

### **4.3.2 params 字段治理**

- artifacts 传递业务"名词"，params 仅传递流程控制的"副词"或元数据。通过严格的代码审查来执行。

### **4.4 代理规格说明 (Agent Specifications)**

(注：以下仅展示代理的核心 I/O 结构，具体实现依赖于 SDK)

- **AGENT_1: 创意总监 (Creative Director)**
    - **读取 input_data:** {"artifacts": [], "params": {"chatInput": "...", "sessionId": "..."}}
    - **写入 output_data:** {"schema_id": "CreativeBrief_v1.0", "payload": {...}}
- **AGENT_2: 视觉总监 (Visual Director)**
    - **读取 input_data:** {"artifacts": [{"name": "creative_brief", "source_task_id": 101}], "params": {}}
    - **写入 output_data:** {"schema_id": "VisualExplorations_v1.0", "payload": {...}}
- **AGENT_3: 首席叙事架构师 (Chief Narrative Architect)**
    - **读取 input_data:** {"artifacts": [{"name": "creative_brief", "source_task_id": 101}, {"name": "visual_explorations", "source_task_id": 102}], "params": {"prompt_version_to_use": "..."}}
    - **写入 output_data:** {"schema_id": "PresentationBlueprint_v1.0", "payload": {...}}
- **AGENT_4: 质量保证机器人 (QAQC Bot)**
    - **读取 input_data:** {"artifacts": [{"name": "presentation_blueprint", "source_task_id": 103}], "params": {}}
    - **写入 output_data:** {"schema_id": "ValidationReport_v1.0", "payload": {...}}
- **AGENT_5: 元优化师 (Meta-Optimizer)**
    - **读取 input_data:** {"artifacts": [], "params": {"failed_job_id": 42}}
    - **写入 output_data:** {"schema_id": "OptimizationProposal_v1.0", "payload": {...}}

### **4.4 数据库核心 Schema (Database Core Schema)**

- **jobs 表:** id (PK), status (ENUM), initial_request (JSONB), created_at, updated_at
- **tasks 表:** id (PK), job_id (FK), agent_id (VARCHAR), status (ENUM), input_data (JSONB), output_data (JSONB), error_log (TEXT), retry_count (INT)
- **agent_prompts 表:** id (PK), agent_id (VARCHAR), version (VARCHAR), prompt_text (TEXT), created_at

### **4.5 代理开发框架 (SDK) 与治理**

- **SDK 核心要求:**
    - **批量构件获取:** sdk.get_artifacts() 必须实现批量查询，解决 N+1 问题。
    - **生命周期验证:** sdk.save_output() 必须在写入前验证 Schema。
- **params 字段治理:** artifacts 传递业务"名词"，params 仅传递流程控制的"副词"或元数据。通过严格的代码审查来执行。

## **5. 设计哲学与执行策略 (Design Philosophy & Implementation Strategy)**

### **5.1 设计辩护：必要工程化 (The Rationale: Necessary Engineering)**

本 PRD 中的架构决策（状态机、引用协议、SDK）并非过度工程化，而是构建可靠、可扩展系统所必需的最小投入。

### **5.2 执行策略：最小化可行严肃性 (Minimum Viable Rigor)**

我们必须坚守架构原则，但以最轻量级的方式实现支持性工具。让复杂性因需而生。

- **SDK:** 从一个简单的共享帮助函数文件开始 (sdk/agent_sdk.py)。
- **Schema 管理:** 从一个代码库内的 schemas/ 目录开始。
- **工作流定义:** 从一个简单的 JSON 配置文件开始 (workflows.json)。

## **6. 本地开发入门 (Getting Started)**

本节将指导您如何在本地设置和运行 HELIX 系统。

### **6.1 先决条件**

- Git
- Docker
- Docker Compose

### **6.2 安装与启动**

1. **克隆仓库**Generated bash
    
    ```jsx
          git clone <your-repo-url>
    cd project-helix
    ```
    
2. **配置环境变量**Generated bash
    
    复制示例环境变量文件，并根据需要修改其中的配置（如数据库密码、API密钥等）。
    
    ```jsx
          cp .env.example .env
    ```
    
3. **构建并启动服务**Generated bash
    
    此命令将使用 docker-compose.yml 文件来构建所有服务的镜像，并以后台模式启动容器。
    
    ```jsx
          docker-compose up --build -d
    ```
    
4. **验证运行状态**
    - 查看所有容器是否正常运行：Generated bash
        
        ```jsx
              docker-compose ps
        ```
        
    - 实时查看服务日志：Generated bash
        
        ```jsx
              docker-compose logs -f
        ```
        
    - 访问 FastAPI 的 API 文档页面，确认 API 服务正常： http://localhost:8000/docs
5. **停止服务**Generated bash
    
          `docker-compose down`
    

## **7. 项目结构 (Project Structure)**

以下是推荐的项目目录结构，它将文档中的概念映射到实际的代码组织方式。

```jsx
      .
├── api/                 # FastAPI 应用，提供创建作业的 API 入口
├── agents/              # 包含各个专业化 Agent 的核心业务逻辑
│   ├── creative.py
│   ├── visual.py
│   └── ...
├── orchestrator/        # 核心编排器服务，负责轮询数据库和驱动工作流
├── sdk/                 # 代理开发框架 (Agent SDK)，提供共享的工具函数
│   └── agent_sdk.py
├── schemas/             # 存放所有构件的 JSON Schema 定义文件
│   ├── CreativeBrief_v1.1.json
│   └── ...
├── .env.example         # 环境变量示例文件
├── .gitignore           # Git 忽略文件配置
├── docker-compose.yml   # 定义和运行整个多容器应用程序
├── workflows.json       # 工作流定义文件，描述 Agent 的执行顺序和依赖关系
└── README.md            # 本文档
```

### **7.1 运行时架构 (Runtime Architecture)**

当通过 docker-compose up 启动后，HELIX 系统将以一组解耦的微服务形式运行：

- **api 服务:** 一个 FastAPI 应用，作为系统的唯一入口，负责接收用户请求并创建初始的 Job 记录。
- **orchestrator 服务:** 系统的"大脑"。一个独立的进程，持续轮询数据库，根据 workflows.json 的定义来创建和调度 Task。
- **agent 服务(群):** 一个或多个 Agent 工作者进程。它们是系统的"手脚"，持续轮巡数据库，获取分配给自己的 Task 并执行。可以水平扩展以增加系统的处理能力。

所有服务之间不直接通信，完全通过读写中心数据库来解耦和协作。

## **8. 未来路线图 (Future Roadmap)**

- **v1.5: 人类在环 (Human-in-the-Loop):** 在工作流中增加 PENDING_HUMAN_APPROVAL 状态。
- **v1.6: 分支与并行 (Branching & Parallelism):** 编排器支持并行任务。
- **v2.0: 引入新的代理:** 添加 AGENT_6 (UX Writer) 等。
- **v2.1: A/B 测试框架:** 支持新旧版本 Prompt 的并行运行与评估。

## **9. 许可 (License)**

本项目采用 [MIT License](https://www.google.com/url?sa=E&q=LICENSE) 授权。