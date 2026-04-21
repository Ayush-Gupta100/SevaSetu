import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Users, UserPlus, Shield, User, Mail, Loader2 } from 'lucide-react'
import { api } from '../lib/api'
import { cn } from '../lib/utils'

export function Team() {
  const ngoId = localStorage.getItem('ngo_id') || '0'
  const queryClient = useQueryClient()
  
  const { data: members, isLoading } = useQuery({
    queryKey: ['ngo_members', ngoId],
    queryFn: () => api.getNgoMembers(ngoId),
    enabled: ngoId !== '0'
  })

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState({ email: '', name: '', role: 'field_worker', skills: '' })

  const addMemberMutation = useMutation({
    mutationFn: (data: any) => api.addNgoMemberByEmail(ngoId, data),
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ['ngo_members', ngoId] })
      setIsModalOpen(false)
      setFormData({ email: '', name: '', role: 'field_worker', skills: '' })
      const tempPassword = data?.temporary_password
      if (tempPassword) {
        alert(`Member added successfully. Temporary password: ${tempPassword}`)
      } else {
        alert('Member added successfully!')
      }
    },
    onError: (err: any) => {
      alert('Failed to add member: ' + (err.response?.data?.detail || err.message))
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const parsedSkills = formData.skills
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
      .map((skillName) => ({ skill_name: skillName, category: 'ngo', proficiency_level: 'intermediate' }))

    addMemberMutation.mutate({
      email: formData.email,
      name: formData.name || undefined,
      role: formData.role,
      create_if_missing: true,
      skills: parsedSkills,
    })
  }

  return (
    <div className="space-y-6 pb-20 relative">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground/90">Team Management</h1>
          <p className="text-muted text-sm mt-1">Manage your NGO members and their roles</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors flex items-center gap-2 shadow-lg shadow-primary/20"
        >
          <UserPlus className="w-4 h-4" />
          Add Member
        </button>
      </div>

      <div className="grid gap-4">
        {isLoading ? (
          <div className="flex justify-center p-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : members?.length === 0 ? (
          <div className="glass p-12 text-center text-muted rounded-2xl">
            <Users className="w-12 h-12 mx-auto mb-4 opacity-20" />
            <p>No members found. Add your first team member to get started.</p>
          </div>
        ) : (
          <div className="glass rounded-2xl overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead className="bg-white/5 border-b border-white/10 text-muted">
                <tr>
                  <th className="px-6 py-4 font-medium">User</th>
                  <th className="px-6 py-4 font-medium">Role</th>
                  <th className="px-6 py-4 font-medium">Joined Date</th>
                  <th className="px-6 py-4 font-medium">Skills</th>
                  <th className="px-6 py-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {members?.map((member: any) => (
                  <tr key={member.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                          <User className="w-5 h-5" />
                        </div>
                        <div>
                          <p className="font-semibold text-foreground/90">{member.user_name || `User ID: ${member.user_id}`}</p>
                          <p className="text-xs text-muted italic">{member.user_email || 'Member account linked'}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn(
                        "px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border",
                        member.role === 'admin' ? "bg-purple-500/10 text-purple-400 border-purple-500/20" :
                        member.role === 'manager' ? "bg-blue-500/10 text-blue-400 border-blue-500/20" :
                        "bg-green-500/10 text-green-400 border-green-500/20"
                      )}>
                        {member.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-muted">
                      {new Date(member.joined_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-muted text-xs">
                      {member.skills?.length ? member.skills.join(', ') : 'No skills'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-muted hover:text-red-400 text-xs font-medium transition-colors">
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-surface border border-white/10 rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 className="text-xl font-bold text-foreground mb-4">Add Team Member</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Member Email</label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
                  <input 
                    type="email" 
                    required 
                    value={formData.email} 
                    onChange={e => setFormData({...formData, email: e.target.value})} 
                    className="w-full pl-10 pr-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary" 
                    placeholder="member@example.com" 
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Member Name (optional)</label>
                <div className="relative">
                  <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
                  <input
                    type="text"
                    value={formData.name}
                    onChange={e => setFormData({...formData, name: e.target.value})}
                    className="w-full pl-10 pr-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                    placeholder="Full name"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Role</label>
                <div className="relative">
                  <Shield className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
                  <select 
                    value={formData.role} 
                    onChange={e => setFormData({...formData, role: e.target.value})} 
                    className="w-full pl-10 pr-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary appearance-none"
                  >
                    <option value="field_worker">Field Worker</option>
                    <option value="manager">Manager</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Skills (comma separated)</label>
                <input
                  type="text"
                  value={formData.skills}
                  onChange={e => setFormData({...formData, skills: e.target.value})}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  placeholder="first aid, logistics, surveying"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setIsModalOpen(false)} className="flex-1 px-4 py-2 border border-border text-foreground font-medium rounded-lg hover:bg-white/5 transition-colors">
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={addMemberMutation.isPending}
                  className="flex-1 px-4 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {addMemberMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Invite Member'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
