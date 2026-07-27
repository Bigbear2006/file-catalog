import { keepPreviousData, useQuery } from '@tanstack/react-query'

import {
  getDownloadedFiles,
  type GetDownloadedFilesRequest,
} from '@/api/file.ts'

export function useFiles(params: GetDownloadedFilesRequest) {
  return useQuery({
    queryKey: ['files', params],
    queryFn: () => getDownloadedFiles(params),
    placeholderData: keepPreviousData,
  })
}
