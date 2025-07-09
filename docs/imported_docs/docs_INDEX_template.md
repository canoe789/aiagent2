# Project HELIX Documentation Index

**版本:** 1.0  
**更新:** 2025-07-09  
**状态:** 文档导航中心

---

## 📋 文档导航索引

欢迎来到Project HELIX文档中心！本页面是所有项目文档的统一导航索引，按照系统级CLAUDE.md智能文件管理规范组织。

## 🚀 快速开始指南 (Getting Started)

| 文档 | 用途 | 受众 | 预计时间 |
|------|------|------|----------|
| [Quick Start Guide](QUICK_START.md) | 5分钟快速上手 | 新开发者 | 5分钟 |
| [Frontend Setup](FRONTEND_SETUP.md) | 前端环境配置 | 前端开发者 | 15分钟 |
| [System Startup Guide](SYSTEM_STARTUP_GUIDE.md) | 系统启动指南 | 运维人员 | 10分钟 |

## 🏗️ 架构与设计 (Architecture & Design)

| 文档 | 用途 | 重要性 |
|------|------|--------|
| [README.md](../README.md) | **项目架构蓝图** - 唯一事实来源 | 🔥 必读 |
| [BACKEND_README.md](BACKEND_README.md) | Agent开发指南 | 🔥 必读 |
| [Architecture Documentation](ARCHITECTURE.md) | 详细架构说明 | ⭐ 重要 |
| [Design Principles](../README.md#core-principles) | P1-P7核心设计原则 | 🔥 必读 |

## 👨‍💻 开发指南 (Development Guide)

| 文档 | 适用场景 | 技能要求 |
|------|----------|----------|
| [Development Guide](DEVELOPMENT_GUIDE.md) | 日常开发规范与流程 | Python, FastAPI |
| [API Reference](API_REFERENCE.md) | API接口开发与调试 | Web API开发 |
| [Agent Development](../README.md#agent-specifications) | Agent开发规范 | 异步编程, AI集成 |
| [Schema Design Guide](SCHEMA_DESIGN.md) | 数据结构设计 | Pydantic, JSON Schema |

## 🚀 部署与运维 (Deployment & Operations)

| 文档 | 应用场景 | 紧急程度 |
|------|----------|----------|
| [Deployment Guide](DEPLOYMENT_GUIDE.md) | 生产环境部署 | ⭐ 重要 |
| [Process Management](PROCESS_MANAGEMENT.md) | 进程管理与监控 | 🚨 关键 |
| [Port Configuration](PORT_CONFIGURATION_ANALYSIS.md) | 端口配置分析 | ⭐ 重要 |
| [Dynamic Port Management](DYNAMIC_PORT_MANAGEMENT_GUIDE.md) | 动态端口管理SOP | 🔥 必读 |

## 🔧 运维与故障排查 (Operations & Troubleshooting)

| 文档 | 使用时机 | 预期解决率 |
|------|----------|------------|
| [Troubleshooting Guide](TROUBLESHOOTING.md) | 系统故障排查 | 80% |
| [Data Cleanup SOP](DIRTY_DATA_CLEANUP_SOP.md) | 数据清理标准程序 | 95% |
| [Emergency Recovery](EMERGENCY_RECOVERY.md) | 紧急恢复程序 | 90% |
| [Performance Tuning](PERFORMANCE_TUNING.md) | 性能优化指南 | 70% |

## 📊 项目管理 (Project Management)

| 文档 | 更新频率 | 责任人 |
|------|----------|--------|
| [Project Progress](PROJECT_PROGRESS.md) | 每日更新 | 项目负责人 |
| [Development Log](PROJECT_PROGRESS.md#development-history) | 实时更新 | 开发团队 |
| [Milestone Tracking](MILESTONES.md) | 每周更新 | 产品经理 |
| [Issue Tracking](ISSUES.md) | 实时更新 | 全体成员 |

## 🤖 AI协作 (AI Collaboration)

| 文档 | 用途 | 重要性 |
|------|------|--------|
| [Claude.md](../CLAUDE.md) | **AI结对编程指挥官手册** | 🔥 必读 |
| [AI Collaboration Best Practices](../CLAUDE.md#collaboration-protocol) | AI协作最佳实践 | ⭐ 重要 |
| [Prompt Engineering Guide](AI_PROMPTS.md) | Prompt设计指南 | ⭐ 重要 |

## 🧪 测试与质量保证 (Testing & QA)

| 文档 | 覆盖范围 | 自动化程度 |
|------|----------|------------|
| [Testing Strategy](TESTING_STRATEGY.md) | 测试策略与框架 | 手动设计 |
| [Unit Testing Guide](UNIT_TESTING.md) | 单元测试规范 | 80%自动化 |
| [Integration Testing](INTEGRATION_TESTING.md) | 集成测试流程 | 60%自动化 |
| [Quality Standards](QUALITY_STANDARDS.md) | 代码质量标准 | 90%自动化 |

## 📚 参考资料 (References)

### 外部资源
- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)

### 工具链
- [Docker Compose Configuration](../config/docker-compose.yml)
- [Environment Setup](../.env.example)
- [Workflow Definitions](../workflows.json)
- [Schema Definitions](../schemas/)

## 🔄 文档维护协议 (Documentation Maintenance)

### 更新责任
- **INDEX.md (本文档):** 每次添加新文档时必须更新
- **架构文档:** 重大架构变更时必须同步更新
- **开发指南:** 新功能或API变更时更新
- **故障排查:** 新问题解决后及时补充

### 文档质量标准
- ✅ 标题层级清晰 (H1-H4)
- ✅ 代码示例可执行
- ✅ 链接引用有效
- ✅ 更新日期标注
- ✅ 责任人明确

### 审查流程
1. 新文档创建后进行peer review
2. 重要文档变更需要团队确认
3. 每月进行文档有效性检查
4. 过期文档及时归档或删除

---

## 📞 获取帮助 (Getting Help)

### 快速查找
- 🔍 **搜索关键词:** 使用Ctrl+F在本索引中搜索
- 📝 **问题模板:** 参考[Issue Template](ISSUE_TEMPLATE.md)
- 💬 **团队沟通:** 优先查阅文档，后询问团队

### 常见查找路径
```
新手入门: INDEX.md → QUICK_START.md → README.md
开发问题: INDEX.md → DEVELOPMENT_GUIDE.md → API_REFERENCE.md  
部署问题: INDEX.md → DEPLOYMENT_GUIDE.md → TROUBLESHOOTING.md
Agent开发: INDEX.md → BACKEND_README.md → Agent Specifications
系统故障: INDEX.md → TROUBLESHOOTING.md → PROCESS_MANAGEMENT.md
```

---

**🎯 目标:** 让任何人都能在5分钟内找到所需的项目信息，提升整体开发效率和知识传承。

**📌 维护提醒:** 本索引是活文档，需要随着项目发展持续更新。添加新文档时请同步更新此索引。