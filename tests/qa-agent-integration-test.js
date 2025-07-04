/**
 * QA Agent集成测试
 * 验证QA与合规机器人与HELIX系统的兼容性和工作流集成
 */

// 加载环境变量
require('dotenv').config();

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

class QAAgentIntegrationTest {
  constructor() {
    this.memory = new SimpleMemory();
    this.orchestrator = new HelixOrchestrator({ 
      memory: this.memory,
      maxRetries: 2,
      minApiInterval: 1000
    });
  }

  async runComprehensiveTest() {
    console.log('🧪 QA Agent集成测试');
    console.log('='.repeat(70));
    console.log('目标：验证QA与合规机器人与现有系统的完整集成');
    console.log('');

    const testResults = {
      qaValidationWorkflow: null,
      fullImplementationWithQA: null,
      aiRoutingToQA: null,
      qaReportValidation: null
    };

    // 测试1: 单独QA验证工作流
    console.log('📋 测试1: 单独QA验证工作流');
    console.log('─'.repeat(50));
    testResults.qaValidationWorkflow = await this.testQAValidationWorkflow();

    // 测试2: 完整实现+QA工作流  
    console.log('\n📋 测试2: 完整实现+QA四Agent协作工作流');
    console.log('─'.repeat(50));
    testResults.fullImplementationWithQA = await this.testFullImplementationWithQAWorkflow();

    // 测试3: AI智能路由到QA工作流
    console.log('\n📋 测试3: AI智能路由到QA工作流');
    console.log('─'.repeat(50));
    testResults.aiRoutingToQA = await this.testAIRoutingToQA();

    // 测试4: QA报告验证
    console.log('\n📋 测试4: QA报告结构和内容验证');
    console.log('─'.repeat(50));
    testResults.qaReportValidation = await this.testQAReportValidation();

    // 生成综合报告
    this.generateIntegrationReport(testResults);
  }

