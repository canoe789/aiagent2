/**
 * Simple Memory Manager - 简单的记忆库实现
 * 
 * 基于原有记忆库接口，简化实现，专注核心功能
 */

class SimpleMemory {
  constructor() {
    // 内存存储，生产环境应该用数据库
    this.storage = new Map();
    this.projectData = new Map();
    // 失败日志存储 (用于Meta-Agent)
    this.failureLogs = new Map();
  }

  /**
   * 设置上下文数据
   * @param {string} projectId - 项目ID
   * @param {string} key - 数据键
   * @param {any} value - 数据值
   */
  async setContext(projectId, key, value) {
    const projectKey = `${projectId}_${key}`;
    this.storage.set(projectKey, {
      value,
      timestamp: new Date().toISOString(),
      projectId,
      key
    });
    
    // 记录到项目数据中
    if (!this.projectData.has(projectId)) {
      this.projectData.set(projectId, new Set());
    }
    this.projectData.get(projectId).add(key);
    
    return true;
  }

  /**
   * 获取上下文数据
   * @param {string} projectId - 项目ID
   * @param {string} key - 数据键
   * @returns {any} 数据值
   */
  async getContext(projectId, key) {
    const projectKey = `${projectId}_${key}`;
    const data = this.storage.get(projectKey);
    return data ? data.value : null;
  }

  /**
   * 获取项目的所有数据
   * @param {string} projectId - 项目ID
   * @returns {Object} 项目所有数据
   */
  async getProjectData(projectId) {
    const keys = this.projectData.get(projectId) || new Set();
    const result = {};
    
    for (const key of keys) {
      result[key] = await this.getContext(projectId, key);
    }
    
    return result;
  }

  /**
   * 删除项目数据
   * @param {string} projectId - 项目ID
   */
  async deleteProject(projectId) {
    const keys = this.projectData.get(projectId) || new Set();
    
    for (const key of keys) {
      const projectKey = `${projectId}_${key}`;
      this.storage.delete(projectKey);
    }
    
    this.projectData.delete(projectId);
    return true;
  }

  /**
   * 搜索数据
   * @param {string} query - 搜索查询
   * @returns {Array} 搜索结果
   */
  async search(query) {
    const results = [];
    const lowerQuery = query.toLowerCase();
    
    for (const [key, data] of this.storage.entries()) {
      const valueStr = JSON.stringify(data.value).toLowerCase();
      if (valueStr.includes(lowerQuery)) {
        results.push({
          key,
          projectId: data.projectId,
          dataKey: data.key,
          value: data.value,
          timestamp: data.timestamp
        });
      }
    }
    
    return results;
  }

  /**
   * 获取存储统计
   * @returns {Object} 统计信息
   */
  getStats() {
    return {
      totalEntries: this.storage.size,
      totalProjects: this.projectData.size,
      memoryUsage: process.memoryUsage()
    };
  }

  /**
   * 清理过期数据（超过24小时的数据）
   */
  async cleanup() {
    const now = new Date();
    const expiredKeys = [];
    
    for (const [key, data] of this.storage.entries()) {
      const dataTime = new Date(data.timestamp);
      const hoursDiff = (now - dataTime) / (1000 * 60 * 60);
      
      if (hoursDiff > 24) {
        expiredKeys.push(key);
      }
    }
    
    for (const key of expiredKeys) {
      this.storage.delete(key);
    }
    
    return expiredKeys.length;
  }

  /**
   * 导出项目数据
   * @param {string} projectId - 项目ID
   * @returns {Object} 导出的数据
   */
  async exportProject(projectId) {
    const projectData = await this.getProjectData(projectId);
    return {
      projectId,
      exportedAt: new Date().toISOString(),
      data: projectData
    };
  }

  /**
   * 导入项目数据
   * @param {Object} exportData - 导出的数据
   */
  async importProject(exportData) {
    const { projectId, data } = exportData;
    
    for (const [key, value] of Object.entries(data)) {
      await this.setContext(projectId, key, value);
    }
    
    return projectId;
  }

  /**
   * 记录失败事件 (用于Meta-Agent)
   * @param {Object} failureEvent - 失败事件对象
   */
  async recordFailureEvent(failureEvent) {
    this.failureLogs.set(failureEvent.id, {
      ...failureEvent,
      recordedAt: new Date().toISOString()
    });
    
    console.log(`📝 记录失败事件: ${failureEvent.agentId} - ${failureEvent.errorType}`);
    return true;
  }

  /**
   * 扫描失败日志 (用于Meta-Agent)
   * @returns {Array} 所有失败日志
   */
  async scanFailureLogs() {
    const logs = Array.from(this.failureLogs.values());
    console.log(`🔍 扫描失败日志: 找到 ${logs.length} 条记录`);
    return logs;
  }

  /**
   * 标记失败日志为已处理 (用于Meta-Agent)
   * @param {string} logId - 日志ID
   */
  async markFailureLogProcessed(logId) {
    const log = this.failureLogs.get(logId);
    if (log) {
      log.processed = true;
      log.processedAt = new Date().toISOString();
      this.failureLogs.set(logId, log);
      console.log(`✅ 标记失败日志已处理: ${logId}`);
      return true;
    }
    return false;
  }

  /**
   * 清理已处理的失败日志 (定期维护)
   * @param {number} daysBefore - 清理多少天前的已处理日志
   */
  async cleanupProcessedFailureLogs(daysBefore = 7) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysBefore);
    
    let cleanedCount = 0;
    for (const [id, log] of this.failureLogs.entries()) {
      if (log.processed && new Date(log.processedAt) < cutoffDate) {
        this.failureLogs.delete(id);
        cleanedCount++;
      }
    }
    
    console.log(`🧹 清理已处理的失败日志: ${cleanedCount} 条`);
    return cleanedCount;
  }

  /**
   * 获取失败统计 (用于Meta-Agent健康检查)
   * @returns {Object} 失败统计信息
   */
  getFailureStats() {
    const logs = Array.from(this.failureLogs.values());
    const unprocessed = logs.filter(log => !log.processed);
    const processed = logs.filter(log => log.processed);
    
    // 按Agent分组统计
    const byAgent = {};
    logs.forEach(log => {
      if (!byAgent[log.agentId]) {
        byAgent[log.agentId] = { total: 0, unprocessed: 0 };
      }
      byAgent[log.agentId].total++;
      if (!log.processed) {
        byAgent[log.agentId].unprocessed++;
      }
    });
    
    return {
      total: logs.length,
      unprocessed: unprocessed.length,
      processed: processed.length,
      byAgent,
      lastFailure: logs.length > 0 ? logs[logs.length - 1].timestamp : null
    };
  }
}

module.exports = { SimpleMemory };