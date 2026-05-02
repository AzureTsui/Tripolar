import { useState, useEffect } from 'react'
import { api } from '../api/client'
import Loading from '../components/Loading'

export default function Sources() {
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', url: '', type: 'rss' })
  const [submitting, setSubmitting] = useState(false)

  const load = () => {
    setLoading(true)
    api
      .getSources()
      .then(setSources)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await api.createSource(form)
      setForm({ name: '', url: '', type: 'rss' })
      setShowForm(false)
      load()
    } catch (err) {
      alert(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this source?')) return
    try {
      await api.deleteSource(id)
      load()
    } catch (err) {
      alert(err.message)
    }
  }

  if (loading) return <Loading />
  if (error) return <p className="text-red-500 text-center py-10">{error}</p>

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Sources</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
        >
          {showForm ? 'Cancel' : '+ Add Source'}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="bg-white border border-gray-200 rounded-lg p-4 mb-4 space-y-3"
        >
          <input
            placeholder="Source name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
            className="w-full px-3 py-2 border border-gray-200 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
          />
          <input
            placeholder="RSS URL"
            value={form.url}
            onChange={(e) => setForm({ ...form, url: e.target.value })}
            required
            className="w-full px-3 py-2 border border-gray-200 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
          />
          <button
            type="submit"
            disabled={submitting}
            className="px-4 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            {submitting ? 'Submitting...' : 'Add'}
          </button>
        </form>
      )}

      <div className="space-y-2">
        {sources.length === 0 ? (
          <p className="text-gray-400 text-center py-10">No sources yet. Add one above.</p>
        ) : (
          sources.map((s) => (
            <div
              key={s.id}
              className="bg-white border border-gray-200 rounded-lg p-4 flex items-center justify-between"
            >
              <div className="min-w-0 flex-1">
                <p className="font-medium text-sm">{s.name}</p>
                <p className="text-xs text-gray-500 truncate">{s.url}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-gray-400">{s.type}</span>
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded ${
                      s.status === 'active'
                        ? 'bg-green-50 text-green-600'
                        : 'bg-gray-100 text-gray-500'
                    }`}
                  >
                    {s.status}
                  </span>
                  {s.last_fetched_at && (
                    <span className="text-xs text-gray-400">
                      Last fetched: {new Date(s.last_fetched_at).toLocaleDateString('zh-CN')}
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={() => handleDelete(s.id)}
                className="text-red-500 hover:text-red-700 text-sm ml-4 shrink-0"
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
