/**
 * 视觉总监 / 概念艺术家 Agent
 * 
 * 专注于将创意蓝图转化为具有感染力的视觉概念方向
 * 通过三幕剧思考仪式，从故事到画面的深度转化
 */

class VisualDirectorAgent {
  constructor(options = {}) {
    this.memory = options.memory;
    this.orchestrator = options.orchestrator;
    
    this.agentInfo = {
      name: "Visual Director",
      role: "概念艺术家",
      version: "1.0",
      specialization: "视觉概念设计与情感表达"
    };
    
    // 视觉风格库 - 用于灵感和方向指导
    this.visualStyles = {
      cinematic: {
        name: "电影级叙事",
        characteristics: ["戏剧化光影", "深度景深", "情感色温", "动态构图"],
        mood: "史诗感、沉浸感"
      },
      minimalist: {
        name: "极简主义",
        characteristics: ["留白艺术", "几何纯粹", "单色调和", "功能美学"],
        mood: "宁静、专注、纯粹"
      },
      organic: {
        name: "有机自然",
        characteristics: ["流动曲线", "自然纹理", "渐变过渡", "生命韵律"],
        mood: "温暖、亲和、生命力"
      },
      futuristic: {
        name: "未来科技",
        characteristics: ["霓虹辉光", "数字美学", "全息质感", "动态效果"],
        mood: "前瞻、创新、科技感"
      },
      retro: {
        name: "复古怀旧",
        characteristics: ["胶片质感", "暖色调色", "手工细节", "时光印记"],
        mood: "怀旧、温暖、人文情怀"
      },
      luxury: {
        name: "奢华精致",
        characteristics: ["金属质感", "细腻材质", "优雅比例", "精工细节"],
        mood: "高端、精致、品质感"
      }
    };
  }

  /**
   * 处理视觉设计任务 - 主入口
   */
  async processVisualTask(taskPayload) {
    console.log(`🎨 视觉总监开始处理任务: ${taskPayload.project_id}`);
    
    try {
      // 从记忆库读取创意蓝图
      const creativeBrief = await this.readCreativeBrief(taskPayload.project_id);
      
      if (!creativeBrief) {
        throw new Error(`无法找到项目 ${taskPayload.project_id} 的创意蓝图`);
      }
      
      // 第一幕：故事沉浸与解码
      const storyImmersion = await this.storyImmersionPhase(creativeBrief);
      
      // 第二幕：平行宇宙构想
      const visualConcepts = await this.parallelUniversesPhase(creativeBrief, storyImmersion);
      
      // 第三幕：概念画板呈现
      const conceptArtboard = await this.conceptArtboardPhase(visualConcepts, creativeBrief);
      
      // 存储到记忆库
      await this.storeVisualConcepts(taskPayload.project_id, conceptArtboard);
      
      console.log(`✅ 视觉概念已完成: ${taskPayload.project_id}`);
      return conceptArtboard;
      
    } catch (error) {
      console.error(`❌ 视觉总监处理失败:`, error);
      throw error;
    }
  }

  /**
   * 从记忆库读取创意蓝图
   */
  async readCreativeBrief(projectId) {
    try {
      // 直接通过键读取创意蓝图
      const creativeBrief = await this.memory.getContext(projectId, 'creative_brief');
      
      if (!creativeBrief) {
        console.warn(`项目 ${projectId} 暂无创意蓝图`);
        return null;
      }
      
      return creativeBrief;
    } catch (error) {
      console.error(`无法读取项目 ${projectId} 的创意蓝图:`, error);
      return null;
    }
  }

  /**
   * 第一幕：故事沉浸与解码
   */
  async storyImmersionPhase(creativeBrief) {
    console.log(`🔍 第一幕：故事沉浸与解码 - 提取视觉灵魂`);
    
    const payload = creativeBrief.payload;
    const narrativeStrategy = payload.narrative_strategy;
    
    // 1. 情感共振
    const emotionalResonance = {
      userPersona: narrativeStrategy.target_user_persona,
      userStory: narrativeStrategy.user_story,
      desiredFeeling: narrativeStrategy.desired_feeling,
      coreConflict: narrativeStrategy.core_conflict,
      emotionalJourney: this.extractEmotionalJourney(narrativeStrategy)
    };
    
    // 2. 提取视觉关键词
    const visualKeywords = this.extractVisualKeywords(creativeBrief);
    
    // 3. 分析内容结构的视觉暗示
    const structuralHints = this.analyzeStructuralVisualHints(payload.content_structure);
    
    return {
      emotionalResonance,
      visualKeywords,
      structuralHints,
      briefContext: creativeBrief
    };
  }

