/**
 * AI驱动的任务路由器
 * 
 * 替代关键词匹配，使用AI进行智能任务分类和置信度评估
 */

class AITaskRouter {
  constructor(llmService, options = {}) {
    // 兼容不同的LLM服务接口格式
    if (typeof llmService === 'function') {
      // 如果直接传入函数，包装为对象
      this.llmService = {
        callGeminiAPI: llmService
      };
    } else if (llmService && typeof llmService.callGeminiAPI === 'function') {
      // 如果传入的是包含callGeminiAPI方法的对象
      this.llmService = llmService;
    } else {
      // 兼容旧格式：{callGeminiAPI: function}
      this.llmService = llmService || {};
    }
    
    // 配置参数
    this.confidenceThreshold = options.confidenceThreshold || 0.7;
    
    // AI任务分类的系统提示词
    this.classificationPrompt = `你是HELIX调度中心的智能任务分类器。基于用户请求，你需要分析用户的真实意图并分配最合适的工作流。

可用的工作流类型：
1. creative_only - 纯创意策划（内容策略、用户故事、叙事框架、品牌定位）
2. visual_only - 纯视觉设计（UI设计、视觉概念、界面布局）
3. frontend_only - 纯前端实现（HTML/CSS/JS代码开发）
4. creative_visual - 创意+视觉工作流（从策略到设计的双Agent协作）
5. visual_frontend - 视觉+前端工作流（从设计到实现的双Agent协作）
6. full_implementation - 完整实现工作流（创意→视觉→前端的三Agent协作）
7. qa_validation - QA质量验证工作流（代码合规检查、可访问性验证、性能审计）
8. full_implementation_with_qa - 完整实现+QA验证（创意→视觉→前端→QA的四Agent协作）
9. clarification_needed - 需要澄清用户意图
10. general_research - 通用研究分析

Agent专业能力：
- 创意总监：内容策略、用户体验设计、叙事架构、品牌定位、用户故事
- 视觉总监：UI/UX设计、视觉概念、色彩方案、交互设计、界面布局
- 工程艺术大师：前端开发、HTML/CSS/JS、响应式设计、代码实现
- QA合规机器人：代码质量检查、可访问性验证、设计系统合规、性能预算审计、响应式设计验证

分析要点：
1. 理解用户的核心需求和最终目标
2. 识别任务涉及的专业领域（创意、视觉、技术）
3. 评估任务复杂度和Agent协作需求
4. 考虑前置条件和依赖关系
5. 判断是否需要多阶段研究和动态决策

复杂性判断标准：
需要DRD框架(requires_drd: true)的情况：
- 需要深度市场研究或竞品分析
- 涉及多个不确定因素需要调研
- 用户需求模糊，需要多轮澄清和探索
- 需要数据收集和综合分析的项目
- 明确提到"研究"、"调研"、"分析"、"策略制定"
- 复杂度评估为high且包含研究性质

简单工作流(requires_drd: false)的情况：
- 明确的创意、设计或开发任务
- 用户需求清晰，无需额外调研
- 标准的三Agent协作能够完成
- 复杂度为low或medium且任务边界清晰

重要：请基于用户的真实意图进行分类，不要被表面的关键词误导。

返回纯JSON格式（不要使用markdown代码块）：
{
  "workflow": "工作流类型",
  "confidence": 0.95,
  "reasoning": "详细分析用户意图和选择此工作流的原因",
  "user_intent": "用户的核心目标",
  "complexity": "low|medium|high",
  "agents_needed": ["所需Agent列表"],
  "prerequisites": ["前置条件列表"],
  "estimated_duration": "预估完成时间",
  "requires_drd": false,
  "complexity_score": 0.3,
  "complexity_indicators": ["指标列表"]
}`;
  }

