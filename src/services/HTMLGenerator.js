/**
 * HTML文档生成器 - 将HELIX系统输出转换为美观的HTML文档
 * 
 * 支持所有Agent工作流输出：创意蓝图、视觉概念、前端代码、QA报告等
 */

class HTMLGenerator {
  constructor() {
    this.baseTemplate = this.getBaseTemplate();
  }

  /**
   * 生成项目完整HTML文档
   * @param {Object} projectData - 项目数据
   * @param {Object} result - 处理结果
   * @returns {string} HTML文档
   */
  generateProjectHTML(projectData, result) {
    const { userRequest, status, completedAt, workflowType } = projectData.project_info || {};
    const timestamp = completedAt || new Date().toISOString();
    
    let content = '';
    let title = '项目报告';
    
    // 根据不同的工作流类型生成不同的内容
    switch (workflowType) {
      case 'full_implementation':
        title = '完整实现项目报告';
        content = this.generateFullImplementationHTML(result, projectData);
        break;
      case 'full_implementation_with_qa':
        title = '完整实现+QA验证项目报告';
        content = this.generateFullImplementationWithQAHTML(result, projectData);
        break;
      case 'creative_visual':
        title = '创意+视觉设计项目报告';
        content = this.generateCreativeVisualHTML(result, projectData);
        break;
      case 'visual_frontend':
        title = '视觉+前端实现项目报告';
        content = this.generateVisualFrontendHTML(result, projectData);
        break;
      case 'creative_only':
        title = '创意蓝图报告';
        content = this.generateCreativeOnlyHTML(result, projectData);
        break;
      case 'visual_only':
        title = '视觉设计报告';
        content = this.generateVisualOnlyHTML(result, projectData);
        break;
      case 'frontend_only':
        title = '前端实现报告';
        content = this.generateFrontendOnlyHTML(result, projectData);
        break;
      case 'qa_validation':
        title = 'QA验证报告';
        content = this.generateQAOnlyHTML(result, projectData);
        break;
      default:
        title = '研究分析报告';
        content = this.generateGeneralReportHTML(result, projectData);
        break;
    }

    // 添加项目概览
    const overview = this.generateProjectOverview(userRequest, workflowType, timestamp);
    
    return this.baseTemplate
      .replace('{{TITLE}}', title)
      .replace('{{OVERVIEW}}', overview)
      .replace('{{CONTENT}}', content)
      .replace('{{TIMESTAMP}}', timestamp);
  }

