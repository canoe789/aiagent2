/**
 * 创意总监 / 首席故事官 Agent
 * 
 * 专注于将原始素材转化为具有情感共鸣的创意蓝图
 * 通过三幕剧思考仪式，从信息到故事的深度转化
 */

class CreativeDirectorAgent {
  constructor(options = {}) {
    this.memory = options.memory;
    this.orchestrator = options.orchestrator;
    
    this.agentInfo = {
      name: "Creative Director",
      role: "首席故事官",
      version: "1.1",
      specialization: "情感驱动的内容架构设计"
    };
    
    // 核心叙事框架库
    this.frameworks = {
      comparison: {
        name: "对比思维模型",
        description: "A vs B Framework - 通过对比突出差异，简化决策",
        whenToUse: "涉及两个或多个事物比较时",
        emotionalAppeal: "快速搞懂差异、帮我做选择"
      },
      ranking: {
        name: "分层排行思维模型",
        description: "Ranking Framework - 满足人们对秩序和等级的需求",
        whenToUse: "包含可排序数据或明确层级关系时",
        emotionalAppeal: "定位自身位置、识别头部信息"
      },
      process: {
        name: "流程因果思维模型",
        description: "Process & Causality Framework - 拆解复杂系统为线性步骤",
        whenToUse: "需要解释过程、步骤或事件来龙去脉时",
        emotionalAppeal: "理解运作黑箱、消除困惑焦虑"
      },
      checklist: {
        name: "清单矩阵思维模型",
        description: "Matrix / Checklist Framework - 提供打包好的知识清单",
        whenToUse: "盘点趋势、总结经验、推荐资源时",
        emotionalAppeal: "怕错过、求盘点、一键收藏价值感"
      },
      system: {
        name: "系统解构思维模型",
        description: "System Map Framework - 提供上帝视角看清全局",
        whenToUse: "展示组织业务构成、产业链关系时",
        emotionalAppeal: "强烈好奇心、理解复杂系统内部运作"
      },
      case: {
        name: "案例剖析思维模型",
        description: "Case Study / Archetype Framework - 通过具体故事具象化理论",
        whenToUse: "解释商业模式、成功路径、策略时",
        emotionalAppeal: "故事是理解世界最有效方式"
      },
      analogy: {
        name: "类比隐喻思维模型",
        description: "Analogy / Metaphor Framework - 将陌生概念与已知事物联系",
        whenToUse: "解释专业术语或复杂原理时",
        emotionalAppeal: "降低认知负荷的终极武器"
      }
    };
  }

  /**
   * 处理创意任务 - 主入口
   */
  async processCreativeTask(taskPayload) {
    console.log(`🎨 创意总监开始处理任务: ${taskPayload.project_id}`);
    
    try {
      // 第一幕：同理心潜航
      const empathyInsights = await this.empathyDeepDive(taskPayload);
      
      // 第二幕：框架角斗场
      const frameworkBattle = await this.frameworkArena(taskPayload, empathyInsights);
      
      // 第三幕：创作蓝图绘制
      const creativeBrief = await this.createBlueprintDraft(taskPayload, empathyInsights, frameworkBattle);
      
      // 生成最终输出
      const finalOutput = this.generateFinalOutput(taskPayload, creativeBrief);
      
      // 存储到记忆库
      await this.storeCreativeBrief(taskPayload.project_id, finalOutput);
      
      console.log(`✅ 创意蓝图已完成: ${taskPayload.project_id}`);
      return finalOutput;
      
    } catch (error) {
      console.error(`❌ 创意总监处理失败:`, error);
      throw error;
    }
  }

