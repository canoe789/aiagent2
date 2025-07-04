/**
 * AI驱动的HELIX智能路由器
 * 
 * 展示如何使用LLM的判断能力替代关键词匹配进行任务路由
 */

class AIPoweredHelixRouter {
  constructor(llmService) {
    this.llmService = llmService;
    
    // 系统提示词 - 专门用于任务分类
    this.routingPrompt = `你是HELIX调度中心的智能任务分析器。你的职责是分析用户请求并决定最佳的工作流路径。

可用的工作流类型：
1. creative_only - 纯创意策划（内容策略、用户故事、叙事框架）
2. visual_only - 纯视觉设计（UI设计、视觉概念、界面布局）  
3. frontend_only - 纯前端实现（HTML/CSS/JS代码开发）
4. creative_visual - 创意+视觉工作流（从策略到设计）
5. visual_frontend - 视觉+前端工作流（从设计到实现）
6. full_implementation - 完整实现工作流（创意→视觉→前端）
7. clarification_needed - 需要澄清用户意图
8. general_research - 通用研究分析

Agent专业能力：
- 创意总监：内容策略、用户体验设计、叙事架构、品牌定位
- 视觉总监：UI/UX设计、视觉概念、色彩方案、交互设计
- 工程艺术大师：前端开发、代码实现、响应式设计、性能优化

分析用户请求时考虑：
1. 用户的明确需求和隐含意图
2. 任务的复杂程度和涉及的专业领域
3. 是否需要多个Agent协作
4. 前置条件依赖关系

请以JSON格式返回分析结果：
{
  "workflow": "工作流类型",
  "confidence": 0.95,
  "reasoning": "详细的分析推理过程",
  "user_intent": "用户真实意图概述",
  "complexity": "low|medium|high",
  "prerequisites": ["需要的前置条件"],
  "agents_needed": ["所需的Agent列表"],
  "estimated_steps": 3
}`;
  }

  /**
   * AI驱动的智能路由决策
   */
  async intelligentRoute(userRequest) {
    console.log('🧠 AI智能路由分析开始...');
    console.log(`📝 用户请求: "${userRequest.message}"`);
    
    const analysisPrompt = `${this.routingPrompt}

用户请求分析：
消息：${userRequest.message}
类型：${userRequest.type || '未指定'}

请分析此请求并返回最合适的工作流决策。`;

    try {
      // 调用LLM进行智能分析
      const response = await this.llmService.callLLM(analysisPrompt, 0.3);
      const analysis = JSON.parse(response);
      
      console.log(`🎯 AI分析结果:`);
      console.log(`  工作流: ${analysis.workflow}`);
      console.log(`  置信度: ${(analysis.confidence * 100).toFixed(1)}%`);
      console.log(`  用户意图: ${analysis.user_intent}`);
      console.log(`  复杂度: ${analysis.complexity}`);
      console.log(`  推理过程: ${analysis.reasoning}`);
      
      if (analysis.prerequisites && analysis.prerequisites.length > 0) {
        console.log(`  前置条件: ${analysis.prerequisites.join(', ')}`);
      }
      
      console.log(`  需要Agent: ${analysis.agents_needed.join(' → ')}`);
      console.log(`  预估步骤: ${analysis.estimated_steps}`);
      
      return analysis;
      
    } catch (error) {
      console.error('❌ AI路由分析失败，回退到规则路由:', error.message);
      return this.fallbackToRuleBasedRouting(userRequest);
    }
  }

  /**
   * 回退到规则路由（安全网）
   */
  fallbackToRuleBasedRouting(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    
    // 简化的规则逻辑
    if (message.includes('完整') && message.includes('实现')) {
      return {
        workflow: 'full_implementation',
        confidence: 0.7,
        reasoning: '规则回退：检测到完整实现关键词',
        fallback: true
      };
    }
    
    if (message.includes('设计') || message.includes('视觉')) {
      return {
        workflow: 'visual_only',
        confidence: 0.6,
        reasoning: '规则回退：检测到视觉设计关键词',
        fallback: true
      };
    }
    
    return {
      workflow: 'clarification_needed',
      confidence: 0.5,
      reasoning: '规则回退：无法确定用户意图',
      fallback: true
    };
  }

  /**
   * 对比当前关键词方法与AI方法
   */
  async compareRoutingMethods(userRequest) {
    console.log('\n🔍 路由方法对比测试');
    console.log('='.repeat(60));
    
    // 当前关键词方法
    console.log('\n1️⃣ 当前关键词方法:');
    const keywordResult = this.simulateCurrentKeywordRouting(userRequest);
    console.log(`  结果: ${keywordResult.workflow}`);
    console.log(`  检测逻辑: ${keywordResult.detection_logic}`);
    
    // AI智能方法
    console.log('\n2️⃣ AI智能方法:');
    const aiResult = await this.intelligentRoute(userRequest);
    
    // 对比分析
    console.log('\n📊 对比分析:');
    if (keywordResult.workflow === aiResult.workflow) {
      console.log('✅ 路由结果一致');
    } else {
      console.log('⚠️  路由结果不同!');
      console.log(`  关键词方法: ${keywordResult.workflow}`);
      console.log(`  AI方法: ${aiResult.workflow}`);
      console.log(`  可能原因: ${this.analyzeDiscrepancy(keywordResult, aiResult)}`);
    }
    
    return { keywordResult, aiResult };
  }

