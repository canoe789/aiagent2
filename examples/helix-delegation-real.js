/**
 * HELIX调度中心真实任务委派逻辑演示
 * 
 * 基于实际代码展示调度中心如何进行任务委派决策
 */

class HelixTaskDelegator {
  constructor() {
    this.agents = {
      creativeDirector: {
        processCreativeTask: async (payload) => {
          console.log(`  🎨 创意总监接收任务: ${JSON.stringify(payload.user_request.message.substring(0, 50))}...`);
          // 模拟创意总监处理
          await this.simulateProcessing(2000);
          console.log(`  ✅ 创意总监完成，返回创意蓝图`);
          return { asset_type: 'creative_brief', content: '创意蓝图内容...' };
        }
      },
      visualDirector: {
        processVisualTask: async (payload) => {
          console.log(`  🎨 视觉总监接收任务: ${JSON.stringify(payload.user_request.message.substring(0, 50))}...`);
          await this.simulateProcessing(2500);
          console.log(`  ✅ 视觉总监完成，返回视觉概念`);
          return { asset_type: 'visual_concepts', concepts: ['概念1', '概念2', '概念3'] };
        }
      },
      engineeringArtist: {
        processFrontendTask: async (payload) => {
          console.log(`  💻 工程艺术大师接收任务: ${JSON.stringify(payload.user_request.message.substring(0, 50))}...`);
          await this.simulateProcessing(3000);
          console.log(`  ✅ 工程艺术大师完成，返回前端实现`);
          return { asset_type: 'frontend_implementation', html: '<div>...</div>', css: '.style {...}' };
        }
      }
    };

    this.memory = new Map(); // 模拟内存存储
  }

