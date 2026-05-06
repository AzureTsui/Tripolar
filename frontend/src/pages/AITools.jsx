import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import Pagination from '../components/Pagination'
import Loading from '../components/Loading'

export default function AITools() {
  const [tools, setTools] = useState([])
  const [meta, setMeta] = useState({ page: 1, total: 0, per_page: 24 })
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [productTypes, setProductTypes] = useState([])
  const [useCases, setUseCases] = useState([])
  const [productTypeId, setProductTypeId] = useState(null)
  const [useCaseId, setUseCaseId] = useState(null)
  const [search, setSearch] = useState('')

  useEffect(() => {
    api.getAIToolProductTypes().then(setProductTypes).catch(() => {})
    api.getAIToolUseCases().then(setUseCases).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError(null)
    api
      .getAITools({ page, per_page: 24, product_type_id: productTypeId, use_case_id: useCaseId, search })
      .then((res) => {
        setTools(res.data)
        setMeta(res.meta)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [page, productTypeId, useCaseId, search])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">AI Tools</h1>

      {/* Search */}
      <input
        type="text"
        placeholder="Search tools by name or company..."
        value={search}
        onChange={(e) => { setSearch(e.target.value); setPage(1) }}
        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      {/* Product type filter */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-2">
        <button
          onClick={() => { setProductTypeId(null); setPage(1) }}
          className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
            productTypeId === null
              ? 'bg-blue-600 text-white'
              : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-300'
          }`}
        >
          All Types
        </button>
        {productTypes.map((pt) => (
          <button
            key={pt.id}
            onClick={() => { setProductTypeId(pt.id); setPage(1) }}
            className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
              productTypeId === pt.id
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-300'
            }`}
          >
            {pt.name}
          </button>
        ))}
      </div>

      {/* Use case filter */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-4">
        <button
          onClick={() => { setUseCaseId(null); setPage(1) }}
          className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
            useCaseId === null
              ? 'bg-blue-600 text-white'
              : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-300'
          }`}
        >
          All Use Cases
        </button>
        {useCases.map((uc) => (
          <button
            key={uc.id}
            onClick={() => { setUseCaseId(uc.id); setPage(1) }}
            className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
              useCaseId === uc.id
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-300'
            }`}
          >
            {uc.name}
          </button>
        ))}
      </div>

      {/* Tool cards */}
      {loading ? (
        <Loading />
      ) : error ? (
        <p className="text-red-500 text-center py-10">{error}</p>
      ) : tools.length === 0 ? (
        <p className="text-gray-400 text-center py-10">No AI tools found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {tools.map((tool) => (
            <Link
              key={tool.id}
              to={`/tools/${tool.id}`}
              className="block p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <h3 className="font-semibold text-gray-900 truncate">{tool.name}</h3>
              <p className="text-xs text-gray-500 mt-1">{tool.company || '—'}</p>
              <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                {tool.short_description || tool.overview?.slice(0, 100)}
              </p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {tool.product_type && (
                  <span className="px-2 py-0.5 text-xs rounded-full bg-blue-50 text-blue-700">
                    {tool.product_type.name}
                  </span>
                )}
                {tool.use_case && (
                  <span className="px-2 py-0.5 text-xs rounded-full bg-green-50 text-green-700">
                    {tool.use_case.name}
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}

      <Pagination page={meta.page} total={meta.total} perPage={meta.per_page} onChange={setPage} />
    </div>
  )
}