  /**
   * AI驱动的智能任务分类
   */
  async classifyRequest(userRequest) {
    try {
      console.log('🧠 AI任务分类开始...');
      console.log(`📝 分析请求: "${userRequest.message}"`);
      
      const analysisPrompt = `${this.classificationPrompt}

用户请求分析：
消息：${userRequest.message}
类型：${userRequest.type || '未指定'}
时间：${userRequest.timestamp || new Date().toISOString()}

请分析此请求并返回最合适的工作流分类。`;

      // 调用LLM进行智能分析
      const response = await this.llmService.callGeminiAPI(analysisPrompt, 0.3);
      
      let classification;
      try {
        // 清理响应，移除可能的markdown代码块
        let cleanResponse = response;
        if (typeof cleanResponse === 'string') {
          // 移除```json和```标记
          cleanResponse = cleanResponse.replace(/^```json\s*/, '').replace(/\s*```.*$/, '');
          // 移除```标记
          cleanResponse = cleanResponse.replace(/^```\s*/, '').replace(/\s*```.*$/, '');
          // 只保留JSON部分，处理多行情况
          const jsonMatch = cleanResponse.match(/^\s*\{[\s\S]*\}\s*$/);
          if (jsonMatch) {
            cleanResponse = jsonMatch[0].trim();
          }
        }
        
        classification = JSON.parse(cleanResponse);
      } catch (parseError) {
        console.warn('⚠️ AI响应解析失败，使用回退逻辑');
        return this.fallbackClassification(userRequest);
      }

      // 验证分类结果
      if (!this.validateClassification(classification)) {
        console.warn('⚠️ AI分类结果无效，使用回退逻辑');
        return this.fallbackClassification(userRequest);
      }

      console.log(`🎯 AI分类结果:`);
      console.log(`  工作流: ${classification.workflow}`);
      console.log(`  置信度: ${(classification.confidence * 100).toFixed(1)}%`);
      console.log(`  用户意图: ${classification.user_intent}`);
      console.log(`  复杂度: ${classification.complexity}`);
      console.log(`  需要Agent: ${classification.agents_needed.join(' → ')}`);
      console.log(`  推理过程: ${classification.reasoning}`);

      // 置信度检查
      if (classification.confidence < this.confidenceThreshold) {
        console.log(`⚠️ 置信度较低 (${(classification.confidence * 100).toFixed(1)}%)，建议澄清`);
        classification.workflow = 'clarification_needed';
        classification.clarification_reason = '用户意图不够明确，需要进一步澄清';
      }

      // DRD框架判断
      if (classification.requires_drd) {
        console.log(`🔬 AI检测到复杂任务，建议使用DRD动态研究框架`);
        classification.suggested_framework = 'drd';
      } else {
        classification.suggested_framework = 'simple_workflow';
      }

      return {
        success: true,
        classification,
        method: 'ai_analysis',
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error('❌ AI任务分类失败:', error.message);
      console.log('🔄 回退到规则分类...');
      return this.fallbackClassification(userRequest);
    }
  }

  /**
   * 验证AI分类结果的有效性
   */
  validateClassification(classification) {
    const validWorkflows = [
      'creative_only', 'visual_only', 'frontend_only',
      'creative_visual', 'visual_frontend', 'full_implementation',
      'qa_validation', 'full_implementation_with_qa',
      'clarification_needed', 'general_research'
    ];

    const validComplexity = ['low', 'medium', 'high'];

    return (
      classification &&
      typeof classification === 'object' &&
      validWorkflows.includes(classification.workflow) &&
      typeof classification.confidence === 'number' &&
      classification.confidence >= 0 &&
      classification.confidence <= 1 &&
      validComplexity.includes(classification.complexity) &&
      Array.isArray(classification.agents_needed) &&
      typeof classification.reasoning === 'string' &&
      classification.reasoning.length > 10
    );
  }

  /**
   * 回退分类逻辑（安全网）
   */
  fallbackClassification(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    
    console.log('🔧 使用回退分类逻辑');

    // 简化的智能规则
    let workflow = 'general_research';
    let confidence = 0.6;
    let reasoning = '回退逻辑：基于关键词模式匹配';
    let agents_needed = [];

    // 完整实现检测
    if (message.includes('设计并实现') || 
        message.includes('完整实现') || 
        message.includes('端到端') ||
        (message.includes('设计') && message.includes('实现') && message.includes('代码'))) {
      workflow = 'full_implementation';
      confidence = 0.8;
      reasoning = '回退逻辑：检测到完整实现意图';
      agents_needed = ['creativeDirector', 'visualDirector', 'engineeringArtist'];
    }
    // 前端实现检测
    else if (message.includes('html') || message.includes('css') || 
             message.includes('前端') || message.includes('代码实现') ||
             message.includes('响应式')) {
      workflow = 'frontend_only';
      confidence = 0.75;
      reasoning = '回退逻辑：检测到前端技术关键词';
      agents_needed = ['engineeringArtist'];
    }
    // 视觉设计检测
    else if (message.includes('设计') || message.includes('视觉') || 
             message.includes('界面') || message.includes('ui')) {
      workflow = 'visual_only';
      confidence = 0.7;
      reasoning = '回退逻辑：检测到视觉设计关键词';
      agents_needed = ['visualDirector'];
    }
    // 创意策划检测
    else if (message.includes('策略') || message.includes('内容') || 
             message.includes('用户故事') || message.includes('创意')) {
      workflow = 'creative_only';
      confidence = 0.7;
      reasoning = '回退逻辑：检测到创意策划关键词';
      agents_needed = ['creativeDirector'];
    }

    return {
      success: true,
      classification: {
        workflow,
        confidence,
        reasoning,
        user_intent: '基于关键词推断的用户意图',
        complexity: 'medium',
        agents_needed,
        prerequisites: [],
        estimated_duration: '未知'
      },
      method: 'fallback_rules',
      timestamp: new Date().toISOString()
    };
  }

  /**
   * 获取工作流的详细信息
   */
  getWorkflowInfo(workflowType) {
    const workflowInfo = {
      creative_only: {
        description: '纯创意策划工作流',
        agents: ['creativeDirector'],
        steps: 1,
        output: 'creative_brief'
      },
      visual_only: {
        description: '纯视觉设计工作流',
        agents: ['visualDirector'],
        steps: 1,
        output: 'visual_concepts',
        prerequisites: ['需要已有创意蓝图或明确设计要求']
      },
      frontend_only: {
        description: '纯前端实现工作流',
        agents: ['engineeringArtist'],
        steps: 1,
        output: 'frontend_implementation',
        prerequisites: ['需要已有视觉设计或明确技术规范']
      },
      creative_visual: {
        description: '创意+视觉工作流',
        agents: ['creativeDirector', 'visualDirector'],
        steps: 2,
        output: 'creative_brief + visual_concepts'
      },
      visual_frontend: {
        description: '视觉+前端工作流',
        agents: ['visualDirector', 'engineeringArtist'],
        steps: 2,
        output: 'visual_concepts + frontend_implementation'
      },
      full_implementation: {
        description: '完整实现工作流',
        agents: ['creativeDirector', 'visualDirector', 'engineeringArtist'],
        steps: 3,
        output: 'creative_brief + visual_concepts + frontend_implementation'
      },
      qa_validation: {
        description: 'QA质量验证工作流',
        agents: ['qaComplianceRobot'],
        steps: 1,
        output: 'qa_validation_report',
        prerequisites: ['需要已有前端代码实现']
      },
      full_implementation_with_qa: {
        description: '完整实现+QA验证工作流',
        agents: ['creativeDirector', 'visualDirector', 'engineeringArtist', 'qaComplianceRobot'],
        steps: 4,
        output: 'creative_brief + visual_concepts + frontend_implementation + qa_validation_report'
      },
      clarification_needed: {
        description: '需要澄清用户意图',
        agents: [],
        steps: 0,
        output: 'clarification_questions'
      },
      general_research: {
        description: '通用研究分析',
        agents: [],
        steps: 1,
        output: 'research_results'
      }
    };

    return workflowInfo[workflowType] || null;
  }

  /**
   * 生成澄清问题
   */
  generateClarificationQuestions(userRequest, classification) {
    const questions = [];

    if (classification.confidence < 0.5) {
      questions.push('您希望实现什么样的最终目标？');
      questions.push('这个项目主要涉及哪些方面：内容策划、视觉设计，还是技术实现？');
    }

    if (classification.workflow === 'clarification_needed') {
      questions.push('您能提供更多具体的需求细节吗？');
      questions.push('您期望的交付物是什么样的？');
    }

    return questions;
  }
}

module.exports = { AITaskRouter };