# AI Model Configuration Guide

**版本:** 1.0  
**更新:** 2025-07-09  
**状态:** 系统配置指南

---

## 1. 当前AI模型配置

### 1.1 默认配置

HELIX系统已配置为使用**Google Gemini 2.5 Flash**作为默认AI模型：

```bash
# 环境变量配置
DEFAULT_AI_PROVIDER=gemini
DEFAULT_AI_MODEL=gemini-2.5-flash
```

### 1.2 模型特性

**Gemini 2.5 Flash优势：**
- 🚀 **高速响应**: 针对快速推理优化
- 🎯 **多模态支持**: 支持文本、图像、代码等多种输入格式
- 💡 **智能理解**: 具备强大的上下文理解能力
- 🔧 **结构化输出**: 特别适合生成JSON格式的结构化响应

## 2. 配置文件位置

### 2.1 环境配置

```bash
# 主配置文件
/home/canoezhang/Projects/aiagent/.env

# 模板文件
/home/canoezhang/Projects/aiagent/.env.example
```

### 2.2 代码配置

```bash
# AI客户端工厂
/home/canoezhang/Projects/aiagent/src/ai_clients/client_factory.py

# Gemini客户端实现
/home/canoezhang/Projects/aiagent/src/ai_clients/gemini_client.py
```

## 3. 使用示例

### 3.1 在Agent中使用

```python
# 标准Agent实现
from ai_clients.client_factory import AIClientFactory

class YourAgent(BaseAgent):
    async def _generate_with_ai(self, artifacts, system_prompt):
        # 自动使用配置的Gemini 2.5 Flash
        ai_client = AIClientFactory.create_client()
        
        response = await ai_client.generate_response(
            system_prompt=system_prompt,
            user_input=self._prepare_input_materials(artifacts),
            temperature=0.7,
            max_tokens=3000
        )
        
        return self._parse_ai_response(response["content"], response)
```

### 3.2 显式指定模型

```python
# 显式指定Gemini 2.5 Flash
ai_client = AIClientFactory.create_client(
    provider="gemini",
    model="gemini-2.5-flash"
)
```

## 4. 配置验证

### 4.1 运行配置测试

```bash
# 验证配置是否正确
source venv/bin/activate
python test_gemini_config.py
```

### 4.2 预期输出

```
🎉 SUCCESS: System is correctly configured to use Gemini 2.5 Flash!
   - Default provider: gemini
   - Default model: gemini-2.5-flash
   - All components aligned
```

## 5. 支持的AI提供商

### 5.1 可用提供商

| 提供商 | 默认模型 | 描述 |
|--------|----------|------|
| **gemini** | gemini-2.5-flash | Google Gemini 2.5 Flash - 快速高效的多模态AI模型 |
| deepseek | deepseek-chat | DeepSeek AI - 具有强推理能力的对话AI |

### 5.2 提供商配置

```bash
# Gemini配置
GEMINI_API_KEY=your_gemini_api_key_here

# DeepSeek配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## 6. 故障排查

### 6.1 常见问题

**问题1: 模型响应慢**
- 解决方案: Gemini 2.5 Flash已优化为高速响应
- 检查网络连接和API配额

**问题2: API密钥错误**
- 解决方案: 检查`.env`文件中的`GEMINI_API_KEY`配置
- 确保API密钥有效且有足够配额

**问题3: 模型不存在**
- 解决方案: 确认模型名称为`gemini-2.5-flash`
- 检查Google AI API是否支持该模型

### 6.2 调试工具

```bash
# 检查环境变量
echo $DEFAULT_AI_PROVIDER
echo $DEFAULT_AI_MODEL

# 测试API连接
python -c "
import asyncio
from src.ai_clients.client_factory import AIClientFactory
from dotenv import load_dotenv
load_dotenv()

async def test():
    client = AIClientFactory.create_client()
    print(f'Provider: {client.__class__.__name__}')
    print(f'Model: {client.model_name}')
    
    # 测试API调用
    response = await client.generate_response(
        system_prompt='You are a helpful assistant.',
        user_input='Hello, please respond with \"Configuration working!\"',
        temperature=0.1,
        max_tokens=50
    )
    print(f'Response: {response[\"content\"]}')

asyncio.run(test())
"
```

## 7. 性能优化建议

### 7.1 提示词优化

```python
# 针对Gemini 2.5 Flash优化的提示词模式
enhanced_prompt = f"""{system_prompt}

CRITICAL: You must respond with VALID JSON only. Do not include any text before or after the JSON.
The JSON must follow this exact structure:

{schema_template}

Remember: Follow your internal thinking process, but output ONLY the final JSON result."""
```

### 7.2 参数调优

```python
# 推荐的Gemini 2.5 Flash参数
response = await ai_client.generate_response(
    system_prompt=enhanced_prompt,
    user_input=input_materials,
    temperature=0.7,        # 平衡创造性和准确性
    max_tokens=3000,        # 足够的输出长度
    top_p=0.95,            # 适当的核采样
    top_k=64               # 合适的top-k采样
)
```

## 8. 监控和日志

### 8.1 日志格式

```python
# 标准日志记录
logger.info("AI client created successfully", 
           provider="gemini", 
           model="gemini-2.5-flash")

logger.info("Gemini response received successfully",
           content_length=len(content),
           tokens_used=usage["total_tokens"])
```

### 8.2 监控指标

- **响应时间**: 通常 < 2秒
- **Token使用量**: 根据输入复杂度自动调整
- **成功率**: 目标 > 95%
- **错误率**: 主要监控API限流和认证错误

---

## 📝 总结

HELIX系统现已完全配置为使用Google Gemini 2.5 Flash模型，提供快速、高效的AI响应。所有Agent将自动使用这个配置，无需额外代码修改。

**关键配置点:**
1. ✅ 默认提供商: gemini
2. ✅ 默认模型: gemini-2.5-flash  
3. ✅ 所有Agent自动使用
4. ✅ 支持结构化JSON输出
5. ✅ 优化的提示词模式

如需更改AI模型，只需修改`.env`文件中的相应配置即可。