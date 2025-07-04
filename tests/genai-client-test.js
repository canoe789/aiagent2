/**
 * Google Genai客户端集成测试
 * 验证从axios迁移到@google/genai客户端的正确性
 */

// 加载环境变量
require('dotenv').config();

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

class GenaiClientTest {
  constructor() {
    this.memory = new SimpleMemory();
    this.orchestrator = new HelixOrchestrator({ 
      memory: this.memory,
      maxRetries: 2, // 减少重试次数以便快速测试
      minApiInterval: 1000 // 减少间隔以便测试
    });
  }

  async testGenaiClientIntegration() {
    console.log('🧪 Google Genai客户端集成测试');
    console.log('='.repeat(50));
    console.log('目标：验证从axios迁移到@google/genai客户端的正确性');
    console.log('');

    try {
      // 测试1: 直接API调用
      console.log('📋 测试1: 直接Gemini API调用');
      console.log('─'.repeat(30));
      
      const testPrompt = "请用一句话解释AI的核心作用。";
      console.log(`💬 测试提示: "${testPrompt}"`);
      
      const startTime = Date.now();
      const response = await this.orchestrator.callGeminiAPI(testPrompt, 0.3);
      const responseTime = Date.now() - startTime;
      
      console.log(`✅ Gemini响应成功 (${responseTime}ms)`);
      console.log(`📝 响应内容: ${response.substring(0, 100)}${response.length > 100 ? '...' : ''}`);
      
      const test1Result = {
        success: true,
        responseTime,
        responseLength: response.length,
        hasValidContent: response.length > 10
      };

      // 测试2: AI任务分类
      console.log('\n📋 测试2: AI任务分类系统');
      console.log('─'.repeat(30));
      
      const classificationRequest = {
        message: "为电商网站设计一个现代简约的首页",
        type: "design_task"
      };
      
      console.log(`💬 分类请求: "${classificationRequest.message}"`);
      
      const startTime2 = Date.now();
      const classificationResult = await this.orchestrator.aiTaskRouter.classifyRequest(classificationRequest);
      const classificationTime = Date.now() - startTime2;
      
      console.log(`✅ 分类成功 (${classificationTime}ms)`);
      console.log(`🎯 分类结果: ${classificationResult.classification?.workflow || 'unknown'}`);
      console.log(`📊 置信度: ${((classificationResult.classification?.confidence || 0) * 100).toFixed(1)}%`);
      console.log(`🔧 使用方法: ${classificationResult.method}`);
      
      const test2Result = {
        success: classificationResult.success,
        classificationTime,
        workflow: classificationResult.classification?.workflow,
        confidence: classificationResult.classification?.confidence,
        method: classificationResult.method
      };

      // 测试3: 完整工作流
      console.log('\n📋 测试3: 完整工作流执行');
      console.log('─'.repeat(30));
      
      const workflowRequest = {
        message: "设计一个简单的按钮组件",
        type: "ui_component"
      };
      
      console.log(`💬 工作流请求: "${workflowRequest.message}"`);
      
      const startTime3 = Date.now();
      const workflowResult = await this.orchestrator.processRequest(workflowRequest);
      const workflowTime = Date.now() - startTime3;
      
      console.log(`✅ 工作流完成 (${workflowTime}ms)`);
      console.log(`📊 结果类型: ${workflowResult.type}`);
      console.log(`🆔 项目ID: ${workflowResult.projectId}`);
      
      if (workflowResult.agentsUsed) {
        console.log(`🤖 使用Agent: ${workflowResult.agentsUsed.join(' → ')}`);
      }
      
      const test3Result = {
        success: workflowResult.type === 'COMPLETED',
        workflowTime,
        resultType: workflowResult.type,
        agentsUsed: workflowResult.agentsUsed || []
      };

      return {
        directApi: test1Result,
        classification: test2Result,
        workflow: test3Result
      };
      
    } catch (error) {
      console.error(`❌ 测试失败: ${error.message}`);
      return {
        error: error.message,
        stack: error.stack
      };
    }
  }

