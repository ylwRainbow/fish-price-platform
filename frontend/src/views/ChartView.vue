<template>
  <div class="chart-container">
    <div class="design-preview-link">
      <router-link to="/design-preview">
        🎨 UI 设计方案预览
      </router-link>
    </div>
    <div class="filter-panel">
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">市场</label>
          <el-select v-model="selectedMarket"
            placeholder="选择市场" class="filter-select" style="width: 280px">
            <el-option v-for="market in markets" :key="market.id" :label="market.name" :value="market.id" />
          </el-select>
        </div>
        <div class="filter-group">
          <label class="filter-label">品种</label>
          <el-select v-model="selectedFish"
            placeholder="选择品种" class="filter-select" style="width: 200px">
            <el-option v-for="fish in fishes" :key="fish.id" :label="fish.name" :value="fish.id" />
          </el-select>
        </div>
        <div class="filter-group">
          <label class="filter-label">时间类型</label>
          <el-radio-group v-model="calendarType" size="small">
            <el-radio-button value="solar">公历</el-radio-button>
            <el-radio-button value="lunar">农历</el-radio-button>
          </el-radio-group>
        </div>
        <div class="filter-group">
          <label class="filter-label">价格类型</label>
          <el-select v-model="selectedPriceType" class="filter-select" style="width: 120px">
            <el-option label="塘口价" value="pond" />
            <el-option label="批发价" value="wholesale" />
            <el-option label="零售价" value="retail" />
          </el-select>
        </div>
        <div class="filter-group">
          <label class="filter-label">单位</label>
          <el-select v-model="selectedUnit" class="filter-select" style="width: 110px">
            <el-option label="元/kg" value="kg" />
            <el-option label="元/斤" value="斤" />
          </el-select>
        </div>
      </div>

      <div class="time-periods-section">
        <div class="section-header">
          <span class="section-title">时间段配置</span>
          <div class="header-actions">
            <SavedPeriods 
              :current-period="currentTimePeriod" 
              :calendar-type="calendarType"
              @load="loadSavedPeriod"
            />
          </div>
        </div>
        <div class="time-periods-list">
          <div v-for="(period, index) in timePeriods" :key="index" class="time-period-item">
            <el-input v-model="period.name" placeholder="线条名称" class="period-name-input" />
            <div class="period-inputs">
              <template v-if="calendarType === 'solar'">
                <el-date-picker v-model="period.start" type="date" placeholder="开始日期"
                  format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 150px" />
                <span class="separator">至</span>
                <el-date-picker v-model="period.end" type="date" placeholder="结束日期"
                  format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 150px" />
              </template>
              <template v-else>
                <LunarDatePicker v-model="period.start" placeholder="农历开始" style="width: 150px" />
                <span class="separator">至</span>
                <LunarDatePicker v-model="period.end" placeholder="农历结束" style="width: 150px" />
              </template>
            </div>
            <div class="period-quick" v-if="calendarType === 'solar'">
              <el-button size="small" @click="setQuickPeriod(index, 'month1')">近 1 月</el-button>
              <el-button size="small" @click="setQuickPeriod(index, 'month3')">近 3 月</el-button>
              <el-button size="small" @click="setQuickPeriod(index, 'year1')">近 1 年</el-button>
              <el-button size="small" @click="setQuickPeriod(index, 'all')">全部</el-button>
            </div>
            <div class="period-actions">
              <el-button type="success" size="small" @click="saveSinglePeriod(index)" title="保存当前时间段">
                <el-icon><Check /></el-icon>
              </el-button>
              <el-button type="primary" size="small" @click="loadSinglePeriod(index)" title="加载已保存时间段">
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button v-if="timePeriods.length > 1" type="danger" size="small" 
                @click="removeTimePeriod(index)" title="删除当前时间段">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
        <div class="combination-actions">
          <el-button type="warning" size="small" @click="saveCombination" :disabled="timePeriods.length === 0">
            <el-icon><FolderAdd /></el-icon>
            保存组合
          </el-button>
          <el-button type="info" size="small" @click="loadCombination">
            <el-icon><FolderOpened /></el-icon>
            加载组合
          </el-button>
        </div>
        <div class="add-period-row">
          <el-button type="primary" size="small" @click="addTimePeriod" :disabled="timePeriods.length >= 10">
            <el-icon><Plus /></el-icon>
            添加时间段
          </el-button>
          <span class="period-count-hint" v-if="timePeriods.length >= 10">最多支持 10 个时间段</span>
        </div>
      </div>

      <div class="action-row">
        <el-button type="primary" :loading="loading" @click="fetchData">
          <el-icon><Search /></el-icon>
          查询对比
        </el-button>
        <el-button @click="resetFilters">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </div>

    <div class="chart-panel">
      <div class="chart-header" v-if="chartSeries.length > 0">
        <h3 class="chart-title">价格走势对比图</h3>
        <div class="chart-legend">
          <div 
            v-for="(series, index) in chartSeries" 
            :key="series.name" 
            class="legend-item"
            :class="{ 'legend-hidden': !seriesVisibility[index] }"
            @click="toggleSeries(index)"
          >
            <span class="legend-color" :style="{ background: series.color }"></span>
            <span class="legend-label">{{ series.name }}</span>
          </div>
        </div>
      </div>
      <div ref="chartRef" class="chart-wrapper" v-loading="loading"></div>
      <div v-if="!loading && chartSeries.length === 0" class="empty-state">
        <el-empty description="请选择查询条件后点击查询">
          <el-button type="primary" @click="fetchData">立即查询</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Solar, Lunar } from 'lunar-javascript'
