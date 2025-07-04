# HTML文档输出功能使用指南

HELIX系统现在支持将所有Agent工作流的输出转换为美观的HTML文档，便于分享、存档和展示。

## 🚀 快速开始

### 1. API请求时指定HTML输出

在调用主处理API时，设置`outputFormat`参数为`html`：

```bash
curl -X POST http://localhost:3000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "设计一个现代化的博客平台界面",
    "type": "creative",
    "outputFormat": "html"
  }'
```

系统将直接返回格式化的HTML文档，而不是JSON响应。

### 2. 项目完成后导出HTML

如果已有完成的项目，可以通过导出API获取HTML版本：

```bash
# 导出为HTML文档
curl "http://localhost:3000/api/project/{projectId}/export?format=html" \
  --output "project-report.html"

# 导出为JSON（默认）
curl "http://localhost:3000/api/project/{projectId}/export" \
  --output "project-data.json"
```

## 📋 支持的工作流类型

HTML生成器支持所有HELIX工作流的输出：

### 🎨✨💻 完整实现工作流
- **创意蓝图**: 内容架构和策略规划
- **视觉概念**: 3个不同风格的视觉方案
- **前端实现**: 完整的代码实现和技术说明

### 🎨✨💻🔍 完整实现+QA工作流
- 包含上述所有内容
- **QA验证报告**: 详细的质量检查结果
- **验证状态横幅**: 清晰显示通过/失败状态

### 🎨✨ 创意+视觉工作流
- **创意蓝图**: 内容策略和架构
- **视觉概念**: 视觉设计方案

### ✨💻 视觉+前端工作流
- **视觉概念**: 设计方案
- **前端实现**: 代码实现

### 单一Agent工作流
- 🎨 **创意工作流**: 内容策略蓝图
- ✨ **视觉工作流**: 视觉设计概念
- 💻 **前端工作流**: 代码实现方案
- 🔍 **QA工作流**: 质量验证报告

### 📊 研究分析工作流
- **分析报告**: 深度研究和分析结果

## 🎨 HTML文档特性

### 响应式设计
- 完美适配桌面、平板、手机设备
- 现代化的渐变背景和卡片式布局
- 专业的色彩搭配和字体选择

### 内容格式化
- **Markdown支持**: 自动转换标题、粗体、斜体
- **代码高亮**: 语法高亮的代码块展示
- **QA状态**: 可视化的验证结果展示
- **响应式网格**: 自适应的内容布局

### 专业样式
- 现代化的CSS3样式
- 渐变背景和阴影效果
- 色彩编码的状态指示
- 清晰的层次结构

## 📝 使用示例

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function generateHTMLReport(message, type = 'creative') {
  try {
    const response = await axios.post('http://localhost:3000/api/process', {
      message,
      type,
      outputFormat: 'html'
    });
    
    // 直接获得HTML文档
    const htmlDocument = response.data;
    
    // 保存到文件
    require('fs').writeFileSync('report.html', htmlDocument);
    console.log('HTML报告已生成: report.html');
    
  } catch (error) {
    console.error('生成报告失败:', error.message);
  }
}

// 使用示例
generateHTMLReport('设计一个企业门户网站', 'creative');
```

### Python

```python
import requests
import json

def generate_html_report(message, report_type='creative'):
    try:
        response = requests.post('http://localhost:3000/api/process', 
            json={
                'message': message,
                'type': report_type,
                'outputFormat': 'html'
            }
        )
        
        if response.status_code == 200:
            # 保存HTML文档
            with open('report.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print('HTML报告已生成: report.html')
        else:
            print(f'请求失败: {response.status_code}')
            
    except Exception as e:
        print(f'生成报告失败: {e}')

# 使用示例
generate_html_report('创建电商平台的用户体验设计', 'creative')
```

### cURL

```bash
#!/bin/bash

# 生成HTML报告的函数
generate_html_report() {
    local message="$1"
    local type="${2:-creative}"
    local output_file="${3:-report.html}"
    
    curl -X POST http://localhost:3000/api/process \
      -H "Content-Type: application/json" \
      -d "{
        \"message\": \"$message\",
        \"type\": \"$type\",
        \"outputFormat\": \"html\"
      }" \
      --output "$output_file"
    
    echo "HTML报告已生成: $output_file"
}

# 使用示例
generate_html_report "设计一个在线教育平台" "creative" "education-platform-report.html"
```

## 🔧 高级配置

### 自定义输出样式

HTMLGenerator类支持扩展和自定义。你可以：

1. **修改CSS样式**: 编辑`getBaseTemplate()`方法中的CSS
2. **添加新的工作流支持**: 实现新的`generate[WorkflowType]HTML()`方法
3. **自定义内容格式化**: 扩展`formatMarkdown()`和`formatCodeBlocks()`方法

### 批量导出

```javascript
// 批量导出所有项目为HTML
async function exportAllProjectsAsHTML() {
  const projects = await getProjectList(); // 获取项目列表
  
  for (const project of projects) {
    const response = await axios.get(
      `http://localhost:3000/api/project/${project.id}/export?format=html`
    );
    
    fs.writeFileSync(`${project.id}-report.html`, response.data);
  }
}
```

## 📊 质量保证

### QA报告特殊功能

当工作流包含QA验证时，HTML输出会包含：

- **状态横幅**: 清晰显示整体验证结果
- **指标概览**: 错误和警告数量统计
- **详细结果**: 每个验证协议的具体结果
- **问题列表**: 发现的具体问题和建议

### 响应式验证

HTML文档在各种设备上都能完美显示：

- **桌面端**: 多栏布局，完整展示
- **平板端**: 自适应双栏布局
- **手机端**: 单栏垂直布局

## 🚀 最佳实践

1. **及时导出**: 完成项目后立即导出HTML，便于存档
2. **分享友好**: HTML文档可以直接发送给客户或团队成员
3. **版本管理**: 为重要项目保留HTML版本，便于对比
4. **打印支持**: HTML文档支持打印，适合制作纸质报告

## 🔮 未来计划

- **PDF导出**: 直接生成PDF格式报告
- **主题选择**: 多种视觉主题可选
- **交互功能**: 添加折叠、筛选等交互特性
- **数据可视化**: 集成图表和数据可视化组件

---

💡 **提示**: HTML输出功能完全兼容现有的JSON API，不会影响现有的集成和使用方式。只需添加`outputFormat: 'html'`参数即可获得美观的HTML文档输出！