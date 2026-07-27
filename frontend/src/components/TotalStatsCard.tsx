import type { FileList } from '@/api/file.ts'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card.tsx'
import { NumberStartCard } from '@/components/NumberStartCard.tsx'

interface TotalStatsCardProps {
  fileList: FileList
}

export function TotalStatsCard({ fileList }: TotalStatsCardProps) {
  return (
    <Card>
      <CardHeader className="justify-start text-left">
        <CardTitle>Общая статистика по файлам</CardTitle>
        <CardDescription>
          Сколько раз встретилась каждая цифра во всех выбранных файлах
        </CardDescription>
      </CardHeader>
      <CardContent>
        {fileList.stats && fileList.stats.length > 0 && (
          <NumberStartCard stats={fileList.stats} />
        )}
      </CardContent>
    </Card>
  )
}
