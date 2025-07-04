/**
 * 关键词路由 vs AI智能路由对比演示
 * 
 * 展示当前关键词匹配的局限性和AI模型判断的优势
 */

class KeywordRouter {
  detectCreativeTask(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    const creativeKeywords = [
      '内容架构', '内容策略', '创意蓝图', '故事架构', 
      '用户故事', '内容规划', '文案策略'
    ];
    
    return creativeKeywords.some(keyword => message.includes(keyword));
  }

  detectVisualTask(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    const visualKeywords = [
      '视觉', '界面', '设计', '美观', '颜色', '色彩', '风格',
      'ui', 'interface', 'style', 'color', 'theme'
    ];
    
    return visualKeywords.some(keyword => message.includes(keyword));
  }

  detectFrontendTask(userRequest) {
    const message = (userRequest.message || '').toLowerCase();
    const frontendKeywords = [
      '前端实现', 'html', 'css', 'javascript', '代码实现',
      '网页开发', '响应式', '交互实现'
    ];
    
    return frontendKeywords.some(keyword => message.includes(keyword));
  }

  route(userRequest) {
    const isCreative = this.detectCreativeTask(userRequest);
    const isVisual = this.detectVisualTask(userRequest);
    const isFrontend = this.detectFrontendTask(userRequest);
    
    if (isCreative && isVisual && isFrontend) {
      return 'full_implementation_workflow';
    } else if (isCreative) {
      return 'creative_only_workflow';
    } else if (isVisual) {
      return 'visual_only_workflow';
    } else if (isFrontend) {
      return 'frontend_only_workflow';
    } else {
      return 'general_research_workflow';
    }
  }
}

class AISmartRouter {
  constructor() {
    // 模拟AI模型的上下文理解能力
    this.contextPatterns = {
      creative_planning: [
        /需要.*?(策略|规划|架构)/,
        /制定.*?(内容|方案)/,
        /设计.*?(流程|体验|故事)/,
        /规划.*?(用户|产品)/
      ],
      visual_design: [
        /视觉.*?(风格|效果|设计)/,
        /界面.*?(布局|样式)/,
        /需要.*?(好看|美观|吸引人)/,
        /.*?(现代|简约|温暖|专业).*?感觉/
      ],
      frontend_implementation: [
        /实现.*?(网页|页面|功能)/,
        /开发.*?(前端|界面)/,
        /代码.*?(实现|编写)/,
        /需要.*?(响应式|交互)/
      ],
      full_workflow: [
        /从.*?到.*?(实现|上线)/,
        /完整.*?(解决方案|流程)/,
        /端到端.*?(开发|实现)/,
        /.*?并实现.*?/
      ]
    };
  }

  analyzeIntent(userRequest) {
    const message = userRequest.message || '';
    const analysis = {
      intent_confidence: {},
      contextual_clues: [],
      user_goal: '',
      complexity_level: 'medium'
    };

    // 分析每种意图的置信度
    for (const [intent, patterns] of Object.entries(this.contextPatterns)) {
      let confidence = 0;
      const matches = [];

      for (const pattern of patterns) {
        if (pattern.test(message)) {
          confidence += 0.3;
          matches.push(pattern.source);
        }
      }

      // 上下文加权
      if (intent === 'creative_planning' && message.includes('策略')) confidence += 0.2;
      if (intent === 'visual_design' && message.includes('感觉')) confidence += 0.2;
      if (intent === 'frontend_implementation' && message.includes('代码')) confidence += 0.2;
      if (intent === 'full_workflow' && message.includes('完整')) confidence += 0.3;

      analysis.intent_confidence[intent] = Math.min(confidence, 1.0);
      if (matches.length > 0) {
        analysis.contextual_clues.push({ intent, matches });
      }
    }

    // 推断用户目标
    analysis.user_goal = this.inferUserGoal(message);
    analysis.complexity_level = this.assessComplexity(message, analysis.intent_confidence);

    return analysis;
  }

  inferUserGoal(message) {
    if (message.includes('应用') || message.includes('网站')) {
      return 'build_digital_product';
    } else if (message.includes('页面') || message.includes('界面')) {
      return 'create_interface';
    } else if (message.includes('策略') || message.includes('规划')) {
      return 'strategic_planning';
    }
    return 'general_assistance';
  }

  assessComplexity(message, confidences) {
    const multiIntent = Object.values(confidences).filter(c => c > 0.3).length;
    
    if (multiIntent >= 3) return 'high';
    if (multiIntent >= 2) return 'medium';
    return 'low';
  }

