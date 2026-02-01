import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { taskService } from '@/services/taskService'
import { Task, TaskCreate, TaskUpdate } from '@/types/task'

// Query hook for fetching tasks
export function useTasksQuery(searchTerm?: string, categoryFilter?: string) {
    return useQuery({
        queryKey: ['tasks', searchTerm, categoryFilter],
        queryFn: () => taskService.getAllTasksWithFilters(searchTerm, categoryFilter),
        staleTime: 1000 * 10, // 10 seconds
    })
}

// Mutation hook for creating a task
export function useCreateTaskMutation() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (taskData: TaskCreate) => taskService.createTask(taskData),
        onSuccess: () => {
            // Invalidate all task queries to trigger refetch
            queryClient.invalidateQueries({ queryKey: ['tasks'] })
        },
    })
}

// Mutation hook for updating a task
export function useUpdateTaskMutation() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: TaskUpdate }) =>
            taskService.updateTask(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['tasks'] })
        },
    })
}

// Mutation hook for toggling task completion
export function useToggleTaskMutation() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, completed }: { id: string; completed: boolean }) =>
            taskService.completeTask(id, completed),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['tasks'] })
        },
    })
}

// Mutation hook for deleting a task
export function useDeleteTaskMutation() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => taskService.deleteTask(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['tasks'] })
        },
    })
}

// Hook to manually invalidate tasks (for chatbot integration)
export function useInvalidateTasks() {
    const queryClient = useQueryClient()

    return () => {
        queryClient.invalidateQueries({ queryKey: ['tasks'] })
    }
}
