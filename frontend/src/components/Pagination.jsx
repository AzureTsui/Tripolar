export default function Pagination({ page, total, perPage, onChange }) {
  const totalPages = Math.ceil(total / perPage)
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-center gap-2 mt-6">
      <button
        onClick={() => onChange(page - 1)}
        disabled={page <= 1}
        className="px-3 py-1.5 rounded text-sm border border-gray-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
      >
        Prev
      </button>
      <span className="text-sm text-gray-500">
        {page} / {totalPages}
      </span>
      <button
        onClick={() => onChange(page + 1)}
        disabled={page >= totalPages}
        className="px-3 py-1.5 rounded text-sm border border-gray-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
      >
        Next
      </button>
    </div>
  )
}
