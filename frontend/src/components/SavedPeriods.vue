<template>
  <div class="saved-periods">
    <!-- 单个时间段操作按钮已移至 ChartView，这里只保留对话框 -->
    
    <!-- 保存单个时间段对话框 -->
    <el-dialog
      v-model="saveDialogVisible"
      title="保存时间段"
      width="400px"
    >
      <el-form :model="saveForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="saveForm.name" :placeholder="defaultName" />
        </el-form-item>
        <el-form-item label="时间段">
          <span class="period-display">{{ savePeriodDisplay }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePeriod" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 保存组合对话框 -->
    <el-dialog
      v-model="saveCombinationDialogVisible"
      title="保存时间段组合"
      width="500px"
    >
      <el-form :model="saveCombinationForm" label-width="80px">
        <el-form-item label="组合名称">
          <el-input v-model="saveCombinationForm.name" placeholder="例如：2024 年价格对比" />
        </el-form-item>
        <el-form-item label="时间段">
          <el-table :data="saveCombinationForm.periods" style="width: 100%" max-height="300">
            <el-table-column prop="name" label="名称" />
            <el-table-column label="时间段">
              <template #default="scope">
                {{ scope.row.start }} 至 {{ scope.row.end }}
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveCombinationDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCombination" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 加载对话框 -->
    <el-dialog
      v-model="loadDialogVisible"
      title="加载已保存的时间段"
      width="600px"
    >
      <el-tabs v-model="activeTab">
        <el-tab-pane label="单个时间段" name="single">
          <el-tabs v-model="singleType">
            <el-tab-pane label="农历" name="lunar">
              <el-table :data="lunarPeriods" style="width: 100%">
                <el-table-column prop="name" label="名称" />
                <el-table-column prop="start_date" label="开始日期" />
                <el-table-column prop="end_date" label="结束日期" />
                <el-table-column label="操作" width="180" align="center">
                  <template #default="scope">
                    <div class="action-buttons">
                      <el-button size="small" type="primary" @click="loadSinglePeriod('lunar', scope.row)">
                        <el-icon><Download /></el-icon>
                        加载
                      </el-button>
                      <el-button size="small" type="danger" @click="deletePeriod('lunar', scope.row.id)">
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="公历" name="solar">
              <el-table :data="solarPeriods" style="width: 100%">
                <el-table-column prop="name" label="名称" />
                <el-table-column prop="start_date" label="开始日期" />
                <el-table-column prop="end_date" label="结束日期" />
                <el-table-column label="操作" width="180" align="center">
                  <template #default="scope">
                    <div class="action-buttons">
                      <el-button size="small" type="primary" @click="loadSinglePeriod('solar', scope.row)">
                        <el-icon><Download /></el-icon>
                        加载
                      </el-button>
                      <el-button size="small" type="danger" @click="deletePeriod('solar', scope.row.id)">
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-tab-pane>
        <el-tab-pane label="时间段组合" name="combination">
          <el-table :data="combinationPeriods" style="width: 100%">
            <el-table-column prop="name" label="组合名称" />
            <el-table-column label="包含时间段" width="300">
              <template #default="scope">
                <div v-for="(p, i) in scope.row.periods" :key="i" style="font-size: 12px; margin-bottom: 4px;">
                  {{ p.name }}: {{ p.start }} 至 {{ p.end }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center">
              <template #default="scope">
                <div class="action-buttons">
                  <el-button size="small" type="primary" @click="loadCombinationPeriod(scope.row)">
                    <el-icon><Download /></el-icon>
                    加载
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteCombination(scope.row.id)">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="loadDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  currentPeriod: {
    type: Object,
    default: null
  },
  calendarType: {
    type: String,
    default: 'solar'
  }
})

const emit = defineEmits(['load'])

const saveDialogVisible = ref(false)
const saveCombinationDialogVisible = ref(false)
const loadDialogVisible = ref(false)
const saving = ref(false)
const activeTab = ref('single')
const singleType = ref('lunar')

