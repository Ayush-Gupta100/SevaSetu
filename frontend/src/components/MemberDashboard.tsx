import React, { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { CheckSquare, AlertCircle, Clock, Bell } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'

export function MemberDashboard() {
  const role = localStorage.getItem('user_role')
  const canManageSkills = role === 'ngo_member' || role === 'volunteer'
  const [newSkillName, setNewSkillName] = useState('')
  const [skillCategory, setSkillCategory] = useState('')
  const [proficiencyLevel, setProficiencyLevel] = useState('intermediate')
  const [editingSkillName, setEditingSkillName] = useState<string | null>(null)
  const [editCategory, setEditCategory] = useState('')
  const [editProficiency, setEditProficiency] = useState('intermediate')
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

  const { data: mySkillsData, refetch: refetchMySkills } = useQuery({
    queryKey: ['my_skills'],
    queryFn: api.getMySkills,
    retry: 1,
    enabled: canManageSkills,
  })

  const { data: categoryData } = useQuery({
    queryKey: ['skill_categories'],
    queryFn: api.getSkillCategories,
    retry: 1,
    enabled: canManageSkills,
  })

  const { data: allSkillsData } = useQuery({
    queryKey: ['all_skills_catalog'],
    queryFn: api.getSkills,
    retry: 1,
    enabled: canManageSkills,
  })

  const addSkillsMutation = useMutation({
    mutationFn: (payload: any) => api.addUserSkills(payload),
    onSuccess: () => {
      setNewSkillName('')
      setSkillsMessage('Skills saved successfully.')
      refetchMySkills()
    },
    onError: (err: any) => {
      setSkillsMessage(err.response?.data?.detail || 'Failed to save skills.')
    },
  })

  const tasks = tasksData || []
  const mySkills = Array.isArray(mySkillsData) ? mySkillsData : []
  const fetchedCategories = Array.isArray(categoryData)
    ? categoryData.map((item: any) => item.name).filter((item: string) => !!item)
    : []
  const fetchedSkillNames = Array.isArray(allSkillsData)
    ? allSkillsData.map((item: any) => item.name).filter((item: string) => !!item)
    : []
  const existingSkillNameSet = new Set(mySkills.map((skill: any) => skill.skill_name))
  const selectableSkillNames = fetchedSkillNames.filter((name: string) => !existingSkillNameSet.has(name))
  const availableCategories = fetchedCategories.length > 0 ? fetchedCategories : ['General']
  const selectedCategory = skillCategory || availableCategories[0]
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

    const selectedSkill = newSkillName.trim()
    if (!selectedSkill) {
      setSkillsMessage('Please select a skill from the dropdown.')
      return
    }

    await addSkillsMutation.mutateAsync({
      skills: [
        {
          skill_name: selectedSkill,
          category: selectedCategory,
          proficiency_level: proficiencyLevel,
        },
      ],
    })
  }

  const startEditSkill = (skill: any) => {
    setEditingSkillName(skill.skill_name)
    setEditCategory(skill.category || availableCategories[0])
    setEditProficiency(skill.proficiency_level || 'intermediate')
    setSkillsMessage('')
  }

  const handleUpdateSkill = async () => {
    if (!editingSkillName) {
      return
    }

    await addSkillsMutation.mutateAsync({
      skills: [
        {
          skill_name: editingSkillName,
          category: editCategory || availableCategories[0],
          proficiency_level: editProficiency,
        },
      ],
    })

    setEditingSkillName(null)
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
          <p className="text-sm text-muted mt-1">View and edit your skills using standardized categories for better task matching.</p>

          <div className="mt-4 space-y-3">
            {mySkills.length === 0 ? (
              <div className="text-sm text-muted border border-border rounded-lg p-3">No skills added yet.</div>
            ) : (
              mySkills.map((skill: any) => (
                <div key={skill.skill_name} className="border border-border rounded-lg p-3 bg-surface/40">
                  {editingSkillName === skill.skill_name ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
                      <div>
                        <label className="block text-xs text-muted mb-1">Skill</label>
                        <div className="text-sm font-medium text-foreground/90">{skill.skill_name}</div>
                      </div>
                      <div>
                        <label className="block text-xs text-muted mb-1">Category</label>
                        <select
                          value={editCategory || availableCategories[0]}
                          onChange={(e) => setEditCategory(e.target.value)}
                          className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                        >
                          {availableCategories.map((category) => (
                            <option key={category} value={category}>{category}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs text-muted mb-1">Proficiency</label>
                        <select
                          value={editProficiency}
                          onChange={(e) => setEditProficiency(e.target.value)}
                          className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                        >
                          <option value="beginner">Beginner</option>
                          <option value="intermediate">Intermediate</option>
                          <option value="advanced">Advanced</option>
                          <option value="expert">Expert</option>
                        </select>
                      </div>
                      <div className="md:col-span-3 flex gap-2 justify-end">
                        <button
                          type="button"
                          onClick={() => setEditingSkillName(null)}
                          className="px-3 py-1.5 rounded-md border border-border text-sm hover:bg-slate-100 transition-colors"
                        >
                          Cancel
                        </button>
                        <button
                          type="button"
                          onClick={handleUpdateSkill}
                          disabled={addSkillsMutation.isPending}
                          className="px-3 py-1.5 rounded-md bg-primary text-white text-sm hover:bg-primary-hover transition-colors disabled:opacity-50"
                        >
                          {addSkillsMutation.isPending ? 'Saving...' : 'Save'}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-foreground/90">{skill.skill_name}</p>
                        <p className="text-xs text-muted">{skill.category || 'General'} • {skill.proficiency_level || 'intermediate'}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => startEditSkill(skill)}
                        className="px-3 py-1.5 rounded-md border border-border text-sm hover:bg-slate-100 transition-colors"
                      >
                        Edit
                      </button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          <form onSubmit={handleSaveSkills} className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-3">
            <select
              value={newSkillName}
              onChange={(e) => setNewSkillName(e.target.value)}
              className="md:col-span-2 w-full px-3 py-2 rounded-lg bg-surface border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              required
            >
              <option value="">Select Skill</option>
              {selectableSkillNames.map((skillName) => (
                <option key={skillName} value={skillName}>{skillName}</option>
              ))}
            </select>

            <select
              value={selectedCategory}
              onChange={(e) => setSkillCategory(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            >
              {availableCategories.map((category) => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>

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
              disabled={addSkillsMutation.isPending || selectableSkillNames.length === 0}
              className="md:col-span-4 px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-hover transition-colors disabled:opacity-50"
            >
              {addSkillsMutation.isPending ? 'Saving...' : 'Add Skill'}
            </button>
          </form>

          {selectableSkillNames.length === 0 && (
            <div className="mt-3 text-sm text-muted border border-border rounded-lg px-3 py-2">
              No new skills available to add from the dropdown.
            </div>
          )}

          {skillsMessage && (
            <div className="mt-3 text-sm text-foreground bg-slate-100 border border-border rounded-lg px-3 py-2">{skillsMessage}</div>
          )}
        </div>
      )}
    </div>
  )
}
