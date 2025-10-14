'use client'

import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { PROJECT_STATUS } from '@/lib/constants'
import { formatDateTime } from '@/lib/utils/format'
import type { SubmissionSummary } from '@/types/submission'

interface ProjectCardProps {
  project: SubmissionSummary
  onClick?: () => void
}

export function ProjectCard({ project, onClick }: ProjectCardProps) {
  const router = useRouter()
  
  const statusConfig = PROJECT_STATUS[project.status] || PROJECT_STATUS.draft
  const clientName = project.client_name || project.applicant_name || 'Untitled Project'
  
  const handleClick = () => {
    if (onClick) {
      onClick()
    } else {
      router.push(`/dashboard/projects/${project.id}`)
    }
  }

  return (
    <Card 
      className="cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-[1.02]"
      onClick={handleClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold truncate mb-1">
              {clientName}
            </h3>
            <p className="text-xs text-muted-foreground">
              ID: {project.id.slice(0, 8)}
            </p>
          </div>
          <Badge variant={statusConfig.variant}>
            {statusConfig.label}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-2">
          {/* Stats */}
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <span>📍</span>
              <span>{project.total_locations} location{project.total_locations !== 1 ? 's' : ''}</span>
            </div>
            <div className="flex items-center gap-1">
              <span>📋</span>
              <span>{project.total_losses} loss{project.total_losses !== 1 ? 'es' : ''}</span>
            </div>
          </div>
          
          {/* Validation Status */}
          {project.validation_errors_count > 0 || project.validation_warnings_count > 0 ? (
            <div className="flex items-center gap-2 text-xs">
              {project.validation_errors_count > 0 && (
                <span className="text-destructive">
                  ❌ {project.validation_errors_count} error{project.validation_errors_count !== 1 ? 's' : ''}
                </span>
              )}
              {project.validation_warnings_count > 0 && (
                <span className="text-yellow-600">
                  ⚠️ {project.validation_warnings_count} warning{project.validation_warnings_count !== 1 ? 's' : ''}
                </span>
              )}
            </div>
          ) : project.is_valid ? (
            <div className="text-xs text-green-600">
              ✓ Validated
            </div>
          ) : null}
          
          {/* Timestamp */}
          <div className="text-xs text-muted-foreground pt-1 border-t">
            Updated {formatDateTime(project.updated_at)}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}