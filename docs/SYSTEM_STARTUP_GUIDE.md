# 🚀 HELIX系统启动指南与端口管理规范

## 📋 问题诊断与解决方案

### 根本问题分析
1. **"Failed to fetch"错误原因**：
   - 前端使用 `window.location.origin` 动态获取API地址
   - 当通过某些方式访问时，可能获取到错误的origin
   - 浏览器的CORS策略阻止跨域请求

2. **系统复杂性问题**：
   - 主系统依赖数据库，启动失败
   - 简化版本API可以运行，但前后端通信有问题
   - 端口配置混乱（8000 vs 8001）

## ✅ 解决方案：统一端口规范

### 端口分配标准
```
8000 - 主系统API（需要完整环境）
8001 - 简化API（用于开发测试）
8080 - 调试工具和文档服务
```

### 标准启动流程

#### 方案A：简化API模式（推荐用于快速测试）
```bash
# 1. 进入项目目录
cd /home/canoezhang/Projects/aiagent

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 启动简化API服务器
python simple_api.py

# 4. 访问系统
浏览器打开: http://localhost:8001
```

#### 方案B：完整系统模式（需要数据库）
```bash
# 1. 确保PostgreSQL运行
docker ps | grep postgres

# 2. 启动完整系统
source venv/bin/activate
python start_system.py

# 3. 访问系统
浏览器打开: http://localhost:8000
```

## 🔧 故障排查步骤

### 1. 验证服务器状态
```bash
# 检查端口监听
netstat -tln | grep -E "(8000|8001)"

# 检查进程
ps aux | grep -E "(simple_api|uvicorn)"

# 测试API健康状态
curl http://localhost:8001/api/v1/health
```

### 2. 浏览器调试
1. 打开浏览器控制台（F12）
2. 检查Console标签页的错误信息
3. 检查Network标签页的失败请求
4. 查看具体的错误类型：
   - `net::ERR_CONNECTION_REFUSED` - 服务器未运行
   - `CORS error` - 跨域问题
   - `Failed to fetch` - 网络连接问题

### 3. 使用调试工具
```bash
# 在浏览器中打开调试页面
http://localhost:8001/debug_frontend.html
```

## 🛡️ 防火墙和安全设置

### Linux防火墙检查
```bash
# 检查防火墙状态
sudo ufw status

# 如需要，临时允许端口
sudo ufw allow 8001/tcp
```

### 浏览器安全设置
- 确保浏览器允许localhost连接
- 禁用可能干扰的浏览器扩展
- 尝试使用隐私/无痕模式

## 📝 最佳实践建议

### 1. 开发环境配置
```javascript
// frontend/index.html - 开发环境硬编码API地址
const API_BASE = 'http://localhost:8001';
```

### 2. 生产环境配置
```javascript
// 使用环境变量或配置文件
const API_BASE = process.env.REACT_APP_API_URL || window.location.origin;
```

### 3. CORS配置规范
```python
# 开发环境 - 宽松配置
allow_origins=["*"]

# 生产环境 - 严格配置
allow_origins=["https://your-domain.com"]
```

## 🚨 常见错误及解决

### 错误1：Failed to fetch
**原因**：前端无法连接到后端API
**解决**：
1. 确认API服务器运行在正确端口
2. 修改前端硬编码API地址
3. 检查防火墙设置

### 错误2：CORS blocked
**原因**：跨域请求被阻止
**解决**：
1. 确保后端CORS中间件正确配置
2. 前后端使用相同的origin

### 错误3：Connection refused
**原因**：服务器未启动或端口错误
**解决**：
1. 确认服务器进程存在
2. 检查端口监听状态
3. 使用正确的启动命令

## 📊 系统健康检查清单

- [ ] PostgreSQL容器运行正常（如果使用主系统）
- [ ] API服务器进程存在
- [ ] 端口8001正在监听
- [ ] 能够通过curl访问API
- [ ] 浏览器能够加载前端页面
- [ ] 前端能够成功调用API

## 🎯 快速修复命令

```bash
# 杀死所有相关进程并重启
pkill -f "python.*api"
source venv/bin/activate
nohup python simple_api.py > server.log 2>&1 &

# 查看服务器日志
tail -f server.log

# 测试API
curl -X POST http://localhost:8001/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{"chat_input": "测试任务创建", "session_id": "test"}'
```

---

**记住**：始终使用 **http://localhost:8001** 访问简化版本系统！