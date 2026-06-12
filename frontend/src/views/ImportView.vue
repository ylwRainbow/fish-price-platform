<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-decoration"></div>
      <h1 class="page-title">
        <span class="title-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        </span>
        批量导入
      </h1>
      <p class="page-subtitle">BATCH IMPORT // 上传Excel/CSV文件或手动批量录入</p>
    </div>

    <div class="content-grid">
      <div class="section-card">
        <div class="section-header">
          <div class="header-line"></div>
          <span class="header-text">文件上传 // FILE UPLOAD</span>
          <div class="header-line"></div>
        </div>
        <div class="upload-section">
          <p class="upload-desc">
            支持 Excel (.xlsx, .xls) 和 CSV 文件，统一由后端解析并校验
          </p>
          <div class="code-block">
            <div class="code-header">
              <span class="code-dot"></span>
              <span class="code-dot"></span>
              <span class="code-dot"></span>
              <span class="code-title">format.csv</span>
            </div>
            <pre class="code-content">鱼种名称,市场名称,价格,日期,货币,单位,价格类型,来源URL
鲈鱼,上海农产品中心,15.80,2024-01-15,CNY,kg,pond,
泥鳅,民众渔业,12.50,2024-01-16,CNY,kg,pond,</pre>
          </div>
          <div class="upload-actions">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :limit="1"
              accept=".xlsx,.xls,.csv"
              :on-change="handleFileChange"
              :show-file-list="false"
            >
              <template #trigger>
                <button class="cyber-btn primary">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                  选择文件
                </button>
              </template>
            </el-upload>
            <button class="cyber-btn success" :disabled="uploadLoading" @click="handleUpload">
              <svg v-if="!uploadLoading" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              <span v-if="uploadLoading">导入中...</span>
              <span v-else>开始导入</span>
            </button>
          </div>
          <div class="template-section">
            <span class="template-label">下载模板:</span>
            <button class="template-btn" @click="downloadExcelTemplate">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Excel模板
            </button>
            <button class="template-btn" @click="downloadCSVTemplate">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              CSV模板
            </button>
          </div>
        </div>
      </div>

      <div class="section-card result-card">
        <div class="section-header">
          <div class="header-line"></div>
          <span class="header-text">导入结果 // RESULT</span>
          <div class="header-line"></div>
        </div>
        <div v-if="importResult" class="result-section">
          <div class="result-icon" :class="importResult.failed === 0 ? 'success' : 'warning'">
            <svg v-if="importResult.failed === 0" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          </div>
          <div class="result-title">{{ importResult.failed === 0 ? '导入成功' : '部分导入成功' }}</div>
          <div class="result-stats">
            <div class="stat-item success">
              <span class="stat-value">{{ importResult.added }}</span>
              <span class="stat-label">成功</span>
            </div>
            <div class="stat-item error">
              <span class="stat-value">{{ importResult.failed }}</span>
              <span class="stat-label">失败</span>
            </div>
          </div>
          <div v-if="importResult.errors && importResult.errors.length > 0" class="error-list">
            <div class="error-header">错误详情</div>
            <div class="error-items">
              <p v-for="(err, idx) in importResult.errors" :key="idx" class="error-item">
                <span class="error-index">{{ idx + 1 }}</span>
                {{ err }}
              </p>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          <span>暂无导入结果</span>
        </div>
      </div>
    </div>

    <div class="section-card batch-section">
      <div class="section-header">
        <div class="header-line"></div>
        <span class="header-text">手动批量录入 // MANUAL ENTRY</span>
        <div class="header-line"></div>
      </div>
      <div class="batch-table-wrapper">
        <table class="batch-table">
          <thead>
            <tr>
              <th>鱼种</th>
              <th>市场</th>
              <th>价格</th>
              <th>单位</th>
              <th>日期</th>
              <th>类型</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in batchData" :key="index">
              <td>
                <el-select v-model="row.fish_id" size="small" class="table-select">
                  <el-option
                    v-for="fish in catalogStore.fishes"
                    :key="fish.id"
                    :label="fish.name"
                    :value="fish.id"
                  />
                </el-select>
              </td>
              <td>
                <el-select v-model="row.market_id" size="small" class="table-select">
                  <el-option
                    v-for="market in catalogStore.markets"
                    :key="market.id"
                    :label="market.name"
                    :value="market.id"
                  />
                </el-select>
              </td>
              <td>
                <el-input-number
                  v-model="row.price"
                  :precision="2"
                  :min="0"
                  size="small"
                  placeholder="价格"
                  class="table-input"
                />
              </td>
              <td>
                <el-select v-model="row.unit" size="small" class="table-select small">
                  <el-option label="元/kg" value="kg" />
                  <el-option label="元/斤" value="斤" />
                </el-select>
              </td>
              <td>
                <el-date-picker
                  v-model="row.ts"
                  type="date"
                  size="small"
                  value-format="YYYY-MM-DD"
                  class="table-date"
                />
              </td>
              <td>
                <el-select v-model="row.price_type" size="small" class="table-select small">
                  <el-option label="塘口价" value="pond" />
                  <el-option label="批发价" value="wholesale" />
                </el-select>
              </td>
              <td>
                <button class="row-delete" @click="removeRow(index)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="batch-actions">
        <button class="cyber-btn" @click="addRow">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          添加行
        </button>
        <button class="cyber-btn success" :disabled="batchLoading" @click="submitBatch">
          <svg v-if="!batchLoading" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
          <span v-if="batchLoading">提交中...</span>
          <span v-else>批量提交</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useCatalogStore } from '@/stores/catalog'
