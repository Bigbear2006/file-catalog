import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination.tsx'
import type { Dispatch, SetStateAction } from 'react'
import { Link } from '@tanstack/react-router'

interface FileListPaginationProps {
  page: number
  setPage: Dispatch<SetStateAction<number>>
  totalPages: number
}

export function FileListPagination({
  page,
  setPage,
  totalPages,
}: FileListPaginationProps) {
  return (
    <Pagination>
      <PaginationContent>
        <PaginationItem>
          <Link to="." search={{ page: page - 1 }} />
          <PaginationPrevious to="." search={{ page: page - 1 }} text="Назад" />
        </PaginationItem>
        {new Array(totalPages).fill(0).map((_, index) => (
          <PaginationItem key={index + 1}>
            <PaginationLink
              to="."
              search={{ page: index + 1 }}
              isActive={index + 1 === page}
              onClick={() => setPage(index + 1)}
            >
              {index + 1}
            </PaginationLink>
          </PaginationItem>
        ))}
        <PaginationItem>
          <PaginationNext to="." search={{ page: page + 1 }} text="Вперёд" />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  )
}
