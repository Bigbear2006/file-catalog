import { Button } from './components/ui/button.tsx'

import { useState } from 'react'
import { type FileSorting, type SortingOrder } from '@/api/file.ts'
import { useFiles } from '@/hooks/queries/file.ts'
import { DownloadProgress } from '@/components/DownloadProgress.tsx'
import { SortingSelect } from '@/components/SortingSelect.tsx'
import { FileCard } from '@/components/FileCard.tsx'
import { FileListPagination } from '@/components/FileListPagination.tsx'
import { Loader } from 'lucide-react'
import { SelectFiles } from '@/components/SelectFiles.tsx'
import { TotalStatsCard } from '@/components/TotalStatsCard.tsx'
import { useSearch } from '@tanstack/react-router'
import { toast } from 'sonner'

function App() {
  const pageParam = useSearch({ from: '/', select: (state) => state.page })

  const [page, setPage] = useState<number>(pageParam || 1)
  const [sorting, setSorting] = useState<FileSorting>(null)
  const [order, setOrder] = useState<SortingOrder>('DESC')
  const [filesWithStats, setFilesWithStats] = useState<number[] | boolean>([])
  const [debouncedFilesWithStats, setDebouncedFilesWithStats] = useState<
    number[] | boolean
  >([])

  const { data: fileList } = useFiles({
    page,
    sorting,
    order,
    withStats: debouncedFilesWithStats,
  })

  if (!fileList) {
    return (
      <div className="py-20 flex gap-4 text-center justify-center items-center">
        <Loader className="animate-spin" size={40} />
        <h1 className="text-xl">Загрузка...</h1>
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

        <FileListPagination
          page={page}
          setPage={setPage}
          totalPages={fileList.pages}
        />
      </div>
    </div>
  )
}

export default App
