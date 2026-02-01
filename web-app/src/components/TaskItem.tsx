'use client'

import { useState, useRef, useEffect } from 'react'
import { Task } from '../types/task'

interface TaskItemProps {
  task: Task
  onUpdate: (task: Task) => void
  onDelete: (id: string) => void
  onToggleComplete: (id: string) => void
}

const categories = ['General', 'Work', 'Personal', 'Shopping', 'Health']
const priorities = ['High', 'Medium', 'Low']

export default function TaskItem({ task, onUpdate, onDelete, onToggleComplete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedDescription, setEditedDescription] = useState(task.description)
  const [showCategoryDropdown, setShowCategoryDropdown] = useState(false)
  const [showPriorityDropdown, setShowPriorityDropdown] = useState(false)
  const [dropdownPosition, setDropdownPosition] = useState<'top' | 'bottom'>('bottom')
  const containerRef = useRef<HTMLDivElement>(null)
  const priorityBtnRef = useRef<HTMLButtonElement>(null)
  const categoryBtnRef = useRef<HTMLButtonElement>(null)

  // Calculate if dropdown should open up or down
  const checkDropdownPosition = (btnRef: React.RefObject<HTMLButtonElement>) => {
    if (btnRef.current) {
      const rect = btnRef.current.getBoundingClientRect()
      const windowHeight = window.innerHeight
      const spaceBelow = windowHeight - rect.bottom
      // If less than 200px below, open upward
      setDropdownPosition(spaceBelow < 200 ? 'top' : 'bottom')
    }
  }

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setShowCategoryDropdown(false)
        setShowPriorityDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSave = () => {
    if (editedDescription.trim() && editedDescription !== task.description) {
      onUpdate({ ...task, description: editedDescription.trim() })
    }
    setIsEditing(false)
  }

  const handleCategoryChange = (newCategory: string) => {
    onUpdate({ ...task, category: newCategory })
    setShowCategoryDropdown(false)
  }

  const handlePriorityChange = (newPriority: string) => {
    onUpdate({ ...task, priority: newPriority })
    setShowPriorityDropdown(false)
  }

  const priorityColors: { [key: string]: string } = {
    High: 'from-red-500 to-pink-500',
    Medium: 'from-amber-500 to-orange-500',
    Low: 'from-green-500 to-emerald-500'
  }

  const priorityEmojis: { [key: string]: string } = {
    High: '🔴',
    Medium: '🟡',
    Low: '🟢'
  }

  const categoryEmojis: { [key: string]: string } = {
    General: '📁',
    Work: '💼',
    Personal: '👤',
    Shopping: '🛒',
    Health: '❤️'
  }

  const isDropdownOpen = showCategoryDropdown || showPriorityDropdown

  return (
    <div
      className={`glass-card p-3 sm:p-4 transition-all duration-200 ${task.completed ? 'opacity-50' : ''} ${isDropdownOpen ? 'relative z-50' : 'relative z-0'}`}
      ref={containerRef}
    >
      <div className="flex items-start gap-2 sm:gap-3">
        {/* Toggle Checkbox */}
        <button
          onClick={() => onToggleComplete(task.id)}
          className={`flex-shrink-0 w-6 h-6 sm:w-7 sm:h-7 rounded-lg border-2 transition-all duration-300 flex items-center justify-center active:scale-90 ${task.completed
            ? 'bg-gradient-to-br from-green-500 to-emerald-500 border-transparent'
            : 'border-slate-500 hover:border-purple-500 active:border-purple-400'
            }`}
        >
          {task.completed && (
            <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Description - Editable */}
          {isEditing ? (
            <input
              type="text"
              value={editedDescription}
              onChange={(e) => setEditedDescription(e.target.value)}
              onBlur={handleSave}
              onKeyDown={(e) => e.key === 'Enter' && handleSave()}
              className="w-full px-2 py-1 text-sm bg-white/10 border border-purple-500 rounded-lg text-white focus:outline-none"
              autoFocus
            />
          ) : (
            <p
              className={`text-sm leading-relaxed break-words ${task.completed ? 'text-slate-500 line-through' : 'text-white'
                }`}
              onClick={() => !task.completed && setIsEditing(true)}
            >
              {task.description}
            </p>
          )}

          {/* Tags - Horizontal scroll on mobile */}
          <div className="flex items-center gap-1.5 sm:gap-2 mt-2 overflow-visible">
            {/* Priority Tag */}
            <div className="relative flex-shrink-0">
              <button
                ref={priorityBtnRef}
                onClick={() => {
                  if (!task.completed) {
                    checkDropdownPosition(priorityBtnRef)
                    setShowPriorityDropdown(!showPriorityDropdown)
                    setShowCategoryDropdown(false)
                  }
                }}
                disabled={task.completed}
                className={`text-[10px] sm:text-xs px-2 py-0.5 sm:py-1 rounded-full bg-gradient-to-r ${priorityColors[task.priority]} text-white transition-transform active:scale-95 disabled:cursor-not-allowed disabled:opacity-50`}
              >
                {priorityEmojis[task.priority]} {task.priority}
              </button>
              {showPriorityDropdown && !task.completed && (
                <div
                  className={`absolute left-0 bg-slate-800 border border-white/10 rounded-lg shadow-2xl overflow-hidden min-w-[110px] ${dropdownPosition === 'top' ? 'bottom-full mb-1' : 'top-full mt-1'
                    }`}
                  style={{ zIndex: 100 }}
                >
                  {priorities.map((p) => (
                    <button
                      key={p}
                      onClick={() => handlePriorityChange(p)}
                      className={`block w-full px-3 py-2.5 text-xs text-left hover:bg-white/10 transition-colors ${p === task.priority ? 'bg-purple-600/30 text-purple-300' : 'text-white'
                        }`}
                    >
                      {priorityEmojis[p]} {p}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Category Tag */}
            <div className="relative flex-shrink-0">
              <button
                ref={categoryBtnRef}
                onClick={() => {
                  if (!task.completed) {
                    checkDropdownPosition(categoryBtnRef)
                    setShowCategoryDropdown(!showCategoryDropdown)
                    setShowPriorityDropdown(false)
                  }
                }}
                disabled={task.completed}
                className="text-[10px] sm:text-xs px-2 py-0.5 sm:py-1 rounded-full bg-white/10 text-slate-300 hover:bg-white/20 transition-colors active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {categoryEmojis[task.category] || '📁'} {task.category}
              </button>
              {showCategoryDropdown && !task.completed && (
                <div
                  className={`absolute left-0 bg-slate-800 border border-white/10 rounded-lg shadow-2xl overflow-hidden min-w-[130px] ${dropdownPosition === 'top' ? 'bottom-full mb-1' : 'top-full mt-1'
                    }`}
                  style={{ zIndex: 100 }}
                >
                  {categories.map((c) => (
                    <button
                      key={c}
                      onClick={() => handleCategoryChange(c)}
                      className={`block w-full px-3 py-2.5 text-xs text-left hover:bg-white/10 transition-colors ${c === task.category ? 'bg-purple-600/30 text-purple-300' : 'text-white'
                        }`}
                    >
                      {categoryEmojis[c]} {c}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Delete Button */}
        <button
          onClick={() => onDelete(task.id)}
          className="flex-shrink-0 p-1.5 sm:p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all active:scale-90"
          aria-label="Delete task"
        >
          <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  )
}