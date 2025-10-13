import { AppHeader } from '@/components/layout/AppHeader'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <AppHeader />
      <main className="flex-1">{children}</main>
      {/* No footer in app - keeps focus on workflow */}
    </div>
  )
}