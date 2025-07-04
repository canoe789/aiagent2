/**
 * 快速内存检查工具
 * 运行一个简单的测试并检查存储的数据
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

async function quickMemoryCheck() {
  console.log('🔍 快速内存存储检查');
  console.log('='.repeat(50));
  
  const memory = new SimpleMemory();
  const orchestrator = new HelixOrchestrator({ memory });
  
  // 运行一个简单测试
  const testRequest = {
    message: "为心理健康应用设计并实现温暖的欢迎页面，包含前端代码",
    type: "full_implementation"
  };
  
  console.log('📝 执行测试请求...');
  const result = await orchestrator.processRequest(testRequest);
  
  console.log(`✅ 测试完成，项目ID: ${result.projectId}`);
  console.log('');
  
  // 检查存储的数据
  console.log('📊 存储的数据详情:');
  console.log('─'.repeat(30));
  
  const projectData = await memory.getProjectData(result.projectId);
  
  for (const [key, value] of Object.entries(projectData)) {
    console.log(`\n🔑 ${key}:`);
    if (typeof value === 'object') {
      console.log(JSON.stringify(value, null, 2));
    } else {
      console.log(value);
    }
  }
  
  // 检查原始存储
  console.log('\n' + '='.repeat(50));
  console.log('🗄️ 原始存储键值:');
  console.log('─'.repeat(30));
  
  for (const [storageKey, data] of memory.storage.entries()) {
    console.log(`\n📁 ${storageKey}:`);
    console.log(`   时间戳: ${data.timestamp}`);
    console.log(`   项目ID: ${data.projectId}`);
    console.log(`   数据键: ${data.key}`);
    console.log(`   数据大小: ${JSON.stringify(data.value).length} 字符`);
  }
  
  // 验证数据完整性
  console.log('\n' + '='.repeat(50));
  console.log('✅ 数据完整性验证:');
  console.log('─'.repeat(30));
  
  const expectedKeys = ['project_info', 'creative_brief', 'visual_concepts', 'frontend_implementation'];
  const actualKeys = Object.keys(projectData);
  
  console.log(`期望的键: ${expectedKeys.join(', ')}`);
  console.log(`实际的键: ${actualKeys.join(', ')}`);
  
  const missingKeys = expectedKeys.filter(key => !actualKeys.includes(key));
  const extraKeys = actualKeys.filter(key => !expectedKeys.includes(key));
  
  if (missingKeys.length === 0 && extraKeys.length === 0) {
    console.log('✅ 数据完整性检查通过!');
  } else {
    if (missingKeys.length > 0) {
      console.log(`❌ 缺失的键: ${missingKeys.join(', ')}`);
    }
    if (extraKeys.length > 0) {
      console.log(`⚠️ 额外的键: ${extraKeys.join(', ')}`);
    }
  }
  
  return { result, projectData, memory };
}

if (require.main === module) {
  quickMemoryCheck().catch(console.error);
}

module.exports = { quickMemoryCheck };