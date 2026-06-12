const API_BASE = '/api'

async function parseResponse(res) {
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.detail || data.message || `HTTP ${res.status}`)
  }
  return data
}

export async function getFishes() {
  const res = await fetch(`${API_BASE}/fishes/list`)
  return parseResponse(res)
}

export async function getMarkets() {
  const res = await fetch(`${API_BASE}/markets/list`)
  return parseResponse(res)
}

export async function getPrices(params) {
  const query = new URLSearchParams(params)
  const res = await fetch(`${API_BASE}/prices?${query}`)
  return parseResponse(res)
}

export async function addPrice(data) {
  const res = await fetch(`${API_BASE}/prices`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  return parseResponse(res)
}

export async function addPricesBatch(prices) {
  const res = await fetch(`${API_BASE}/prices/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prices })
  })
  return parseResponse(res)
}

export async function importPriceFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}/import/prices`, {
    method: 'POST',
    body: formData
  })
  return parseResponse(res)
}

export async function importExcel(file) {
  return importPriceFile(file)
}

export function getExcelTemplateUrl() {
  return `${API_BASE}/templates/prices.xlsx`
}

export function getCSVTemplateUrl() {
  return `${API_BASE}/templates/prices.csv`
}
