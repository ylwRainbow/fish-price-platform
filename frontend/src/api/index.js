const API_BASE = '/api'

export async function getFishes() {
  const res = await fetch(`${API_BASE}/fishes/list`)
  return res.json()
}

export async function getMarkets() {
  const res = await fetch(`${API_BASE}/markets/list`)
  return res.json()
}

export async function getPrices(params) {
  const query = new URLSearchParams(params)
  const res = await fetch(`${API_BASE}/prices?${query}`)
  return res.json()
}

export async function addPrice(data) {
  const res = await fetch(`${API_BASE}/prices`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  return res.json()
}

export async function addPricesBatch(prices) {
  const res = await fetch(`${API_BASE}/prices/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prices })
  })
  return res.json()
}

export async function importExcel(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}/import/excel`, {
    method: 'POST',
    body: formData
  })
  return res.json()
}

export function getExcelTemplateUrl() {
  return `${API_BASE}/templates/prices.xlsx`
}

export function getCSVTemplateUrl() {
  return `${API_BASE}/templates/prices.csv`
}