  /**
   * 第二幕：平行宇宙构想
   */
  async parallelUniversesPhase(creativeBrief, storyImmersion) {
    console.log(`⚔️ 第二幕：平行宇宙构想 - 创造三个视觉世界`);
    
    // 基于情感目标和关键词选择3种不同的视觉方向
    const selectedStyles = this.selectVisualStyles(storyImmersion);
    
    const visualConcepts = [];
    
    for (let i = 0; i < 3; i++) {
      const style = selectedStyles[i];
      const concept = await this.createVisualConcept(
        style, 
        storyImmersion, 
        creativeBrief,
        i + 1
      );
      visualConcepts.push(concept);
    }
    
    return visualConcepts;
  }

  /**
   * 第三幕：概念画板呈现
   */
  async conceptArtboardPhase(visualConcepts, creativeBrief) {
    console.log(`📝 第三幕：概念画板呈现 - 构建最终输出`);
    
    return {
      asset_type: "VISUAL_CONCEPTS",
      asset_version: "1.0",
      project_id: creativeBrief.project_id,
      source_brief: creativeBrief.asset_type,
      visual_explorations: visualConcepts.map(concept => ({
        concept_name: concept.name,
        core_metaphor: concept.metaphor,
        atmosphere: concept.atmosphere,
        color_narrative: concept.colorStory,
        signature_interaction: concept.signatureInteraction
      }))
    };
  }

  /**
   * 提取情感旅程
   */
  extractEmotionalJourney(narrativeStrategy) {
    const feelings = narrativeStrategy.desired_feeling.split('、');
    const conflict = narrativeStrategy.core_conflict;
    
    return {
      starting_emotion: this.inferStartingEmotion(conflict),
      journey_stages: feelings,
      end_emotion: feelings[feelings.length - 1] || "满足感"
    };
  }

  /**
   * 提取视觉关键词
   */
  extractVisualKeywords(creativeBrief) {
    const text = JSON.stringify(creativeBrief).toLowerCase();
    
    const keywords = {
      functional: [],
      emotional: [],
      metaphorical: []
    };
    
    // 功能性关键词
    if (text.includes('对比') || text.includes('比较')) {
      keywords.functional.push('对比', '差异', '选择');
    }
    if (text.includes('清单') || text.includes('要点')) {
      keywords.functional.push('列表', '整理', '条理');
    }
    if (text.includes('步骤') || text.includes('流程')) {
      keywords.functional.push('引导', '进展', '路径');
    }
    
    // 情感性关键词
    if (text.includes('安心') || text.includes('信任')) {
      keywords.emotional.push('温暖', '稳定', '拥抱');
    }
    if (text.includes('清晰') || text.includes('明确')) {
      keywords.emotional.push('光明', '透明', '清澈');
    }
    if (text.includes('效率') || text.includes('快速')) {
      keywords.emotional.push('流畅', '敏捷', '直接');
    }
    
    // 隐喻性关键词
    if (text.includes('旅程') || text.includes('路径')) {
      keywords.metaphorical.push('道路', '指南针', '地图');
    }
    if (text.includes('选择') || text.includes('决策')) {
      keywords.metaphorical.push('天平', '路口', '门');
    }
    
    return keywords;
  }

  /**
   * 分析结构的视觉暗示
   */
  analyzeStructuralVisualHints(contentStructure) {
    const hints = {
      layout_pattern: '线性',
      hierarchy_style: '平等',
      navigation_metaphor: '翻页'
    };
    
    if (contentStructure.length === 2) {
      hints.layout_pattern = '对称';
      hints.navigation_metaphor = '左右对比';
    } else if (contentStructure.length >= 3) {
      hints.layout_pattern = '网格';
      hints.navigation_metaphor = '卡片切换';
    }
    
    // 基于章节标题推断层级
    const hasComparison = contentStructure.some(ch => 
      ch.chapter_title.includes('对比') || ch.chapter_title.includes('选择')
    );
    
    if (hasComparison) {
      hints.hierarchy_style = '差异突出';
      hints.navigation_metaphor = '天平摆动';
    }
    
    return hints;
  }

