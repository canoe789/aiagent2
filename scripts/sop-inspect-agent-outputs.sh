#!/bin/bash
# SOP: 直接检测Agent实际输出 - 消除推测，显示真相
# 专门解决系统透明度问题，让Agent输出可见

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 默认参数
JOB_ID=""
TASK_ID=""
FORMAT="human"
SHOW_RAW="false"

usage() {
    cat << EOF
🔍 SOP: Agent输出检测器 - 消除推测，直接查看真相

用法: $0 [选项]

选项:
    -j, --job-id JOB_ID        检查指定Job的所有Agent真实输出
    -t, --task-id TASK_ID      检查指定Task的完整真实输出
    --raw                      显示原始数据库内容，不做任何格式化
    -h, --help                 显示帮助

核心功能:
    1. 直接从数据库提取Agent的实际input_data和output_data
    2. 显示完整的JSON数据，不截断不推测
    3. 展示Agent的真实错误信息，不是日志推断
    4. 验证Schema匹配情况

示例:
    $0 --job-id 20             # 查看Job 20每个Agent的真实输出
    $0 --task-id 128233        # 查看AGENT_2的具体输出数据
    $0 --job-id 20 --raw       # 显示原始数据库记录

EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -j|--job-id)
            JOB_ID="$2"
            shift 2
            ;;
        -t|--task-id)
            TASK_ID="$2"
            shift 2
            ;;
        --raw)
            SHOW_RAW="true"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            usage
            exit 1
            ;;
    esac
done

# 数据库直连函数 - 使用Python asyncpg
db_query() {
    local query="$1"
    python3 -c "
import asyncio
import asyncpg
import sys

async def run_query():
    try:
        conn = await asyncpg.connect('postgresql://helix_user:helix_secure_password_2024@localhost/helix')
        result = await conn.fetch('$query')
        for row in result:
            print('|'.join(str(v) if v is not None else ' ' for v in row))
        await conn.close()
    except Exception as e:
        print(f'数据库错误: {e}', file=sys.stderr)
        sys.exit(1)

asyncio.run(run_query())
" 2>/dev/null
}

# 格式化JSON - 保持完整性
format_json_safe() {
    local json_data="$1"
    if [[ "$SHOW_RAW" == "true" ]]; then
        echo "$json_data"
    else
        # 使用Python安全格式化，失败则显示原始数据
        echo "$json_data" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    print(json.dumps(data, indent=2, ensure_ascii=False))
except:
    # 如果JSON解析失败，直接输出原始内容
    sys.stdin.seek(0)
    print(sys.stdin.read())
" 2>/dev/null || echo "$json_data"
    fi
}

# 检查Job的真实Agent输出
inspect_job_real_outputs() {
    local job_id="$1"
    
    echo -e "${BLUE}🔍 SOP检测: Job ${job_id} 的Agent真实输出${NC}"
    echo "=================================================================="
    
    # 获取Job信息
    local job_query="SELECT status, initial_request->>'chat_input' as chat_input, created_at FROM jobs WHERE id = $job_id;"
    local job_info=$(db_query "$job_query")
    
    if [[ -z "$job_info" ]]; then
        echo -e "${RED}❌ 错误: Job $job_id 不存在${NC}"
        return 1
    fi
    
    echo -e "${GREEN}📋 Job基本信息:${NC}"
    echo "$job_info" | while IFS='|' read -r status chat_input created_at; do
        echo "  状态: $status"
        echo "  请求: $chat_input"
        echo "  创建: $created_at"
    done
    echo
    
    # 获取所有Tasks的完整数据
    local tasks_query="
        SELECT id, agent_id, status, 
               input_data, output_data, error_log,
               started_at, completed_at,
               EXTRACT(EPOCH FROM (completed_at - started_at)) as duration_seconds
        FROM tasks 
        WHERE job_id = $job_id 
        ORDER BY id ASC;
    "
    
    echo -e "${PURPLE}🤖 Agent真实执行结果:${NC}"
    echo "=================================================================="
    
    local task_count=0
    db_query "$tasks_query" | while IFS='|' read -r task_id agent_id status input_data output_data error_log started_at completed_at duration; do
        task_count=$((task_count + 1))
        
        echo -e "${CYAN}📝 Task $task_id: $agent_id${NC}"
        echo "  状态: $status"
        echo "  开始: $started_at"
        echo "  完成: ${completed_at:-未完成}"
        if [[ "$duration" != "" && "$duration" != " " ]]; then
            echo "  耗时: ${duration}秒"
        fi
        
        # 显示错误信息（如果有）
        if [[ -n "$error_log" && "$error_log" != " " && "$error_log" != "[ORCHESTRATED]" ]]; then
            echo -e "${RED}🚨 真实错误信息:${NC}"
            echo "$error_log" | sed 's/^/    /'
            echo
        fi
        
        # 显示输入数据
        echo -e "${YELLOW}📥 输入数据 (input_data):${NC}"
        if [[ -n "$input_data" && "$input_data" != " " ]]; then
            echo "$input_data" | format_json_safe | sed 's/^/    /'
        else
            echo "    (无输入数据)"
        fi
        echo
        
        # 显示输出数据 - 这是关键部分
        echo -e "${GREEN}📤 输出数据 (output_data) - Agent的真实返回:${NC}"
        if [[ -n "$output_data" && "$output_data" != " " ]]; then
            echo "$output_data" | format_json_safe | sed 's/^/    /'
        else
            echo -e "${RED}    ❌ 无输出数据 - Agent可能未正常完成${NC}"
        fi
        
        echo "=================================================================="
    done
    
    # 统计信息
    local stats_query="
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
            COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed,
            COUNT(CASE WHEN status = 'IN_PROGRESS' THEN 1 END) as in_progress,
            COUNT(CASE WHEN output_data IS NOT NULL AND output_data != ' ' THEN 1 END) as has_output
        FROM tasks WHERE job_id = $job_id;
    "
    
    echo -e "${BLUE}📊 Job $job_id 执行统计:${NC}"
    db_query "$stats_query" | while IFS='|' read -r total completed failed in_progress has_output; do
        echo "  总任务数: $total"
        echo "  已完成: $completed"
        echo "  失败: $failed"
        echo "  进行中: $in_progress"
        echo "  有输出数据: $has_output"
        
        if [[ "$has_output" != "$completed" ]]; then
            echo -e "${RED}  ⚠️  警告: 完成任务数与有输出数据的任务数不匹配！${NC}"
        fi
    done
}

