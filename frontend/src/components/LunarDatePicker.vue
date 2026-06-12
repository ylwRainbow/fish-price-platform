<template>
  <el-popover
    v-model:visible="visible"
    placement="bottom-start"
    :width="320"
    trigger="click"
  >
    <template #reference>
      <el-input
        v-model="inputValue"
        :placeholder="placeholder"
        :size="size"
        style="width: 125px"
        @input="handleInputChange"
        @blur="handleBlur"
      >
        <template #suffix>
          <el-icon style="cursor: pointer;"><Calendar /></el-icon>
        </template>
      </el-input>
    </template>
    <div class="lunar-picker">
      <div class="lunar-picker-header">
        <el-button link @click="prevYear">
          <el-icon><DArrowLeft /></el-icon>
        </el-button>
        <el-button link @click="prevMonth">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <span class="lunar-picker-title">{{ currentYear }}年 {{ lunarMonthTitle }}</span>
        <el-button link @click="nextMonth">
          <el-icon><ArrowRight /></el-icon>
        </el-button>
        <el-button link @click="nextYear">
          <el-icon><DArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="lunar-picker-body">
        <div class="lunar-days-header">
          <span v-for="day in ['一', '二', '三', '四', '五', '六', '日']" :key="day">{{ day }}</span>
        </div>
        <div class="lunar-days">
          <div
            v-for="(day, index) in lunarDays"
            :key="index"
            class="lunar-day"
            :class="{
              'other-month': day.otherMonth,
              'selected': isSelected(day),
              'today': isToday(day),
              'festival': day.festival
            }"
            @click="selectDay(day)"
          >
            <span class="solar-day">{{ day.solarDay }}</span>
            <span class="lunar-day-text">{{ day.lunarDayText }}</span>
          </div>
        </div>
      </div>
    </div>
  </el-popover>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Solar, Lunar } from 'lunar-javascript'
import { DArrowLeft, ArrowLeft, ArrowRight, DArrowRight, Calendar } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '选择日期'
  },
  size: {
    type: String,
    default: 'small'
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const inputValue = ref('')

/**
 * 监听外部值变化，更新输入框显示
 */
watch(() => props.modelValue, (newVal) => {
  inputValue.value = newVal || ''
}, { immediate: true })

/**
 * 农历月份标题
 */
const lunarMonthTitle = computed(() => {
  const lunar = Lunar.fromDate(new Date(currentYear.value, currentMonth.value - 1, 1))
  return lunar.getMonthInChinese() + '月'
})

/**
 * 计算当前月份的所有日期
 */
const lunarDays = computed(() => {
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value - 1, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value, 0)
  
  let startWeekday = firstDay.getDay()
  if (startWeekday === 0) startWeekday = 7
  
  const prevMonthLastDay = new Date(currentYear.value, currentMonth.value - 1, 0)
  for (let i = startWeekday - 1; i > 0; i--) {
    const date = new Date(prevMonthLastDay)
    date.setDate(prevMonthLastDay.getDate() - i + 1)
    days.push(createDayInfo(date, true))
  }
  
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(currentYear.value, currentMonth.value - 1, i)
    days.push(createDayInfo(date, false))
  }
  
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    const date = new Date(currentYear.value, currentMonth.value, i)
    days.push(createDayInfo(date, true))
  }
  
  return days
})

/**
 * 创建日期信息对象
 */
function createDayInfo(date, otherMonth) {
  const solar = Solar.fromDate(date)
  const lunar = solar.getLunar()
  
  const festivals = lunar.getFestivals()
  const solarTerms = lunar.getJieQi()
  
  let lunarDayText = lunar.getDayInChinese()
  if (lunar.getDay() === 1) {
    lunarDayText = lunar.getMonthInChinese() + '月'
  }
  
  if (festivals.length > 0) {
    lunarDayText = festivals[0]
  } else if (solarTerms) {
    lunarDayText = solarTerms
  }
  
  return {
    date: date,
    year: date.getFullYear(),
    month: date.getMonth() + 1,
    solarDay: date.getDate(),
    lunarYear: lunar.getYear(),
    lunarMonth: lunar.getMonth(),
    lunarDay: lunar.getDay(),
    lunarDayText: lunarDayText,
    otherMonth: otherMonth,
    festival: festivals.length > 0 || !!solarTerms,
    solarDate: solar.toString()
  }
}

/**
 * 选择日期
 */
