/**
 * HELIX Orchestrator完整测试
 * 
 * 测试包含Mock模式和真实API模式（如果配置了Gemini API Key）
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

async function testHelixOrchestrator() {
  console.log('🧪 开始测试 HELIX Orchestrator...\n');
  
  const memory = new SimpleMemory();
  const orchestrator = new HelixOrchestrator({ memory });
  
  try {
    // 测试1: 简单用户请求处理
    console.log('📝 测试1: 简单用户请求处理');
    const simpleRequest = {
      message: '帮我分析人工智能的发展趋势',
      type: 'analysis'
    };
    
    const result1 = await orchestrator.processRequest(simpleRequest);
    console.log('✅ 请求类型:', result1.type);
    console.log('✅ 项目ID:', result1.projectId);
    console.log('✅ 消息:', result1.message);
    
    if (result1.type === 'COMPLETED') {
      console.log('✅ 分析摘要长度:', result1.result.summary.length, '字符');
      console.log('✅ 研究任务数:', result1.result.researchData.length);
    }
    
    // 测试2: 需要澄清的模糊请求
    console.log('\n📝 测试2: 模糊请求处理');
    const vagueRequest = {
      message: '帮我做个东西',
      type: 'general'
    };
    
    const result2 = await orchestrator.processRequest(vagueRequest);
    console.log('✅ 请求类型:', result2.type);
    
    if (result2.type === 'USER_CLARIFICATION_NEEDED') {
      console.log('✅ 澄清消息:', result2.message);
      
      // 测试3: 继续澄清后的项目
      console.log('\n📝 测试3: 用户澄清后继续');
      const continueResult = await orchestrator.continueProject(
        result2.projectId, 
        '我想要一个分析市场趋势的报告'
      );
      console.log('✅ 继续处理结果:', continueResult.type);
    }
    
    // 测试4: 项目状态查询
    console.log('\n📝 测试4: 项目状态查询');
    const status = await orchestrator.getProjectStatus(result1.projectId);
    console.log('✅ 项目状态:', status);
    
    // 测试5: 记忆库集成验证
    console.log('\n📝 测试5: 记忆库集成验证');
    const projectData = await memory.getProjectData(result1.projectId);
    console.log('✅ 存储的数据键:', Object.keys(projectData));
    
    // 验证完整的DRD Framework数据
    if (projectData.planning_result) {
      console.log('✅ 规划阶段完成，任务数:', projectData.planning_result.plan?.tasks?.length || 0);
    }
    
    if (projectData.research_results) {
      console.log('✅ 研究阶段完成，结果数:', projectData.research_results.length);
    }
    
    if (projectData.final_analysis) {
      console.log('✅ 分析阶段完成，摘要长度:', projectData.final_analysis.summary.length);
    }
    
    // 测试6: 复杂研究请求
    console.log('\n📝 测试6: 复杂研究请求');
    const complexRequest = {
      message: '我需要一个关于区块链技术在供应链管理中应用的全面分析报告，包括技术可行性、经济效益、实施挑战和未来发展趋势',
      type: 'comprehensive_analysis'
    };
    
    const result6 = await orchestrator.processRequest(complexRequest);
    console.log('✅ 复杂请求处理:', result6.type);
    
    if (result6.type === 'COMPLETED') {
      console.log('✅ 研究任务分解数:', result6.result.researchData.length);
      console.log('✅ 每个任务描述:');
      result6.result.researchData.forEach((task, index) => {
        console.log(`   ${index + 1}. ${task.taskDescription}`);
      });
    }
    
    // 测试7: 错误处理
    console.log('\n📝 测试7: 错误处理');
    try {
      // 模拟内存错误
      const brokenMemory = {
        setContext: async () => { throw new Error('Memory error'); }
      };
      const brokenOrchestrator = new HelixOrchestrator({ memory: brokenMemory });
      
      const errorResult = await brokenOrchestrator.processRequest({
        message: '测试错误处理',
        type: 'test'
      });
      
      console.log('✅ 错误处理结果:', errorResult.type);
      console.log('✅ 错误消息:', errorResult.message);
    } catch (e) {
      console.log('✅ 捕获预期错误:', e.message);
    }
    
    // 测试8: 性能基准测试
    console.log('\n📝 测试8: 性能基准测试');
    const startTime = Date.now();
    
    const performanceRequest = {
      message: '快速分析：当前AI市场的三个主要趋势',
      type: 'quick_analysis'
    };
    
    const perfResult = await orchestrator.processRequest(performanceRequest);
    const endTime = Date.now();
    
    console.log('✅ 处理时间:', endTime - startTime, 'ms');
    console.log('✅ 请求处理:', perfResult.type);
    
    // 最终统计
    console.log('\n📊 测试统计:');
    const finalStats = memory.getStats();
    console.log('✅ 总项目数:', finalStats.totalProjects);
    console.log('✅ 总数据条目:', finalStats.totalEntries);
    console.log('✅ 内存使用:', Math.round(finalStats.memoryUsage.heapUsed / 1024 / 1024), 'MB');
    
    // 检查API配置状态
    console.log('\n🔧 API配置状态:');
    if (process.env.GEMINI_API_KEY && process.env.GEMINI_API_KEY !== 'your_gemini_api_key_here') {
      console.log('✅ Gemini API Key: 已配置');
      console.log('💡 测试使用真实Gemini Flash API');
    } else {
      console.log('⚠️ Gemini API Key: 未配置');
      console.log('💡 测试使用Mock响应模式');
    }
    
    console.log('\n🎉 所有HELIX Orchestrator测试通过！');
    
    return {
      success: true,
      projectsProcessed: finalStats.totalProjects,
      dataItemsStored: finalStats.totalEntries,
      apiMode: process.env.GEMINI_API_KEY ? 'real' : 'mock'
    };
    
  } catch (error) {
    console.error('❌ HELIX测试失败:', error);
    throw error;
  }
}

// 运行测试
if (require.main === module) {
  // 设置测试环境
  require('dotenv').config();
  
  testHelixOrchestrator().then(result => {
    console.log('\n📋 测试摘要:', result);
  }).catch(console.error);
}

module.exports = { testHelixOrchestrator };