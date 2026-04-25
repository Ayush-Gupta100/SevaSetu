import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { BrainCircuit, CheckCircle2, Clock3, Users } from 'lucide-react'
import { api } from '../lib/api'

export function Insights() {
  const { data } = useQuery({ queryKey: ['ai_insights'], queryFn: api.getAiInsights, retry: 1 })
  const insights = data

  return (
    <div className="space-y-6 pb-20">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground/90">AI Insights</h1>
        <p className="text-muted text-sm mt-1">Operational analytics across problems, tasks, and matching quality.</p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="glass rounded-xl p-5 border-l-4 border-l-primary">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted">Total Problems</span>
            <BrainCircuit className="w-4 h-4 text-primary" />
          </div>
          <p className="text-3xl font-bold">{insights?.total_problems ?? 0}</p>
        </div>
        <div className="glass rounded-xl p-5 border-l-4 border-l-blue-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted">Verified Problems</span>
            <CheckCircle2 className="w-4 h-4 text-blue-500" />
          </div>
          <p className="text-3xl font-bold">{insights?.verified_problems ?? 0}</p>
        </div>
        <div className="glass rounded-xl p-5 border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted">Open Tasks</span>
            <Clock3 className="w-4 h-4 text-amber-500" />
          </div>
          <p className="text-3xl font-bold">{insights?.open_tasks ?? 0}</p>
        </div>
        <div className="glass rounded-xl p-5 border-l-4 border-l-green-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted">Completed Tasks</span>
            <CheckCircle2 className="w-4 h-4 text-green-500" />
          </div>
          <p className="text-3xl font-bold">{insights?.completed_tasks ?? 0}</p>
        </div>
        <div className="glass rounded-xl p-5 border-l-4 border-l-violet-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted">Total Matches</span>
            <Users className="w-4 h-4 text-violet-500" />
          </div>
          <p className="text-3xl font-bold">{insights?.total_matches ?? 0}</p>
        </div>
        <div className="glass rounded-xl p-5 border-l-4 border-l-cyan-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted">Average Match Score</span>
            <BrainCircuit className="w-4 h-4 text-cyan-500" />
          </div>
          <p className="text-3xl font-bold">{Number(insights?.average_match_score ?? 0).toFixed(2)}</p>
        </div>
      </div>
    </div>
  )
}
