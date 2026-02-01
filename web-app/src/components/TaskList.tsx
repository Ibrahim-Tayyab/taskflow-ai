'use client'

import { Task } from '../types/task'
import TaskItem from './TaskItem'

interface TaskListProps {
  tasks: Task[]
  onUpdateTask: (task: Task) => void
  onDeleteTask: (id: string) => void
  onToggleCompletion: (id: string) => void
}

export default function TaskList({ tasks, onUpdateTask, onDeleteTask, onToggleCompletion }: TaskListProps) {
  return (
    <div className="space-y-3">
      {tasks.map((task, index) => (
        <div
          key={task.id}
          className="animate-fadeIn"
          style={{ animationDelay: `${index * 0.05}s` }}
        >
          <TaskItem
            task={task}
            onUpdate={onUpdateTask}
            onDelete={onDeleteTask}
            onToggleComplete={onToggleCompletion}
          />
        </div>
      ))}
    </div>
  )
}