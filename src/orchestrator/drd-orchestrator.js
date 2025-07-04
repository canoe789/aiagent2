/**
 * DRD Orchestrator - 动态研究与决策框架
 * 
 * 实现4阶段循环：理解规划 → 并行执行 → 综合决策 → 质量交付
 * 专门处理复杂、模糊或需要深度研究的任务
 */

class DRDOrchestrator {
  constructor(options = {}) {
    this.memory = options.memory;
    this.helix = options.helix; // 引用主Orchestrator进行API调用
    this.maxResearchCycles = options.maxResearchCycles || 3;
    
    // DRD专用的系统提示词
    this.drdSystemPrompt = `你是HELIX动态研究与决策框架的核心引擎。你专门处理复杂、模糊或需要深度调研的任务。

你的工作遵循4阶段循环：

【阶段1：理解与规划】
- 深度分析用户需求的真实意图
- 识别不确定因素和知识缺口
- 制定并行研究计划，最多启动5个研究分支

【阶段2：并行执行与监控】  
- 同时执行多个独立的研究子任务
- 专注于数据收集、竞品分析、市场调研
- 监控各分支进度和质量

【阶段3：综合评估与决策】
- 综合所有研究结果
- 进行差距分析，判断是否需要更多研究
- 决定：继续研究 / 进入实施阶段 / 与用户澄清

【阶段4：质量保证与交付】
- 整合最终研究报告
- 如进入实施，委派给相应的专业Agent
- 确保输出质量和用户满意度

你擅长处理模糊需求、多变量分析、策略制定类任务。`;
  }

  /**
   * DRD框架主流程入口
   */
  async processDRDRequest(projectId, userRequest, classification) {
    console.log('🔬 启动DRD动态研究与决策框架');
    console.log(`📋 项目ID: ${projectId}`);
    
    // 存储原始请求
    this.originalRequest = userRequest;
    
    try {
      // 阶段1：理解与规划
      const planningResult = await this.phase1_understandAndPlan(projectId, userRequest, classification);
      
      if (planningResult.needsClarification) {
        return this.handleClarificationRequest(projectId, planningResult);
      }
      
      // 开始研究循环
      let currentCycle = 1;
      let researchComplete = false;
      let researchResults = null;
      
      while (!researchComplete && currentCycle <= this.maxResearchCycles) {
        console.log(`\n🔄 DRD研究循环 第${currentCycle}轮`);
        
        // 阶段2：并行执行与监控
        const executionResults = await this.phase2_parallelExecuteAndMonitor(projectId, planningResult);
        
        // 阶段3：综合评估与决策
        const evaluationResult = await this.phase3_synthesizeEvaluateAndDecide(projectId, executionResults);
        
        if (evaluationResult.decision === 'continue_research') {
          console.log(`📊 第${currentCycle}轮研究完成，需要继续深入研究`);
          // 更新研究计划，继续下一轮
          planningResult.researchPlan = evaluationResult.updatedPlan;
          currentCycle++;
        } else if (evaluationResult.decision === 'proceed_to_implementation') {
          console.log(`✅ 研究阶段完成，进入实施阶段`);
          researchComplete = true;
          researchResults = evaluationResult;
        } else if (evaluationResult.decision === 'clarify_with_user') {
          console.log(`❓ 需要用户澄清关键决策点`);
          return this.handleClarificationRequest(projectId, evaluationResult);
        }
      }
      
      if (!researchComplete) {
        console.log(`⚠️ 达到最大研究轮数(${this.maxResearchCycles})，强制进入实施阶段`);
        researchResults = await this.phase3_synthesizeEvaluateAndDecide(projectId, null, true);
      }
      
      // 阶段4：质量保证与交付
      return await this.phase4_qualityAssuranceAndDelivery(projectId, researchResults);
      
    } catch (error) {
      console.error('❌ DRD框架执行失败:', error);
      // 回退到简单工作流
      return this.fallbackToSimpleWorkflow(projectId, userRequest, classification);
    }
  }

