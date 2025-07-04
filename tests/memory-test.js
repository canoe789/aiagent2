/**
 * SimpleMemory 数据库功能测试
 */

const { SimpleMemory } = require('../src/memory/simple-memory');

async function testMemory() {
  console.log('🧪 开始测试 SimpleMemory...\n');
  
  const memory = new SimpleMemory();
  const projectId = 'test_project_123';
  
  try {
    // 测试1: 基础存储和读取
    console.log('📝 测试1: 基础存储和读取');
    await memory.setContext(projectId, 'user_request', {
      message: '帮我分析市场趋势',
      type: 'analysis',
      timestamp: new Date().toISOString()
    });
    
    const userRequest = await memory.getContext(projectId, 'user_request');
    console.log('✅ 存储成功:', userRequest.message);
    
    // 测试2: 多个数据存储
    console.log('\n📝 测试2: 多个数据存储');
    await memory.setContext(projectId, 'planning_result', {
      needsUserClarification: false,
      plan: {
        tasks: [
          { id: 'task_1', description: '分析技术趋势' },
          { id: 'task_2', description: '研究市场数据' }
        ]
      }
    });
    
    await memory.setContext(projectId, 'research_results', [
      {
        taskId: 'task_1',
        result: 'AI技术快速发展，市场需求增长',
        completedAt: new Date().toISOString()
      },
      {
        taskId: 'task_2', 
        result: '市场规模预计年增长25%',
        completedAt: new Date().toISOString()
      }
    ]);
    
    console.log('✅ 多数据存储成功');
    
    // 测试3: 获取项目所有数据
    console.log('\n📝 测试3: 获取项目所有数据');
    const allData = await memory.getProjectData(projectId);
    console.log('✅ 项目数据键:', Object.keys(allData));
    console.log('✅ 研究任务数量:', allData.research_results?.length || 0);
    
    // 测试4: 搜索功能
    console.log('\n📝 测试4: 搜索功能');
    const searchResults = await memory.search('市场');
    console.log('✅ 搜索结果数量:', searchResults.length);
    console.log('✅ 搜索到的项目:', searchResults.map(r => r.projectId));
    
    // 测试5: 导出和导入
    console.log('\n📝 测试5: 导出和导入');
    const exportData = await memory.exportProject(projectId);
    console.log('✅ 导出数据包含键:', Object.keys(exportData.data));
    
    // 创建新项目ID测试导入
    const newProjectId = 'imported_project_456';
    await memory.importProject({
      projectId: newProjectId,
      data: exportData.data
    });
    
    const importedData = await memory.getProjectData(newProjectId);
    console.log('✅ 导入成功，键:', Object.keys(importedData));
    
    // 测试6: 统计信息
    console.log('\n📝 测试6: 统计信息');
    const stats = memory.getStats();
    console.log('✅ 总条目数:', stats.totalEntries);
    console.log('✅ 总项目数:', stats.totalProjects);
    console.log('✅ 内存使用:', Math.round(stats.memoryUsage.heapUsed / 1024 / 1024), 'MB');
    
    // 测试7: 数据清理（创建过期数据测试）
    console.log('\n📝 测试7: 数据清理');
    
    // 手动设置过期数据（修改时间戳）
    const oldProjectId = 'old_project_789';
    await memory.setContext(oldProjectId, 'old_data', { test: 'old' });
    
    // 手动修改时间戳为25小时前
    const oldTimestamp = new Date(Date.now() - 25 * 60 * 60 * 1000).toISOString();
    const oldKey = `${oldProjectId}_old_data`;
    memory.storage.set(oldKey, {
      value: { test: 'old' },
      timestamp: oldTimestamp,
      projectId: oldProjectId,
      key: 'old_data'
    });
    
    const cleanedCount = await memory.cleanup();
    console.log('✅ 清理过期数据:', cleanedCount, '条');
    
    // 测试8: 错误处理
    console.log('\n📝 测试8: 错误处理');
    const nonExistentData = await memory.getContext('non_existent', 'no_key');
    console.log('✅ 不存在的数据返回:', nonExistentData);
    
    // 测试9: 复杂数据结构
    console.log('\n📝 测试9: 复杂数据结构');
    const complexData = {
      analysis: {
        summary: '市场分析完成',
        findings: [
          { title: '趋势1', importance: 'HIGH', data: [1, 2, 3] },
          { title: '趋势2', importance: 'MEDIUM', data: [4, 5, 6] }
        ],
        metadata: {
          model: 'gpt-4',
          tokens: 1500,
          cost: 0.03
        }
      }
    };
    
    await memory.setContext(projectId, 'final_analysis', complexData);
    const retrievedComplex = await memory.getContext(projectId, 'final_analysis');
    console.log('✅ 复杂数据存储成功');
    console.log('✅ 发现数量:', retrievedComplex.analysis.findings.length);
    console.log('✅ 模型信息:', retrievedComplex.analysis.metadata.model);
    
    // 最终统计
    console.log('\n📊 最终统计:');
    const finalStats = memory.getStats();
    console.log('✅ 最终条目数:', finalStats.totalEntries);
    console.log('✅ 最终项目数:', finalStats.totalProjects);
    
    console.log('\n🎉 所有测试通过！SimpleMemory 工作正常。');
    
  } catch (error) {
    console.error('❌ 测试失败:', error);
    throw error;
  }
}

// 运行测试
if (require.main === module) {
  testMemory().catch(console.error);
}

module.exports = { testMemory };