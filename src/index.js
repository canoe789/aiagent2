/**
 * AI Agent Project - Main Entry Point
 * 
 * 简单的Express服务器，集成HELIX Orchestrator和记忆库
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

const { HelixOrchestrator } = require('./orchestrator/helix');
const { SimpleMemory } = require('./memory/simple-memory');
const { HTMLGenerator } = require('./services/HTMLGenerator');

const app = express();
const port = process.env.PORT || 3000;

// 中间件
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));

// 静态文件服务
app.use(express.static('public'));

// 初始化核心组件
const memory = new SimpleMemory();
const orchestrator = new HelixOrchestrator({ memory });
const htmlGenerator = new HTMLGenerator();

// 路由

/**
 * 健康检查
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: memory.getStats()
  });
});

/**
 * 处理用户请求 - 主要API
 */
app.post('/api/process', async (req, res) => {
  try {
    const { message, type = 'general', outputFormat = 'json' } = req.body;
    
    if (!message) {
      return res.status(400).json({
        error: 'Message is required',
        code: 'MISSING_MESSAGE'
      });
    }

    const userRequest = {
      message,
      type,
      timestamp: new Date().toISOString(),
      clientInfo: {
        userAgent: req.headers['user-agent'],
        ip: req.ip
      }
    };

    console.log('Processing request:', userRequest);
    
    const result = await orchestrator.processRequest(userRequest);
    
    // 如果请求HTML格式输出
    if (outputFormat === 'html' && result.type === 'COMPLETED') {
      const projectData = await memory.getProjectData(result.projectId);
      const htmlDocument = htmlGenerator.generateProjectHTML(projectData, result);
      
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      res.send(htmlDocument);
      return;
    }
    
    res.json({
      success: true,
      result,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      code: 'PROCESSING_ERROR',
      message: error.message
    });
  }
});

/**
 * 继续项目（用于用户澄清后继续）
 */
app.post('/api/continue/:projectId', async (req, res) => {
  try {
    const { projectId } = req.params;
    const { response } = req.body;
    
    if (!response) {
      return res.status(400).json({
        error: 'Response is required',
        code: 'MISSING_RESPONSE'
      });
    }

    const result = await orchestrator.continueProject(projectId, response);
    
    res.json({
      success: true,
      result,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Continue API Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      code: 'CONTINUE_ERROR',
      message: error.message
    });
  }
});

/**
 * 获取项目状态
 */
app.get('/api/project/:projectId/status', async (req, res) => {
  try {
    const { projectId } = req.params;
    const status = await orchestrator.getProjectStatus(projectId);
    const projectData = await memory.getProjectData(projectId);
    
    res.json({
      projectId,
      status,
      data: projectData,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Status API Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      code: 'STATUS_ERROR',
      message: error.message
    });
  }
});

/**
 * 导出项目数据
 */
app.get('/api/project/:projectId/export', async (req, res) => {
  try {
    const { projectId } = req.params;
    const { format = 'json' } = req.query;
    
    if (format === 'html') {
      // 导出为HTML文档
      const projectData = await memory.getProjectData(projectId);
      const htmlDocument = htmlGenerator.generateProjectHTML(projectData, projectData);
      
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      res.setHeader('Content-Disposition', `attachment; filename="${projectId}-report.html"`);
      res.send(htmlDocument);
    } else {
      // 导出为JSON
      const exportData = await memory.exportProject(projectId);
      res.json(exportData);
    }

  } catch (error) {
    console.error('Export API Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      code: 'EXPORT_ERROR',
      message: error.message
    });
  }
});

/**
 * 搜索记忆库
 */
app.get('/api/search', async (req, res) => {
  try {
    const { q: query } = req.query;
    
    if (!query) {
      return res.status(400).json({
        error: 'Query parameter q is required',
        code: 'MISSING_QUERY'
      });
    }

    const results = await memory.search(query);
    
    res.json({
      query,
      results,
      count: results.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Search API Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      code: 'SEARCH_ERROR',
      message: error.message
    });
  }
});

/**
 * 系统统计
 */
app.get('/api/stats', async (req, res) => {
  try {
    const stats = memory.getStats();
    
    res.json({
      ...stats,
      server: {
        uptime: process.uptime(),
        version: process.version,
        platform: process.platform
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Stats API Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      code: 'STATS_ERROR',
      message: error.message
    });
  }
});

// 错误处理中间件
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    error: 'Internal server error',
    code: 'UNHANDLED_ERROR'
  });
});

// 404处理
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    code: 'NOT_FOUND',
    path: req.path
  });
});

// 启动服务器
app.listen(port, () => {
  console.log(`🚀 AI Agent Server running on port ${port}`);
  console.log(`🌐 Web UI: http://localhost:${port}`);
  console.log(`📚 Health check: http://localhost:${port}/health`);
  console.log(`🤖 Main API: POST http://localhost:${port}/api/process`);
  
  // 定期清理过期数据
  setInterval(async () => {
    const cleaned = await memory.cleanup();
    if (cleaned > 0) {
      console.log(`🧹 Cleaned ${cleaned} expired entries`);
    }
  }, 60 * 60 * 1000); // 每小时清理一次
});

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('🛑 SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('🛑 SIGINT received, shutting down gracefully');
  process.exit(0);
});