  /**
   * 第一幕：同理心潜航
   */
  async empathyDeepDive(taskPayload) {
    console.log(`🔍 第一幕：同理心潜航 - 理解用户内心`);
    
    const rawContent = taskPayload.content || taskPayload.message || '';
    
    // 1. 素材本质透视
    const coreEntities = this.extractCoreEntities(rawContent);
    const entityRelationships = this.analyzeRelationships(coreEntities);
    
    // 2. 用户画像速写
    const userPersona = this.createUserPersona(taskPayload, rawContent);
    
    // 3. 挖掘内心独白
    const innerMonologue = this.extractInnerMonologue(userPersona, rawContent);
    
    return {
      coreEntities,
      entityRelationships,
      userPersona,
      innerMonologue,
      rawContent
    };
  }

  /**
   * 第二幕：框架角斗场
   */
  async frameworkArena(taskPayload, empathyInsights) {
    console.log(`⚔️ 第二幕：框架角斗场 - 选择最佳叙事框架`);
    
    // 1. 候选框架入场
    const candidates = this.selectCandidateFrameworks(empathyInsights);
    
    // 2. 模拟对决与观众反馈
    const battleResults = [];
    for (const candidate of candidates) {
      const pros = this.evaluateFrameworkPros(candidate, empathyInsights);
      const cons = this.evaluateFrameworkCons(candidate, empathyInsights);
      
      battleResults.push({
        framework: candidate,
        pros,
        cons,
        score: this.calculateFrameworkScore(pros, cons, empathyInsights)
      });
    }
    
    // 3. 桂冠授予
    const winner = battleResults.reduce((best, current) => 
      current.score > best.score ? current : best
    );
    
    const justification = this.createJustification(winner, battleResults, empathyInsights);
    
    return {
      candidates,
      battleResults,
      winner: winner.framework,
      justification
    };
  }

  /**
   * 第三幕：创作蓝图绘制
   */
  async createBlueprintDraft(taskPayload, empathyInsights, frameworkBattle) {
    console.log(`📝 第三幕：创作蓝图绘制 - 构建情感化故事结构`);
    
    // 1. 确立情感目标
    const desiredFeeling = this.defineDesiredFeeling(empathyInsights, frameworkBattle.winner);
    
    // 2. 设计破冰标题
    const iceBreakingHeadline = this.designHeadline(empathyInsights.innerMonologue);
    
    // 3. 规划故事线区块
    const storyChapters = this.planStorylineChapters(
      empathyInsights.rawContent, 
      frameworkBattle.winner,
      desiredFeeling
    );
    
    // 4. 构建叙事策略
    const narrativeStrategy = {
      target_user_persona: empathyInsights.userPersona.description,
      user_story: empathyInsights.userPersona.scenario,
      desired_feeling: desiredFeeling,
      main_quest: this.defineMainQuest(empathyInsights, frameworkBattle.winner),
      core_conflict: empathyInsights.innerMonologue,
      storyline_summary: this.createStorylineSummary(storyChapters)
    };
    
    return {
      strategicChoice: {
        chosen_framework: frameworkBattle.winner.name,
        justification: frameworkBattle.justification
      },
      narrativeStrategy,
      contentStructure: storyChapters,
      iceBreakingHeadline
    };
  }

  /**
   * 提取核心实体
   */
  extractCoreEntities(content) {
    // 简化实现 - 在实际应用中可以使用NLP技术
    const entities = [];
    
    // 检测价格信息
    if (content.match(/\d+元|\$\d+|价格|费用/)) {
      entities.push({ type: 'price', importance: 'high' });
    }
    
    // 检测时间信息
    if (content.match(/时间|日期|\d+天|\d+小时/)) {
      entities.push({ type: 'time', importance: 'medium' });
    }
    
    // 检测流程步骤
    if (content.match(/步骤|流程|第\d+|首先|然后|最后/)) {
      entities.push({ type: 'process', importance: 'high' });
    }
    
    // 检测比较内容
    if (content.match(/vs|对比|比较|区别|优势|劣势/)) {
      entities.push({ type: 'comparison', importance: 'high' });
    }
    
    return entities;
  }

