import type { NumberStats } from '@/api/file.ts'

interface NumberStartCardProps {
  stats: NumberStats[]
}

export function NumberStartCard({ stats }: NumberStartCardProps) {
  return (
    <div className="flex flex-wrap gap-1">
      {stats &&
        stats.map((stat, index) => (
          <p>
            {stat.number} ({stat.count} раз)
            {index !== stats!.length - 1 && ', '}
          </p>
        ))}
    </div>
  )
}