  /**
   * 模拟当前的关键词路由逻辑
   */
  simulateCurrentKeywordRouting(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    const type = (userRequest.type || '').toLowerCase();
    
    // 模拟当前HELIX的检测逻辑
    const hasCreative = message.includes('内容策略') || message.includes('创意');
    const hasVisual = message.includes('视觉') || message.includes('设计');
    const hasFrontend = message.includes('实现') || message.includes('代码') || message.includes('html');
    const hasFullImpl = message.includes('完整实现') || message.includes('设计并实现');
    
    let workflow;
    let detection_logic;
    
    if (hasFullImpl || (hasCreative && hasVisual && hasFrontend)) {
      workflow = 'full_implementation';
      detection_logic = '检测到完整实现关键词或三种需求并存';
    } else if (hasCreative && hasVisual) {
      workflow = 'creative_visual';
      detection_logic = '检测到创意和视觉关键词';
    } else if (hasFrontend && !hasCreative && !hasVisual) {
      workflow = 'frontend_only';
      detection_logic = '检测到纯前端关键词';
    } else if (hasVisual && !hasCreative) {
      workflow = 'visual_only';
      detection_logic = '检测到纯视觉关键词';
    } else if (hasCreative) {
      workflow = 'creative_only';
      detection_logic = '检测到创意关键词';
    } else {
      workflow = 'general_research';
      detection_logic = '未匹配到特定关键词';
    }
    
    return { workflow, detection_logic };
  }

  /**
   * 分析路由差异的原因
   */
  analyzeDiscrepancy(keywordResult, aiResult) {
    if (keywordResult.workflow === 'general_research' && aiResult.workflow !== 'general_research') {
      return 'AI能理解隐含意图，而关键词匹配失败';
    }
    
    if (aiResult.workflow === 'clarification_needed' && keywordResult.workflow !== 'clarification_needed') {
      return 'AI识别出歧义需要澄清，关键词匹配过于武断';
    }
    
    if (aiResult.confidence < 0.7) {
      return 'AI检测到用户意图模糊，需要更多上下文';
    }
    
    return 'AI提供了更精确的语义理解';
  }
}

// 模拟LLM服务
class MockLLMService {
  async callLLM(prompt, temperature) {
    // 模拟不同用户请求的AI分析结果
    if (prompt.includes('在线书店看起来更专业')) {
      return JSON.stringify({
        workflow: "full_implementation",
        confidence: 0.85,
        reasoning: "用户希望提升在线书店的专业度和吸引力，并直接应用到网站，这需要从内容策略到视觉设计再到前端实现的完整工作流",
        user_intent: "提升网站整体形象和用户信任度，需要可直接部署的解决方案",
        complexity: "high",
        prerequisites: [],
        agents_needed: ["创意总监", "视觉总监", "工程艺术大师"],
        estimated_steps: 3
      });
    }
    
    if (prompt.includes('用户在购买过程中的情感旅程')) {
      return JSON.stringify({
        workflow: "creative_only",
        confidence: 0.90,
        reasoning: "用户需要重新审视购买流程的用户体验设计，这是典型的创意策划和用户体验优化任务",
        user_intent: "优化用户购买体验的情感设计",
        complexity: "medium",
        prerequisites: [],
        agents_needed: ["创意总监"],
        estimated_steps: 1
      });
    }
    
    if (prompt.includes('登录页面需要更现代的感觉')) {
      return JSON.stringify({
        workflow: "visual_frontend",
        confidence: 0.75,
        reasoning: "需要视觉升级和移动端适配，涉及设计和前端实现两个专业领域",
        user_intent: "现代化登录页面的视觉和技术实现",
        complexity: "medium",
        prerequisites: [],
        agents_needed: ["视觉总监", "工程艺术大师"],
        estimated_steps: 2
      });
    }
    
    // 默认返回需要澄清
    return JSON.stringify({
      workflow: "clarification_needed",
      confidence: 0.3,
      reasoning: "用户请求包含歧义，需要进一步澄清具体需求和期望的交付物",
      user_intent: "不够明确",
      complexity: "unknown",
      prerequisites: ["用户澄清"],
      agents_needed: [],
      estimated_steps: 0
    });
  }
}

// 演示对比
async function demonstrateAIRouting() {
  const llmService = new MockLLMService();
  const aiRouter = new AIPoweredHelixRouter(llmService);
  
  const testCases = [
    {
      message: "我想让我的在线书店看起来更专业更有吸引力，能让用户感到信任，最好能直接用到我的网站上",
      type: "enhancement"
    },
    {
      message: "我们需要重新思考用户在购买过程中的情感旅程，让整个体验更流畅",
      type: "ux_optimization"
    },
    {
      message: "这个登录页面需要更现代的感觉，同时要确保在手机上也能正常工作",
      type: "page_improvement"
    }
  ];

  console.log('🚀 AI驱动的HELIX智能路由演示');
  console.log('='.repeat(80));

  for (let i = 0; i < testCases.length; i++) {
    console.log(`\n📋 测试案例 ${i + 1}/${testCases.length}`);
    console.log('─'.repeat(50));
    
    await aiRouter.compareRoutingMethods(testCases[i]);
    
    if (i < testCases.length - 1) {
      console.log('\n' + '='.repeat(80));
    }
  }

  console.log('\n🎯 结论: AI路由的核心优势');
  console.log('✅ 语义理解：理解用户的真实意图，不被表达方式局限');
  console.log('✅ 上下文推理：能推断隐含需求和最终目标');  
  console.log('✅ 置信度评估：提供决策可信度，避免错误路由');
  console.log('✅ 智能澄清：识别歧义并主动寻求澄清');
  console.log('✅ 动态适应：无需维护关键词库，自然适应新表达');
}

if (require.main === module) {
  demonstrateAIRouting().catch(console.error);
}

module.exports = { AIPoweredHelixRouter };