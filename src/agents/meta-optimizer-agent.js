/**
 * Meta-Agent / 系统优化师 (Prometheus) - META_OPTIMIZER_AGENT_V1.0
 * 
 * HELIX系统的"免疫系统"和"进化引擎"
 * 分析失败案例，诊断根本原因，并提出可验证的优化方案
 */

const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

class MetaOptimizerAgent {
  constructor(options = {}) {
    this.memory = options.memory;
    this.orchestrator = options.orchestrator;
    this.agentId = 'meta-optimizer-agent';
    this.version = 'V1.0';
    this.codename = 'Prometheus';
    
    // Agent身份和配置
    this.identity = 'META_OPTIMIZER_AGENT_V1.0';
    this.activationMode = 'ASYNCHRONOUS_ANALYSIS';
    
    // 配置参数
    this.config = {
      failureAnalysisThreshold: options.failureAnalysisThreshold || 3, // 触发分析的失败次数
      analysisInterval: options.analysisInterval || 300000, // 5分钟分析间隔
      maxRetries: options.maxRetries || 2,
      confidenceThreshold: options.confidenceThreshold || 0.8
    };
    
    // 失败模式检测
    this.failurePatterns = new Map(); // 存储失败模式统计
    this.lastAnalysisTime = 0;
    
    // 提示词版本管理
    this.promptVersions = new Map();
    
    console.log(`🔬 Meta-Agent / 系统优化师已初始化 (${this.version} - ${this.codename})`);
  }

  /**
   * 主要处理入口 - 异步分析失败模式
   */
  async processFailureAnalysis() {
    console.log(`🔬 ${this.codename} 开始系统分析...`);
    
    try {
      // 收集失败数据
      const failureData = await this.collectFailureData();
      
      if (failureData.length === 0) {
        console.log(`📊 ${this.codename}: 未发现失败案例，系统运行良好`);
        return { type: 'NO_FAILURES_DETECTED', message: '系统运行正常' };
      }
      
      // 检测失败模式
      const patterns = await this.detectFailurePatterns(failureData);
      
      // 执行根本原因分析
      const analysisResults = [];
      for (const pattern of patterns) {
        if (pattern.frequency >= this.config.failureAnalysisThreshold) {
          console.log(`🧐 分析失败模式: ${pattern.type} (发生${pattern.frequency}次)`);
          const analysis = await this.performRootCauseAnalysis(pattern);
          analysisResults.push(analysis);
        }
      }
      
      if (analysisResults.length === 0) {
        console.log(`📊 ${this.codename}: 失败频率未达到分析阈值`);
        return { type: 'INSUFFICIENT_FAILURE_DATA', message: '失败频率低，暂不需要优化' };
      }
      
      // 生成优化建议
      const optimizations = [];
      for (const analysis of analysisResults) {
        const optimization = await this.generateOptimization(analysis);
        if (optimization) {
          optimizations.push(optimization);
        }
      }
      
      // 存储分析结果
      await this.storeAnalysisResults({
        timestamp: new Date().toISOString(),
        failureCount: failureData.length,
        patternsDetected: patterns.length,
        optimizationsProposed: optimizations.length,
        results: optimizations
      });
      
      console.log(`✅ ${this.codename} 完成分析: 发现${patterns.length}个模式，提出${optimizations.length}个优化建议`);
      
      return {
        type: 'ANALYSIS_COMPLETED',
        patterns: patterns.length,
        optimizations: optimizations.length,
        results: optimizations,
        message: `🔬 系统分析完成，发现${optimizations.length}个优化机会`
      };
      
    } catch (error) {
      console.error(`❌ ${this.codename} 分析失败:`, error);
      return {
        type: 'ANALYSIS_ERROR',
        error: error.message,
        message: '系统分析遇到错误'
      };
    }
  }

  /**
   * 收集失败数据
   */
  async collectFailureData() {
    const failureEvents = [];
    
    try {
      // 扫描SimpleMemory中的失败日志
      const failureLogs = await this.memory.scanFailureLogs();
      
      for (const log of failureLogs) {
        if (!log.processed) {
          failureEvents.push({
            id: log.id,
            timestamp: log.timestamp,
            agentId: log.agentId,
            errorType: log.errorType,
            errorMessage: log.errorMessage,
            context: log.context,
            userRequest: log.userRequest
          });
          
          // 标记为已处理
          await this.memory.markFailureLogProcessed(log.id);
        }
      }
      
    } catch (error) {
      console.error('收集失败数据时出错:', error);
    }
    
    return failureEvents;
  }

  /**
   * 检测失败模式
   */
  async detectFailurePatterns(failureData) {
    const patterns = new Map();
    
    for (const failure of failureData) {
      const patternKey = `${failure.agentId}_${failure.errorType}`;
      
      if (!patterns.has(patternKey)) {
        patterns.set(patternKey, {
          type: patternKey,
          agentId: failure.agentId,
          errorType: failure.errorType,
          frequency: 0,
          instances: [],
          firstSeen: failure.timestamp,
          lastSeen: failure.timestamp
        });
      }
      
      const pattern = patterns.get(patternKey);
      pattern.frequency++;
      pattern.instances.push(failure);
      pattern.lastSeen = failure.timestamp;
    }
    
    return Array.from(patterns.values()).sort((a, b) => b.frequency - a.frequency);
  }

