<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-decoration"></div>
      <h1 class="page-title">
        <span class="title-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
        </span>
        价格录入
      </h1>
      <p class="page-subtitle">PRICE ENTRY // 录入单条鱼价数据</p>
    </div>

    <div class="content-grid">
      <div class="main-section">
        <div class="section-card">
          <div class="section-header">
            <div class="header-line"></div>
            <span class="header-text">新增价格记录 // NEW RECORD</span>
            <div class="header-line"></div>
          </div>
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-position="top"
            @submit.prevent="handleSubmit"
            class="cyber-form"
          >
            <div class="form-grid">
              <div class="form-item">
                <label class="form-label">鱼种 // FISH</label>
                <el-select v-model="form.fish_id" placeholder="选择鱼种" class="cyber-select">
                  <el-option
                    v-for="fish in catalogStore.fishes"
                    :key="fish.id"
                    :label="fish.name"
                    :value="fish.id"
                  />
                </el-select>
              </div>
              <div class="form-item">
                <label class="form-label">市场 // MARKET</label>
                <el-select v-model="form.market_id" placeholder="选择市场" class="cyber-select">
                  <el-option
                    v-for="market in catalogStore.markets"
                    :key="market.id"
                    :label="market.name"
                    :value="market.id"
                  />
                </el-select>
              </div>
              <div class="form-item">
                <label class="form-label">价格 (元/斤) // PRICE</label>
                <el-input-number
                  v-model="form.price"
                  :precision="2"
                  :min="0"
                  placeholder="输入价格"
                  class="cyber-input-number"
                />
              </div>
              <div class="form-item">
                <label class="form-label">日期 // DATE</label>
                <el-date-picker
                  v-model="form.ts"
                  type="date"
                  placeholder="选择日期"
                  value-format="YYYY-MM-DD"
                  class="cyber-datepicker"
                />
              </div>
              <div class="form-item">
                <label class="form-label">价格类型 // TYPE</label>
                <div class="cyber-radio-group">
                  <button 
                    class="cyber-radio" 
                    :class="{ active: form.price_type === 'pond' }"
                    @click="form.price_type = 'pond'"
                  >塘口价</button>
                  <button 
                    class="cyber-radio" 
                    :class="{ active: form.price_type === 'wholesale' }"
                    @click="form.price_type = 'wholesale'"
                  >批发价</button>
                  <button 
                    class="cyber-radio" 
                    :class="{ active: form.price_type === 'retail' }"
                    @click="form.price_type = 'retail'"
                  >零售价</button>
                </div>
              </div>
              <div class="form-item">
                <label class="form-label">来源 // SOURCE</label>
                <el-input v-model="form.source_url" placeholder="如: 民众渔业" class="cyber-input" />
              </div>
            </div>
            <div class="form-actions">
              <button type="submit" class="cyber-btn primary" @click="handleSubmit" :disabled="loading">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                <span v-if="loading">提交中...</span>
                <span v-else>提交记录</span>
              </button>
              <button type="button" class="cyber-btn secondary" @click="resetForm">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
                重置表单
              </button>
            </div>
          </el-form>
        </div>
      </div>

      <div class="side-section">
        <div class="section-card recent-card">
          <div class="section-header">
            <div class="header-line"></div>
            <span class="header-text">最近录入 // RECENT</span>
            <div class="header-line"></div>
          </div>
          <div class="recent-list" v-if="recentRecords.length > 0">
            <div v-for="record in recentRecords" :key="record.id" class="recent-item">
              <div class="recent-info">
                <span class="recent-name">{{ record.fishName }} - {{ record.marketName }}</span>
                <span class="recent-date">{{ record.ts }}</span>
              </div>
              <div class="recent-price">{{ record.price.toFixed(2) }}</div>
            </div>
          </div>
          <div v-else class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
            <span>暂无录入记录</span>
          </div>
        </div>
      </div>
    </div>

    <div class="section-card quick-section">
      <div class="section-header">
        <div class="header-line"></div>
        <span class="header-text">快速录入 // QUICK ENTRY</span>
        <div class="header-line"></div>
      </div>
      <div class="quick-grid">
        <div
          v-for="fish in catalogStore.fishes"
          :key="fish.id"
          class="quick-item"
        >
          <div class="quick-fish-name">{{ fish.name }}</div>
          <div class="quick-fields">
            <el-select v-model="quickEntry[fish.id].market_id" size="small" class="quick-select">
              <el-option
                v-for="market in catalogStore.markets"
                :key="market.id"
                :label="market.name"
                :value="market.id"
              />
            </el-select>
            <el-input-number
              v-model="quickEntry[fish.id].price"
              :precision="2"
              :min="0"
              size="small"
              placeholder="价格"
              class="quick-price"
            />
            <el-date-picker
              v-model="quickEntry[fish.id].ts"
              type="date"
              size="small"
              value-format="YYYY-MM-DD"
              class="quick-date"
            />
            <button
              class="quick-save"
              :class="{ saved: quickEntry[fish.id].saved }"
              :disabled="quickEntry[fish.id].loading"
              @click="saveQuickEntry(fish.id)"
            >
              <svg v-if="quickEntry[fish.id].saved" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              <span v-else-if="quickEntry[fish.id].loading">...</span>
              <span v-else>保存</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useCatalogStore } from '@/stores/catalog'
import { addPrice } from '@/api'

const catalogStore = useCatalogStore()

const formRef = ref(null)
const loading = ref(false)
const recentRecords = ref([])

