import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { CheckSquare, Clock, User, ArrowRight } from 'lucide-react'
import { api } from '../lib/api'

const mockTasks = [
  { id: 101, title: 'Dispatch water tanker', status: 'open', deadline: '2026-04-18', volunteers_needed: 2 },
  { id: 102, title: 'Clear road debris', status: 'assigned', deadline: '2026-04-19', volunteers_needed: 5, assigned_to: 'Team Alpha' },
  { id: 103, title: 'Deliver medical kits', status: 'in_progress', deadline: '2026-04-17', volunteers_needed: 1, assigned_to: 'Dr. Smith' },
]

export function Tasks() {
  const role = localStorage.getItem('user_role')
  const isMemberView = role === 'ngo_member' || role === 'volunteer'
  const { data: tasksData } = useQuery({
    queryKey: ['tasks', isMemberView ? 'mine' : 'all'],
    queryFn: () => api.getTasks(isMemberView ? '?mine=true' : ''),
    retry: 1,
  })
  const tasks = tasksData || mockTasks

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

            {tasks.filter((t: any) => t.status === colStatus).map((task: any) => (
              <div key={task.id} className="glass rounded-lg p-4 hover:border-primary/50 transition-colors cursor-grab active:cursor-grabbing">
                <h4 className="font-medium text-foreground/90 mb-2">{task.title}</h4>
                <div className="flex items-center justify-between text-xs text-muted mt-4">
                  <div className="flex items-center gap-1 text-orange-400">
                    <Clock className="w-3 h-3" />
                    {task.deadline}
                  </div>
                  <div className="flex items-center gap-1">
                    <User className="w-3 h-3" />
                    {task.assigned_to || `${task.volunteers_needed} needed`}
                  </div>
                </div>
                {colStatus === 'open' && (
                  <button className="w-full mt-4 py-1.5 bg-slate-50 hover:bg-slate-100 rounded-md text-xs font-medium text-foreground transition-colors flex items-center justify-center gap-2">
                    Auto-Assign via AI <ArrowRight className="w-3 h-3" />
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
