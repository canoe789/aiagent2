#!/bin/bash
# Project HELIX 文档结构规范化执行脚本
# 版本: 1.0
# 日期: 2025-07-09
# 目标: 将项目转换为符合系统级CLAUDE.md规范的标准化结构

set -e  # 遇到错误立即退出

echo "🚀 开始执行 Project HELIX 文档结构规范化..."
echo "=================================================="

# 设置项目路径 (请根据实际情况修改)
PROJECT_ROOT="/projects/Projects/aiagent"
BACKUP_DIR="$PROJECT_ROOT/backup_$(date +%Y%m%d_%H%M%S)"

# 检查项目目录是否存在
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "❌ 错误: 项目目录不存在: $PROJECT_ROOT"
    echo "请修改脚本中的 PROJECT_ROOT 变量为正确路径"
    exit 1
fi

echo "📁 项目路径: $PROJECT_ROOT"
echo "💾 备份路径: $BACKUP_DIR"

# ===============================================
# 第一步: 创建备份 (安全措施)
# ===============================================
echo ""
echo "📋 第一步: 创建安全备份..."
mkdir -p "$BACKUP_DIR"

# 备份即将移动的文件
echo "   备份临时文件和日志..."
cp "$PROJECT_ROOT"/*.py "$BACKUP_DIR/" 2>/dev/null || true
cp "$PROJECT_ROOT"/*.log "$BACKUP_DIR/" 2>/dev/null || true
cp "$PROJECT_ROOT"/*.html "$BACKUP_DIR/" 2>/dev/null || true
cp "$PROJECT_ROOT"/*.txt "$BACKUP_DIR/" 2>/dev/null || true
cp "$PROJECT_ROOT"/job_*_outputs "$BACKUP_DIR/" 2>/dev/null || true

# 备份根目录文档
echo "   备份根目录文档..."
cp "$PROJECT_ROOT"/FRONTEND_SETUP.md "$BACKUP_DIR/" 2>/dev/null || true
cp "$PROJECT_ROOT"/QUICK_START.md "$BACKUP_DIR/" 2>/dev/null || true
cp "$PROJECT_ROOT"/SYSTEM_STARTUP_GUIDE.md "$BACKUP_DIR/" 2>/dev/null || true

# 备份当前.gitignore
cp "$PROJECT_ROOT/.gitignore" "$BACKUP_DIR/gitignore_backup" 2>/dev/null || true

echo "✅ 备份完成: $BACKUP_DIR"

# ===============================================
# 第二步: 创建目录结构
# ===============================================
echo ""
echo "📁 第二步: 创建标准目录结构..."

cd "$PROJECT_ROOT"

# 创建tmp子目录
echo "   创建 tmp/ 目录结构..."
mkdir -p tmp/{debug,utilities,tests,logs,archives}

echo "✅ 目录结构创建完成"

# ===============================================
# 第三步: 移动临时文件到tmp目录
# ===============================================
echo ""
echo "🗂️ 第三步: 移动临时文件到 tmp/ 目录..."

# 移动调试脚本
echo "   移动调试脚本到 tmp/debug/..."
mv debug_agent5.py tmp/debug/ 2>/dev/null || echo "   ⚠️ debug_agent5.py 未找到"
mv debug_job20.py tmp/debug/ 2>/dev/null || echo "   ⚠️ debug_job20.py 未找到"
mv test_agent2_debug.py tmp/debug/ 2>/dev/null || echo "   ⚠️ test_agent2_debug.py 未找到"

# 移动工具脚本
echo "   移动工具脚本到 tmp/utilities/..."
for file in check_agent_outputs.py check_job_tasks.py cleanup_with_env.py \
           delete_all_tasks.py delete_all_tasks_direct.py delete_via_api.py \
           direct_cleanup.py export_agent_outputs.py trace_job_flow.py \
           track_workflow.py; do
    if [ -f "$file" ]; then
        mv "$file" tmp/utilities/
        echo "   ✅ 移动: $file"
    else
        echo "   ⚠️ 未找到: $file"
    fi
done

# 移动临时测试
echo "   移动临时测试到 tmp/tests/..."
for file in test_complete_workflow.py test_db_connection.py \
           test_frontend_integration.py test_agent5_trigger.py \
           test_browser.html; do
    if [ -f "$file" ]; then
        mv "$file" tmp/tests/
        echo "   ✅ 移动: $file"
    else
        echo "   ⚠️ 未找到: $file"
    fi
done

# 移动日志文件
echo "   移动日志文件到 tmp/logs/..."
for file in *.log; do
    if [ -f "$file" ]; then
        mv "$file" tmp/logs/
        echo "   ✅ 移动: $file"
    fi
done

# 移动归档文件
echo "   移动归档文件到 tmp/archives/..."
if [ -f "prompt.txt" ]; then
    mv prompt.txt tmp/archives/
    echo "   ✅ 移动: prompt.txt"
fi

if [ -d "job_26_outputs" ]; then
    mv job_26_outputs tmp/archives/
    echo "   ✅ 移动: job_26_outputs/"
fi

echo "✅ 临时文件移动完成"

# ===============================================
# 第四步: 移动文档文件到docs目录
# ===============================================
echo ""
echo "📚 第四步: 重组文档结构..."

# 移动根目录文档到docs/
echo "   移动根目录文档到 docs/..."
for file in FRONTEND_SETUP.md QUICK_START.md SYSTEM_STARTUP_GUIDE.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/
        echo "   ✅ 移动: $file"
    else
        echo "   ⚠️ 未找到: $file"
    fi
done

# 创建文档索引 (如果不存在)
if [ ! -f "docs/INDEX.md" ]; then
    echo "   创建 docs/INDEX.md 文档索引..."
    cat > docs/INDEX.md << 'EOF'
# Project HELIX Documentation Index

**版本:** 1.0  
**更新:** $(date +%Y-%m-%d)  
**状态:** 文档导航中心

---

## 📋 文档导航索引

欢迎来到Project HELIX文档中心！本页面是所有项目文档的统一导航索引。

## 🚀 快速开始指南
- [Quick Start Guide](QUICK_START.md) - 5分钟快速上手
- [Frontend Setup](FRONTEND_SETUP.md) - 前端环境配置
- [System Startup Guide](SYSTEM_STARTUP_GUIDE.md) - 系统启动指南

## 🏗️ 架构与设计
- [README.md](../README.md) - **项目架构蓝图** (唯一事实来源)
- [CLAUDE.md](../CLAUDE.md) - AI协作指南

## 📊 项目管理
- [Project Progress](PROJECT_PROGRESS.md) - 项目进度跟踪
- [Process Management](PROCESS_MANAGEMENT.md) - 进程管理
- [Port Configuration](PORT_CONFIGURATION_ANALYSIS.md) - 端口配置
- [Dynamic Port Management](DYNAMIC_PORT_MANAGEMENT_GUIDE.md) - 动态端口管理
- [Data Cleanup SOP](DIRTY_DATA_CLEANUP_SOP.md) - 数据清理标准程序

---

**🎯 目标:** 让任何人都能在5分钟内找到所需的项目信息，提升整体开发效率。

**📌 维护提醒:** 本索引是活文档，需要随着项目发展持续更新。
EOF
    echo "   ✅ 创建: docs/INDEX.md"
else
    echo "   ℹ️ docs/INDEX.md 已存在，跳过创建"
fi

echo "✅ 文档结构重组完成"

# ===============================================
# 第五步: 更新.gitignore
# ===============================================
echo ""
echo "🔒 第五步: 更新 .gitignore 规则..."

# 备份当前.gitignore
if [ -f ".gitignore" ]; then
    cp .gitignore .gitignore.backup
    echo "   📋 备份原有 .gitignore 为 .gitignore.backup"
fi

# 添加临时文件规则到.gitignore (如果尚未存在)
if ! grep -q "tmp/" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Project HELIX 临时文件管理 (规范化添加)" >> .gitignore
    echo "tmp/" >> .gitignore
    echo "*.log" >> .gitignore
    echo "*_debug.py" >> .gitignore
    echo "debug_*.py" >> .gitignore
    echo "test_*.py" >> .gitignore
    echo "check_*.py" >> .gitignore
    echo "trace_*.py" >> .gitignore
    echo "track_*.py" >> .gitignore
    echo "cleanup_*.py" >> .gitignore
    echo "delete_*.py" >> .gitignore
    echo "export_*.py" >> .gitignore
    echo "job_*_outputs/" >> .gitignore
    echo "prompt.txt" >> .gitignore
    echo "" >> .gitignore
    echo "✅ 更新 .gitignore 规则"
else
    echo "   ℹ️ .gitignore 已包含临时文件规则，跳过更新"
fi

# ===============================================
# 第六步: 创建说明文件
# ===============================================
echo ""
echo "📝 第六步: 创建说明文件..."

# 创建tmp目录说明
cat > tmp/README.md << 'EOF'
# tmp/ 目录说明

本目录用于统一管理项目的临时文件、调试脚本和日志文件，符合系统级CLAUDE.md智能文件管理规范。

## 目录结构

- `debug/` - 调试脚本
- `utilities/` - 临时工具脚本  
- `tests/` - 临时测试文件
- `logs/` - 日志文件
- `archives/` - 归档文件

## 重要说明

- 本目录内容不应提交到版本控制
- 定期清理过期文件
- 正式脚本应移动到 scripts/ 目录
- 正式测试应移动到 tests/ 目录
EOF

echo "✅ 创建 tmp/README.md 说明文件"

# ===============================================
# 第七步: 验证结构
# ===============================================
echo ""
echo "🔍 第七步: 验证新结构..."

echo "   检查根目录清洁度..."
ROOT_FILES=$(find . -maxdepth 1 -name "*.py" -o -name "*.log" -o -name "test_*.html" | wc -l)
if [ "$ROOT_FILES" -eq 0 ]; then
    echo "   ✅ 根目录已清洁，无临时文件"
else
    echo "   ⚠️ 根目录仍有 $ROOT_FILES 个临时文件需要处理"
fi

echo "   检查tmp目录结构..."
for dir in debug utilities tests logs archives; do
    if [ -d "tmp/$dir" ]; then
        FILES_COUNT=$(ls tmp/$dir 2>/dev/null | wc -l)
        echo "   ✅ tmp/$dir/ 存在 ($FILES_COUNT 个文件)"
    else
        echo "   ❌ tmp/$dir/ 不存在"
    fi
done

echo "   检查docs目录结构..."
if [ -f "docs/INDEX.md" ]; then
    echo "   ✅ docs/INDEX.md 存在"
else
    echo "   ❌ docs/INDEX.md 不存在"
fi

# ===============================================
# 完成报告
# ===============================================
echo ""
echo "🎉 Project HELIX 规范化完成！"
echo "=================================================="
echo ""
echo "📊 执行摘要:"
echo "   📁 创建了 tmp/ 目录统一管理临时文件"
echo "   📚 重组了 docs/ 目录并创建了导航索引"
echo "   🔒 更新了 .gitignore 防止临时文件污染"
echo "   💾 创建了安全备份: $BACKUP_DIR"
echo ""
echo "🎯 项目现在符合系统级CLAUDE.md智能文件管理规范!"
echo ""
echo "📋 建议下一步操作:"
echo "   1. 检查移动后的文件是否正确"
echo "   2. 运行 git status 查看变更"
echo "   3. 测试系统启动是否正常"
echo "   4. 提交规范化变更: git add . && git commit -m 'feat: 规范化项目文档结构'"
echo "   5. 如有问题，可从备份目录恢复: $BACKUP_DIR"
echo ""
echo "✨ 规范化执行完成！项目现在具有企业级的专业结构。"