# **HELIX 脏数据清理标准操作规程 (Dirty Data Cleanup SOP)**

**版本:** 1.0  
**生效日期:** 2025-07-08  
**适用范围:** Project HELIX v2.0 所有环境

---

## **1. 概述 (Overview)**

### **1.1 目的**
本SOP规范了HELIX系统中脏数据识别、评估、清理和预防的标准流程，确保数据一致性和系统稳定性。

### **1.2 适用场景**
- `duplicate key` 约束违反错误
- Task状态与Artifact状态不一致
- Agent处理失败导致的残留数据
- 系统升级后的数据迁移清理
- 开发测试环境的数据重置

### **1.3 风险评级**
- **高风险:** 生产环境数据清理
- **中风险:** 预发布环境数据清理
- **低风险:** 开发测试环境数据清理

---

## **2. 脏数据识别 (Dirty Data Identification)**

### **2.1 常见脏数据类型**

#### **类型A: 事务边界不一致**
- **症状:** Task状态为COMPLETED，但Artifact创建失败
- **表现:** `duplicate key value violates unique constraint "artifacts_task_id_name_key"`
- **影响:** 系统无法继续处理该Job的后续steps

#### **类型B: 孤儿Artifacts**
- **症状:** Artifact存在但对应Task状态为FAILED
- **表现:** 数据库中有artifact记录，但workflow无法继续
- **影响:** 资源浪费，状态混乱

#### **类型C: 不完整Job**
- **症状:** Job状态为IN_PROGRESS，但所有Tasks都已失败
- **表现:** 系统持续重试，消耗资源
- **影响:** 性能下降，日志混乱

### **2.2 自动检测脚本**

```bash
# 使用内置的脏数据扫描工具
python scripts/cleanup_dirty_data.py scan
```

**检测逻辑:**
- 查找状态为IN_PROGRESS但包含FAILED tasks的Jobs
- 识别Task状态与Artifact状态不匹配的记录
- 检测超过最大重试次数的失败Jobs

---

## **3. 脏数据评估 (Data Assessment)**

### **3.1 影响评估矩阵**

| 数据类型 | 系统影响 | 业务影响 | 处理优先级 |
|---------|---------|---------|----------|
| 活跃Job的事务不一致 | 🔴 高 | 🔴 高 | 🔥 立即处理 |
| 历史Job的孤儿数据 | 🟡 中 | 🟢 低 | 📅 计划处理 |
| 测试环境残留数据 | 🟢 低 | 🟢 低 | 🧹 定期清理 |

### **3.2 评估清单**

在执行清理前，必须确认：

- [ ] **数据归属:** 确认哪些Jobs/Tasks/Artifacts需要清理
- [ ] **依赖关系:** 检查是否有其他组件依赖这些数据
- [ ] **备份状态:** 重要环境是否已完成数据备份
- [ ] **影响范围:** 清理操作可能影响的用户或业务流程
- [ ] **回滚计划:** 如果清理出现问题的恢复方案

---

## **4. 清理执行流程 (Cleanup Execution)**

### **4.1 预清理检查**

```bash
# 1. SSH安全检查
source ./scripts/ssh-safe-manager.sh
SSH_SAFETY_CHECK

# 2. 系统状态确认
ps aux | grep "start_system\|python.*helix" | grep -v grep

# 3. 数据库连接测试
python -c "
import asyncio
from src.database.connection import db_manager
asyncio.run(db_manager.test_connection())
"

# 4. 创建数据快照 (生产环境必须)
pg_dump -h localhost -U helix_user helix > backup_$(date +%Y%m%d_%H%M%S).sql
```

### **4.2 清理执行步骤**

#### **步骤1: 干运行 (Dry Run)**
```bash
# 查看将被清理的数据
python scripts/cleanup_dirty_data.py cleanup <job_id>
```

#### **步骤2: 确认清理范围**
- 验证输出中的数据条目数量
- 确认没有包含重要的生产数据
- 与团队确认清理范围

#### **步骤3: 执行实际清理**
```bash
# 执行清理
python scripts/cleanup_dirty_data.py cleanup <job_id> --execute
```

#### **步骤4: 验证清理结果**
```bash
# 验证数据已清理
python scripts/cleanup_dirty_data.py scan

# 重启系统测试
python start_system.py
```

### **4.3 批量清理流程**

对于多个问题Jobs的批量清理：

```bash
#!/bin/bash
# 批量清理脚本示例

PROBLEM_JOBS=(1 2 3 4)  # 问题Job ID列表

for job_id in "${PROBLEM_JOBS[@]}"; do
    echo "清理Job $job_id..."
    
    # 干运行检查
    python scripts/cleanup_dirty_data.py cleanup $job_id
    
    # 等待确认
    read -p "确认清理Job $job_id? (y/N): " confirm
    if [ "$confirm" = "y" ]; then
        python scripts/cleanup_dirty_data.py cleanup $job_id --execute
        echo "Job $job_id 清理完成"
    else
        echo "跳过Job $job_id"
    fi
    
    echo "---"
done
```

---

