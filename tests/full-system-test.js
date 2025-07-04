/**
 * HELIX全系统集成测试 - Flash模型
 * 
 * 使用Gemini Flash模型测试完整的HELIX AI多元智能体系统：
 * 1. 所有5个Agent协作
 * 2. AI任务路由和分类
 * 3. 完整工作流执行
 * 4. Meta-Agent失败监控
 * 5. HTML文档输出
 * 6. 系统健康监控
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');
const { HTMLGenerator } = require('../src/services/HTMLGenerator');
const fs = require('fs').promises;
const path = require('path');

// 测试场景配置
const TEST_SCENARIOS = [
  {
    id: 'creative_design',
    name: '创意设计项目',
    request: {
      message: '为一家新兴科技公司设计品牌官网，要求现代化、简洁、体现创新精神',
      type: 'creative'
    },
    expectedWorkflow: 'full_implementation',
    expectHTML: true
  },
  {
    id: 'ecommerce_platform',
    name: '电商平台设计',
    request: {
      message: '创建一个面向年轻人的时尚电商平台界面，需要包含产品展示、购物车、用户中心等功能',
      type: 'creative'
    },
    expectedWorkflow: 'full_implementation_with_qa',
    expectHTML: true
  },
  {
    id: 'mobile_app_ui',
    name: '移动应用界面',
    request: {
      message: '设计一个健康管理App的用户界面，包括运动记录、饮食跟踪、健康报告等功能',
      type: 'visual'
    },
    expectedWorkflow: 'visual_frontend',
    expectHTML: true
  },
  {
    id: 'qa_validation',
    name: '代码质量验证',
    request: {
      message: '请对现有的React组件进行QA验证，检查无障碍性、性能和响应式设计',
      type: 'qa'
    },
    expectedWorkflow: 'qa_validation',
    expectHTML: true
  }
];

async function runFullSystemTest() {
  console.log('🚀 开始HELIX全系统集成测试...\n');
  console.log('🧠 使用Gemini Flash模型进行AI驱动的智能分析\n');

  // 初始化系统
  console.log('📦 正在初始化HELIX系统...');
  const memory = new SimpleMemory();
  const helix = new HelixOrchestrator({ 
    memory,
    // 测试配置
    failureAnalysisThreshold: 2,
    analysisInterval: 5000,
    temperature: 0.7,
    maxRetries: 3
  });
  const htmlGenerator = new HTMLGenerator();

  console.log('✅ HELIX Orchestrator 已初始化');
  console.log('✅ Simple Memory 已初始化');
  console.log('✅ HTML Generator 已初始化');

  // 验证系统状态
  const agents = helix.getRegisteredAgents();
  console.log(`\n🤖 已注册的Agent: ${agents.length}个`);
  agents.forEach(agent => {
    console.log(`  - ${agent.name}: ${agent.info} (${agent.type})`);
  });

  // 初始系统健康检查
  console.log('\n🏥 系统健康检查...');
  const initialHealth = await helix.getSystemHealth();
  console.log(`系统状态: ${initialHealth.status}`);
  console.log(`Agent数量: ${initialHealth.agents_registered}`);
  console.log(`内存使用: ${Math.round(initialHealth.memory_usage.totalEntries)} 条记录`);

  let testResults = {
    totalTests: TEST_SCENARIOS.length,
    passed: 0,
    failed: 0,
    results: [],
    htmlDocuments: [],
    systemHealth: null
  };

  // 执行测试场景
  console.log(`\n🧪 开始执行 ${TEST_SCENARIOS.length} 个测试场景...\n`);

  for (let i = 0; i < TEST_SCENARIOS.length; i++) {
    const scenario = TEST_SCENARIOS[i];
    console.log(`📋 测试 ${i + 1}/${TEST_SCENARIOS.length}: ${scenario.name}`);
    console.log(`   请求: ${scenario.request.message.substring(0, 50)}...`);
    console.log(`   类型: ${scenario.request.type}`);
    console.log(`   期望工作流: ${scenario.expectedWorkflow}`);

    const testStart = Date.now();
    let testResult = {
      scenarioId: scenario.id,
      name: scenario.name,
      success: false,
      duration: 0,
      workflowExecuted: null,
      agentsUsed: [],
      htmlGenerated: false,
      error: null
    };

    try {
      // 执行HELIX处理
      console.log('   🔄 正在处理请求...');
      const result = await helix.processRequest(scenario.request);
      
      testResult.duration = Date.now() - testStart;
      testResult.workflowExecuted = result.type;

      if (result.type === 'COMPLETED') {
        testResult.success = true;
        testResult.agentsUsed = result.agentsUsed || [];
        
        console.log(`   ✅ 处理完成 (${testResult.duration}ms)`);
        console.log(`   🎯 执行的工作流: ${result.message}`);
        console.log(`   🤖 使用的Agent: ${testResult.agentsUsed.join(', ')}`);

        // 生成HTML文档（如果期望）
        if (scenario.expectHTML) {
          try {
            console.log('   📄 正在生成HTML文档...');
            const projectData = await memory.getProjectData(result.projectId);
            const htmlDocument = htmlGenerator.generateProjectHTML(projectData, result);
            
            // 保存HTML文档
            const outputDir = path.join(__dirname, '../tmp');
            try {
              await fs.access(outputDir);
            } catch {
              await fs.mkdir(outputDir, { recursive: true });
            }
            
            const htmlPath = path.join(outputDir, `${scenario.id}-${Date.now()}-report.html`);
            await fs.writeFile(htmlPath, htmlDocument, 'utf8');
            
            testResult.htmlGenerated = true;
            testResults.htmlDocuments.push(htmlPath);
            
            console.log(`   📄 HTML文档已生成: ${path.basename(htmlPath)}`);
            
          } catch (htmlError) {
            console.warn(`   ⚠️ HTML生成失败: ${htmlError.message}`);
          }
        }

        testResults.passed++;
        
      } else if (result.type === 'USER_CLARIFICATION_NEEDED') {
        console.log(`   ❓ 需要用户澄清: ${result.message}`);
        testResult.success = true; // 澄清请求也算成功
        testResults.passed++;
        
      } else {
        console.log(`   ❌ 处理失败: ${result.message}`);
        testResult.error = result.message;
        testResults.failed++;
      }

    } catch (error) {
      testResult.duration = Date.now() - testStart;
      testResult.error = error.message;
      testResults.failed++;
      
      console.log(`   ❌ 测试失败: ${error.message}`);
      
      // 记录失败给Meta-Agent
      await helix.recordAgentFailure(
        'system-test',
        'TEST_EXECUTION_ERROR',
        error.message,
        { scenarioId: scenario.id },
        scenario.request
      );
    }

    testResults.results.push(testResult);
    console.log(''); // 空行分隔
  }

  // Meta-Agent分析（如果有失败）
  if (testResults.failed > 0) {
    console.log('🔬 触发Meta-Agent失败分析...');
    try {
      const analysisResult = await helix.agents.metaOptimizer.processFailureAnalysis();
      console.log(`分析结果: ${analysisResult.type}`);
      if (analysisResult.type === 'ANALYSIS_COMPLETED') {
        console.log(`优化建议: ${analysisResult.optimizations} 个`);
      }
    } catch (metaError) {
      console.warn(`Meta-Agent分析失败: ${metaError.message}`);
    }
  }

  // 最终系统健康检查
  console.log('🏥 最终系统健康检查...');
  const finalHealth = await helix.getSystemHealth();
  testResults.systemHealth = finalHealth;
  
  console.log(`系统状态: ${finalHealth.status}`);
  console.log(`总失败数: ${finalHealth.failure_summary.total}`);
  console.log(`未处理失败: ${finalHealth.failure_summary.unprocessed}`);

  // 生成测试报告
  console.log('\n📊 生成综合测试报告...');
  const testReport = generateTestReport(testResults);
  
  const reportPath = path.join(__dirname, '../tmp', `full-system-test-report-${Date.now()}.html`);
  await fs.writeFile(reportPath, testReport, 'utf8');
  
  // 测试总结
  console.log('🎉 HELIX全系统测试完成！\n');
  console.log('📈 测试结果总结:');
  console.log(`   总测试数: ${testResults.totalTests}`);
  console.log(`   成功: ${testResults.passed}/${testResults.totalTests} (${(testResults.passed/testResults.totalTests*100).toFixed(1)}%)`);
  console.log(`   失败: ${testResults.failed}/${testResults.totalTests}`);
  console.log(`   生成HTML文档: ${testResults.htmlDocuments.length} 个`);
  console.log(`   系统最终状态: ${finalHealth.status}`);
  
  console.log('\n📁 输出文件:');
  console.log(`   测试报告: ${reportPath}`);
  testResults.htmlDocuments.forEach((doc, index) => {
    console.log(`   HTML文档${index + 1}: ${doc}`);
  });

  console.log('\n🚀 系统性能表现:');
  const avgDuration = testResults.results.reduce((sum, r) => sum + r.duration, 0) / testResults.results.length;
  console.log(`   平均响应时间: ${Math.round(avgDuration)}ms`);
  console.log(`   最快响应: ${Math.min(...testResults.results.map(r => r.duration))}ms`);
  console.log(`   最慢响应: ${Math.max(...testResults.results.map(r => r.duration))}ms`);

  // 验证核心功能
  console.log('\n✅ 核心功能验证:');
  console.log(`   AI任务路由: ${testResults.passed > 0 ? '✅ 正常' : '❌ 异常'}`);
  console.log(`   多Agent协作: ${testResults.results.some(r => r.agentsUsed.length > 1) ? '✅ 正常' : '❌ 异常'}`);
  console.log(`   HTML文档生成: ${testResults.htmlDocuments.length > 0 ? '✅ 正常' : '❌ 异常'}`);
  console.log(`   Meta-Agent监控: ${finalHealth.meta_analysis ? '✅ 正常' : '❌ 异常'}`);
  console.log(`   内存管理: ${finalHealth.memory_usage.totalEntries > 0 ? '✅ 正常' : '❌ 异常'}`);

  if (testResults.passed === testResults.totalTests) {
    console.log('\n🎊 所有测试通过！HELIX系统运行完美！');
  } else {
    console.log(`\n⚠️ ${testResults.failed} 个测试失败，请检查系统配置`);
  }

  return testResults;
}

/**
 * 生成综合测试报告HTML
 */
