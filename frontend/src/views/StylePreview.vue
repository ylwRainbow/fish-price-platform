<template>
  <div class="style-preview">
    <div class="preview-header">
      <h1>科技风格预览</h1>
      <p>请选择您喜欢的风格</p>
    </div>
    
    <div class="styles-grid">
      <!-- 赛博朋克风 -->
      <div class="style-card cyberpunk" @click="selectStyle('cyberpunk')">
        <div class="style-badge">推荐</div>
        <div class="card-glow"></div>
        <h2>赛博朋克风</h2>
        <div class="demo-content">
          <div class="demo-header">
            <div class="demo-logo">
              <span class="logo-icon">◈</span>
              <span class="logo-text">FISH PRICE</span>
            </div>
            <div class="demo-nav">
              <span class="nav-item active">价格走势</span>
              <span class="nav-item">数据录入</span>
            </div>
          </div>
          <div class="demo-chart">
            <div class="chart-line line-1"></div>
            <div class="chart-line line-2"></div>
            <div class="chart-line line-3"></div>
          </div>
          <div class="demo-stats">
            <div class="stat-item">
              <span class="stat-value">¥12.5</span>
              <span class="stat-label">当前价格</span>
            </div>
            <div class="stat-item">
              <span class="stat-value up">+5.2%</span>
              <span class="stat-label">涨跌幅</span>
            </div>
          </div>
        </div>
        <p class="style-desc">深色背景、霓虹渐变、发光边框、青色/紫色/蓝色配色</p>
      </div>

      <!-- 科幻仪表盘风 -->
      <div class="style-card scifi" @click="selectStyle('scifi')">
        <div class="card-glow"></div>
        <h2>科幻仪表盘风</h2>
        <div class="demo-content">
          <div class="demo-header">
            <div class="demo-logo">
              <span class="logo-icon">◉</span>
              <span class="logo-text">FISH.SYS</span>
            </div>
            <div class="demo-nav">
              <span class="nav-item active">ANALYTICS</span>
              <span class="nav-item">INPUT</span>
            </div>
          </div>
          <div class="demo-chart">
            <div class="chart-grid"></div>
            <div class="chart-line line-1"></div>
            <div class="chart-line line-2"></div>
          </div>
          <div class="demo-stats">
            <div class="stat-item">
              <span class="stat-value">12.50</span>
              <span class="stat-label">PRICE</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">▲5.2%</span>
              <span class="stat-label">CHANGE</span>
            </div>
          </div>
        </div>
        <p class="style-desc">深蓝色背景、发光线条、数据流效果、冷色调</p>
      </div>

      <!-- 玻璃拟态风 -->
      <div class="style-card glass" @click="selectStyle('glass')">
        <div class="card-glow"></div>
        <h2>玻璃拟态风</h2>
        <div class="demo-content">
          <div class="demo-header">
            <div class="demo-logo">
              <span class="logo-icon">◇</span>
              <span class="logo-text">鱼价平台</span>
            </div>
            <div class="demo-nav">
              <span class="nav-item active">走势</span>
              <span class="nav-item">录入</span>
            </div>
          </div>
          <div class="demo-chart">
            <div class="chart-line line-1"></div>
            <div class="chart-line line-2"></div>
          </div>
          <div class="demo-stats">
            <div class="stat-item">
              <span class="stat-value">¥12.5</span>
              <span class="stat-label">当前价格</span>
            </div>
            <div class="stat-item">
              <span class="stat-value up">+5.2%</span>
              <span class="stat-label">涨跌幅</span>
            </div>
          </div>
        </div>
        <p class="style-desc">玻璃拟态、半透明卡片、模糊背景、柔和发光</p>
      </div>

      <!-- 暗黑极简风 -->
      <div class="style-card dark" @click="selectStyle('dark')">
        <div class="card-glow"></div>
        <h2>暗黑极简风</h2>
        <div class="demo-content">
          <div class="demo-header">
            <div class="demo-logo">
              <span class="logo-icon">○</span>
              <span class="logo-text">FISH</span>
            </div>
            <div class="demo-nav">
              <span class="nav-item active">CHART</span>
              <span class="nav-item">ENTRY</span>
            </div>
          </div>
          <div class="demo-chart">
            <div class="chart-line line-1"></div>
            <div class="chart-line line-2"></div>
          </div>
          <div class="demo-stats">
            <div class="stat-item">
              <span class="stat-value">12.50</span>
              <span class="stat-label">CNY</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">+5.2%</span>
              <span class="stat-label">UP</span>
            </div>
          </div>
        </div>
        <p class="style-desc">纯黑背景、极简线条、单色强调、高对比度</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function selectStyle(style) {
  localStorage.setItem('selectedStyle', style)
  router.push('/')
}
</script>

