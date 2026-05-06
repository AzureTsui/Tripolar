import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Feed from './pages/Feed'
import ArticleDetail from './pages/ArticleDetail'
import Sources from './pages/Sources'
import AITools from './pages/AITools'
import AIToolDetail from './pages/AIToolDetail'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Feed />} />
          <Route path="/article/:id" element={<ArticleDetail />} />
          <Route path="/sources" element={<Sources />} />
          <Route path="/tools" element={<AITools />} />
          <Route path="/tools/:id" element={<AIToolDetail />} />
        </Routes>
      </main>
    </div>
  )
}
