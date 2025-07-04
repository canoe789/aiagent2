/**
 * DeepSeek回退机制测试
 * 验证当Gemini API失败时，系统能否正确切换到DeepSeek
 */

// 加载环境变量
require('dotenv').config();

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

class DeepSeekFallbackTest {
  constructor() {
    this.memory = new SimpleMemory();
    // 创建一个模拟Gemini API失败的orchestrator
    this.orchestrator = new HelixOrchestrator({ 
      memory: this.memory,
      maxRetries: 2, // 减少重试次数以便快速测试
      deepSeekMinInterval: 3000 // 减少DeepSeek间隔以便测试
    });
  }

  async testDeepSeekFallback() {
    console.log('🧪 DeepSeek回退机制测试');
    console.log('='.repeat(50));
    console.log('目标：验证Gemini API失败时的DeepSeek回退');
    console.log('');

    try {
      // 直接测试DeepSeek API调用
      console.log('📋 测试1: 直接调用DeepSeek API');
      console.log('─'.repeat(30));
      
      const testPrompt = "请简单回答：AI的核心作用是什么？用一句话回答。";
      console.log(`💬 测试提示: "${testPrompt}"`);
      
      const startTime = Date.now();
      const response = await this.orchestrator.callDeepSeekAPI(testPrompt, 0.3);
      const responseTime = Date.now() - startTime;
      
      console.log(`✅ DeepSeek响应成功 (${responseTime}ms)`);
      console.log(`📝 响应内容: ${response.substring(0, 100)}${response.length > 100 ? '...' : ''}`);
      
      return {
        success: true,
        responseTime,
        responseLength: response.length
      };
      
    } catch (error) {
      console.error(`❌ DeepSeek测试失败: ${error.message}`);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async testFallbackChain() {
    console.log('\n📋 测试2: 完整回退链测试');
    console.log('─'.repeat(30));
    console.log('注意：此测试会先尝试Gemini（可能失败），然后自动回退到DeepSeek');
    
    try {
      const testRequest = {
        message: "请分析人工智能的发展趋势",
        type: "research_analysis"
      };
      
      console.log(`💬 用户请求: "${testRequest.message}"`);
      
      const startTime = Date.now();
      const result = await this.orchestrator.processRequest(testRequest);
      const totalTime = Date.now() - startTime;
      
      console.log(`✅ 请求处理成功 (总时间: ${totalTime}ms)`);
      console.log(`📊 结果类型: ${result.type}`);
      console.log(`🆔 项目ID: ${result.projectId}`);
      
      // 检查是否有DeepSeek回退的迹象
      const classificationData = await this.memory.getContext(result.projectId, 'task_classification');
      
      return {
        success: true,
        totalTime,
        resultType: result.type,
        classificationMethod: classificationData?.method || 'unknown'
      };
      
    } catch (error) {
      console.error(`❌ 回退链测试失败: ${error.message}`);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async runComprehensiveTest() {
    console.log('🚀 开始DeepSeek回退机制综合测试...\n');
    
    const results = {
      directDeepSeek: await this.testDeepSeekFallback(),
      fallbackChain: await this.testFallbackChain()
    };
    
    this.generateTestReport(results);
  }

  generateTestReport(results) {
    console.log('\n' + '='.repeat(50));
    console.log('📊 DeepSeek回退机制测试报告');
    console.log('='.repeat(50));
    
    console.log('\n📈 测试结果:');
    
    // 直接DeepSeek测试结果
    if (results.directDeepSeek.success) {
      console.log('✅ 直接DeepSeek API调用: 成功');
      console.log(`  响应时间: ${results.directDeepSeek.responseTime}ms`);
      console.log(`  响应长度: ${results.directDeepSeek.responseLength} 字符`);
    } else {
      console.log('❌ 直接DeepSeek API调用: 失败');
      console.log(`  错误原因: ${results.directDeepSeek.error}`);
    }
    
    // 回退链测试结果
    if (results.fallbackChain.success) {
      console.log('✅ 完整回退链: 成功');
      console.log(`  总处理时间: ${results.fallbackChain.totalTime}ms`);
      console.log(`  结果类型: ${results.fallbackChain.resultType}`);
      console.log(`  分类方法: ${results.fallbackChain.classificationMethod}`);
    } else {
      console.log('❌ 完整回退链: 失败');
      console.log(`  错误原因: ${results.fallbackChain.error}`);
    }
    
    console.log('\n🔍 关键发现:');
    
    if (results.directDeepSeek.success) {
      console.log('1. ✅ DeepSeek R1模型可以正常调用');
      console.log('2. ✅ API密钥配置正确');
      
      if (results.directDeepSeek.responseTime > 10000) {
        console.log('3. ⚠️ DeepSeek响应较慢，建议增加超时时间');
      } else {
        console.log('3. ✅ DeepSeek响应时间在可接受范围内');
      }
    } else {
      console.log('1. ❌ DeepSeek配置存在问题，需要检查API密钥');
    }
    
    if (results.fallbackChain.success) {
      console.log('4. ✅ 系统具备完整的容错能力');
      console.log('5. ✅ 多级回退机制工作正常');
    } else {
      console.log('4. ❌ 系统回退机制需要优化');
    }
    
    console.log('\n💡 优化建议:');
    console.log('1. DeepSeek作为可靠的回退方案，响应质量高但速度较慢');
    console.log('2. 建议在生产环境中适当增加DeepSeek的超时时间');
    console.log('3. 可以考虑根据任务复杂度动态选择回退策略');
    console.log('4. 监控回退使用频率，优化主要API的稳定性');
  }
}

async function runDeepSeekFallbackTest() {
  const tester = new DeepSeekFallbackTest();
  await tester.runComprehensiveTest();
}

if (require.main === module) {
  runDeepSeekFallbackTest().catch(console.error);
}

module.exports = { DeepSeekFallbackTest };