  async runComprehensiveTest() {
    console.log('🚀 开始Google Genai客户端综合测试...\n');
    
    const results = await this.testGenaiClientIntegration();
    
    this.generateTestReport(results);
  }

  generateTestReport(results) {
    console.log('\n' + '='.repeat(50));
    console.log('📊 Google Genai客户端测试报告');
    console.log('='.repeat(50));
    
    if (results.error) {
      console.log('\n❌ 测试整体失败');
      console.log(`错误信息: ${results.error}`);
      return;
    }
    
    console.log('\n📈 测试结果:');
    
    // 直接API调用测试
    if (results.directApi.success) {
      console.log('✅ 直接Gemini API调用: 成功');
      console.log(`  响应时间: ${results.directApi.responseTime}ms`);
      console.log(`  响应长度: ${results.directApi.responseLength} 字符`);
      console.log(`  内容有效: ${results.directApi.hasValidContent ? '是' : '否'}`);
    } else {
      console.log('❌ 直接Gemini API调用: 失败');
    }
    
    // AI分类测试
    if (results.classification.success) {
      console.log('✅ AI任务分类: 成功');
      console.log(`  分类时间: ${results.classification.classificationTime}ms`);
      console.log(`  工作流类型: ${results.classification.workflow}`);
      console.log(`  置信度: ${(results.classification.confidence * 100).toFixed(1)}%`);
      console.log(`  分类方法: ${results.classification.method}`);
    } else {
      console.log('❌ AI任务分类: 失败');
    }
    
    // 工作流执行测试
    if (results.workflow.success) {
      console.log('✅ 完整工作流: 成功');
      console.log(`  执行时间: ${results.workflow.workflowTime}ms`);
      console.log(`  结果类型: ${results.workflow.resultType}`);
      console.log(`  Agent数量: ${results.workflow.agentsUsed.length}`);
    } else {
      console.log('❌ 完整工作流: 失败');
    }
    
    console.log('\n🔍 关键发现:');
    
    if (results.directApi.success) {
      console.log('1. ✅ Google Genai客户端集成成功');
      console.log('2. ✅ API调用响应正常');
      
      if (results.directApi.responseTime < 5000) {
        console.log('3. ✅ 响应时间在可接受范围内');
      } else {
        console.log('3. ⚠️ 响应时间较长，可能需要优化');
      }
    } else {
      console.log('1. ❌ Genai客户端配置存在问题');
    }
    
    if (results.classification.success && results.classification.method === 'ai_analysis') {
      console.log('4. ✅ AI驱动的任务分类正常工作');
    } else if (results.classification.method === 'fallback_rules') {
      console.log('4. ⚠️ 使用了回退分类规则，AI分类可能有问题');
    }
    
    if (results.workflow.success) {
      console.log('5. ✅ 端到端工作流执行正常');
      console.log('6. ✅ 系统迁移成功完成');
    } else {
      console.log('5. ❌ 工作流执行存在问题');
    }
    
    console.log('\n💡 优化建议:');
    console.log('1. Google Genai客户端提供更好的类型安全和错误处理');
    console.log('2. 建议监控API响应时间，优化用户体验');
    console.log('3. 可以考虑实现智能缓存减少API调用次数');
    console.log('4. 新API密钥格式更安全，建议更新所有环境配置');
    
    console.log('\n🎯 迁移状态:');
    
    const allTestsPassed = results.directApi.success && 
                          results.classification.success && 
                          results.workflow.success;
    
    if (allTestsPassed) {
      console.log('🎉 迁移完全成功！系统已成功从axios迁移到Google官方genai客户端');
      console.log('📋 建议: 可以移除旧的axios相关代码和依赖');
    } else {
      console.log('⚠️ 迁移部分成功，需要进一步调试和优化');
    }
  }
}

async function runGenaiClientTest() {
  const tester = new GenaiClientTest();
  await tester.runComprehensiveTest();
}

if (require.main === module) {
  runGenaiClientTest().catch(console.error);
}

module.exports = { GenaiClientTest };