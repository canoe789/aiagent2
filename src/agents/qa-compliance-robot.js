/**
 * QA与合规机器人 - QA_COMPLIANCE_BOT_V2.1
 * 
 * 专门负责代码质量检查和合规验证的Agent
 * 执行结构化的、自动化的验证程序，输出机器可读的JSON格式报告
 */

class QAComplianceRobotAgent {
  constructor(options = {}) {
    this.memory = options.memory;
    this.orchestrator = options.orchestrator;
    this.agentId = 'qa-compliance-robot';
    this.version = 'V2.1';
    
    // Agent身份和配置
    this.identity = 'QA_COMPLIANCE_BOT_V2.1';
    this.activationMode = 'ON_DEMAND';
    
    // 验证协议栈配置
    this.protocols = {
      'V-ACC-01': 'accessibility_validation',
      'V-DS-02': 'design_system_compliance',
      'V-PERF-03': 'performance_budget',
      'V-RESP-04': 'responsive_design'
    };
    
    // 默认工程约束
    this.defaultConstraints = {
      accessibility_standard: "WCAG_2.1_AA",
      performance_budget: {
        css_max_kb: 100,
        js_max_kb: 250,
        lcp_max_ms: 2500
      },
      design_system_tokens: {
        colors: {
          primary: "#007bff",
          secondary: "#6c757d",
          success: "#28a745",
          danger: "#dc3545",
          warning: "#ffc107",
          info: "#17a2b8",
          light: "#f8f9fa",
          dark: "#343a40"
        },
        spacing: {
          base: 8, // 8px base grid
          scale: [4, 8, 16, 24, 32, 48, 64, 96, 128]
        },
        typography: {
          fontFamilies: {
            sans: ["Inter", "system-ui", "sans-serif"],
            mono: ["Fira Code", "Monaco", "monospace"]
          }
        }
      },
      responsive_breakpoints: [
        "mobile: 375px",
        "tablet: 768px", 
        "desktop: 1280px"
      ]
    };
    
    console.log(`🤖 QA与合规机器人已初始化 (${this.version})`);
  }

  /**
   * 主要处理入口 - 执行代码验证任务
   */
  async processTask(projectId, userRequest) {
    console.log(`🔍 QA合规机器人开始处理任务: ${projectId}`);
    
    try {
      // 从记忆库获取前端实现代码
      const frontendCode = await this.memory.getContext(projectId, 'frontend_implementation');
      
      if (!frontendCode) {
        return this.createErrorResponse(projectId, 'NO_CODE_ASSETS', '未找到可验证的前端代码资产');
      }

      // 解析代码资产
      const assets = this.extractCodeAssets(frontendCode);
      
      // 获取或使用默认工程约束
      const constraints = userRequest.engineering_constraints || this.defaultConstraints;
      
      // 执行验证协议栈
      const validationResults = await this.executeValidationProtocols(assets, constraints);
      
      // 生成标准化报告
      const report = this.generateValidationReport(validationResults);
      
      // 存储验证报告到记忆库
      await this.memory.setContext(projectId, 'qa_validation_report', report);
      
      console.log(`✅ QA验证完成: 发现${report.errors.length}个错误，${report.warnings.length}个警告`);
      
      return {
        type: 'QA_VALIDATION_COMPLETED',
        projectId,
        validation_report: report,
        message: `🔍 QA验证完成: ${report.validation_passed ? '通过所有检查' : `发现${report.errors.length}个错误需要修复`}`,
        agentUsed: this.agentId
      };
      
    } catch (error) {
      console.error(`❌ QA验证失败: ${error.message}`);
      return this.createErrorResponse(projectId, 'VALIDATION_ERROR', error.message);
    }
  }

  /**
   * 从前端实现中提取代码资产
   */
  extractCodeAssets(frontendImplementation) {
    const assets = {
      html: '',
      css: '',
      javascript: ''
    };

    if (typeof frontendImplementation === 'string') {
      // 如果是纯字符串，尝试解析HTML、CSS、JS
      assets.html = this.extractHTML(frontendImplementation);
      assets.css = this.extractCSS(frontendImplementation);
      assets.javascript = this.extractJavaScript(frontendImplementation);
    } else if (typeof frontendImplementation === 'object') {
      // 如果是对象，直接使用结构化数据
      assets.html = frontendImplementation.html || frontendImplementation.htmlCode || '';
      assets.css = frontendImplementation.css || frontendImplementation.cssCode || '';
      assets.javascript = frontendImplementation.js || frontendImplementation.javascript || '';
    }

    return assets;
  }