import { Plus, Delete, Search, Refresh, Check, Download, FolderAdd, FolderOpened } from '@element-plus/icons-vue'
import LunarDatePicker from '@/components/LunarDatePicker.vue'
import SavedPeriods from '@/components/SavedPeriods.vue'
import { getFishes, getMarkets, getPrices } from '@/api'

const chartRef = ref(null)
let chartInstance = null

const loading = ref(false)
const selectedMarket = ref(null)
const selectedFish = ref(null)
const selectedPriceType = ref('pond')
const selectedUnit = ref('kg')
const calendarType = ref('solar')
const timePeriods = ref([
  { name: '线条1', start: '', end: '' }
])
const chartSeries = ref([])
const markets = ref([])
const fishes = ref([])
const selectedSeriesCount = ref(0)
const allSeriesData = ref([]) // 存储所有系列的完整数据
const seriesVisibility = ref({}) // 存储每个系列的显示状态 {0: true, 1: false, ...}
const chartUnit = ref('kg')

// 当前选中的时间段（用于保存功能）
const currentTimePeriod = computed(() => {
  if (timePeriods.value.length === 1 && timePeriods.value[0].start && timePeriods.value[0].end) {
    return {
      name: timePeriods.value[0].name,
      start: timePeriods.value[0].start,
      end: timePeriods.value[0].end
    }
  }
  return null
})

// 加载已保存的时间段
function loadSavedPeriod(period) {
  timePeriods.value = [{
    name: period.name,
    start: period.start,
    end: period.end
  }]
}

// 保存单个时间段
function saveSinglePeriod(index) {
  const period = timePeriods.value[index]
  if (!period.start || !period.end) {
    ElMessage.warning('请先设置开始和结束日期')
    return
  }
  // 触发 SavedPeriods 组件的保存对话框
  const event = new CustomEvent('save-period', { 
    detail: { 
      name: period.name, 
      start: period.start, 
      end: period.end,
      index: index 
    } 
  })
  window.dispatchEvent(event)
}

// 加载单个时间段
function loadSinglePeriod(index) {
  const event = new CustomEvent('load-period', { 
    detail: { 
      onSelect: (period) => {
        timePeriods.value[index] = {
          name: period.name,
          start: period.start,
          end: period.end
        }
        ElMessage.success('时间段已加载')
      }
    } 
  })
  window.dispatchEvent(event)
}

// 保存时间段组合
function saveCombination() {
  const validPeriods = timePeriods.value.filter(p => p.start && p.end)
  if (validPeriods.length === 0) {
    ElMessage.warning('没有可保存的时间段')
    return
  }
  const event = new CustomEvent('save-combination', { 
    detail: { periods: validPeriods } 
  })
  window.dispatchEvent(event)
}