<style scoped>
.style-preview {
  min-height: 100vh;
  padding: 40px;
  background: #0a0a0f;
}

.preview-header {
  text-align: center;
  margin-bottom: 60px;
}

.preview-header h1 {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, #00f5ff, #bf00ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}

.preview-header p {
  color: #6b7280;
  font-size: 18px;
}

.styles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
  max-width: 1400px;
  margin: 0 auto;
}

.style-card {
  position: relative;
  border-radius: 24px;
  padding: 32px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.style-card:hover {
  transform: translateY(-8px) scale(1.02);
}

.style-card h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  letter-spacing: 0.05em;
}

.style-desc {
  margin-top: 20px;
  font-size: 14px;
  opacity: 0.7;
}

.style-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  z-index: 10;
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 24px;
  opacity: 0;
  transition: opacity 0.4s;
  pointer-events: none;
}

.style-card:hover .card-glow {
  opacity: 1;
}

/* Demo Content */
.demo-content {
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
}

.demo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.demo-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.1em;
}

.demo-nav {
  display: flex;
  gap: 16px;
}

.nav-item {
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 6px;
  opacity: 0.6;
  transition: all 0.3s;
}

.nav-item.active {
  opacity: 1;
}

.demo-chart {
  height: 100px;
  position: relative;
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.chart-line {
  position: absolute;
  height: 2px;
  left: 0;
  right: 0;
  animation: pulse 2s ease-in-out infinite;
}

.chart-line:nth-child(1) {
  top: 30%;
  animation-delay: 0s;
}

.chart-line:nth-child(2) {
  top: 50%;
  animation-delay: 0.3s;
}

.chart-line:nth-child(3) {
  top: 70%;
  animation-delay: 0.6s;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.chart-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(0, 255, 255, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}

.demo-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  font-family: 'Courier New', monospace;
}

.stat-value.up {
  color: #00ff88;
}

.stat-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.6;
}

