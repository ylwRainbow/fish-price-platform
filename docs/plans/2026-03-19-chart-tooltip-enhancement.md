# 图表 Tooltip 增强功能设计方案

## 需求概述

**目标**：增强图表 tooltip 显示，支持智能切换触发模式，同时显示阳历和农历日期信息

**用户场景**：
1. 多时间段对比时，鼠标悬浮显示所有线条在该日期的详细信息
2. 单选单个时间段时，鼠标悬浮只显示该线条点位的详细信息
3. 所有日期信息同时显示阳历和农历

**技术选型**：ECharts tooltip + lunar-javascript 库

---

## 功能设计

### 1. 智能 Tooltip 触发模式

**多选模式（轴触发）**：
- 触发条件：选中多个时间段（线条）
- 触发方式：`trigger: 'axis'`
- 显示效果：悬浮 X 轴显示该日期所有线条的信息
- 使用场景：多时间段对比

**单选模式（点触发）**：
- 触发条件：只选中一个时间段
- 触发方式：`trigger: 'item'`
- 显示效果：悬浮具体点位只显示该线条的信息
- 使用场景：查看单条折线详情

### 2. Tooltip 显示内容

#### 多选模式 - 对比版布局
```
{农历日期}（农历）
● {线条名称}（{年份}年）
  阳历：{阳历日期}
  价格：{价格} 元/斤
---
● {线条名称 2}（{年份 2}年）
  阳历：{阳历日期 2}
  价格：{价格 2} 元/斤
```

**示例**：
```
01-15（农历）
● 线条 1（2025 年）
  阳历：2025-02-13
  价格：25.5 元/斤
---
● 线条 2（2024 年）
  阳历：2024-02-14
  价格：23.8 元/斤
```

#### 单选模式 - 详细版布局
```
📊 {线条名称}
日期：{阳历日期}（阳历）
      {农历日期}（农历）
价格：{价格} 元/斤
```

**示例**：
```
📊 线条 1
日期：2025-02-13（阳历）
      2025-01-15（农历）
价格：25.5 元/斤
```

---

## 技术架构

### 数据结构增强

#### 当前数据结构
```javascript
chartSeries.value = [
  {
    name: '线条 1',
    color: '#00f7ff',
    year: 2025,
    data: [
      {
        date: '2025-02-13',
        price: 25.5,
        monthDay: '02-13'
      }
    ]
  }
]
```

#### 增强后的数据结构
```javascript
chartSeries.value = [
  {
    name: '线条 1',
    color: '#00f7ff',
    year: 2025,
    data: [
      {
        date: '2025-02-13',      // 阳历日期
        lunarDate: '2025-01-15', // 农历日期（新增）
        price: 25.5,
        monthDay: '02-13'
      }
    ]
  }
]
```

### 核心函数

#### 1. 农历日期计算函数
```javascript
/**
 * 阳历日期转农历日期字符串
 * @param {string} solarDateStr - 阳历日期字符串 (YYYY-MM-DD)
 * @returns {string} 农历日期字符串 (YYYY-MM-DD)
 */
function solarToLunar(solarDateStr) {
  try {
    const [year, month, day] = solarDateStr.split('-').map(Number)
    const solar = Solar.fromYmd(year, month, day)
    const lunar = solar.getLunar()
    const lunarYear = lunar.getYear()
    const lunarMonth = String(lunar.getMonth()).padStart(2, '0')
    const lunarDay = String(lunar.getDay()).padStart(2, '0')
    return `${lunarYear}-${lunarMonth}-${lunarDay}`
  } catch (e) {
    console.error('农历转换失败:', e)
    return solarDateStr
  }
}
```

#### 2. 农历缓存（避免重复计算）
```javascript
const lunarCache = new Map()

/**
 * 获取农历日期（带缓存）
 */
function getLunarDate(solarDateStr) {
  if (lunarCache.has(solarDateStr)) {
    return lunarCache.get(solarDateStr)
  }
  
  const lunarDate = solarToLunar(solarDateStr)
  lunarCache.set(solarDateStr, lunarDate)
  return lunarDate
}
```

