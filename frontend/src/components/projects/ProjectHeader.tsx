'use client'

import Link from 'next/link'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { PROJECT_STATUS } from '@/lib/constants'
import type { Submission } from '@/types/submission'

interface ProjectHeaderProps {
  project: Submission
  showActions?: boolean
}

export function ProjectHeader({ project, showActions = true }: ProjectHeaderProps) {
  const statusConfig = PROJECT_STATUS[project.status] || PROJECT_STATUS.draft
  const clientName = project.client_name || project.applicant?.business_name || 'Untitled Project'

  return (
    <div className="mb-6">
      {/* Breadcrumbs */}
      <nav className="flex items-center space-x-2 text-sm text-muted-foreground mb-4">
        <Link 
          href="/dashboard" 
          className="hover:text-foreground transition-colors"
        >
          Projects
        </Link>
        <span>›</span>
        <span className="text-foreground font-medium">{clientName}</span>
      </nav>

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2 flex-wrap">
            <h1 className="text-3xl font-bold tracking-tight">
              {clientName}
            </h1>
            <Badge variant={statusConfig.variant} className="text-sm">
              {statusConfig.label}
            </Badge>
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>Project ID: {project.id.slice(0, 8)}</span>
            {project.broker_name && (
              <>
                <span>•</span>
                <span>Broker: {project.broker_name}</span>
              </>
            )}
            {project.carrier_name && (
              <>
                <span>•</span>
                <span>Carrier: {project.carrier_name}</span>
              </>
            )}
          </div>
        </div>

        {/* Actions */}
        {showActions && (
          <div className="flex items-center gap-2">
            {/* Future: Edit, Delete, Share buttons */}
            <Button variant="outline" size="sm" disabled>
              Edit Details
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}