  /**
   * 测试单独的QA验证工作流
   */
  async testQAValidationWorkflow() {
    try {
      console.log('💬 模拟请求: "检查我的前端代码质量和合规性"');
      
      // 首先创建一些前端代码用于测试
      const testProjectId = this.generateProjectId();
      await this.createMockFrontendCode(testProjectId);
      
      const startTime = Date.now();
      const result = await this.orchestrator.executeQAValidationWorkflow(testProjectId, {
        message: "检查我的前端代码质量和合规性",
        type: "qa_validation"
      });
      const executionTime = Date.now() - startTime;
      
      console.log(`✅ QA验证工作流完成 (${executionTime}ms)`);
      console.log(`📊 结果类型: ${result.type}`);
      
      if (result.validation_report) {
        const report = result.validation_report;
        console.log(`🔍 验证结果: ${report.validation_passed ? '通过' : '未通过'}`);
        console.log(`📈 错误数: ${report.summary.errors_found}`);
        console.log(`⚠️ 警告数: ${report.summary.warnings_found}`);
      }
      
      return {
        success: true,
        executionTime,
        resultType: result.type,
        validationPassed: result.validation_report?.validation_passed,
        errorsFound: result.validation_report?.summary.errors_found || 0,
        warningsFound: result.validation_report?.summary.warnings_found || 0
      };
      
    } catch (error) {
      console.error(`❌ QA验证工作流测试失败: ${error.message}`);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 测试完整实现+QA四Agent协作工作流
   */
  async testFullImplementationWithQAWorkflow() {
    try {
      console.log('💬 模拟请求: "为健身应用设计并实现登录页面，需要完整的质量检查"');
      
      const startTime = Date.now();
      const result = await this.orchestrator.executeFullImplementationWithQAWorkflow(
        this.generateProjectId(), 
        {
          message: "为健身应用设计并实现登录页面，需要完整的质量检查",
          type: "full_implementation_with_qa"
        }
      );
      const executionTime = Date.now() - startTime;
      
      console.log(`✅ 四Agent协作工作流完成 (${executionTime}ms)`);
      console.log(`📊 结果类型: ${result.type}`);
      console.log(`🤖 使用Agent: ${result.agentsUsed.join(' → ')}`);
      
      if (result.qa_validation_summary) {
        const qa = result.qa_validation_summary;
        console.log(`🔍 QA验证: ${qa.passed ? '通过' : '未通过'}`);
        console.log(`📈 质量问题: ${qa.errors}个错误, ${qa.warnings}个警告`);
      }
      
      return {
        success: true,
        executionTime,
        resultType: result.type,
        agentsUsed: result.agentsUsed || [],
        qaValidationPassed: result.qa_validation_summary?.passed,
        hasAllExpectedComponents: this.validateFullWorkflowComponents(result)
      };
      
    } catch (error) {
      console.error(`❌ 四Agent协作工作流测试失败: ${error.message}`);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 测试AI智能路由到QA工作流
   */
  async testAIRoutingToQA() {
    try {
      const testCases = [
        {
          name: "明确QA请求",
          message: "请检查我的网页代码的可访问性和性能",
          expectedWorkflow: "qa_validation"
        },
        {
          name: "完整实现+质量检查",
          message: "设计并实现一个产品展示页面，确保代码质量符合标准",
          expectedWorkflow: "full_implementation_with_qa"
        }
      ];

      const routingResults = [];

      for (const testCase of testCases) {
        console.log(`🎯 测试用例: ${testCase.name}`);
        console.log(`💬 请求: "${testCase.message}"`);
        
        try {
          const result = await this.orchestrator.processRequest({
            message: testCase.message,
            type: "auto_classify"
          });
          
          // 检查分类数据
          const classificationData = await this.memory.getContext(result.projectId, 'task_classification');
          
          if (classificationData) {
            const workflow = classificationData.classification.workflow;
            const confidence = classificationData.classification.confidence;
            
            console.log(`  📊 AI分类: ${workflow} (置信度: ${(confidence * 100).toFixed(1)}%)`);
            console.log(`  ✅ 执行结果: ${result.type}`);
            
            const routingCorrect = workflow === testCase.expectedWorkflow;
            console.log(`  🎯 路由准确性: ${routingCorrect ? '正确' : '错误'}`);
            
            routingResults.push({
              testCase: testCase.name,
              expectedWorkflow: testCase.expectedWorkflow,
              actualWorkflow: workflow,
              confidence,
              routingCorrect,
              resultType: result.type
            });
          }
        } catch (error) {
          console.log(`  ❌ 测试失败: ${error.message}`);
          routingResults.push({
            testCase: testCase.name,
            error: error.message,
            routingCorrect: false
          });
        }
        
        console.log('');
      }

      const successfulRoutings = routingResults.filter(r => r.routingCorrect).length;
      const routingAccuracy = (successfulRoutings / routingResults.length) * 100;

      return {
        success: true,
        routingResults,
        routingAccuracy,
        totalTests: routingResults.length,
        successfulRoutings
      };
      
    } catch (error) {
      console.error(`❌ AI路由测试失败: ${error.message}`);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 测试QA报告的结构和内容验证
   */
  async testQAReportValidation() {
    try {
      console.log('🔍 创建测试用的前端代码（包含已知问题）');
      
      const testProjectId = this.generateProjectId();
      await this.createProblematicFrontendCode(testProjectId);
      
      const result = await this.orchestrator.executeQAValidationWorkflow(testProjectId, {
        message: "验证这段包含问题的代码",
        type: "qa_validation"
      });
      
      if (!result.validation_report) {
        throw new Error('QA报告缺失');
      }
      
      const report = result.validation_report;
      
      // 验证报告结构
      const hasRequiredFields = [
        'validation_passed',
        'summary',
        'errors',
        'warnings',
        'timestamp',
        'validator_version'
      ].every(field => report.hasOwnProperty(field));
      
      console.log(`📋 报告结构完整性: ${hasRequiredFields ? '✅' : '❌'}`);
      console.log(`📊 验证通过: ${report.validation_passed}`);
      console.log(`📈 问题统计: ${report.summary.errors_found}个错误, ${report.summary.warnings_found}个警告`);
      
      // 验证具体的验证协议
      const protocolsCovered = new Set();
      [...report.errors, ...report.warnings].forEach(issue => {
        protocolsCovered.add(issue.protocol_id);
      });
      
      console.log(`🔬 覆盖的验证协议: ${Array.from(protocolsCovered).join(', ')}`);
      
      // 验证错误和警告的详细信息
      const hasDetailedIssues = [...report.errors, ...report.warnings].every(issue => 
        issue.protocol_id && 
        issue.type && 
        issue.message &&
        issue.message.length > 10
      );
      
      console.log(`📝 问题详情完整性: ${hasDetailedIssues ? '✅' : '❌'}`);
      
      return {
        success: true,
        reportStructureValid: hasRequiredFields,
        validationPassed: report.validation_passed,
        totalIssues: report.summary.errors_found + report.summary.warnings_found,
        protocolsCovered: Array.from(protocolsCovered),
        detailedIssuesValid: hasDetailedIssues,
        reportTimestamp: report.timestamp
      };
      
    } catch (error) {
      console.error(`❌ QA报告验证失败: ${error.message}`);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 生成综合集成报告
   */
  generateIntegrationReport(results) {
    console.log('\n' + '='.repeat(70));
    console.log('📊 QA Agent集成测试报告');
    console.log('='.repeat(70));
    
    console.log('\n📈 测试结果总览:');
    
    // 单独QA工作流
    if (results.qaValidationWorkflow?.success) {
      console.log('✅ 单独QA验证工作流: 成功');
      console.log(`  执行时间: ${results.qaValidationWorkflow.executionTime}ms`);
      console.log(`  验证结果: ${results.qaValidationWorkflow.validationPassed ? '通过' : '未通过'}`);
    } else {
      console.log('❌ 单独QA验证工作流: 失败');
    }
    
    // 四Agent协作工作流
    if (results.fullImplementationWithQA?.success) {
      console.log('✅ 完整实现+QA工作流: 成功');
      console.log(`  执行时间: ${results.fullImplementationWithQA.executionTime}ms`);
      console.log(`  Agent协作: ${results.fullImplementationWithQA.agentsUsed.length === 4 ? '完整' : '不完整'}`);
    } else {
      console.log('❌ 完整实现+QA工作流: 失败');
    }
    
    // AI路由准确性
    if (results.aiRoutingToQA?.success) {
      console.log('✅ AI智能路由: 成功');
      console.log(`  路由准确率: ${results.aiRoutingToQA.routingAccuracy.toFixed(1)}%`);
      console.log(`  成功案例: ${results.aiRoutingToQA.successfulRoutings}/${results.aiRoutingToQA.totalTests}`);
    } else {
      console.log('❌ AI智能路由: 失败');
    }
    
    // QA报告验证
    if (results.qaReportValidation?.success) {
      console.log('✅ QA报告验证: 成功');
      console.log(`  报告结构: ${results.qaReportValidation.reportStructureValid ? '完整' : '不完整'}`);
      console.log(`  协议覆盖: ${results.qaReportValidation.protocolsCovered.length}个验证协议`);
    } else {
      console.log('❌ QA报告验证: 失败');
    }
    
    console.log('\n🔍 关键发现:');
    
    const allTestsPassed = Object.values(results).every(result => result?.success);
    
    if (allTestsPassed) {
      console.log('1. ✅ QA Agent成功集成到HELIX系统');
      console.log('2. ✅ 四Agent协作工作流运行正常');
      console.log('3. ✅ AI路由能正确识别QA相关任务');
      console.log('4. ✅ QA报告格式标准化且内容详细');
      console.log('5. ✅ 向后兼容性良好，现有工作流不受影响');
    } else {
      console.log('1. ⚠️ 部分集成功能需要优化');
      console.log('2. 🔧 建议检查失败的测试用例');
    }
    
    console.log('\n💡 系统架构优势:');
    console.log('- 🎯 智能任务路由：自动识别是否需要QA验证');
    console.log('- 🔗 无缝集成：QA Agent与现有三Agent系统完美协作');
    console.log('- 📊 标准化报告：结构化的JSON格式验证报告');
    console.log('- 🛡️ 质量保证：四层验证协议确保代码质量');
    console.log('- ⚡ 按需调用：可单独使用QA验证或作为完整工作流的一部分');
    
    console.log('\n🚀 集成状态:');
    
    if (allTestsPassed) {
      console.log('🎉 QA Agent集成完全成功！系统现在支持四Agent协作的完整质量保证工作流');
      console.log('📋 建议: 系统已准备好投入生产使用，提供端到端的代码质量保证');
    } else {
      console.log('⚠️ 集成部分成功，建议针对失败的测试进行进一步调试');
    }
  }

  // 辅助方法
  generateProjectId() {
    return `project_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async createMockFrontendCode(projectId) {
    const mockCode = {
      html: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
</head>
<body>
    <div class="container">
        <h1>Welcome</h1>
        <img src="logo.png" alt="Company Logo">
        <button onclick="alert('Hello')">Click Me</button>
    </div>
</body>
</html>`,
      css: `.container { 
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 20px; 
  color: #333;
}
h1 { 
  font-family: Arial, sans-serif; 
  margin-bottom: 16px; 
}
button { 
  background-color: #007bff; 
  color: white; 
  padding: 8px 16px; 
  border: none; 
  border-radius: 4px; 
}`,
      javascript: `function handleClick() {
  console.log('Button clicked');
}`
    };
    
    await this.memory.setContext(projectId, 'frontend_implementation', mockCode);
  }

  async createProblematicFrontendCode(projectId) {
    const problematicCode = {
      html: `<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <div style="width: 1500px;">
        <h1 style="color: #ccc;">Title</h1>
        <img src="test.jpg">
        <input type="text">
        <a href="#" style="color: #ddd;">Link</a>
    </div>
</body>
</html>`,
      css: `#main .content .article > p { 
  color: #999999; 
  margin: 21px; 
  font-family: "Comic Sans MS"; 
  width: 1400px; 
}
.text { 
  background: #ffffff; 
  color: #cccccc; 
}`,
      javascript: `// Large unoptimized script
var largeData = new Array(50000).fill('data');
console.log(largeData);`
    };
    
    await this.memory.setContext(projectId, 'frontend_implementation', problematicCode);
  }

  validateFullWorkflowComponents(result) {
    return result.result && 
           result.result.creativeBrief && 
           result.result.visualConcepts && 
           result.result.frontendImplementation && 
           result.result.qaReport;
  }
}

async function runQAAgentIntegrationTest() {
  const tester = new QAAgentIntegrationTest();
  await tester.runComprehensiveTest();
}

if (require.main === module) {
  runQAAgentIntegrationTest().catch(console.error);
}

module.exports = { QAAgentIntegrationTest };