  /**
   * 创建用户画像
   */
  createUserPersona(taskPayload, content) {
    // 基于内容类型和任务推断用户画像
    let persona = {};
    
    if (content.includes('投资') || content.includes('股票') || content.includes('理财')) {
      persona = {
        identity: "一个对投资理财感兴趣但经验有限的上班族",
        demographics: "25-35岁，有一定收入，想要理财增值",
        motivation: "希望通过投资实现财务自由，但担心风险",
        painPoints: "信息太多不知道选择，怕亏钱，缺乏专业知识",
        description: "李明，28岁软件工程师，月薪1.5万，想要开始投资但不知从何入手",
        scenario: "下班后在家里用手机搜索投资信息，希望找到靠谱的理财方式"
      };
    } else if (content.includes('旅游') || content.includes('景点') || content.includes('门票')) {
      persona = {
        identity: "一个计划出行的家庭主妇",
        demographics: "30-40岁，有孩子，重视家庭生活质量",
        motivation: "想要给家人安排一次完美的旅行",
        painPoints: "预算有限，担心花冤枉钱，希望行程安排合理",
        description: "王女士，35岁，两个孩子的妈妈，正在规划暑假家庭旅行",
        scenario: "晚上孩子睡觉后，在沙发上用平板电脑查看旅游攻略"
      };
    } else {
      persona = {
        identity: "一个寻求信息的普通用户",
        demographics: "20-45岁，使用移动设备获取信息",
        motivation: "快速找到有用的信息",
        painPoints: "信息过载，不知道什么是重要的",
        description: "现代都市人，生活节奏快，希望高效获取信息",
        scenario: "在地铁上或休息间隙使用手机查找相关信息"
      };
    }
    
    return persona;
  }

  /**
   * 提取内心独白
   */
  extractInnerMonologue(persona, content) {
    const painPoints = persona.painPoints;
    
    if (painPoints.includes('选择')) {
      return "天啊，选择这么多，到底哪个才是我需要的？别让我花冤枉钱！";
    } else if (painPoints.includes('风险')) {
      return "这个看起来不错，但会不会有什么坑？我可不想被套路...";
    } else if (painPoints.includes('信息过载')) {
      return "信息太多了，我只想要最重要的几个要点，别让我脑子爆炸！";
    } else {
      return "希望这次能找到真正有用的信息，不要又是那些废话连篇的内容...";
    }
  }

  /**
   * 选择候选框架
   */
  selectCandidateFrameworks(empathyInsights) {
    const candidates = [];
    const entities = empathyInsights.coreEntities;
    const content = empathyInsights.rawContent.toLowerCase();
    
    // 优先基于内容关键词选择
    if (content.includes('比较') || content.includes('对比') || content.includes('vs') || 
        content.includes('优缺点') || content.includes('区别')) {
      candidates.push(this.frameworks.comparison);
    }
    
    if (content.includes('步骤') || content.includes('流程') || content.includes('如何') || 
        content.includes('指南') || content.includes('教程')) {
      candidates.push(this.frameworks.process);
    }
    
    if (content.includes('案例') || content.includes('故事') || content.includes('成功') || 
        content.includes('经验')) {
      candidates.push(this.frameworks.case);
    }
    
    // 基于实体类型补充
    if (entities.some(e => e.type === 'comparison') && !candidates.includes(this.frameworks.comparison)) {
      candidates.push(this.frameworks.comparison);
    }
    
    if (entities.some(e => e.type === 'process') && !candidates.includes(this.frameworks.process)) {
      candidates.push(this.frameworks.process);
    }
    
    // 清单框架作为默认选项（通用性强）
    if (!candidates.includes(this.frameworks.checklist)) {
      candidates.push(this.frameworks.checklist);
    }
    
    // 确保至少有3个候选
    if (candidates.length < 3) {
      const remaining = [
        this.frameworks.ranking,
        this.frameworks.system,
        this.frameworks.analogy
      ].filter(f => !candidates.includes(f));
      
      candidates.push(...remaining.slice(0, 3 - candidates.length));
    }
    
    return candidates.slice(0, 3);
  }