  /**
   * 执行验证协议栈
   */
  async executeValidationProtocols(assets, constraints) {
    const results = {
      errors: [],
      warnings: []
    };

    // V-ACC-01: 可访问性验证
    const accessibilityResults = await this.validateAccessibility(assets, constraints);
    results.errors.push(...accessibilityResults.errors);
    results.warnings.push(...accessibilityResults.warnings);

    // V-DS-02: 设计系统合规性验证
    const designSystemResults = await this.validateDesignSystemCompliance(assets, constraints);
    results.errors.push(...designSystemResults.errors);
    results.warnings.push(...designSystemResults.warnings);

    // V-PERF-03: 性能预算验证
    const performanceResults = await this.validatePerformanceBudget(assets, constraints);
    results.errors.push(...performanceResults.errors);
    results.warnings.push(...performanceResults.warnings);

    // V-RESP-04: 响应式设计验证
    const responsiveResults = await this.validateResponsiveDesign(assets, constraints);
    results.errors.push(...responsiveResults.errors);
    results.warnings.push(...responsiveResults.warnings);

    return results;
  }

  /**
   * V-ACC-01: 可访问性验证
   */
  async validateAccessibility(assets, constraints) {
    const results = { errors: [], warnings: [] };
    const standard = constraints.accessibility_standard || "WCAG_2.1_AA";

    // 检查图像Alt文本
    const imgRegex = /<img[^>]*>/gi;
    const imgMatches = assets.html.match(imgRegex) || [];
    
    imgMatches.forEach((img, index) => {
      if (!img.includes('alt=') || img.includes('alt=""') || img.includes("alt=''")) {
        results.errors.push({
          protocol_id: "V-ACC-01",
          type: "MISSING_ALT_TEXT",
          message: "Image element is missing descriptive alt text for screen readers.",
          location: {
            html_element: img.substring(0, 50) + (img.length > 50 ? '...' : '')
          }
        });
      }
    });

    // 检查表单标签
    const inputRegex = /<(input|textarea|select)[^>]*>/gi;
    const inputMatches = assets.html.match(inputRegex) || [];
    
    inputMatches.forEach((input) => {
      const hasId = /id\s*=\s*["']([^"']+)["']/i.exec(input);
      if (hasId) {
        const inputId = hasId[1];
        const labelRegex = new RegExp(`<label[^>]*for\\s*=\\s*["']${inputId}["']`, 'i');
        if (!labelRegex.test(assets.html)) {
          results.errors.push({
            protocol_id: "V-ACC-01",
            type: "MISSING_FORM_LABEL",
            message: `Form input with id="${inputId}" is missing an associated label element.`,
            location: {
              html_element: input.substring(0, 50) + (input.length > 50 ? '...' : '')
            }
          });
        }
      }
    });

    // 检查链接和按钮文本
    const linkButtonRegex = /<(a|button)[^>]*>([^<]*)<\/(a|button)>/gi;
    let match;
    while ((match = linkButtonRegex.exec(assets.html)) !== null) {
      const content = match[2].trim();
      if (!content || content.length < 2) {
        results.errors.push({
          protocol_id: "V-ACC-01",
          type: "INSUFFICIENT_LINK_TEXT",
          message: "Link or button element lacks descriptive text content.",
          location: {
            html_element: match[0]
          }
        });
      }
    }

    // 检查ARIA属性使用
    const ariaRegex = /aria-[a-z]+/gi;
    const ariaMatches = assets.html.match(ariaRegex) || [];
    if (ariaMatches.length > 0) {
      results.warnings.push({
        protocol_id: "V-ACC-01",
        type: "ARIA_USAGE_REVIEW",
        message: `Found ${ariaMatches.length} ARIA attributes. Please ensure they are used correctly and are not redundant.`,
        location: {
          count: ariaMatches.length
        }
      });
    }

    return results;
  }

