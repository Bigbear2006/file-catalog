import type { FileSorting, SortingOrder } from '@/api/file.ts'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select.tsx'
import type { Dispatch, SetStateAction } from 'react'

const SORTING = [
  { value: null, label: 'Без сортировки' },
  { value: 'downloaded_at', label: 'По времени скачивания' },
] as const

const ORDERS = [
  { value: 'DESC', label: 'По убыванию' },
  { value: 'ASC', label: 'По возрастанию' },
] as const

interface SortingSelectProps {
  sorting: FileSorting
  setSorting: Dispatch<SetStateAction<FileSorting>>
  order: SortingOrder
  setOrder: Dispatch<SetStateAction<SortingOrder>>
}

export function SortingSelect({
  sorting,
  setSorting,
  order,
  setOrder,
}: SortingSelectProps) {
  return (
    <Select
      multiple
      value={[sorting, order]}
      onValueChange={(values) => {
        const value = values[values.length - 1]
        if (value === null || (value !== 'ASC' && value !== 'DESC')) {
          setSorting(value)
        } else {
          setOrder(value as unknown as SortingOrder)
        }
      }}
    >
      <SelectTrigger className="w-full max-w-80">
        <SelectValue placeholder="Сортировать по...">
          {(value: (string | null)[]) => {
            const _sorting = SORTING.find((el) => el.value === value[0])
            const _order = ORDERS.find((el) => el.value === value[1])
            return (
              <>
                {_sorting?.label}
                {_sorting?.value && ` (${_order?.label.toLowerCase()})`}
              </>
            )
          }}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Сортировка</SelectLabel>
          {SORTING.map((el) => (
            <SelectItem key={el.value} value={el.value} label={el.label}>
              {el.label}
            </SelectItem>
          ))}
        </SelectGroup>
        <SelectGroup>
          <SelectLabel>Порядок</SelectLabel>
          {ORDERS.map((el) => (
            <SelectItem key={el.value} value={el.value} label={el.label}>
              {el.label}
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  )
}
