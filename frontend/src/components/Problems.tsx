import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AlertCircle, CheckCircle2, Clock, MapPin, Search } from 'lucide-react'
import { api } from '../lib/api'
import { cn } from '../lib/utils'

// Mock fallback
const mockProblems = [
  { id: 1, title: 'Water shortage in Sector 4', category: 'water', status: 'pending', priority_score: 8.5, ai_confidence: 92, location: 'Sector 4, Delhi' },
  { id: 2, title: 'Broken road blocks ambulance', category: 'infrastructure', status: 'verified', priority_score: 9.8, ai_confidence: 88, location: 'Main St, Mumbai' },
  { id: 3, title: 'Medical supplies needed', category: 'health', status: 'in_progress', priority_score: 7.2, ai_confidence: 95, location: 'Clinic B, Pune' },
]

export function Problems() {
  const { data: problemsData, refetch } = useQuery({
    queryKey: ['problems'],
    queryFn: () => api.getProblems(),
    retry: 1
  })

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState({ title: '', description: '', category: '', address: '' })
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const geo = await api.geocode({ address: formData.address })
      await api.createProblem({
        title: formData.title,
        description: formData.description,
        category: formData.category,
        location_id: geo.location_id,
      })
      alert('Problem reported successfully!')
      setIsModalOpen(false)
      setFormData({ title: '', description: '', category: '', address: '' })
      refetch()
    } catch (err: any) {
      alert('Failed to report problem: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSubmitting(false)
    }
  }

  const problems = problemsData || mockProblems

  return (
    <div className="space-y-6 pb-20 relative">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground/90">Community Problems</h1>
          <p className="text-muted text-sm mt-1">Track, verify, and convert issues into actionable tasks.</p>
        </div>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="glass rounded-lg flex items-center px-3 py-2 bg-surface/50 flex-1 sm:flex-initial">
            <Search className="w-4 h-4 text-muted mr-2" />
            <input type="text" placeholder="Filter problems..." className="bg-transparent border-none outline-none text-sm w-full text-foreground placeholder:text-muted" />
          </div>
          <button onClick={() => setIsModalOpen(true)} className="px-4 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors shadow-sm whitespace-nowrap">
            Report Problem
          </button>
        </div>
      </div>

      <div className="grid gap-4">
        {problems.map((problem: any) => (
          <div key={problem.id} className="glass rounded-xl p-5 hover:bg-white/[0.07] transition-all group relative overflow-hidden">
            <div className="flex flex-col sm:flex-row justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-primary/20 text-primary border border-primary/20 uppercase tracking-wider">
                    {problem.category}
                  </span>
                  <span className={cn(
                    "px-2.5 py-0.5 rounded-full text-[10px] font-medium border uppercase tracking-wider flex items-center gap-1",
                    problem.status === 'pending' ? "bg-yellow-500/10 text-yellow-500 border-yellow-500/20" :
                    problem.status === 'verified' ? "bg-blue-500/10 text-blue-400 border-blue-500/20" :
                    "bg-green-500/10 text-green-400 border-green-500/20"
                  )}>
                    {problem.status === 'pending' ? <Clock className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                    {problem.status}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-foreground/90">{problem.title}</h3>
                <div className="flex items-center gap-4 mt-3 text-sm text-muted">
                  <div className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    {problem.location?.address || problem.address || 'Unknown Location'}
                  </div>
                  <div className="flex items-center gap-1">
                    <AlertCircle className="w-4 h-4 text-red-400" />
                    Priority: {problem.priority_score || 0}/10
                  </div>
                </div>
              </div>
              <div className="flex flex-col items-end justify-between">
                <div className="text-right">
                  <div className="text-xs text-muted mb-1">AI Confidence</div>
                  <div className="text-xl font-bold text-primary">{problem.ai_confidence || 0}%</div>
                </div>
                <button className="px-4 py-2 bg-primary text-background font-semibold text-sm rounded-lg hover:bg-primary-hover transition-colors shadow-[0_0_15px_rgba(0,209,178,0.3)]">
                  Verify & Create Task
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-surface border border-white/10 rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 className="text-xl font-bold text-foreground mb-4">Report Community Problem</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Title</label>
                <input type="text" required value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary" placeholder="e.g. Broken water pipe" />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Category</label>
                <select value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})} className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary">
                  <option value="">Select Category</option>
                  <option value="infrastructure">Infrastructure</option>
                  <option value="health">Health</option>
                  <option value="education">Education</option>
                  <option value="environment">Environment</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Description</label>
                <textarea required value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary" rows={3}></textarea>
              </div>
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Address/Location</label>
                <input type="text" required value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary" placeholder="Street, city, state" />
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setIsModalOpen(false)} className="flex-1 px-4 py-2 border border-border text-foreground font-medium rounded-lg hover:bg-white/5 transition-colors">
                  Cancel
                </button>
                <button type="submit" disabled={submitting} className="flex-1 px-4 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors disabled:opacity-50">
                  {submitting ? 'Submitting...' : 'Submit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