  /**
   * V-DS-02: 设计系统合规性验证
   */
  async validateDesignSystemCompliance(assets, constraints) {
    const results = { errors: [], warnings: [] };
    const tokens = constraints.design_system_tokens || this.defaultConstraints.design_system_tokens;

    // 检查硬编码颜色
    const colorRegex = /(#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)|hsl\([^)]+\)|hsla\([^)]+\))/g;
    const colorMatches = assets.css.match(colorRegex) || [];
    
    const allowedColors = Object.values(tokens.colors);
    
    colorMatches.forEach((color) => {
      if (!allowedColors.includes(color.toLowerCase())) {
        results.errors.push({
          protocol_id: "V-DS-02",
          type: "HARDCODED_COLOR_DETECTED",
          message: `Hardcoded color '${color}' found. It does not match any value in the design system tokens.`,
          location: {
            css_color: color
          }
        });
      }
    });

    // 检查魔法数字（间距）
    const spacingRegex = /(margin|padding|gap):\s*([0-9]+)px/g;
    let match;
    while ((match = spacingRegex.exec(assets.css)) !== null) {
      const value = parseInt(match[2]);
      const baseGrid = tokens.spacing.base;
      
      if (value % baseGrid !== 0) {
        results.warnings.push({
          protocol_id: "V-DS-02",
          type: "MAGIC_NUMBER_DETECTED",
          message: `Spacing value '${value}px' is not a multiple of the ${baseGrid}px base grid.`,
          location: {
            css_property: match[1],
            value: `${value}px`
          }
        });
      }
    }

    // 检查字体家族
    const fontFamilyRegex = /font-family:\s*([^;]+)/g;
    const fontMatches = assets.css.match(fontFamilyRegex) || [];
    
    const allowedFonts = [
      ...tokens.typography.fontFamilies.sans,
      ...tokens.typography.fontFamilies.mono
    ];

    fontMatches.forEach((fontDeclaration) => {
      const hasAllowedFont = allowedFonts.some(font => 
        fontDeclaration.toLowerCase().includes(font.toLowerCase())
      );
      
      if (!hasAllowedFont) {
        results.warnings.push({
          protocol_id: "V-DS-02",
          type: "UNAUTHORIZED_FONT_FAMILY",
          message: `Font family declaration '${fontDeclaration}' does not match design system typography tokens.`,
          location: {
            css_declaration: fontDeclaration
          }
        });
      }
    });

    return results;
  }

  /**
   * V-PERF-03: 性能预算验证
   */
  async validatePerformanceBudget(assets, constraints) {
    const results = { errors: [], warnings: [] };
    const budget = constraints.performance_budget || this.defaultConstraints.performance_budget;

    // 检查CSS文件大小
    const cssSize = Buffer.byteLength(assets.css, 'utf8');
    const cssSizeKB = cssSize / 1024;
    
    if (cssSizeKB > budget.css_max_kb) {
      results.errors.push({
        protocol_id: "V-PERF-03",
        type: "CSS_BUDGET_EXCEEDED",
        message: `CSS size ${cssSizeKB.toFixed(1)}KB exceeds budget limit of ${budget.css_max_kb}KB.`,
        location: {
          actual_size: `${cssSizeKB.toFixed(1)}KB`,
          budget_limit: `${budget.css_max_kb}KB`
        }
      });
    }

    // 检查JS文件大小
    if (assets.javascript) {
      const jsSize = Buffer.byteLength(assets.javascript, 'utf8');
      const jsSizeKB = jsSize / 1024;
      
      if (jsSizeKB > budget.js_max_kb) {
        results.errors.push({
          protocol_id: "V-PERF-03",
          type: "JS_BUDGET_EXCEEDED",
          message: `JavaScript size ${jsSizeKB.toFixed(1)}KB exceeds budget limit of ${budget.js_max_kb}KB.`,
          location: {
            actual_size: `${jsSizeKB.toFixed(1)}KB`,
            budget_limit: `${budget.js_max_kb}KB`
          }
        });
      }
    }

    // 检查CSS选择器复杂度
    const complexSelectorRegex = /#[^{]*{|[^{]*>[^{]*>[^{]*{|[^{]*\s+[^{]*\s+[^{]*\s+[^{]*{/g;
    const complexSelectors = assets.css.match(complexSelectorRegex) || [];
    
    complexSelectors.forEach((selector) => {
      const cleanSelector = selector.replace('{', '').trim();
      results.warnings.push({
        protocol_id: "V-PERF-03",
        type: "HIGH_SPECIFICITY_SELECTOR",
        message: `CSS selector '${cleanSelector}' has high specificity, which can lead to maintenance issues.`,
        location: {
          css_selector: cleanSelector
        }
      });
    });

    return results;
  }

  /**
   * V-RESP-04: 响应式设计验证
   */
  async validateResponsiveDesign(assets, constraints) {
    const results = { errors: [], warnings: [] };

    // 检查Viewport元标签
    const viewportRegex = /<meta[^>]*name\s*=\s*["']viewport["'][^>]*>/i;
    if (!viewportRegex.test(assets.html)) {
      results.errors.push({
        protocol_id: "V-RESP-04",
        type: "MISSING_VIEWPORT_META",
        message: "Missing viewport meta tag. This is required for proper responsive behavior.",
        location: {
          html_section: "<head>"
        }
      });
    }

    // 检查固定宽度元素（水平滚动风险）
    const fixedWidthRegex = /width:\s*([0-9]+)px/g;
    let match;
    while ((match = fixedWidthRegex.exec(assets.css)) !== null) {
      const width = parseInt(match[1]);
      if (width > 375) { // 大于最小移动端宽度
        results.warnings.push({
          protocol_id: "V-RESP-04",
          type: "HORIZONTAL_SCROLL_RISK",
          message: `Fixed width ${width}px may cause horizontal scrolling on mobile devices (375px).`,
          location: {
            css_property: "width",
            value: `${width}px`
          }
        });
      }
    }

    // 检查媒体查询存在性
    const mediaQueryRegex = /@media[^{]+{/g;
    const mediaQueries = assets.css.match(mediaQueryRegex) || [];
    
    if (assets.css.length > 1000 && mediaQueries.length === 0) {
      results.warnings.push({
        protocol_id: "V-RESP-04",
        type: "MISSING_MEDIA_QUERIES",
        message: "Complex CSS detected but no media queries found. Consider adding responsive breakpoints.",
        location: {
          css_size: `${(assets.css.length / 1024).toFixed(1)}KB`
        }
      });
    }

    return results;
  }

  /**
   * 生成标准化验证报告
   */
  generateValidationReport(validationResults) {
    const errors = validationResults.errors;
    const warnings = validationResults.warnings;

    return {
      validation_passed: errors.length === 0,
      summary: {
        errors_found: errors.length,
        warnings_found: warnings.length
      },
      errors,
      warnings,
      timestamp: new Date().toISOString(),
      validator_version: this.version
    };
  }

  /**
   * 创建错误响应
   */
  createErrorResponse(projectId, errorType, message) {
    return {
      type: 'QA_VALIDATION_ERROR',
      projectId,
      error: {
        type: errorType,
        message
      },
      validation_report: {
        validation_passed: false,
        summary: {
          errors_found: 1,
          warnings_found: 0
        },
        errors: [{
          protocol_id: "SYSTEM",
          type: errorType,
          message
        }],
        warnings: []
      },
      agentUsed: this.agentId
    };
  }

  /**
   * 辅助方法：从混合内容中提取HTML
   */
  extractHTML(content) {
    const htmlMatch = content.match(/<!DOCTYPE[^>]*>[\s\S]*?<\/html>/i) || 
                     content.match(/<html[^>]*>[\s\S]*?<\/html>/i) ||
                     content.match(/<div[^>]*>[\s\S]*?<\/div>/i);
    return htmlMatch ? htmlMatch[0] : content;
  }

  /**
   * 辅助方法：从混合内容中提取CSS
   */
  extractCSS(content) {
    const cssBlocks = [];
    
    // 提取 <style> 标签内容
    const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi;
    let match;
    while ((match = styleRegex.exec(content)) !== null) {
      cssBlocks.push(match[1]);
    }
    
    // 如果没有找到 <style> 标签，尝试提取看起来像CSS的内容
    if (cssBlocks.length === 0) {
      const cssLikeRegex = /[.#][a-zA-Z][^{]*{[^}]*}/g;
      const cssMatches = content.match(cssLikeRegex) || [];
      cssBlocks.push(...cssMatches);
    }
    
    return cssBlocks.join('\n');
  }

  /**
   * 辅助方法：从混合内容中提取JavaScript
   */
  extractJavaScript(content) {
    const jsBlocks = [];
    
    // 提取 <script> 标签内容
    const scriptRegex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
    let match;
    while ((match = scriptRegex.exec(content)) !== null) {
      jsBlocks.push(match[1]);
    }
    
    return jsBlocks.join('\n');
  }
}

module.exports = { QAComplianceRobotAgent };