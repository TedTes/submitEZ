'use client'

import { useState, useEffect } from 'react'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'

interface EditableFieldProps {
  value: any
  onChange: (value: any) => void
  type?: 'text' | 'email' | 'tel' | 'number' | 'date' | 'textarea'
  className?: string
}

export function EditableField({
  value,
  onChange,
  type = 'text',
  className,
}: EditableFieldProps) {
  const [localValue, setLocalValue] = useState(value || '')
  const [isDirty, setIsDirty] = useState(false)

  useEffect(() => {
    setLocalValue(value || '')
    setIsDirty(false)
  }, [value])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setLocalValue(e.target.value)
    setIsDirty(true)
  }

  const handleBlur = () => {
    if (isDirty) {
      let processedValue = localValue

      // Type-specific processing
      if (type === 'number') {
        processedValue = localValue ? parseFloat(localValue) : null
      }

      onChange(processedValue)
      setIsDirty(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && type !== 'textarea') {
      (e.currentTarget as  HTMLElement).blur()
    }
  }

  if (type === 'textarea') {
    return (
      <textarea
        value={localValue}
        onChange={handleChange}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        className={cn(
          'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          isDirty && 'border-yellow-500',
          className
        )}
      />
    )
  }

  return (
    <Input
      type={type}
      value={localValue}
      onChange={handleChange}
      onBlur={handleBlur}
      onKeyDown={handleKeyDown}
      className={cn(
        isDirty && 'border-yellow-500',
        className
      )}
    />
  )
}