  async simulateProcessing(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 核心任务委派方法 - 完全模拟真实HELIX逻辑
   */
  async processRequest(userRequest) {
    const projectId = `project_${Date.now()}`;
    console.log(`\n🚀 HELIX调度中心开始处理请求`);
    console.log(`📋 项目ID: ${projectId}`);
    console.log(`📝 用户请求: "${userRequest.message}"`);
    console.log(`📊 请求类型: ${userRequest.type || '未指定'}`);
    console.log('');

    try {
      // 第一步：规划阶段 - 任务类型检测和工作流选择
      console.log('📈 第一步：规划阶段');
      console.log('─'.repeat(30));
      
      const planningResult = await this.planningPhase(projectId, userRequest);
      
      if (planningResult.needsUserClarification) {
        console.log('❓ 需要用户澄清');
        return planningResult;
      }

      if (planningResult.delegatedTo) {
        console.log(`✅ 任务已委派完成`);
        return planningResult;
      }

      // 第二步：执行阶段（如果是非Agent任务）
      console.log('\n📊 第二步：执行阶段');
      console.log('─'.repeat(30));
      return await this.executeNonAgentWorkflow(projectId, planningResult);

    } catch (error) {
      console.error('❌ 处理失败:', error.message);
      return { type: 'ERROR', projectId, message: '处理过程中遇到问题' };
    }
  }

  /**
   * 规划阶段 - 核心任务委派决策逻辑
   */
  async planningPhase(projectId, userRequest) {
    // 任务类型检测 - 完全基于真实代码
    console.log('🔍 任务类型检测...');
    
    const isCreativeTask = this.detectCreativeTask(userRequest);
    const isVisualTask = this.detectVisualTask(userRequest);
    const isFrontendTask = this.detectFrontendTask(userRequest);
    const needsFullWorkflow = this.detectFullCreativeWorkflow(userRequest);
    const needsFullImplementation = this.detectFullImplementationWorkflow(userRequest);

    console.log(`  创意任务: ${isCreativeTask ? '✅' : '❌'}`);
    console.log(`  视觉任务: ${isVisualTask ? '✅' : '❌'}`);
    console.log(`  前端任务: ${isFrontendTask ? '✅' : '❌'}`);
    console.log(`  完整创意工作流: ${needsFullWorkflow ? '✅' : '❌'}`);
    console.log(`  完整实现工作流: ${needsFullImplementation ? '✅' : '❌'}`);
    console.log('');

    // 工作流决策逻辑 - 基于真实优先级
    console.log('🎯 工作流选择决策...');

    // 优先级1：完整三Agent实现工作流
    if (needsFullImplementation) {
      console.log(`  ➤ 选择: 完整实现工作流 (创意→视觉→前端)`);
      return await this.executeFullImplementationWorkflow(projectId, userRequest);
    }

    // 优先级2：完整创意+视觉工作流
    if (needsFullWorkflow) {
      console.log(`  ➤ 选择: 完整创意工作流 (创意→视觉)`);
      return await this.executeFullCreativeWorkflow(projectId, userRequest);
    }

    // 优先级3：单独前端任务
    if (isFrontendTask && !isCreativeTask && !isVisualTask) {
      console.log(`  ➤ 选择: 纯前端实现工作流`);
      return await this.executeFrontendOnlyWorkflow(projectId, userRequest);
    }

    // 优先级4：单独视觉任务
    if (isVisualTask && !isCreativeTask) {
      console.log(`  ➤ 选择: 纯视觉工作流`);
      return await this.executeVisualOnlyWorkflow(projectId, userRequest);
    }

    // 优先级5：单独创意任务
    if (isCreativeTask) {
      console.log(`  ➤ 选择: 纯创意工作流`);
      return await this.executeCreativeOnlyWorkflow(projectId, userRequest);
    }

    // 默认：通用研究任务
    console.log(`  ➤ 选择: 通用研究工作流`);
    return {
      needsUserClarification: false,
      plan: {
        tasks: [
          { id: 'research_1', description: '分析用户需求核心要点', type: 'research' },
          { id: 'research_2', description: '收集相关信息和数据', type: 'research' }
        ]
      }
    };
  }

  /**
   * 完整实现工作流 - 三Agent协作
   */
  async executeFullImplementationWorkflow(projectId, userRequest) {
    console.log(`\n🎨✨💻 执行完整实现工作流`);
    console.log('═'.repeat(50));

    const results = {};

    try {
      // 第一步：创意总监
      console.log(`📝 第一阶段：创意总监处理`);
      const creativeBrief = await this.agents.creativeDirector.processCreativeTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 调度中心获得控制权，存储结果
      this.memory.set(`${projectId}_creative_brief`, creativeBrief);
      results.creativeBrief = creativeBrief;
      console.log(`  📁 创意蓝图已存储到内存`);

      // 第二步：视觉总监
      console.log(`\n🎨 第二阶段：视觉总监处理`);
      const visualConcepts = await this.agents.visualDirector.processVisualTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 调度中心获得控制权，存储结果
      this.memory.set(`${projectId}_visual_concepts`, visualConcepts);
      results.visualConcepts = visualConcepts;
      console.log(`  📁 视觉概念已存储到内存`);

      // 第三步：工程艺术大师
      console.log(`\n💻 第三阶段：工程艺术大师处理`);
      const frontendImplementation = await this.agents.engineeringArtist.processFrontendTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 调度中心获得控制权，存储结果
      this.memory.set(`${projectId}_frontend_implementation`, frontendImplementation);
      results.frontendImplementation = frontendImplementation;
      console.log(`  📁 前端实现已存储到内存`);

      // 调度中心更新项目状态
      this.memory.set(`${projectId}_project_info`, {
        userRequest,
        status: 'COMPLETED',
        completedAt: new Date().toISOString(),
        workflowType: 'full_implementation',
        agentsUsed: ['creativeDirector', 'visualDirector', 'engineeringArtist']
      });

      console.log(`\n✅ 完整实现工作流成功完成！`);
      console.log(`📊 总共执行了3个Agent任务`);
      console.log(`💾 项目数据已完整存储`);

      return {
        type: 'COMPLETED',
        projectId,
        result: results,
        message: '🎨✨💻 完整实现工作流已完成！从创意构思到视觉设计，再到前端实现，三位专家已为您打造了完整的解决方案。',
        agentsUsed: ['creativeDirector', 'visualDirector', 'engineeringArtist']
      };

    } catch (error) {
      console.error(`❌ 完整实现工作流失败:`, error);
      throw error;
    }
  }

  /**
   * 单独创意工作流
   */
  async executeCreativeOnlyWorkflow(projectId, userRequest) {
    console.log(`\n🎨 执行纯创意工作流`);
    console.log('─'.repeat(30));

    const creativeBrief = await this.agents.creativeDirector.processCreativeTask({
      project_id: projectId,
      user_request: userRequest
    });

    this.memory.set(`${projectId}_creative_brief`, creativeBrief);
    this.memory.set(`${projectId}_project_info`, {
      userRequest,
      status: 'COMPLETED',
      completedAt: new Date().toISOString(),
      workflowType: 'creative_only'
    });

    console.log(`✅ 创意工作流完成`);

    return {
      delegatedTo: 'creativeDirector',
      creativeBrief: creativeBrief
    };
  }

  async executeVisualOnlyWorkflow(projectId, userRequest) {
    console.log(`\n✨ 执行纯视觉工作流`);
    console.log('─'.repeat(30));

    // 检查前置条件
    const existingBrief = this.memory.get(`${projectId}_creative_brief`);
    if (!existingBrief) {
      console.log(`❌ 缺少创意蓝图前置条件`);
      return {
        type: 'USER_CLARIFICATION_NEEDED',
        message: '视觉设计需要基于创意蓝图进行。请先提供内容策略。',
        projectId
      };
    }

    const visualConcepts = await this.agents.visualDirector.processVisualTask({
      project_id: projectId,
      user_request: userRequest
    });

    this.memory.set(`${projectId}_visual_concepts`, visualConcepts);
    console.log(`✅ 视觉工作流完成`);

    return {
      type: 'COMPLETED',
      projectId,
      result: visualConcepts,
      agentUsed: 'visualDirector'
    };
  }

  async executeFrontendOnlyWorkflow(projectId, userRequest) {
    console.log(`\n💻 执行纯前端实现工作流`);
    console.log('─'.repeat(30));

    // 检查前置条件
    const existingConcepts = this.memory.get(`${projectId}_visual_concepts`);
    if (!existingConcepts) {
      console.log(`❌ 缺少视觉概念前置条件`);
      return {
        type: 'USER_CLARIFICATION_NEEDED',
        message: '前端实现需要基于视觉概念进行。请先提供视觉设计。',
        projectId
      };
    }

    const frontendImplementation = await this.agents.engineeringArtist.processFrontendTask({
      project_id: projectId,
      user_request: userRequest
    });

    this.memory.set(`${projectId}_frontend_implementation`, frontendImplementation);
    console.log(`✅ 前端实现工作流完成`);

    return {
      type: 'COMPLETED',
      projectId,
      result: frontendImplementation,
      agentUsed: 'engineeringArtist'
    };
  }

  async executeFullCreativeWorkflow(projectId, userRequest) {
    console.log(`\n🎨✨ 执行完整创意工作流`);
    console.log('─'.repeat(40));

    // 第一步：创意总监
    const creativeBrief = await this.agents.creativeDirector.processCreativeTask({
      project_id: projectId,
      user_request: userRequest
    });
    this.memory.set(`${projectId}_creative_brief`, creativeBrief);

    // 第二步：视觉总监
    const visualConcepts = await this.agents.visualDirector.processVisualTask({
      project_id: projectId,
      user_request: userRequest
    });
    this.memory.set(`${projectId}_visual_concepts`, visualConcepts);

    console.log(`✅ 完整创意工作流完成`);

    return {
      type: 'COMPLETED',
      projectId,
      result: { creativeBrief, visualConcepts },
      agentsUsed: ['creativeDirector', 'visualDirector']
    };
  }

  async executeNonAgentWorkflow(projectId, planningResult) {
    console.log('🔬 执行通用研究任务');
    // 模拟研究过程
    await this.simulateProcessing(1000);
    console.log('✅ 研究任务完成');
    
    return {
      type: 'COMPLETED',
      projectId,
      result: '研究分析结果',
      message: '任务完成！已完成深度研究和分析。'
    };
  }

  // 任务检测方法 - 基于真实代码
  detectCreativeTask(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    const creativeKeywords = ['内容策略', '用户故事', '创意', '策略'];
    return creativeKeywords.some(keyword => message.includes(keyword));
  }

  detectVisualTask(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    const visualKeywords = ['视觉', '设计', 'ui', '界面'];
    return visualKeywords.some(keyword => message.includes(keyword));
  }

  detectFrontendTask(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    const frontendKeywords = ['实现', '开发', '代码', 'html', 'css', '前端'];
    return frontendKeywords.some(keyword => message.includes(keyword));
  }

  detectFullCreativeWorkflow(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    return message.includes('创意') && message.includes('视觉') && !message.includes('实现');
  }

  detectFullImplementationWorkflow(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    const type = (userRequest.type || '').toLowerCase();
    
    const fullImplKeywords = ['完整实现', '设计并实现', '包含实现'];
    if (fullImplKeywords.some(keyword => message.includes(keyword))) return true;
    if (type === 'full_implementation') return true;
    
    const hasCreative = message.includes('创意') || message.includes('内容');
    const hasVisual = message.includes('视觉') || message.includes('设计');
    const hasImplementation = message.includes('实现') || message.includes('代码');
    
    return hasCreative && hasVisual && hasImplementation;
  }
}

// 演示完整的任务委派流程
async function demonstrateRealDelegation() {
  const helix = new HelixTaskDelegator();

  const testCase = {
    message: "为一个心理健康应用设计并实现一个温暖治愈的欢迎页面，需要传达安全、信任和希望的感觉，包含完整的前端代码实现",
    type: "full_implementation"
  };

  console.log('🎯 HELIX调度中心真实任务委派演示');
  console.log('='.repeat(60));

  const result = await helix.processRequest(testCase);

  console.log('\n' + '='.repeat(60));
  console.log('📋 最终结果摘要:');
  console.log(`  类型: ${result.type}`);
  console.log(`  项目ID: ${result.projectId}`);
  console.log(`  使用的Agent: ${result.agentsUsed ? result.agentsUsed.join(' → ') : '无'}`);
  console.log(`  消息: ${result.message}`);
}

if (require.main === module) {
  demonstrateRealDelegation().catch(console.error);
}

module.exports = { HelixTaskDelegator };