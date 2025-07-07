# HELIX Configuration Directory

按照系统级CLAUDE.md规范，本目录存放所有项目配置文件。

## 文件结构

- `development.env` - 开发环境配置
- `docker-compose.yml` - Docker编排配置  
- `Dockerfile` - 容器构建配置
- `production.env.example` - 生产环境配置模板

## 使用说明

1. 复制 `development.env` 到 `.env` 并修改相应配置
2. 生产环境请使用 `production.env.example` 作为模板
3. 敏感配置文件（*.env）已在 .gitignore 中排除

## 安全提醒

⚠️ 切勿将包含真实密钥的配置文件提交到版本控制