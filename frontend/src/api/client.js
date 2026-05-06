const API_BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  if (res.status === 204) return null
  return res.json()
}

function buildQuery(params) {
  const q = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') q.set(k, v)
  })
  return q.toString()
}

export const api = {
  // Articles
  getArticles: (params = {}) => {
    const q = new URLSearchParams()
    if (params.page) q.set('page', params.page)
    if (params.source) q.set('source', params.source)
    return request(`/articles?${q}`)
  },
  getArticle: (id) => request(`/articles/${id}`),

  // Sources
  getSources: () => request('/sources'),
  createSource: (data) => request('/sources', { method: 'POST', body: JSON.stringify(data) }),
  deleteSource: (id) => request(`/sources/${id}`, { method: 'DELETE' }),

  // AI Tools
  getAITools: (params = {}) => {
    const q = buildQuery(params)
    return request(`/tools?${q}`)
  },
  getAITool: (id) => request(`/tools/${id}`),
  getAIToolProductTypes: () => request('/tools/meta/product-types'),
  getAIToolUseCases: () => request('/tools/meta/use-cases'),
}