  /**
   * 评估框架优势
   */
  evaluateFrameworkPros(framework, empathyInsights) {
    const userPainPoints = empathyInsights.userPersona.painPoints;
    
    switch (framework.name) {
      case "对比思维模型":
        return "快速明确差异，简化选择决策，直击用户'不知道选哪个'的痛点";
      case "流程因果思维模型":
        return "step-by-step降低认知负荷，让复杂信息变得可操作";
      case "清单矩阵思维模型":
        return "提供完整要点盘点，满足'怕错过'心理，便于收藏和分享";
      default:
        return "提供清晰的信息组织结构，提升用户理解效率";
    }
  }

  /**
   * 评估框架劣势
   */
  evaluateFrameworkCons(framework, empathyInsights) {
    switch (framework.name) {
      case "对比思维模型":
        return "如果选项过多可能造成选择困难，需要预先筛选";
      case "流程因果思维模型":
        return "过于线性化可能忽略用户的个性化需求";
      case "清单矩阵思维模型":
        return "可能导致信息平铺，缺乏重点突出";
      default:
        return "可能不够针对用户的具体使用场景";
    }
  }

  /**
   * 计算框架分数
   */
  calculateFrameworkScore(pros, cons, empathyInsights) {
    // 简化评分逻辑
    let score = 50; // 基础分
    
    // 根据用户痛点调整分数
    const painPoints = empathyInsights.userPersona.painPoints;
    const content = empathyInsights.rawContent.toLowerCase();
    
    // 内容类型匹配奖励
    if (content.includes('比较') || content.includes('对比') || content.includes('vs') || content.includes('优缺点')) {
      if (pros.includes('选择') || pros.includes('差异')) {
        score += 40; // 对比框架优势
      }
    }
    
    if (content.includes('步骤') || content.includes('如何') || content.includes('流程')) {
      if (pros.includes('step-by-step') || pros.includes('降低认知负荷')) {
        score += 35;
      }
    }
    
    // 用户痛点匹配
    if (painPoints.includes('选择') && pros.includes('选择')) {
      score += 30;
    }
    if (painPoints.includes('信息过载') && pros.includes('要点')) {
      score += 25;
    }
    if (painPoints.includes('专业知识') && pros.includes('step-by-step')) {
      score += 20;
    }
    
    // 劣势惩罚
    if (cons.includes('选择困难') && painPoints.includes('选择')) {
      score -= 15;
    }
    
    return score;
  }

  /**
   * 创建选择理由
   */
  createJustification(winner, battleResults, empathyInsights) {
    const persona = empathyInsights.userPersona.identity;
    const painPoint = empathyInsights.innerMonologue;
    
    return `${winner.framework.name}最终胜出，因为它完美契合了${persona}的核心需求。面对"${painPoint}"这样的心理状态，${winner.pros}。同时，它巧妙地规避了其他框架可能带来的认知负担，正是当前场景下的最佳解药。`;
  }

  /**
   * 定义期望情感
   */
  defineDesiredFeeling(empathyInsights, winnerFramework) {
    const painPoints = empathyInsights.userPersona.painPoints;
    
    if (painPoints.includes('选择')) {
      return "豁然开朗、胸有成竹、感觉自己做了个聪明的决定";
    } else if (painPoints.includes('风险')) {
      return "安心踏实、一切尽在掌握、对未来充满信心";
    } else {
      return "信息获取高效、重点清晰明确、觉得时间花得值";
    }
  }