const saveForm = ref({
  name: ''
})

const saveCombinationForm = ref({
  name: '',
  periods: []
})

const lunarPeriods = ref([])
const solarPeriods = ref([])
const combinationPeriods = ref([])

// 当前回调函数
let currentLoadCallback = null

const defaultName = computed(() => {
  if (!props.currentPeriod && !saveForm.value.tempData) return ''
  const data = saveForm.value.tempData || props.currentPeriod
  return data.name || `时间段 (${data.start} ~ ${data.end})`
})

const savePeriodDisplay = computed(() => {
  const data = saveForm.value.tempData || props.currentPeriod
  if (!data) return ''
  return `${data.start} 至 ${data.end}`
})

// 显示保存对话框
const showSaveDialog = () => {
  saveForm.value.name = ''
  saveDialogVisible.value = true
}

// 显示保存组合对话框
const showSaveCombinationDialog = (periods) => {
  saveCombinationForm.value.name = ''
  saveCombinationForm.value.periods = periods
  saveCombinationDialogVisible.value = true
}

// 显示加载对话框
const showLoadDialog = async () => {
  loadDialogVisible.value = true
  await loadPeriods('lunar')
  await loadPeriods('solar')
  await loadCombinationPeriods()
}

// 监听来自 ChartView 的事件
const handleSavePeriod = (event) => {
  const { name, start, end, index } = event.detail
  saveForm.value.name = name || ''
  saveForm.value.tempData = { start, end, index }
  saveDialogVisible.value = true
}

const handleLoadPeriod = (event) => {
  const { onSelect } = event.detail
  currentLoadCallback = onSelect
  showLoadDialog()
}

const handleSaveCombination = (event) => {
  const { periods } = event.detail
  showSaveCombinationDialog(periods)
}

const handleLoadCombination = (event) => {
  const { onSelect } = event.detail
  currentLoadCallback = onSelect
  activeTab.value = 'combination'
  showLoadDialog()
}

// 添加事件监听
onMounted(() => {
  window.addEventListener('save-period', handleSavePeriod)
  window.addEventListener('load-period', handleLoadPeriod)
  window.addEventListener('save-combination', handleSaveCombination)
  window.addEventListener('load-combination', handleLoadCombination)
  
  // 初始化加载列表
  loadPeriods('lunar')
  loadPeriods('solar')
  loadCombinationPeriods()
})

// 移除事件监听
onUnmounted(() => {
  window.removeEventListener('save-period', handleSavePeriod)
  window.removeEventListener('load-period', handleLoadPeriod)
  window.removeEventListener('save-combination', handleSaveCombination)
  window.removeEventListener('load-combination', handleLoadCombination)
})

// 加载时间段列表
const loadPeriods = async (type) => {
  try {
    const res = await fetch(`/api/saved-periods?type=${type}&limit=20`)
    const data = await res.json()
    if (data.success) {
      if (type === 'lunar') {
        lunarPeriods.value = data.data
      } else {
        solarPeriods.value = data.data
      }
    }
  } catch (e) {
    console.error('加载已保存时间段失败:', e)
  }
}

// 保存单个时间段
const savePeriod = async () => {
  saving.value = true
  try {
    // 使用临时数据或 currentPeriod
    const periodData = saveForm.value.tempData || props.currentPeriod
    if (!periodData) {
      ElMessage.error('没有可保存的时间段')
      return
    }
    
    const res = await fetch('/api/saved-periods', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: props.calendarType,
        name: saveForm.value.name || periodData.name || '时间段',
        start_date: periodData.start,
        end_date: periodData.end
      })
    })
    
    const data = await res.json()
    if (data.success) {
      ElMessage.success('保存成功')
      saveDialogVisible.value = false
      saveForm.value.tempData = null
      // 刷新列表
      await loadPeriods(props.calendarType)
    } else {
      ElMessage.error(data.error || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败：' + e.message)
  } finally {
    saving.value = false
  }
}

