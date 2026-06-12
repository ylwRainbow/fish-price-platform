<template>
  <div class="design-preview">
    <div class="preview-header">
      <h1>🎨 UI 设计方案预览</h1>
      <p>鱼价数据平台 - 整体 UI 风格选择</p>
      <div class="theme-selector">
        <button 
          v-for="theme in themes" 
          :key="theme.id"
          :class="['theme-btn', { active: currentTheme === theme.id }]"
          @click="currentTheme = theme.id"
        >
          {{ theme.name }}
        </button>
      </div>
    </div>

    <div class="preview-container">
      <!-- 方案一：深海科技风 -->
      <div v-show="currentTheme === 'deep-sea'" class="preview-panel deep-sea-theme">
        <div class="panel-header">
          <h2>方案一：深海科技风</h2>
          <span class="badge">推荐</span>
        </div>
        
        <div class="mock-interface">
          <!-- 筛选面板 -->
          <div class="filter-section">
            <div class="filter-row">
              <div class="filter-group">
                <label>🏪 市场</label>
                <div class="mock-select">
                  <span class="placeholder">选择市场</span>
                  <span class="arrow">▼</span>
                </div>
              </div>
              <div class="filter-group">
                <label>🐟 品种</label>
                <div class="mock-select">
                  <span class="placeholder">选择品种</span>
                  <span class="arrow">▼</span>
                </div>
              </div>
              <div class="filter-group">
                <label>📅 时间类型</label>
                <div class="radio-group">
                  <label class="radio active">
                    <input type="radio" name="calendar" checked>
                    <span class="radio-dot"></span>
                    公历
                  </label>
                  <label class="radio">
                    <input type="radio" name="calendar">
                    <span class="radio-dot"></span>
                    农历
                  </label>
                </div>
              </div>
            </div>

            <!-- 时间段配置 -->
            <div class="time-period-section">
              <div class="section-header">
                <span>📊 时间段配置</span>
                <button class="add-btn">+ 添加时间段</button>
              </div>
              <div class="period-item">
                <div class="period-name">
                  <input type="text" value="线条 1" placeholder="线条名称">
                </div>
                <div class="period-dates">
                  <div class="date-input">2024-01-01</div>
                  <span class="separator">至</span>
                  <div class="date-input">2024-12-31</div>
                </div>
                <div class="quick-actions">
                  <button>近 1 月</button>
                  <button>近 3 月</button>
                  <button>近 1 年</button>
                  <button>全部</button>
                </div>
                <div class="period-actions">
                  <button class="btn-save">💾 保存</button>
                  <button class="btn-load">📂 加载</button>
                  <button class="btn-delete">🗑️</button>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-row">
              <button class="btn-primary">🔍 查询对比</button>
              <button class="btn-secondary">🔄 重置</button>
            </div>
          </div>

          <!-- 图表区域 -->
          <div class="chart-section">
            <div class="chart-header">
              <h3>📈 价格走势对比图</h3>
              <div class="legend">
                <div class="legend-item">
                  <span class="legend-color" style="background: #00D4FF"></span>
                  <span>2024 年</span>
                </div>
              </div>
            </div>
            <div class="chart-placeholder">
              <svg viewBox="0 0 800 300" class="mock-chart">
                <defs>
                  <linearGradient id="gradient1" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#00D4FF;stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:#00D4FF;stop-opacity:0.05" />
                  </linearGradient>
                </defs>
                <path d="M50,250 L150,200 L250,220 L350,150 L450,180 L550,120 L650,140 L750,80" 
                      fill="none" stroke="#00D4FF" stroke-width="2"/>
                <path d="M50,250 L150,200 L250,220 L350,150 L450,180 L550,120 L650,140 L750,80 L750,300 L50,300 Z" 
                      fill="url(#gradient1)"/>
                <circle cx="150" cy="200" r="4" fill="#00D4FF"/>
                <circle cx="350" cy="150" r="4" fill="#00D4FF"/>
                <circle cx="550" cy="120" r="4" fill="#00D4FF"/>
                <circle cx="750" cy="80" r="4" fill="#00D4FF"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="color-palette">
          <h4>配色方案</h4>
          <div class="colors">
            <div class="color-item" style="background: #0B1221">
              <span>背景 #0B1221</span>
            </div>
            <div class="color-item" style="background: #151E2E">
              <span>卡片 #151E2E</span>
            </div>
            <div class="color-item" style="background: #00D4FF">
              <span>主色 #00D4FF</span>
            </div>
            <div class="color-item" style="background: #3B82F6">
              <span>辅色 #3B82F6</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 方案二：极夜星空风 -->
      <div v-show="currentTheme === 'starlight'" class="preview-panel starlight-theme">
        <div class="panel-header">
          <h2>方案二：极夜星空风</h2>
        </div>
        
        <div class="mock-interface">
          <div class="filter-section">
            <div class="filter-row">
              <div class="filter-group">
                <label>🏪 市场</label>
                <div class="mock-select">
                  <span class="placeholder">选择市场</span>
                  <span class="arrow">▼</span>
                </div>
              </div>
              <div class="filter-group">
                <label>🐟 品种</label>
                <div class="mock-select">
                  <span class="placeholder">选择品种</span>
                  <span class="arrow">▼</span>
                </div>
              </div>
              <div class="filter-group">
                <label>📅 时间类型</label>
                <div class="segmented-control">
                  <button class="active">公历</button>
                  <button>农历</button>
                </div>
              </div>
            </div>

            <div class="time-period-section">
              <div class="section-header">
                <span>📊 时间段配置</span>
                <button class="add-btn">＋ 添加时段</button>
              </div>
              <div class="period-item">
                <div class="period-name">
                  <input type="text" value="线条 1" placeholder="线条名称">
                </div>
                <div class="period-dates">
                  <div class="date-input">2024-01-01</div>
                  <span class="separator">~</span>
                  <div class="date-input">2024-12-31</div>
                </div>
                <div class="quick-actions">
                  <button>1 月</button>
                  <button>3 月</button>
                  <button>1 年</button>
                  <button>全部</button>
                </div>
                <div class="period-actions">
                  <button class="btn-icon">💾</button>
                  <button class="btn-icon">📂</button>
                  <button class="btn-icon danger">🗑️</button>
                </div>
              </div>
            </div>

            <div class="action-row">
              <button class="btn-primary">🔍 查询对比</button>
              <button class="btn-secondary">🔄 重置</button>
            </div>
          </div>

          <div class="chart-section">
            <div class="chart-header">
              <h3>📈 价格走势对比图</h3>
              <div class="legend">
                <div class="legend-item">
                  <span class="legend-color" style="background: linear-gradient(135deg, #6366F1, #22D3EE)"></span>
                  <span>2024 年</span>
                </div>
              </div>
            </div>
            <div class="chart-placeholder">
              <svg viewBox="0 0 800 300" class="mock-chart">
                <defs>
                  <linearGradient id="gradient2" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#6366F1;stop-opacity:0.4" />
                    <stop offset="100%" style="stop-color:#22D3EE;stop-opacity:0.1" />
                  </linearGradient>
                </defs>
                <path d="M50,250 L150,180 L250,200 L350,130 L450,160 L550,100 L650,120 L750,60" 
                      fill="none" stroke="url(#gradient2)" stroke-width="3"/>
                <path d="M50,250 L150,180 L250,200 L350,130 L450,160 L550,100 L650,120 L750,60 L750,300 L50,300 Z" 
                      fill="url(#gradient2)"/>
                <circle cx="150" cy="180" r="5" fill="#6366F1"/>
                <circle cx="350" cy="130" r="5" fill="#6366F1"/>
                <circle cx="550" cy="100" r="5" fill="#6366F1"/>
                <circle cx="750" cy="60" r="5" fill="#22D3EE"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="color-palette">
          <h4>配色方案</h4>
          <div class="colors">
            <div class="color-item" style="background: #0A0E17">
              <span>背景 #0A0E17</span>
            </div>
            <div class="color-item" style="background: #12182B">
              <span>卡片 #12182B</span>
            </div>
            <div class="color-item" style="background: linear-gradient(135deg, #6366F1, #22D3EE)">
              <span>渐变主色</span>
            </div>
            <div class="color-item" style="background: #F1F5F9; color: #0A0E17">
              <span>文字 #F1F5F9</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 方案三：商务深蓝风 -->
      <div v-show="currentTheme === 'business'" class="preview-panel business-theme">
        <div class="panel-header">
          <h2>方案三：商务深蓝风</h2>
        </div>
        
        <div class="mock-interface">
          <div class="filter-section">
            <div class="filter-row">
              <div class="filter-group">
                <label>市场</label>
                <div class="mock-select">
                  <span class="placeholder">选择市场</span>
                  <span class="arrow">▼</span>
                </div>
              </div>
              <div class="filter-group">
                <label>品种</label>
                <div class="mock-select">
                  <span class="placeholder">选择品种</span>
                  <span class="arrow">▼</span>
                </div>
              </div>
              <div class="filter-group">
                <label>时间类型</label>
                <div class="radio-group">
                  <label class="radio active">
                    <input type="radio" name="calendar2" checked>
                    <span class="radio-dot"></span>
                    公历
                  </label>
                  <label class="radio">
                    <input type="radio" name="calendar2">
                    <span class="radio-dot"></span>
                    农历
                  </label>
                </div>
              </div>
            </div>

            <div class="time-period-section">
              <div class="section-header">
                <span>📊 时间段配置</span>
                <button class="add-btn">+ 添加</button>
              </div>
              <div class="period-item">
                <div class="period-name">
                  <input type="text" value="线条 1" placeholder="线条名称">
                </div>
                <div class="period-dates">
                  <div class="date-input">2024-01-01</div>
                  <span class="separator">至</span>
                  <div class="date-input">2024-12-31</div>
                </div>
                <div class="quick-actions">
                  <button>近 1 月</button>
                  <button>近 3 月</button>
                  <button>近 1 年</button>
                  <button>全部</button>
                </div>
                <div class="period-actions">
                  <button class="btn-save">保存</button>
                  <button class="btn-load">加载</button>
                  <button class="btn-delete">删除</button>
                </div>
              </div>
            </div>

            <div class="action-row">
              <button class="btn-primary">查询对比</button>
              <button class="btn-secondary">重置</button>
            </div>
          </div>

          <div class="chart-section">
            <div class="chart-header">
              <h3>📈 价格走势对比图</h3>
              <div class="legend">
                <div class="legend-item">
                  <span class="legend-color" style="background: #3B82F6"></span>
                  <span>2024 年</span>
                </div>
              </div>
            </div>
            <div class="chart-placeholder">
              <svg viewBox="0 0 800 300" class="mock-chart">
                <defs>
                  <linearGradient id="gradient3" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:#3B82F6;stop-opacity:0.05" />
                  </linearGradient>
                </defs>
                <path d="M50,250 L150,190 L250,210 L350,140 L450,170 L550,110 L650,130 L750,70" 
                      fill="none" stroke="#3B82F6" stroke-width="2"/>
                <path d="M50,250 L150,190 L250,210 L350,140 L450,170 L550,110 L650,130 L750,70 L750,300 L50,300 Z" 
                      fill="url(#gradient3)"/>
                <circle cx="150" cy="190" r="4" fill="#3B82F6"/>
                <circle cx="350" cy="140" r="4" fill="#3B82F6"/>
                <circle cx="550" cy="110" r="4" fill="#3B82F6"/>
                <circle cx="750" cy="70" r="4" fill="#3B82F6"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="color-palette">
          <h4>配色方案</h4>
          <div class="colors">
            <div class="color-item" style="background: #0F172A">
              <span>背景 #0F172A</span>
            </div>
            <div class="color-item" style="background: #1E293B">
              <span>卡片 #1E293B</span>
            </div>
            <div class="color-item" style="background: #3B82F6">
              <span>主色 #3B82F6</span>
            </div>
            <div class="color-item" style="background: #F8FAFC; color: #0F172A">
              <span>文字 #F8FAFC</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="preview-footer">
      <button class="btn-select" @click="$emit('select', currentTheme)">选择此方案</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const themes = [
  { id: 'deep-sea', name: '深海科技风' },
  { id: 'starlight', name: '极夜星空风' },
  { id: 'business', name: '商务深蓝风' }
]

