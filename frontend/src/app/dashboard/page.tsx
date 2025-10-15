'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ProjectCard } from '@/components/projects/ProjectCard'
import { ProjectEmptyState } from '@/components/projects/ProjectEmptyState'
import { CreateProjectDialog } from '@/components/projects/CreateProjectDialog'
import { useSubmission, useRecentSubmissions } from '@/hooks/useSubmission'

export default function DashboardPage() {

  const { loadRecentSubmissions } = useSubmission()
  const recentProjects = useRecentSubmissions()
  
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadRecentSubmissions()
  }, [loadRecentSubmissions])

  // Filter projects by search
  const filteredProjects = recentProjects.filter((project) => {
    const clientName = project.client_name || project.applicant_name || ''
    const searchLower = searchQuery.toLowerCase()
    return (
      clientName.toLowerCase().includes(searchLower) ||
      project.id.toLowerCase().includes(searchLower)
    )
  })

  const hasProjects = recentProjects.length > 0

  return (
    <div className="container max-w-7xl py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Projects</h1>
          <p className="text-muted-foreground">
            Manage your client submission projects
          </p>
        </div>
        {/* Only show button when projects exist */}
      </div>

      {/* Search (if projects exist) */}
      {hasProjects && (
        <div className="mb-6">
          <Input
            placeholder="Search projects by client name or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-md"
          />
        </div>
      )}

      {/* Content */}
      {recentProjects.length === 0 ? (
        <ProjectEmptyState onCreateProject={() => setShowCreateDialog(true)} />
      ) : filteredProjects.length === 0 ? (
        <ProjectEmptyState
          title="No projects found"
          description="Try adjusting your search query"
          actionLabel="Clear Search"
          icon="🔍"
          onCreateProject={() => setSearchQuery('')}
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredProjects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      {/* Create Dialog */}
      <CreateProjectDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onSuccess={() => {
          // Reload projects when new one is created
          loadRecentSubmissions()
        }}
      />
    </div>
  )
}