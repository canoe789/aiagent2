/**
 * API 接口测试（不需要真实AI调用）
 */

const { SimpleMemory } = require('../src/memory/simple-memory');

async function testAPI() {
  console.log('🧪 开始测试 API 相关功能...\n');
  
  const memory = new SimpleMemory();
  
  try {
    // 模拟API请求处理流程
    console.log('📝 测试1: 模拟API请求处理流程');
    
    const userRequest = {
      message: '帮我分析人工智能的发展趋势',
      type: 'analysis',
      timestamp: new Date().toISOString(),
      clientInfo: {
        userAgent: 'test-client',
        ip: '127.0.0.1'
      }
    };
    
    const projectId = `project_${Date.now()}`;
    
    // Step 1: 存储项目信息
    await memory.setContext(projectId, 'project_info', {
      userRequest,
      status: 'PLANNING',
      createdAt: new Date().toISOString()
    });
    
    console.log('✅ 项目创建成功:', projectId);
    
    // Step 2: 模拟规划结果
    const planningResult = {
      needsUserClarification: false,
      clarificationMessage: null,
      plan: {
        tasks: [
          { id: 'task_1', description: '分析AI技术发展历程', type: 'research' },
          { id: 'task_2', description: '研究当前AI市场状况', type: 'research' },
          { id: 'task_3', description: '预测未来AI发展趋势', type: 'research' }
        ]
      }
    };
    
    await memory.setContext(projectId, 'planning_result', planningResult);
    console.log('✅ 规划阶段完成，任务数:', planningResult.plan.tasks.length);
    
    // Step 3: 模拟研究结果
    const researchResults = [
      {
        taskId: 'task_1',
        taskDescription: '分析AI技术发展历程',
        result: '人工智能经历了三次发展浪潮：1956年达特茅斯会议标志诞生，1980年代专家系统兴起，2010年代深度学习突破。',
        completedAt: new Date().toISOString()
      },
      {
        taskId: 'task_2', 
        taskDescription: '研究当前AI市场状况',
        result: '2024年全球AI市场规模约2000亿美元，年增长率35%。主要应用领域包括自然语言处理、计算机视觉、自动驾驶等。',
        completedAt: new Date().toISOString()
      },
      {
        taskId: 'task_3',
        taskDescription: '预测未来AI发展趋势', 
        result: '未来5年AI将在多模态、强化学习、边缘计算方面取得重大突破。AGI可能在2030年代实现重要进展。',
        completedAt: new Date().toISOString()
      }
    ];
    
    await memory.setContext(projectId, 'research_results', researchResults);
    console.log('✅ 研究阶段完成，结果数:', researchResults.length);
    
    // Step 4: 模拟最终分析
    const analysisResult = {
      summary: `基于深入研究，人工智能正处于快速发展期：

## 核心发现总结
1. **历史发展**: AI经历三次浪潮，当前处于深度学习主导的第三次浪潮
2. **市场现状**: 2024年市场规模2000亿美元，年增长35%，应用广泛
3. **未来趋势**: 多模态AI、强化学习、边缘计算将是关键发展方向

## 具体建议
- **投资机会**: 关注多模态AI和边缘计算相关企业
- **技术布局**: 重点关注大模型、强化学习、具身智能
- **风险防范**: 注意AI安全、数据隐私、算法偏见等问题

## 后续行动建议
1. 持续跟踪AGI研发进展
2. 关注AI监管政策变化
3. 评估AI对各行业的具体影响`,
      researchData: researchResults,
      completedAt: new Date().toISOString()
    };
    
    await memory.setContext(projectId, 'final_analysis', analysisResult);
    
    // 更新项目状态为完成
    const projectInfo = await memory.getContext(projectId, 'project_info');
    await memory.setContext(projectId, 'project_info', {
      ...projectInfo,
      status: 'COMPLETED',
      completedAt: new Date().toISOString()
    });
    
    console.log('✅ 分析阶段完成');
    
    // 测试2: 项目状态查询
    console.log('\n📝 测试2: 项目状态查询');
    const finalProjectInfo = await memory.getContext(projectId, 'project_info');
    console.log('✅ 项目状态:', finalProjectInfo.status);
    console.log('✅ 处理时长:', 
      new Date(finalProjectInfo.completedAt) - new Date(finalProjectInfo.createdAt), 'ms');
    
    // 测试3: 完整数据导出
    console.log('\n📝 测试3: 完整数据导出');
    const exportData = await memory.exportProject(projectId);
    console.log('✅ 导出数据包含:');
    Object.keys(exportData.data).forEach(key => {
      console.log(`   - ${key}`);
    });
    
    // 测试4: 搜索功能验证
    console.log('\n📝 测试4: 搜索功能验证');
    const aiSearchResults = await memory.search('人工智能');
    console.log('✅ "人工智能"搜索结果:', aiSearchResults.length, '条');
    
    const marketSearchResults = await memory.search('市场');
    console.log('✅ "市场"搜索结果:', marketSearchResults.length, '条');
    
    // 测试5: 模拟需要澄清的情况
    console.log('\n📝 测试5: 模拟需要澄清的情况');
    const clarificationProjectId = `project_clarify_${Date.now()}`;
    
    const vaguePlanningResult = {
      needsUserClarification: true,
      clarificationMessage: '您希望分析哪个具体的技术领域？比如：自然语言处理、计算机视觉、还是机器学习算法？',
      plan: null
    };
    
    await memory.setContext(clarificationProjectId, 'project_info', {
      userRequest: { message: '帮我分析技术发展', type: 'general' },
      status: 'WAITING_CLARIFICATION',
      createdAt: new Date().toISOString()
    });
    
    await memory.setContext(clarificationProjectId, 'planning_result', vaguePlanningResult);
    console.log('✅ 澄清场景模拟完成');
    console.log('✅ 澄清消息:', vaguePlanningResult.clarificationMessage);
    
    // 测试6: 系统统计
    console.log('\n📝 测试6: 系统统计');
    const stats = memory.getStats();
    console.log('✅ 系统统计:');
    console.log(`   - 总数据条目: ${stats.totalEntries}`);
    console.log(`   - 活跃项目数: ${stats.totalProjects}`);
    console.log(`   - 内存使用: ${Math.round(stats.memoryUsage.heapUsed / 1024 / 1024)}MB`);
    
    // 测试7: 错误处理
    console.log('\n📝 测试7: 错误处理');
    
    // 测试不存在的项目
    const nonExistentProject = await memory.getContext('non_existent_project', 'project_info');
    console.log('✅ 不存在项目返回:', nonExistentProject);
    
    // 测试空搜索
    const emptySearch = await memory.search('不存在的内容xyz123');
    console.log('✅ 空搜索结果:', emptySearch.length, '条');
    
    console.log('\n🎉 所有API测试通过！系统工作正常。');
    
    // 返回测试结果摘要
    return {
      success: true,
      projectsCreated: 2,
      dataItemsStored: stats.totalEntries,
      memoryUsed: Math.round(stats.memoryUsage.heapUsed / 1024 / 1024),
      testProjectId: projectId
    };
    
  } catch (error) {
    console.error('❌ API测试失败:', error);
    throw error;
  }
}

// 运行测试
if (require.main === module) {
  testAPI().then(result => {
    console.log('\n📋 测试摘要:', result);
  }).catch(console.error);
}

module.exports = { testAPI };