  /**
   * 阶段1：理解与规划
   */
  async phase1_understandAndPlan(projectId, userRequest, classification) {
    console.log('🎯 阶段1：理解与规划');
    
    const planningPrompt = `${this.drdSystemPrompt}

用户请求分析：
消息：${userRequest.message}
类型：${userRequest.type || '未指定'}
AI分类：${classification.workflow}
用户意图：${classification.user_intent}
复杂度：${classification.complexity}

请制定详细的研究计划：
1. 深度分析用户的真实需求和目标
2. 识别关键的不确定因素和知识缺口
3. 设计3-5个并行研究分支，每个分支负责一个特定方面
4. 评估是否需要用户澄清

返回JSON格式：
{
  "user_needs_analysis": "深度需求分析",
  "uncertainty_factors": ["不确定因素列表"],
  "knowledge_gaps": ["知识缺口列表"],
  "research_branches": [
    {
      "branch_id": "research_1",
      "focus": "研究重点",
      "objectives": ["具体目标"],
      "methodology": "研究方法"
    }
  ],
  "needs_clarification": false,
  "clarification_questions": []
}`;

    const response = await this.helix.callGeminiAPI(planningPrompt, 0.3);
    const planningResult = this.parseGeminiResponse(response);
    
    // 存储研究计划
    await this.memory.setContext(projectId, 'drd_planning', planningResult);
    
    console.log(`📋 制定了${planningResult.research_branches?.length || 0}个研究分支`);
    console.log(`🔍 识别了${planningResult.uncertainty_factors?.length || 0}个不确定因素`);
    
    return planningResult;
  }

  /**
   * 阶段2：并行执行与监控
   */
  async phase2_parallelExecuteAndMonitor(projectId, planningResult) {
    console.log('⚡ 阶段2：并行执行与监控');
    
    const researchResults = [];
    const branches = planningResult.research_branches || [];
    
    // 控制并发执行研究分支，避免API速率限制
    const batchSize = 2; // 每批最多2个并发请求
    
    for (let i = 0; i < branches.length; i += batchSize) {
      const batch = branches.slice(i, i + batchSize);
      console.log(`🔄 执行研究分支批次 ${Math.floor(i/batchSize) + 1}/${Math.ceil(branches.length/batchSize)}`);
      
      const batchPromises = batch.map(async (branch, batchIndex) => {
        const branchPrompt = `${this.drdSystemPrompt}

研究分支任务：
分支ID：${branch.branch_id}
研究重点：${branch.focus}
研究目标：${branch.objectives?.join(', ')}
研究方法：${branch.methodology}

原始用户需求：${JSON.stringify(planningResult.user_needs_analysis)}

请执行深度研究并返回结构化结果：
{
  "branch_id": "${branch.branch_id}",
  "findings": "关键发现",
  "data_points": ["重要数据点"],
  "insights": ["深度洞察"],
  "limitations": ["研究局限性"],
  "confidence_level": 0.8,
  "next_steps_suggestions": ["后续建议"]
}`;

        try {
          console.log(`🔍 执行研究分支: ${branch.focus}`);
          const response = await this.helix.callGeminiAPI(branchPrompt, 0.5);
          const result = this.parseGeminiResponse(response);
          result.execution_time = Date.now();
          return result;
        } catch (error) {
          console.warn(`⚠️ 研究分支 ${branch.branch_id} 执行失败:`, error.message);
          return {
            branch_id: branch.branch_id,
            findings: `研究分支执行失败: ${error.message}`,
            confidence_level: 0,
            error: true
          };
        }
      });

      const batchResults = await Promise.allSettled(batchPromises);
      
      // 处理批次结果
      batchResults.forEach((result, batchIndex) => {
        if (result.status === 'fulfilled') {
          researchResults.push(result.value);
        } else {
          const globalIndex = i + batchIndex;
          console.error(`❌ 研究分支 ${globalIndex + 1} 失败:`, result.reason);
          researchResults.push({
            branch_id: `research_${globalIndex + 1}`,
            findings: '研究分支执行失败',
            confidence_level: 0,
            error: true
          });
        }
      });
    }

    // 存储研究结果
    await this.memory.setContext(projectId, 'drd_research_results', researchResults);
    
    console.log(`📊 完成${researchResults.length}个研究分支`);
    
    return researchResults;
  }

