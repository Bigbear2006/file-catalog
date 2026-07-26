import { Card, CardContent } from '@/components/ui/card.tsx'
import type { File } from '@/api/file.ts'
import { displayDateTime } from '@/lib/fmt.ts'
import { Checkbox } from '@/components/ui/checkbox.tsx'
import type { Dispatch, SetStateAction } from 'react'
import { NumberStartCard } from '@/components/NumberStartCard.tsx'

interface FileCardProps {
  file: File
  filesWithStats: number[] | boolean
  setFilesWithStats: Dispatch<SetStateAction<number[] | boolean>>
}

export function FileCard({
  file,
  filesWithStats,
  setFilesWithStats,
}: FileCardProps) {
  return (
    <Card key={file.name} className="p-4">
      <CardContent className="flex justify-between items-center p-0 px-2">
        <div className="flex flex-col gap-2 items-start">
          <div className="flex flex-col items-start">
            <p className="text-lg">{file.name}</p>
            <p>{displayDateTime(file.downloadedAt, { sep: ', ' })}</p>
          </div>
          {file.stats && file.stats.length > 0 && (
            <div className="flex flex-col items-start">
              <p className="font-semibold">Статистика</p>
              <NumberStartCard stats={file.stats} />
            </div>
          )}
        </div>
        <Checkbox
          className="size-5 border-2"
          checked={
            typeof filesWithStats === 'boolean'
              ? filesWithStats
              : filesWithStats.includes(file.id)
          }
          onCheckedChange={(checked) =>
            setFilesWithStats((prev) => {
              if (typeof prev === 'boolean') {
                if (checked) {
                  return prev ? prev : [file.id]
                }
                return [file.id]
              }
              return checked
                ? [...prev, file.id]
                : prev.filter((file_id) => file_id !== file.id)
            })
          }
        />
      </CardContent>
    </Card>
  )
}