// 加载时间段组合
function loadCombination() {
  const event = new CustomEvent('load-combination', { 
    detail: { 
      onSelect: (periods) => {
        timePeriods.value = periods.map(p => ({
          name: p.name,
          start: p.start,
          end: p.end
        }))
        ElMessage.success('时间段组合已加载')
      }
    } 
  })
  window.dispatchEvent(event)
}

/**
 * 切换系列的显示/隐藏状态
 * @param {number} index - 系列索引
 */
function toggleSeries(index) {
  if (!chartInstance) return
  
  // 切换状态
  const isVisible = !seriesVisibility.value[index]
  seriesVisibility.value[index] = isVisible
  
  // 获取当前图表的所有系列配置
  const currentOption = chartInstance.getOption()
  const seriesList = currentOption.series[0]
  
  // 创建新的系列配置，只更新指定索引的透明度
  const newSeries = seriesList.map((s, i) => {
    if (i === index) {
      return {
        ...s,
        lineStyle: {
          ...s.lineStyle,
          opacity: isVisible ? 1 : 0
        },
        areaStyle: {
          ...s.areaStyle,
          opacity: isVisible ? 0.3 : 0
        }
      }
    }
    return s
  })
  
  // 更新图表，使用 notMerge: true 确保完全替换
  chartInstance.setOption({
    series: newSeries
  }, { notMerge: true })
}

watch(calendarType, () => {
  timePeriods.value = [{ name: '线条 1', start: '', end: '' }]
})

const colors = [
  '#00f7ff', '#ff6b6b', '#4ecdc4', '#ffd93d', '#6bcb77',
  '#ff8c42', '#a855f7', '#ec4899', '#14b8a6', '#f97316'
]

/**
 * 加载后端目录数据
 */
async function loadConfig() {
  try {
    const [marketData, fishData] = await Promise.all([
      getMarkets(),
      getFishes()
    ])
    markets.value = marketData || []
    fishes.value = fishData || []
  } catch (error) {
    console.error('加载目录数据失败:', error)
    ElMessage.error('目录数据加载失败，请检查后端和数据库连接')
  }
}

/**
 * 农历转公历
 */
function lunarToSolar(lunarStr) {
  if (!lunarStr) return null
  const parts = lunarStr.split('-')
  if (parts.length !== 3) return null
  
  const lunarYear = parseInt(parts[0])
  const lunarMonth = parseInt(parts[1])
  let lunarDay = parseInt(parts[2])
  
  try {
    while (lunarDay > 0) {
      try {
        const lunar = Lunar.fromYmd(lunarYear, lunarMonth, lunarDay)
        const solar = lunar.getSolar()
        return solar.toString()
      } catch (e) {
        lunarDay--
      }
    }
    return null
  } catch (e) {
    console.error('农历转换失败:', e)
    return null
  }
}

/**
 * 添加时间段
 */
function addTimePeriod() {
  timePeriods.value.push({ name: `线条${timePeriods.value.length + 1}`, start: '', end: '' })
}

/**
 * 移除时间段
 */
function removeTimePeriod(index) {
  timePeriods.value.splice(index, 1)
}

/**
 * 设置快速时间段
 */
function setQuickPeriod(index, type) {
  const now = new Date()
  let startDate = new Date()
  
  switch (type) {
    case 'month1':
      startDate.setMonth(now.getMonth() - 1)
      break
    case 'month3':
      startDate.setMonth(now.getMonth() - 3)
      break
    case 'year1':
      startDate.setFullYear(now.getFullYear() - 1)
      break
    case 'all':
      startDate = new Date('2017-01-01')
      break
  }
  
  const formatDate = (d) => d.toISOString().split('T')[0]
  timePeriods.value[index].start = formatDate(startDate)
  timePeriods.value[index].end = formatDate(now)
}

/**
 * 重置筛选条件
 */
function resetFilters() {
  selectedMarket.value = null
  selectedFish.value = null
  selectedPriceType.value = 'pond'
  selectedUnit.value = 'kg'
  calendarType.value = 'solar'
  timePeriods.value = [{ start: '', end: '' }]
  chartSeries.value = []
  chartUnit.value = 'kg'
  if (chartInstance) {
    chartInstance.clear()
  }
}

/**
 * 获取市场名称
 */
function getMarketName(marketId) {
  const market = markets.value.find(m => m.id === marketId)
  return market ? market.name : marketId
}

/**
 * 获取品种名称
 */
