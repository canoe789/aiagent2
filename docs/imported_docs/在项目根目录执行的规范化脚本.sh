#!/bin/bash
# 在Project HELIX项目根目录执行的规范化脚本
# 路径: /projects/Projects/aiagent/

echo "🚀 Project HELIX 根目录规范化脚本"
echo "项目路径: /projects/Projects/aiagent/"
echo "=================================="

# 检查是否在正确的项目根目录
if [ ! -f "README.md" ] || [ ! -f "CLAUDE.md" ] || [ ! -f "workflows.json" ]; then
    echo "❌ 错误: 请在Project HELIX根目录下运行此脚本"
    echo "   当前目录: $(pwd)"
    echo "   应该在包含 README.md, CLAUDE.md, workflows.json 的目录"
    exit 1
fi

echo "✅ 检测到Project HELIX项目根目录"

# 创建tmp子目录结构
echo ""
echo "📁 创建tmp子目录结构..."
mkdir -p tmp/debug tmp/utilities tmp/tests tmp/logs tmp/archives
echo "   ✅ tmp/debug/ - 调试脚本"
echo "   ✅ tmp/utilities/ - 工具脚本"  
echo "   ✅ tmp/tests/ - 临时测试"
echo "   ✅ tmp/logs/ - 日志文件"
echo "   ✅ tmp/archives/ - 归档文件"

# 移动调试脚本
echo ""
echo "🐛 移动调试脚本到 tmp/debug/..."
for file in debug_*.py *_debug.py; do
    if [ -f "$file" ]; then
        mv "$file" tmp/debug/
        echo "   ✅ $file → tmp/debug/"
    fi
done

# 移动工具脚本
echo ""
echo "🛠️ 移动工具脚本到 tmp/utilities/..."
for file in check_*.py cleanup_*.py delete_*.py export_*.py trace_*.py track_*.py; do
    if [ -f "$file" ]; then
        mv "$file" tmp/utilities/
        echo "   ✅ $file → tmp/utilities/"
    fi
done

# 移动临时测试
echo ""
echo "🧪 移动临时测试到 tmp/tests/..."
for file in test_*.py test_*.html; do
    if [ -f "$file" ]; then
        mv "$file" tmp/tests/
        echo "   ✅ $file → tmp/tests/"
    fi
done

# 移动日志文件
echo ""
echo "📋 移动日志文件到 tmp/logs/..."
for file in *.log; do
    if [ -f "$file" ]; then
        mv "$file" tmp/logs/
        echo "   ✅ $file → tmp/logs/"
    fi
done

# 移动归档文件
echo ""
echo "📦 移动归档文件到 tmp/archives/..."
[ -f "prompt.txt" ] && mv prompt.txt tmp/archives/ && echo "   ✅ prompt.txt → tmp/archives/"
[ -d "job_26_outputs" ] && mv job_26_outputs tmp/archives/ && echo "   ✅ job_26_outputs/ → tmp/archives/"

# 移动文档到docs
echo ""
echo "📚 移动文档到 docs/..."
for file in FRONTEND_SETUP.md QUICK_START.md SYSTEM_STARTUP_GUIDE.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/
        echo "   ✅ $file → docs/"
    fi
done

# 创建文档索引
echo ""
echo "📋 创建文档索引 docs/INDEX.md..."
if [ ! -f "docs/INDEX.md" ]; then
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
    echo "   ✅ 创建成功"
else
    echo "   ℹ️ 已存在，跳过"
fi

# 更新.gitignore
echo ""
echo "🔒 更新.gitignore..."
if ! grep -q "tmp/debug/" .gitignore 2>/dev/null; then
    cat >> .gitignore << 'EOF'

# Project HELIX 临时文件分类管理
tmp/debug/
tmp/utilities/
tmp/tests/
tmp/logs/
tmp/archives/
*.log
*_debug.py
debug_*.py
check_*.py
prompt.txt
job_*_outputs/
EOF
    echo "   ✅ 添加临时文件规则"
else
    echo "   ℹ️ 规则已存在"
fi

# 验证结果
echo ""
echo "🔍 验证规范化结果..."
echo "========================"
temp_files=$(find . -maxdepth 1 -name "*.py" -o -name "*.log" | wc -l)
echo "📊 根目录临时文件数: $temp_files"

if [ "$temp_files" -eq 0 ]; then
    echo "   ✅ 根目录已清洁"
else
    echo "   ⚠️ 还有临时文件需要处理"
fi

echo ""
echo "🎉 Project HELIX 根目录规范化完成！"
echo "=================================="
echo ""
echo "📁 tmp目录现在包含:"
echo "   📂 tmp/debug/ - 调试脚本"
echo "   📂 tmp/utilities/ - 工具脚本"
echo "   📂 tmp/tests/ - 临时测试"
echo "   📂 tmp/logs/ - 日志文件"
echo "   📂 tmp/archives/ - 归档文件"
echo ""
echo "📚 docs目录现在包含:"
echo "   📄 INDEX.md - 文档导航索引"
echo "   📄 所有指南文档已移入"
echo ""
echo "🎯 项目现在符合企业级标准结构！"