import { addPricesBatch, importPriceFile, getExcelTemplateUrl, getCSVTemplateUrl } from '@/api'

const catalogStore = useCatalogStore()

const uploadRef = ref(null)
const uploadLoading = ref(false)
const importResult = ref(null)
const batchLoading = ref(false)
const selectedFile = ref(null)

const batchData = ref([])

/**
 * 添加新行
 */
function addRow() {
  batchData.value.push({
    fish_id: catalogStore.fishes[0]?.id || null,
    market_id: catalogStore.markets[0]?.id || null,
    price: null,
    unit: 'kg',
    ts: new Date().toISOString().slice(0, 10),
    price_type: 'pond'
  })
}

/**
 * 删除指定行
 * @param {number} index - 行索引
 */
function removeRow(index) {
  batchData.value.splice(index, 1)
}

/**
 * 处理文件选择
 * @param {Object} file - 上传文件对象
 */
function handleFileChange(file) {
  selectedFile.value = file.raw
}

/**
 * 处理文件上传
 */
async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploadLoading.value = true
  try {
    const fileName = selectedFile.value.name.toLowerCase()
    
    if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls') || fileName.endsWith('.csv')) {
      const result = await importPriceFile(selectedFile.value)
      importResult.value = result
      ElMessage.success(`导入完成：成功 ${result.added} 条，失败 ${result.failed} 条`)
    } else {
      ElMessage.error('不支持的文件格式，请上传 Excel 或 CSV 文件')
    }
    
    uploadRef.value?.clearFiles()
    selectedFile.value = null
  } catch (e) {
    ElMessage.error('导入失败: ' + e.message)
  } finally {
    uploadLoading.value = false
  }
}

/**
 * 下载Excel模板
 */
function downloadExcelTemplate() {
  window.open(getExcelTemplateUrl(), '_blank')
}

/**
 * 下载CSV模板
 */
function downloadCSVTemplate() {
  window.open(getCSVTemplateUrl(), '_blank')
}

/**
 * 提交批量数据
 */
async function submitBatch() {
  const validData = batchData.value.filter(row => 
    row.fish_id && row.market_id && row.price && row.unit && row.ts
  )

  if (validData.length === 0) {
    ElMessage.warning('没有有效的数据行')
    return
  }

  batchLoading.value = true
  try {
    const result = await addPricesBatch(validData)
    ElMessage.success(`批量录入完成：成功 ${result.added} 条，失败 ${result.failed} 条`)
    batchData.value = []
    addRow()
  } catch (e) {
    ElMessage.error('提交失败: ' + e.message)
  } finally {
    batchLoading.value = false
  }
}

onMounted(() => {
  catalogStore.loadCatalog().then(() => {
    addRow()
  })
})
</script>

<style scoped>
.page-container {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
  min-height: calc(100vh - 70px);
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
  position: relative;
  padding: 32px;
}

.header-decoration {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-primary), transparent);
  box-shadow: 0 0 20px var(--color-primary);
}

.page-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 32px;
  font-weight: 900;
  color: var(--color-primary);
  text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
  letter-spacing: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin: 0 0 8px 0;
}

.title-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, rgba(0, 245, 255, 0.2) 0%, rgba(191, 0, 255, 0.2) 100%);
  border: 1px solid var(--color-primary);
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
}

.title-icon svg {
  width: 24px;
  height: 24px;
  stroke: var(--color-primary);
  filter: drop-shadow(0 0 4px var(--color-primary));
}

.page-subtitle {
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  color: var(--color-text-secondary);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin: 0;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.section-card {
  background: linear-gradient(180deg, rgba(13, 13, 26, 0.8) 0%, rgba(10, 10, 18, 0.6) 100%);
  border: 1px solid rgba(0, 245, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.section-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--color-primary), transparent);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 245, 255, 0.3), transparent);
}

.header-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-desc {
  color: var(--color-text-secondary);
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
}

.code-block {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(0, 245, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
}

.code-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(0, 245, 255, 0.1);
}

.code-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(0, 245, 255, 0.3);
}

