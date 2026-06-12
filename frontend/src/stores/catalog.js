import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getFishes, getMarkets } from '@/api'

export const useCatalogStore = defineStore('catalog', () => {
  const fishes = ref([])
  const markets = ref([])
  const loading = ref(false)

  async function loadCatalog() {
    if (fishes.value.length > 0) return
    
    loading.value = true
    try {
      const [fishData, marketData] = await Promise.all([
        getFishes(),
        getMarkets()
      ])
      fishes.value = fishData
      markets.value = marketData
    } catch (e) {
      console.error('Failed to load catalog:', e)
    } finally {
      loading.value = false
    }
  }

  function getFishById(id) {
    return fishes.value.find(f => f.id === id)
  }

  function getMarketById(id) {
    return markets.value.find(m => m.id === id)
  }

  return {
    fishes,
    markets,
    loading,
    loadCatalog,
    getFishById,
    getMarketById
  }
})
