import { Link } from 'react-router-dom'

export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-gray-900 tracking-tight">
          Tripolar
        </Link>
        <nav className="flex gap-6 text-sm text-gray-600">
          <Link to="/" className="hover:text-gray-900 transition-colors">
            Feed
          </Link>
          <Link to="/tools" className="hover:text-gray-900 transition-colors">
            Tools
          </Link>
          <Link to="/sources" className="hover:text-gray-900 transition-colors">
            Sources
          </Link>
        </nav>
      </div>
    </header>
  )
}
