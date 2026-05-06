import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'
import Loading from '../components/Loading'

export default function AIToolDetail() {
  const { id } = useParams()
  const [tool, setTool] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    api
      .getAITool(id)
      .then(setTool)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <Loading />
  if (error) return <p className="text-red-500 text-center py-10">{error}</p>
  if (!tool) return null

  return (
    <div className="max-w-3xl mx-auto">
      {/* Back link */}
      <Link
        to="/tools"
        className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 mb-4 transition-colors"
      >
        &larr; Back to Tools
      </Link>

      {/* Name & company */}
      <h1 className="text-2xl font-bold text-gray-900">{tool.name}</h1>
      {tool.company && (
        <p className="text-sm text-gray-500 mt-1">{tool.company}</p>
      )}

      {/* Badges */}
      <div className="mt-3 flex flex-wrap gap-2">
        {tool.product_type && (
          <span className="px-2.5 py-1 text-xs rounded-full bg-blue-50 text-blue-700 font-medium">
            {tool.product_type.name}
          </span>
        )}
        {tool.use_case && (
          <span className="px-2.5 py-1 text-xs rounded-full bg-green-50 text-green-700 font-medium">
            {tool.use_case.name}
          </span>
        )}
        <span className="px-2.5 py-1 text-xs rounded-full bg-gray-100 text-gray-600">
          {tool.status === 'active' ? 'Active' : tool.status}
        </span>
      </div>

      {/* Short description */}
      {tool.short_description && (
        <p className="mt-4 text-lg text-gray-700 font-medium">{tool.short_description}</p>
      )}

      {/* Website link */}
      {tool.website_url && (
        <a
          href={tool.website_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 transition-colors"
        >
          Visit Website &rarr;
        </a>
      )}

      {/* Overview */}
      {tool.overview && (
        <div className="mt-6">
          <h2 className="text-base font-semibold text-gray-900 mb-2">Overview</h2>
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{tool.overview}</p>
        </div>
      )}

      {/* Meta info */}
      <div className="mt-8 pt-4 border-t border-gray-200 text-xs text-gray-400">
        {tool.created_at && (
          <p>Added: {new Date(tool.created_at).toLocaleDateString('zh-CN')}</p>
        )}
        <p className="mt-1">Slug: {tool.slug}</p>
      </div>
    </div>
  )
}