function getFishName(fishId) {
  const fish = fishes.value.find(f => f.id === fishId)
  return fish ? fish.name : fishId
}

/**
 * 从日期字符串提取年份
 */
function extractYear(dateStr) {
  return dateStr ? parseInt(dateStr.split('-')[0]) : null
}

/**
 * 从日期字符串提取月日（MM-DD格式）
 */
function extractMonthDay(dateStr) {
  if (!dateStr) return null
  const parts = dateStr.split('-')
  if (parts.length >= 3) {
    return `${parts[1]}-${parts[2]}`
  }
  return null
}

/**
 * 获取数据
 */
async function fetchData() {
  if (!selectedMarket.value || !selectedFish.value) {
    ElMessage.warning('请先选择市场和品种')
    return
  }
  
  const validPeriods = timePeriods.value.filter(p => p.start && p.end)
  if (validPeriods.length === 0) {
    ElMessage.warning('请至少设置一个有效时间段')
    return
  }
  
  loading.value = true
  chartSeries.value = []
  
  try {
    const seriesData = []
    let colorIndex = 0
    
    for (let i = 0; i < validPeriods.length; i++) {
      const period = validPeriods[i]
      let startDate = period.start
      let endDate = period.end
      
      if (!startDate || !endDate) continue
      
      // 从时间段提取年份作为系列名称
      const startYear = extractYear(startDate)
      const endYear = extractYear(endDate)
      const periodName = period.name || `${startYear}年`
      
      try {
        const marketId = selectedMarket.value
        const fishId = selectedFish.value
        
        const response = await getPrices({
          market_id: marketId,
          fish_id: fishId,
          start: startDate,
          end: endDate,
          price_type: selectedPriceType.value,
          unit: selectedUnit.value
        })
        
        const rawData = response.points || []
        const data = rawData.map(p => {
          const dateStr = p.ts.split('T')[0]
          const monthDay = extractMonthDay(dateStr)
          const year = extractYear(dateStr)
          const lunarDate = getLunarDate(dateStr)
          let label = monthDay
          
          if (calendarType.value === 'lunar') {
            const parts = dateStr.split('-')
            const y = parseInt(parts[0])
            const m = parseInt(parts[1])
            const d = parseInt(parts[2])
            const solar = Solar.fromYmd(y, m, d)
            const lunar = solar.getLunar()
            label = `${lunar.getMonthInChinese()}月${lunar.getDayInChinese()}`
          }
          
          return {
            date: dateStr,
            lunarDate: lunarDate,
            monthDay: monthDay,
            year: year,
            label: label,
            price: p.price,
            unit: p.unit || response.market?.unit || 'kg',
            dataTrust: p.data_trust
          }
        })
        
        if (data.length > 0) {
          chartUnit.value = data[0].unit || chartUnit.value
          seriesData.push({
            name: periodName,
            year: startYear,
            data: data,
            color: colors[colorIndex % colors.length]
          })
          colorIndex++
        }
      } catch (e) {
        console.error('获取数据失败:', e)
        ElMessage.error(`获取 ${periodName} 数据失败：${e.message}`)
      }
    }
    
    chartSeries.value = seriesData
    // 初始化所有系列为可见状态
    seriesVisibility.value = {}
    seriesData.forEach((_, index) => {
      seriesVisibility.value[index] = true
    })
    await nextTick()
    renderChart()
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error(`查询失败：${error.message}`)
  } finally {
    loading.value = false
  }
}

/**
 * 阳历日期转农历数字标签（MM-DD 格式）
 */
function solarToLunarLabel(dateStr) {
  try {
    const parts = dateStr.split('-')
    const year = parseInt(parts[0])
    const month = parseInt(parts[1])
    const day = parseInt(parts[2])
    const solar = Solar.fromYmd(year, month, day)
    const lunar = solar.getLunar()
    const lunarMonth = String(lunar.getMonth()).padStart(2, '0')
    const lunarDay = String(lunar.getDay()).padStart(2, '0')
    return `${lunarMonth}-${lunarDay}`
  } catch (e) {
    return dateStr
  }
}

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

/**
 * 格式化单个数据点的详细信息（用于单选模式）
 */
