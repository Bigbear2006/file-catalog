import { createFileRoute } from '@tanstack/react-router'
import App from '@/App.tsx'
import { z } from 'zod'

const AppSearchSchema = z.object({
  page: z.int().min(1).optional().catch(1),
})

export const Route = createFileRoute('/')({
  component: App,
  validateSearch: (search) => AppSearchSchema.parse(search),
})
