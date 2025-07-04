/**
 * 任务委派决策机制演示
 * 
 * 展示HELIX调度中心如何分析用户请求并决定委派给哪个Agent或工作流
 */

// 模拟当前HELIX的任务检测逻辑
class TaskDelegationDemo {
  constructor() {
    this.agents = {
      creativeDirector: { name: "创意总监", specialization: "内容策略、用户体验" },
      visualDirector: { name: "视觉总监", specialization: "UI/UX设计、视觉概念" },
      engineeringArtist: { name: "工程艺术大师", specialization: "前端实现、代码开发" }
    };
  }

  /**
   * 核心任务委派决策引擎
   */
  async delegateTask(userRequest) {
    console.log('🎯 任务委派决策开始');
    console.log('─'.repeat(50));
    console.log(`用户请求: "${userRequest.message}"`);
    console.log(`请求类型: ${userRequest.type || '未指定'}`);
    console.log('');

    // 第一步：任务类型检测
    const taskAnalysis = this.analyzeTaskRequirements(userRequest);
    console.log('📊 任务分析结果:');
    console.log(`  创意需求: ${taskAnalysis.needsCreative ? '✅' : '❌'}`);
    console.log(`  视觉需求: ${taskAnalysis.needsVisual ? '✅' : '❌'}`);
    console.log(`  前端需求: ${taskAnalysis.needsFrontend ? '✅' : '❌'}`);
    console.log(`  完整工作流: ${taskAnalysis.needsFullWorkflow ? '✅' : '❌'}`);
    console.log('');

    // 第二步：工作流决策
    const workflowDecision = this.makeWorkflowDecision(taskAnalysis);
    console.log('🚀 工作流决策:');
    console.log(`  选择的工作流: ${workflowDecision.workflow}`);
    console.log(`  参与的Agent: ${workflowDecision.agents.join(' → ')}`);
    console.log(`  执行顺序: ${workflowDecision.executionOrder}`);
    console.log('');

    // 第三步：执行计划生成
    const executionPlan = this.generateExecutionPlan(workflowDecision, userRequest);
    console.log('📋 执行计划:');
    executionPlan.steps.forEach((step, index) => {
      console.log(`  ${index + 1}. ${step.action}`);
      console.log(`     负责Agent: ${step.agent}`);
      console.log(`     输入: ${step.input}`);
      console.log(`     期望输出: ${step.expectedOutput}`);
      console.log('');
    });

    return executionPlan;
  }

  /**
   * 第一步：分析任务需求
   */
  analyzeTaskRequirements(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    const type = (userRequest.type || '').toLowerCase();

    // 创意任务检测
    const creativeKeywords = [
      '内容策略', '用户故事', '创意蓝图', '叙事框架', 
      '用户体验', '内容架构', '战略规划', '品牌定位'
    ];
    const needsCreative = creativeKeywords.some(keyword => message.includes(keyword)) ||
                         message.includes('创意') || message.includes('策略');

    // 视觉任务检测
    const visualKeywords = [
      '界面设计', 'ui设计', 'ux设计', '视觉概念', '色彩方案',
      '布局设计', '组件设计', '原型设计', '视觉风格'
    ];
    const needsVisual = visualKeywords.some(keyword => message.includes(keyword)) ||
                       message.includes('视觉') || message.includes('设计');

    // 前端任务检测
    const frontendKeywords = [
      '前端实现', 'html', 'css', 'javascript', '代码实现',
      '网页开发', '响应式', '交互实现', '界面开发'
    ];
    const needsFrontend = frontendKeywords.some(keyword => message.includes(keyword)) ||
                         message.includes('实现') || message.includes('开发') || message.includes('代码');

    // 完整工作流检测
    const fullWorkflowKeywords = [
      '完整实现', '端到端', '从概念到代码', '设计并实现',
      '完整解决方案', '全流程', '包含实现'
    ];
    const needsFullWorkflow = fullWorkflowKeywords.some(keyword => message.includes(keyword)) ||
                             (needsCreative && needsVisual && needsFrontend) ||
                             type === 'full_implementation';

    return {
      needsCreative,
      needsVisual, 
      needsFrontend,
      needsFullWorkflow
    };
  }

