import { Link } from 'react-router-dom'

export default function ArticleCard({ article }) {
  return (
    <article className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-sm transition-shadow">
      <div className="flex-1 min-w-0">
        <Link to={`/article/${article.id}`} className="block">
          <h2 className="text-base font-semibold text-gray-900 line-clamp-2 hover:text-blue-600 transition-colors">
            {article.title}
          </h2>
        </Link>
        <div className="mt-2 flex items-center gap-3 text-xs text-gray-500">
          {article.source_name && <span>{article.source_name}</span>}
          {article.published_at && (
            <span>{new Date(article.published_at).toLocaleDateString('zh-CN')}</span>
          )}
          {article.heat_score > 0 && (
            <span className="text-orange-500">{article.heat_score.toFixed(1)}</span>
          )}
        </div>
        {article.summary && (
          <p className="mt-2 text-sm text-gray-600 line-clamp-2">{article.summary}</p>
        )}
        {article.tags?.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {article.tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </article>
  )
}
