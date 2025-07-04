// HELIX AI Assistant - JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('HELIX AI Assistant loaded');
    
    const input = document.getElementById('input');
    const output = document.getElementById('output');
    const button = document.getElementById('submit');
    
    // 测试后端连接
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            console.log('Backend connection OK:', data);
            output.textContent = '✅ 系统已就绪，请输入您的请求...';
            output.className = 'ready';
        })
        .catch(error => {
            console.error('Backend connection failed:', error);
            output.textContent = '❌ 后端连接失败: ' + error.message;
            output.className = 'error';
        });
    
    // 处理请求函数
    async function processRequest() {
        console.log('Processing request...');
        
        const message = input.value.trim();
        if (!message) {
            output.textContent = '请输入内容';
            output.className = 'error';
            return;
        }
        
        // 禁用按钮，显示加载状态
        button.disabled = true;
        output.textContent = '🤖 AI正在处理您的请求，请稍候...';
        output.className = 'loading';
        
        const requestData = {
            message: message,
            type: 'general'
        };
        
        try {
            console.log('Sending request:', requestData);
            
            const response = await fetch('/api/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            console.log('Response status:', response.status);
            
            const data = await response.json();
            console.log('Response data:', data);
            
            if (response.ok && data.success) {
                // 格式化输出
                let formattedOutput = '';
                const result = data.result;
                
                if (result.type === 'COMPLETED') {
                    formattedOutput = `✅ 任务完成！\n\n`;
                    formattedOutput += `项目ID: ${result.projectId}\n`;
                    formattedOutput += `使用的Agent: ${result.agentsUsed ? result.agentsUsed.join(', ') : '未知'}\n`;
                    formattedOutput += `消息: ${result.message}\n\n`;
                    formattedOutput += `详细结果:\n${JSON.stringify(result.result, null, 2)}`;
                } else if (result.type === 'USER_CLARIFICATION_NEEDED') {
                    formattedOutput = `❓ 需要进一步澄清\n\n`;
                    formattedOutput += `消息: ${result.message}\n\n`;
                    if (result.clarificationQuestions) {
                        formattedOutput += `澄清问题:\n`;
                        result.clarificationQuestions.forEach((q, i) => {
                            formattedOutput += `${i + 1}. ${q}\n`;
                        });
                    }
                } else {
                    formattedOutput = JSON.stringify(result, null, 2);
                }
                
                output.textContent = formattedOutput;
                output.className = 'success';
            } else {
                output.textContent = '❌ 错误: ' + (data.message || data.error || '处理失败');
                output.className = 'error';
            }
        } catch (error) {
            console.error('Network error:', error);
            output.textContent = '❌ 网络错误: ' + error.message;
            output.className = 'error';
        } finally {
            button.disabled = false;
        }
    }
    
    // 绑定事件
    button.addEventListener('click', processRequest);
    
    // 支持回车键发送
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            processRequest();
        }
    });
    
    // 全局暴露processRequest函数以便调试
    window.processRequest = processRequest;
});