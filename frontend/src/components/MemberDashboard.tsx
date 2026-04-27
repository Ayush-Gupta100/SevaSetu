import React, { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { CheckSquare, AlertCircle, Clock, Bell } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'

export function MemberDashboard() {
  const role = localStorage.getItem('user_role')
  const canManageSkills = role === 'ngo_member' || role === 'volunteer'
  const [skillsInput, setSkillsInput] = useState('')
  const [skillCategory, setSkillCategory] = useState('General')
  const [proficiencyLevel, setProficiencyLevel] = useState('intermediate')
  const [skillsMessage, setSkillsMessage] = useState('')

  const { data: tasksData } = useQuery({
    queryKey: ['my_tasks_overview'],
    queryFn: () => api.getTasks('?mine=true'),
    retry: 1,
  })

  const { data: notificationsData } = useQuery({
    queryKey: ['member_notifications_overview'],
    queryFn: api.getNotifications,
    retry: 1,
  })

  const addSkillsMutation = useMutation({
    mutationFn: (payload: any) => api.addUserSkills(payload),
    onSuccess: () => {
      setSkillsInput('')
      setSkillsMessage('Skills saved successfully.')
    },
    onError: (err: any) => {
      setSkillsMessage(err.response?.data?.detail || 'Failed to save skills.')
    },
  })

  const tasks = tasksData || []
  const notifications = Array.isArray(notificationsData) ? notificationsData : []
  const recentNotifications = [...notifications]
    .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)
  const openCount = tasks.filter((t: any) => t.status === 'assigned' || t.status === 'open').length
  const inProgressCount = tasks.filter((t: any) => t.status === 'in_progress').length
  const completedCount = tasks.filter((t: any) => t.status === 'completed').length

  const handleSaveSkills = async (e: React.FormEvent) => {
    e.preventDefault()
    setSkillsMessage('')

    const parsedSkills = skillsInput
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)

    if (!parsedSkills.length) {
      setSkillsMessage('Please enter at least one skill.')
      return
    }

    await addSkillsMutation.mutateAsync({
      skills: parsedSkills.map((skillName) => ({
        skill_name: skillName,
        category: skillCategory,
        proficiency_level: proficiencyLevel,
      })),
    })
  }

  return (
    <div className="space-y-6 pb-20">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground/90">Member Dashboard</h1>
        <p className="text-muted text-sm mt-1">Track your assigned work and report new community issues.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass rounded-xl p-5">
          <div className="text-xs uppercase text-muted">Open / Assigned</div>
          <div className="mt-2 text-3xl font-bold text-foreground">{openCount}</div>
          <div className="mt-2 text-sm text-muted flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Needs your action
          </div>
        </div>
        <div className="glass rounded-xl p-5">
          <div className="text-xs uppercase text-muted">In Progress</div>
          <div className="mt-2 text-3xl font-bold text-foreground">{inProgressCount}</div>
          <div className="mt-2 text-sm text-muted flex items-center gap-2">
            <CheckSquare className="w-4 h-4" />
            Currently working
          </div>
        </div>
        <div className="glass rounded-xl p-5">
          <div className="text-xs uppercase text-muted">Completed</div>
          <div className="mt-2 text-3xl font-bold text-foreground">{completedCount}</div>
          <div className="mt-2 text-sm text-muted flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            Finished tasks
          </div>
        </div>
      </div>

      <div className="glass rounded-xl p-5 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground/90">Quick Actions</h2>
          <p className="text-sm text-muted">Jump directly to your tasks or report a new problem.</p>
        </div>
        <div className="flex gap-3">
          <Link to="/tasks" className="px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-hover transition-colors">
            View My Tasks
          </Link>
          <Link to="/problems" className="px-4 py-2 rounded-lg border border-border text-foreground text-sm font-medium hover:bg-slate-100 transition-colors">
            Report Problem
          </Link>
        </div>
      </div>

      <div className="glass rounded-xl p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-foreground/90 flex items-center gap-2">
            <Bell className="w-5 h-5 text-primary" />
            Recent Notifications
          </h2>
          <Link to="/notifications" className="text-xs text-primary hover:underline">
            View all
          </Link>
        </div>

        {recentNotifications.length === 0 ? (
          <p className="text-sm text-muted">No notifications yet.</p>
        ) : (
          <div className="space-y-3">
            {recentNotifications.map((notification: any) => (
              <div key={notification.id} className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
                <p className="text-sm font-medium text-foreground/90">{notification.title}</p>
                <p className="text-xs text-muted mt-1 line-clamp-2">{notification.message}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {canManageSkills && (
        <div className="glass rounded-xl p-5">
          <h2 className="text-lg font-semibold text-foreground/90">My Skills</h2>
          <p className="text-sm text-muted mt-1">Add your skills so task assignment can better match your profile.</p>

          <form onSubmit={handleSaveSkills} className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-3">
            <input
              type="text"
              value={skillsInput}
              onChange={(e) => setSkillsInput(e.target.value)}
              placeholder="e.g. First Aid, Logistics, Data Entry"
              className="md:col-span-2 w-full px-3 py-2 rounded-lg bg-surface border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              required
            />

            <input
              type="text"
              value={skillCategory}
              onChange={(e) => setSkillCategory(e.target.value)}
              placeholder="Category"
              className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />

            <select
              value={proficiencyLevel}
              onChange={(e) => setProficiencyLevel(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="expert">Expert</option>
            </select>

            <button
              type="submit"
              disabled={addSkillsMutation.isPending}
              className="md:col-span-4 px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-hover transition-colors disabled:opacity-50"
            >
              {addSkillsMutation.isPending ? 'Saving...' : 'Save Skills'}
            </button>
          </form>

          {skillsMessage && (
            <div className="mt-3 text-sm text-foreground bg-slate-100 border border-border rounded-lg px-3 py-2">{skillsMessage}</div>
          )}
        </div>
      )}
    </div>
  )
}