## **5. 清理后验证 (Post-Cleanup Verification)**

### **5.1 数据一致性检查**

```sql
-- 验证没有孤儿artifacts
SELECT a.id, a.task_id, a.name 
FROM artifacts a 
LEFT JOIN tasks t ON a.task_id = t.id 
WHERE t.id IS NULL;

-- 验证Task状态一致性
SELECT t.id, t.status, t.agent_id, 
       CASE WHEN a.id IS NOT NULL THEN 'HAS_ARTIFACT' ELSE 'NO_ARTIFACT' END as artifact_status
FROM tasks t 
LEFT JOIN artifacts a ON t.id = a.task_id 
WHERE t.status = 'COMPLETED' AND a.id IS NULL;
```

### **5.2 系统功能测试**

```bash
# 1. 系统启动测试
timeout 30s python start_system.py
# 应该无duplicate key错误

# 2. API健康检查
curl -f http://localhost:$API_PORT/api/v1/health

# 3. 创建新Job测试 (可选)
curl -X POST http://localhost:$API_PORT/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{"chat_input": "测试清理后的系统功能"}'
```

---

## **6. 预防措施 (Prevention Measures)**

### **6.1 系统改进**

已实施的改进：
- ✅ **事务边界修复:** Agent SDK中的`save_output_and_complete_task`方法
- ✅ **Schema验证增强:** 所有agents的输出格式统一
- ✅ **自动清理工具:** `cleanup_dirty_data.py`脚本

### **6.2 监控告警**

建议实施的监控：

```bash
# 定期检查脏数据 (添加到crontab)
0 */6 * * * cd /home/canoezhang/Projects/aiagent && python scripts/cleanup_dirty_data.py scan | grep "发现.*问题" && echo "ALERT: 发现脏数据" | mail -s "HELIX脏数据告警" admin@company.com
```

### **6.3 开发规范**

强制执行的开发规范：
- 所有数据库操作必须在事务中进行
- Agent输出必须先通过schema验证
- 新增Agent必须更新workflow配置和artifact映射
- 数据结构变更必须包含迁移脚本

---

## **7. 应急响应 (Emergency Response)**

### **7.1 生产环境紧急清理**

当生产环境出现严重脏数据问题时：

```bash
# 1. 立即停止系统 (SSH安全)
source ./scripts/ssh-safe-manager.sh
SAFE_CLEANUP_ALL_HELIX

# 2. 创建紧急备份
pg_dump -h localhost -U helix_user helix > emergency_backup_$(date +%Y%m%d_%H%M%S).sql

# 3. 评估影响范围
python scripts/cleanup_dirty_data.py scan

# 4. 与团队沟通
# - 通知相关团队成员
# - 评估业务影响
# - 制定清理计划

# 5. 执行清理 (团队确认后)
python scripts/cleanup_dirty_data.py cleanup <job_id> --execute

# 6. 系统恢复
python start_system.py
```

### **7.2 回滚操作**

如果清理导致问题：

```bash
# 1. 停止系统
SAFE_CLEANUP_ALL_HELIX

# 2. 恢复数据库
psql -h localhost -U helix_user helix < backup_file.sql

# 3. 重启系统
python start_system.py

# 4. 验证恢复
curl -f http://localhost:$API_PORT/api/v1/health
```

---

## **8. 文档更新 (Documentation Updates)**

### **8.1 清理记录**

每次清理操作必须记录：
- 清理时间和执行人
- 问题描述和清理范围
- 清理前后的数据状态
- 遇到的问题和解决方案

### **8.2 SOP改进**

根据实际操作经验，定期更新本SOP：
- 新发现的脏数据类型
- 更高效的清理方法
- 预防措施的改进
- 自动化工具的优化

---

## **9. 工具参考 (Tool Reference)**

### **9.1 清理工具命令**

```bash
# 扫描问题
python scripts/cleanup_dirty_data.py scan

# 预览清理
python scripts/cleanup_dirty_data.py cleanup <job_id>

# 执行清理
python scripts/cleanup_dirty_data.py cleanup <job_id> --execute
```

### **9.2 SSH安全工具**

```bash
# 加载安全管理器
source ./scripts/ssh-safe-manager.sh

# 安全检查
SSH_SAFETY_CHECK

# 安全终止进程
SAFE_KILL_HELIX <PID>

# 清理所有HELIX进程
SAFE_CLEANUP_ALL_HELIX
```

### **9.3 系统状态检查**

```bash
# 检查运行状态
ps aux | grep -E "(start_system|python.*aiagent)" | grep -v grep

# 检查端口使用
netstat -tuln | grep :$API_PORT

# 检查数据库连接
python -c "import asyncio; from src.database.connection import db_manager; asyncio.run(db_manager.test_connection())"
```

---

**📞 紧急联系:**
- 系统管理员: [联系信息]
- 开发团队: [联系信息]
- 数据库团队: [联系信息]

**🔗 相关文档:**
- [HELIX 系统架构文档](README.md)
- [数据库Schema文档](schemas/)
- [SSH安全管理指南](CLAUDE.md#ssh安全与系统完整性保护)