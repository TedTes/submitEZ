import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

interface ProjectEmptyStateProps {
  onCreateProject: () => void
  title?: string
  description?: string
  actionLabel?: string
  icon?: string
}

export function ProjectEmptyState({
  onCreateProject,
  title = 'No projects yet',
  description = 'Create your first project to get started with document automation',
  actionLabel = 'Create Your First Project',
  icon = '📁',
}: ProjectEmptyStateProps) {
  return (
    <Card className="border-dashed border-2">
      <CardContent className="flex flex-col items-center justify-center py-16 px-6">
        {/* Icon */}
        <div className="w-20 h-20 bg-blue-50 dark:bg-blue-950 rounded-full flex items-center justify-center mb-6">
          <span className="text-4xl">{icon}</span>
        </div>
        
        {/* Title */}
        <h3 className="text-xl font-semibold mb-2 text-center">{title}</h3>
        
        {/* Description */}
        <p className="text-muted-foreground text-center max-w-md mb-6">
          {description}
        </p>
        
        {/* CTA Button */}
        <Button size="lg" onClick={onCreateProject}>
          {actionLabel}
        </Button>
        
        {/* Optional Tips */}
        <div className="mt-10 pt-8 border-t w-full max-w-lg">
          <p className="text-sm text-muted-foreground text-center mb-3">
            <strong>You can upload:</strong>
          </p>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-0.5">•</span>
              <span>ACORD forms (125, 126, 140)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-0.5">•</span>
              <span>Property schedules (Excel/PDF)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-0.5">•</span>
              <span>Loss runs and claim history</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-0.5">•</span>
              <span>Previous policy documents</span>
            </li>
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}