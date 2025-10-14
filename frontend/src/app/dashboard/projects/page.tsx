'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ProjectCard } from '@/components/projects/ProjectCard'
import { ProjectEmptyState } from '@/components/projects/ProjectEmptyState'
import { CreateProjectDialog } from '@/components/projects/CreateProjectDialog'
import submissionAPI from '@/lib/api/submission-api'
import type { SubmissionSummary } from '@/types/submission'

export default function ProjectsPage() {
  const router = useRouter()
  const [projects, setProjects] = useState<SubmissionSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateDialog, setShowCreateDialog] = useState(false)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setLoading(true)
      const result = await submissionAPI.listSubmissions({ limit: 100 })
      setProjects(result.items)
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredProjects = projects.filter((project) => {
    const clientName = project.client_name || project.applicant_name || ''
    const searchLower = searchQuery.toLowerCase()
    return (
      clientName.toLowerCase().includes(searchLower) ||
      project.id.toLowerCase().includes(searchLower)
    )
  })

  return (
    <div className="container max-w-7xl py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            All Projects
          </h1>
          <p className="text-muted-foreground">
            View and manage all your client submission projects
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          New Project
        </Button>
      </div>

      {/* Search */}
      {projects.length > 0 && (
        <Card className="mb-6">
          <CardContent className="pt-6">
            <Input
              placeholder="Search by client name or project ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </CardContent>
        </Card>
      )}

      {/* Projects Grid */}
      <Card>
        <CardHeader>
          <CardTitle>
            {filteredProjects.length} Project
            {filteredProjects.length !== 1 ? 's' : ''}
          </CardTitle>
          <CardDescription>
            Click on any project to view details and manage files
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">Loading projects...</p>
            </div>
          ) : projects.length === 0 ? (
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
        </CardContent>
      </Card>

      {/* Create Dialog */}
      <CreateProjectDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
      />
    </div>
  )
}