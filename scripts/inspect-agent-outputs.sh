#!/bin/bash
# HELIX Agent Output Inspector
# 实时查看Agent的详细输入输出，解决系统透明度问题

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 默认参数
JOB_ID=""
TASK_ID=""
AGENT_ID=""
FORMAT="human"
SHOW_FULL_JSON="false"
OUTPUT_FILE=""

usage() {
    cat << EOF
🔍 HELIX Agent Output Inspector

用法: $0 [选项]

选项:
    -j, --job-id JOB_ID        检查指定Job的所有Agent输出
    -t, --task-id TASK_ID      检查指定Task的详细输出
    -a, --agent-id AGENT_ID    检查指定Agent的最近输出
    --format FORMAT            输出格式: human|json|yaml (默认: human)
    --full-json                显示完整JSON而非截断版本
    -o, --output FILE          输出到文件
    -h, --help                 显示此帮助信息

示例:
    $0 --job-id 20                    # 查看Job 20的完整Agent流程
    $0 --task-id 128233               # 查看特定Task的详细输出
    $0 --agent-id AGENT_2             # 查看AGENT_2的最近输出
    $0 --job-id 20 --full-json        # 显示Job 20的完整JSON数据
    $0 --job-id 20 -o job20_debug.txt # 输出到文件

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
        -a|--agent-id)
            AGENT_ID="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --full-json)
            SHOW_FULL_JSON="true"
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
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

# 重定向输出到文件（如果指定）
if [[ -n "$OUTPUT_FILE" ]]; then
    exec > >(tee "$OUTPUT_FILE")
fi

# 数据库连接检查
check_database() {
    if ! command -v psql &> /dev/null; then
        echo -e "${RED}❌ 错误: psql 命令未找到${NC}"
        exit 1
    fi
}

# 格式化JSON输出
format_json() {
    local json_data="$1"
    local max_length="${2:-500}"
    
    if [[ "$SHOW_FULL_JSON" == "true" ]]; then
        echo "$json_data" | python3 -m json.tool 2>/dev/null || echo "$json_data"
    else
        # 截断长JSON但保持结构
        echo "$json_data" | python3 -c "
import json
import sys
data = json.load(sys.stdin)
json_str = json.dumps(data, indent=2, ensure_ascii=False)
if len(json_str) > $max_length:
    print(json_str[:$max_length] + '\\n... [JSON截断，使用 --full-json 查看完整内容]')
else:
    print(json_str)
" 2>/dev/null || echo "$json_data"
    fi
}

