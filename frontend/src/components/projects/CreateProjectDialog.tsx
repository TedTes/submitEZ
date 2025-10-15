'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { useSubmission } from '@/hooks/useSubmission'
import { toast } from 'sonner'
interface CreateProjectDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function CreateProjectDialog({
  open,
  onOpenChange,
  onSuccess
}: CreateProjectDialogProps) {
  const router = useRouter()
  const { createSubmission } = useSubmission()
  
  const [clientName, setClientName] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState('')

  const handleCreate = async () => {
    // Validation
    if (!clientName.trim()) {
      setError('Client name is required')
      return
    }
    
    if (clientName.length > 200) {
      setError('Client name must be less than 200 characters')
      return
    }

    try {
      setIsCreating(true)
      setError('')
      
      // Create submission with client name
      const clientNameTrimmed = clientName.trim()
    const submissionId = await createSubmission({
      client_name: clientNameTrimmed,
    })
      
      if (submissionId) {
        // Close dialog
        onOpenChange(false)

        // Reset form
        setClientName('')

        // Show success message
      toast.success(`Project "${clientNameTrimmed}" created successfully!`)

        onSuccess?.()

      } else {
        setError('Failed to create project')
      }
    } catch (err: any) {
      console.error('Create project error:', err)
      setError(err?.message || 'Failed to create project')
    } finally {
      setIsCreating(false)
    }
  }

  const handleCancel = () => {
    setClientName('')
    setError('')
    onOpenChange(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && clientName.trim() && !isCreating) {
      handleCreate()
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Project</DialogTitle>
          <DialogDescription>
            Enter the client name to create a new submission project
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="clientName">Client Name</Label>
            <Input
              id="clientName"
              placeholder="e.g., ABC Manufacturing Company"
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              onKeyDown={handleKeyDown}
              autoFocus
              disabled={isCreating}
              className={error ? 'border-destructive' : ''}
            />
            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
          </div>

          <p className="text-sm text-muted-foreground">
            This will be used to organize and identify your submission package.
          </p>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={isCreating}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreate}
            disabled={!clientName.trim() || isCreating}
          >
            {isCreating ? 'Creating...' : 'Create Project'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}