/**
 * 真实内存检查器
 * 
 * 检查实际运行中的SimpleMemory仓库内容
 * 包括之前测试留下的真实数据
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');

async function inspectRealMemory() {
  console.log('🔍 真实内存仓库检查器\n');
  
  // 创建一个新的内存实例来模拟真实场景
  const memory = new SimpleMemory();
  const orchestrator = new HelixOrchestrator({ memory });
  
  // 首先运行一个真实的三Agent工作流来生成数据
  console.log('🚀 执行真实工作流生成数据...');
  const testRequest = {
    message: "为一个在线书店设计并实现主页，需要温馨书香的感觉，包含完整实现",
    type: "full_implementation",
    timestamp: new Date().toISOString()
  };
  
  const result = await orchestrator.processRequest(testRequest);
  const projectId = result.projectId;
  
  console.log(`✅ 工作流完成，项目ID: ${projectId}\n`);
  
  // 现在检查内存中的真实数据
  console.log('📊 内存仓库完整检查');
  console.log('═'.repeat(60));
  
  // 1. 基础统计
  console.log('\n1️⃣ 基础统计信息:');
  const stats = memory.getStats();
  console.log(`   总条目数: ${stats.totalEntries}`);
  console.log(`   项目数量: ${stats.totalProjects}`);
  console.log(`   内存使用: ${Math.round(stats.memoryUsage.heapUsed / 1024 / 1024 * 100) / 100} MB`);
  
  // 2. 项目列表
  console.log('\n2️⃣ 项目列表:');
  for (const [pid, keys] of memory.projectData.entries()) {
    console.log(`   📁 ${pid}`);
    console.log(`      数据键: ${Array.from(keys).join(', ')}`);
  }
  
  // 3. 详细数据内容
  console.log('\n3️⃣ 项目详细数据:');
  console.log('─'.repeat(40));
  
  const projectData = await memory.getProjectData(projectId);
  
  if (projectData.creative_brief) {
    console.log('\n📝 创意蓝图 (Creative Brief):');
    const brief = projectData.creative_brief;
    console.log(`   资产类型: ${brief.asset_type}`);
    console.log(`   版本: ${brief.asset_version}`);
    console.log(`   选择框架: ${brief.payload?.strategic_choice?.chosen_framework}`);
    console.log(`   用户画像: ${brief.payload?.narrative_strategy?.target_user_persona}`);
    console.log(`   期望情感: ${brief.payload?.narrative_strategy?.desired_feeling}`);
    console.log(`   章节数量: ${brief.payload?.content_structure?.length || 0}`);
  }
  
  if (projectData.visual_concepts) {
    console.log('\n🎨 视觉概念 (Visual Concepts):');
    const visual = projectData.visual_concepts;
    console.log(`   资产类型: ${visual.asset_type}`);
    console.log(`   版本: ${visual.asset_version}`);
    console.log(`   概念数量: ${visual.visual_explorations?.length || 0}`);
    
    visual.visual_explorations?.forEach((concept, index) => {
      console.log(`   ${index + 1}. ${concept.concept_name}`);
      console.log(`      氛围: ${concept.atmosphere?.substring(0, 100)}...`);
    });
  }
  
  if (projectData.frontend_implementation) {
    console.log('\n💻 前端实现 (Frontend Implementation):');
    const impl = projectData.frontend_implementation;
    console.log(`   资产类型: ${impl.asset_type}`);
    console.log(`   版本: ${impl.asset_version}`);
    console.log(`   选择概念: ${impl.implementation_choice?.chosen_concept}`);
    console.log(`   优化记录: ${impl.refinement_log?.length || 0} 项`);
    console.log(`   HTML长度: ${impl.frontend_code?.html?.length || 0} 字符`);
    console.log(`   CSS长度: ${impl.frontend_code?.css?.length || 0} 字符`);
  }
  
  if (projectData.project_info) {
    console.log('\n📊 项目信息 (Project Info):');
    const info = projectData.project_info;
    console.log(`   状态: ${info.status}`);
    console.log(`   工作流类型: ${info.workflowType}`);
    console.log(`   完成时间: ${info.completedAt}`);
  }
  
  // 4. 数据关系图
  console.log('\n4️⃣ 数据流关系图:');
  console.log('─'.repeat(40));
  console.log('用户请求');
  console.log('    ↓');
  console.log('HELIX调度中心');
  console.log('    ↓');
  console.log('创意总监 → creative_brief');
  console.log('    ↓');
  console.log('视觉总监 → visual_concepts');
  console.log('    ↓');
  console.log('工程艺术大师 → frontend_implementation');
  console.log('    ↓');
  console.log('项目完成 → project_info');
  
  // 5. 内存键值映射
  console.log('\n5️⃣ 内存键值映射:');
  console.log('─'.repeat(40));
  for (const [key, data] of memory.storage.entries()) {
    console.log(`🔑 ${key}`);
    console.log(`   项目: ${data.projectId}`);
    console.log(`   键: ${data.key}`);
    console.log(`   时间: ${data.timestamp}`);
    console.log(`   大小: ${JSON.stringify(data.value).length} 字符`);
  }
  
  // 6. 搜索演示
  console.log('\n6️⃣ 搜索功能演示:');
  console.log('─'.repeat(40));
  
  const searchTerms = ['书店', '温馨', '概念', '实现'];
  for (const term of searchTerms) {
    const searchResults = await memory.search(term);
    console.log(`🔎 搜索 "${term}": ${searchResults.length} 个结果`);
    searchResults.forEach(result => {
      console.log(`   - ${result.dataKey} (项目: ${result.projectId.substring(0, 20)}...)`);
    });
  }
  
  console.log('\n═'.repeat(60));
  console.log('🎉 真实内存仓库检查完成！');
  
  return { memory, projectId, projectData };
}

// 额外的内存分析工具
async function analyzeMemoryStructure(memory) {
  console.log('\n📈 内存结构分析');
  console.log('─'.repeat(40));
  
  const analysis = {
    dataTypes: {},
    sizesInBytes: {},
    projectCount: memory.projectData.size,
    totalEntries: memory.storage.size
  };
  
  for (const [key, data] of memory.storage.entries()) {
    // 分析数据类型
    const dataType = data.key;
    if (!analysis.dataTypes[dataType]) {
      analysis.dataTypes[dataType] = 0;
    }
    analysis.dataTypes[dataType]++;
    
    // 分析大小
    const size = JSON.stringify(data.value).length;
    analysis.sizesInBytes[dataType] = (analysis.sizesInBytes[dataType] || 0) + size;
  }
  
  console.log('数据类型分布:');
  Object.entries(analysis.dataTypes).forEach(([type, count]) => {
    const avgSize = Math.round(analysis.sizesInBytes[type] / count);
    console.log(`   ${type}: ${count} 个，平均 ${avgSize} 字符`);
  });
  
  console.log(`\n总体统计:`);
  console.log(`   项目数: ${analysis.projectCount}`);
  console.log(`   条目数: ${analysis.totalEntries}`);
  console.log(`   总存储: ${Object.values(analysis.sizesInBytes).reduce((a, b) => a + b, 0)} 字符`);
  
  return analysis;
}

// 主程序
async function main() {
  try {
    const { memory, projectId, projectData } = await inspectRealMemory();
    await analyzeMemoryStructure(memory);
    
    console.log('\n💡 提示：你可以使用以下方法查看SimpleMemory仓库：');
    console.log('1. memory.getStats() - 获取统计信息');
    console.log('2. memory.getProjectData(projectId) - 获取特定项目数据');
    console.log('3. memory.getContext(projectId, key) - 获取特定数据项');
    console.log('4. memory.search(query) - 搜索数据');
    console.log('5. memory.storage - 查看原始存储Map');
    console.log('6. memory.projectData - 查看项目索引Map');
    
  } catch (error) {
    console.error('❌ 检查过程出错:', error);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { inspectRealMemory, analyzeMemoryStructure };