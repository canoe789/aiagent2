/**
 * AI驱动路由测试
 * 验证HELIX是否已升级为置信度分析而非关键词匹配
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

async function testAIRouting() {
  console.log('🧪 AI驱动路由升级验证测试');
  console.log('='.repeat(60));
  console.log('目标：验证系统是否已从关键词匹配升级为AI置信度分析');
  console.log('');

  const memory = new SimpleMemory();
  const orchestrator = new HelixOrchestrator({ memory });

  // 测试案例：特意设计的模糊/复杂请求，关键词匹配容易失败
  const testCases = [
    {
      name: "语义理解测试 - 无明显关键词",
      request: {
        message: "我想让我的在线书店看起来更专业更有吸引力，能让用户感到信任，最好能直接用到我的网站上",
        type: "enhancement"
      },
      expectedAI: "full_implementation", // AI应该理解这需要完整解决方案
      expectedKeyword: "general_research" // 关键词匹配可能失败
    },
    {
      name: "上下文推理测试 - 隐含需求",
      request: {
        message: "用户在购买过程中的情感旅程需要重新设计，让整个体验更流畅",
        type: "ux_optimization"
      },
      expectedAI: "creative_only", // AI应该识别这是UX策划
      expectedKeyword: "general_research" // 关键词匹配可能失败
    },
    {
      name: "技术与设计混合测试",
      request: {
        message: "登录页面需要更现代的感觉，同时要确保在手机上也能正常工作",
        type: "page_improvement"
      },
      expectedAI: "visual_frontend", // AI应该识别视觉+技术需求
      expectedKeyword: "general_research" // 关键词匹配可能失败
    },
    {
      name: "模糊需求测试 - 置信度检查",
      request: {
        message: "帮我优化这个产品",
        type: "unclear"
      },
      expectedAI: "clarification_needed", // AI应该要求澄清
      expectedKeyword: "general_research" // 关键词匹配默认
    }
  ];

  let aiSuccessCount = 0;
  let totalTests = testCases.length;

  for (let i = 0; i < testCases.length; i++) {
    const testCase = testCases[i];
    console.log(`\n📋 测试 ${i + 1}/${totalTests}: ${testCase.name}`);
    console.log('─'.repeat(50));
    console.log(`💬 用户请求: "${testCase.request.message}"`);
    
    try {
      // 执行AI路由测试
      const result = await orchestrator.processRequest(testCase.request);
      
      // 检查是否使用了AI分类
      const classificationData = await memory.getContext(result.projectId, 'task_classification');
      
      if (classificationData) {
        console.log('✅ 检测到AI分类数据');
        console.log(`   分类结果: ${classificationData.classification.workflow}`);
        console.log(`   置信度: ${(classificationData.classification.confidence * 100).toFixed(1)}%`);
        console.log(`   分析方法: ${classificationData.method}`);
        console.log(`   推理过程: ${classificationData.classification.reasoning}`);
        
        // 验证AI分类的准确性
        const actualWorkflow = classificationData.classification.workflow;
        if (actualWorkflow === testCase.expectedAI) {
          console.log('🎯 AI分类结果准确!');
          aiSuccessCount++;
        } else {
          console.log(`⚠️ AI分类偏差: 期望 ${testCase.expectedAI}, 实际 ${actualWorkflow}`);
        }
        
        console.log('🧠 确认：系统已使用AI驱动路由');
        
      } else {
        console.log('❌ 未检测到AI分类数据 - 可能仍在使用关键词匹配!');
      }
      
    } catch (error) {
      console.error(`❌ 测试失败: ${error.message}`);
    }
  }

  // 生成测试报告
  console.log('\n' + '='.repeat(60));
  console.log('📊 AI路由升级验证报告');
  console.log('='.repeat(60));
  
  console.log(`\n📈 总体结果:`);
  console.log(`  总测试数: ${totalTests}`);
  console.log(`  AI分类成功: ${aiSuccessCount}`);
  console.log(`  准确率: ${((aiSuccessCount / totalTests) * 100).toFixed(1)}%`);
  
  if (aiSuccessCount === totalTests) {
    console.log('\n🎉 验证成功！系统已成功升级为AI驱动的置信度分析路由');
    console.log('✅ 关键词匹配已被智能语义理解替代');
    console.log('✅ 系统能够理解复杂和模糊的用户意图');
    console.log('✅ 提供置信度评估和推理过程');
  } else if (aiSuccessCount > totalTests * 0.7) {
    console.log('\n✅ 部分成功：AI路由基本工作，但准确性有待提升');
    console.log('💡 建议：优化AI分类提示词和置信度阈值');
  } else {
    console.log('\n❌ 升级失败：AI路由准确性不足');
    console.log('🔧 需要：检查AI分类逻辑和训练数据');
  }
  
  console.log('\n🔍 关键改进点:');
  console.log('1. 从硬编码关键词 → AI语义理解');
  console.log('2. 从二元判断 → 置信度评估');
  console.log('3. 从简单匹配 → 上下文推理');
  console.log('4. 从静态规则 → 动态学习');
}

// 对比测试：模拟旧的关键词方法
function simulateOldKeywordRouting(userRequest) {
  const message = (userRequest.message || '').toLowerCase();
  
  // 模拟原始的关键词检测
  const hasDesign = message.includes('设计') || message.includes('视觉');
  const hasImplementation = message.includes('实现') || message.includes('代码');
  const hasCreative = message.includes('创意') || message.includes('策略');
  
  if (hasCreative && hasDesign && hasImplementation) {
    return 'full_implementation';
  } else if (hasDesign) {
    return 'visual_only';
  } else if (hasImplementation) {
    return 'frontend_only';
  } else if (hasCreative) {
    return 'creative_only';
  } else {
    return 'general_research';
  }
}

if (require.main === module) {
  testAIRouting().catch(console.error);
}

module.exports = { testAIRouting };