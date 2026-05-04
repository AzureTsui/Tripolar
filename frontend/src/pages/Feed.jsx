import { useState, useEffect } from 'react'
import { api } from '../api/client'
import ArticleCard from '../components/ArticleCard'
import Pagination from '../components/Pagination'
import Loading from '../components/Loading'

export default function Feed() {
  const [articles, setArticles] = useState([])
  const [meta, setMeta] = useState({ page: 1, total: 0, per_page: 20 })
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sources, setSources] = useState([])
  const [selectedSource, setSelectedSource] = useState(null)

  useEffect(() => {
    api.getSources().then(setSources).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError(null)
    api
      .getArticles({ page, source: selectedSource })
      .then((res) => {
        setArticles(res.data)
        setMeta(res.meta)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [page, selectedSource])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Feed</h1>
      <div className="flex gap-2 overflow-x-auto pb-2">
        <button
          onClick={() => { setSelectedSource(null); setPage(1) }}
          className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
            selectedSource === null
              ? 'bg-blue-600 text-white'
              : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-300'
          }`}
        >
          All
        </button>
        {sources.map((s) => (
          <button
            key={s.id}
            onClick={() => { setSelectedSource(s.name); setPage(1) }}
            className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
              selectedSource === s.name
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-300'
            }`}
          >
            {s.name}
          </button>
        ))}
      </div>
      <div className="mt-4 space-y-3">
        {loading ? (
          <Loading />
        ) : error ? (
          <p className="text-red-500 text-center py-10">{error}</p>
        ) : articles.length === 0 ? (
          <p className="text-gray-400 text-center py-10">
            No articles yet. Run{' '}
            <code className="bg-gray-100 px-1 rounded">python scripts/fetch_articles.py</code> to
            fetch RSS data.
          </p>
        ) : (
          articles.map((a) => <ArticleCard key={a.id} article={a} />)
        )}
      </div>
      <Pagination page={meta.page} total={meta.total} perPage={meta.per_page} onChange={setPage} />
    </div>
  )
}
