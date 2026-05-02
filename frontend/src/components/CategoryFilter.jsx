export default function CategoryFilter({ categories, selected, onChange, loading }) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      <button
        onClick={() => onChange(null)}
        className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
          selected === null
            ? 'bg-blue-600 text-white'
            : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-300'
        }`}
      >
        All
      </button>
      {loading
        ? [1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="w-20 h-8 rounded-full bg-gray-200 animate-pulse" />
          ))
        : categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => onChange(cat.id)}
              className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
                selected === cat.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-300'
              }`}
            >
              {cat.name}
            </button>
          ))}
    </div>
  )
}
