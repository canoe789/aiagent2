# HELIX 前端MVP快速启动指南

## 🎯 核心特性

✅ **极简MVP**: 单文件前端，零构建步骤  
✅ **完整流程**: 输入 → AI处理 → HTML输出  
✅ **实时状态**: 轮询显示处理进度  
✅ **一体化部署**: FastAPI同时服务前后端  

## 🚀 快速启动

### 1. 启动系统
```bash
cd /home/canoezhang/Projects/aiagent

# 方法1: 完整系统启动（推荐）
python start_system.py

# 方法2: 仅启动API（测试用）
python -m src.api.main
```

### 2. 访问前端
```
浏览器打开: http://localhost:8000
```

### 3. 测试接口连接
```bash
# 运行集成测试
python test_frontend_integration.py
```

## 📡 API接口说明

### 核心接口
```
POST   /api/v1/jobs              - 创建任务
GET    /api/v1/jobs/{job_id}     - 查询任务状态  
GET    /api/v1/jobs/{job_id}/result - 获取HTML结果
GET    /api/v1/jobs/{job_id}/artifacts - 获取所有构件
```

### 状态流转
```
PENDING → IN_PROGRESS → COMPLETED
                    ↘   FAILED
```

## 🔧 接口连接关键点

### 1. 任务创建
```javascript
// 前端请求格式
{
    "chat_input": "用户输入的创意需求",
    "session_id": "session_12345"
}

// 后端响应格式  
{
    "job_id": 123,
    "status": "PENDING", 
    "message": "Job created successfully"
}
```

### 2. 状态轮询
```javascript
// 每3秒查询一次状态
setInterval(async () => {
    const response = await fetch(`/api/v1/jobs/${jobId}`);
    const job = await response.json();
    
    // 状态判断
    switch (job.status) {
        case 'PENDING': // 排队中
        case 'IN_PROGRESS': // 处理中
        case 'COMPLETED': // 完成 → 获取结果
        case 'FAILED': // 失败 → 显示错误
    }
}, 3000);
```

### 3. HTML结果获取
```javascript
// 获取最终HTML演示文稿
const response = await fetch(`/api/v1/jobs/${jobId}/result`);
const html = await response.text();

// 直接注入DOM（注意XSS风险）
document.getElementById('container').innerHTML = html;
```

## 🗂️ 文件结构
```
aiagent/
├── frontend/
│   └── index.html              # 完整前端（一个文件）
├── src/api/
│   ├── main.py                 # FastAPI主程序 + 静态文件服务
│   ├── jobs.py                 # 任务管理API
│   └── artifacts.py            # 构件获取API（新增）
├── start_system.py             # 系统启动脚本
└── test_frontend_integration.py # 接口测试脚本
```

## 🛠️ 关键设计决策

### 轮询 vs WebSocket
- **选择**: 轮询（3秒间隔）
- **理由**: MVP简化实现，减少复杂性
- **优化**: 指数退避，避免服务器过载

### HTML存储方案
- **存储**: PostgreSQL artifacts表
- **转换**: PresentationBlueprint → HTML  
- **服务**: 通过API直接返回HTML内容

### 错误处理
- **网络错误**: try-catch + 用户友好提示
- **API错误**: HTTP状态码 + 详细错误信息  
- **处理失败**: FAILED状态 + error_message

## 🔒 安全考虑

### XSS防护
```javascript
// 当前方案（MVP可接受）
container.innerHTML = trustedAIGeneratedHTML;

// 生产环境建议
// 1. 使用iframe沙箱
// 2. HTML内容过滤 
// 3. CSP策略
```

### 输入验证
```python
# 后端验证
class JobCreate(BaseModel):
    chat_input: str = Field(..., min_length=10, max_length=2000)
    session_id: Optional[str] = None
```

## 📊 性能优化

### 前端优化
- 请求缓存：避免重复状态查询
- 懒加载：结果生成后再获取HTML
- 压缩：启用gzip压缩

### 后端优化  
- 连接池：数据库连接复用
- 异步处理：非阻塞任务创建
- 缓存：频繁查询结果缓存

## 🚨 故障排查

### 常见问题

1. **前端访问404**
   ```bash
   # 检查静态文件路径
   ls frontend/index.html
   
   # 重启服务
   python start_system.py
   ```

2. **API连接失败**
   ```bash
   # 测试API健康状态
   curl http://localhost:8000/api/v1/health
   
   # 检查端口占用
   lsof -i :8000
   ```

3. **任务状态一直PENDING**
   ```bash
   # 检查Orchestrator是否启动
   ps aux | grep orchestrator
   
   # 查看数据库连接
   docker ps | grep postgres
   ```

4. **HTML结果404**
   ```bash
   # 检查artifacts表
   SELECT * FROM artifacts WHERE task_id IN (
       SELECT id FROM tasks WHERE job_id = YOUR_JOB_ID
   );
   ```

## 🔄 开发工作流

### 快速迭代
```bash
# 1. 修改前端
vim frontend/index.html

# 2. 重启服务（自动重载）
# 无需重启，刷新浏览器即可

# 3. 修改后端API
vim src/api/artifacts.py

# 4. 重启服务
Ctrl+C
python start_system.py
```

### 调试模式
```javascript
// 前端调试
const DEBUG = true;  // 启用控制台日志

// 查看网络请求
// F12 → Network → 查看API调用详情
```

## 📈 后续扩展

### MVP → 生产
1. **WebSocket**: 实时状态更新
2. **用户认证**: JWT + 权限控制  
3. **对象存储**: S3存储大文件
4. **监控告警**: 性能指标监控
5. **负载均衡**: 多实例部署

### 功能增强
1. **任务管理**: 历史记录、收藏夹
2. **实时协作**: 多用户编辑
3. **模板系统**: 预设创意模板
4. **导出功能**: PDF、PPT格式
5. **AI优化**: 用户反馈学习

---

**🎉 恭喜！你已经拥有一个完整的AI创意生产系统MVP！**