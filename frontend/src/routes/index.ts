import { createFileRoute } from '@tanstack/react-router'
import { z } from 'zod'

import App from '@/App.tsx'

const AppSearchSchema = z.object({
  page: z.int().min(1).optional().catch(1),
})

export const Route = createFileRoute('/')({
  component: App,
  validateSearch: (search) => AppSearchSchema.parse(search),
})