function formatSingleTooltip(param) {
  if (!param || param.value === null || param.value === undefined) return ''
  
  const seriesName = param.seriesName
  const price = param.value
  const axisValue = param.axisValue
  
  // 从保存的完整数据中查找
  let solarDate = ''
  let lunarDate = ''
  
  if (allSeriesData.value && param.seriesIndex !== undefined) {
    const seriesData = allSeriesData.value[param.seriesIndex]
    if (seriesData) {
      // 查找匹配价格的数据点
      const dataPoint = seriesData.find(d => d.price === price)
      if (dataPoint) {
        solarDate = dataPoint.date
        lunarDate = dataPoint.lunarDate
      }
    }
  }
  
  const solarDisplay = solarDate || axisValue
  const lunarDisplay = lunarDate || solarDisplay
  
  return `
    <div style="font-weight:bold;margin-bottom:8px;font-size:14px;">📊 ${seriesName}</div>
    <div style="margin-bottom:4px;">日期：<strong>${solarDisplay}</strong>（阳历）</div>
    <div style="margin-bottom:4px; margin-left: 40px;"><strong>${lunarDisplay}</strong>（农历）</div>
    <div style="margin-bottom:4px;">价格：<strong style="color:#ffd700">${price}</strong> 元/${chartUnit.value}</div>
  `.trim()
}

/**
 * 格式化多个数据点的详细信息（用于多选模式）
 */
function formatMultiTooltip(params) {
  if (!params || params.length === 0) return ''
  
  const axisValue = params[0].axisValue
  let result = `<div style="font-weight:bold;margin-bottom:6px;font-size:14px;">${axisValue}</div>`
  
  params.forEach(p => {
    if (p.value !== null && p.value !== undefined) {
      const seriesName = p.seriesName
      const price = p.value
      
      let solarDate = ''
      let lunarDate = ''
      
      // 从保存的完整数据中查找
      if (allSeriesData.value && p.seriesIndex !== undefined) {
        const seriesData = allSeriesData.value[p.seriesIndex]
        if (seriesData) {
          const dataPoint = seriesData.find(d => d.price === price)
          if (dataPoint) {
            solarDate = dataPoint.date
            lunarDate = dataPoint.lunarDate
          }
        }
      }
      
      const solarDisplay = solarDate || axisValue
      const lunarDisplay = lunarDate || solarDisplay
      
      result += `
        <div style="margin-bottom:6px;padding:4px;background:rgba(255,255,255,0.05);border-radius:3px;">
          <div style="margin-bottom:3px;"><span style="color:${p.color}">●</span> <strong>${seriesName}</strong></div>
          <div style="font-size:11px;color:#a0a0a0;margin-bottom:2px;padding-left:16px;">阳历：${solarDisplay} | 农历：${lunarDisplay}</div>
          <div style="padding-left:16px;">价格：<strong style="color:#ffd700">${price}</strong> 元/${chartUnit.value}</div>
        </div>
      `.trim()
    }
  })
  
  return result
}

/**
 * 农历数字标签排序
 */
function sortLunarLabels(labels) {
  return labels.sort((a, b) => {
    const [monthA, dayA] = a.split('-').map(Number)
    const [monthB, dayB] = b.split('-').map(Number)
    if (monthA !== monthB) return monthA - monthB
    return dayA - dayB
  })
}

/**
 * 渲染图表
 */
