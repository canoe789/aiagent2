#!/bin/bash
# Project HELIX 快速规范化脚本
# 简化版本 - 适合快速执行

echo "🚀 Project HELIX 快速规范化启动..."
echo "=================================="

# 检查是否在项目根目录
if [ ! -f "README.md" ] || [ ! -f "CLAUDE.md" ]; then
    echo "❌ 错误: 请在Project HELIX根目录下运行此脚本"
    echo "   (应该包含 README.md 和 CLAUDE.md 文件)"
    exit 1
fi

echo "✅ 检测到Project HELIX项目"

# 创建tmp目录结构
echo "📁 创建tmp目录结构..."
mkdir -p tmp/{debug,utilities,tests,logs,archives}
echo "✅ tmp目录创建完成"

# 移动临时文件 (简化版本)
echo "🗂️ 移动临时文件..."

# 移动调试脚本
echo "   处理调试脚本..."
for file in debug_*.py *_debug.py; do
    [ -f "$file" ] && mv "$file" tmp/debug/ && echo "   ✅ $file → tmp/debug/"
done

# 移动临时测试
echo "   处理临时测试..."
for file in test_*.py test_*.html; do
    [ -f "$file" ] && mv "$file" tmp/tests/ && echo "   ✅ $file → tmp/tests/"
done

# 移动工具脚本
echo "   处理工具脚本..."
for file in check_*.py cleanup_*.py delete_*.py export_*.py trace_*.py track_*.py; do
    [ -f "$file" ] && mv "$file" tmp/utilities/ && echo "   ✅ $file → tmp/utilities/"
done

# 移动日志文件
echo "   处理日志文件..."
for file in *.log; do
    [ -f "$file" ] && mv "$file" tmp/logs/ && echo "   ✅ $file → tmp/logs/"
done

# 移动其他临时文件
echo "   处理其他文件..."
[ -f "prompt.txt" ] && mv prompt.txt tmp/archives/ && echo "   ✅ prompt.txt → tmp/archives/"
[ -d "job_*_outputs" ] && mv job_*_outputs tmp/archives/ 2>/dev/null && echo "   ✅ job输出目录 → tmp/archives/"

# 移动文档文件到docs
echo "📚 重组文档..."
for file in FRONTEND_SETUP.md QUICK_START.md SYSTEM_STARTUP_GUIDE.md; do
    [ -f "$file" ] && mv "$file" docs/ && echo "   ✅ $file → docs/"
done

# 创建文档索引 (如果不存在)
if [ ! -f "docs/INDEX.md" ]; then
    echo "📋 创建文档索引..."
    cat > docs/INDEX.md << 'EOF'
# Project HELIX Documentation Index

## 🚀 快速开始
- [Quick Start Guide](QUICK_START.md)
- [Frontend Setup](FRONTEND_SETUP.md)
- [System Startup Guide](SYSTEM_STARTUP_GUIDE.md)

## 🏗️ 架构文档
- [README.md](../README.md) - 项目架构蓝图
- [CLAUDE.md](../CLAUDE.md) - AI协作指南

## 📊 项目管理
- [Project Progress](PROJECT_PROGRESS.md)
- [Process Management](PROCESS_MANAGEMENT.md)
- [Port Configuration](PORT_CONFIGURATION_ANALYSIS.md)
- [Dynamic Port Management](DYNAMIC_PORT_MANAGEMENT_GUIDE.md)
- [Data Cleanup SOP](DIRTY_DATA_CLEANUP_SOP.md)

---
**目标:** 5分钟内找到所需信息，提升开发效率
EOF
    echo "   ✅ 创建 docs/INDEX.md"
fi

# 更新.gitignore
echo "🔒 更新.gitignore..."
if ! grep -q "tmp/" .gitignore 2>/dev/null; then
    cat >> .gitignore << 'EOF'

# Project HELIX 临时文件管理
tmp/
*.log
*_debug.py
debug_*.py
test_*.py
check_*.py
prompt.txt
job_*_outputs/
EOF
    echo "   ✅ 更新.gitignore规则"
else
    echo "   ℹ️ .gitignore已包含相关规则"
fi

# 创建tmp说明
cat > tmp/README.md << 'EOF'
# tmp/ 临时文件目录

统一管理临时文件、调试脚本和日志文件。

## 目录说明
- debug/ - 调试脚本
- utilities/ - 工具脚本
- tests/ - 临时测试
- logs/ - 日志文件
- archives/ - 归档文件

⚠️ 本目录内容不会提交到版本控制
EOF

# 完成报告
echo ""
echo "🎉 规范化完成！"
echo "================"
echo ""
echo "📊 改进摘要:"
echo "   ✅ 创建了tmp/目录统一管理临时文件"
echo "   ✅ 重组了docs/目录并创建导航索引"
echo "   ✅ 更新了.gitignore防止文件污染"
echo ""
echo "📋 建议操作:"
echo "   1. 检查文件移动是否正确"
echo "   2. 运行 git status 查看变更"
echo "   3. 提交更改: git add . && git commit -m 'feat: 规范化项目结构'"
echo ""
echo "🎯 项目现在符合企业级标准结构！"