const form = reactive({
  fish_id: null,
  market_id: null,
  price: null,
  ts: new Date().toISOString().slice(0, 10),
  price_type: 'pond',
  source_url: ''
})

const rules = {
  fish_id: [{ required: true, message: '请选择鱼种', trigger: 'change' }],
  market_id: [{ required: true, message: '请选择市场', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  ts: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

const quickEntry = reactive({})

watch(() => catalogStore.fishes, (fishes) => {
  if (fishes.length > 0) {
    fishes.forEach(fish => {
      if (!quickEntry[fish.id]) {
        quickEntry[fish.id] = {
          market_id: catalogStore.markets[0]?.id || null,
          price: null,
          ts: new Date().toISOString().slice(0, 10),
          loading: false,
          saved: false
        }
      }
    })
  }
}, { immediate: true })

/**
 * 提交表单数据
 */
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const result = await addPrice(form)
    if (result.success) {
      ElMessage.success('价格录入成功！')
      
      const fish = catalogStore.getFishById(form.fish_id)
      const market = catalogStore.getMarketById(form.market_id)
      recentRecords.value.unshift({
        id: Date.now(),
        fishName: fish?.name,
        marketName: market?.name,
        price: form.price,
        ts: form.ts
      })
      
      if (recentRecords.value.length > 10) {
        recentRecords.value.pop()
      }
      
      resetForm()
    } else {
      ElMessage.error('录入失败: ' + (result.detail || '未知错误'))
    }
  } catch (e) {
    ElMessage.error('网络错误: ' + e.message)
  } finally {
    loading.value = false
  }
}

/**
 * 重置表单
 */
function resetForm() {
  formRef.value?.resetFields()
  form.price = null
  form.source_url = ''
  form.ts = new Date().toISOString().slice(0, 10)
}

/**
 * 保存快速录入项
 * @param {number} fishId - 鱼种ID
 */
async function saveQuickEntry(fishId) {
  const entry = quickEntry[fishId]
  if (!entry.price || !entry.ts) {
    ElMessage.warning('请填写价格和日期')
    return
  }

  entry.loading = true
  try {
    const result = await addPrice({
      fish_id: fishId,
      market_id: entry.market_id,
      price: entry.price,
      ts: entry.ts
    })
    if (result.success) {
      entry.saved = true
      ElMessage.success('保存成功')
      setTimeout(() => {
        entry.saved = false
      }, 2000)
    }
  } catch (e) {
    ElMessage.error('保存失败: ' + e.message)
  } finally {
    entry.loading = false
  }
}

onMounted(() => {
  catalogStore.loadCatalog()
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
  grid-template-columns: 1fr 320px;
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

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-family: 'Rajdhani', sans-serif;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-secondary);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.cyber-select,
.cyber-input-number,
.cyber-datepicker,
.cyber-input {
  width: 100%;
}

.cyber-radio-group {
  display: flex;
  gap: 8px;
}

.cyber-radio {
  flex: 1;
  padding: 10px 16px;
  background: rgba(0, 245, 255, 0.05);
  border: 1px solid rgba(0, 245, 255, 0.2);
  border-radius: 8px;
  color: var(--color-text-secondary);
  font-family: 'Rajdhani', sans-serif;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cyber-radio:hover {
  background: rgba(0, 245, 255, 0.1);
  border-color: rgba(0, 245, 255, 0.4);
}

.cyber-radio.active {
  background: rgba(0, 245, 255, 0.15);
  border-color: var(--color-primary);
  color: var(--color-primary);
  box-shadow: 0 0 15px rgba(0, 245, 255, 0.2);
}

.form-actions {
  display: flex;
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 245, 255, 0.1);
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

.cyber-btn.primary:hover {
  box-shadow: 0 0 30px rgba(0, 245, 255, 0.4);
}

.cyber-btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  color: var(--color-text-secondary);
}

.cyber-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.4);
  color: var(--color-text-primary);
}

.cyber-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.recent-card {
  height: 100%;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 245, 255, 0.1);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.recent-item:hover {
  border-color: rgba(0, 245, 255, 0.3);
  background: rgba(0, 245, 255, 0.02);
}

.recent-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recent-name {
  font-family: 'Rajdhani', sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.recent-date {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.recent-price {
  font-family: 'Orbitron', sans-serif;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-primary);
  text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--color-text-secondary);
  gap: 12px;
}

.empty-state svg {
  opacity: 0.3;
}

.empty-state span {
  font-size: 13px;
}

.quick-section {
  margin-top: 0;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 245, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.quick-item:hover {
  border-color: rgba(0, 245, 255, 0.3);
  background: rgba(0, 245, 255, 0.02);
}

.quick-fish-name {
  font-family: 'Orbitron', sans-serif;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 1px;
}

.quick-fields {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-select {
  width: 100px;
}

.quick-price {
  width: 90px;
}

.quick-date {
  width: 120px;
}

.quick-save {
  padding: 8px 16px;
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 6px;
  color: var(--color-success);
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.quick-save:hover {
  background: rgba(0, 255, 136, 0.2);
  border-color: var(--color-success);
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.3);
}

.quick-save.saved {
  background: rgba(0, 255, 136, 0.2);
  border-color: var(--color-success);
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.3);
}

.quick-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-grid {
    grid-template-columns: 1fr;
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
  
  .quick-fields {
    flex-direction: column;
    align-items: stretch;
  }
  
  .quick-select,
  .quick-price,
  .quick-date {
    width: 100%;
  }
  
  .quick-save {
    width: 100%;
    justify-content: center;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .cyber-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
