import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination.tsx'

interface FileListPaginationProps {
  page: number
  totalPages: number
}

export function FileListPagination({
  page,
  totalPages,
}: FileListPaginationProps) {
  return (
    <Pagination>
      <PaginationContent>
        {page > 1 && (
          <PaginationItem>
            <PaginationPrevious
              to="."
              search={{ page: page - 1 }}
              text="Назад"
            />
          </PaginationItem>
        )}
        {new Array(totalPages).fill(0).map((_, index) => (
          <PaginationItem key={index + 1}>
            <PaginationLink
              to="."
              search={{ page: index + 1 }}
              isActive={index + 1 === page}
            >
              {index + 1}
            </PaginationLink>
          </PaginationItem>
        ))}
        {page < totalPages && (
          <PaginationItem>
            <PaginationNext to="." search={{ page: page + 1 }} text="Вперёд" />
          </PaginationItem>
        )}
      </PaginationContent>
    </Pagination>
  )
}