function renderChart() {
  if (!chartRef.value) return
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
  
  if (chartSeries.value.length === 0) {
    chartInstance.clear()
    selectedSeriesCount.value = 0
    return
  }
  
  // 初始化选中线条数量（默认全部选中）
  selectedSeriesCount.value = chartSeries.value.length
  
  // 保存完整数据供 tooltip 使用
  allSeriesData.value = chartSeries.value.map(s => s.data)
  
  let xAxisData = []
  let series = []
  
  if (calendarType.value === 'lunar') {
    // 农历模式：收集所有农历标签
    const allLunarLabels = new Set()
    chartSeries.value.forEach(s => {
      s.data.forEach(d => {
        const lunarLabel = solarToLunarLabel(d.date)
        if (lunarLabel) {
          allLunarLabels.add(lunarLabel)
        }
      })
    })
    
    xAxisData = sortLunarLabels([...allLunarLabels])
    
    series = chartSeries.value.map(s => {
      const lunarDataMap = new Map()
      s.data.forEach(d => {
        const lunarLabel = solarToLunarLabel(d.date)
        if (lunarLabel) {
          lunarDataMap.set(lunarLabel, d.price)
        }
      })
      
      return {
        name: s.name,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        connectNulls: true,
        data: xAxisData.map(label => lunarDataMap.get(label) ?? null),
        allData: s.data,
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
        }
      }
    })
  } else {
    // 公历模式：X轴使用月日格式（MM-DD），不同年份的数据映射到同一个X轴
    const allMonthDays = new Set()
    chartSeries.value.forEach(s => {
      s.data.forEach(d => {
        if (d.monthDay) {
          allMonthDays.add(d.monthDay)
        }
      })
    })
    
    // 按月日排序
    xAxisData = [...allMonthDays].sort((a, b) => {
      const [monthA, dayA] = a.split('-').map(Number)
      const [monthB, dayB] = b.split('-').map(Number)
      if (monthA !== monthB) return monthA - monthB
      return dayA - dayB
    })
    
    series = chartSeries.value.map(s => {
      // 创建月日到价格的映射
      const monthDayDataMap = new Map()
      s.data.forEach(d => {
        if (d.monthDay) {
          monthDayDataMap.set(d.monthDay, d.price)
        }
      })
      
      return {
        name: s.name,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        connectNulls: true,
        data: xAxisData.map(monthDay => monthDayDataMap.get(monthDay) ?? null),
        allData: s.data,
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
        }
      }
    })
  }
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: selectedSeriesCount.value > 1 ? 'axis' : 'item',
      backgroundColor: 'rgba(10, 20, 40, 0.95)',
      borderColor: '#00f7ff',
      borderWidth: 1,
      textStyle: { color: '#e0e0e0', fontSize: 13 },
      formatter: function(params) {
        if (selectedSeriesCount.value > 1) {
          return formatMultiTooltip(Array.isArray(params) ? params : [params])
        } else {
          return formatSingleTooltip(Array.isArray(params) ? params[0] : params)
        }
      }
    },
    legend: {
      type: 'scroll',
      bottom: 10,
      textStyle: { color: '#a0a0a0', fontSize: 12 },
      pageTextStyle: { color: '#a0a0a0' },
      pageIconColor: '#00f7ff',
      pageIconInactiveColor: '#666'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLine: { lineStyle: { color: 'rgba(0, 247, 255, 0.3)' } },
      axisLabel: { 
        color: '#a0a0a0', 
        fontSize: 11,
        rotate: xAxisData.length > 30 ? 45 : 0,
        interval: xAxisData.length > 60 ? Math.floor(xAxisData.length / 60) : 0
      },
      axisTick: { lineStyle: { color: 'rgba(0, 247, 255, 0.3)' } }
    },
    yAxis: {
      type: 'value',
      name: `价格 (元/${chartUnit.value})`,
      nameTextStyle: { color: '#a0a0a0', fontSize: 12 },
      axisLine: { lineStyle: { color: 'rgba(0, 247, 255, 0.3)' } },
      axisLabel: { color: '#a0a0a0', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(0, 247, 255, 0.1)' } },
      axisTick: { lineStyle: { color: 'rgba(0, 247, 255, 0.3)' } }
    },
    series: series
  }
  
  chartInstance.setOption(option, true)
  
  // 清除旧的图例监听
  chartInstance.off('legendselectchanged')
  
  // 添加图例选择监听，动态更新 tooltip trigger
  chartInstance.on('legendselectchanged', function(params) {
    const selected = params.selected
    const count = Object.values(selected).filter(v => v).length
    selectedSeriesCount.value = count
    
    // 重新设置 tooltip trigger
    chartInstance.setOption({
      tooltip: {
        trigger: count > 1 ? 'axis' : 'item'
      }
    })
  })
}

/**
 * 处理窗口大小变化
 */
