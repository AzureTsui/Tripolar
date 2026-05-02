import { useState, useEffect } from 'react'
import { api } from '../api/client'
import ArticleCard from '../components/ArticleCard'
import CategoryFilter from '../components/CategoryFilter'
import Pagination from '../components/Pagination'
import Loading from '../components/Loading'

export default function Feed() {
  const [articles, setArticles] = useState([])
  const [categories, setCategories] = useState([])
  const [meta, setMeta] = useState({ page: 1, total: 0, per_page: 20 })
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getCategories().then(setCategories).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError(null)
    api
      .getArticles({ page, category_id: selectedCategory })
      .then((res) => {
        setArticles(res.data)
        setMeta(res.meta)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [page, selectedCategory])

  const handleCategoryChange = (id) => {
    setSelectedCategory(id)
    setPage(1)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Feed</h1>
      <CategoryFilter
        categories={categories}
        selected={selectedCategory}
        onChange={handleCategoryChange}
        loading={categories.length === 0}
      />
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
