'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { DocumentPreview } from '@/components/download/DocumentPreview'
import { DownloadButton } from '@/components/download/DownloadButton'
import { DataReviewTable } from '@/components/review/DataReviewTable'
import submissionAPI from '@/lib/api/submission-api'
import { formatFileSize, formatDateTime } from '@/lib/utils/format'
import type { Submission } from '@/types/submission'

interface ProjectResultsProps {
  project: Submission
  onUpdate?: (updated: Submission) => void
}

export function ProjectResults({ project, onUpdate }: ProjectResultsProps) {
  const [selectedFileUrl, setSelectedFileUrl] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'applicant' | 'locations' | 'coverage' | 'losses'>('applicant')
  const [editedProject, setEditedProject] = useState(project)

  const generatedFiles = project.generated_files || []
  const hasFiles = generatedFiles.length > 0

  const handleDownloadAll = async () => {
    try {
      await submissionAPI.downloadAllFiles(project.id)
    } catch (err: any) {
      alert(`Failed to download files: ${err?.message}`)
    }
  }

  const handleSaveChanges = async () => {
    try {
      const updated = await submissionAPI.updateSubmission(project.id, {
        applicant: editedProject.applicant,
        locations: editedProject.locations,
        coverage: editedProject.coverage,
        loss_history: editedProject.loss_history,
      })
      
      if (onUpdate) {
        onUpdate(updated)
      }
      
      alert('Changes saved successfully')
    } catch (err: any) {
      alert(`Failed to save: ${err?.message}`)
    }
  }

  return (
    <div className="space-y-6">
      {/* Success Alert */}
      <Alert>
        <AlertDescription className="flex items-center gap-2">
          <span className="text-lg">🎉</span>
          <span className="font-medium">Processing Complete!</span>
          <span className="text-muted-foreground">
            Your submission package is ready to download
          </span>
        </AlertDescription>
      </Alert>

      {/* Generated Files */}
      {hasFiles && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* File List */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Generated Files</CardTitle>
                  <CardDescription>
                    {generatedFiles.length} file{generatedFiles.length !== 1 ? 's' : ''} ready
                  </CardDescription>
                </div>
                <DownloadButton onClick={handleDownloadAll}>
                  Download All
                </DownloadButton>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {generatedFiles.map((file, index) => (
                  <div
                    key={index}
                    className={`flex items-center justify-between p-3 border rounded-lg cursor-pointer transition-colors hover:bg-muted/50 ${
                      selectedFileUrl === file.url ? 'bg-muted' : ''
                    }`}
                    onClick={() => setSelectedFileUrl(file.url)}
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="text-2xl">📄</div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium truncate">
                          {file.form_type}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {file.filename} • {formatFileSize(file.size_bytes)}
                        </div>
                      </div>
                    </div>
                    <DownloadButton
                      onClick={async (e) => {
                        e.stopPropagation()
                        await submissionAPI.downloadFile(file.url, file.filename)
                      }}
                      variant="ghost"
                      size="sm"
                    >
                      Download
                    </DownloadButton>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Preview */}
          <Card>
            <CardHeader>
              <CardTitle>Preview</CardTitle>
              <CardDescription>
                {selectedFileUrl
                  ? 'PDF preview (if supported by browser)'
                  : 'Select a file to preview'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedFileUrl ? (
                <DocumentPreview url={selectedFileUrl} />
              ) : (
                <div className="flex items-center justify-center h-[500px] bg-muted/30 rounded-lg">
                  <p className="text-muted-foreground">No file selected</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Extracted Data Review */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Extracted Data</CardTitle>
              <CardDescription>
                Review and edit the data extracted from your documents
              </CardDescription>
            </div>
            <Button onClick={handleSaveChanges} variant="secondary">
              Save Changes
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Tabs */}
          <div className="flex gap-2 mb-4 border-b">
            {['applicant', 'locations', 'coverage', 'losses'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`px-4 py-2 font-medium capitalize transition-colors ${
                  activeTab === tab
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {tab}
                {tab === 'locations' && ` (${editedProject.locations.length})`}
                {tab === 'losses' && ` (${editedProject.loss_history.length})`}
              </button>
            ))}
          </div>

          {/* Data Tables */}
          <div className="mt-4">
            {activeTab === 'applicant' && editedProject.applicant && (
              <DataReviewTable
                data={editedProject.applicant}
                type="applicant"
                onChange={(updated) =>
                  setEditedProject({ ...editedProject, applicant: updated })
                }
              />
            )}
            {activeTab === 'locations' && (
              <DataReviewTable
                data={editedProject.locations}
                type="locations"
                onChange={(updated) =>
                  setEditedProject({ ...editedProject, locations: updated })
                }
              />
            )}
            {activeTab === 'coverage' && editedProject.coverage && (
              <DataReviewTable
                data={editedProject.coverage}
                type="coverage"
                onChange={(updated) =>
                  setEditedProject({ ...editedProject, coverage: updated })
                }
              />
            )}
            {activeTab === 'losses' && (
              <DataReviewTable
                data={editedProject.loss_history}
                type="losses"
                onChange={(updated) =>
                  setEditedProject({ ...editedProject, loss_history: updated })
                }
              />
            )}
          </div>
        </CardContent>
      </Card>

      {/* Project Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Project Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="font-medium text-muted-foreground">Client</dt>
              <dd>{project.client_name || project.applicant?.business_name || 'N/A'}</dd>
            </div>
            <div>
              <dt className="font-medium text-muted-foreground">Project ID</dt>
              <dd className="font-mono">{project.id.slice(0, 16)}</dd>
            </div>
            <div>
              <dt className="font-medium text-muted-foreground">Locations</dt>
              <dd>{project.locations.length}</dd>
            </div>
            <div>
              <dt className="font-medium text-muted-foreground">Loss History</dt>
              <dd>{project.loss_history.length}</dd>
            </div>
            {project.carrier_name && (
              <div>
                <dt className="font-medium text-muted-foreground">Carrier</dt>
                <dd>{project.carrier_name}</dd>
              </div>
            )}
            {project.broker_name && (
              <div>
                <dt className="font-medium text-muted-foreground">Broker</dt>
                <dd>{project.broker_name}</dd>
              </div>
            )}
            <div>
              <dt className="font-medium text-muted-foreground">Created</dt>
              <dd>{formatDateTime(project.created_at)}</dd>
            </div>
            <div>
              <dt className="font-medium text-muted-foreground">Completed</dt>
              <dd>{project.generated_at ? formatDateTime(project.generated_at) : 'N/A'}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  )
}