function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(async () => {
  await loadConfig()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.chart-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
}

.design-preview-link {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.design-preview-link a {
  background: linear-gradient(135deg, #00D4FF, #3B82F6);
  color: #0B1221;
  padding: 10px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
  transition: all 0.2s;
}

.design-preview-link a:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
}

.filter-panel {
  background: linear-gradient(135deg, rgba(10, 20, 40, 0.95) 0%, rgba(20, 40, 80, 0.9) 100%);
  border: 1px solid rgba(0, 247, 255, 0.2);
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.filter-row {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  color: #00f7ff;
  font-size: 12px;
  font-weight: 500;
}

.filter-select :deep(.el-input__wrapper) {
  background: rgba(0, 20, 40, 0.6);
  border: 1px solid rgba(0, 247, 255, 0.3);
  box-shadow: none;
}

.filter-select :deep(.el-input__inner) {
  color: #e0e0e0;
}

.filter-select :deep(.el-tag) {
  background: rgba(0, 247, 255, 0.2);
  border-color: rgba(0, 247, 255, 0.3);
  color: #00f7ff;
}

.time-periods-section {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  color: #e0e0e0;
  font-size: 14px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.time-periods-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.time-period-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 20, 40, 0.4);
  border: 1px solid rgba(0, 247, 255, 0.15);
  border-radius: 8px;
  flex-wrap: wrap;
}

.period-label {
  color: #a0a0a0;
  font-size: 12px;
  min-width: 60px;
}

.period-name-input {
  width: 100px;
}

.period-name-input :deep(.el-input__wrapper) {
  background: rgba(0, 20, 40, 0.6);
  border: 1px solid rgba(0, 247, 255, 0.3);
  box-shadow: none;
}

.period-name-input :deep(.el-input__inner) {
  color: #00f7ff;
  font-size: 12px;
}

.period-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.period-inputs :deep(.el-input__wrapper) {
  background: rgba(0, 20, 40, 0.6);
  border: 1px solid rgba(0, 247, 255, 0.3);
  box-shadow: none;
}

.period-inputs :deep(.el-input__inner) {
  color: #e0e0e0;
}

.separator {
  color: #a0a0a0;
}

.period-quick {
  display: flex;
  gap: 6px;
}

.period-quick .el-button {
  background: rgba(0, 20, 40, 0.6);
  border: 1px solid rgba(0, 247, 255, 0.3);
  color: #a0a0a0;
  font-size: 11px;
  padding: 4px 8px;
}

.period-quick .el-button:hover {
  border-color: #00f7ff;
  color: #00f7ff;
}

.period-actions {
  display: flex;
  gap: 6px;
  margin-left: auto;
}

.period-actions .el-button {
  padding: 6px 8px;
}

.combination-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 247, 255, 0.15);
}

.combination-actions .el-button {
  flex: 1;
  max-width: 200px;
}

.add-period-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.add-period-row .el-button {
  width: 100%;
}

.period-count-hint {
  color: #a0a0a0;
  font-size: 12px;
}

.action-row {
  display: flex;
  gap: 12px;
}

.action-row .el-button--primary {
  background: linear-gradient(135deg, #00f7ff 0%, #0080ff 100%);
  border: none;
  color: #000;
  font-weight: 600;
}

.action-row .el-button:not(.el-button--primary) {
  background: rgba(0, 20, 40, 0.6);
  border: 1px solid rgba(0, 247, 255, 0.3);
  color: #a0a0a0;
}

.action-row .el-button:not(.el-button--primary):hover {
  border-color: #00f7ff;
  color: #00f7ff;
}

.chart-panel {
  flex: 1;
  background: linear-gradient(135deg, rgba(10, 20, 40, 0.95) 0%, rgba(20, 40, 80, 0.9) 100%);
  border: 1px solid rgba(0, 247, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chart-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 247, 255, 0.15);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  color: #e0e0e0;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: opacity 0.3s ease, transform 0.2s ease;
  user-select: none;
}

.legend-item:hover {
  opacity: 0.7;
  transform: scale(1.05);
}

.legend-item.legend-hidden {
  opacity: 0.3;
}

.legend-item.legend-hidden:hover {
  opacity: 0.5;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  transition: opacity 0.3s ease;
}

.legend-label {
  color: #a0a0a0;
  font-size: 12px;
  transition: color 0.3s ease;
}

.chart-wrapper {
  flex: 1;
  min-height: 400px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 400px;
}

.empty-state :deep(.el-empty__description) {
  color: #a0a0a0;
}

.empty-state :deep(.el-button--primary) {
  background: linear-gradient(135deg, #00f7ff 0%, #0080ff 100%);
  border: none;
  color: #000;
}
</style>
