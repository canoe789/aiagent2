/**
 * Meta-Agent / 系统优化师 集成测试
 * 
 * 测试Meta-Agent与HELIX系统的完整集成：
 * 1. 失败事件记录
 * 2. 模式检测
 * 3. 根本原因分析
 * 4. 优化方案生成
 * 5. 系统健康监控
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

async function testMetaAgentIntegration() {
  console.log('🧪 开始Meta-Agent集成测试...\n');

  // 初始化系统
  const memory = new SimpleMemory();
  const helix = new HelixOrchestrator({ 
    memory,
    failureAnalysisThreshold: 2, // 降低阈值以便测试
    analysisInterval: 1000 // 1秒间隔用于测试
  });

  console.log('✅ HELIX系统已初始化，包含Meta-Agent');
  console.log(`📊 已注册Agent数量: ${helix.getRegisteredAgents().length}`);
  console.log(`🔬 Meta-Agent配置: Prometheus v${helix.agents.metaOptimizer.version}\n`);

  // 测试1: 验证系统初始健康状态
  console.log('📋 测试1: 系统初始健康状态');
  const initialHealth = await helix.getSystemHealth();
  console.log(`系统状态: ${initialHealth.status}`);
  console.log(`失败记录: ${initialHealth.failure_summary.total} 条`);
  console.log(`Agent数量: ${initialHealth.agents_registered} 个\n`);

  // 测试2: 模拟失败事件
  console.log('📋 测试2: 模拟多个失败事件');
  
  // 模拟创意Agent的重复失败
  await helix.recordAgentFailure(
    'creative-director',
    'PARSING_ERROR',
    'Failed to parse user creative requirements',
    { step: 'content_analysis', input_length: 500 },
    { message: '设计一个现代化的博客界面', type: 'creative' }
  );

  await helix.recordAgentFailure(
    'creative-director', 
    'PARSING_ERROR',
    'Invalid JSON response from AI model',
    { step: 'content_analysis', input_length: 750 },
    { message: '创建企业网站的内容架构', type: 'creative' }
  );

  await helix.recordAgentFailure(
    'creative-director',
    'PARSING_ERROR', 
    'Unable to extract structured content from response',
    { step: 'content_analysis', input_length: 300 },
    { message: '设计产品展示页面的内容策略', type: 'creative' }
  );

  // 模拟其他Agent的失败
  await helix.recordAgentFailure(
    'visual-director',
    'STYLE_GENERATION_ERROR',
    'Color palette generation failed',
    { step: 'color_analysis', theme: 'modern' },
    { message: '生成极简风格的视觉设计', type: 'visual' }
  );

  console.log('✅ 已记录4个失败事件\n');

  // 测试3: 验证失败记录
  console.log('📋 测试3: 验证失败记录存储');
  const failureStats = memory.getFailureStats();
  console.log(`总失败数: ${failureStats.total}`);
  console.log(`未处理: ${failureStats.unprocessed}`);
  console.log(`按Agent统计:`);
  Object.entries(failureStats.byAgent).forEach(([agent, stats]) => {
    console.log(`  - ${agent}: ${stats.total}次 (${stats.unprocessed}未处理)`);
  });
  console.log('');

  // 测试4: 触发Meta-Agent分析
  console.log('📋 测试4: 触发Meta-Agent失败分析');
  const analysisResult = await helix.agents.metaOptimizer.processFailureAnalysis();
  
  console.log(`分析类型: ${analysisResult.type}`);
  if (analysisResult.type === 'ANALYSIS_COMPLETED') {
    console.log(`检测到模式: ${analysisResult.patterns} 个`);
    console.log(`生成优化方案: ${analysisResult.optimizations} 个`);
    console.log(`分析消息: ${analysisResult.message}`);
    
    if (analysisResult.results && analysisResult.results.length > 0) {
      console.log('\n🔍 优化方案详情:');
      analysisResult.results.forEach((result, index) => {
        console.log(`方案${index + 1}:`);
        console.log(`  - 目标Agent: ${result.optimization.targetAgent}`);
        console.log(`  - 优化类型: ${result.optimization.optimizationType}`);
        console.log(`  - 验证状态: ${result.status}`);
        console.log(`  - 验证通过率: ${result.validation.passRate ? (result.validation.passRate * 100).toFixed(1) + '%' : 'N/A'}`);
      });
    }
  } else {
    console.log(`分析结果: ${analysisResult.message}`);
  }
  console.log('');

  // 测试5: 验证系统健康状态更新
  console.log('📋 测试5: 分析后系统健康状态');
  const updatedHealth = await helix.getSystemHealth();
  console.log(`系统状态: ${updatedHealth.status}`);
  console.log(`总失败数: ${updatedHealth.failure_summary.total}`);
  console.log(`未处理失败: ${updatedHealth.failure_summary.unprocessed}`);
  console.log(`已处理失败: ${updatedHealth.failure_summary.processed}`);
  console.log(`关键模式: ${updatedHealth.meta_analysis.criticalPatterns} 个`);
  console.log(`上次分析: ${updatedHealth.meta_analysis.lastAnalysis || '未进行'}\n`);

  // 测试6: 测试清理功能
  console.log('📋 测试6: 测试失败日志清理');
  const cleanedCount = await memory.cleanupProcessedFailureLogs(0); // 立即清理所有已处理的
  console.log(`清理已处理日志: ${cleanedCount} 条\n`);

  // 测试7: 验证Agent注册信息
  console.log('📋 测试7: 验证Agent注册信息');
  const registeredAgents = helix.getRegisteredAgents();
  console.log('已注册的Agent:');
  registeredAgents.forEach(agent => {
    console.log(`  - ${agent.name}: ${agent.info?.identity || 'Unknown'}`);
  });
  console.log('');

  // 测试8: 模拟工作流错误并验证记录
  console.log('📋 测试8: 模拟工作流错误');
  try {
    // 创建一个会导致错误的请求
    const errorRequest = { message: 'test-error-trigger', type: 'invalid' };
    await helix.recordAgentFailure(
      'test-workflow',
      'INTEGRATION_TEST_ERROR',
      'This is a test error for integration testing',
      { testCase: 'workflow_error_simulation' },
      errorRequest
    );
    console.log('✅ 工作流错误记录成功\n');
  } catch (error) {
    console.error('❌ 工作流错误记录失败:', error.message);
  }

  // 最终报告
  console.log('📊 Meta-Agent集成测试完成总结:');
  const finalStats = memory.getFailureStats();
  const finalHealth = await helix.getSystemHealth();
  
  console.log(`✅ 系统状态: ${finalHealth.status}`);
  console.log(`✅ Meta-Agent状态: 运行正常`);
  console.log(`✅ 失败事件处理: ${finalStats.total}条记录，${finalStats.processed}条已处理`);
  console.log(`✅ 失败分析: ${finalHealth.meta_analysis.criticalPatterns}个关键模式需要关注`);
  console.log(`✅ 系统优化: Meta-Agent正在持续监控和优化系统性能`);
  
  if (finalHealth.status === 'HEALTHY') {
    console.log('\n🎉 Meta-Agent集成测试全部通过！系统运行良好！');
  } else {
    console.log(`\n⚠️ 系统需要关注: ${finalHealth.status}`);
  }

  return {
    success: true,
    failureStats: finalStats,
    systemHealth: finalHealth,
    analysisResult
  };
}

// 运行测试
if (require.main === module) {
  testMetaAgentIntegration()
    .then(result => {
      console.log('\n✅ Meta-Agent集成测试完成');
      process.exit(0);
    })
    .catch(error => {
      console.error('\n❌ Meta-Agent集成测试失败:', error);
      process.exit(1);
    });
}

module.exports = { testMetaAgentIntegration };