  /**
   * 设计标题
   */
  designHeadline(innerMonologue) {
    if (innerMonologue.includes('选择')) {
      return "3分钟搞定选择难题，让决策变得简单明了";
    } else if (innerMonologue.includes('坑')) {
      return "避坑指南：聪明人都在用的判断标准";
    } else if (innerMonologue.includes('要点')) {
      return "核心要点全梳理，这一篇就够了";
    } else {
      return "终于找到了！最实用的解决方案在这里";
    }
  }

  /**
   * 规划故事章节
   */
  planStorylineChapters(content, framework, desiredFeeling) {
    const chapters = [];
    
    // 根据框架类型规划章节结构
    if (framework.name === "对比思维模型") {
      chapters.push({
        chapter: 1,
        chapter_title: "选择困难？先看这个对比清单",
        chosen_framework: framework.name,
        justification: "开篇就解决用户最大痛点：选择焦虑",
        key_points: "关键差异点A\n关键差异点B\n关键差异点C"
      });
      
      chapters.push({
        chapter: 2,
        chapter_title: "深度解析：哪个更适合你？",
        chosen_framework: framework.name,
        justification: "提供个性化判断标准，赋予用户决策权力",
        key_points: "适用场景分析\n个人情况匹配\n决策建议"
      });
      
    } else if (framework.name === "清单矩阵思维模型") {
      chapters.push({
        chapter: 1,
        chapter_title: "核心要点一览表",
        chosen_framework: framework.name,
        justification: "快速概览，满足用户'一眼看全'的需求",
        key_points: "要点1：核心概念\n要点2：关键数据\n要点3：重要提醒"
      });
      
      chapters.push({
        chapter: 2,
        chapter_title: "详细说明与注意事项",
        chosen_framework: framework.name,
        justification: "深入展开，确保用户理解透彻",
        key_points: "详细解释\n实操建议\n常见误区"
      });
      
    } else {
      // 默认流程化结构
      chapters.push({
        chapter: 1,
        chapter_title: "快速入门指南",
        chosen_framework: framework.name,
        justification: "降低认知门槛，让用户快速上手",
        key_points: "基础概念\n重要前提\n准备工作"
      });
      
      chapters.push({
        chapter: 2,
        chapter_title: "实操步骤详解",
        chosen_framework: framework.name,
        justification: "提供具体可执行的行动方案",
        key_points: "步骤1：...\n步骤2：...\n步骤3：..."
      });
    }
    
    return chapters;
  }

  /**
   * 定义主要任务
   */
  defineMainQuest(empathyInsights, framework) {
    const motivation = empathyInsights.userPersona.motivation;
    return `帮助用户${motivation}，通过${framework.name}提供清晰的行动指导`;
  }

  /**
   * 创建故事线摘要
   */
  createStorylineSummary(chapters) {
    const chapterTitles = chapters.map(c => c.chapter_title).join(' → ');
    return `从困惑到清晰的完整旅程：${chapterTitles}`;
  }

  /**
   * 生成最终输出
   */
  generateFinalOutput(taskPayload, creativeBrief) {
    return {
      asset_type: "CREATIVE_BRIEF",
      asset_version: "1.1",
      project_id: taskPayload.project_id,
      payload: {
        strategic_choice: creativeBrief.strategicChoice,
        narrative_strategy: creativeBrief.narrativeStrategy,
        content_structure: creativeBrief.contentStructure
      }
    };
  }

  /**
   * 存储创意蓝图到记忆库
   */
  async storeCreativeBrief(projectId, creativeBrief) {
    if (this.memory) {
      await this.memory.setContext(projectId, 'creative_brief', creativeBrief);
      console.log(`💾 创意蓝图已存储到记忆库: ${projectId}`);
    }
  }

  /**
   * 分析实体关系
   */
  analyzeRelationships(entities) {
    // 简化实现
    return entities.map(e => e.type).join(' → ');
  }

  /**
   * 获取Agent信息
   */
  getAgentInfo() {
    return this.agentInfo;
  }
}

module.exports = { CreativeDirectorAgent };