#### 3. Tooltip 格式化函数
```javascript
/**
 * Tooltip 格式化函数
 */
function tooltipFormatter(params) {
  // 判断是否为多选模式
  const isMultiSeries = Array.isArray(params) && params.length > 1
  
  if (isMultiSeries) {
    return formatMultiTooltip(params)
  } else {
    const param = Array.isArray(params) ? params[0] : params
    return formatSingleTooltip(param)
  }
}

/**
 * 多选模式 - 对比版布局
 */
function formatMultiTooltip(params) {
  // 获取第一个参数的农历日期作为标题
  const firstParam = params[0]
  const solarDate = firstParam.data.date
  const lunarDate = getLunarDate(solarDate)
  const lunarMonthDay = lunarDate.substring(5) // 获取 MM-DD
  
  let result = `<div style="font-weight:bold;margin-bottom:8px;font-size:14px;">${lunarMonthDay}（农历）</div>`
  
  // 遍历所有线条
  params.forEach((param, index) => {
    const seriesName = param.seriesName
    const solarDate = param.data.date
    const lunarDate = getLunarDate(solarDate)
    const price = param.value
    
    // 提取年份
    const year = solarDate.split('-')[0]
    
    result += `<div style="margin-bottom:6px;">`
    result += `<span style="color:${param.color}">●</span> ${seriesName}（${year}年）<br/>`
    result += `<span style="margin-left:20px;color:#a0a0a0;">阳历：${solarDate}<br/></span>`
    result += `<span style="margin-left:20px;color:#a0a0a0;">价格：<strong>${price}</strong> 元/斤</span>`
    result += `</div>`
    
    // 添加分隔线（最后一条不加）
    if (index < params.length - 1) {
      result += `<div style="border-top:1px solid rgba(0,247,255,0.3);margin:6px 0;"></div>`
    }
  })
  
  return result
}

/**
 * 单选模式 - 详细版布局
 */
function formatSingleTooltip(param) {
  const seriesName = param.seriesName
  const solarDate = param.data.date
  const lunarDate = getLunarDate(solarDate)
  const price = param.value
  
  let result = `<div style="margin-bottom:8px;">`
  result += `<div style="font-weight:bold;margin-bottom:6px;font-size:14px;">📊 ${seriesName}</div>`
  result += `<div style="color:#a0a0a0;margin-bottom:4px;">`
  result += `日期：<span style="color:#e0e0e0;">${solarDate}</span>（阳历）<br/>`
  result += `<span style="margin-left:52px;color:#e0e0e0;">${lunarDate}</span>（农历）`
  result += `</div>`
  result += `<div style="color:#a0a0a0;">`
  result += `价格：<strong style="color:${param.color};font-size:15px;">${price}</strong> 元/斤`
  result += `</div>`
  result += `</div>`
  
  return result
}
```

#### 4. 图例点击监听
```javascript
/**
 * 监听图例选择变化，动态切换 tooltip 触发模式
 */
function setupLegendListener() {
  if (!chartInstance) return
  
  chartInstance.on('legendselectchanged', function(params) {
    const selectedLegends = params.selected
    const selectedCount = Object.values(selectedLegends).filter(v => v).length
    
    // 动态设置 tooltip 触发方式
    const newTrigger = selectedCount === 1 ? 'item' : 'axis'
    
    const option = chartInstance.getOption()
    if (option.tooltip && option.tooltip[0]) {
      option.tooltip[0].trigger = newTrigger
      chartInstance.setOption({ tooltip: option.tooltip[0] })
    }
  })
}
```

---

## 实现步骤

### 阶段 1：数据增强

#### 1.1 在 fetchData 中添加农历计算
```javascript
// 在 fetchData 函数的数据获取循环中
for (const item of responseData) {
  const solarDate = item.date
  const lunarDate = getLunarDate(solarDate)
  
  data.push({
    date: solarDate,
    lunarDate: lunarDate,    // 新增
    price: item.price,
    monthDay: extractMonthDay(solarDate)
  })
}
```

#### 1.2 在 chartSeries 中保留完整数据
```javascript
// 修改 series 数据构建逻辑
series = chartSeries.value.map(s => {
  // 农历模式：创建农历标签到完整数据的映射
  const lunarDataMap = new Map()
  s.data.forEach(d => {
    const lunarLabel = solarToLunarLabel(d.date)
    if (lunarLabel) {
      lunarDataMap.set(lunarLabel, d)  // 存储完整对象
    }
  })
  
  return {
    name: s.name,
    type: 'line',
    data: xAxisData.map(label => {
      const dataItem = lunarDataMap.get(label)
      return dataItem ? dataItem.price : null
    }),
    // 保留原始数据用于 tooltip
    allData: s.data  // 新增
  }
})
```

### 阶段 2：Tooltip 配置

