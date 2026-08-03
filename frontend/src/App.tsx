import { useSearch } from '@tanstack/react-router'
import { Loader } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { type FileSorting, type SortingOrder } from '@/api/file.ts'
import { DownloadProgress } from '@/components/DownloadProgress.tsx'
import { FileCard } from '@/components/FileCard.tsx'
import { FileListPagination } from '@/components/FileListPagination.tsx'
import { SelectFiles } from '@/components/SelectFiles.tsx'
import { SortingSelect } from '@/components/SortingSelect.tsx'
import { TotalStatsCard } from '@/components/TotalStatsCard.tsx'
import { useFiles } from '@/hooks/queries/file.ts'

import { Button } from './components/ui/button.tsx'
import { isAxiosError } from 'axios'
import { displayRetryAfter } from '@/lib/retry.ts'

function App() {
  const page = useSearch({ from: '/', select: (state) => state.page }) || 1

  const [sorting, setSorting] = useState<FileSorting>(null)
  const [order, setOrder] = useState<SortingOrder>('DESC')
  const [filesWithStats, setFilesWithStats] = useState<number[] | boolean>([])
  const [debouncedFilesWithStats, setDebouncedFilesWithStats] = useState<
    number[] | boolean
  >([])

  const { data: fileList, error } = useFiles({
    page,
    sorting,
    order,
    withStats: debouncedFilesWithStats,
  })

  if (!fileList) {
    return (
      <div className="py-20 flex gap-4 text-center justify-center items-center">
        {error ? (
          isAxiosError(error) && error.response ? (
            <p className="text-xl font-semibold text-balance">
              {displayRetryAfter(error.response)}
            </p>
          ) : (
            <div className="flex flex-col">
              <p className="text-xl font-semibold text-balance">
                Что-то пошло не так...
              </p>
              <p>{error.message}</p>
            </div>
          )
        ) : (
          <>
            <Loader className="animate-spin-slow" size={40} />
            <h1 className="text-xl">Загрузка...</h1>
          </>
        )}
      </div>
    )
  }

  return (
    <div className="p-10 flex flex-col gap-10">
      <DownloadProgress fileList={fileList} />
      <div className="flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row gap-2 justify-between text-center items-center">
          <p className="text-xl font-semibold">Скачанные файлы</p>
          <SortingSelect
            sorting={sorting}
            setSorting={setSorting}
            order={order}
            setOrder={setOrder}
          />
        </div>

        <div className="flex flex-col gap-2">
          {fileList.files.map((file) => (
            <FileCard
              file={file}
              filesWithStats={filesWithStats}
              setFilesWithStats={setFilesWithStats}
            />
          ))}
        </div>

        <SelectFiles
          fileList={fileList}
          setFilesWithStats={setFilesWithStats}
        />
        <Button
          onClick={() => {
            setDebouncedFilesWithStats(filesWithStats)
            toast.info('Расчёты произведены')
          }}
        >
          Произвести расчёты
        </Button>
        <TotalStatsCard fileList={fileList} />

        <FileListPagination page={page} totalPages={fileList.pages} />
      </div>
    </div>
  )
}

export default App