  /**
   * 生成项目概览部分
   */
  generateProjectOverview(userRequest, workflowType, timestamp) {
    const workflowNames = {
      'full_implementation': '🎨✨💻 完整实现工作流',
      'full_implementation_with_qa': '🎨✨💻🔍 完整实现+QA工作流',
      'creative_visual': '🎨✨ 创意+视觉工作流',
      'visual_frontend': '✨💻 视觉+前端工作流',
      'creative_only': '🎨 创意工作流',
      'visual_only': '✨ 视觉设计工作流',
      'frontend_only': '💻 前端实现工作流',
      'qa_validation': '🔍 QA验证工作流'
    };

    return `
      <div class="project-overview">
        <h2>📋 项目概览</h2>
        <div class="overview-grid">
          <div class="overview-item">
            <strong>原始需求：</strong>
            <p>${this.escapeHtml(userRequest?.message || '未知')}</p>
          </div>
          <div class="overview-item">
            <strong>执行工作流：</strong>
            <p>${workflowNames[workflowType] || workflowType || '通用研究'}</p>
          </div>
          <div class="overview-item">
            <strong>完成时间：</strong>
            <p>${new Date(timestamp).toLocaleString('zh-CN')}</p>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * 生成完整实现工作流HTML
   */
  generateFullImplementationHTML(result, projectData) {
    const { creativeBrief, visualConcepts, frontendImplementation } = result.result || result;
    
    let html = '<div class="full-implementation-report">';
    
    // 创意蓝图部分
    if (creativeBrief) {
      html += this.generateCreativeBriefSection(creativeBrief);
    }
    
    // 视觉概念部分
    if (visualConcepts) {
      html += this.generateVisualConceptsSection(visualConcepts);
    }
    
    // 前端实现部分
    if (frontendImplementation) {
      html += this.generateFrontendImplementationSection(frontendImplementation);
    }
    
    html += '</div>';
    return html;
  }

  /**
   * 生成完整实现+QA工作流HTML
   */
  generateFullImplementationWithQAHTML(result, projectData) {
    const { creativeBrief, visualConcepts, frontendImplementation, qaReport } = result.result || result;
    
    let html = '<div class="full-implementation-qa-report">';
    
    // QA验证状态概览
    if (qaReport && qaReport.validation_report) {
      const passed = qaReport.validation_report.validation_passed;
      html += `
        <div class="qa-status-banner ${passed ? 'qa-passed' : 'qa-failed'}">
          <h2>${passed ? '✅ QA验证通过' : '⚠️ QA验证发现问题'}</h2>
          <p>错误: ${qaReport.validation_report.summary.errors_found}个 | 
             警告: ${qaReport.validation_report.summary.warnings_found}个</p>
        </div>
      `;
    }
    
    // 完整实现内容
    html += this.generateFullImplementationHTML(result, projectData);
    
    // QA报告部分
    if (qaReport) {
      html += this.generateQAReportSection(qaReport);
    }
    
    html += '</div>';
    return html;
  }

  /**
   * 生成创意蓝图部分
   */
  generateCreativeBriefSection(creativeBrief) {
    return `
      <section class="creative-brief-section">
        <h2>🎨 创意蓝图</h2>
        <div class="creative-content">
          ${this.formatCreativeContent(creativeBrief)}
        </div>
      </section>
    `;
  }

  /**
   * 生成视觉概念部分
   */
  generateVisualConceptsSection(visualConcepts) {
    return `
      <section class="visual-concepts-section">
        <h2>✨ 视觉概念设计</h2>
        <div class="visual-content">
          ${this.formatVisualContent(visualConcepts)}
        </div>
      </section>
    `;
  }

  /**
   * 生成前端实现部分
   */
  generateFrontendImplementationSection(frontendImplementation) {
    return `
      <section class="frontend-implementation-section">
        <h2>💻 前端实现</h2>
        <div class="frontend-content">
          ${this.formatFrontendContent(frontendImplementation)}
        </div>
      </section>
    `;
  }

  /**
   * 生成QA报告部分
   */
  generateQAReportSection(qaReport) {
    return `
      <section class="qa-report-section">
        <h2>🔍 QA验证报告</h2>
        <div class="qa-content">
          ${this.formatQAContent(qaReport)}
        </div>
      </section>
    `;
  }

  /**
   * 格式化创意内容
   */
  formatCreativeContent(content) {
    if (typeof content === 'string') {
      return `<div class="content-text">${this.formatMarkdown(content)}</div>`;
    }
    return `<pre class="content-json">${JSON.stringify(content, null, 2)}</pre>`;
  }

  /**
   * 格式化视觉内容
   */
  formatVisualContent(content) {
    if (typeof content === 'string') {
      return `<div class="content-text">${this.formatMarkdown(content)}</div>`;
    }
    return `<pre class="content-json">${JSON.stringify(content, null, 2)}</pre>`;
  }

  /**
   * 格式化前端内容
   */
  formatFrontendContent(content) {
    if (typeof content === 'string') {
      // 检查是否包含代码
      if (content.includes('```') || content.includes('<html>') || content.includes('function')) {
        return `<div class="code-content">${this.formatCodeBlocks(content)}</div>`;
      }
      return `<div class="content-text">${this.formatMarkdown(content)}</div>`;
    }
    return `<pre class="content-json">${JSON.stringify(content, null, 2)}</pre>`;
  }

  /**
   * 格式化QA内容
   */
  formatQAContent(qaReport) {
    let html = '';
    
    if (qaReport.validation_report) {
      const report = qaReport.validation_report;
      
      html += `
        <div class="qa-summary">
          <h3>验证概览</h3>
          <div class="qa-metrics">
            <div class="metric ${report.validation_passed ? 'passed' : 'failed'}">
              <span class="metric-label">总体状态:</span>
              <span class="metric-value">${report.validation_passed ? '✅ 通过' : '❌ 失败'}</span>
            </div>
            <div class="metric">
              <span class="metric-label">错误数量:</span>
              <span class="metric-value error-count">${report.summary.errors_found}</span>
            </div>
            <div class="metric">
              <span class="metric-label">警告数量:</span>
              <span class="metric-value warning-count">${report.summary.warnings_found}</span>
            </div>
          </div>
        </div>
      `;
      
      // 详细验证结果
      if (report.validation_details && report.validation_details.length > 0) {
        html += '<div class="qa-details"><h3>详细验证结果</h3>';
        report.validation_details.forEach(detail => {
          const statusClass = detail.passed ? 'passed' : 'failed';
          html += `
            <div class="validation-item ${statusClass}">
              <h4>${detail.protocol_id}: ${detail.protocol_name}</h4>
              <p><strong>状态:</strong> ${detail.passed ? '✅ 通过' : '❌ 失败'}</p>
              <p><strong>描述:</strong> ${this.escapeHtml(detail.description)}</p>
              ${detail.issues && detail.issues.length > 0 ? `
                <div class="issues">
                  <strong>发现的问题:</strong>
                  <ul>
                    ${detail.issues.map(issue => `<li>${this.escapeHtml(issue)}</li>`).join('')}
                  </ul>
                </div>
              ` : ''}
            </div>
          `;
        });
        html += '</div>';
      }
    }
    
    return html;
  }

  /**
   * 简单的Markdown转HTML
   */
  formatMarkdown(text) {
    return text
      .replace(/### (.*$)/gm, '<h3>$1</h3>')
      .replace(/## (.*$)/gm, '<h2>$1</h2>')
      .replace(/# (.*$)/gm, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>')
      .replace(/^(.*)$/gm, '<p>$1</p>')
      .replace(/<p><\/p>/g, '')
      .replace(/<p><h([1-6])>/g, '<h$1>')
      .replace(/<\/h([1-6])><\/p>/g, '</h$1>');
  }

  /**
   * 格式化代码块
   */
  formatCodeBlocks(text) {
    return text.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, language, code) => {
      const lang = language || 'text';
      return `<div class="code-block">
        <div class="code-header">${lang}</div>
        <pre><code class="language-${lang}">${this.escapeHtml(code.trim())}</code></pre>
      </div>`;
    });
  }

  /**
   * 生成创意工作流HTML
   */
  generateCreativeOnlyHTML(result, projectData) {
    return `
      <section class="creative-only-report">
        <h2>🎨 创意蓝图</h2>
        <div class="creative-content">
          ${this.formatCreativeContent(result.result || result)}
        </div>
      </section>
    `;
  }

  /**
   * 生成视觉工作流HTML
   */
  generateVisualOnlyHTML(result, projectData) {
    return `
      <section class="visual-only-report">
        <h2>✨ 视觉设计</h2>
        <div class="visual-content">
          ${this.formatVisualContent(result.result || result)}
        </div>
      </section>
    `;
  }

  /**
   * 生成前端工作流HTML
   */
  generateFrontendOnlyHTML(result, projectData) {
    return `
      <section class="frontend-only-report">
        <h2>💻 前端实现</h2>
        <div class="frontend-content">
          ${this.formatFrontendContent(result.result || result)}
        </div>
      </section>
    `;
  }

  /**
   * 生成QA工作流HTML
   */
  generateQAOnlyHTML(result, projectData) {
    return `
      <section class="qa-only-report">
        <h2>🔍 QA验证报告</h2>
        <div class="qa-content">
          ${this.formatQAContent(result.result || result)}
        </div>
      </section>
    `;
  }

  /**
   * 生成创意+视觉工作流HTML
   */
  generateCreativeVisualHTML(result, projectData) {
    const { creativeBrief, visualConcepts } = result.result || result;
    
    let html = '<div class="creative-visual-report">';
    
    // 创意蓝图部分
    if (creativeBrief) {
      html += this.generateCreativeBriefSection(creativeBrief);
    }
    
    // 视觉概念部分
    if (visualConcepts) {
      html += this.generateVisualConceptsSection(visualConcepts);
    }
    
    html += '</div>';
    return html;
  }

  /**
   * 生成视觉+前端工作流HTML
   */
  generateVisualFrontendHTML(result, projectData) {
    const { visualConcepts, frontendImplementation } = result.result || result;
    
    let html = '<div class="visual-frontend-report">';
    
    // 视觉概念部分
    if (visualConcepts) {
      html += this.generateVisualConceptsSection(visualConcepts);
    }
    
    // 前端实现部分
    if (frontendImplementation) {
      html += this.generateFrontendImplementationSection(frontendImplementation);
    }
    
    html += '</div>';
    return html;
  }

  /**
   * 生成通用报告HTML（研究分析等）
   */
  generateGeneralReportHTML(result, projectData) {
    return `
      <section class="general-report">
        <h2>📊 分析报告</h2>
        <div class="report-content">
          ${this.formatMarkdown(result.summary || JSON.stringify(result, null, 2))}
        </div>
      </section>
    `;
  }

  /**
   * 转义HTML特殊字符
   */
  escapeHtml(text) {
    if (typeof text !== 'string') {
      text = String(text);
    }
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /**
   * 获取基础HTML模板
   */
  getBaseTemplate() {
    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}} - HELIX AI系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .header .subtitle {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        .project-overview {
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .overview-item {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }
        
        section {
            background: white;
            margin-bottom: 30px;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        
        section h2 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 25px;
            margin: 0;
            font-size: 1.5em;
        }
        
        .creative-content, .visual-content, .frontend-content, .qa-content, .report-content {
            padding: 25px;
        }
        
        .code-block {
            margin: 20px 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .code-header {
            background: #2c3e50;
            color: white;
            padding: 10px 15px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .code-block pre {
            background: #f4f4f4;
            padding: 20px;
            overflow-x: auto;
            margin: 0;
        }
        
        .code-block code {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        .qa-status-banner {
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .qa-passed {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            color: white;
        }
        
        .qa-failed {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
            color: white;
        }
        
        .qa-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .metric {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .metric.passed {
            background: #d4edda;
            border: 1px solid #c3e6cb;
        }
        
        .metric.failed {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
        }
        
        .metric-label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 1.2em;
        }
        
        .validation-item {
            background: #f8f9fa;
            margin: 15px 0;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #ddd;
        }
        
        .validation-item.passed {
            background: #d4edda;
            border-left-color: #28a745;
        }
        
        .validation-item.failed {
            background: #f8d7da;
            border-left-color: #dc3545;
        }
        
        .issues ul {
            margin-top: 10px;
            padding-left: 20px;
        }
        
        .issues li {
            margin: 5px 0;
        }
        
        .content-text p {
            margin-bottom: 15px;
        }
        
        .content-text h1, .content-text h2, .content-text h3 {
            margin: 25px 0 15px 0;
            color: #2c3e50;
        }
        
        .content-json {
            background: #f4f4f4;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .overview-grid {
                grid-template-columns: 1fr;
            }
            
            .qa-metrics {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{{TITLE}}</h1>
            <div class="subtitle">由HELIX AI多元智能体系统生成</div>
        </header>
        
        {{OVERVIEW}}
        
        <main>
            {{CONTENT}}
        </main>
        
        <footer class="footer">
            <p>生成时间: {{TIMESTAMP}}</p>
            <p>Powered by HELIX Orchestrator - 多元智能体协作平台</p>
        </footer>
    </div>
</body>
</html>`;
  }
}

module.exports = { HTMLGenerator };