#### 2.1 修改 renderChart 中的 tooltip 配置
```javascript
const option = {
  tooltip: {
    trigger: 'axis',  // 默认轴触发
    backgroundColor: 'rgba(10, 20, 40, 0.95)',
    borderColor: '#00f7ff',
    borderWidth: 1,
    textStyle: { color: '#e0e0e0', fontSize: 13 },
    formatter: tooltipFormatter
  },
  // ... 其他配置
}

chartInstance.setOption(option)
setupLegendListener()
```

### 阶段 3：性能优化

#### 3.1 预计算农历日期
```javascript
// 在 fetchData 开始时清空缓存
lunarCache.clear()

// 批量预计算
const allDates = new Set()
chartSeries.value.forEach(s => {
  s.data.forEach(d => {
    allDates.add(d.date)
  })
})

allDates.forEach(date => {
  getLunarDate(date)  // 预计算并缓存
})
```

---

## 错误处理

### 1. 农历转换失败
```javascript
function getLunarDate(solarDateStr) {
  try {
    if (lunarCache.has(solarDateStr)) {
      return lunarCache.get(solarDateStr)
    }
    
    const lunarDate = solarToLunar(solarDateStr)
    lunarCache.set(solarDateStr, lunarDate)
    return lunarDate
  } catch (e) {
    console.error('农历转换失败:', solarDateStr, e)
    return solarDateStr  // 降级显示阳历
  }
}
```

### 2. Tooltip 数据缺失
```javascript
function formatSingleTooltip(param) {
  const solarDate = param.data?.date || '未知'
  const lunarDate = param.data?.lunarDate || getLunarDate(solarDate)
  const price = param.value ?? '无数据'
  
  // ... 构建 tooltip
}
```

---

## 测试计划

### 功能测试

#### 测试 1：多选模式 Tooltip
**步骤**：
1. 选择 3 个时间段
2. 点击查询
3. 鼠标悬浮到图表上

**预期**：
- Tooltip 显示所有 3 条线条的信息
- 每条信息包含：线条名称、阳历日期、农历日期、价格
- 使用对比版布局

#### 测试 2：单选模式 Tooltip
**步骤**：
1. 选择 1 个时间段
2. 点击查询
3. 鼠标悬浮到图表上

**预期**：
- Tooltip 只显示该线条的信息
- 包含：📊图标、线条名称、阳历日期、农历日期、价格
- 使用详细版布局

#### 测试 3：图例切换
**步骤**：
1. 选择 3 个时间段
2. 点击图例隐藏其中 2 条
3. 鼠标悬浮到图表上

**预期**：
- Tooltip 从对比版自动切换为详细版
- 只显示剩余 1 条线条的信息

#### 测试 4：农历模式
**步骤**：
1. 切换到农历模式
2. 选择多个时间段
3. 鼠标悬浮查看 tooltip

**预期**：
- X 轴显示农历 MM-DD 格式
- Tooltip 中农历和阳历都正确显示

### 性能测试

#### 测试 5：大量数据
**步骤**：
1. 选择"全部"时间段（3 年数据）
2. 快速移动鼠标查看 tooltip

**预期**：
- Tooltip 响应流畅，无明显卡顿
- 农历计算使用缓存，无重复计算

### 边界测试

#### 测试 6：空数据
**步骤**：
1. 查询无数据的时间段
2. 鼠标悬浮

**预期**：
- Tooltip 显示"无数据"
- 不报错

#### 测试 7：日期格式错误
**步骤**：
1. 手动修改数据中的日期格式
2. 查看 tooltip

**预期**：
- Tooltip 降级显示原始日期
- 不报错

---

## 文件清单

### 修改文件
- `frontend/src/views/ChartView.vue` - 主要修改
  - 添加农历计算函数
  - 增强数据结构
  - 修改 tooltip formatter
  - 添加图例监听

### 新增文件
- 无（所有功能集成到 ChartView.vue）

---

## 时间估算

- **数据增强**：30 分钟
- **Tooltip 开发**：1 小时
- **性能优化**：30 分钟
- **测试**：30 分钟
- **总计**：2.5 小时

---

## 后续优化

### 短期优化
1. 添加 tooltip 字体大小配置
2. 支持自定义显示字段
3. 添加日期转换工具函数到独立文件

### 长期优化
1. 支持 tooltip 导出功能
2. 添加数据点标注功能
3. 支持多图表联动 tooltip

---

## 风险评估

### 技术风险
- **低**：ECharts tooltip 成熟稳定
- **低**：lunar-javascript 库已在使用

### 性能风险
- **中**：大量数据时农历计算可能影响性能
- **缓解**：使用缓存机制，预计算

### 用户体验风险
- **低**：智能切换逻辑直观
- **低**：信息布局清晰易读
