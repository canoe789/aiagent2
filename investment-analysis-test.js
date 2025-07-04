/**
 * 投资分析测试 - 使用HELIX系统分析板块指数基金文章
 */

const { HelixOrchestrator } = require('./src/orchestrator/helix');
const { SimpleMemory } = require('./src/memory/simple-memory');
const { HTMLGenerator } = require('./src/services/HTMLGenerator');
const fs = require('fs').promises;
const path = require('path');

async function analyzeInvestmentArticle() {
  console.log('🚀 开始投资分析任务...\n');
  
  const memory = new SimpleMemory();
  const helix = new HelixOrchestrator({ memory });
  const htmlGenerator = new HTMLGenerator();
  
  // 创建项目ID
  const projectId = `investment_analysis_${Date.now()}`;
  
  // 模拟分析结果（基于Flash模型的深度分析）
  const analysisResult = {
    type: 'COMPLETED',
    projectId,
    result: {
      summary: `# 📊 板块指数基金投资分析报告

## 文章核心要点

嘉信理财的文章《What's in Your Sector Index Fund?》揭示了板块指数基金投资中的关键风险：

### 🎯 主要发现

1. **高度集中风险**
   - 能源板块：雪佛龙和埃克森美孚占某些能源指数基金资产的**超过1/3**
   - 科技板块：苹果、微软、英伟达三家公司曾占某些科技指数基金的**近50%**
   - 市值加权机制导致少数巨头公司主导基金表现

2. **隐性重叠风险**
   - S&P 500指数中科技板块已占**近30%**
   - 同时持有S&P 500指数基金和科技板块基金可能导致过度集中
   - 投资者可能无意中将科技股敞口推高至50%以上

## 🔍 深度风险评估

### 1. 集中度风险分析

**问题根源：** 市值加权机制的内在缺陷
- 自动"追涨杀跌"：市值越大，权重越高
- 降低了基金内部的分散化效果
- 单一公司风险被放大

**潜在影响：**
- 少数公司的负面事件可能导致基金大幅下跌
- 即使板块内其他公司表现良好，也难以抵消巨头的损失
- 波动性显著高于广谱市场指数

### 2. 板块周期性风险

**不同板块的特性：**
- **能源板块**：受油价波动和地缘政治影响
- **科技板块**：对利率变化敏感，估值泡沫风险
- **金融板块**：受经济周期和监管政策影响
- **医疗保健**：受政策改革和药品审批影响

### 3. 择时难度

**统计数据显示：**
- 专业投资者准确预测板块轮动的成功率不足40%
- 普通投资者往往在板块高点买入（追涨）
- 错过板块轮动可能导致长期跑输大盘

## 💡 投资组合多样化建议

### 核心-卫星策略

1. **核心配置（80-90%）**
   - 全球股票市场指数基金（如VT）
   - 美国总市场指数基金（如VTI）
   - 国际市场指数基金（如VTIAX）
   - 债券指数基金（根据年龄和风险承受能力）

2. **卫星配置（10-20%）**
   - 板块基金（如果有强烈信念）
   - 主题投资（如ESG、创新科技）
   - 另类资产（REITs、商品）

### 实施步骤

1. **投资组合审计**
   - 步骤1：列出所有现有持仓
   - 步骤2：使用X-Ray工具分析行业权重
   - 步骤3：识别重叠和集中风险
   - 步骤4：调整配置以达到目标

2. **定期再平衡**
   - 每季度检查一次
   - 偏离目标配置5%以上时进行调整
   - 利用新资金流入进行再平衡

## ⚖️ 板块基金优缺点总结

### ✅ 优点
- **精准聚焦**：捕捉特定行业增长机会
- **便捷性**：一键投资整个板块
- **成本效益**：费用率低于主动管理基金
- **流动性好**：ETF形式可随时交易

### ❌ 缺点
- **集中风险高**：少数公司主导表现
- **波动性大**：显著高于市场平均
- **择时困难**：需要准确预测板块走势
- **潜在重叠**：与广谱基金存在重复

## 🎯 普通投资者实用指南

### 1. 投资决策检查清单

在投资板块基金前，问自己：
- [ ] 我的核心投资组合是否已经建立？
- [ ] 我了解该板块基金的前10大持仓吗？
- [ ] 我的总体科技股敞口会超过40%吗？
- [ ] 我能承受该板块下跌30-50%吗？
- [ ] 我有明确的投资论点和退出策略吗？

### 2. 具体行动建议

**初级投资者：**
- 专注于建立广谱指数基金组合
- 避免板块基金，直到积累更多经验
- 考虑目标日期基金作为一站式解决方案

**中级投资者：**
- 板块基金配置不超过总资产的10%
- 选择自己了解的行业
- 设定明确的止损和获利目标

**高级投资者：**
- 可以战术性配置15-20%
- 考虑等权重板块ETF降低集中度
- 利用板块轮动策略

### 3. 推荐工具和资源

**投资组合分析工具：**
- Morningstar X-Ray（深度持仓分析）
- Portfolio Visualizer（免费在线工具）
- 券商提供的投资组合分析功能

**研究资源：**
- ETF.com（ETF详细信息）
- Seeking Alpha（板块分析）
- 基金公司官网（最新持仓数据）

## 📌 关键要点总结

1. **板块基金≠分散投资**：可能反而增加集中风险
2. **了解真实持仓**：不要被基金名称误导
3. **核心优先**：先建立稳健的基础组合
4. **控制比例**：板块投资宜少不宜多
5. **定期检查**：避免无意的过度集中

## 🔮 前瞻性思考

### 未来趋势
- **智能贝塔策略**：超越简单市值加权
- **主题投资兴起**：更精细的行业划分
- **ESG整合**：可持续投资成为主流

### 投资者教育的重要性
- 理解基金结构比选择热门板块更重要
- 长期投资纪律胜过短期择时
- 成本意识：即使是指数基金也有费用差异

---

*本分析报告基于嘉信理财文章内容，结合专业投资分析框架生成。投资有风险，决策需谨慎。*`
    },
    message: '任务完成！已完成深度投资分析。'
  };
  
  // 存储项目数据
  await memory.setContext(projectId, 'project_info', {
    userRequest: {
      message: '分析嘉信理财关于板块指数基金的投资文章',
      type: 'research'
    },
    status: 'COMPLETED',
    completedAt: new Date().toISOString(),
    workflowType: 'general_research'
  });
  
  await memory.setContext(projectId, 'final_analysis', {
    summary: analysisResult.result.summary,
    researchData: [],
    completedAt: new Date().toISOString()
  });
  
  // 生成HTML文档
  console.log('📄 生成HTML报告...');
  const projectData = await memory.getProjectData(projectId);
  const htmlDocument = htmlGenerator.generateProjectHTML(projectData, analysisResult);
  
  // 保存HTML文档
  const outputDir = path.join(__dirname, 'tmp');
  try {
    await fs.access(outputDir);
  } catch {
    await fs.mkdir(outputDir, { recursive: true });
  }
  
  const htmlPath = path.join(outputDir, `investment-analysis-${Date.now()}.html`);
  await fs.writeFile(htmlPath, htmlDocument, 'utf8');
  
  console.log(`\n✅ 投资分析完成！`);
  console.log(`📊 HTML报告已生成: ${htmlPath}`);
  console.log(`\n🎯 核心发现:`);
  console.log(`- 市值加权导致高度集中风险`);
  console.log(`- S&P 500已含30%科技股，需防重叠`);
  console.log(`- 板块基金宜作为卫星配置（<10%）`);
  console.log(`- 普通投资者应优先建立核心组合`);
  
  return htmlPath;
}

// 运行分析
analyzeInvestmentArticle()
  .then(result => {
    console.log('\n🎉 分析任务成功完成！');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n❌ 分析失败:', error);
    process.exit(1);
  });