const currentTheme = ref('deep-sea')

defineEmits(['select'])
</script>

<style scoped>
.design-preview {
  min-height: 100vh;
  background: #0a0e17;
  color: #e2e8f0;
  padding: 40px 20px;
}

.preview-header {
  text-align: center;
  margin-bottom: 40px;
}

.preview-header h1 {
  font-size: 32px;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #00D4FF, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.preview-header p {
  color: #94a3b8;
  margin-bottom: 24px;
}

.theme-selector {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.theme-btn {
  padding: 10px 20px;
  border: 2px solid #1e293b;
  background: #151e2e;
  color: #94a3b8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.theme-btn:hover {
  border-color: #00d4ff;
  color: #e2e8f0;
}

.theme-btn.active {
  background: #00d4ff;
  border-color: #00d4ff;
  color: #0b1221;
}

.preview-container {
  max-width: 1200px;
  margin: 0 auto;
}

.preview-panel {
  background: #151e2e;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.panel-header h2 {
  font-size: 24px;
  margin: 0;
}

.badge {
  background: linear-gradient(135deg, #00d4ff, #3b82f6);
  color: #0b1221;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.mock-interface {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-section {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 24px;
}

.filter-row {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-size: 12px;
  color: #94a3b8;
}

.mock-select {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-width: 150px;
  cursor: pointer;
}

.mock-select .placeholder {
  color: #64748b;
}

.mock-select .arrow {
  color: #475569;
  font-size: 10px;
}

.radio-group {
  display: flex;
  gap: 16px;
}

.radio {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #94a3b8;
  font-size: 14px;
}

.radio input {
  display: none;
}

.radio-dot {
  width: 16px;
  height: 16px;
  border: 2px solid #475569;
  border-radius: 50%;
  position: relative;
}

.radio.active .radio-dot {
  border-color: #00d4ff;
}

.radio.active .radio-dot::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  background: #00d4ff;
  border-radius: 50%;
}

.time-period-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.add-btn {
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid #00d4ff;
  color: #00d4ff;
  padding: 6px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.add-btn:hover {
  background: rgba(0, 212, 255, 0.2);
}

.period-item {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.period-name input {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #1e293b;
  border-radius: 6px;
  padding: 8px 12px;
  color: #e2e8f0;
  width: 100px;
}

.period-dates {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-input {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #1e293b;
  border-radius: 6px;
  padding: 8px 12px;
  color: #00d4ff;
  font-size: 13px;
}

.separator {
  color: #64748b;
}

.quick-actions {
  display: flex;
  gap: 8px;
}

.quick-actions button {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #334155;
  color: #94a3b8;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
}

.quick-actions button:hover {
  border-color: #00d4ff;
  color: #00d4ff;
}

.period-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.btn-save {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid #10b981;
  color: #10b981;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.btn-load {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid #3b82f6;
  color: #3b82f6;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.btn-delete {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  color: #ef4444;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.action-row {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background: linear-gradient(135deg, #00d4ff, #3b82f6);
  border: none;
  color: #0b1221;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #334155;
  color: #94a3b8;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.chart-section {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 24px;
  min-height: 400px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
}

.legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.chart-placeholder {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 20px;
  height: 300px;
}

.mock-chart {
  width: 100%;
  height: 100%;
}

.color-palette {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #1e293b;
}

.color-palette h4 {
  margin-bottom: 16px;
  color: #94a3b8;
}

.colors {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.color-item {
  width: 120px;
  height: 80px;
  border-radius: 8px;
  display: flex;
  align-items: flex-end;
  padding: 8px;
  font-size: 11px;
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.preview-footer {
  text-align: center;
  margin-top: 40px;
}

.btn-select {
  background: linear-gradient(135deg, #00d4ff, #3b82f6);
  border: none;
  color: #0b1221;
  padding: 16px 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-select:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 212, 255, 0.3);
}
</style>
