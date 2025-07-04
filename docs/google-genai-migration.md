# Google Genai客户端迁移指南

## 迁移概述

HELIX系统已成功从axios直接HTTP调用迁移到Google官方的`@google/genai`客户端库，提升了API调用的稳定性和开发体验。

## 主要变更

### 1. 依赖更新

**新增依赖:**
```json
{
  "@google/genai": "^1.8.0"
}
```

**API密钥格式更新:**
```bash
# 旧格式（已废弃）
GEMINI_API_KEY=sk-431f94e5a010435b9c7ca45e5e429d99

# 新格式
GEMINI_API_KEY=AIzaSyDhRl1VoOcm_FFr506sfvEhBbdilZb-Wp0
```

### 2. 代码变更

**客户端初始化:**
```javascript
// 旧方式（axios）
this.apiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

// 新方式（@google/genai）
const { GoogleGenAI } = require('@google/genai');
this.geminiClient = new GoogleGenAI({ apiKey: this.apiKey });
```

**API调用方式:**
```javascript
// 旧方式（axios）
const response = await axios.post(`${this.apiUrl}?key=${this.apiKey}`, requestBody);
return response.data.candidates[0].content.parts[0].text;

// 新方式（@google/genai）
const response = await this.geminiClient.models.generateContent({
  model: 'gemini-2.5-flash',
  contents: prompt
});
return response.text;
```

### 3. 错误处理更新

**兼容多种错误格式:**
```javascript
// 支持genai客户端和axios的错误格式
const isRateLimit = (error.response && error.response.status === 429) || 
                   (error.status === 429) || 
                   (error.message && error.message.includes('429')) ||
                   (error.message && error.message.includes('quota'));
```

## 优势和改进

### ✅ 主要优势

1. **官方支持**: 使用Google官方维护的客户端库
2. **更好的类型安全**: 更完善的TypeScript支持
3. **简化的API**: 更直观的调用接口
4. **更好的错误处理**: 官方库提供更详细的错误信息
5. **向前兼容**: 支持Google最新的API特性

### 📊 性能对比

| 指标 | 旧方式（axios） | 新方式（@google/genai） |
|------|----------------|----------------------|
| 响应时间 | ~8秒 | ~8秒 |
| 错误处理 | 基础HTTP状态码 | 丰富的错误类型 |
| 类型安全 | 无 | 内置TypeScript支持 |
| API兼容性 | 手动维护 | 自动更新 |

## 验证测试

### 测试结果
```
✅ 直接Gemini API调用: 成功 (8086ms)
✅ AI任务分类: 成功 (置信度: 95.0%)
✅ 完整系统集成: 正常工作
```

### 运行测试
```bash
# 运行迁移验证测试
node tests/genai-client-test.js

# 运行完整系统测试
node tests/helix-decision-storage-test.js
```

## 配置要求

### 环境变量
```bash
# 必需：Google AI API密钥（新格式）
GEMINI_API_KEY=AIzaSy...

# 可选：DeepSeek回退
DEEPSEEK_API_KEY=sk-9a9...
```

### Node.js要求
- Node.js >= 18.0.0
- 支持ES6模块和async/await

## 兼容性保证

### 向后兼容
- ✅ 所有现有API接口保持不变
- ✅ DeepSeek回退机制继续工作
- ✅ 速率限制和重试逻辑正常
- ✅ 错误处理机制增强但兼容

### 迁移检查清单

- [x] 更新API密钥为新格式
- [x] 安装@google/genai依赖
- [x] 更新客户端初始化代码
- [x] 适配API调用方式
- [x] 更新错误处理逻辑
- [x] 运行完整测试验证
- [x] 更新文档

## 故障排除

### 常见问题

**1. API密钥格式错误**
```
错误: Invalid API key format
解决: 确保使用新格式的API密钥 (AIzaSy...)
```

**2. 客户端初始化失败**
```
错误: Cannot read properties of undefined
解决: 检查@google/genai包安装和导入
```

**3. 响应格式变化**
```
错误: Cannot read property 'text'
解决: 新客户端直接返回response.text，无需解析嵌套结构
```

## 后续计划

### 短期优化
1. 监控新客户端的性能表现
2. 收集用户反馈
3. 优化错误处理逻辑

### 长期规划
1. 探索Google AI的新功能特性
2. 实现更智能的缓存策略
3. 考虑支持流式响应

---

**重要提醒**: 请确保在生产环境中使用新格式的API密钥，旧格式可能随时停止支持。

**迁移完成**: ✅ 系统已成功迁移到Google官方genai客户端，所有核心功能正常工作。