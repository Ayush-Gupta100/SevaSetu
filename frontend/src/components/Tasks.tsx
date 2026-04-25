import React from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckSquare, Clock, User, ArrowRight } from 'lucide-react'
import { api } from '../lib/api'

export function Tasks() {
  const queryClient = useQueryClient()
  const role = localStorage.getItem('user_role')
  const isMemberView = role === 'ngo_member' || role === 'volunteer'
  const canAssign = role === 'ngo_admin' || role === 'ngo_member'
  const canAccept = role === 'volunteer'
  const canComplete = role === 'ngo_admin' || role === 'ngo_member'

  const { data: tasksData } = useQuery({
    queryKey: ['tasks', isMemberView ? 'mine' : 'all'],
    queryFn: () => api.getTasks(isMemberView ? '?mine=true' : ''),
    retry: 1,
  })

  const assignMutation = useMutation({
    mutationFn: async (taskId: number) => {
      const userIdInput = window.prompt('Enter user ID to assign this task to:')
      if (!userIdInput) {
        throw new Error('Assignment cancelled.')
      }
      const userId = Number(userIdInput)
      if (!Number.isFinite(userId) || userId <= 0) {
        throw new Error('Invalid user ID.')
      }

      return api.assignTask(String(taskId), { user_id: userId, role: 'volunteer' })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || err.message || 'Failed to assign task.')
    },
  })

  const acceptMutation = useMutation({
    mutationFn: (taskId: number) => api.acceptTask(String(taskId)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || err.message || 'Failed to accept task.')
    },
  })

  const completeMutation = useMutation({
    mutationFn: (taskId: number) => api.completeTask(String(taskId)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || err.message || 'Failed to complete task.')
    },
  })

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
                    <button className="w-full mt-4 py-1.5 bg-slate-50 hover:bg-slate-100 rounded-md text-xs font-medium text-foreground transition-colors flex items-center justify-center gap-2">
                      Auto-Assign via AI <ArrowRight className="w-3 h-3" />
                    </button>
                    {canAssign && (
                      <button
                        type="button"
                        onClick={() => assignMutation.mutate(task.id)}
                        disabled={assignMutation.isPending}
                        className="w-full mt-2 py-1.5 bg-primary/20 hover:bg-primary/30 rounded-md text-xs font-medium text-primary transition-colors disabled:opacity-50"
                      >
                        {assignMutation.isPending ? 'Assigning...' : 'Assign Task'}
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
    </div>
  )
}
