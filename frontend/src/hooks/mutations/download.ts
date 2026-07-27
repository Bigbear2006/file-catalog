import { type QueryClient, useMutation } from '@tanstack/react-query'

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
      let { names: fileNames } = await getFileNames()
      while (fileNames.length !== 0) {
        onNewFileNamesChunk(fileNames)
        for (let i = 0; i < Math.ceil(fileNames.length / 3); i++) {
          const fileNamesChunk = fileNames.slice(i * 3, i * 3 + 3)
          await downloadFiles({ names: fileNamesChunk })
          await markDownloadedFiles({ names: fileNamesChunk })
          await queryClient.invalidateQueries({ queryKey: ['files'] })
          const fileNamesResponse = await getFileNames()
          fileNames = fileNamesResponse.names
        }
      }
    },
  })
}
