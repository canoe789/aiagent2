#!/usr/bin/env node

/**
 * SimpleMemory命令行工具
 * 
 * 提供交互式的内存仓库查看和管理功能
 */

const { SimpleMemory } = require('../src/memory/simple-memory');
const readline = require('readline');

class MemoryCLI {
  constructor() {
    this.memory = new SimpleMemory();
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: 'memory> '
    });
  }

  start() {
    console.log('🗄️ SimpleMemory 命令行工具');
    console.log('输入 "help" 查看可用命令，输入 "exit" 退出\n');
    
    this.showPrompt();
    
    this.rl.on('line', async (input) => {
      const command = input.trim();
      await this.handleCommand(command);
      this.showPrompt();
    });
    
    this.rl.on('close', () => {
      console.log('\n👋 再见！');
      process.exit(0);
    });
  }
  
  showPrompt() {
    this.rl.prompt();
  }
  
  async handleCommand(command) {
    const [cmd, ...args] = command.split(' ');
    
    try {
      switch (cmd) {
        case 'help':
        case 'h':
          this.showHelp();
          break;
          
        case 'stats':
        case 's':
          await this.showStats();
          break;
          
        case 'projects':
        case 'p':
          await this.listProjects();
          break;
          
        case 'project':
          if (args.length === 0) {
            console.log('❌ 请提供项目ID: project <project_id>');
          } else {
            await this.showProject(args[0]);
          }
          break;
          
        case 'get':
          if (args.length < 2) {
            console.log('❌ 用法: get <project_id> <key>');
          } else {
            await this.getValue(args[0], args[1]);
          }
          break;
          
        case 'search':
          if (args.length === 0) {
            console.log('❌ 请提供搜索词: search <query>');
          } else {
            await this.searchData(args.join(' '));
          }
          break;
          
        case 'keys':
          await this.showAllKeys();
          break;
          
        case 'clear':
          await this.clearMemory();
          break;
          
        case 'export':
          await this.exportData(args[0]);
          break;
          
        case 'recent':
          await this.showRecentData(parseInt(args[0]) || 5);
          break;
          
        case 'size':
          await this.showSizeAnalysis();
          break;
          
        case 'exit':
        case 'quit':
        case 'q':
          this.rl.close();
          break;
          
        case '':
          // 空命令，不做任何事
          break;
          
        default:
          console.log(`❌ 未知命令: ${cmd}. 输入 "help" 查看帮助`);
      }
    } catch (error) {
      console.error('❌ 执行命令时出错:', error.message);
    }
  }
  
  showHelp() {
    console.log(`
📚 可用命令:

基础查看:
  stats, s           - 显示内存统计信息
  projects, p        - 列出所有项目
  project <id>       - 显示特定项目的详细信息
  get <id> <key>     - 获取特定数据项
  keys               - 显示所有存储键
  
搜索分析:
  search <query>     - 搜索数据内容
  recent [n]         - 显示最近的n条数据 (默认5条)
  size               - 显示存储大小分析
  
管理操作:
  clear              - 清空所有数据 (谨慎使用!)
  export [file]      - 导出数据到文件
  
其他:
  help, h            - 显示此帮助信息
  exit, quit, q      - 退出程序
`);
  }
  
  async showStats() {
    const stats = this.memory.getStats();
    console.log('\n📊 内存统计:');
    console.log(`   总条目数: ${stats.totalEntries}`);
    console.log(`   项目数量: ${stats.totalProjects}`);
    console.log(`   内存使用: ${Math.round(stats.memoryUsage.heapUsed / 1024 / 1024 * 100) / 100} MB`);
    console.log(`   RSS: ${Math.round(stats.memoryUsage.rss / 1024 / 1024 * 100) / 100} MB`);
    console.log('');
  }
  
  async listProjects() {
    console.log('\n📁 项目列表:');
    if (this.memory.projectData.size === 0) {
      console.log('   (暂无项目)');
    } else {
      for (const [projectId, keys] of this.memory.projectData.entries()) {
        console.log(`   📂 ${projectId}`);
        console.log(`      数据键 (${keys.size}): ${Array.from(keys).join(', ')}`);
      }
    }
    console.log('');
  }
  
  async showProject(projectId) {
    const projectData = await this.memory.getProjectData(projectId);
    
    if (Object.keys(projectData).length === 0) {
      console.log(`❌ 项目不存在: ${projectId}`);
      return;
    }
    
    console.log(`\n📂 项目: ${projectId}`);
    console.log('─'.repeat(50));
    
    for (const [key, value] of Object.entries(projectData)) {
      console.log(`\n🔑 ${key}:`);
      const preview = JSON.stringify(value, null, 2);
      if (preview.length > 200) {
        console.log(preview.substring(0, 200) + '...');
        console.log(`   (共 ${preview.length} 字符)`);
      } else {
        console.log(preview);
      }
    }
    console.log('');
  }
  
  async getValue(projectId, key) {
    const value = await this.memory.getContext(projectId, key);
    
    if (value === null) {
      console.log(`❌ 数据不存在: ${projectId}.${key}`);
      return;
    }
    
    console.log(`\n🎯 ${projectId}.${key}:`);
    console.log(JSON.stringify(value, null, 2));
    console.log('');
  }
  
  async searchData(query) {
    const results = await this.memory.search(query);
    
    console.log(`\n🔍 搜索 "${query}" 的结果:`);
    if (results.length === 0) {
      console.log('   (无结果)');
    } else {
      results.forEach((result, index) => {
        console.log(`   ${index + 1}. ${result.projectId}.${result.dataKey}`);
        console.log(`      时间: ${result.timestamp}`);
        const preview = JSON.stringify(result.value).substring(0, 100);
        console.log(`      内容: ${preview}...`);
      });
    }
    console.log('');
  }
  
  async showAllKeys() {
    console.log('\n🗝️ 所有存储键:');
    if (this.memory.storage.size === 0) {
      console.log('   (暂无数据)');
    } else {
      for (const [key, data] of this.memory.storage.entries()) {
        console.log(`   ${key}`);
        console.log(`      时间: ${data.timestamp}`);
        console.log(`      大小: ${JSON.stringify(data.value).length} 字符`);
      }
    }
    console.log('');
  }
  
  async clearMemory() {
    console.log('⚠️  确定要清空所有数据吗？这个操作不可恢复！');
    console.log('输入 "yes" 确认，或按 Enter 取消:');
    
    const confirmation = await new Promise((resolve) => {
      this.rl.question('', resolve);
    });
    
    if (confirmation.toLowerCase() === 'yes') {
      this.memory.storage.clear();
      this.memory.projectData.clear();
      console.log('✅ 内存已清空');
    } else {
      console.log('❌ 操作已取消');
    }
  }
  
  async exportData(filename) {
    const exportData = {
      timestamp: new Date().toISOString(),
      stats: this.memory.getStats(),
      projects: {}
    };
    
    for (const [projectId] of this.memory.projectData.entries()) {
      exportData.projects[projectId] = await this.memory.getProjectData(projectId);
    }
    
    const output = JSON.stringify(exportData, null, 2);
    
    if (filename) {
      const fs = require('fs').promises;
      try {
        await fs.writeFile(filename, output);
        console.log(`✅ 数据已导出到: ${filename}`);
      } catch (error) {
        console.log(`❌ 导出失败: ${error.message}`);
      }
    } else {
      console.log('\n📤 导出数据:');
      console.log(output);
    }
    console.log('');
  }
  
  async showRecentData(count) {
    const entries = Array.from(this.memory.storage.entries())
      .sort((a, b) => new Date(b[1].timestamp) - new Date(a[1].timestamp))
      .slice(0, count);
    
    console.log(`\n⏰ 最近 ${count} 条数据:`);
    if (entries.length === 0) {
      console.log('   (暂无数据)');
    } else {
      entries.forEach(([key, data], index) => {
        console.log(`   ${index + 1}. ${data.projectId}.${data.key}`);
        console.log(`      时间: ${data.timestamp}`);
        console.log(`      大小: ${JSON.stringify(data.value).length} 字符`);
      });
    }
    console.log('');
  }
  
  async showSizeAnalysis() {
    const analysis = {};
    let totalSize = 0;
    
    for (const [key, data] of this.memory.storage.entries()) {
      const size = JSON.stringify(data.value).length;
      const type = data.key;
      
      if (!analysis[type]) {
        analysis[type] = { count: 0, totalSize: 0 };
      }
      
      analysis[type].count++;
      analysis[type].totalSize += size;
      totalSize += size;
    }
    
    console.log('\n📏 存储大小分析:');
    for (const [type, info] of Object.entries(analysis)) {
      const avgSize = Math.round(info.totalSize / info.count);
      const percentage = Math.round(info.totalSize / totalSize * 100);
      console.log(`   ${type}:`);
      console.log(`      数量: ${info.count}`);
      console.log(`      总大小: ${info.totalSize} 字符 (${percentage}%)`);
      console.log(`      平均大小: ${avgSize} 字符`);
    }
    console.log(`\n   总计: ${totalSize} 字符`);
    console.log('');
  }
}

// 启动CLI
if (require.main === module) {
  const cli = new MemoryCLI();
  cli.start();
}

module.exports = { MemoryCLI };