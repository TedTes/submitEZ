import { AppHeader } from '@/components/layout/AppHeader'
import { Toaster } from 'sonner'
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <AppHeader />
      <main className="flex-1">{children}</main>
      <Toaster position="top-right" richColors />
    </div>
  )
}