# 检查Job的所有Agent输出
inspect_job() {
    local job_id="$1"
    
    echo -e "${BLUE}🔍 检查Job ${job_id}的Agent执行流程${NC}"
    echo "========================================================"
    
    # 获取Job基本信息
    local job_info=$(psql "postgresql://helix_user:helix_secure_password_2024@localhost/helix" -t -c "
        SELECT status, initial_request, created_at, updated_at, completed_at, error_message
        FROM jobs 
        WHERE id = $job_id;
    " 2>/dev/null)
    
    if [[ -z "$job_info" ]]; then
        echo -e "${RED}❌ Job $job_id 未找到${NC}"
        return 1
    fi
    
    echo -e "${GREEN}📋 Job 信息:${NC}"
    echo "$job_info" | while IFS='|' read -r status initial_request created_at updated_at completed_at error_message; do
        echo "  状态: $status"
        echo "  创建时间: $created_at"
        echo "  更新时间: $updated_at"
        echo "  完成时间: ${completed_at:-未完成}"
        if [[ -n "$error_message" ]]; then
            echo -e "  ${RED}错误: $error_message${NC}"
        fi
        echo "  初始请求:"
        echo "$initial_request" | format_json
    done
    
    echo
    echo -e "${PURPLE}🤖 Agent执行详情:${NC}"
    echo "========================================================"
    
    # 获取所有相关Task
    psql "postgresql://helix_user:helix_secure_password_2024@localhost/helix" -t -c "
        SELECT id, agent_id, status, input_data, output_data, error_log, 
               started_at, completed_at, retry_count
        FROM tasks 
        WHERE job_id = $job_id 
        ORDER BY id ASC;
    " 2>/dev/null | while IFS='|' read -r task_id agent_id status input_data output_data error_log started_at completed_at retry_count; do
        
        echo -e "${CYAN}📝 Task $task_id: $agent_id${NC}"
        echo "  状态: $status"
        echo "  开始时间: $started_at"
        echo "  完成时间: ${completed_at:-进行中}"
        echo "  重试次数: $retry_count"
        
        if [[ -n "$error_log" && "$error_log" != " " ]]; then
            echo -e "  ${RED}错误日志:${NC} $error_log"
        fi
        
        echo -e "  ${YELLOW}📥 输入数据:${NC}"
        if [[ -n "$input_data" && "$input_data" != " " ]]; then
            echo "$input_data" | format_json | sed 's/^/    /'
        else
            echo "    (无输入数据)"
        fi
        
        echo -e "  ${GREEN}📤 输出数据:${NC}"
        if [[ -n "$output_data" && "$output_data" != " " ]]; then
            echo "$output_data" | format_json | sed 's/^/    /'
        else
            echo "    (无输出数据)"
        fi
        
        echo "----------------------------------------"
    done
}

# 检查特定Task的详细输出
inspect_task() {
    local task_id="$1"
    
    echo -e "${BLUE}🔍 检查Task ${task_id}的详细信息${NC}"
    echo "========================================================"
    
    local task_info=$(psql "postgresql://helix_user:helix_secure_password_2024@localhost/helix" -t -c "
        SELECT job_id, agent_id, status, input_data, output_data, error_log, 
               assigned_at, started_at, completed_at, retry_count
        FROM tasks 
        WHERE id = $task_id;
    " 2>/dev/null)
    
    if [[ -z "$task_info" ]]; then
        echo -e "${RED}❌ Task $task_id 未找到${NC}"
        return 1
    fi
    
    echo "$task_info" | while IFS='|' read -r job_id agent_id status input_data output_data error_log assigned_at started_at completed_at retry_count; do
        echo -e "${GREEN}📋 基本信息:${NC}"
        echo "  Task ID: $task_id"
        echo "  Job ID: $job_id" 
        echo "  Agent: $agent_id"
        echo "  状态: $status"
        echo "  分配时间: $assigned_at"
        echo "  开始时间: $started_at"
        echo "  完成时间: ${completed_at:-进行中}"
        echo "  重试次数: $retry_count"
        
        if [[ -n "$error_log" && "$error_log" != " " ]]; then
            echo
            echo -e "${RED}🚨 错误日志:${NC}"
            echo "$error_log"
        fi
        
        echo
        echo -e "${YELLOW}📥 输入数据 (input_data):${NC}"
        if [[ -n "$input_data" && "$input_data" != " " ]]; then
            echo "$input_data" | format_json
        else
            echo "  (无输入数据)"
        fi
        
        echo
        echo -e "${GREEN}📤 输出数据 (output_data):${NC}"
        if [[ -n "$output_data" && "$output_data" != " " ]]; then
            echo "$output_data" | format_json
        else
            echo "  (无输出数据)"
        fi
    done
}

# 检查特定Agent的最近输出
inspect_agent() {
    local agent_id="$1"
    
    echo -e "${BLUE}🔍 检查${agent_id}的最近输出${NC}"
    echo "========================================================"
    
    psql "postgresql://helix_user:helix_secure_password_2024@localhost/helix" -t -c "
        SELECT id, job_id, status, output_data, error_log, completed_at
        FROM tasks 
        WHERE agent_id = '$agent_id' 
        ORDER BY id DESC 
        LIMIT 5;
    " 2>/dev/null | while IFS='|' read -r task_id job_id status output_data error_log completed_at; do
        
        echo -e "${CYAN}📝 Task $task_id (Job $job_id)${NC}"
        echo "  状态: $status"
        echo "  完成时间: ${completed_at:-进行中}"
        
        if [[ -n "$error_log" && "$error_log" != " " ]]; then
            echo -e "  ${RED}错误:${NC} $error_log"
        fi
        
        if [[ -n "$output_data" && "$output_data" != " " ]]; then
            echo -e "  ${GREEN}输出:${NC}"
            echo "$output_data" | format_json | sed 's/^/    /'
        else
            echo "  (无输出数据)"
        fi
        
        echo "----------------------------------------"
    done
}

# 显示系统概览
show_overview() {
    echo -e "${BLUE}🔍 HELIX Agent 输出总览${NC}"
    echo "========================================================"
    
    echo -e "${GREEN}📊 最近活跃的Jobs:${NC}"
    psql "postgresql://helix_user:helix_secure_password_2024@localhost/helix" -t -c "
        SELECT id, status, 
               substring(initial_request->>'chat_input' from 1 for 50) as request_preview,
               created_at
        FROM jobs 
        ORDER BY id DESC 
        LIMIT 10;
    " 2>/dev/null | while IFS='|' read -r job_id status request_preview created_at; do
        echo "  Job $job_id [$status]: $request_preview... ($created_at)"
    done
    
    echo
    echo -e "${PURPLE}🤖 Agent执行统计:${NC}"
    psql "postgresql://helix_user:helix_secure_password_2024@localhost/helix" -t -c "
        SELECT agent_id, 
               COUNT(*) as total,
               COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
               COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed,
               COUNT(CASE WHEN status = 'IN_PROGRESS' THEN 1 END) as in_progress
        FROM tasks 
        WHERE created_at > NOW() - INTERVAL '24 hours'
        GROUP BY agent_id 
        ORDER BY agent_id;
    " 2>/dev/null | while IFS='|' read -r agent_id total completed failed in_progress; do
        echo "  $agent_id: 总计$total, 完成$completed, 失败$failed, 进行中$in_progress"
    done
}

# 主逻辑
main() {
    check_database
    
    if [[ -n "$JOB_ID" ]]; then
        inspect_job "$JOB_ID"
    elif [[ -n "$TASK_ID" ]]; then
        inspect_task "$TASK_ID"
    elif [[ -n "$AGENT_ID" ]]; then
        inspect_agent "$AGENT_ID"
    else
        show_overview
    fi
}

# 执行主逻辑
main "$@"