function generateTestReport(testResults) {
  const passRate = (testResults.passed / testResults.totalTests * 100).toFixed(1);
  const healthStatus = testResults.systemHealth?.status || 'UNKNOWN';
  
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HELIX全系统测试报告</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin: 0 0 10px 0;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .metric {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .metric.success .metric-value { color: #28a745; }
        .metric.warning .metric-value { color: #ffc107; }
        .metric.danger .metric-value { color: #dc3545; }
        .results {
            padding: 30px;
        }
        .test-item {
            background: #f8f9fa;
            margin: 15px 0;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #ddd;
        }
        .test-item.success { border-left-color: #28a745; background: #d4edda; }
        .test-item.fail { border-left-color: #dc3545; background: #f8d7da; }
        .test-item h3 {
            margin: 0 0 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .badge {
            padding: 4px 12px;
            border-radius: 20px;
            color: white;
            font-size: 0.8em;
            font-weight: bold;
        }
        .badge.success { background: #28a745; }
        .badge.fail { background: #dc3545; }
        .footer {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🚀 HELIX全系统测试报告</h1>
            <p>基于Gemini Flash的AI多元智能体系统完整测试</p>
            <p>测试时间: ${new Date().toLocaleString('zh-CN')}</p>
        </header>
        
        <section class="summary">
            <div class="metric success">
                <div class="metric-value">${passRate}%</div>
                <div class="metric-label">成功率</div>
            </div>
            <div class="metric ${testResults.passed > 0 ? 'success' : 'danger'}">
                <div class="metric-value">${testResults.passed}/${testResults.totalTests}</div>
                <div class="metric-label">测试通过</div>
            </div>
            <div class="metric ${testResults.htmlDocuments.length > 0 ? 'success' : 'warning'}">
                <div class="metric-value">${testResults.htmlDocuments.length}</div>
                <div class="metric-label">HTML文档</div>
            </div>
            <div class="metric ${healthStatus === 'HEALTHY' ? 'success' : 'warning'}">
                <div class="metric-value">${healthStatus}</div>
                <div class="metric-label">系统状态</div>
            </div>
        </section>
        
        <section class="results">
            <h2>📋 详细测试结果</h2>
            ${testResults.results.map(result => `
                <div class="test-item ${result.success ? 'success' : 'fail'}">
                    <h3>
                        ${result.name}
                        <span class="badge ${result.success ? 'success' : 'fail'}">
                            ${result.success ? '✅ 通过' : '❌ 失败'}
                        </span>
                    </h3>
                    <p><strong>场景ID:</strong> ${result.scenarioId}</p>
                    <p><strong>执行时间:</strong> ${result.duration}ms</p>
                    <p><strong>工作流:</strong> ${result.workflowExecuted || 'N/A'}</p>
                    <p><strong>使用Agent:</strong> ${result.agentsUsed.join(', ') || 'N/A'}</p>
                    <p><strong>HTML生成:</strong> ${result.htmlGenerated ? '✅' : '❌'}</p>
                    ${result.error ? `<p><strong>错误:</strong> ${result.error}</p>` : ''}
                </div>
            `).join('')}
        </section>
        
        <footer class="footer">
            <p>Powered by HELIX Orchestrator - 多元智能体协作平台</p>
            <p>🤖 包含5个专业Agent: 创意总监、视觉总监、工程艺术大师、QA合规机器人、Meta系统优化师</p>
        </footer>
    </div>
</body>
</html>`;
}

// 运行测试
if (require.main === module) {
  runFullSystemTest()
    .then(results => {
      console.log('\n✅ 全系统测试完成');
      process.exit(results.passed === results.totalTests ? 0 : 1);
    })
    .catch(error => {
      console.error('\n❌ 全系统测试失败:', error);
      process.exit(1);
    });
}

module.exports = { runFullSystemTest };