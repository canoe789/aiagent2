/**
 * 展示前端实现能力测试
 * 
 * 运行一个完整的三Agent工作流，并展示最终生成的HTML/CSS代码
 */

const { HelixOrchestrator } = require('../src/orchestrator/helix');
const { SimpleMemory } = require('../src/memory/simple-memory');
const fs = require('fs').promises;
const path = require('path');

async function showcaseFrontendImplementation() {
  console.log('🎨 展示前端实现能力测试\n');
  
  // 初始化组件
  const memory = new SimpleMemory();
  const orchestrator = new HelixOrchestrator({ memory });
  
  // 创建一个展示案例
  const showcaseRequest = {
    message: "为创业孵化器设计并实现一个吸引力十足的着陆页，需要传达创新、活力和专业感，包含完整的前端代码实现",
    type: "full_implementation",
    timestamp: new Date().toISOString()
  };
  
  console.log(`📝 用户需求: ${showcaseRequest.message}\n`);
  console.log('🚀 开始执行三Agent协作流程...\n');
  
  try {
    const result = await orchestrator.processRequest(showcaseRequest);
    
    if (result.type === 'COMPLETED' && result.result.frontendImplementation) {
      console.log('\n✅ 成功生成完整解决方案！\n');
      
      // 展示创意蓝图核心
      if (result.result.creativeBrief) {
        const brief = result.result.creativeBrief;
        console.log('📋 创意蓝图核心:');
        console.log(`   标题: ${brief.strategicChoice?.headline || 'N/A'}`);
        console.log(`   期望情感: ${brief.narrativeStrategy?.content_core?.desired_feeling || 'N/A'}`);
        console.log('');
      }
      
      // 展示视觉概念
      if (result.result.visualConcepts) {
        console.log('🎨 生成的视觉概念:');
        result.result.visualConcepts.visual_explorations?.forEach((concept, index) => {
          console.log(`   ${index + 1}. ${concept.concept_name} - ${concept.atmosphere}`);
        });
        console.log('');
      }
      
      // 展示前端实现决策
      const impl = result.result.frontendImplementation;
      console.log('💻 前端实现决策:');
      console.log(`   选择的概念: ${impl.implementation_choice?.chosen_concept}`);
      console.log(`   决策理由: ${impl.implementation_choice?.reasoning}`);
      console.log('');
      
      // 展示优化记录
      if (impl.refinement_log?.length > 0) {
        console.log('✨ 代码优化记录:');
        impl.refinement_log.forEach((log, index) => {
          console.log(`   ${index + 1}. 发现: ${log.issue_found}`);
          console.log(`      修复: ${log.fix_applied}`);
        });
        console.log('');
      }
      
      // 保存生成的代码到文件
      const outputDir = path.join(__dirname, 'output');
      await fs.mkdir(outputDir, { recursive: true });
      
      const htmlPath = path.join(outputDir, 'landing-page.html');
      const cssPath = path.join(outputDir, 'style.css');
      
      await fs.writeFile(htmlPath, impl.frontend_code.html);
      await fs.writeFile(cssPath, impl.frontend_code.css);
      
      console.log('💾 生成的代码已保存到:');
      console.log(`   HTML: ${htmlPath}`);
      console.log(`   CSS: ${cssPath}`);
      console.log('');
      
      console.log('📄 HTML预览 (前50行):');
      console.log('─'.repeat(50));
      const htmlLines = impl.frontend_code.html.split('\n');
      console.log(htmlLines.slice(0, 50).join('\n'));
      if (htmlLines.length > 50) {
        console.log(`... (还有 ${htmlLines.length - 50} 行)`);
      }
      console.log('─'.repeat(50));
      
      console.log('\n🎨 CSS预览 (前30行):');
      console.log('─'.repeat(50));
      const cssLines = impl.frontend_code.css.split('\n');
      console.log(cssLines.slice(0, 30).join('\n'));
      if (cssLines.length > 30) {
        console.log(`... (还有 ${cssLines.length - 30} 行)`);
      }
      console.log('─'.repeat(50));
      
      console.log('\n🎉 展示完成！你可以在浏览器中打开生成的HTML文件查看效果。');
      
      // 获取项目ID用于后续查询
      console.log(`\n📌 项目ID: ${result.projectId}`);
      console.log('   (可用于后续查询或修改)');
      
    } else {
      console.log('❌ 未能生成完整的前端实现');
      console.log(result);
    }
    
  } catch (error) {
    console.error('❌ 执行失败:', error);
  }
}

// 运行展示
if (require.main === module) {
  showcaseFrontendImplementation().catch(console.error);
}

module.exports = { showcaseFrontendImplementation };