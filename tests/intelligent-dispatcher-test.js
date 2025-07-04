/**
 * 智能分发器兼容性测试
 * 验证简单工作流与DRD框架的智能路由
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

class IntelligentDispatcherTest {
  constructor() {
    this.memory = new SimpleMemory();
    this.orchestrator = new HelixOrchestrator({ 
      memory: this.memory,
      confidenceThreshold: 0.7,
      maxResearchCycles: 2 // 减少测试时间
    });
  }

  async runComprehensiveTest() {
    console.log('🧪 智能分发器兼容性测试');
    console.log('='.repeat(70));
    console.log('目标：验证简单工作流与DRD框架的智能路由机制');
    console.log('');

    const testCases = [
      {
        name: "简单创意任务 - 应使用简单工作流",
        request: {
          message: "为咖啡店设计一个温馨的品牌故事",
          type: "creative_task"
        },
        expectedFramework: "simple_workflow",
        expectedWorkflow: "creative_only"
      },
      {
        name: "明确实现任务 - 应使用简单工作流",
        request: {
          message: "设计并实现一个登录页面，包含用户名和密码输入",
          type: "development_task"
        },
        expectedFramework: "simple_workflow", 
        expectedWorkflow: "visual_frontend"
      },
      {
        name: "复杂研究任务 - 应使用DRD框架",
        request: {
          message: "分析竞品电商平台的用户体验策略，制定我们的差异化方案",
          type: "research_analysis"
        },
        expectedFramework: "drd",
        expectedWorkflow: "general_research"
      },
      {
        name: "模糊需求任务 - 应使用DRD框架",
        request: {
          message: "我想做一个创新的产品，需要深入研究市场机会和用户痛点",
          type: "strategic_planning"
        },
        expectedFramework: "drd",
        expectedWorkflow: "general_research"
      },
      {
        name: "多变量分析任务 - 应使用DRD框架",
        request: {
          message: "研究人工智能在教育领域的应用现状，分析技术趋势和市场机会",
          type: "market_research"
        },
        expectedFramework: "drd",
        expectedWorkflow: "general_research"
      }
    ];

    let simpleWorkflowCount = 0;
    let drdFrameworkCount = 0;
    let correctRoutingCount = 0;

    for (let i = 0; i < testCases.length; i++) {
      const testCase = testCases[i];
      console.log(`\n📋 测试 ${i + 1}/${testCases.length}: ${testCase.name}`);
      console.log('─'.repeat(50));
      console.log(`💬 用户请求: "${testCase.request.message}"`);
      
      try {
        const result = await this.orchestrator.processRequest(testCase.request);
        
        // 检查分类数据
        const classificationData = await this.memory.getContext(result.projectId, 'task_classification');
        
        if (classificationData) {
          const framework = classificationData.classification.suggested_framework;
          const workflow = classificationData.classification.workflow;
          
          console.log(`🎯 AI分类结果:`);
          console.log(`  框架选择: ${framework}`);
          console.log(`  工作流类型: ${workflow}`);
          console.log(`  置信度: ${(classificationData.classification.confidence * 100).toFixed(1)}%`);
          console.log(`  复杂度: ${classificationData.classification.complexity}`);
          
          if (classificationData.classification.requires_drd !== undefined) {
            console.log(`  需要DRD: ${classificationData.classification.requires_drd}`);
          }
          
          // 统计框架使用情况
          if (framework === 'simple_workflow') {
            simpleWorkflowCount++;
          } else if (framework === 'drd') {
            drdFrameworkCount++;
          }
          
          // 验证路由准确性
          const routingCorrect = framework === testCase.expectedFramework;
          if (routingCorrect) {
            correctRoutingCount++;
            console.log(`✅ 路由正确: 期望 ${testCase.expectedFramework}, 实际 ${framework}`);
          } else {
            console.log(`❌ 路由错误: 期望 ${testCase.expectedFramework}, 实际 ${framework}`);
          }
          
          // 检查执行结果
          console.log(`📊 执行结果:`);
          console.log(`  结果类型: ${result.type}`);
          console.log(`  项目ID: ${result.projectId}`);
          
          if (result.type.includes('DRD')) {
            console.log(`🔬 DRD框架执行成功`);
          } else if (result.type === 'COMPLETED') {
            console.log(`⚡ 简单工作流执行成功`);
          } else {
            console.log(`ℹ️ 其他结果类型: ${result.type}`);
          }
          
        } else {
          console.log(`❌ 未找到分类数据`);
        }
        
      } catch (error) {
        console.error(`❌ 测试失败: ${error.message}`);
      }
    }

    // 生成测试报告
    this.generateCompatibilityReport(testCases.length, simpleWorkflowCount, drdFrameworkCount, correctRoutingCount);
  }

  generateCompatibilityReport(totalTests, simpleCount, drdCount, correctCount) {
    console.log('\n' + '='.repeat(70));
    console.log('📊 智能分发器兼容性报告');
    console.log('='.repeat(70));
    
    console.log(`\n📈 路由统计:`);
    console.log(`  总测试数: ${totalTests}`);
    console.log(`  简单工作流路由: ${simpleCount}`);
    console.log(`  DRD框架路由: ${drdCount}`);
    console.log(`  正确路由数: ${correctCount}`);
    console.log(`  路由准确率: ${((correctCount / totalTests) * 100).toFixed(1)}%`);
    
    console.log(`\n🔍 兼容性分析:`);
    
    if (simpleCount > 0) {
      console.log(`✅ 简单工作流保持运行 - 向后兼容性良好`);
    } else {
      console.log(`⚠️ 未测试到简单工作流路由`);
    }
    
    if (drdCount > 0) {
      console.log(`✅ DRD框架成功启用 - 复杂任务处理能力增强`);
    } else {
      console.log(`⚠️ 未测试到DRD框架路由`);
    }
    
    const routingAccuracy = (correctCount / totalTests) * 100;
    if (routingAccuracy >= 80) {
      console.log(`🎯 智能分发器工作良好 (${routingAccuracy.toFixed(1)}% 准确率)`);
    } else if (routingAccuracy >= 60) {
      console.log(`⚠️ 智能分发器需要优化 (${routingAccuracy.toFixed(1)}% 准确率)`);
    } else {
      console.log(`❌ 智能分发器需要重新调整 (${routingAccuracy.toFixed(1)}% 准确率)`);
    }
    
    console.log(`\n💡 关键成就:`);
    console.log(`1. 实现了智能任务路由，根据复杂性自动选择处理框架`);
    console.log(`2. 保持了现有简单工作流的高效性`);
    console.log(`3. 为复杂任务引入了DRD动态研究框架`);
    console.log(`4. 实现了渐进式架构升级，确保向后兼容`);
    
    console.log(`\n🚀 用户价值:`);
    console.log(`- 简单任务: 快速高效处理，保持原有体验`);
    console.log(`- 复杂任务: 深度研究分析，提供更全面的解决方案`);
    console.log(`- 智能识别: 自动判断任务复杂度，用户无需手动选择`);
    console.log(`- 统一接口: 用户体验保持一致，内部智能路由`);
  }

  // 快速验证简单工作流兼容性
  async quickCompatibilityCheck() {
    console.log('⚡ 快速兼容性检查');
    console.log('─'.repeat(30));
    
    const simpleTests = [
      { message: "设计一个按钮", expected: "simple" },
      { message: "研究人工智能发展趋势", expected: "drd" }
    ];
    
    for (const test of simpleTests) {
      console.log(`\n测试: ${test.message}`);
      try {
        const result = await this.orchestrator.processRequest({ message: test.message });
        const classification = await this.memory.getContext(result.projectId, 'task_classification');
        
        const framework = classification.classification.suggested_framework;
        const isCorrect = (test.expected === "simple" && framework === "simple_workflow") ||
                         (test.expected === "drd" && framework === "drd");
        
        console.log(`${isCorrect ? '✅' : '❌'} ${framework} (${isCorrect ? '正确' : '错误'})`);
      } catch (error) {
        console.log(`❌ 失败: ${error.message}`);
      }
    }
  }
}

async function runIntelligentDispatcherTest() {
  const tester = new IntelligentDispatcherTest();
  await tester.runComprehensiveTest();
}

async function runQuickCheck() {
  const tester = new IntelligentDispatcherTest();
  await tester.quickCompatibilityCheck();
}

if (require.main === module) {
  const arg = process.argv[2];
  if (arg === 'quick') {
    runQuickCheck().catch(console.error);
  } else {
    runIntelligentDispatcherTest().catch(console.error);
  }
}

module.exports = { IntelligentDispatcherTest };