  /**
   * 选择视觉风格
   */
  selectVisualStyles(storyImmersion) {
    const keywords = storyImmersion.visualKeywords;
    const emotion = storyImmersion.emotionalResonance.desiredFeeling;
    
    const styles = [];
    
    // 基于情感选择主要风格
    if (emotion.includes('清晰') || emotion.includes('效率')) {
      styles.push(this.visualStyles.minimalist);
    } else if (emotion.includes('安心') || emotion.includes('信任')) {
      styles.push(this.visualStyles.organic);
    } else {
      styles.push(this.visualStyles.cinematic);
    }
    
    // 添加对比风格
    if (keywords.functional.includes('对比')) {
      styles.push(this.visualStyles.luxury);
    } else {
      styles.push(this.visualStyles.futuristic);
    }
    
    // 第三个风格作为创意选择
    const remainingStyles = Object.values(this.visualStyles)
      .filter(style => !styles.includes(style));
    styles.push(remainingStyles[0] || this.visualStyles.retro);
    
    return styles.slice(0, 3);
  }

  /**
   * 创建单个视觉概念
   */
  async createVisualConcept(style, storyImmersion, creativeBrief, index) {
    const emotion = storyImmersion.emotionalResonance;
    const keywords = storyImmersion.visualKeywords;
    
    // 生成概念名称
    const conceptName = this.generateConceptName(style, emotion, index);
    
    // 生成核心比喻
    const coreMetaphor = this.generateCoreMetaphor(style, emotion, keywords);
    
    // 生成氛围描述
    const atmosphere = this.generateAtmosphere(style, emotion);
    
    // 生成色彩叙事
    const colorStory = this.generateColorNarrative(style, emotion);
    
    // 生成标志性交互
    const signatureInteraction = this.generateSignatureInteraction(style, storyImmersion);
    
    return {
      name: conceptName,
      metaphor: coreMetaphor,
      atmosphere: atmosphere,
      colorStory: colorStory,
      signatureInteraction: signatureInteraction,
      style: style.name
    };
  }

  /**
   * 生成概念名称
   */
  generateConceptName(style, emotion, index) {
    const themes = {
      cinematic: ["深度叙事", "情感镜头", "戏剧光影"],
      minimalist: ["纯净空间", "专注之境", "简约诗意"],
      organic: ["自然韵律", "生命脉动", "温暖拥抱"],
      futuristic: ["数字新境", "未来织梦", "科技诗篇"],
      retro: ["时光印记", "怀旧情怀", "记忆温度"],
      luxury: ["精致细节", "品质美学", "奢华体验"]
    };
    
    const styleKey = Object.keys(this.visualStyles).find(key => 
      this.visualStyles[key] === style
    );
    
    const options = themes[styleKey] || ["创意概念", "视觉故事", "设计理念"];
    return options[index - 1] || `${style.name}世界`;
  }

  /**
   * 生成核心比喻
   */
  generateCoreMetaphor(style, emotion, keywords) {
    const metaphors = {
      cinematic: `用户的每一次交互，都像是在观看一部为他个人定制的情感电影，界面元素如同镜头语言，引导着他的视线和心情。`,
      minimalist: `界面如同一座禅意花园，每个元素都经过精心雕琢，用户的目光如清风拂过，专注而宁静。`,
      organic: `整个体验如同漫步在温暖的森林中，每个功能都像自然生长的果实，触手可及且充满生命力。`,
      futuristic: `用户置身于一个智能的数字生态系统中，每次点击都像是与未来对话，界面响应如光速般敏锐。`,
      retro: `界面承载着时光的温度，每个元素都像是精心保存的记忆，用户在怀旧中找到现代的便利。`,
      luxury: `每次交互都是一次品质体验的仪式，界面如同精工制作的艺术品，细节彰显着品味和专业。`
    };
    
    const styleKey = Object.keys(this.visualStyles).find(key => 
      this.visualStyles[key] === style
    );
    
    return metaphors[styleKey] || "用户与界面的每次互动，都是一次独特的情感交流体验。";
  }

  /**
   * 生成氛围描述
   */
  generateAtmosphere(style, emotion) {
    const baseAtmosphere = style.mood;
    const lightingMood = this.inferLightingMood(emotion.desiredFeeling);
    const materialFeel = this.inferMaterialFeel(emotion.desiredFeeling);
    
    return `${baseAtmosphere}的整体基调，${lightingMood}的光影效果，${materialFeel}的材质触感。空间感营造出${emotion.desiredFeeling}的情感氛围，让用户在视觉和心理上都能感受到这种独特的${style.characteristics.join('、')}美学。`;
  }

