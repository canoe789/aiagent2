/**
 * 详细工作流检查测试
 * 
 * 展示每个Agent的完整输入输出，深入了解三Agent协作的每个节点
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

async function detailedWorkflowInspection() {
  console.log('🔍 详细工作流检查测试\n');
  console.log('本测试将展示三Agent协作的每个节点的完整输入输出\n');
  console.log('═'.repeat(60) + '\n');
  
  // 初始化组件
  const memory = new SimpleMemory();
  const orchestrator = new HelixOrchestrator({ memory });
  
  // 测试请求
  const testRequest = {
    message: "为一个心理健康应用设计并实现一个温暖治愈的欢迎页面，需要传达安全、信任和希望的感觉，包含完整的前端代码实现",
    type: "full_implementation",
    timestamp: new Date().toISOString()
  };
  
  console.log('📋 用户请求详情:');
  console.log('─'.repeat(40));
  console.log(`消息: ${testRequest.message}`);
  console.log(`类型: ${testRequest.type}`);
  console.log(`时间: ${testRequest.timestamp}`);
  console.log('\n');
  
  try {
    // 执行完整工作流
    const result = await orchestrator.processRequest(testRequest);
    const projectId = result.projectId;
    
    console.log('🎯 项目ID:', projectId);
    console.log('\n' + '═'.repeat(60) + '\n');
    
    // 第一部分：创意总监输出
    console.log('📝 第一节点：创意总监 (Creative Director)');
    console.log('─'.repeat(40));
    
    const creativeBrief = await memory.getContext(projectId, 'creative_brief');
    if (creativeBrief) {
      console.log('\n🎨 创意蓝图 (Creative Brief):');
      console.log(JSON.stringify(creativeBrief, null, 2));
    }
    
    console.log('\n' + '═'.repeat(60) + '\n');
    
    // 第二部分：视觉总监输出
    console.log('🎨 第二节点：视觉总监 (Visual Director)');
    console.log('─'.repeat(40));
    
    const visualConcepts = await memory.getContext(projectId, 'visual_concepts');
    if (visualConcepts) {
      console.log('\n✨ 视觉概念 (Visual Concepts):');
      console.log(JSON.stringify(visualConcepts, null, 2));
    }
    
    console.log('\n' + '═'.repeat(60) + '\n');
    
    // 第三部分：工程艺术大师输出
    console.log('💻 第三节点：工程艺术大师 (Engineering Artist)');
    console.log('─'.repeat(40));
    
    const frontendImpl = await memory.getContext(projectId, 'frontend_implementation');
    if (frontendImpl) {
      console.log('\n🔧 前端实现元数据:');
      console.log(`资产类型: ${frontendImpl.asset_type}`);
      console.log(`版本: ${frontendImpl.asset_version}`);
      
      console.log('\n🎯 实现决策:');
      console.log(`选择的概念: ${frontendImpl.implementation_choice?.chosen_concept}`);
      console.log(`决策理由: ${frontendImpl.implementation_choice?.reasoning}`);
      
      console.log('\n✨ 优化记录:');
      frontendImpl.refinement_log?.forEach((log, index) => {
        console.log(`${index + 1}. 问题: ${log.issue_found}`);
        console.log(`   修复: ${log.fix_applied}`);
      });
      
      console.log('\n📄 生成的HTML (完整):');
      console.log('─'.repeat(40));
      console.log(frontendImpl.frontend_code?.html);
      
      console.log('\n🎨 生成的CSS (完整):');
      console.log('─'.repeat(40));
      console.log(frontendImpl.frontend_code?.css);
    }
    
    console.log('\n' + '═'.repeat(60) + '\n');
    
    // 第四部分：项目完整状态
    console.log('📊 项目完整状态');
    console.log('─'.repeat(40));
    
    const projectInfo = await memory.getContext(projectId, 'project_info');
    if (projectInfo) {
      console.log('\n项目信息:');
      console.log(JSON.stringify(projectInfo, null, 2));
    }
    
    // 第五部分：内存中的所有数据
    console.log('\n' + '═'.repeat(60) + '\n');
    console.log('💾 项目在内存中的所有数据');
    console.log('─'.repeat(40));
    
    const allProjectData = await memory.getProjectData(projectId);
    console.log('\n存储的键:');
    Object.keys(allProjectData).forEach(key => {
      console.log(`- ${key}`);
    });
    
    console.log('\n' + '═'.repeat(60) + '\n');
    console.log('✅ 详细工作流检查完成！');
    console.log('\n总结:');
    console.log('1. 创意总监生成了包含叙事策略和内容结构的创意蓝图');
    console.log('2. 视觉总监基于创意蓝图创造了3个独特的视觉概念');
    console.log('3. 工程艺术大师选择最适合的概念并生成了优化后的前端代码');
    console.log('4. 所有数据都被妥善存储在内存中，可供查询和复用');
    
  } catch (error) {
    console.error('❌ 工作流执行失败:', error);
    console.error(error.stack);
  }
}

// 运行检查
if (require.main === module) {
  detailedWorkflowInspection().catch(console.error);
}

module.exports = { detailedWorkflowInspection };