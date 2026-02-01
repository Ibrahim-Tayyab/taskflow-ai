'use client'

import { useState, useRef, useEffect } from 'react'
import { TaskCreate } from '../types/task'

interface TaskFormProps {
  onTaskAdded: (task: TaskCreate) => void
}

const categories = [
  { value: 'General', emoji: '📁' },
  { value: 'Work', emoji: '💼' },
  { value: 'Personal', emoji: '👤' },
  { value: 'Shopping', emoji: '🛒' },
  { value: 'Health', emoji: '❤️' },
]

const priorities = [
  { value: 'Low', emoji: '🟢', color: 'text-green-400' },
  { value: 'Medium', emoji: '🟡', color: 'text-yellow-400' },
  { value: 'High', emoji: '🔴', color: 'text-red-400' },
]

// Custom Dropdown Component
function CustomDropdown({
  options,
  value,
  onChange,
  disabled
}: {
  options: { value: string; emoji: string; color?: string }[]
  value: string
  onChange: (val: string) => void
  disabled: boolean
}) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const selectedOption = options.find(o => o.value === value) || options[0]

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="relative flex-1" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-sm text-left flex items-center justify-between gap-2 transition-all duration-300 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-purple-500 ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <span className="flex items-center gap-2">
          <span>{selectedOption.emoji}</span>
          <span className={selectedOption.color}>{selectedOption.value}</span>
        </span>
        <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-slate-800 border border-white/10 rounded-xl shadow-xl z-50 overflow-hidden animate-fadeIn">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => {
                onChange(option.value)
                setIsOpen(false)
              }}
              className={`w-full px-4 py-3 text-left flex items-center gap-2 transition-colors ${option.value === value
                  ? 'bg-purple-600/30 text-purple-300'
                  : 'text-white hover:bg-white/10'
                }`}
            >
              <span>{option.emoji}</span>
              <span className={option.color}>{option.value}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default function TaskForm({ onTaskAdded }: TaskFormProps) {
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('General')
  const [priority, setPriority] = useState('Medium')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!description.trim()) return

    setIsSubmitting(true)
    try {
      await onTaskAdded({
        description: description.trim(),
        category,
        priority
      })
      setDescription('')
      setCategory('General')
      setPriority('Medium')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Description Input */}
      <div>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="What needs to be done?"
          className="input-field text-sm sm:text-base"
          disabled={isSubmitting}
        />
      </div>

      {/* Category & Priority - Responsive */}
      <div className="flex flex-col sm:flex-row gap-3">
        <CustomDropdown
          options={categories}
          value={category}
          onChange={setCategory}
          disabled={isSubmitting}
        />

        <CustomDropdown
          options={priorities}
          value={priority}
          onChange={setPriority}
          disabled={isSubmitting}
        />

        <button
          type="submit"
          disabled={!description.trim() || isSubmitting}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              Adding...
            </span>
          ) : (
            <>
              <span className="hidden sm:inline">Add Task</span>
              <span className="sm:hidden">Add</span>
            </>
          )}
        </button>
      </div>
    </form>
  )
}