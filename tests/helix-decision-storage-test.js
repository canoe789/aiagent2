/**
 * HELIX调度中心任务决策和数据存储测试
 * 
 * 测试当前调度中心是否能：
 * 1. 正确判断任务类型和工作流
 * 2. 正确保存决策记录到数据仓库
 * 3. 完整追踪整个决策和执行过程
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

class HelixDecisionStorageTest {
  constructor() {
    this.memory = new SimpleMemory();
    this.orchestrator = new HelixOrchestrator({ memory: this.memory });
    this.testResults = [];
  }

  /**
   * 全面测试调度中心的决策和存储能力
   */
  async runComprehensiveTest() {
    console.log('🧪 HELIX调度中心决策和存储能力测试');
    console.log('='.repeat(70));
    console.log('测试目标：');
    console.log('✓ 任务类型检测准确性');
    console.log('✓ 工作流选择正确性');
    console.log('✓ 数据持久化完整性');
    console.log('✓ 决策过程可追溯性');
    console.log('');

    const testCases = [
      {
        name: "完整实现工作流测试",
        request: {
          message: "为一个心理健康应用设计并实现一个温暖治愈的欢迎页面，需要传达安全、信任和希望的感觉，包含完整的前端代码实现",
          type: "full_implementation"
        },
        expectedWorkflow: "full_implementation",
        expectedAgents: ["creativeDirector", "visualDirector", "engineeringArtist"]
      },
      {
        name: "纯创意任务测试",
        request: {
          message: "为在线教育平台制定内容策略和用户故事架构",
          type: "creative_planning"
        },
        expectedWorkflow: "creative_only",
        expectedAgents: ["creativeDirector"]
      },
      {
        name: "纯视觉设计测试",
        request: {
          message: "设计一个现代简约风格的电商网站视觉界面",
          type: "visual_design"
        },
        expectedWorkflow: "visual_only",
        expectedAgents: ["visualDirector"]
      },
      {
        name: "关键词匹配边界测试",
        request: {
          message: "我想要一个看起来很专业的网站首页",
          type: "unclear"
        },
        expectedWorkflow: "general_research", // 当前系统可能无法正确识别
        expectedAgents: []
      },
      {
        name: "前端实现测试",
        request: {
          message: "请实现一个响应式的导航栏组件，包含HTML和CSS代码",
          type: "frontend_development"
        },
        expectedWorkflow: "frontend_only", 
        expectedAgents: ["engineeringArtist"]
      }
    ];

    for (let i = 0; i < testCases.length; i++) {
      const testCase = testCases[i];
      console.log(`\n📋 测试 ${i + 1}/${testCases.length}: ${testCase.name}`);
      console.log('─'.repeat(50));
      
      await this.testSingleCase(testCase);
      
      // 分析当前内存状态
      await this.analyzeMemoryState();
    }

    // 生成测试报告
    this.generateTestReport();
  }

  /**
   * 测试单个案例
   */
  async testSingleCase(testCase) {
    const startTime = Date.now();
    
    try {
      console.log(`📝 用户请求: "${testCase.request.message}"`);
      console.log(`📊 请求类型: ${testCase.request.type}`);
      console.log('');

      // 第一步：测试AI任务分类
      console.log('🔍 第一步：AI任务分类测试');
      const detectionResult = await this.testTaskDetection(testCase.request);
      console.log(`  AI分类结果: ${JSON.stringify(detectionResult, null, 2)}`);
      
      // 第二步：执行实际调度决策
      console.log('\n🎯 第二步：调度决策执行');
      const result = await this.orchestrator.processRequest(testCase.request);
      const executionTime = Date.now() - startTime;
      
      console.log(`  项目ID: ${result.projectId}`);
      console.log(`  最终状态: ${result.type}`);
      console.log(`  执行时间: ${executionTime}ms`);
      
      if (result.agentsUsed) {
        console.log(`  使用的Agent: ${result.agentsUsed.join(' → ')}`);
      }
      
      // 第三步：验证数据存储
      console.log('\n💾 第三步：数据存储验证');
      const storageVerification = await this.verifyDataStorage(result.projectId);
      
      // 第四步：对比预期结果
      console.log('\n📊 第四步：结果对比');
      const comparison = this.compareWithExpected(testCase, result, storageVerification);
      
      // 记录测试结果
      this.testResults.push({
        testName: testCase.name,
        request: testCase.request,
        expected: testCase,
        actual: result,
        storage: storageVerification,
        comparison,
        executionTime,
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      console.error(`❌ 测试失败: ${error.message}`);
      this.testResults.push({
        testName: testCase.name,
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  }

  /**
   * 测试AI任务分类（替代旧的关键词检测）
   */
  async testTaskDetection(userRequest) {
    try {
      // 使用AI任务分类器
      const classificationResult = await this.orchestrator.aiTaskRouter.classifyRequest(userRequest);
      
      if (classificationResult.success) {
        const classification = classificationResult.classification;
        return {
          aiClassification: classification.workflow,
          confidence: classification.confidence,
          reasoning: classification.reasoning,
          method: classificationResult.method,
          isAIBased: true
        };
      } else {
        return {
          aiClassification: 'unknown',
          confidence: 0,
          reasoning: 'AI分类失败',
          method: 'fallback',
          isAIBased: false
        };
      }
    } catch (error) {
      return {
        aiClassification: 'error',
        confidence: 0,
        reasoning: `分类错误: ${error.message}`,
        method: 'error',
        isAIBased: false
      };
    }
  }

  /**
   * 验证数据存储完整性
   */
  async verifyDataStorage(projectId) {
    console.log(`  🔍 检查项目 ${projectId} 的存储数据...`);
    
    const storedData = {
      project_info: await this.memory.getContext(projectId, 'project_info'),
      creative_brief: await this.memory.getContext(projectId, 'creative_brief'),
      visual_concepts: await this.memory.getContext(projectId, 'visual_concepts'),
      frontend_implementation: await this.memory.getContext(projectId, 'frontend_implementation'),
      planning_result: await this.memory.getContext(projectId, 'planning_result'),
      research_results: await this.memory.getContext(projectId, 'research_results')
    };

    // 分析存储的数据
    const dataAnalysis = {
      totalKeys: 0,
      existingKeys: [],
      missingKeys: [],
      dataIntegrity: true
    };

    for (const [key, value] of Object.entries(storedData)) {
      if (value !== null) {
        dataAnalysis.totalKeys++;
        dataAnalysis.existingKeys.push(key);
        console.log(`    ✅ ${key}: 已存储 (${JSON.stringify(value).length} 字符)`);
      } else {
        dataAnalysis.missingKeys.push(key);
        console.log(`    ❌ ${key}: 未存储`);
      }
    }

    // 验证数据完整性
    if (storedData.project_info) {
      const projectInfo = storedData.project_info;
      console.log(`    📊 项目状态: ${projectInfo.status}`);
      console.log(`    🕐 完成时间: ${projectInfo.completedAt}`);
      console.log(`    🔄 工作流类型: ${projectInfo.workflowType || '未指定'}`);
    }

    return { storedData, dataAnalysis };
  }

  /**
   * 对比实际结果与预期
   */
  compareWithExpected(testCase, actualResult, storageVerification) {
    const comparison = {
      workflowMatch: false,
      agentsMatch: false,
      dataStorageComplete: false,
      overallSuccess: false,
      issues: []
    };

    // 工作流匹配检查
    const actualWorkflow = this.inferWorkflowFromResult(actualResult, storageVerification);
    comparison.workflowMatch = actualWorkflow === testCase.expectedWorkflow;
    
    if (!comparison.workflowMatch) {
      comparison.issues.push(`工作流不匹配: 期望 ${testCase.expectedWorkflow}, 实际 ${actualWorkflow}`);
    }

    // Agent使用匹配检查
    const actualAgents = actualResult.agentsUsed || [];
    const expectedAgents = testCase.expectedAgents || [];
    comparison.agentsMatch = JSON.stringify(actualAgents.sort()) === JSON.stringify(expectedAgents.sort());
    
    if (!comparison.agentsMatch) {
      comparison.issues.push(`Agent使用不匹配: 期望 [${expectedAgents.join(', ')}], 实际 [${actualAgents.join(', ')}]`);
    }

    // 数据存储完整性检查
    comparison.dataStorageComplete = storageVerification.dataAnalysis.totalKeys >= expectedAgents.length;
    
    if (!comparison.dataStorageComplete) {
      comparison.issues.push(`数据存储不完整: 期望至少 ${expectedAgents.length} 个数据项, 实际 ${storageVerification.dataAnalysis.totalKeys} 个`);
    }

    // 整体成功评估
    comparison.overallSuccess = comparison.workflowMatch && comparison.agentsMatch && comparison.dataStorageComplete;

    console.log(`  工作流匹配: ${comparison.workflowMatch ? '✅' : '❌'}`);
    console.log(`  Agent匹配: ${comparison.agentsMatch ? '✅' : '❌'}`);
    console.log(`  数据存储: ${comparison.dataStorageComplete ? '✅' : '❌'}`);
    console.log(`  整体评估: ${comparison.overallSuccess ? '✅ 成功' : '❌ 失败'}`);
    
    if (comparison.issues.length > 0) {
      console.log(`  问题列表:`);
      comparison.issues.forEach(issue => console.log(`    - ${issue}`));
    }

    return comparison;
  }

  /**
   * 从结果推断实际工作流
   */
  inferWorkflowFromResult(result, storageVerification) {
    const agentsUsed = result.agentsUsed || [];
    const storedKeys = storageVerification.dataAnalysis.existingKeys;

    if (agentsUsed.length === 3 && agentsUsed.includes('creativeDirector') && 
        agentsUsed.includes('visualDirector') && agentsUsed.includes('engineeringArtist')) {
      return 'full_implementation';
    }
    
    if (agentsUsed.includes('creativeDirector') && agentsUsed.includes('visualDirector')) {
      return 'creative_visual';
    }
    
    if (agentsUsed.includes('engineeringArtist') && !agentsUsed.includes('creativeDirector')) {
      return 'frontend_only';
    }
    
    if (agentsUsed.includes('visualDirector') && !agentsUsed.includes('creativeDirector')) {
      return 'visual_only';
    }
    
    if (agentsUsed.includes('creativeDirector') && agentsUsed.length === 1) {
      return 'creative_only';
    }
    
    if (storedKeys.includes('research_results')) {
      return 'general_research';
    }

    return 'unknown';
  }

  /**
   * 分析当前内存状态
   */
  async analyzeMemoryState() {
    console.log('\n🧠 内存状态分析:');
    const stats = this.memory.getStats();
    console.log(`  总条目数: ${stats.totalEntries}`);
    console.log(`  项目数量: ${stats.totalProjects}`);
    
    // 显示所有存储的键
    console.log('  存储的数据键:');
    for (const [key, data] of this.memory.storage.entries()) {
      console.log(`    ${key} (${data.timestamp})`);
    }
  }

  /**
   * 生成测试报告
   */
  generateTestReport() {
    console.log('\n' + '='.repeat(70));
    console.log('📊 测试报告总结');
    console.log('='.repeat(70));

    const totalTests = this.testResults.length;
    const successfulTests = this.testResults.filter(r => r.comparison?.overallSuccess).length;
    const failedTests = totalTests - successfulTests;

    console.log(`\n📈 总体统计:`);
    console.log(`  总测试数: ${totalTests}`);
    console.log(`  成功测试: ${successfulTests}`);
    console.log(`  失败测试: ${failedTests}`);
    console.log(`  成功率: ${((successfulTests / totalTests) * 100).toFixed(1)}%`);

    console.log(`\n📋 详细结果:`);
    this.testResults.forEach((result, index) => {
      const status = result.comparison?.overallSuccess ? '✅' : '❌';
      console.log(`  ${index + 1}. ${status} ${result.testName}`);
      
      if (result.error) {
        console.log(`     错误: ${result.error}`);
      } else if (result.comparison && !result.comparison.overallSuccess) {
        console.log(`     问题: ${result.comparison.issues.join('; ')}`);
      }
    });

    console.log(`\n🔍 关键发现:`);
    this.analyzeKeyFindings();

    console.log(`\n💡 改进建议:`);
    this.provideImprovementSuggestions();
  }

  /**
   * 分析关键发现
   */
  analyzeKeyFindings() {
    const workflowIssues = this.testResults.filter(r => r.comparison && !r.comparison.workflowMatch);
    const agentIssues = this.testResults.filter(r => r.comparison && !r.comparison.agentsMatch);
    const storageIssues = this.testResults.filter(r => r.comparison && !r.comparison.dataStorageComplete);

    if (workflowIssues.length > 0) {
      console.log(`  ⚠️  工作流识别准确率较低 (${workflowIssues.length}/${this.testResults.length} 个案例失败)`);
    }
    
    if (agentIssues.length > 0) {
      console.log(`  ⚠️  Agent委派存在问题 (${agentIssues.length}/${this.testResults.length} 个案例不匹配)`);
    }
    
    if (storageIssues.length > 0) {
      console.log(`  ⚠️  数据存储不完整 (${storageIssues.length}/${this.testResults.length} 个案例有缺失)`);
    }

    const avgExecutionTime = this.testResults
      .filter(r => r.executionTime)
      .reduce((sum, r) => sum + r.executionTime, 0) / this.testResults.filter(r => r.executionTime).length;
    
    console.log(`  ⏱️  平均执行时间: ${avgExecutionTime.toFixed(0)}ms`);
  }

  /**
   * 提供改进建议
   */
  provideImprovementSuggestions() {
    console.log(`  1. 升级任务检测逻辑: 从关键词匹配升级到AI语义分析`);
    console.log(`  2. 增强数据验证: 添加存储完整性检查和回滚机制`);
    console.log(`  3. 改善错误处理: 提供更详细的失败原因和恢复策略`);
    console.log(`  4. 添加性能监控: 跟踪决策时间和存储延迟`);
    console.log(`  5. 实现决策审计: 记录完整的决策路径和依据`);
  }
}

// 运行测试
async function runHelixTest() {
  const tester = new HelixDecisionStorageTest();
  await tester.runComprehensiveTest();
}

if (require.main === module) {
  runHelixTest().catch(console.error);
}

module.exports = { HelixDecisionStorageTest };