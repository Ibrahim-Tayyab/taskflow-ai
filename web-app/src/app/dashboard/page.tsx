'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import TaskForm from '../../components/TaskForm'
import TaskList from '../../components/TaskList'
import SearchFilter from '../../components/SearchFilter'
import ChatWindow from '../../components/ChatWindow'
import { Task, TaskCreate } from '../../types/task'
import { authService } from '../../services/authService'
import {
  useTasksQuery,
  useCreateTaskMutation,
  useUpdateTaskMutation,
  useDeleteTaskMutation,
  useToggleTaskMutation
} from '../../hooks/useTaskQueries'

type SortOption = 'newest' | 'oldest' | 'priority' | 'alphabetical'

export default function DashboardPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [priorityFilter, setPriorityFilter] = useState('')
  const [sortBy, setSortBy] = useState<SortOption>('newest')
  const [authChecked, setAuthChecked] = useState(false)
  const [userName, setUserName] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const router = useRouter()

  // React Query hooks
  const { data: tasks = [], isLoading: loading } = useTasksQuery(searchTerm, categoryFilter)
  const createTaskMutation = useCreateTaskMutation()
  const updateTaskMutation = useUpdateTaskMutation()
  const deleteTaskMutation = useDeleteTaskMutation()
  const toggleTaskMutation = useToggleTaskMutation()

  useEffect(() => {
    const checkAuth = () => {
      const isAuth = authService.isAuthenticated();
      if (!isAuth) {
        router.push('/login');
        return;
      }
      const user = authService.getUser();
      if (user) {
        setUserName(user.name || user.email);
      }
      setAuthChecked(true);
    };
    checkAuth();
  }, [router])

  // Feature 1: Sorted & Filtered Tasks
  const filteredAndSortedTasks = useMemo(() => {
    let result = [...tasks]

    // Search filter
    if (searchTerm) {
      result = result.filter(t =>
        t.description.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Category filter
    if (categoryFilter) {
      result = result.filter(t => t.category === categoryFilter)
    }

    // Priority filter
    if (priorityFilter) {
      result = result.filter(t => t.priority === priorityFilter)
    }

    // Sorting
    const priorityOrder = { 'High': 0, 'Medium': 1, 'Low': 2 }

    switch (sortBy) {
      case 'newest':
        result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        break
      case 'oldest':
        result.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
        break
      case 'priority':
        result.sort((a, b) => (priorityOrder[a.priority as keyof typeof priorityOrder] || 1) - (priorityOrder[b.priority as keyof typeof priorityOrder] || 1))
        break
      case 'alphabetical':
        result.sort((a, b) => a.description.localeCompare(b.description))
        break
    }

    return result
  }, [tasks, searchTerm, categoryFilter, priorityFilter, sortBy])

  const handleAddTask = async (taskData: TaskCreate) => {
    createTaskMutation.mutate(taskData)
  }

  const handleDelete = async (id: string) => {
    deleteTaskMutation.mutate(id)
  }

  const updateTask = async (updatedTask: Task) => {
    updateTaskMutation.mutate({
      id: updatedTask.id,
      data: {
        description: updatedTask.description,
        completed: updatedTask.completed,
        category: updatedTask.category,
        priority: updatedTask.priority
      }
    })
  }

  const toggleTaskCompletion = async (id: string) => {
    const task = tasks.find(t => t.id === id);
    if (!task) return;
    toggleTaskMutation.mutate({ id, completed: !task.completed })
  }

  // Feature 2: Quick Actions
  const markAllComplete = () => {
    const incomplete = tasks.filter(t => !t.completed)
    incomplete.forEach(t => toggleTaskCompletion(t.id))
  }

  const clearCompleted = () => {
    const completed = tasks.filter(t => t.completed)
    completed.forEach(t => handleDelete(t.id))
  }

  if (!authChecked) {
    return (
      <div className="min-h-[calc(100vh-56px)] sm:min-h-[calc(100vh-64px)] bg-gradient-to-br from-slate-900 via-purple-900/50 to-slate-900 flex items-center justify-center">
        <div className="text-center animate-fadeIn">
          <div className="animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 border-4 border-purple-500 border-t-transparent mx-auto"></div>
          <p className="mt-4 text-sm sm:text-base text-purple-300 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  const completedCount = tasks.filter(t => t.completed).length;
  const pendingCount = tasks.filter(t => !t.completed).length;
  const highPriorityCount = tasks.filter(t => t.priority === 'High' && !t.completed).length;
  const completionRate = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0;

  return (
    <div className="min-h-[calc(100vh-56px)] sm:min-h-[calc(100vh-64px)] bg-gradient-to-br from-slate-900 via-purple-900/50 to-slate-900">
      <div className="max-w-6xl mx-auto px-3 sm:px-6 py-4 sm:py-8">
        {/* Welcome Header - Compact on mobile */}
        <div className="mb-4 sm:mb-8 animate-fadeIn">
          <h1 className="text-xl sm:text-3xl font-bold text-white">
            Hi, <span className="gradient-text">{userName || 'User'}</span> 👋
          </h1>
          <p className="text-slate-400 text-xs sm:text-base mt-0.5 sm:mt-1">Let's get things done!</p>
        </div>

        {/* Stats Cards - 2x2 Grid on mobile */}
        <div className="grid grid-cols-4 gap-2 sm:gap-4 mb-4 sm:mb-8">
          <div className="glass-card p-3 sm:p-4 animate-fadeIn">
            <div className="text-center sm:text-left sm:flex sm:items-center sm:gap-3">
              <div className="hidden sm:flex w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <p className="text-xl sm:text-2xl font-bold text-white">{tasks.length}</p>
                <p className="text-[10px] sm:text-xs text-slate-400">Total</p>
              </div>
            </div>
          </div>

          <div className="glass-card p-3 sm:p-4 animate-fadeIn stagger-1">
            <div className="text-center sm:text-left sm:flex sm:items-center sm:gap-3">
              <div className="hidden sm:flex w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-xl sm:text-2xl font-bold text-amber-400">{pendingCount}</p>
                <p className="text-[10px] sm:text-xs text-slate-400">Pending</p>
              </div>
            </div>
          </div>

          <div className="glass-card p-3 sm:p-4 animate-fadeIn stagger-2">
            <div className="text-center sm:text-left sm:flex sm:items-center sm:gap-3">
              <div className="hidden sm:flex w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-pink-500 items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <p className="text-xl sm:text-2xl font-bold text-red-400">{highPriorityCount}</p>
                <p className="text-[10px] sm:text-xs text-slate-400">Urgent</p>
              </div>
            </div>
          </div>

          <div className="glass-card p-3 sm:p-4 animate-fadeIn stagger-3">
            <div className="text-center sm:text-left sm:flex sm:items-center sm:gap-3">
              <div className="hidden sm:flex w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-xl sm:text-2xl font-bold text-green-400">{completionRate}%</p>
                <p className="text-[10px] sm:text-xs text-slate-400">Done</p>
              </div>
            </div>
          </div>
        </div>

        {/* Add Task Section */}
        <div className="glass-card p-3 sm:p-6 mb-3 sm:mb-6 animate-fadeIn relative z-30">
          <h2 className="text-sm sm:text-lg font-semibold text-white mb-3 sm:mb-4 flex items-center gap-2">
            <span className="text-purple-400">+</span>
            Add Task
          </h2>
          <TaskForm onTaskAdded={handleAddTask} />
        </div>

        {/* Quick Actions */}
        {tasks.length > 0 && (
          <div className="mb-3 sm:mb-6 animate-fadeIn relative z-20">
            <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide">
              <span className="text-xs text-slate-400 flex-shrink-0">Quick:</span>
              <button
                onClick={markAllComplete}
                disabled={pendingCount === 0}
                className="flex-shrink-0 px-3 py-1.5 text-xs bg-green-600/20 text-green-400 rounded-lg hover:bg-green-600/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                ✓ Complete All
              </button>
              <button
                onClick={clearCompleted}
                disabled={completedCount === 0}
                className="flex-shrink-0 px-3 py-1.5 text-xs bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                🗑 Clear Done
              </button>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex-shrink-0 px-3 py-1.5 text-xs rounded-lg transition-colors whitespace-nowrap ${showFilters ? 'bg-purple-600 text-white' : 'bg-white/10 text-slate-300'}`}
              >
                🔍 Filters
              </button>
            </div>
          </div>
        )}

        {/* Search, Filter & Sort */}
        <div className={`overflow-hidden transition-all duration-300 ${showFilters || tasks.length === 0 ? 'max-h-96 mb-3 sm:mb-6' : 'max-h-0'} relative z-20`}>
          <div className="glass-card p-3 sm:p-6 animate-fadeIn">
            <div className="space-y-3 sm:space-y-4">
              <SearchFilter
                onSearch={setSearchTerm}
                onCategoryFilter={setCategoryFilter}
                currentCategory={categoryFilter || 'All'}
              />

              {/* Priority Filter & Sort */}
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                  <span className="text-xs text-slate-400">Priority:</span>
                  {['', 'High', 'Medium', 'Low'].map((p) => (
                    <button
                      key={p || 'all'}
                      onClick={() => setPriorityFilter(p)}
                      className={`px-2 sm:px-3 py-1 text-xs rounded-lg transition-all ${priorityFilter === p
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                        : 'bg-white/5 text-slate-300 hover:bg-white/10'
                        }`}
                    >
                      {p || 'All'}
                    </button>
                  ))}
                </div>

                <div className="flex items-center gap-2 sm:ml-auto">
                  <span className="text-xs text-slate-400">Sort:</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as SortOption)}
                    className="flex-1 sm:flex-none px-3 py-1.5 text-xs bg-slate-800 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
                  >
                    <option value="newest">Newest</option>
                    <option value="oldest">Oldest</option>
                    <option value="priority">Priority</option>
                    <option value="alphabetical">A-Z</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Task List */}
        <div className="glass-card p-3 sm:p-6 animate-fadeIn relative z-10">
          <h2 className="text-sm sm:text-lg font-semibold text-white mb-3 sm:mb-4 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <span className="text-purple-400">📋</span>
              Tasks
            </span>
            <span className="text-xs sm:text-sm font-normal text-slate-400">
              {filteredAndSortedTasks.length} items
            </span>
          </h2>

          {loading ? (
            <div className="flex items-center justify-center py-8 sm:py-12">
              <div className="animate-spin rounded-full h-8 w-8 sm:h-10 sm:w-10 border-3 border-purple-500 border-t-transparent"></div>
            </div>
          ) : filteredAndSortedTasks.length === 0 ? (
            <div className="text-center py-8 sm:py-12">
              <div className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-3 sm:mb-4 rounded-full bg-white/5 flex items-center justify-center">
                <span className="text-2xl sm:text-3xl">📝</span>
              </div>
              <p className="text-slate-400 text-sm sm:text-lg">{tasks.length === 0 ? 'No tasks yet' : 'No matching tasks'}</p>
              <p className="text-slate-500 text-xs sm:text-sm">{tasks.length === 0 ? 'Add your first task above!' : 'Try adjusting your filters'}</p>
            </div>
          ) : (
            <TaskList
              tasks={filteredAndSortedTasks}
              onUpdateTask={updateTask}
              onDeleteTask={handleDelete}
              onToggleCompletion={toggleTaskCompletion}
            />
          )}
        </div>
      </div>
      <ChatWindow />
    </div>
  )
}