  /**
   * 阶段3：综合评估与决策
   */
  async phase3_synthesizeEvaluateAndDecide(projectId, researchResults, forceComplete = false) {
    console.log('🧠 阶段3：综合评估与决策');
    
    const synthesisPrompt = `${this.drdSystemPrompt}

综合评估任务：
强制完成：${forceComplete}

研究结果汇总：
${JSON.stringify(researchResults, null, 2)}

请综合分析所有研究结果并做出决策：
1. 信息是否足够完整？
2. 是否还有关键缺口需要研究？
3. 能否进入实施阶段？

返回JSON格式：
{
  "synthesis": "综合分析总结",
  "information_completeness": 0.8,
  "critical_gaps": ["关键缺口"],
  "decision": "continue_research|proceed_to_implementation|clarify_with_user",
  "reasoning": "决策理由",
  "recommended_workflow": "如果进入实施，推荐的工作流",
  "updated_plan": "如果继续研究，更新的计划",
  "clarification_needed": "如果需要澄清，具体问题"
}`;

    const response = await this.helix.callGeminiAPI(synthesisPrompt, 0.3);
    const evaluationResult = this.parseGeminiResponse(response);
    
    // 存储决策结果
    await this.memory.setContext(projectId, 'drd_evaluation', evaluationResult);
    
    console.log(`💡 决策: ${evaluationResult.decision}`);
    console.log(`📈 信息完整度: ${(evaluationResult.information_completeness * 100).toFixed(1)}%`);
    
    return evaluationResult;
  }

  /**
   * 阶段4：质量保证与交付
   */
  async phase4_qualityAssuranceAndDelivery(projectId, evaluationResult) {
    console.log('🚀 阶段4：质量保证与交付');
    
    // 如果评估结果建议进入实施阶段
    if (evaluationResult.recommended_workflow) {
      console.log(`🔄 委派给标准工作流: ${evaluationResult.recommended_workflow}`);
      
      // 构造增强的用户请求，包含研究发现
      const enhancedRequest = {
        ...this.originalRequest,
        drd_research_summary: evaluationResult.synthesis,
        drd_insights: evaluationResult,
        enhanced_by_drd: true
      };
      
      // 委派给HELIX的标准工作流
      return await this.helix.executeWorkflowByType(projectId, evaluationResult.recommended_workflow, enhancedRequest);
    }
    
    // 否则返回研究报告
    return {
      type: 'DRD_RESEARCH_COMPLETED',
      projectId,
      research_summary: evaluationResult.synthesis,
      evaluation: evaluationResult,
      message: '🔬 DRD深度研究已完成',
      next_actions: ['基于研究结果制定具体实施方案', '与相关专家进一步讨论技术细节']
    };
  }

  /**
   * 处理澄清请求
   */
  handleClarificationRequest(projectId, result) {
    return {
      type: 'USER_CLARIFICATION_NEEDED',
      projectId,
      message: '需要您的进一步澄清',
      questions: result.clarification_questions || result.clarification_needed,
      context: result
    };
  }

  /**
   * 回退到简单工作流
   */
  async fallbackToSimpleWorkflow(projectId, userRequest, classification) {
    console.log('🔄 DRD失败，回退到简单工作流');
    
    // 选择最合适的简单工作流
    const fallbackWorkflow = classification.workflow === 'general_research' ? 
      'creative_only' : classification.workflow;
    
    return await this.helix.executeWorkflowByType(projectId, fallbackWorkflow, userRequest);
  }

  /**
   * 解析Gemini API响应
   */
  parseGeminiResponse(response) {
    try {
      // 清理markdown代码块
      let cleanResponse = response;
      if (typeof cleanResponse === 'string') {
        cleanResponse = cleanResponse.replace(/^```json\s*/, '').replace(/\s*```.*$/, '');
        cleanResponse = cleanResponse.replace(/^```\s*/, '').replace(/\s*```.*$/, '');
        const jsonMatch = cleanResponse.match(/^\s*\{[\s\S]*\}\s*$/);
        if (jsonMatch) {
          cleanResponse = jsonMatch[0].trim();
        }
      }
      
      return JSON.parse(cleanResponse);
    } catch (error) {
      console.warn('⚠️ DRD响应解析失败，使用备用逻辑');
      return {
        findings: response,
        confidence_level: 0.5,
        decision: 'proceed_to_implementation',
        recommended_workflow: 'general_research'
      };
    }
  }
}

module.exports = { DRDOrchestrator };