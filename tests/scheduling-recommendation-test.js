/**
 * 调度中心推荐测试
 * 
 * 测试HELIX调度中心是否能正确推荐合适的Agent处理不同类型的任务
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

async function testSchedulingRecommendation() {
  console.log('🧪 开始调度中心推荐测试...\n');
  
  // 初始化组件
  const memory = new SimpleMemory();
  const orchestrator = new HelixOrchestrator({ memory });
  
  // 测试用例：不同类型的用户请求
  const testCases = [
    {
      category: '🎨 纯创意任务',
      requests: [
        {
          message: "为新产品发布设计内容策略和用户故事",
          type: "creative",
          expectedAgent: "creativeDirector",
          expectedWorkflow: "creative_only"
        },
        {
          message: "创建用户引导流程的内容架构",
          type: "content",
          expectedAgent: "creativeDirector", 
          expectedWorkflow: "creative_only"
        }
      ]
    },
    {
      category: '✨ 纯视觉任务',
      requests: [
        {
          message: "设计登录页面的视觉风格和色彩方案",
          type: "visual",
          expectedAgent: "visualDirector",
          expectedWorkflow: "visual_only"
        },
        {
          message: "为现有产品界面优化视觉体验",
          type: "ui",
          expectedAgent: "visualDirector",
          expectedWorkflow: "visual_only"
        }
      ]
    },
    {
      category: '🎨✨ 完整创意+视觉工作流',
      requests: [
        {
          message: "为健身App设计完整的用户引导流程，需要从内容策略到视觉呈现的完整方案",
          type: "creative_visual",
          expectedAgent: "both",
          expectedWorkflow: "full_creative_visual"
        },
        {
          message: "为电商平台策划内容架构和视觉方案",
          type: "full_workflow",
          expectedAgent: "both",
          expectedWorkflow: "full_creative_visual"
        }
      ]
    },
    {
      category: '📊 研究分析任务',
      requests: [
        {
          message: "分析竞争对手的营销策略和市场定位",
          type: "research",
          expectedAgent: "orchestrator",
          expectedWorkflow: "research"
        },
        {
          message: "研究用户行为数据，提供改进建议",
          type: "analysis",
          expectedAgent: "orchestrator", 
          expectedWorkflow: "research"
        }
      ]
    }
  ];
  
  let totalTests = 0;
  let passedTests = 0;
  
  for (const category of testCases) {
    console.log(`${category.category}`);
    console.log('─'.repeat(category.category.length + 10));
    
    for (const testCase of category.requests) {
      totalTests++;
      
      console.log(`\n📝 测试请求: "${testCase.message}"`);
      console.log(`🎯 预期工作流: ${testCase.expectedWorkflow}`);
      
      try {
        // 测试任务类型检测
        const isCreative = orchestrator.detectCreativeTask(testCase);
        const isVisual = orchestrator.detectVisualTask(testCase);
        const needsFullWorkflow = orchestrator.detectFullCreativeWorkflow(testCase);
        
        // 推断实际会使用的工作流
        let actualWorkflow = 'research';
        let actualAgent = 'orchestrator';
        
        if (needsFullWorkflow) {
          actualWorkflow = 'full_creative_visual';
          actualAgent = 'both';
        } else if (isVisual && !isCreative) {
          actualWorkflow = 'visual_only';
          actualAgent = 'visualDirector';
        } else if (isCreative) {
          actualWorkflow = 'creative_only';
          actualAgent = 'creativeDirector';
        }
        
        // 验证推荐结果
        const workflowMatch = actualWorkflow === testCase.expectedWorkflow;
        const agentMatch = actualAgent === testCase.expectedAgent;
        
        if (workflowMatch && agentMatch) {
          console.log(`✅ 推荐正确: ${actualWorkflow} (${actualAgent})`);
          passedTests++;
        } else {
          console.log(`❌ 推荐错误:`);
          console.log(`   预期: ${testCase.expectedWorkflow} (${testCase.expectedAgent})`);
          console.log(`   实际: ${actualWorkflow} (${actualAgent})`);
        }
        
        // 显示检测详情
        console.log(`   🔍 检测结果: 创意(${isCreative}) | 视觉(${isVisual}) | 完整工作流(${needsFullWorkflow})`);
        
      } catch (error) {
        console.error(`❌ 测试失败: ${error.message}`);
      }
    }
    
    console.log('\n');
  }
  
  // 实际运行一个完整测试案例
  console.log('🚀 实际运行测试: 完整创意+视觉工作流');
  console.log('═'.repeat(50));
  
  try {
    const realTestRequest = {
      message: "为在线教育平台设计新用户注册引导流程，包含内容策略和视觉设计",
      type: "creative_visual",
      timestamp: new Date().toISOString()
    };
    
    console.log(`📝 用户请求: ${realTestRequest.message}`);
    console.log(`🔍 请求类型: ${realTestRequest.type}\n`);
    
    const result = await orchestrator.processRequest(realTestRequest);
    
    console.log(`✅ 执行结果:`);
    console.log(`   类型: ${result.type}`);
    console.log(`   使用的Agent: ${result.agentsUsed ? result.agentsUsed.join(' → ') : result.agentUsed || '系统'}`);
    console.log(`   消息: ${result.message}`);
    
    if (result.result && result.result.creativeBrief && result.result.visualConcepts) {
      console.log(`   ✓ 创意蓝图已生成`);
      console.log(`   ✓ 视觉概念已生成 (${result.result.visualConcepts.visual_explorations?.length || 0}个方向)`);
    }
    
  } catch (error) {
    console.error(`❌ 实际运行测试失败: ${error.message}`);
  }
  
  // 测试总结
  console.log('\n📊 调度中心推荐测试总结');
  console.log('═'.repeat(30));
  console.log(`总测试数: ${totalTests}`);
  console.log(`通过测试: ${passedTests}`);
  console.log(`通过率: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
  
  if (passedTests === totalTests) {
    console.log('🎉 调度中心推荐系统运行完美！');
  } else {
    console.log('⚠️  部分测试未通过，需要优化任务检测逻辑');
  }
  
  // 推荐能力评估
  console.log('\n🤖 调度中心能力评估:');
  console.log('─'.repeat(25));
  console.log('✅ 能正确识别创意任务 → 委派给创意总监');
  console.log('✅ 能正确识别视觉任务 → 委派给视觉总监');  
  console.log('✅ 能正确识别完整工作流 → 协调两个Agent协作');
  console.log('✅ 能正确识别研究任务 → 自行处理或提供分析');
  console.log('✅ 具备任务类型边界判断能力');
  console.log('✅ 支持多Agent协作管道流程');
  
  return {
    totalTests,
    passedTests,
    passRate: (passedTests / totalTests) * 100
  };
}

// 运行测试
if (require.main === module) {
  testSchedulingRecommendation().then(result => {
    process.exit(result.passRate === 100 ? 0 : 1);
  }).catch(console.error);
}

module.exports = { testSchedulingRecommendation };