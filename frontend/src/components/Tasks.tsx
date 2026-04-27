import React, { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckSquare, Clock, User } from 'lucide-react'
import { api } from '../lib/api'
import { useFeedback } from '../lib/feedback'

export function Tasks() {
  const queryClient = useQueryClient()
  const { showError, showSuccess } = useFeedback()
  const role = localStorage.getItem('user_role')
  const isMemberView = role === 'ngo_member' || role === 'volunteer'
  const canAssign = role === 'ngo_admin' || role === 'ngo_member'
  const canAccept = role === 'volunteer'
  const canComplete = role === 'ngo_admin' || role === 'ngo_member'
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false)
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null)
  const [selectedUserId, setSelectedUserId] = useState('')

  const { data: tasksData } = useQuery({
    queryKey: ['tasks', isMemberView ? 'mine' : 'all'],
    queryFn: () => api.getTasks(isMemberView ? '?mine=true' : ''),
    retry: 1,
  })

  const assignMutation = useMutation({
    mutationFn: async ({ taskId, userId }: { taskId: number; userId: number }) => {
      return api.assignTask(String(taskId), { user_id: userId, role: 'volunteer' })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      showSuccess('Task assigned successfully.')
      setIsAssignModalOpen(false)
      setSelectedTaskId(null)
      setSelectedUserId('')
    },
    onError: (err: any) => {
      showError(err.response?.data?.detail || err.message || 'Failed to assign task.')
    },
  })

  const acceptMutation = useMutation({
    mutationFn: (taskId: number) => api.acceptTask(String(taskId)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      showSuccess('Task accepted successfully.')
    },
    onError: (err: any) => {
      showError(err.response?.data?.detail || err.message || 'Failed to accept task.')
    },
  })

  const completeMutation = useMutation({
    mutationFn: (taskId: number) => api.completeTask(String(taskId)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      showSuccess('Task marked as completed.')
    },
    onError: (err: any) => {
      showError(err.response?.data?.detail || err.message || 'Failed to complete task.')
    },
  })

  const openAssignModal = (taskId: number) => {
    setSelectedTaskId(taskId)
    setSelectedUserId('')
    setIsAssignModalOpen(true)
  }

  const handleAssignSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedTaskId) {
      showError('No task selected for assignment.')
      return
    }

    const userId = Number(selectedUserId)
    if (!Number.isFinite(userId) || userId <= 0) {
      showError('Please enter a valid user ID.')
      return
    }

    assignMutation.mutate({ taskId: selectedTaskId, userId })
  }

  const tasks = Array.isArray(tasksData) ? tasksData : []

  return (
    <div className="space-y-6 pb-20">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground/90">Task Board</h1>
        <p className="text-muted text-sm mt-1">Execution and volunteer coordination</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Kanban style columns */}
        {['open', 'assigned', 'in_progress'].map((colStatus) => (
          <div key={colStatus} className="glass rounded-xl p-4 min-h-[500px] flex flex-col gap-4">
            <h3 className="font-semibold text-sm uppercase tracking-wider text-muted flex items-center justify-between border-b border-white/10 pb-2">
              {colStatus.replace('_', ' ')}
              <span className="bg-slate-100 px-2 py-0.5 rounded-full text-xs text-foreground">
                {tasks.filter((t: any) => t.status === colStatus).length}
              </span>
            </h3>

            {tasks.filter((t: any) => t.status === colStatus).length === 0 && (
              <p className="text-xs text-muted">No tasks in this column.</p>
            )}

            {tasks.filter((t: any) => t.status === colStatus).map((task: any) => (
              <div key={task.id} className="glass rounded-lg p-4 hover:border-primary/50 transition-colors cursor-grab active:cursor-grabbing">
                <h4 className="font-medium text-foreground/90 mb-2">{task.title}</h4>
                <div className="flex items-center justify-between text-xs text-muted mt-4">
                  <div className="flex items-center gap-1 text-orange-400">
                    <Clock className="w-3 h-3" />
                    {task.deadline ? new Date(task.deadline).toLocaleDateString() : 'No deadline'}
                  </div>
                  <div className="flex items-center gap-1">
                    <User className="w-3 h-3" />
                    {task.assigned_to || 'Unassigned'}
                  </div>
                </div>
                {colStatus === 'open' && (
                  <>
                    {canAssign && (
                      <button
                        type="button"
                        onClick={() => openAssignModal(task.id)}
                        disabled={assignMutation.isPending}
                        className="w-full mt-4 py-1.5 bg-primary/20 hover:bg-primary/30 rounded-md text-xs font-medium text-primary transition-colors disabled:opacity-50"
                      >
                        Assign Task
                      </button>
                    )}
                  </>
                )}

                {colStatus === 'assigned' && canAccept && (
                  <button
                    type="button"
                    onClick={() => acceptMutation.mutate(task.id)}
                    disabled={acceptMutation.isPending}
                    className="w-full mt-2 py-1.5 bg-primary/20 hover:bg-primary/30 rounded-md text-xs font-medium text-primary transition-colors disabled:opacity-50"
                  >
                    {acceptMutation.isPending ? 'Accepting...' : 'Accept Task'}
                  </button>
                )}

                {(colStatus === 'assigned' || colStatus === 'in_progress') && canComplete && (
                  <button
                    type="button"
                    onClick={() => completeMutation.mutate(task.id)}
                    disabled={completeMutation.isPending}
                    className="w-full mt-2 py-1.5 bg-green-500/20 hover:bg-green-500/30 rounded-md text-xs font-medium text-green-400 transition-colors disabled:opacity-50"
                  >
                    {completeMutation.isPending ? 'Completing...' : 'Mark Completed'}
                  </button>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>

      {isAssignModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-surface border border-white/10 rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 className="text-xl font-bold text-foreground mb-4">Assign Task</h2>
            <form onSubmit={handleAssignSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Volunteer User ID</label>
                <input
                  type="number"
                  min={1}
                  required
                  value={selectedUserId}
                  onChange={(e) => setSelectedUserId(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  placeholder="Enter user ID"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setIsAssignModalOpen(false)
                    setSelectedTaskId(null)
                    setSelectedUserId('')
                  }}
                  className="flex-1 px-4 py-2 border border-border text-foreground font-medium rounded-lg hover:bg-white/5 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={assignMutation.isPending}
                  className="flex-1 px-4 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors disabled:opacity-50"
                >
                  {assignMutation.isPending ? 'Assigning...' : 'Assign'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
