/**
 * SimpleMemory仓库浏览器
 * 
 * 提供多种方式查看和管理SimpleMemory中的数据
 */

const { SimpleMemory } = require('../src/memory/simple-memory');

async function exploreMemory() {
  console.log('💾 SimpleMemory仓库浏览器\n');
  
  // 创建一个测试内存实例
  const memory = new SimpleMemory();
  
  // 先添加一些测试数据
  console.log('📝 添加测试数据...');
  await memory.setContext('test_project_001', 'user_info', {
    name: '张三',
    type: '企业用户',
    requirements: ['UI设计', '前端开发']
  });
  
  await memory.setContext('test_project_001', 'creative_brief', {
    theme: '现代简约',
    target_audience: '年轻专业人士',
    tone: '专业而友好'
  });
  
  await memory.setContext('test_project_002', 'visual_concepts', {
    concepts: ['极简风格', '科技感', '温暖色调'],
    selected: '极简风格'
  });
  
  console.log('✅ 测试数据已添加\n');
  
  // 方式1：获取内存统计信息
  console.log('📊 方式1：内存统计信息');
  console.log('─'.repeat(40));
  const stats = memory.getStats();
  console.log('统计信息:', JSON.stringify(stats, null, 2));
  console.log('');
  
  // 方式2：查看所有项目
  console.log('🗂️ 方式2：所有项目概览');
  console.log('─'.repeat(40));
  
  // 获取内部存储信息
  const internalStorage = memory.storage; // Map对象
  const projectData = memory.projectData; // Map对象
  
  console.log('项目列表:');
  for (const [projectId, keys] of projectData.entries()) {
    console.log(`📁 项目: ${projectId}`);
    console.log(`   数据键: ${Array.from(keys).join(', ')}`);
  }
  console.log('');
  
  // 方式3：查看特定项目的所有数据
  console.log('🔍 方式3：特定项目完整数据');
  console.log('─'.repeat(40));
  
  const project001Data = await memory.getProjectData('test_project_001');
  console.log('test_project_001 完整数据:');
  console.log(JSON.stringify(project001Data, null, 2));
  console.log('');
  
  // 方式4：查看特定数据项
  console.log('🎯 方式4：查看特定数据项');
  console.log('─'.repeat(40));
  
  const userInfo = await memory.getContext('test_project_001', 'user_info');
  console.log('用户信息:', JSON.stringify(userInfo, null, 2));
  
  const creativeBrief = await memory.getContext('test_project_001', 'creative_brief');
  console.log('创意蓝图:', JSON.stringify(creativeBrief, null, 2));
  console.log('');
  
  // 方式5：搜索功能
  console.log('🔎 方式5：搜索功能');
  console.log('─'.repeat(40));
  
  const searchResults = await memory.search('简约');
  console.log('搜索"简约"的结果:');
  searchResults.forEach((result, index) => {
    console.log(`${index + 1}. 项目: ${result.projectId}, 键: ${result.dataKey}`);
    console.log(`   匹配内容: ${JSON.stringify(result.value)}`);
  });
  console.log('');
  
  // 方式6：原始存储数据查看
  console.log('🗄️ 方式6：原始存储结构');
  console.log('─'.repeat(40));
  
  console.log('所有存储键:');
  for (const [key, data] of internalStorage.entries()) {
    console.log(`${key}:`);
    console.log(`  项目ID: ${data.projectId}`);
    console.log(`  数据键: ${data.key}`);
    console.log(`  时间戳: ${data.timestamp}`);
    console.log(`  数据预览: ${JSON.stringify(data.value).substring(0, 100)}...`);
    console.log('');
  }
  
  return memory;
}

/**
 * 实时内存监控器
 */
async function memoryMonitor(memory) {
  console.log('📡 实时内存监控器');
  console.log('─'.repeat(40));
  
  // 显示当前状态
  function showCurrentState() {
    const stats = memory.getStats();
    const timestamp = new Date().toLocaleTimeString();
    
    console.log(`[${timestamp}] 当前状态:`);
    console.log(`  项目数: ${stats.projectCount || 0}`);
    console.log(`  总键值对: ${stats.totalKeys || 0}`);
    console.log(`  内存使用: ${typeof stats.memoryUsage === 'object' ? JSON.stringify(stats.memoryUsage) : stats.memoryUsage}`);
    console.log('');
  }
  
  showCurrentState();
  
  // 模拟添加新数据
  console.log('🔄 模拟添加新数据...');
  await memory.setContext('monitor_test', 'new_data', {
    message: '这是新添加的数据',
    timestamp: new Date().toISOString()
  });
  
  showCurrentState();
}

/**
 * 内存清理工具
 */
async function memoryCleanup(memory) {
  console.log('🧹 内存清理工具');
  console.log('─'.repeat(40));
  
  console.log('清理前状态:');
  const beforeStats = memory.getStats();
  console.log(JSON.stringify(beforeStats, null, 2));
  
  // 删除测试项目
  console.log('\n删除测试项目...');
  await memory.deleteProject('test_project_001');
  await memory.deleteProject('test_project_002');
  await memory.deleteProject('monitor_test');
  
  console.log('\n清理后状态:');
  const afterStats = memory.getStats();
  console.log(JSON.stringify(afterStats, null, 2));
}

/**
 * 数据导出工具
 */
async function exportMemoryData(memory) {
  console.log('📤 数据导出工具');
  console.log('─'.repeat(40));
  
  const exportData = {
    timestamp: new Date().toISOString(),
    stats: memory.getStats(),
    projects: {}
  };
  
  // 导出所有项目数据
  for (const [projectId] of memory.projectData.entries()) {
    exportData.projects[projectId] = await memory.getProjectData(projectId);
  }
  
  console.log('导出的数据结构:');
  console.log(JSON.stringify(exportData, null, 2));
  
  return exportData;
}

// 主函数
async function main() {
  try {
    // 1. 基础浏览
    const memory = await exploreMemory();
    
    console.log('═'.repeat(60) + '\n');
    
    // 2. 实时监控
    await memoryMonitor(memory);
    
    console.log('═'.repeat(60) + '\n');
    
    // 3. 数据导出
    await exportMemoryData(memory);
    
    console.log('═'.repeat(60) + '\n');
    
    // 4. 清理
    await memoryCleanup(memory);
    
    console.log('\n🎉 SimpleMemory浏览完成！');
    
  } catch (error) {
    console.error('❌ 浏览过程中出错:', error);
  }
}

// 如果直接运行这个文件
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  exploreMemory,
  memoryMonitor,
  memoryCleanup,
  exportMemoryData
};