  /**
   * 第二步：工作流决策逻辑
   */
  makeWorkflowDecision(taskAnalysis) {
    const { needsCreative, needsVisual, needsFrontend, needsFullWorkflow } = taskAnalysis;

    // 决策优先级：完整工作流 > 双Agent协作 > 单Agent任务
    
    if (needsFullWorkflow) {
      return {
        workflow: 'full_implementation_workflow',
        agents: ['创意总监', '视觉总监', '工程艺术大师'],
        executionOrder: 'sequential', // 顺序执行
        rationale: '检测到完整实现需求，需要三Agent协作'
      };
    }

    if (needsCreative && needsVisual && !needsFrontend) {
      return {
        workflow: 'creative_visual_workflow', 
        agents: ['创意总监', '视觉总监'],
        executionOrder: 'sequential',
        rationale: '需要从概念到视觉的完整设计流程'
      };
    }

    if (needsVisual && needsFrontend && !needsCreative) {
      return {
        workflow: 'visual_frontend_workflow',
        agents: ['视觉总监', '工程艺术大师'], 
        executionOrder: 'sequential',
        rationale: '基于已有概念进行视觉设计和前端实现'
      };
    }

    // 单Agent任务
    if (needsFrontend && !needsCreative && !needsVisual) {
      return {
        workflow: 'frontend_only_workflow',
        agents: ['工程艺术大师'],
        executionOrder: 'single',
        rationale: '纯前端实现任务，需要已有视觉设计'
      };
    }

    if (needsVisual && !needsCreative && !needsFrontend) {
      return {
        workflow: 'visual_only_workflow', 
        agents: ['视觉总监'],
        executionOrder: 'single',
        rationale: '纯视觉设计任务，需要已有创意蓝图'
      };
    }

    if (needsCreative) {
      return {
        workflow: 'creative_only_workflow',
        agents: ['创意总监'],
        executionOrder: 'single', 
        rationale: '创意策略和内容架构任务'
      };
    }

    // 默认回退到研究型任务
    return {
      workflow: 'research_workflow',
      agents: ['HELIX调度中心'],
      executionOrder: 'single',
      rationale: '通用研究和分析任务'
    };
  }

  /**
   * 第三步：生成具体执行计划
   */
  generateExecutionPlan(workflowDecision, userRequest) {
    const steps = [];

    switch (workflowDecision.workflow) {
      case 'full_implementation_workflow':
        steps.push({
          action: '创意总监生成创意蓝图',
          agent: '创意总监',
          input: '用户原始需求',
          expectedOutput: 'creative_brief (内容策略、用户故事、叙事框架)',
          nextAgent: '视觉总监'
        });
        steps.push({
          action: '视觉总监基于创意蓝图设计视觉概念',
          agent: '视觉总监', 
          input: 'creative_brief + 用户需求',
          expectedOutput: 'visual_concepts (3个视觉方向、设计规范)',
          nextAgent: '工程艺术大师'
        });
        steps.push({
          action: '工程艺术大师实现前端代码',
          agent: '工程艺术大师',
          input: 'visual_concepts + creative_brief',
          expectedOutput: 'frontend_implementation (HTML/CSS/JS代码)',
          nextAgent: null
        });
        break;

      case 'creative_only_workflow':
        steps.push({
          action: '创意总监生成创意策略',
          agent: '创意总监',
          input: '用户需求',
          expectedOutput: 'creative_brief (完整内容架构)',
          nextAgent: null
        });
        break;

      case 'visual_only_workflow':
        steps.push({
          action: '检查是否存在创意蓝图',
          agent: 'StateManager',
          input: 'projectId',
          expectedOutput: '前置条件验证',
          nextAgent: '视觉总监'
        });
        steps.push({
          action: '视觉总监生成视觉概念',
          agent: '视觉总监',
          input: '已有creative_brief + 用户需求',
          expectedOutput: 'visual_concepts',
          nextAgent: null
        });
        break;

      case 'frontend_only_workflow':
        steps.push({
          action: '检查是否存在视觉概念',
          agent: 'StateManager', 
          input: 'projectId',
          expectedOutput: '前置条件验证',
          nextAgent: '工程艺术大师'
        });
        steps.push({
          action: '工程艺术大师实现前端',
          agent: '工程艺术大师',
          input: '已有visual_concepts + 用户需求', 
          expectedOutput: 'frontend_implementation',
          nextAgent: null
        });
        break;

      default:
        steps.push({
          action: '通用研究和分析',
          agent: 'HELIX调度中心',
          input: '用户需求',
          expectedOutput: '研究报告和建议',
          nextAgent: null
        });
    }

    return {
      workflow: workflowDecision.workflow,
      totalSteps: steps.length,
      estimatedAgents: workflowDecision.agents.length,
      steps,
      executionType: workflowDecision.executionOrder
    };
  }
}

// 演示不同类型的任务委派
async function demonstrateTaskDelegation() {
  const delegator = new TaskDelegationDemo();

  const testCases = [
    {
      message: "为一个心理健康应用设计并实现一个温暖治愈的欢迎页面，需要传达安全、信任和希望的感觉，包含完整的前端代码实现",
      type: "full_implementation"
    },
    {
      message: "帮我设计一个电商网站的视觉风格，要求现代简约",
      type: "visual_design"
    },
    {
      message: "为在线教育平台制定内容策略和用户故事",
      type: "creative_planning"
    },
    {
      message: "将这个设计稿实现为响应式网页",
      type: "frontend_implementation"
    },
    {
      message: "分析区块链技术的发展趋势",
      type: "research"
    }
  ];

  for (let i = 0; i < testCases.length; i++) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`测试案例 ${i + 1}/${testCases.length}`);
    console.log('='.repeat(60));
    
    await delegator.delegateTask(testCases[i]);
    
    if (i < testCases.length - 1) {
      console.log('\n按Enter继续下一个测试案例...');
      // 在实际环境中可以添加暂停
    }
  }
}

// 运行演示
if (require.main === module) {
  demonstrateTaskDelegation().catch(console.error);
}

module.exports = { TaskDelegationDemo };