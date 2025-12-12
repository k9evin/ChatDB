# 图表功能说明

## 📊 功能概述

ChatDB Agent 现在支持自动生成数据可视化图表！当查询返回数值数据或时间序列数据时，Agent 会自动分析并生成合适的图表。

## 🎯 支持的图表类型

1. **柱状图 (Bar Chart)** - 用于分类数据对比
2. **折线图 (Line Chart)** - 用于时间序列数据
3. **面积图 (Area Chart)** - 用于时间序列趋势
4. **饼图 (Pie Chart)** - 用于比例分布
5. **散点图 (Scatter Chart)** - 用于关系分析

## 🔧 工作原理

### 后端工具

1. **suggest_chart_type** - 分析查询结果并建议图表类型
   - 检测时间序列数据
   - 识别数值列和分类列
   - 根据数据特征选择最佳图表类型

2. **prepare_chart_data** - 准备和转换数据用于图表
   - 转换数据格式
   - 处理数值类型
   - 生成图表配置

### Agent 工作流

Agent 会在以下情况自动使用图表工具：

1. 用户查询包含图表关键词（chart, graph, plot, visualize, trend, compare 等）
2. 查询结果包含时间序列数据
3. 查询结果包含数值和分类数据组合
4. 数据行数 > 1 且适合可视化

### 前端展示

- 使用 Recharts 库渲染图表
- 自动适配不同图表类型
- 支持多系列数据
- 响应式设计

## 📝 使用示例

### 示例查询

```
"Show me sales trends over time"
→ 自动生成折线图显示时间序列

"Compare order amounts by customer"
→ 自动生成柱状图对比数据

"Show the distribution of products by category"
→ 自动生成饼图显示分布

"What's the relationship between price and stock?"
→ 自动生成散点图显示关系
```

## 🎨 图表配置

图表配置包括：

- `chart_type`: 图表类型
- `x_key`: X 轴数据键
- `y_key`: Y 轴数据键
- `title`: 图表标题
- `x_label`: X 轴标签
- `y_label`: Y 轴标签
- `multiple_series`: 多系列数据键（可选）

## 🚀 技术实现

### 后端

- `backend/tools/visualization.py` - 图表工具实现
- 集成到 LangGraph agent 工作流
- 自动分析数据特征

### 前端

- `frontend/components/chat/chart-visualization.tsx` - 图表组件
- 使用 Recharts 进行渲染
- 支持多种图表类型

## 🔍 数据流

```
用户查询
  ↓
SQL 执行 → 获取数据
  ↓
suggest_chart_type → 分析数据特征
  ↓
prepare_chart_data → 准备图表数据
  ↓
WebSocket 传输 → 发送到前端
  ↓
ChartVisualization → 渲染图表
```

## 💡 最佳实践

1. **明确表达可视化需求** - 使用 "show", "visualize", "chart" 等关键词
2. **时间序列查询** - 包含日期/时间列的查询会自动生成折线图
3. **对比查询** - 使用 "compare", "by" 等词会生成柱状图
4. **分布查询** - 使用 "distribution", "percentage" 会生成饼图

## 🐛 故障排除

### 图表未显示

- 检查查询是否返回了数据
- 确认数据包含数值列
- 查看浏览器控制台错误

### 图表类型不合适

- Agent 会根据数据特征自动选择
- 可以在查询中明确指定图表类型需求

### 数据格式问题

- 确保数值列包含有效数字
- 时间列格式正确

## 📚 相关文件

- `backend/tools/visualization.py` - 图表工具
- `backend/agent/prompts.py` - Agent 提示词（包含图表说明）
- `frontend/components/chat/chart-visualization.tsx` - 图表组件
- `frontend/components/chat-layout.tsx` - 消息显示（包含图表渲染）