// 保存时间段组合
const saveCombination = async () => {
  if (!saveCombinationForm.value.periods || saveCombinationForm.value.periods.length === 0) {
    ElMessage.error('没有可保存的时间段')
    return
  }
  
  saving.value = true
  try {
    const params = new URLSearchParams({
      type: props.calendarType,
      name: saveCombinationForm.value.name || '时间段组合',
      periods: JSON.stringify(saveCombinationForm.value.periods)
    })
    
    const res = await fetch('/api/saved-period-combinations?' + params.toString(), {
      method: 'POST'
    })
    
    const data = await res.json()
    if (data.success) {
      ElMessage.success('组合保存成功')
      saveCombinationDialogVisible.value = false
      await loadCombinationPeriods()
    } else {
      ElMessage.error(data.error || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败：' + e.message)
  } finally {
    saving.value = false
  }
}

// 加载单个时间段
const loadSinglePeriod = (type, period) => {
  if (currentLoadCallback) {
    currentLoadCallback({
      name: period.name,
      start: period.start_date,
      end: period.end_date
    })
    currentLoadCallback = null
  } else {
    emit('load', {
      type,
      name: period.name,
      start: period.start_date,
      end: period.end_date
    })
  }
  loadDialogVisible.value = false
}

// 加载组合时间段
const loadCombinationPeriod = (combination) => {
  if (currentLoadCallback) {
    currentLoadCallback(combination.periods)
    currentLoadCallback = null
  }
  loadDialogVisible.value = false
}

// 删除单个时间段
const deletePeriod = async (type, id) => {
  try {
    const res = await fetch(`/api/saved-periods/${id}?type=${type}`, {
      method: 'DELETE'
    })
    
    if (res.ok) {
      ElMessage.success('删除成功')
      await loadPeriods(type)
    } else {
      ElMessage.error('删除失败')
    }
  } catch (e) {
    ElMessage.error('删除失败：' + e.message)
  }
}

// 加载组合列表
const loadCombinationPeriods = async () => {
  try {
    const res = await fetch('/api/saved-period-combinations?type=' + props.calendarType)
    const data = await res.json()
    if (data.success) {
      combinationPeriods.value = data.data || []
    }
  } catch (e) {
    console.error('加载组合列表失败:', e)
  }
}

// 删除组合
const deleteCombination = async (id) => {
  try {
    const res = await fetch(`/api/saved-period-combinations/${id}`, {
      method: 'DELETE'
    })
    
    if (res.ok) {
      ElMessage.success('删除成功')
      await loadCombinationPeriods()
    } else {
      ElMessage.error('删除失败')
    }
  } catch (e) {
    ElMessage.error('删除失败：' + e.message)
  }
}


</script>

<style scoped>
.saved-periods {
  display: inline-flex;
  gap: 8px;
}

.period-display {
  color: #00f7ff;
  font-weight: 500;
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 6px;
  justify-content: center;
  align-items: center;
}

.action-buttons .el-button {
  padding: 4px 10px;
  font-size: 12px;
}

.action-buttons .el-button .el-icon {
  margin-right: 4px;
}

:deep(.el-table) {
  background: rgba(0, 20, 40, 0.4);
  border-radius: 4px;
}

:deep(.el-table th) {
  background: rgba(0, 247, 255, 0.1);
  color: #00f7ff;
  font-weight: 500;
  font-size: 13px;
}

:deep(.el-table td) {
  background: transparent;
  color: #e0e0e0;
  font-size: 12px;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: rgba(0, 20, 40, 0.2);
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background: rgba(0, 247, 255, 0.1);
}

:deep(.el-tabs__item) {
  font-size: 13px;
}

:deep(.el-tabs__item.is-active) {
  color: #00f7ff;
}

:deep(.el-tabs__active-bar) {
  background: #00f7ff;
}
</style>
