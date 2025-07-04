/**
 * HELIX Orchestrator - 首席策略师 & 动态调度器
 * 
 * 基于Gemini Flash API的简单调度中心，结合记忆库实现动态研究与决策框架
 * 集成专业Agent：创意总监、数据分析师等
 */

const axios = require('axios');
const { GoogleGenAI } = require('@google/genai');
const { CreativeDirectorAgent } = require('../agents/creative-director');
const { VisualDirectorAgent } = require('../agents/visual-director');
const { EngineeringArtistAgent } = require('../agents/engineering-artist');
const { QAComplianceRobotAgent } = require('../agents/qa-compliance-robot');
const { MetaOptimizerAgent } = require('../agents/meta-optimizer-agent');
const { AITaskRouter } = require('../services/AITaskRouter');
const { DRDOrchestrator } = require('./drd-orchestrator');

class HelixOrchestrator {
  constructor(options = {}) {
    this.apiKey = process.env.GEMINI_API_KEY;
    
    // 初始化Google Genai客户端
    if (this.apiKey && this.apiKey !== 'your_gemini_api_key_here') {
      this.geminiClient = new GoogleGenAI({ apiKey: this.apiKey });
    }
    
    // DeepSeek回退配置（安全处理API密钥）
    this.deepSeekConfig = {
      apiKey: process.env.DEEPSEEK_API_KEY,
      apiUrl: 'https://api.deepseek.com/v1/chat/completions',
      model: 'deepseek-reasoner',
      minInterval: options.deepSeekMinInterval || 5000, // DeepSeek更慢，增加到5秒间隔
      lastCallTime: 0
    };
    
    // 使用外部注入的记忆库
    this.memory = options.memory;
    
    // API配置参数（可外部配置）
    this.apiConfig = {
      temperature: options.temperature || 0.7,
      topK: options.topK || 40,
      topP: options.topP || 0.95,
      maxOutputTokens: options.maxOutputTokens || 8192,
      timeout: options.timeout || 30000,
    };

    // API速率限制配置
    this.rateLimit = {
      minInterval: options.minApiInterval || 2000, // 最小2秒间隔
      maxRetries: options.maxRetries || 5,
      baseDelay: options.baseRetryDelay || 1000,
      lastCallTime: 0,
      currentCalls: 0,
      maxConcurrent: options.maxConcurrentCalls || 3
    };
    
    // 初始化AI任务路由器
    this.aiTaskRouter = new AITaskRouter(this.callGeminiAPI.bind(this), {
      confidenceThreshold: options.confidenceThreshold || 0.7
    });

    // 初始化DRD Orchestrator
    this.drdOrchestrator = new DRDOrchestrator({
      memory: this.memory,
      helix: this,
      maxResearchCycles: options.maxResearchCycles || 3
    });

    // 初始化专业Agent
    this.agents = {
      creativeDirector: new CreativeDirectorAgent({
        memory: this.memory,
        orchestrator: this
      }),
      visualDirector: new VisualDirectorAgent({
        memory: this.memory,
        orchestrator: this
      }),
      engineeringArtist: new EngineeringArtistAgent({
        memory: this.memory,
        orchestrator: this
      }),
      qaComplianceRobot: new QAComplianceRobotAgent({
        memory: this.memory,
        orchestrator: this
      }),
      metaOptimizer: new MetaOptimizerAgent({
        memory: this.memory,
        orchestrator: this,
        failureAnalysisThreshold: options.failureAnalysisThreshold || 3,
        analysisInterval: options.analysisInterval || 300000 // 5分钟
      })
    };
    
    if (!this.apiKey) {
      console.warn('GEMINI_API_KEY not configured, service will be disabled');
    }
    
    this.systemPrompt = `你是HELIX，一个多元智能体系统的核心Orchestrator。你的角色是首席策略师和动态调度器。

核心信念：任何复杂的创作任务都是一个不断探索、发现、修正的螺旋过程。

你的工作循环：
1. 理解与规划 - 深刻理解用户意图，制定研究计划
2. 并行执行与监控 - 分解任务，委派给专家子Agent
3. 综合、评估与决策 - 综合信息，决定下一步行动
4. 质量保证与交付 - 确保质量，整合交付

你有完整的记忆库访问权限，所有决策和计划都要持久化存储。

启发式原则：
- 资源效率：根据复杂度动态调整资源
- 用户中心：优先考虑用户需求
- 透明度：向用户展示思考过程`;
  }

