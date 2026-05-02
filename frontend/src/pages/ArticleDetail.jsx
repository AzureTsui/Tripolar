import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'
import Loading from '../components/Loading'

export default function ArticleDetail() {
  const { id } = useParams()
  const [article, setArticle] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    api
      .getArticle(id)
      .then(setArticle)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <Loading />
  if (error) return <p className="text-red-500 text-center py-10">{error}</p>
  if (!article) return null

  return (
    <article className="max-w-3xl mx-auto">
      <Link to="/" className="text-sm text-blue-600 hover:underline mb-4 inline-block">
        &larr; Back to Feed
      </Link>
      <h1 className="text-2xl font-bold mb-3">{article.title}</h1>
      <div className="flex items-center gap-3 text-sm text-gray-500 mb-6">
        {article.source_name && <span>{article.source_name}</span>}
        {article.published_at && (
          <span>{new Date(article.published_at).toLocaleDateString('zh-CN')}</span>
        )}
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline"
        >
          Read original
        </a>
      </div>
      {article.summary && (
        <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 mb-6">
          <h2 className="text-sm font-semibold text-blue-800 mb-1">AI Summary</h2>
          <p className="text-sm text-blue-700">{article.summary}</p>
        </div>
      )}
      {article.content_text && (
        <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
          {article.content_text}
        </div>
      )}
    </article>
  )
}
