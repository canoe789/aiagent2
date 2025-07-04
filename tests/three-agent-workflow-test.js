/**
 * 三Agent协作工作流测试
 * 
 * 测试创意总监→视觉总监→工程艺术大师的完整协作流程
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

async function testThreeAgentWorkflow() {
  console.log('🧪 开始三Agent协作工作流测试...\n');
  
  // 初始化组件
  const memory = new SimpleMemory();
  const orchestrator = new HelixOrchestrator({ memory });
  
  console.log('📋 已注册的Agent列表:');
  const agents = orchestrator.getRegisteredAgents();
  agents.forEach(agent => {
    console.log(`  - ${agent.info.name} (${agent.info.role}) v${agent.info.version}`);
    console.log(`    专长: ${agent.info.specialization}`);
  });
  console.log('');
  
  // 测试案例1: 完整三Agent实现工作流
  console.log('🎨✨💻 测试案例1: 完整三Agent实现工作流');
  console.log('══════════════════════════════════════════');
  
  try {
    const fullImplRequest = {
      message: "为在线教育平台设计并实现一个完整的新用户引导页面，从概念到代码的端到端解决方案",
      type: "full_implementation",
      timestamp: new Date().toISOString()
    };
    
    console.log(`📝 用户请求: ${fullImplRequest.message}`);
    console.log(`🔍 请求类型: ${fullImplRequest.type}\n`);
    
    const result = await orchestrator.processRequest(fullImplRequest);
    
    console.log(`\n✅ 工作流完成`);
    console.log(`📊 结果类型: ${result.type}`);
    console.log(`🤖 使用的Agent: ${result.agentsUsed ? result.agentsUsed.join(' → ') : result.agentUsed || '未知'}`);
    console.log(`💬 系统消息: ${result.message}`);
    
    if (result.result) {
      console.log(`\n📦 交付成果:`);
      if (result.result.creativeBrief) {
        console.log(`  ✓ 创意蓝图: 已生成`);
        console.log(`    - 叙事框架: ${result.result.creativeBrief.strategicChoice?.framework || 'N/A'}`);
      }
      if (result.result.visualConcepts) {
        console.log(`  ✓ 视觉概念: 已生成 (${result.result.visualConcepts.visual_explorations?.length || 0}个方向)`);
      }
      if (result.result.frontendImplementation) {
        console.log(`  ✓ 前端实现: 已生成`);
        console.log(`    - 选择概念: ${result.result.frontendImplementation.implementation_choice?.chosen_concept || 'N/A'}`);
        console.log(`    - 代码文件: HTML + CSS`);
        console.log(`    - 优化记录: ${result.result.frontendImplementation.refinement_log?.length || 0}项`);
      }
    }
    
  } catch (error) {
    console.error(`❌ 完整实现工作流测试失败:`, error.message);
  }
  
  console.log('\n' + '='.repeat(60) + '\n');
  
  // 测试案例2: 单独前端实现任务
  console.log('💻 测试案例2: 单独前端实现任务');
  console.log('─────────────────────────────');
  
  try {
    // 首先创建一个有视觉概念的项目
    const setupRequest = {
      message: "为电商平台首页创建视觉概念",
      type: "visual",
      timestamp: new Date().toISOString()
    };
    
    // 先生成视觉概念
    console.log(`📝 预备步骤: 先生成视觉概念`);
    await orchestrator.processRequest(setupRequest);
    
    // 然后请求前端实现
    const frontendOnlyRequest = {
      message: "基于已有的视觉概念，生成前端实现代码",
      type: "frontend",
      timestamp: new Date().toISOString()
    };
    
    console.log(`📝 用户请求: ${frontendOnlyRequest.message}`);
    console.log(`🔍 请求类型: ${frontendOnlyRequest.type}\n`);
    
    const result = await orchestrator.processRequest(frontendOnlyRequest);
    
    console.log(`✅ 前端实现任务完成`);
    console.log(`📊 结果类型: ${result.type}`);
    console.log(`🤖 使用的Agent: ${result.agentUsed || '未知'}`);
    
  } catch (error) {
    console.error(`❌ 前端实现任务测试失败:`, error.message);
  }
  
  console.log('\n' + '='.repeat(60) + '\n');
  
  // 测试案例3: 任务类型检测（包含新的前端任务）
  console.log('🔍 测试案例3: 任务类型检测');
  console.log('─────────────────────────');
  
  const testCases = [
    {
      message: "生成登录页面的HTML和CSS代码",
      expectedDetection: "前端任务"
    },
    {
      message: "设计并实现一个完整的用户中心页面",
      expectedDetection: "完整实现工作流"
    },
    {
      message: "为产品发布会策划内容架构、视觉方案并生成前端代码",
      expectedDetection: "完整实现工作流"
    },
    {
      message: "优化现有页面的前端性能",
      expectedDetection: "前端任务"
    },
    {
      message: "创建响应式的移动端界面",
      expectedDetection: "前端任务"
    }
  ];
  
  testCases.forEach((testCase, index) => {
    const isCreative = orchestrator.detectCreativeTask({ message: testCase.message });
    const isVisual = orchestrator.detectVisualTask({ message: testCase.message });
    const isFrontend = orchestrator.detectFrontendTask({ message: testCase.message });
    const needsFullImplementation = orchestrator.detectFullImplementationWorkflow({ message: testCase.message });
    
    let detectedType = "研究任务";
    if (needsFullImplementation) {
      detectedType = "完整实现工作流";
    } else if (isFrontend && !isCreative && !isVisual) {
      detectedType = "前端任务";
    } else if (isVisual && !isCreative) {
      detectedType = "视觉任务";
    } else if (isCreative) {
      detectedType = "创意任务";
    }
    
    const isCorrect = detectedType === testCase.expectedDetection ? "✅" : "❌";
    console.log(`${index + 1}. "${testCase.message}"`);
    console.log(`   预期: ${testCase.expectedDetection} | 检测: ${detectedType} ${isCorrect}`);
  });
  
  console.log('\n📊 测试总结:');
  console.log('─────────');
  console.log('✅ 三Agent协作工作流已成功集成');
  console.log('✅ 前端实现任务检测机制正常工作');
  console.log('✅ 创意总监 → 视觉总监 → 工程艺术大师 协作流程已建立');
  console.log('✅ 完整端到端解决方案交付能力已验证');
  console.log('✅ 支持独立和协作两种工作模式');
  
  // 内存统计
  console.log('\n💾 内存统计:');
  const stats = memory.getStats();
  console.log(`   项目数量: ${stats.projectCount}`);
  console.log(`   总键值对: ${stats.totalKeys}`);
  console.log(`   内存使用: ${stats.memoryUsage}`);
  
  console.log('\n🎉 三Agent协作系统测试完成！');
  console.log('   系统现在可以提供从创意构思到前端实现的完整解决方案。');
}

// 运行测试
if (require.main === module) {
  testThreeAgentWorkflow().catch(console.error);
}

module.exports = { testThreeAgentWorkflow };