  /**
   * 执行根本原因分析 (5 Whys Protocol)
   */
  async performRootCauseAnalysis(pattern) {
    console.log(`🔍 执行根本原因分析: ${pattern.type}`);
    
    try {
      // 获取代表性的失败实例
      const sampleFailure = pattern.instances[0];
      
      // 构建分析提示词
      const analysisPrompt = `你是HELIX系统的Meta-Agent，正在分析一个重复出现的失败模式。

失败模式信息：
- Agent: ${pattern.agentId}
- 错误类型: ${pattern.errorType}
- 发生频率: ${pattern.frequency}次
- 错误信息: ${sampleFailure.errorMessage}
- 用户请求示例: ${sampleFailure.userRequest}

请使用"5个为什么"方法进行根本原因分析：

1. 第一层：为什么会出现${pattern.errorType}？
2. 第二层：为什么Agent ${pattern.agentId}会产生这种错误？
3. 第三层：为什么当前的提示词或流程无法避免这种错误？
4. 第四层：为什么系统设计中缺乏相应的预防机制？
5. 第五层：根本原因是什么？

请以JSON格式输出分析结果：
{
  "symptom": "直接症状描述",
  "rootCause": "根本原因",
  "analysisChain": ["第一层原因", "第二层原因", "第三层原因", "第四层原因", "第五层原因"],
  "confidence": 0.8,
  "recommendation": "具体的修复建议"
}`;

      const analysisResponse = await this.orchestrator.callGeminiAPI(analysisPrompt, 0.3);
      
      // 解析AI响应
      let analysis;
      try {
        analysis = JSON.parse(this.extractJSON(analysisResponse));
      } catch (parseError) {
        console.warn('AI分析响应解析失败，使用回退逻辑');
        analysis = this.createFallbackAnalysis(pattern);
      }
      
      return {
        pattern,
        analysis,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      console.error('根本原因分析失败:', error);
      return {
        pattern,
        analysis: this.createFallbackAnalysis(pattern),
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * 生成优化方案
   */
  async generateOptimization(analysisResult) {
    console.log(`💡 生成优化方案: ${analysisResult.pattern.type}`);
    
    try {
      const optimizationPrompt = `基于以下根本原因分析，请设计一个具体的优化方案：

根本原因: ${analysisResult.analysis.rootCause}
Agent: ${analysisResult.pattern.agentId}
建议: ${analysisResult.analysis.recommendation}

请设计一个优化方案，重点是修改Agent的提示词以预防此类错误。

输出JSON格式：
{
  "hypothesis": "优化假设描述",
  "targetAgent": "${analysisResult.pattern.agentId}",
  "optimizationType": "PROMPT_MODIFICATION",
  "promptChanges": {
    "additions": ["需要添加的指令"],
    "modifications": ["需要修改的部分"],
    "validationSteps": ["验证步骤"]
  },
  "expectedImprovement": "预期改进效果",
  "riskAssessment": "风险评估"
}`;

      const optimizationResponse = await this.orchestrator.callGeminiAPI(optimizationPrompt, 0.3);
      
      let optimization;
      try {
        optimization = JSON.parse(this.extractJSON(optimizationResponse));
      } catch (parseError) {
        console.warn('优化方案响应解析失败，使用回退逻辑');
        optimization = this.createFallbackOptimization(analysisResult);
      }
      
      // 验证优化方案
      const validationResult = await this.validateOptimization(optimization, analysisResult);
      
      return {
        id: this.generateOptimizationId(),
        analysisResult,
        optimization,
        validation: validationResult,
        status: validationResult.passed ? 'VALIDATED' : 'NEEDS_REVIEW',
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      console.error('生成优化方案失败:', error);
      return null;
    }
  }

  /**
   * 验证优化方案 (简化的沙箱测试)
   */
  async validateOptimization(optimization, analysisResult) {
    console.log(`🧪 验证优化方案: ${optimization.targetAgent}`);
    
    try {
      // 检查是否有足够的历史数据进行验证
      const historicalData = analysisResult.pattern.instances.slice(0, 3);
      
      if (historicalData.length === 0) {
        return {
          passed: false,
          reason: '缺乏历史数据进行验证',
          confidence: 0.0
        };
      }
      
      // 使用简化的验证逻辑
      const validationResults = [];
      
      for (const instance of historicalData) {
        const testResult = await this.runSimplifiedSandboxTest(
          optimization.targetAgent,
          optimization.promptChanges,
          instance
        );
        validationResults.push(testResult);
      }
      
      const passRate = validationResults.filter(r => r.passed).length / validationResults.length;
      
      return {
        passed: passRate >= 0.7, // 70%成功率阈值
        passRate,
        confidence: Math.min(passRate + 0.1, 1.0),
        details: validationResults,
        reason: `验证通过率: ${(passRate * 100).toFixed(1)}%`
      };
      
    } catch (error) {
      console.error('优化验证失败:', error);
      return {
        passed: false,
        reason: `验证过程出错: ${error.message}`,
        confidence: 0.0
      };
    }
  }

  /**
   * 简化的沙箱测试
   */
  async runSimplifiedSandboxTest(targetAgent, promptChanges, testInstance) {
    try {
      // 构建验证提示词
      const validationPrompt = `请验证以下优化是否能解决问题：

原始错误: ${testInstance.errorMessage}
用户请求: ${testInstance.userRequest}

建议的提示词改进:
- 添加指令: ${promptChanges.additions ? promptChanges.additions.join(', ') : '无'}
- 修改部分: ${promptChanges.modifications ? promptChanges.modifications.join(', ') : '无'}

请判断这些改进是否能有效预防原始错误的发生。

回答 "YES" 或 "NO"，并简要说明理由。`;

      const response = await this.orchestrator.callGeminiAPI(validationPrompt, 0.2);
      
      const passed = response.toLowerCase().includes('yes');
      
      return {
        passed,
        response: response.substring(0, 200),
        testInstance: testInstance.id
      };
      
    } catch (error) {
      return {
        passed: false,
        response: `测试失败: ${error.message}`,
        testInstance: testInstance.id
      };
    }
  }

  /**
   * 存储分析结果
   */
  async storeAnalysisResults(results) {
    const analysisId = `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    await this.memory.setContext(analysisId, 'meta_analysis_results', results);
    
    // 更新最后分析时间
    this.lastAnalysisTime = Date.now();
  }

  /**
   * 检查是否需要触发分析
   */
  shouldTriggerAnalysis() {
    const now = Date.now();
    const timeSinceLastAnalysis = now - this.lastAnalysisTime;
    
    return timeSinceLastAnalysis >= this.config.analysisInterval;
  }

  /**
   * 记录失败事件 (供其他Agent调用)
   */
  async recordFailureEvent(agentId, errorType, errorMessage, context, userRequest) {
    const failureEvent = {
      id: `failure_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      agentId,
      errorType,
      errorMessage,
      context,
      userRequest,
      processed: false
    };
    
    await this.memory.recordFailureEvent(failureEvent);
    
    // 检查是否需要立即触发分析
    if (this.shouldTriggerAnalysis()) {
      // 异步执行分析，不阻塞当前流程
      setImmediate(() => {
        this.processFailureAnalysis().catch(error => {
          console.error('异步分析失败:', error);
        });
      });
    }
  }

  // 辅助方法
  extractJSON(text) {
    const jsonMatch = text.match(/```json\s*([\s\S]*?)\s*```/) || text.match(/{\s*[\s\S]*\s*}/);
    return jsonMatch ? jsonMatch[1] || jsonMatch[0] : text;
  }

  createFallbackAnalysis(pattern) {
    return {
      symptom: `Agent ${pattern.agentId} 重复出现 ${pattern.errorType} 错误`,
      rootCause: `${pattern.agentId} 的提示词或处理逻辑存在缺陷`,
      analysisChain: [
        `出现 ${pattern.errorType} 错误`,
        `Agent处理逻辑不完善`,
        `提示词缺乏相应的约束或指导`,
        `系统缺乏预防机制`,
        `需要改进Agent的提示词和错误处理`
      ],
      confidence: 0.6,
      recommendation: `改进 ${pattern.agentId} 的提示词，增加错误预防指令`
    };
  }

  createFallbackOptimization(analysisResult) {
    return {
      hypothesis: `通过改进 ${analysisResult.pattern.agentId} 的提示词可以减少 ${analysisResult.pattern.errorType} 错误`,
      targetAgent: analysisResult.pattern.agentId,
      optimizationType: 'PROMPT_MODIFICATION',
      promptChanges: {
        additions: [`添加 ${analysisResult.pattern.errorType} 错误的预防检查`],
        modifications: ['增强输出格式验证'],
        validationSteps: ['输出前自检', '格式验证', '错误预防']
      },
      expectedImprovement: `预期减少50%的 ${analysisResult.pattern.errorType} 错误`,
      riskAssessment: '低风险，仅修改提示词'
    };
  }

  generateOptimizationId() {
    return `opt_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
  }

  /**
   * 获取系统健康状态
   */
  async getSystemHealth() {
    const recentFailures = await this.collectFailureData();
    const patterns = await this.detectFailurePatterns(recentFailures);
    
    return {
      totalFailures: recentFailures.length,
      uniquePatterns: patterns.length,
      criticalPatterns: patterns.filter(p => p.frequency >= this.config.failureAnalysisThreshold).length,
      lastAnalysis: this.lastAnalysisTime ? new Date(this.lastAnalysisTime).toISOString() : null,
      systemStatus: recentFailures.length > 10 ? 'NEEDS_ATTENTION' : 'HEALTHY'
    };
  }
}

module.exports = { MetaOptimizerAgent };