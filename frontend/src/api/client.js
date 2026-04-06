const API_BASE = '/api'

export async function getModels() {
  const res = await fetch(`${API_BASE}/models`)
  if (!res.ok) throw new Error('Failed to fetch models')
  return res.json()
}

export async function sendQuestion(question, model, temperature) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, model, temperature }),
  })
  if (!res.ok) throw new Error('Failed to send question')
  return res
}

export async function ingestDocuments(urls = null) {
  const res = await fetch(`${API_BASE}/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ urls }),
  })
  if (!res.ok) throw new Error('Failed to ingest documents')
  return res.json()
}
