'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { CreateProjectDialog } from '@/components/projects/CreateProjectDialog'
import { cn } from '@/lib/utils'

export function AppHeader() {
  const pathname = usePathname()
  const [showCreateDialog, setShowCreateDialog] = useState(false)


  const showNewProjectButton = pathname === '/dashboard' || pathname.startsWith('/dashboard/projects')

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center">
          {/* Logo - Links to projects list */}
          <Link href="/dashboard" className="flex items-center space-x-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white font-bold text-xl">
              S
            </div>
            <span className="hidden font-bold sm:inline-block text-xl">
              SubmitEZ
            </span>
          </Link>

          {/* Simple Navigation */}


          {/* Actions - Only show New Project button when appropriate */}
          <div className="ml-auto flex items-center space-x-4">
            {showNewProjectButton && (
              <Button onClick={() => setShowCreateDialog(true)}>
                New Project
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Create Dialog */}
      <CreateProjectDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
      />
    </>
  )
}