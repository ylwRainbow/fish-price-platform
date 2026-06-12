<template>
  <el-container class="app-container">
    <div class="scanline-overlay"></div>
    <el-header class="app-header">
      <div class="header-content">
        <div class="brand">
          <div class="brand-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6.5 12c.94-3.46 4.94-6 8.5-6 3.56 0 6.06 2.54 7 6"></path>
              <path d="M18 12c-.94 3.46-3.94 6-7.5 6-3.56 0-6.06-2.54-7-6l7-6c-.94 3.46 3.94 6 7.5 6 3.56 0 6.06-2.54 7-6"></path>
              <path d="M2 12h2"></path>
              <path d="M20 12h2"></path>
              <path d="M12 2v2"></path>
              <path d="M12 20v2"></path>
            </svg>
          </div>
          <span class="brand-text">
            <span class="brand-text-main">FISH</span>
            <span class="brand-text-sub">PRICE</span>
          </span>
        </div>
        <nav class="nav-menu">
          <router-link 
            v-for="item in menuItems" 
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: activeMenu === item.path }"
          >
            <span class="nav-icon" v-html="item.icon"></span>
            <span class="nav-text">{{ item.label }}</span>
            <span class="nav-glow"></span>
          </router-link>
        </nav>
        <div class="header-status">
          <div class="status-indicator">
            <span class="status-dot"></span>
            <span class="status-text">ONLINE</span>
          </div>
        </div>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'

const route = useRoute()
const catalogStore = useCatalogStore()

const activeMenu = computed(() => route.path)

const menuItems = [
  {
    path: '/',
    label: '价格走势',
    icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>'
  },
  {
    path: '/entry',
    label: '价格录入',
    icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>'
  },
  {
    path: '/import',
    label: '批量导入',
    icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>'
  }
]

catalogStore.loadCatalog()
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  position: relative;
}

.scanline-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9999;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.03) 0px,
    rgba(0, 0, 0, 0.03) 1px,
    transparent 1px,
    transparent 2px
  );
  animation: scanline 8s linear infinite;
}

@keyframes scanline {
  0% { background-position: 0 0; }
  100% { background-position: 0 100%; }
}

.app-header {
  background: linear-gradient(180deg, rgba(13, 13, 26, 0.98) 0%, rgba(10, 10, 18, 0.95) 100%);
  border-bottom: 1px solid var(--color-border);
  height: 70px;
  display: flex;
  align-items: center;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(20px);
}

.app-header::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--gradient-primary);
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.5), 0 0 40px rgba(191, 0, 255, 0.3);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0, 245, 255, 0.2) 0%, rgba(191, 0, 255, 0.2) 100%);
  border: 1px solid var(--color-primary);
  border-radius: 12px;
  color: var(--color-primary);
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.3), inset 0 0 20px rgba(0, 245, 255, 0.1);
  animation: iconGlow 2s ease-in-out infinite alternate;
}

@keyframes iconGlow {
  0% { box-shadow: 0 0 20px rgba(0, 245, 255, 0.3), inset 0 0 20px rgba(0, 245, 255, 0.1); }
  100% { box-shadow: 0 0 30px rgba(0, 245, 255, 0.5), inset 0 0 30px rgba(0, 245, 255, 0.2); }
}

.brand-icon svg {
  width: 24px;
  height: 24px;
  filter: drop-shadow(0 0 4px var(--color-primary));
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.brand-text-main {
  font-size: 22px;
  font-weight: 900;
  color: var(--color-primary);
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 4px;
  text-shadow: 0 0 10px rgba(0, 245, 255, 0.8), 0 0 20px rgba(0, 245, 255, 0.4);
}

.brand-text-sub {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-secondary);
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 6px;
  text-transform: uppercase;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  color: var(--color-text-secondary);
  text-decoration: none;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 1px;
  text-transform: uppercase;
  border: 1px solid transparent;
  border-radius: 8px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0, 245, 255, 0.1) 0%, rgba(191, 0, 255, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.nav-item:hover {
  color: var(--color-primary);
  border-color: rgba(0, 245, 255, 0.3);
  background: rgba(0, 245, 255, 0.05);
}

.nav-item:hover::before {
  opacity: 1;
}

.nav-item.active {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: rgba(0, 245, 255, 0.1);
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.2), inset 0 0 20px rgba(0, 245, 255, 0.05);
}

.nav-item.active::before {
  opacity: 1;
}

.nav-icon {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon :deep(svg) {
  width: 18px;
  height: 18px;
  stroke: currentColor;
  filter: drop-shadow(0 0 2px currentColor);
}

.nav-text {
  position: relative;
  z-index: 1;
}

.nav-glow {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: var(--gradient-primary);
  transition: width 0.3s ease;
  box-shadow: 0 0 10px var(--color-primary);
}

.nav-item:hover .nav-glow,
.nav-item.active .nav-glow {
  width: 80%;
}

.header-status {
  display: flex;
  align-items: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 20px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: var(--color-success);
  border-radius: 50%;
  animation: statusPulse 2s ease-in-out infinite;
  box-shadow: 0 0 10px var(--color-success);
}

@keyframes statusPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.status-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-success);
  letter-spacing: 2px;
}

.app-main {
  background: var(--color-bg-base);
  padding: 0;
  min-height: calc(100vh - 70px);
}

@media (max-width: 1024px) {
  .app-header {
    padding: 0 20px;
    height: 60px;
  }
  
  .brand-icon {
    width: 36px;
    height: 36px;
  }
  
  .brand-icon svg {
    width: 20px;
    height: 20px;
  }
  
  .brand-text-main {
    font-size: 18px;
    letter-spacing: 2px;
  }
  
  .brand-text-sub {
    font-size: 10px;
    letter-spacing: 4px;
  }
  
  .nav-item {
    padding: 10px 16px;
    font-size: 13px;
  }
  
  .nav-text {
    display: none;
  }
  
  .header-status {
    display: none;
  }
}

@media (max-width: 640px) {
  .app-header {
    padding: 0 16px;
    height: 56px;
  }
  
  .brand-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
  }
  
  .brand-icon svg {
    width: 16px;
    height: 16px;
  }
  
  .brand-text-main {
    font-size: 14px;
  }
  
  .brand-text-sub {
    font-size: 8px;
  }
  
  .nav-item {
    padding: 8px 12px;
  }
}
</style>