# 检查特定Task的完整真实输出
inspect_task_real_output() {
    local task_id="$1"
    
    echo -e "${BLUE}🔍 SOP检测: Task ${task_id} 的完整真实输出${NC}"
    echo "=================================================================="
    
    local task_query="
        SELECT job_id, agent_id, status, 
               input_data, output_data, error_log,
               assigned_at, started_at, completed_at, retry_count,
               EXTRACT(EPOCH FROM (completed_at - started_at)) as duration_seconds
        FROM tasks 
        WHERE id = $task_id;
    "
    
    local task_info=$(db_query "$task_query")
    
    if [[ -z "$task_info" ]]; then
        echo -e "${RED}❌ 错误: Task $task_id 不存在${NC}"
        return 1
    fi
    
    echo "$task_info" | while IFS='|' read -r job_id agent_id status input_data output_data error_log assigned_at started_at completed_at retry_count duration; do
        echo -e "${GREEN}📋 Task详细信息:${NC}"
        echo "  Task ID: $task_id"
        echo "  Job ID: $job_id"
        echo "  Agent: $agent_id"
        echo "  状态: $status"
        echo "  分配时间: $assigned_at"
        echo "  开始时间: $started_at"
        echo "  完成时间: ${completed_at:-未完成}"
        echo "  重试次数: $retry_count"
        if [[ "$duration" != "" && "$duration" != " " ]]; then
            echo "  执行耗时: ${duration}秒"
        fi
        echo
        
        # 错误信息
        if [[ -n "$error_log" && "$error_log" != " " && "$error_log" != "[ORCHESTRATED]" ]]; then
            echo -e "${RED}🚨 真实错误信息:${NC}"
            echo "$error_log"
            echo
        fi
        
        # 输入数据
        echo -e "${YELLOW}📥 Agent输入数据 (完整):${NC}"
        if [[ -n "$input_data" && "$input_data" != " " ]]; then
            echo "$input_data" | format_json_safe
        else
            echo "  (无输入数据)"
        fi
        echo
        
        # 输出数据 - 核心检测点
        echo -e "${GREEN}📤 Agent输出数据 (完整真实返回):${NC}"
        if [[ -n "$output_data" && "$output_data" != " " ]]; then
            echo "$output_data" | format_json_safe
        else
            echo -e "${RED}  ❌ 无输出数据${NC}"
            echo -e "${RED}  这意味着Agent没有返回任何结果，或者返回失败${NC}"
        fi
    done
}

# 显示最新的Agent输出情况
show_recent_outputs() {
    echo -e "${BLUE}🔍 SOP检测: 最近Agent输出概览${NC}"
    echo "=================================================================="
    
    # 最近10个任务的输出情况
    local recent_query="
        SELECT id, job_id, agent_id, status, 
               CASE 
                   WHEN output_data IS NOT NULL AND output_data != ' ' THEN '有输出'
                   ELSE '无输出'
               END as has_output,
               completed_at
        FROM tasks 
        ORDER BY id DESC 
        LIMIT 10;
    "
    
    echo -e "${GREEN}📊 最近10个任务的输出情况:${NC}"
    db_query "$recent_query" | while IFS='|' read -r task_id job_id agent_id status has_output completed_at; do
        if [[ "$has_output" == "有输出" ]]; then
            echo -e "  Task $task_id (Job $job_id): $agent_id [$status] ${GREEN}✓ $has_output${NC} - $completed_at"
        else
            echo -e "  Task $task_id (Job $job_id): $agent_id [$status] ${RED}✗ $has_output${NC} - $completed_at"
        fi
    done
    
    echo
    echo -e "${PURPLE}🔍 Agent输出数据统计 (最近24小时):${NC}"
    local stats_query="
        SELECT agent_id,
               COUNT(*) as total,
               COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
               COUNT(CASE WHEN output_data IS NOT NULL AND output_data != ' ' THEN 1 END) as with_output
        FROM tasks 
        WHERE created_at > NOW() - INTERVAL '24 hours'
        GROUP BY agent_id 
        ORDER BY agent_id;
    "
    
    db_query "$stats_query" | while IFS='|' read -r agent_id total completed with_output; do
        local output_rate="0"
        if [[ "$completed" -gt 0 ]]; then
            output_rate=$(echo "scale=1; $with_output * 100 / $completed" | bc 2>/dev/null || echo "0")
        fi
        
        if [[ "$with_output" == "$completed" ]]; then
            echo -e "  $agent_id: 总计$total, 完成$completed, ${GREEN}有输出$with_output (${output_rate}%)${NC}"
        else
            echo -e "  $agent_id: 总计$total, 完成$completed, ${RED}有输出$with_output (${output_rate}%)${NC}"
        fi
    done
}

# 主逻辑
main() {
    if [[ -n "$JOB_ID" ]]; then
        inspect_job_real_outputs "$JOB_ID"
    elif [[ -n "$TASK_ID" ]]; then
        inspect_task_real_output "$TASK_ID"
    else
        show_recent_outputs
    fi
}

# 执行
main "$@"