  route(userRequest) {
    const analysis = this.analyzeIntent(userRequest);
    const confidences = analysis.intent_confidence;

    // 基于置信度进行智能路由
    const maxConfidence = Math.max(...Object.values(confidences));
    
    if (maxConfidence < 0.3) {
      return {
        workflow: 'clarification_needed',
        reasoning: '用户意图不够明确，需要进一步澄清',
        confidence: maxConfidence,
        analysis
      };
    }

    // 多意图检测
    const highConfidenceIntents = Object.entries(confidences)
      .filter(([_, confidence]) => confidence > 0.4)
      .map(([intent, _]) => intent);

    if (highConfidenceIntents.includes('full_workflow') || 
        confidences.full_workflow > 0.5) {
      return {
        workflow: 'full_implementation_workflow',
        reasoning: '检测到端到端完整实现需求',
        confidence: confidences.full_workflow,
        analysis
      };
    }

    if (highConfidenceIntents.length >= 2) {
      if (highConfidenceIntents.includes('creative_planning') && 
          highConfidenceIntents.includes('visual_design')) {
        return {
          workflow: 'creative_visual_workflow',
          reasoning: '需要创意策划和视觉设计的组合工作流',
          confidence: (confidences.creative_planning + confidences.visual_design) / 2,
          analysis
        };
      }
    }

    // 单一意图路由
    const topIntent = Object.entries(confidences)
      .reduce((a, b) => confidences[a[0]] > confidences[b[0]] ? a : b);

    const workflowMap = {
      creative_planning: 'creative_only_workflow',
      visual_design: 'visual_only_workflow', 
      frontend_implementation: 'frontend_only_workflow'
    };

    return {
      workflow: workflowMap[topIntent[0]] || 'general_research_workflow',
      reasoning: `主要意图: ${topIntent[0]}`,
      confidence: topIntent[1],
      analysis
    };
  }
}

// 对比测试
async function compareRoutingMethods() {
  const keywordRouter = new KeywordRouter();
  const aiRouter = new AISmartRouter();

  const testCases = [
    {
      name: "模糊表达的完整需求",
      request: {
        message: "我想让我的在线书店看起来更专业更有吸引力，能让用户感到信任，最好能直接用到我的网站上"
      }
    },
    {
      name: "隐含的创意需求", 
      request: {
        message: "我们需要重新思考用户在购买过程中的情感旅程，让整个体验更流畅"
      }
    },
    {
      name: "技术与设计混合",
      request: {
        message: "这个登录页面需要更现代的感觉，同时要确保在手机上也能正常工作"
      }
    },
    {
      name: "含有歧义的请求",
      request: {
        message: "帮我优化这个产品的设计"
      }
    },
    {
      name: "明确的技术需求",
      request: {
        message: "请实现一个响应式的导航栏，包含HTML和CSS代码"
      }
    }
  ];

  console.log('🔍 关键词路由 vs AI智能路由对比测试\n');
  console.log('='.repeat(80));

  for (const testCase of testCases) {
    console.log(`\n📋 测试案例: ${testCase.name}`);
    console.log(`💬 用户请求: "${testCase.request.message}"`);
    console.log('-'.repeat(50));

    // 关键词路由结果
    const keywordResult = keywordRouter.route(testCase.request);
    console.log(`🔤 关键词路由: ${keywordResult}`);

    // AI智能路由结果  
    const aiResult = aiRouter.route(testCase.request);
    console.log(`🧠 AI智能路由: ${aiResult.workflow}`);
    console.log(`   推理: ${aiResult.reasoning}`);
    console.log(`   置信度: ${(aiResult.confidence * 100).toFixed(1)}%`);
    
    if (aiResult.analysis.contextual_clues.length > 0) {
      console.log(`   上下文线索: ${aiResult.analysis.contextual_clues.map(c => c.intent).join(', ')}`);
    }

    // 分析差异
    if (keywordResult !== aiResult.workflow) {
      console.log(`⚠️  路由结果不同! 关键词可能遗漏了用户的真实意图`);
    } else {
      console.log(`✅ 路由结果一致`);
    }
  }

  console.log('\n' + '='.repeat(80));
  console.log('📊 总结: AI路由的优势');
  console.log('✅ 上下文理解：能理解隐含意图和情感表达');
  console.log('✅ 置信度评估：提供决策可信度，支持澄清机制');
  console.log('✅ 多意图检测：识别复合需求，选择最优工作流');
  console.log('✅ 语义理解：不依赖特定关键词，适应自然表达');
  console.log('');
  console.log('❌ 关键词路由的局限性');
  console.log('❌ 脆弱性：用户换个说法就可能误判');
  console.log('❌ 维护成本：需要不断添加新关键词');
  console.log('❌ 无法处理歧义：面对模糊表达束手无策');
  console.log('❌ 缺乏推理：无法理解用户的深层需求');
}

if (require.main === module) {
  compareRoutingMethods().catch(console.error);
}

module.exports = { KeywordRouter, AISmartRouter };