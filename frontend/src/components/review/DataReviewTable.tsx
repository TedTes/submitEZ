'use client'

import { EditableField } from './EditableField'
import type { Applicant, PropertyLocation, Coverage, LossHistory } from '@/types/submission'

interface DataReviewTableProps {
  data: any
  type: 'applicant' | 'locations' | 'coverage' | 'losses'
  onChange: (updated: any) => void
}

export function DataReviewTable({ data, type, onChange }: DataReviewTableProps) {
  const handleFieldChange = (path: string, value: any) => {
    if (Array.isArray(data)) {
      // Handle array data (locations, losses)
      const [indexStr, field] = path.split('.')
      const index = parseInt(indexStr)
      const updated = [...data]
      updated[index] = { ...updated[index], [field]: value }
      onChange(updated)
    } else {
      // Handle object data (applicant, coverage)
      onChange({ ...data, [path]: value })
    }
  }

  if (type === 'applicant') {
    return <ApplicantTable data={data} onChange={handleFieldChange} />
  }

  if (type === 'locations') {
    return <LocationsTable data={data} onChange={handleFieldChange} />
  }

  if (type === 'coverage') {
    return <CoverageTable data={data} onChange={handleFieldChange} />
  }

  if (type === 'losses') {
    return <LossesTable data={data} onChange={handleFieldChange} />
  }

  return null
}

function ApplicantTable({ data, onChange }: any) {
  const fields = [
    { key: 'business_name', label: 'Business Name', type: 'text' },
    { key: 'fein', label: 'FEIN', type: 'text' },
    { key: 'dba_name', label: 'DBA Name', type: 'text' },
    { key: 'naics_code', label: 'NAICS Code', type: 'text' },
    { key: 'contact_name', label: 'Contact Name', type: 'text' },
    { key: 'email', label: 'Email', type: 'email' },
    { key: 'phone', label: 'Phone', type: 'tel' },
    { key: 'mailing_address', label: 'Mailing Address', type: 'textarea' },
    { key: 'physical_address', label: 'Physical Address', type: 'textarea' },
  ]

  return (
    <div className="space-y-4">
      {fields.map((field) => (
        <div key={field.key} className="grid grid-cols-3 gap-4 items-start">
          <label className="text-sm font-medium pt-2">{field.label}</label>
          <div className="col-span-2">
            <EditableField
              value={data[field.key]}
              onChange={(value) => onChange(field.key, value)}
              type={field.type as any}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

function LocationsTable({ data, onChange }: any) {
  if (!Array.isArray(data) || data.length === 0) {
    return <p className="text-muted-foreground">No locations found</p>
  }

  return (
    <div className="space-y-6">
      {data.map((location: PropertyLocation, index: number) => (
        <div key={index} className="border rounded-lg p-4">
          <h3 className="font-semibold mb-4">Location {index + 1}</h3>
          <div className="space-y-4">
            {[
              { key: 'address_line1', label: 'Address', type: 'text' },
              { key: 'city', label: 'City', type: 'text' },
              { key: 'state', label: 'State', type: 'text' },
              { key: 'zip_code', label: 'ZIP Code', type: 'text' },
              { key: 'building_value', label: 'Building Value', type: 'number' },
              { key: 'contents_value', label: 'Contents Value', type: 'number' },
              { key: 'total_insured_value', label: 'Total TIV', type: 'number' },
            ].map((field) => (
              <div key={field.key} className="grid grid-cols-3 gap-4 items-start">
                <label className="text-sm font-medium pt-2">{field.label}</label>
                <div className="col-span-2">
                  <EditableField
                    value={location[field.key as keyof PropertyLocation]}
                    onChange={(value) => onChange(`${index}.${field.key}`, value)}
                    type={field.type as any}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function CoverageTable({ data, onChange }: any) {
  const fields = [
    { key: 'policy_type', label: 'Policy Type', type: 'text' },
    { key: 'effective_date', label: 'Effective Date', type: 'date' },
    { key: 'expiration_date', label: 'Expiration Date', type: 'date' },
    { key: 'building_limit', label: 'Building Limit', type: 'number' },
    { key: 'contents_limit', label: 'Contents Limit', type: 'number' },
    { key: 'business_income_limit', label: 'BI Limit', type: 'number' },
    { key: 'deductible', label: 'Deductible', type: 'number' },
  ]

  return (
    <div className="space-y-4">
      {fields.map((field) => (
        <div key={field.key} className="grid grid-cols-3 gap-4 items-start">
          <label className="text-sm font-medium pt-2">{field.label}</label>
          <div className="col-span-2">
            <EditableField
              value={data[field.key]}
              onChange={(value) => onChange(field.key, value)}
              type={field.type as any}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

function LossesTable({ data, onChange }: any) {
  if (!Array.isArray(data) || data.length === 0) {
    return <p className="text-muted-foreground">No loss history found</p>
  }

  return (
    <div className="space-y-6">
      {data.map((loss: LossHistory, index: number) => (
        <div key={index} className="border rounded-lg p-4">
          <h3 className="font-semibold mb-4">Loss {index + 1}</h3>
          <div className="space-y-4">
            {[
              { key: 'loss_date', label: 'Loss Date', type: 'date' },
              { key: 'loss_type', label: 'Loss Type', type: 'text' },
              { key: 'loss_description', label: 'Description', type: 'textarea' },
              { key: 'loss_amount', label: 'Loss Amount', type: 'number' },
              { key: 'paid_amount', label: 'Paid Amount', type: 'number' },
              { key: 'claim_status', label: 'Status', type: 'text' },
            ].map((field) => (
              <div key={field.key} className="grid grid-cols-3 gap-4 items-start">
                <label className="text-sm font-medium pt-2">{field.label}</label>
                <div className="col-span-2">
                  <EditableField
                    value={loss[field.key as keyof LossHistory]}
                    onChange={(value) => onChange(`${index}.${field.key}`, value)}
                    type={field.type as any}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}