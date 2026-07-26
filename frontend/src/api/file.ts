import { axiosInstance } from '@/api/base.ts'

interface FileNames {
  names: string[]
}

export async function getFileNames() {
  const rsp = await axiosInstance.get<FileNames>('/files/names')
  return rsp.data
}

export type FileSorting = 'downloaded_at' | null
export type SortingOrder = 'ASC' | 'DESC'

export interface GetDownloadedFilesRequest {
  page?: number
  sorting?: FileSorting
  order?: SortingOrder
  withStats?: number[] | boolean
}

export interface NumberStats {
  number: number
  count: number
}

interface FileResponse {
  id: number
  name: string
  downloaded_at: string
  stats?: NumberStats[]
}

export interface File {
  id: number
  name: string
  downloadedAt: Date
  stats?: NumberStats[]
}

interface FileListResponse {
  files: FileResponse[]
  stats?: NumberStats[]
  total: number
}

export interface FileList {
  files: File[]
  stats?: NumberStats[]
  total: number
}

export async function getDownloadedFiles(
  params: GetDownloadedFilesRequest,
): Promise<FileList> {
  const rsp = await axiosInstance.get<FileListResponse>('/files/downloaded', {
    params,
  })
  return {
    files: rsp.data.files.map((file) => ({
      id: file.id,
      name: file.name,
      downloadedAt: new Date(file.downloaded_at),
      stats: file.stats,
    })),
    stats: rsp.data.stats,
    total: rsp.data.total,
  }
}

interface DownloadFilesRequest {
  names: string[]
}

export async function downloadFiles(data: DownloadFilesRequest) {
  await axiosInstance.post('/files/download', data)
}

interface MarkDownloadedFilesRequest extends DownloadFilesRequest {}

export async function markDownloadedFiles(data: MarkDownloadedFilesRequest) {
  await axiosInstance.post('/files/downloaded', data)
}