  /**
   * 生成色彩叙事
   */
  generateColorNarrative(style, emotion) {
    const colorStories = {
      cinematic: "主色调采用电影级的深邃蓝调，象征着专业与信任，点缀色用温暖的琥珀金，在关键时刻点亮用户的希望。",
      minimalist: "以纯净的灰白为主调，代表着清晰与专注，偶尔出现的一抹鲜明色彩，如同思维的闪光瞬间。",
      organic: "温暖的大地色系贯穿始终，从浅绿到深褐，讲述着生命成长的故事，让用户感受到自然的包容与支持。",
      futuristic: "科技蓝与霓虹绿构成主要色彩语言，传达着创新与突破，渐变效果营造出数字世界的无限可能。",
      retro: "怀旧的暖色调，从米黄到深橘，承载着时光的记忆，每个色彩都诉说着岁月的温柔与智慧。",
      luxury: "低调的深色调配以精致的金属光泽，传达着品质与专业，细微的色彩变化展现着精工的匠心。"
    };
    
    const styleKey = Object.keys(this.visualStyles).find(key => 
      this.visualStyles[key] === style
    );
    
    return colorStories[styleKey] || "色彩搭配精心呼应着用户的情感需求，在视觉上营造出理想的体验氛围。";
  }

  /**
   * 生成标志性交互
   */
  generateSignatureInteraction(style, storyImmersion) {
    const conflict = storyImmersion.emotionalResonance.coreConflict;
    
    const interactions = {
      cinematic: `当用户面临选择时，界面如电影般缓缓展开对比画面，光影在选项间流转，用优雅的过渡动画引导用户的视线，最终锁定在最佳选择上，如同聚光灯找到了舞台的主角。`,
      minimalist: `用户的鼠标轻触界面，多余的元素如薄雾般消散，只留下最核心的信息在纯净的空间中闪闪发光，这种"减法"的美学让复杂变得简单。`,
      organic: `交互元素如花朵般自然绽放，用户的每次点击都像是给予阳光和水分，界面响应温和而充满生命力，仿佛有着自己的呼吸节奏。`,
      futuristic: `触碰瞬间，数字粒子从指尖散开，形成美丽的信息流，界面像活着的有机体般智能重组，预测并满足用户的下一个需求。`,
      retro: `点击时发出轻柔的机械音效，仿佛是老式收音机的调频声，界面切换带着胶片翻页的质感，在怀旧中给人安全感和确定性。`,
      luxury: `每次交互都伴随着精致的微动效，如丝绸般顺滑，细节处理一丝不苟，让用户感受到被精心呵护的尊贵体验。`
    };
    
    // 随机选择一个交互描述，或基于风格选择
    const styleKey = Object.keys(this.visualStyles).find(key => 
      this.visualStyles[key].name === storyImmersion.visualKeywords.emotional[0]
    ) || 'cinematic';
    
    return interactions[styleKey] || interactions.cinematic;
  }

  /**
   * 推断起始情感
   */
  inferStartingEmotion(conflict) {
    if (conflict.includes('困惑') || conflict.includes('迷茫')) {
      return '困惑焦虑';
    } else if (conflict.includes('选择') || conflict.includes('决策')) {
      return '选择恐惧';
    } else if (conflict.includes('信息过载')) {
      return '压力山大';
    } else {
      return '不确定感';
    }
  }

  /**
   * 推断光影情绪
   */
  inferLightingMood(desiredFeeling) {
    if (desiredFeeling.includes('清晰') || desiredFeeling.includes('明确')) {
      return '明亮通透';
    } else if (desiredFeeling.includes('安心') || desiredFeeling.includes('信任')) {
      return '温暖柔和';
    } else if (desiredFeeling.includes('效率') || desiredFeeling.includes('快速')) {
      return '锐利聚焦';
    } else {
      return '舒适宜人';
    }
  }

  /**
   * 推断材质感觉
   */
  inferMaterialFeel(desiredFeeling) {
    if (desiredFeeling.includes('专业') || desiredFeeling.includes('品质')) {
      return '精致细腻';
    } else if (desiredFeeling.includes('亲和') || desiredFeeling.includes('温暖')) {
      return '温润如玉';
    } else if (desiredFeeling.includes('现代') || desiredFeeling.includes('科技')) {
      return '光滑冷峻';
    } else {
      return '舒适自然';
    }
  }

  /**
   * 存储视觉概念到记忆库
   */
  async storeVisualConcepts(projectId, conceptArtboard) {
    if (this.memory) {
      await this.memory.setContext(projectId, 'visual_concepts', conceptArtboard);
      console.log(`💾 视觉概念已存储到记忆库: ${projectId}`);
    }
  }

  /**
   * 获取Agent信息
   */
  getAgentInfo() {
    return this.agentInfo;
  }
}

module.exports = { VisualDirectorAgent };