  /**
   * 调用Gemini Flash API（带速率限制和重试机制）
   */
  async callGeminiAPI(prompt, temperature = 0.7, retryCount = 0) {
    if (!this.geminiClient) {
      console.warn('Gemini API key not configured, returning mock response');
      return this.createMockResponse(prompt);
    }

    // 检查并发限制
    if (this.rateLimit.currentCalls >= this.rateLimit.maxConcurrent) {
      console.log(`⏳ API并发限制，等待其他调用完成... (当前: ${this.rateLimit.currentCalls})`);
      await this.waitForAvailableSlot();
    }

    // 速率限制：确保最小间隔
    const now = Date.now();
    const timeSinceLastCall = now - this.rateLimit.lastCallTime;
    if (timeSinceLastCall < this.rateLimit.minInterval) {
      const waitTime = this.rateLimit.minInterval - timeSinceLastCall;
      console.log(`⏱️ API速率限制，等待 ${waitTime}ms...`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }

    this.rateLimit.currentCalls++;
    this.rateLimit.lastCallTime = Date.now();

    try {
      // 使用Google官方genai客户端
      const response = await this.geminiClient.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: prompt
      });

      this.rateLimit.currentCalls--;

      if (response.text) {
        // 成功调用，重置重试计数
        if (retryCount > 0) {
          console.log(`✅ API调用成功 (经过${retryCount}次重试)`);
        }
        return response.text;
      } else {
        throw new Error('No valid response from Gemini API');
      }

    } catch (error) {
      this.rateLimit.currentCalls--;
      
      // 处理429 Too Many Requests错误（兼容genai客户端和axios错误格式）
      const isRateLimit = (error.response && error.response.status === 429) || 
                         (error.status === 429) || 
                         (error.message && error.message.includes('429')) ||
                         (error.message && error.message.includes('quota'));
                         
      if (isRateLimit && retryCount < this.rateLimit.maxRetries) {
        const delay = this.calculateRetryDelay(retryCount);
        console.warn(`🔄 API速率限制(429)，${delay/1000}秒后重试... (尝试 ${retryCount + 1}/${this.rateLimit.maxRetries})`);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.callGeminiAPI(prompt, temperature, retryCount + 1);
      }
      
      // 处理其他可重试的错误
      if (this.isRetryableError(error) && retryCount < this.rateLimit.maxRetries) {
        const delay = this.calculateRetryDelay(retryCount);
        console.warn(`🔄 API错误，${delay/1000}秒后重试... (尝试 ${retryCount + 1}/${this.rateLimit.maxRetries}): ${error.message}`);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.callGeminiAPI(prompt, temperature, retryCount + 1);
      }

      console.error('Gemini API Error:', error.message);
      
      // 达到最大重试次数或不可重试的错误，尝试DeepSeek回退
      if (retryCount >= this.rateLimit.maxRetries) {
        console.warn(`⚠️ 达到最大重试次数(${this.rateLimit.maxRetries})，尝试DeepSeek回退...`);
        try {
          return await this.callDeepSeekAPI(prompt, temperature);
        } catch (deepSeekError) {
          console.error('DeepSeek回退也失败，使用mock响应:', deepSeekError.message);
          return this.createMockResponse(prompt);
        }
      }
      
      return this.createMockResponse(prompt);
    }
  }

  /**
   * 计算重试延迟（指数退避 + 随机抖动）
   */
  calculateRetryDelay(retryCount) {
    const exponentialDelay = this.rateLimit.baseDelay * Math.pow(2, retryCount);
    const jitter = Math.random() * 1000; // 最多1秒随机延迟
    return Math.min(exponentialDelay + jitter, 30000); // 最大30秒
  }

  /**
   * 判断是否为可重试的错误（兼容genai客户端和axios错误格式）
   */
  isRetryableError(error) {
    // 网络错误等
    if (!error.response && !error.status) return true;
    
    // 获取状态码（兼容不同的错误格式）
    const status = error.response?.status || error.status;
    
    // 可重试的HTTP状态码
    if (status && [429, 500, 502, 503, 504].includes(status)) {
      return true;
    }
    
    // 基于错误消息判断（用于genai客户端的特殊错误）
    const message = error.message || '';
    return message.includes('network') || 
           message.includes('timeout') || 
           message.includes('connection') ||
           message.includes('server error');
  }

  /**
   * 等待可用的并发槽位
   */
  async waitForAvailableSlot() {
    return new Promise(resolve => {
      const checkSlot = () => {
        if (this.rateLimit.currentCalls < this.rateLimit.maxConcurrent) {
          resolve();
        } else {
          setTimeout(checkSlot, 500); // 每500ms检查一次
        }
      };
      checkSlot();
    });
  }

  /**
   * DeepSeek API调用（回退方案）
   */
  async callDeepSeekAPI(prompt, temperature = 0.7) {
    console.log('🔄 尝试DeepSeek R1回退...');
    
    if (!this.deepSeekConfig.apiKey) {
      throw new Error('DeepSeek API key not configured');
    }
    
    // DeepSeek速率限制：更长的间隔
    const now = Date.now();
    const timeSinceLastCall = now - this.deepSeekConfig.lastCallTime;
    if (timeSinceLastCall < this.deepSeekConfig.minInterval) {
      const waitTime = this.deepSeekConfig.minInterval - timeSinceLastCall;
      console.log(`⏱️ DeepSeek速率限制，等待 ${waitTime}ms...`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
    
    this.deepSeekConfig.lastCallTime = Date.now();
    
    const requestBody = {
      model: this.deepSeekConfig.model,
      messages: [
        {
          role: "user",
          content: prompt
        }
      ],
      temperature: temperature,
      max_tokens: 4000,
      stream: false
    };

    const response = await axios.post(
      this.deepSeekConfig.apiUrl,
      requestBody,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.deepSeekConfig.apiKey}`
        },
        timeout: 60000 // DeepSeek更慢，增加超时时间
      }
    );

    if (response.data?.choices?.[0]?.message?.content) {
      console.log('✅ DeepSeek回退成功');
      return response.data.choices[0].message.content;
    } else {
      throw new Error('No valid response from DeepSeek API');
    }
  }

  /**
   * 创建Mock响应（用于没有API key时的测试）
   */
  createMockResponse(prompt) {
    if (prompt.includes('needsUserClarification')) {
      return JSON.stringify({
        "needsUserClarification": false,
        "clarificationMessage": null,
        "plan": {
          "tasks": [
            {
              "id": "task_1",
              "description": "收集相关背景信息和数据",
              "type": "research"
            },
            {
              "id": "task_2",
              "description": "分析趋势和模式",
              "type": "research"
            }
          ]
        }
      });
    } else if (prompt.includes('研究任务')) {
      return `基于您的研究要求，我进行了深入分析：

## 关键发现
这是一个模拟的研究结果，展示了相关的重要信息。

## 重要数据或事实
- 相关数据点1：具体数值或事实
- 相关数据点2：具体数值或事实
- 相关数据点3：具体数值或事实

## 相关建议或洞察
基于以上分析，建议采取以下措施或关注以下要点...

*注：这是模拟响应，请配置GEMINI_API_KEY以获得真实结果*`;
    } else {
      return `基于深入分析，我为您提供以下综合报告：

## 核心发现总结
通过多维度研究，我们发现了几个关键要点...

## 具体建议或解决方案
1. 短期建议：立即可执行的行动方案
2. 中期建议：需要规划和准备的策略
3. 长期建议：长远发展的方向指导

## 后续行动建议
建议按优先级执行以下步骤...

*注：这是模拟响应，请配置GEMINI_API_KEY以获得真实结果*`;
    }
  }

  /**
   * 处理用户请求的主入口
   */
  async processRequest(userRequest) {
    const projectId = `project_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    try {
      // 存储项目到记忆库
      await this.memory.setContext(projectId, 'project_info', {
        userRequest,
        status: 'PLANNING',
        createdAt: new Date().toISOString()
      });

      // 第一阶段：理解与规划
      const planningResult = await this.planningPhase(projectId, userRequest);
      
      // 如果工作流已完成，直接返回结果
      if (planningResult.type === 'COMPLETED' || planningResult.type === 'USER_CLARIFICATION_NEEDED') {
        return planningResult;
      }
      
      // 根据规划结果决定下一步
      if (planningResult.needsUserClarification) {
        return {
          type: 'USER_CLARIFICATION_NEEDED',
          message: planningResult.clarificationMessage,
          projectId
        };
      }

      // 检查是否为创意任务已完成
      if (planningResult.delegatedTo === 'creativeDirector') {
        // 更新项目状态
        await this.memory.setContext(projectId, 'project_info', {
          userRequest,
          status: 'COMPLETED',
          completedAt: new Date().toISOString(),
          delegatedTo: 'creativeDirector'
        });

        return {
          type: 'COMPLETED',
          projectId,
          result: planningResult.creativeBrief,
          message: '🎨 创意蓝图已完成！创意总监已为您设计了完整的内容架构方案。',
          agentUsed: 'creativeDirector'
        };
      }

      // 第二阶段：执行研究计划（非创意任务）
      const researchResult = await this.researchPhase(projectId, planningResult.plan);
      
      // 第三阶段：综合分析
      const analysisResult = await this.analysisPhase(projectId, researchResult);
      
      return {
        type: 'COMPLETED',
        projectId,
        result: analysisResult,
        message: '任务完成！我已经完成了深度研究和分析。'
      };

    } catch (error) {
      console.error('Orchestrator error:', error);
      await this.memory.setContext(projectId, 'error', {
        message: error.message,
        timestamp: new Date().toISOString()
      });
      
      // 记录失败事件给Meta-Agent分析
      await this.recordAgentFailure(
        'helix-orchestrator',
        'ORCHESTRATION_ERROR',
        error.message,
        { projectId, stack: error.stack },
        userRequest
      );
      
      return {
        type: 'ERROR',
        projectId,
        message: '抱歉，处理过程中遇到了问题。请稍后重试。'
      };
    }
  }

  /**
   * 第一阶段：AI驱动的理解与规划
   */
  async planningPhase(projectId, userRequest) {
    console.log('🧠 启动AI驱动的任务分析...');
    
    // 使用AI任务路由器进行智能分类
    const routingResult = await this.aiTaskRouter.classifyRequest(userRequest);
    
    if (!routingResult.success) {
      console.error('❌ AI任务分类失败，使用通用研究工作流');
      return this.executeGeneralResearchWorkflow(projectId, userRequest);
    }
    
    const classification = routingResult.classification;
    
    // 存储分类结果到内存
    await this.memory.setContext(projectId, 'task_classification', {
      classification,
      method: routingResult.method,
      timestamp: routingResult.timestamp
    });
    
    console.log(`🎯 AI分类决策: ${classification.workflow} (置信度: ${(classification.confidence * 100).toFixed(1)}%)`);
    
    // 智能分发：根据复杂性判断选择处理框架
    if (classification.suggested_framework === 'drd') {
      console.log(`🔬 智能分发器：任务复杂度高，启动DRD动态研究框架`);
      console.log(`📊 复杂度评分: ${classification.complexity_score || 'N/A'}`);
      console.log(`🔍 复杂度指标: ${classification.complexity_indicators?.join(', ') || 'N/A'}`);
      
      // 使用DRD框架处理复杂任务
      return await this.drdOrchestrator.processDRDRequest(projectId, userRequest, classification);
    } else {
      console.log(`⚡ 智能分发器：任务明确，使用高效简单工作流`);
    }
    
    // 基于AI分类结果执行相应的简单工作流
    switch (classification.workflow) {
      case 'full_implementation':
        console.log(`🎨✨💻 AI检测到完整实现工作流，启动三Agent协作`);
        return await this.executeFullImplementationWorkflow(projectId, userRequest);
        
      case 'creative_visual':
        console.log(`🎨✨ AI检测到创意+视觉工作流，启动双Agent协作`);
        return await this.executeFullCreativeWorkflow(projectId, userRequest);
        
      case 'visual_frontend':
        console.log(`✨💻 AI检测到视觉+前端工作流，启动双Agent协作`);
        return await this.executeVisualFrontendWorkflow(projectId, userRequest);
        
      case 'frontend_only':
        console.log(`💻 AI检测到前端实现任务，委派给工程艺术大师`);
        return await this.executeFrontendOnlyWorkflow(projectId, userRequest);
        
      case 'visual_only':
        console.log(`✨ AI检测到视觉任务，委派给视觉总监`);
        return await this.executeVisualOnlyWorkflow(projectId, userRequest);
        
      case 'creative_only':
        console.log(`🎨 AI检测到创意任务，委派给创意总监`);
        return await this.executeCreativeOnlyWorkflow(projectId, userRequest);
        
      case 'clarification_needed':
        console.log(`❓ AI检测到需要澄清用户意图`);
        return await this.handleClarificationNeeded(projectId, userRequest, classification);
        
      case 'qa_validation':
        console.log(`🔍 AI检测到QA验证任务，委派给QA合规机器人`);
        return await this.executeQAValidationWorkflow(projectId, userRequest);
        
      case 'full_implementation_with_qa':
        console.log(`🎨✨💻🔍 AI检测到完整实现+QA工作流，启动四Agent协作`);
        return await this.executeFullImplementationWithQAWorkflow(projectId, userRequest);
        
      case 'general_research':
        console.log(`🔬 AI分类为通用研究任务`);
        return await this.executeGeneralResearchWorkflow(projectId, userRequest);
        
      default:
        console.warn(`⚠️ 未知的工作流类型: ${classification.workflow}，回退到通用研究`);
        return await this.executeGeneralResearchWorkflow(projectId, userRequest);
    }
  }

  /**
   * 第二阶段：研究执行
   */
  async researchPhase(projectId, plan) {
    // 并行执行所有研究任务
    const researchPromises = plan.tasks.map(task => this.executeResearchTask(task));
    const results = await Promise.all(researchPromises);
    
    // 存储研究结果
    await this.memory.setContext(projectId, 'research_results', results);
    
    return results;
  }

  /**
   * 执行单个研究任务
   */
  async executeResearchTask(task) {
    const prompt = `你是一个专业的研究员。请根据任务描述进行深入研究，提供详细、准确的信息。

研究任务：${task.description}

请提供详细的研究结果，包括：
1. 关键发现
2. 重要数据或事实
3. 相关建议或洞察

请以结构化的方式组织信息。`;

    const response = await this.callGeminiAPI(prompt, 0.7);

    return {
      taskId: task.id,
      taskDescription: task.description,
      result: response,
      completedAt: new Date().toISOString()
    };
  }

  /**
   * 第三阶段：综合分析
   */
  async analysisPhase(projectId, researchResults) {
    // 获取原始用户请求
    const projectInfo = await this.memory.getContext(projectId, 'project_info');
    
    const prompt = `${this.systemPrompt}

原始用户请求：${JSON.stringify(projectInfo.userRequest)}

研究结果：
${researchResults.map(r => `任务：${r.taskDescription}\n结果：${r.result}`).join('\n\n---\n\n')}

请综合分析所有研究结果，为用户提供：
1. 核心发现总结
2. 具体建议或解决方案
3. 后续行动建议

请提供清晰、有价值的最终答案。`;

    const response = await this.callGeminiAPI(prompt, 0.5);

    const analysisResult = {
      summary: response,
      researchData: researchResults,
      completedAt: new Date().toISOString()
    };

    // 存储最终结果
    await this.memory.setContext(projectId, 'final_analysis', analysisResult);
    
    // 更新项目状态
    await this.memory.setContext(projectId, 'project_info', {
      ...projectInfo,
      status: 'COMPLETED',
      completedAt: new Date().toISOString()
    });

    return analysisResult;
  }

  /**
   * 获取项目状态
   */
  async getProjectStatus(projectId) {
    const projectInfo = await this.memory.getContext(projectId, 'project_info');
    return projectInfo?.status || 'UNKNOWN';
  }

  /**
   * 继续未完成的项目（用于处理用户澄清后的继续）
   */
  async continueProject(projectId, userResponse) {
    const projectInfo = await this.memory.getContext(projectId, 'project_info');
    const planningResult = await this.memory.getContext(projectId, 'planning_result');

    // 更新用户请求
    const updatedRequest = {
      ...projectInfo.userRequest,
      clarification: userResponse
    };

    // 重新规划或继续执行
    if (planningResult?.needsUserClarification) {
      // 基于用户澄清重新规划
      return await this.planningPhase(projectId, updatedRequest);
    } else {
      // 继续执行现有计划
      const researchResult = await this.researchPhase(projectId, planningResult.plan);
      const analysisResult = await this.analysisPhase(projectId, researchResult);
      
      return {
        type: 'COMPLETED',
        projectId,
        result: analysisResult
      };
    }
  }

  /**
   * 检测是否为创意任务
   */
  detectCreativeTask(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    const type = (userRequest.type || '').toLowerCase();
    
    // 首先排除纯分析研究任务
    if (message.includes('分析') || message.includes('研究') || 
        message.includes('调研') || message.includes('评估')) {
      return false;
    }
    
    // 明确的创意关键词（更精确）
    const creativeKeywords = [
      '内容架构', '内容策略', '创意蓝图', '故事架构', 
      '用户故事', '内容规划', '文案策略'
    ];
    
    // 类型检测
    const creativeTypes = [
      'creative', 'content', 'marketing', 'story', 'blueprint'
    ];
    
    // 检查明确的创意类型
    if (creativeTypes.some(keyword => type.includes(keyword))) {
      return true;
    }
    
    // 检查明确的创意关键词
    if (creativeKeywords.some(keyword => message.includes(keyword))) {
      return true;
    }
    
    return false;
  }

  /**
   * 检测是否需要视觉设计
   */
  detectVisualTask(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    const type = (userRequest.type || '').toLowerCase();
    
    // 视觉设计关键词
    const visualKeywords = [
      '视觉', '界面', '设计', '美观', '颜色', '色彩', '风格',
      'visual', 'ui', 'interface', 'style', 'color', 'theme',
      '外观', '样式', '美化', '布局', '排版', '图标',
      '概念', '效果', '体验', 'mockup', 'prototype'
    ];
    
    // 视觉类型检测
    const visualTypes = [
      'visual', 'ui', 'interface', 'style', 'design',
      'mockup', 'prototype', 'theme', 'layout'
    ];
    
    // 检查类型
    if (visualTypes.some(keyword => type.includes(keyword))) {
      return true;
    }
    
    // 检查消息内容
    if (visualKeywords.some(keyword => message.includes(keyword))) {
      return true;
    }
    
    // 检查是否明确要求视觉概念
    if (message.includes('视觉概念') || message.includes('设计方案') || 
        message.includes('界面设计') || message.includes('视觉风格')) {
      return true;
    }
    
    return false;
  }


  /**
   * 根据工作流类型执行相应的标准工作流（供DRD框架调用）
   */
  async executeWorkflowByType(projectId, workflowType, userRequest) {
    console.log(`🔄 执行标准工作流: ${workflowType}`);
    
    switch (workflowType) {
      case 'full_implementation':
        return await this.executeFullImplementationWorkflow(projectId, userRequest);
      case 'creative_visual':
        return await this.executeFullCreativeWorkflow(projectId, userRequest);
      case 'visual_frontend':
        return await this.executeVisualFrontendWorkflow(projectId, userRequest);
      case 'creative_only':
        return await this.executeCreativeOnlyWorkflow(projectId, userRequest);
      case 'visual_only':
        return await this.executeVisualOnlyWorkflow(projectId, userRequest);
      case 'frontend_only':
        return await this.executeFrontendOnlyWorkflow(projectId, userRequest);
      default:
        console.log(`⚠️ 未知工作流类型 ${workflowType}，使用通用研究`);
        return await this.executeGeneralResearchWorkflow(projectId, userRequest);
    }
  }

  /**
   * 执行完整创意+视觉工作流
   */
  async executeFullCreativeWorkflow(projectId, userRequest) {
    console.log(`🎨✨ 启动完整创意工作流: ${projectId}`);
    
    try {
      // 第一步：创意总监生成创意蓝图
      console.log(`📝 第一步：创意总监生成创意蓝图`);
      const creativeBrief = await this.agents.creativeDirector.processCreativeTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 第二步：视觉总监基于创意蓝图生成视觉概念
      console.log(`🎨 第二步：视觉总监生成视觉概念`);
      const visualConcepts = await this.agents.visualDirector.processVisualTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 更新项目状态
      await this.memory.setContext(projectId, 'project_info', {
        userRequest,
        status: 'COMPLETED',
        completedAt: new Date().toISOString(),
        workflowType: 'full_creative_visual'
      });
      
      return {
        type: 'COMPLETED',
        projectId,
        result: {
          creativeBrief,
          visualConcepts
        },
        message: '🎨✨ 完整创意工作流已完成！创意总监和视觉总监已为您设计了从内容架构到视觉呈现的完整方案。',
        agentsUsed: ['creativeDirector', 'visualDirector']
      };
      
    } catch (error) {
      console.error(`❌ 完整创意工作流失败:`, error);
      
      // 记录失败事件给Meta-Agent分析
      await this.recordAgentFailure(
        'creative-workflow',
        'WORKFLOW_EXECUTION_ERROR',
        error.message,
        { projectId, workflowType: 'full_creative', stack: error.stack },
        userRequest
      );
      
      throw error;
    }
  }

  /**
   * 执行纯视觉工作流（需要已有创意蓝图）
   */
  async executeVisualOnlyWorkflow(projectId, userRequest) {
    console.log(`✨ 启动纯视觉工作流: ${projectId}`);
    
    try {
      // 检查是否存在创意蓝图
      const existingBrief = await this.memory.getContext(projectId, 'creative_brief');
      
      if (!existingBrief) {
        // 如果没有创意蓝图，提醒用户需要先生成
        return {
          type: 'USER_CLARIFICATION_NEEDED',
          message: '视觉设计需要基于创意蓝图进行。请先提供内容策略，或者我可以为您生成一个创意蓝图作为视觉设计的基础。您希望我：\n1. 基于您的需求生成创意蓝图，然后进行视觉设计\n2. 您提供现有的内容策略或蓝图',
          projectId,
          suggestedActions: ['generate_brief_first', 'provide_existing_brief']
        };
      }
      
      // 执行视觉总监任务
      const visualConcepts = await this.agents.visualDirector.processVisualTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 更新项目状态
      await this.memory.setContext(projectId, 'project_info', {
        userRequest,
        status: 'COMPLETED',
        completedAt: new Date().toISOString(),
        workflowType: 'visual_only'
      });
      
      return {
        type: 'COMPLETED',
        projectId,
        result: visualConcepts,
        message: '✨ 视觉概念设计已完成！基于已有的创意蓝图，视觉总监为您创造了3个独特的视觉方向。',
        agentUsed: 'visualDirector'
      };
      
    } catch (error) {
      console.error(`❌ 纯视觉工作流失败:`, error);
      throw error;
    }
  }

  /**
   * 执行纯创意工作流
   */
  async executeCreativeOnlyWorkflow(projectId, userRequest) {
    console.log(`🎨 启动纯创意工作流: ${projectId}`);
    
    try {
      // 委派给创意总监
      const creativeBrief = await this.agents.creativeDirector.processCreativeTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      return {
        type: 'COMPLETED',
        projectId,
        result: creativeBrief,
        message: '🎨 创意蓝图已完成！',
        agentsUsed: ['creativeDirector']
      };
      
    } catch (error) {
      console.error(`❌ 纯创意工作流失败:`, error);
      throw error;
    }
  }

  /**
   * 执行纯前端实现工作流（需要已有视觉概念）
   */
  async executeFrontendOnlyWorkflow(projectId, userRequest) {
    console.log(`💻 启动纯前端实现工作流: ${projectId}`);
    
    try {
      // 检查是否存在视觉概念
      const existingConcepts = await this.memory.getContext(projectId, 'visual_concepts');
      
      if (!existingConcepts) {
        // 如果没有视觉概念，提醒用户需要先生成
        return {
          type: 'USER_CLARIFICATION_NEEDED',
          message: '前端实现需要基于视觉概念进行。请先提供视觉设计，或者我可以为您生成视觉概念作为前端实现的基础。您希望我：\n1. 基于您的需求生成完整的设计方案，然后进行前端实现\n2. 您提供现有的视觉设计或概念',
          projectId,
          suggestedActions: ['generate_design_first', 'provide_existing_design']
        };
      }
      
      // 执行工程艺术大师任务
      const frontendImplementation = await this.agents.engineeringArtist.processFrontendTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 更新项目状态
      await this.memory.setContext(projectId, 'project_info', {
        userRequest,
        status: 'COMPLETED',
        completedAt: new Date().toISOString(),
        workflowType: 'frontend_only'
      });
      
      return {
        type: 'COMPLETED',
        projectId,
        result: frontendImplementation,
        message: '💻 前端实现已完成！工程艺术大师已将视觉概念转化为像素级完美的交互体验。',
        agentUsed: 'engineeringArtist'
      };
      
    } catch (error) {
      console.error(`❌ 纯前端实现工作流失败:`, error);
      throw error;
    }
  }

  /**
   * 执行完整三Agent实现工作流
   */
  async executeFullImplementationWorkflow(projectId, userRequest) {
    console.log(`🎨✨💻 启动完整实现工作流: ${projectId}`);
    
    try {
      // 第一步：创意总监生成创意蓝图
      console.log(`📝 第一步：创意总监生成创意蓝图`);
      const creativeBrief = await this.agents.creativeDirector.processCreativeTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 第二步：视觉总监基于创意蓝图生成视觉概念
      console.log(`🎨 第二步：视觉总监生成视觉概念`);
      const visualConcepts = await this.agents.visualDirector.processVisualTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 第三步：工程艺术大师基于视觉概念生成前端实现
      console.log(`💻 第三步：工程艺术大师生成前端实现`);
      const frontendImplementation = await this.agents.engineeringArtist.processFrontendTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 更新项目状态
      await this.memory.setContext(projectId, 'project_info', {
        userRequest,
        status: 'COMPLETED',
        completedAt: new Date().toISOString(),
        workflowType: 'full_implementation'
      });
      
      return {
        type: 'COMPLETED',
        projectId,
        result: {
          creativeBrief,
          visualConcepts,
          frontendImplementation
        },
        message: '🎨✨💻 完整实现工作流已完成！从创意构思到视觉设计，再到前端实现，三位专家已为您打造了完整的解决方案。',
        agentsUsed: ['creativeDirector', 'visualDirector', 'engineeringArtist']
      };
      
    } catch (error) {
      console.error(`❌ 完整实现工作流失败:`, error);
      throw error;
    }
  }

  /**
   * 处理需要澄清的情况
   */
  async handleClarificationNeeded(projectId, userRequest, classification) {
    const clarificationQuestions = this.aiTaskRouter.generateClarificationQuestions(userRequest, classification);
    
    await this.memory.setContext(projectId, 'clarification_request', {
      originalRequest: userRequest,
      classification,
      questions: clarificationQuestions,
      timestamp: new Date().toISOString()
    });

    return {
      type: 'USER_CLARIFICATION_NEEDED',
      projectId,
      message: `AI分析发现您的请求需要进一步澄清。${classification.clarification_reason || ''}`,
      clarificationQuestions,
      suggestedActions: ['provide_more_details', 'specify_deliverables'],
      confidence: classification.confidence
    };
  }

  /**
   * 执行通用研究工作流
   */
  async executeGeneralResearchWorkflow(projectId, userRequest) {
    // 非创意任务的原有逻辑
    const prompt = `${this.systemPrompt}

用户请求：${JSON.stringify(userRequest)}

请分析这个请求：
1. 是否需要澄清用户意图？如果需要，请提供澄清问题
2. 如果不需要澄清，请制定一个研究计划，包含2-3个可以并行执行的研究任务

请以JSON格式回复：
{
  "needsUserClarification": boolean,
  "clarificationMessage": "string or null",
  "plan": {
    "tasks": [
      {
        "id": "task_1",
        "description": "具体的研究任务",
        "type": "research"
      }
    ]
  }
}`;

    const response = await this.callGeminiAPI(prompt, 0.3);
    
    let planningResult;
    try {
      planningResult = JSON.parse(response);
    } catch (e) {
      console.error('Failed to parse planning result, using fallback');
      planningResult = {
        needsUserClarification: false,
        clarificationMessage: null,
        plan: {
          tasks: [
            { id: 'task_1', description: '分析用户需求的核心要点', type: 'research' },
            { id: 'task_2', description: '收集相关信息和数据', type: 'research' }
          ]
        }
      };
    }
    
    // 存储规划结果
    await this.memory.setContext(projectId, 'planning_result', planningResult);
    
    return planningResult;
  }

  /**
   * 执行视觉+前端工作流
   */
  async executeVisualFrontendWorkflow(projectId, userRequest) {
    console.log(`✨💻 启动视觉+前端工作流: ${projectId}`);
    
    try {
      // 第一步：视觉总监生成视觉概念
      console.log(`🎨 第一步：视觉总监生成视觉概念`);
      const visualConcepts = await this.agents.visualDirector.processVisualTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 第二步：工程艺术大师基于视觉概念生成前端实现
      console.log(`💻 第二步：工程艺术大师生成前端实现`);
      const frontendImplementation = await this.agents.engineeringArtist.processFrontendTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 更新项目状态
      await this.memory.setContext(projectId, 'project_info', {
        userRequest,
        status: 'COMPLETED',
        completedAt: new Date().toISOString(),
        workflowType: 'visual_frontend'
      });
      
      return {
        type: 'COMPLETED',
        projectId,
        result: {
          visualConcepts,
          frontendImplementation
        },
        message: '✨💻 视觉+前端工作流已完成！从视觉设计到前端实现的完整解决方案已准备就绪。',
        agentsUsed: ['visualDirector', 'engineeringArtist']
      };
      
    } catch (error) {
      console.error(`❌ 视觉+前端工作流失败:`, error);
      throw error;
    }
  }

  /**
   * 执行QA验证工作流（单独的QA检查）
   */
  async executeQAValidationWorkflow(projectId, userRequest) {
    try {
      console.log(`🔍 启动QA验证工作流: ${projectId}`);
      
      // QA合规机器人执行验证
      const qaReport = await this.agents.qaComplianceRobot.processTask(projectId, userRequest);
      
      // 更新项目状态
      await this.memory.setContext(projectId, 'project_info', {
        userRequest,
        status: 'COMPLETED',
        completedAt: new Date().toISOString(),
        workflowType: 'qa_validation'
      });
      
      return qaReport;
      
    } catch (error) {
      console.error(`❌ QA验证工作流失败:`, error);
      
      // 记录失败事件给Meta-Agent分析
      await this.recordAgentFailure(
        'qa-workflow',
        'QA_VALIDATION_ERROR',
        error.message,
        { projectId, workflowType: 'qa_validation', stack: error.stack },
        userRequest
      );
      
      throw error;
    }
  }

  /**
   * 执行完整实现+QA验证工作流（四Agent协作）
   */
  async executeFullImplementationWithQAWorkflow(projectId, userRequest) {
    try {
      console.log(`🎨✨💻🔍 启动完整实现+QA工作流: ${projectId}`);
      
      // 第一步：创意总监生成创意蓝图
      console.log(`🎨 第一步：创意总监生成创意蓝图`);
      const creativeBrief = await this.agents.creativeDirector.processCreativeTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 第二步：视觉总监基于创意蓝图生成视觉概念
      console.log(`🎨 第二步：视觉总监生成视觉概念`);
      const visualConcepts = await this.agents.visualDirector.processVisualTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 第三步：工程艺术大师基于视觉概念生成前端实现
      console.log(`💻 第三步：工程艺术大师生成前端实现`);
      const frontendImplementation = await this.agents.engineeringArtist.processFrontendTask({
        project_id: projectId,
        user_request: userRequest
      });
      
      // 第四步：QA合规机器人验证代码质量
      console.log(`🔍 第四步：QA合规机器人验证代码质量`);
      const qaReport = await this.agents.qaComplianceRobot.processTask(projectId, userRequest);
      
      // 更新项目状态
      await this.memory.setContext(projectId, 'project_info', {
        userRequest,
        status: 'COMPLETED',
        completedAt: new Date().toISOString(),
        workflowType: 'full_implementation_with_qa'
      });
      
      return {
        type: 'COMPLETED',
        projectId,
        result: {
          creativeBrief,
          visualConcepts,
          frontendImplementation,
          qaReport
        },
        message: `🎨✨💻🔍 完整实现+QA工作流已完成！${qaReport.validation_report.validation_passed ? '代码质量验证通过✅' : '发现质量问题需要修复⚠️'}`,
        agentsUsed: ['creativeDirector', 'visualDirector', 'engineeringArtist', 'qaComplianceRobot'],
        qa_validation_summary: {
          passed: qaReport.validation_report.validation_passed,
          errors: qaReport.validation_report.summary.errors_found,
          warnings: qaReport.validation_report.summary.warnings_found
        }
      };
      
    } catch (error) {
      console.error(`❌ 完整实现+QA工作流失败:`, error);
      throw error;
    }
  }

  /**
   * 获取已注册的Agent列表
   */
  getRegisteredAgents() {
    return Object.keys(this.agents).map(key => ({
      name: key,
      info: this.agents[key].identity || this.agents[key].agentId || `${key}_agent`,
      version: this.agents[key].version || 'Unknown',
      type: this.agents[key].constructor.name
    }));
  }

  /**
   * 记录Agent失败事件 (供其他Agent调用，触发Meta-Agent分析)
   * @param {string} agentId - 发生错误的Agent ID
   * @param {string} errorType - 错误类型
   * @param {string} errorMessage - 错误消息
   * @param {Object} context - 错误上下文
   * @param {Object} userRequest - 原始用户请求
   */
  async recordAgentFailure(agentId, errorType, errorMessage, context = {}, userRequest = null) {
    try {
      await this.agents.metaOptimizer.recordFailureEvent(
        agentId,
        errorType,
        errorMessage,
        context,
        userRequest
      );
      console.log(`📝 已记录 ${agentId} 的失败事件给Meta-Agent分析`);
    } catch (error) {
      console.warn(`⚠️ Meta-Agent记录失败事件时出错:`, error.message);
    }
  }

  /**
   * 获取系统健康状态 (包含Meta-Agent分析)
   */
  async getSystemHealth() {
    try {
      const metaHealth = await this.agents.metaOptimizer.getSystemHealth();
      const memoryStats = this.memory.getStats();
      const failureStats = this.memory.getFailureStats();
      
      return {
        status: metaHealth.systemStatus,
        meta_analysis: metaHealth,
        memory_usage: memoryStats,
        failure_summary: failureStats,
        agents_registered: Object.keys(this.agents).length,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('获取系统健康状态失败:', error);
      return {
        status: 'ERROR',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }
}

module.exports = { HelixOrchestrator };