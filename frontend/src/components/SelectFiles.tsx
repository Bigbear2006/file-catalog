import { type Dispatch, type SetStateAction, useState } from 'react'

import type { FileList } from '@/api/file.ts'
import { Checkbox } from '@/components/ui/checkbox.tsx'

interface SelectFilesProps {
  fileList: FileList
  setFilesWithStats: Dispatch<SetStateAction<number[] | boolean>>
}

export function SelectFiles({ fileList, setFilesWithStats }: SelectFilesProps) {
  const [allPageFilesSelected, setAllPageFilesSelected] = useState(false)
  const [allFilesSelected, setAllFilesSelected] = useState(false)

  return (
    <div className="flex flex-col sm:flex-row justify-between gap-4">
      <div className="flex items-center gap-2 text-left">
        <Checkbox
          checked={allPageFilesSelected}
          onCheckedChange={(checked) => {
            if (checked) setAllFilesSelected(false)
            setAllPageFilesSelected(checked)
            setFilesWithStats(
              checked ? fileList.files.map((file) => file.id) : [],
            )
          }}
        />
        <p className="text-sm">
          Выбрать все файлы на этой странице ({fileList.files.length})
        </p>
      </div>
      <div className="flex items-center gap-2 text-left">
        <Checkbox
          checked={allFilesSelected}
          onCheckedChange={(checked) => {
            if (checked) setAllPageFilesSelected(false)
            setAllFilesSelected(checked)
            setFilesWithStats(checked)
          }}
        />
        <p className="text-sm">Выбрать все файлы ({fileList.total})</p>
      </div>
    </div>
  )
}
