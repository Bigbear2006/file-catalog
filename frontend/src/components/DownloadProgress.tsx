import {
  Progress,
  ProgressLabel,
  ProgressValue,
} from '../components/ui/progress.tsx'
import { type FileList } from '../api/file.ts'
import { Download, Loader } from 'lucide-react'
import { useDownloadFilesMutation } from '@/hooks/mutations/download.ts'
import { useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button.tsx'
import { displayDateTime } from '@/lib/fmt.ts'

interface DownloadProgressProps {
  fileList: FileList
}

export function DownloadProgress({ fileList }: DownloadProgressProps) {
  const queryClient = useQueryClient()
  const downloadMutation = useDownloadFilesMutation({
    queryClient,
    onNewFileNamesChunk: (fileNames) =>
      setFileNamesCount((prev) => prev + fileNames.length),
  })

  const [fileNamesCount, setFileNamesCount] = useState(fileList.total || 0)

  useEffect(() => {
    if (fileList) setFileNamesCount(fileList.total)
  }, [fileList])

  return (
    <div className="flex flex-col gap-2">
      <Progress value={(fileList.total / fileNamesCount) * 100}>
        <div className="text-left">
          <ProgressLabel>
            получено {fileNamesCount} названий файлов, скачано {fileList.total}{' '}
            из {fileNamesCount}
          </ProgressLabel>
          <p className="text-sm">
            {fileList.files.length > 0
              ? `Скачивание началось ${displayDateTime(fileList.files[0].downloadedAt, { sep: ' в ' })}`
              : 'Скачивание ещё не началось'}
          </p>
        </div>
        <ProgressValue />
      </Progress>
      <Button
        onClick={
          downloadMutation.isPending
            ? undefined
            : () => downloadMutation.mutate()
        }
      >
        {downloadMutation.isPending ? (
          <>
            <Loader className="animate-spin" />
            Данные скачиваются
          </>
        ) : (
          <>
            <Download />
            Скачать данные
          </>
        )}
      </Button>
    </div>
  )
}
