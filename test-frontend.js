/**
 * 前端界面测试脚本
 */

const fs = require('fs');
const path = require('path');

// 验证前端文件存在
function testFrontendFiles() {
  console.log('🧪 测试前端文件...\n');
  
  const htmlPath = path.join(__dirname, 'public', 'index.html');
  
  try {
    const htmlContent = fs.readFileSync(htmlPath, 'utf8');
    
    console.log('✅ HTML文件存在');
    console.log(`✅ 文件大小: ${(htmlContent.length / 1024).toFixed(2)} KB`);
    
    // 检查关键元素
    const checks = [
      { name: 'HTML结构', test: htmlContent.includes('<!DOCTYPE html>') },
      { name: '输入框', test: htmlContent.includes('<textarea id="input"') },
      { name: '提交按钮', test: htmlContent.includes('<button id="submit"') },
      { name: '输出区域', test: htmlContent.includes('<div id="output">') },
      { name: 'JavaScript功能', test: htmlContent.includes('processRequest()') },
      { name: 'API调用', test: htmlContent.includes('/api/process') },
      { name: '样式表', test: htmlContent.includes('<style>') },
      { name: '响应式设计', test: htmlContent.includes('viewport') }
    ];
    
    console.log('\n📋 功能检查:');
    checks.forEach(check => {
      console.log(`${check.test ? '✅' : '❌'} ${check.name}`);
    });
    
    const passedChecks = checks.filter(c => c.test).length;
    console.log(`\n📊 通过率: ${passedChecks}/${checks.length} (${(passedChecks/checks.length*100).toFixed(1)}%)`);
    
    if (passedChecks === checks.length) {
      console.log('\n🎉 前端界面测试全部通过！');
      console.log('\n🌐 访问地址:');
      console.log('   Web UI: http://localhost:3000');
      console.log('   API: http://localhost:3000/api/process');
      console.log('   健康检查: http://localhost:3000/health');
      
      console.log('\n📝 使用说明:');
      console.log('1. 启动服务器: node src/index.js');
      console.log('2. 浏览器访问: http://localhost:3000');
      console.log('3. 在输入框输入请求，点击发送');
      console.log('4. 支持快捷键: Ctrl+Enter');
      
      console.log('\n✨ 功能特性:');
      console.log('- 简洁的输入输出界面');
      console.log('- 实时处理状态显示');
      console.log('- 错误处理和用户反馈');
      console.log('- 响应式设计，支持移动端');
      console.log('- 自动调用HELIX AI系统');
      
    } else {
      console.log('\n⚠️ 部分检查未通过，请检查HTML文件');
    }
    
    return passedChecks === checks.length;
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    return false;
  }
}

// 运行测试
testFrontendFiles();