.code-dot:nth-child(1) { background: rgba(255, 0, 102, 0.5); }
.code-dot:nth-child(2) { background: rgba(255, 170, 0, 0.5); }
.code-dot:nth-child(3) { background: rgba(0, 255, 136, 0.5); }

.code-title {
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-left: 8px;
}

.code-content {
  padding: 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--color-primary);
  line-height: 1.6;
  margin: 0;
  overflow-x: auto;
}

.upload-actions {
  display: flex;
  gap: 12px;
}

.cyber-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: rgba(0, 245, 255, 0.1);
  border: 1px solid rgba(0, 245, 255, 0.3);
  border-radius: 8px;
  color: var(--color-primary);
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cyber-btn:hover {
  background: rgba(0, 245, 255, 0.15);
  border-color: var(--color-primary);
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
}

.cyber-btn.primary {
  background: linear-gradient(135deg, rgba(0, 245, 255, 0.2) 0%, rgba(191, 0, 255, 0.2) 100%);
  border-color: var(--color-primary);
}

.cyber-btn.success {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 245, 255, 0.2) 100%);
  border-color: var(--color-success);
  color: var(--color-success);
}

.cyber-btn.success:hover {
  box-shadow: 0 0 30px rgba(0, 255, 136, 0.4);
}

.cyber-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.template-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 245, 255, 0.1);
}

.template-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.template-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: var(--color-text-secondary);
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-btn:hover {
  background: rgba(0, 245, 255, 0.1);
  border-color: rgba(0, 245, 255, 0.3);
  color: var(--color-primary);
}

.result-card {
  display: flex;
  flex-direction: column;
}

.result-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.result-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-bottom: 16px;
}

.result-icon.success {
  background: rgba(0, 255, 136, 0.1);
  border: 2px solid var(--color-success);
  box-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
}

.result-icon.success svg {
  stroke: var(--color-success);
}

.result-icon.warning {
  background: rgba(255, 170, 0, 0.1);
  border: 2px solid var(--color-warning);
  box-shadow: 0 0 30px rgba(255, 170, 0, 0.3);
}

.result-icon.warning svg {
  stroke: var(--color-warning);
}

.result-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 20px;
}

.result-stats {
  display: flex;
  gap: 32px;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 28px;
  font-weight: 900;
}

.stat-item.success .stat-value {
  color: var(--color-success);
  text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
}

.stat-item.error .stat-value {
  color: var(--color-error);
  text-shadow: 0 0 20px rgba(255, 0, 102, 0.5);
}

.stat-label {
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.error-list {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 0, 102, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.error-header {
  padding: 10px 16px;
  background: rgba(255, 0, 102, 0.1);
  border-bottom: 1px solid rgba(255, 0, 102, 0.2);
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-error);
  letter-spacing: 1px;
}

.error-items {
  max-height: 150px;
  overflow-y: auto;
  padding: 12px 16px;
}

.error-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--color-text-secondary);
  margin: 4px 0;
}

.error-index {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 0, 102, 0.2);
  border-radius: 4px;
  font-size: 10px;
  color: var(--color-error);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--color-text-secondary);
  gap: 16px;
}

.empty-state svg {
  opacity: 0.3;
}

.empty-state span {
  font-size: 14px;
}

.batch-section {
  margin-top: 0;
}

.batch-table-wrapper {
  overflow-x: auto;
}

.batch-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.batch-table th {
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(0, 245, 255, 0.2);
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-primary);
  text-align: left;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.batch-table td {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 245, 255, 0.1);
  vertical-align: middle;
}

.batch-table tr:hover td {
  background: rgba(0, 245, 255, 0.02);
}

.table-select,
.table-input,
.table-date {
  width: 100%;
}

.table-select.small {
  width: 100px;
}

.row-delete {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 0, 102, 0.1);
  border: 1px solid rgba(255, 0, 102, 0.3);
  border-radius: 6px;
  color: var(--color-error);
  cursor: pointer;
  transition: all 0.3s ease;
}

.row-delete:hover {
  background: rgba(255, 0, 102, 0.2);
  border-color: var(--color-error);
  box-shadow: 0 0 15px rgba(255, 0, 102, 0.3);
}

.batch-actions {
  display: flex;
  gap: 16px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 245, 255, 0.1);
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .batch-table th,
  .batch-table td {
    padding: 10px 12px;
  }
}

@media (max-width: 640px) {
  .page-container {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
    flex-direction: column;
    gap: 12px;
  }
  
  .upload-actions {
    flex-direction: column;
  }
  
  .cyber-btn {
    width: 100%;
    justify-content: center;
  }
  
  .template-section {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .batch-actions {
    flex-direction: column;
  }
  
  .result-stats {
    gap: 20px;
  }
  
  .stat-value {
    font-size: 24px;
  }
}
</style>
