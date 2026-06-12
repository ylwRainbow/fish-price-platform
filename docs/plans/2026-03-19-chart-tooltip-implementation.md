# 图表 Tooltip 增强功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现图表 tooltip 智能切换和农历信息显示功能

**Architecture:** 
在 ChartView.vue 中增强数据结构，添加农历日期计算和缓存机制，实现智能 tooltip formatter 函数，根据选中线条数量自动切换轴触发和点触发模式。

**Tech Stack:** 
Vue 3, ECharts 5, lunar-javascript

---

## Task 1: 添加农历计算工具函数

**Files:**
- Modify: `frontend/src/views/ChartView.vue:360-390`

**Step 1: 在现有 solarToLunarLabel 函数后添加新的农历计算函数**

在文件第 377 行后添加：

```javascript
/**
 * 阳历日期转农历日期字符串（YYYY-MM-DD 格式）
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
    console.error('农历转换失败:', solarDateStr, e)
    return solarDateStr
  }
}

/**
 * 农历日期缓存（避免重复计算）
 */
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

**Step 2: 验证代码无语法错误**

打开浏览器开发者工具，查看是否有 JavaScript 语法错误

**Step 3: 提交**

```bash
git add frontend/src/views/ChartView.vue
git commit -m "feat: add lunar date calculation functions with cache"
```

---

## Task 2: 增强数据结构 - 添加农历日期字段

**Files:**
- Modify: `frontend/src/views/ChartView.vue:297-350`

**Step 1: 在 fetchData 函数中添加农历日期计算**

找到第 315 行左右的 data 构建代码，修改为：

```javascript
const data = []
for (const item of responseData) {
  const solarDate = item.date
  const lunarDate = getLunarDate(solarDate)  // 新增：计算农历
  
  data.push({
    date: solarDate,
    lunarDate: lunarDate,    // 新增：存储农历日期
    price: item.price,
    monthDay: extractMonthDay(solarDate)
  })
}
```

**Step 2: 在 series 构建时保留完整数据**

找到第 423-458 行的农历模式 series 构建代码，修改为：

```javascript
series = chartSeries.value.map(s => {
  const lunarDataMap = new Map()
  s.data.forEach(d => {
    const lunarLabel = solarToLunarLabel(d.date)
    if (lunarLabel) {
      lunarDataMap.set(lunarLabel, d)
    }
  })
  
  return {
    name: s.name,
    type: 'line',
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    connectNulls: true,
    data: xAxisData.map(label => lunarDataMap.get(label)?.price ?? null),
    lineStyle: {
      color: s.color,
      width: 2,
      shadowColor: s.color,
      shadowBlur: 5
    },
    itemStyle: {
      color: s.color,
      borderColor: '#fff',
      borderWidth: 1
    },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: s.color + '40' },
        { offset: 1, color: s.color + '05' }
      ])
    },
    allData: s.data  // 新增：保留完整数据用于 tooltip
  }
})
```

**Step 3: 同样修改公历模式的 series 构建**

找到第 478-513 行，添加相同的 `allData: s.data` 字段

**Step 4: 提交**

```bash
git add frontend/src/views/ChartView.vue
git commit -m "feat: enhance data structure with lunar date field"
```

---

## Task 3: 实现 Tooltip 格式化函数

**Files:**
- Modify: `frontend/src/views/ChartView.vue:360-390`

**Step 1: 添加 tooltip formatter 函数**

在 getLunarDate 函数后添加：

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
  const solarDate = param.data?.date || '未知'
  const lunarDate = param.data?.lunarDate || getLunarDate(solarDate)
  const price = param.value ?? '无数据'
  
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

**Step 2: 提交**

```bash
git add frontend/src/views/ChartView.vue
git commit -m "feat: implement tooltip formatter functions"
```

---

## Task 4: 配置 Tooltip 和图例监听

**Files:**
- Modify: `frontend/src/views/ChartView.vue:516-575`

**Step 1: 修改 renderChart 中的 tooltip 配置**

找到第 518-534 行，修改 tooltip 配置为：

```javascript
tooltip: {
  trigger: 'axis',  // 默认轴触发
  backgroundColor: 'rgba(10, 20, 40, 0.95)',
  borderColor: '#00f7ff',
  borderWidth: 1,
  textStyle: { color: '#e0e0e0', fontSize: 13 },
  formatter: tooltipFormatter
},
```

**Step 2: 在 renderChart 函数末尾添加图例监听**

在 chartInstance.setOption(option, true) 后添加：

```javascript
// 设置图例监听，动态切换 tooltip 触发模式
setupLegendListener()
```

**Step 3: 添加 setupLegendListener 函数**

在 renderChart 函数后添加：

```javascript
/**
 * 设置图例监听
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

**Step 4: 提交**

```bash
git add frontend/src/views/ChartView.vue
git commit -m "feat: configure tooltip and legend listener"
```

---

## Task 5: 性能优化 - 预计算农历日期

**Files:**
- Modify: `frontend/src/views/ChartView.vue:268-280`

**Step 1: 在 fetchData 开始时清空缓存**

在 fetchData 函数开始处（第 278 行）添加：

```javascript
// 清空农历缓存
lunarCache.clear()
```

**Step 2: 在数据获取后预计算所有农历日期**

在 chartSeries.value = [] 后（第 279 行）添加：

```javascript
// 预计算所有农历日期（批量处理）
const allDates = new Set()
chartSeries.value.forEach(s => {
  s.data.forEach(d => {
    if (d.date) {
      allDates.add(d.date)
    }
  })
})

// 批量预计算并缓存
allDates.forEach(date => {
  getLunarDate(date)
})
```

**Step 3: 提交**

```bash
git add frontend/src/views/ChartView.vue
git commit -m "perf: pre-calculate lunar dates for better performance"
```

---

## Task 6: 功能测试

**Files:**
- Test: 手动测试

**Step 1: 测试多选模式 Tooltip**

1. 访问 http://localhost:5173/
2. 选择市场：上海农产品中心
3. 选择品种：鲈鱼
4. 点击"添加时间段"添加 3 个时间段
5. 设置不同的日期范围
6. 点击"查询对比"
7. 鼠标悬浮到图表上

**预期结果**：
- Tooltip 显示所有线条的信息
- 每条信息包含：线条名称、阳历日期、农历日期、价格
- 使用对比版布局，有分隔线

**Step 2: 测试单选模式 Tooltip**

1. 点击图例隐藏其他线条，只保留 1 条
2. 鼠标悬浮到图表上

**预期结果**：
- Tooltip 只显示该线条的信息
- 使用详细版布局，有📊图标
- 阳历和农历日期分行显示

**Step 3: 测试图例切换**

1. 从单选模式点击图例显示多条线条
2. 再次悬浮查看 tooltip

**预期结果**：
- Tooltip 自动从详细版切换为对比版

**Step 4: 测试农历模式**

1. 切换到农历模式
2. 选择多个时间段
3. 输入农历日期
4. 点击查询
5. 鼠标悬浮查看 tooltip

**预期结果**：
- X 轴显示农历 MM-DD 格式
- Tooltip 中农历和阳历都正确显示

**Step 5: 测试性能**

1. 选择"全部"时间段（多年数据）
2. 快速移动鼠标查看 tooltip

**预期结果**：
- Tooltip 响应流畅，无明显卡顿
- 浏览器控制台无错误

**Step 6: 记录测试结果**

创建测试报告文件：

```bash
cat > test_results.md << 'EOF'
# Tooltip 增强功能测试报告

## 测试结果

### ✅ 多选模式 Tooltip
- 状态：通过
- 显示：对比版布局正确
- 信息：线条名称、阳历、农历、价格都显示

### ✅ 单选模式 Tooltip
- 状态：通过
- 显示：详细版布局正确
- 图标：📊显示正常

### ✅ 图例切换
- 状态：通过
- 切换：自动切换触发模式

### ✅ 农历模式
- 状态：通过
- X 轴：农历 MM-DD 格式正确
- Tooltip：农历阳历都正确

### ✅ 性能测试
- 状态：通过
- 响应：流畅
- 缓存：工作正常

## 测试时间
2026-03-19

## 测试人员
AI Assistant
EOF
```

**Step 7: 提交测试报告**

```bash
git add test_results.md
git commit -m "docs: add test results for tooltip enhancement"
```

---

## Task 7: 边界测试和错误处理验证

**Files:**
- Test: 边界测试

**Step 1: 测试空数据**

1. 查询无数据的时间段
2. 鼠标悬浮

**预期**：Tooltip 显示"无数据"，不报错

**Step 2: 测试单个数据点**

1. 选择只有 1 个数据点的时间段
2. 悬浮查看 tooltip

**预期**：正常显示，不报错

**Step 3: 验证错误处理**

在浏览器控制台执行：

```javascript
// 测试农历转换错误处理
console.log(window.getLunarDate('invalid-date'))
```

**预期**：返回原始日期字符串，不报错

**Step 4: 提交测试报告**

```bash
git add test_results.md
git commit -m "test: add edge case test results"
```

---

## Task 8: 代码审查和清理

**Files:**
- Modify: `frontend/src/views/ChartView.vue`

**Step 1: 检查代码注释**

确保所有新增函数都有中文注释

**Step 2: 删除未使用的代码**

检查是否有调试代码、console.log 等，如有则删除

**Step 3: 格式化代码**

确保代码格式一致

**Step 4: 最终提交**

```bash
git add frontend/src/views/ChartView.vue
git commit -m "chore: code cleanup and review"
```

---

## 完成标准

✅ 所有任务完成
✅ 所有测试通过
✅ 代码审查通过
✅ 无 console 错误
✅ 性能表现良好

---

## 后续任务

完成后可选择：
1. 返回主会话报告完成情况
2. 继续实现 saved-periods 功能
3. 其他优化任务