function selectDay(day) {
  if (day.otherMonth) return
  
  const solarDate = day.date
  const year = solarDate.getFullYear()
  const month = String(solarDate.getMonth() + 1).padStart(2, '0')
  const dayNum = String(solarDate.getDate()).padStart(2, '0')
  const solarStr = `${year}-${month}-${dayNum}`
  
  const solar = Solar.fromYmd(year, parseInt(month), parseInt(dayNum))
  const lunar = solar.getLunar()
  
  const lunarYear = lunar.getYear()
  const lunarMonth = String(lunar.getMonth()).padStart(2, '0')
  const lunarDay = String(lunar.getDay()).padStart(2, '0')
  const lunarStr = `${lunarYear}-${lunarMonth}-${lunarDay}`
  
  inputValue.value = lunarStr
  emit('update:modelValue', solarStr)
  visible.value = false
}

/**
 * 是否选中
 */
function isSelected(day) {
  if (!props.modelValue || day.otherMonth) return false
  const parts = props.modelValue.split('-')
  if (parts.length !== 3) return false
  
  const year = parseInt(parts[0])
  const month = parseInt(parts[1])
  const dayNum = parseInt(parts[2])
  
  return day.year === year &&
         day.month === month &&
         day.solarDay === dayNum
}

/**
 * 是否今天
 */
function isToday(day) {
  const today = new Date()
  return day.year === today.getFullYear() &&
         day.month === today.getMonth() + 1 &&
         day.solarDay === today.getDate()
}

/**
 * 上一月
 */
function prevMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

/**
 * 下一月
 */
function nextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

/**
 * 上一年
 */
function prevYear() {
  currentYear.value--
}

/**
 * 下一年
 */
function nextYear() {
  currentYear.value++
}

/**
 * 处理输入变化
 */
function handleInputChange(value) {
  const cleaned = value.replace(/[^\d-]/g, '')
  if (cleaned !== value) {
    inputValue.value = cleaned
  }
}

/**
 * 处理失焦事件 - 解析农历日期并转换为阳历
 */
function handleBlur() {
  const value = inputValue.value.trim()
  if (!value) {
    emit('update:modelValue', '')
    return
  }
  
  const parts = value.split('-')
  if (parts.length !== 3) {
    ElMessage.warning('日期格式错误，请输入 YYYY-MM-DD 格式')
    inputValue.value = props.modelValue || ''
    return
  }
  
  const lunarYear = parseInt(parts[0])
  const lunarMonth = parseInt(parts[1])
  const lunarDay = parseInt(parts[2])
  
  if (isNaN(lunarYear) || isNaN(lunarMonth) || isNaN(lunarDay)) {
    ElMessage.warning('日期格式错误，请输入有效的数字')
    inputValue.value = props.modelValue || ''
    return
  }
  
  if (lunarMonth < 1 || lunarMonth > 12) {
    ElMessage.warning('月份必须在 1-12 之间')
    inputValue.value = props.modelValue || ''
    return
  }
  
  if (lunarDay < 1 || lunarDay > 30) {
    ElMessage.warning('日期必须在 1-30 之间')
    inputValue.value = props.modelValue || ''
    return
  }
  
  try {
    const lunar = Lunar.fromYmd(lunarYear, lunarMonth, lunarDay)
    const solar = lunar.getSolar()
    
    const solarYear = solar.getYear()
    const solarMonth = String(solar.getMonth()).padStart(2, '0')
    const solarDay = String(solar.getDay()).padStart(2, '0')
    const solarStr = `${solarYear}-${solarMonth}-${solarDay}`
    
    const formattedLunar = `${lunarYear}-${String(lunarMonth).padStart(2, '0')}-${String(lunarDay).padStart(2, '0')}`
    inputValue.value = formattedLunar
    emit('update:modelValue', solarStr)
    
    currentYear.value = solarYear
    currentMonth.value = parseInt(solarMonth)
  } catch (e) {
    ElMessage.warning('无效的农历日期，请检查输入')
    inputValue.value = props.modelValue || ''
  }
}
</script>

<style scoped>
.lunar-picker {
  font-size: 12px;
}

.lunar-picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 8px;
}

.lunar-picker-title {
  font-weight: 500;
  color: var(--color-text-primary);
}

.lunar-days-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 12px;
  margin-bottom: 4px;
}

.lunar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.lunar-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4px 0;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  min-height: 40px;
}

.lunar-day:hover:not(.other-month) {
  background: var(--color-bg-base);
}

.lunar-day.other-month {
  opacity: 0.3;
}

.lunar-day.selected {
  background: var(--el-color-primary);
  color: #fff;
}

.lunar-day.today {
  border: 1px solid var(--el-color-primary);
}

.lunar-day.festival .lunar-day-text {
  color: var(--el-color-danger);
}

.lunar-day.selected.festival .lunar-day-text {
  color: #fff;
}

.solar-day {
  font-size: 14px;
  font-weight: 500;
}

.lunar-day-text {
  font-size: 10px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.lunar-day.selected .lunar-day-text {
  color: rgba(255, 255, 255, 0.8);
}
</style>
