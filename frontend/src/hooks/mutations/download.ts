import { type QueryClient, useMutation } from '@tanstack/react-query'
import { isAxiosError } from 'axios'
import { toast } from 'sonner'

import { downloadFiles, getFileNames, markDownloadedFiles } from '@/api/file.ts'

interface UseDownloadFilesMutationOptions {
  queryClient: QueryClient
  onNewFileNamesChunk: (fileNames: string[]) => void
}

export function useDownloadFilesMutation({
  queryClient,
  onNewFileNamesChunk,
}: UseDownloadFilesMutationOptions) {
  return useMutation({
    mutationFn: async () => {
      try {
        let { names: fileNames } = await getFileNames()
        while (fileNames.length !== 0) {
          onNewFileNamesChunk(fileNames)
          for (let i = 0; i < Math.ceil(fileNames.length / 3); i++) {
            const fileNamesChunk = fileNames.slice(i * 3, i * 3 + 3)

            const { data: zipData } = await downloadFiles({
              names: fileNamesChunk,
            })
            downloadZipArchive(zipData)

            await markDownloadedFiles({ names: fileNamesChunk })
            await queryClient.invalidateQueries({ queryKey: ['files'] })
          }
          const fileNamesResponse = await getFileNames()
          fileNames = fileNamesResponse.names
        }
      } catch (err) {
        if (!isAxiosError(err) || !err.response) {
          throw err
        }

        const retryAfter = parseInt(err.response.headers['retry-after'])
        const retryAfterStr = Number.isNaN(retryAfter)
          ? ''
          : ` Попробуйте снова через ${retryAfter} секунд`

        if (err.response.status == 429) {
          toast.warning(
            `Слишком много запросов, скачивание остановлено.${retryAfterStr}`,
          )
        }

        if (err.response.status === 403) {
          toast.warning(
            `Вы заблокированы за слишком частые запросы.${retryAfterStr}`,
          )
        }

        throw err
      }
    },
  })
}

function downloadZipArchive(data: any) {
  const blob = new Blob([data], { type: 'application/zip' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'files.zip'
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