/* ========== 赛博朋克风 ========== */
.style-card.cyberpunk {
  background: linear-gradient(135deg, #0d0d1a 0%, #1a0a2e 100%);
  border: 1px solid transparent;
  border-image: linear-gradient(135deg, #00f5ff, #bf00ff) 1;
}

.style-card.cyberpunk .card-glow {
  box-shadow: 
    0 0 40px rgba(0, 245, 255, 0.3),
    0 0 80px rgba(191, 0, 255, 0.2),
    inset 0 0 60px rgba(0, 245, 255, 0.05);
}

.style-card.cyberpunk h2 {
  color: #00f5ff;
  text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
}

.style-card.cyberpunk .style-badge {
  background: linear-gradient(135deg, #bf00ff, #00f5ff);
  color: #000;
}

.style-card.cyberpunk .demo-content {
  background: rgba(0, 245, 255, 0.03);
  border: 1px solid rgba(0, 245, 255, 0.2);
}

.style-card.cyberpunk .logo-icon {
  color: #bf00ff;
  text-shadow: 0 0 20px rgba(191, 0, 255, 0.8);
}

.style-card.cyberpunk .logo-text {
  color: #00f5ff;
  text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
}

.style-card.cyberpunk .nav-item.active {
  background: rgba(0, 245, 255, 0.2);
  color: #00f5ff;
  border: 1px solid rgba(0, 245, 255, 0.3);
}

.style-card.cyberpunk .demo-chart {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 245, 255, 0.1);
}

.style-card.cyberpunk .chart-line {
  background: linear-gradient(90deg, transparent, #00f5ff, #bf00ff, transparent);
  box-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
}

.style-card.cyberpunk .stat-value {
  color: #00f5ff;
  text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
}

.style-card.cyberpunk .stat-label {
  color: #bf00ff;
}

.style-card.cyberpunk .style-desc {
  color: #6b7280;
}

/* ========== 科幻仪表盘风 ========== */
.style-card.scifi {
  background: linear-gradient(180deg, #0a1628 0%, #0d1f3c 100%);
  border: 1px solid rgba(0, 200, 255, 0.3);
}

.style-card.scifi .card-glow {
  box-shadow: 
    0 0 30px rgba(0, 200, 255, 0.2),
    inset 0 0 40px rgba(0, 200, 255, 0.03);
}

.style-card.scifi h2 {
  color: #00c8ff;
  text-shadow: 0 0 15px rgba(0, 200, 255, 0.4);
  font-family: 'Courier New', monospace;
}

.style-card.scifi .demo-content {
  background: rgba(0, 200, 255, 0.02);
  border: 1px solid rgba(0, 200, 255, 0.15);
}

.style-card.scifi .logo-icon {
  color: #00ff88;
  text-shadow: 0 0 15px rgba(0, 255, 136, 0.6);
}

.style-card.scifi .logo-text {
  color: #00c8ff;
  font-family: 'Courier New', monospace;
}

.style-card.scifi .nav-item {
  font-family: 'Courier New', monospace;
  color: #4a90a4;
}

.style-card.scifi .nav-item.active {
  background: rgba(0, 200, 255, 0.15);
  color: #00c8ff;
  border: 1px solid rgba(0, 200, 255, 0.3);
}

.style-card.scifi .demo-chart {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(0, 200, 255, 0.1);
}

.style-card.scifi .chart-line {
  background: linear-gradient(90deg, transparent, #00c8ff, transparent);
  box-shadow: 0 0 8px rgba(0, 200, 255, 0.4);
}

.style-card.scifi .stat-value {
  color: #00ff88;
  font-family: 'Courier New', monospace;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.4);
}

.style-card.scifi .stat-label {
  color: #4a90a4;
  font-family: 'Courier New', monospace;
}

.style-card.scifi .style-desc {
  color: #4a6a7a;
}

/* ========== 玻璃拟态风 ========== */
.style-card.glass {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
}

.style-card.glass .card-glow {
  box-shadow: 
    0 8px 32px rgba(99, 102, 241, 0.2),
    0 0 60px rgba(168, 85, 247, 0.1);
}

.style-card.glass h2 {
  background: linear-gradient(135deg, #818cf8, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.style-card.glass .demo-content {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.style-card.glass .logo-icon {
  color: #a855f7;
}

.style-card.glass .logo-text {
  color: #e2e8f0;
}

.style-card.glass .nav-item {
  color: #94a3b8;
}

.style-card.glass .nav-item.active {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.style-card.glass .demo-chart {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.style-card.glass .chart-line {
  background: linear-gradient(90deg, transparent, #818cf8, #a855f7, transparent);
  box-shadow: 0 0 15px rgba(129, 140, 248, 0.3);
}

.style-card.glass .stat-value {
  background: linear-gradient(135deg, #818cf8, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.style-card.glass .stat-label {
  color: #94a3b8;
}

.style-card.glass .style-desc {
  color: #64748b;
}

/* ========== 暗黑极简风 ========== */
.style-card.dark {
  background: #000;
  border: 1px solid #222;
}

.style-card.dark .card-glow {
  box-shadow: 
    0 0 40px rgba(255, 255, 255, 0.05),
    inset 0 0 40px rgba(255, 255, 255, 0.02);
}

.style-card.dark h2 {
  color: #fff;
  font-weight: 300;
  letter-spacing: 0.2em;
}

.style-card.dark .demo-content {
  background: #0a0a0a;
  border: 1px solid #1a1a1a;
}

.style-card.dark .logo-icon {
  color: #fff;
  opacity: 0.8;
}

.style-card.dark .logo-text {
  color: #fff;
  font-weight: 300;
  letter-spacing: 0.2em;
}

.style-card.dark .nav-item {
  color: #444;
  font-weight: 300;
  letter-spacing: 0.1em;
}

.style-card.dark .nav-item.active {
  background: #fff;
  color: #000;
}

.style-card.dark .demo-chart {
  background: #050505;
  border: 1px solid #111;
}

.style-card.dark .chart-line {
  background: #333;
}

.style-card.dark .stat-value {
  color: #fff;
  font-weight: 300;
}

.style-card.dark .stat-value.up {
  color: #00ff88;
}

.style-card.dark .stat-label {
  color: #444;
  font-weight: 300;
  letter-spacing: 0.15em;
}

.style-card.dark .style-desc {
  color: #444;
}

/* Responsive */
@media (max-width: 1024px) {
  .styles-grid {
    grid-template-columns: 1fr;
  }
}
</style>
