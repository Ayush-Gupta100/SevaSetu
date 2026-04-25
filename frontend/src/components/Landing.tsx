import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Hexagon, ArrowRight, ShieldCheck, Globe, Activity, Loader2, HeartHandshake, HandCoins } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { ThemeToggle } from './ThemeToggle'

export function Landing() {
  const token = localStorage.getItem('jwt_token')
  const [selectedProblem, setSelectedProblem] = useState<any>(null)
  const [showContributeModal, setShowContributeModal] = useState(false)
  const [donationNgoId, setDonationNgoId] = useState('')
  const [donationAmount, setDonationAmount] = useState('')
  const [volunteerForm, setVolunteerForm] = useState({ name: '', email: '', phone: '', password: '' })
  const [contributeLoading, setContributeLoading] = useState(false)
  const [contributeMessage, setContributeMessage] = useState('')

  const { data: stats, isLoading: statsLoading } = useQuery({ 
    queryKey: ['public_stats'], 
    queryFn: api.getPublicStats 
  })
  
  const { data: problems, isLoading: problemsLoading } = useQuery({ 
    queryKey: ['public_problems'], 
    queryFn: api.getPublicProblems 
  })

  const openContribute = (problem: any) => {
    setSelectedProblem(problem)
    setContributeMessage('')
    setShowContributeModal(true)
  }

  const handleDonate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!token) {
      setContributeMessage('Please sign in first to donate.')
      return
    }
    setContributeLoading(true)
    setContributeMessage('')
    try {
      await api.createDonation({
        ngo_id: Number(donationNgoId),
        amount: Number(donationAmount),
        currency: 'INR',
      })
      setContributeMessage('Donation created successfully. Thank you for contributing.')
      setDonationAmount('')
    } catch (err: any) {
      setContributeMessage(err.response?.data?.detail || 'Failed to create donation.')
    } finally {
      setContributeLoading(false)
    }
  }

  const handleVolunteer = async (e: React.FormEvent) => {
    e.preventDefault()
    setContributeLoading(true)
    setContributeMessage('')
    try {
      if (token) {
        const res = await api.publicVolunteerOptIn()
        setContributeMessage(res.message || 'You are now registered as a volunteer.')
      } else {
        const res = await api.publicJoin(volunteerForm)
        setContributeMessage(res.message || 'Volunteer registration successful.')
      }
    } catch (err: any) {
      setContributeMessage(err.response?.data?.detail || 'Failed to register for volunteering.')
    } finally {
      setContributeLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <header className="px-8 py-6 flex items-center justify-between border-b border-border/40 bg-white/50 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center">
          <Hexagon className="w-8 h-8 text-primary" />
          <span className="ml-3 font-bold text-xl tracking-wide">Seva<span className="text-primary">Setu</span></span>
        </div>
        <div className="flex items-center gap-4">
          <ThemeToggle className="px-2.5 py-1.5 text-xs shadow-none" />
          <Link to="/login" className="text-sm font-medium text-muted hover:text-foreground transition-colors">Sign In</Link>
          <Link to="/register" className="px-4 py-2 bg-primary text-white text-sm font-medium rounded-full hover:bg-primary-hover transition-colors shadow-sm">
            Get Started
          </Link>
        </div>
      </header>

      <main className="flex-1">
        <section className="py-24 px-8 max-w-6xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-widest mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            System Online
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-foreground mb-6">
            Community Problem <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500">Coordination Engine</span>
          </h1>
          <p className="text-lg md:text-xl text-muted max-w-2xl mx-auto mb-10 leading-relaxed">
            Report problems, verify field conditions, create tasks, assign volunteers, and allocate resources from one connected NGO operations platform.
          </p>
          
          {statsLoading ? (
            <div className="flex items-center justify-center gap-2 text-muted mb-10">
              <Loader2 className="w-4 h-4 animate-spin" />
              Loading network stats...
            </div>
          ) : stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto mb-16 px-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary">{stats.total_ngos}</div>
                <div className="text-xs text-muted uppercase tracking-widest mt-1">Partner NGOs</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary">{stats.total_volunteers || 0}</div>
                <div className="text-xs text-muted uppercase tracking-widest mt-1">Volunteers</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary">{stats.total_problems || 0}</div>
                <div className="text-xs text-muted uppercase tracking-widest mt-1">Problems Reported</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary">{stats.total_tasks || 0}</div>
                <div className="text-xs text-muted uppercase tracking-widest mt-1">Tasks Created</div>
              </div>
            </div>
          )}

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register" className="px-8 py-4 bg-foreground text-background font-medium rounded-full hover:bg-slate-800 transition-colors flex items-center gap-2 w-full sm:w-auto justify-center">
              Join as Volunteer <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/register?type=ngo" className="px-8 py-4 bg-white border border-border text-foreground font-medium rounded-full hover:bg-slate-50 transition-colors w-full sm:w-auto justify-center text-center shadow-sm">
              Register NGO
            </Link>
          </div>
        </section>

        <section className="py-20 bg-surface border-y border-border/40 overflow-hidden">
          <div className="max-w-6xl mx-auto px-8">
            <h2 className="text-3xl font-bold text-center mb-12">Active Critical Problems</h2>
            {problemsLoading ? (
              <div className="flex justify-center p-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
            ) : (
              <div className="grid md:grid-cols-3 gap-6">
                {(problems || []).slice(0, 3).map((problem: any) => (
                  <div key={problem.id} className="glass p-6 rounded-2xl border border-white/5 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-3">
                      <div className="px-2 py-0.5 rounded-full bg-red-500/10 text-red-500 text-[10px] font-bold uppercase">Critical</div>
                    </div>
                    <h3 className="text-lg font-bold mb-3 mt-4 truncate">{problem.title}</h3>
                    <p className="text-sm text-muted mb-6 line-clamp-2">{problem.description}</p>
                    <div className="flex items-center justify-between text-xs text-muted gap-3">
                      <span>{problem.category}</span>
                      <button
                        onClick={() => openContribute(problem)}
                        className="text-primary font-bold group-hover:underline flex items-center gap-1"
                      >
                        Contribute <ArrowRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        <section className="py-24 px-8 max-w-6xl mx-auto grid md:grid-cols-3 gap-8">
            <div className="glass p-8 rounded-2xl">
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6">
                <ShieldCheck className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Transparent Allocation</h3>
              <p className="text-muted leading-relaxed">Ledger-based tracking for all donations and resource distributions. Every action is verifiable.</p>
            </div>
            <div className="glass p-8 rounded-2xl">
              <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center mb-6">
                <Activity className="w-6 h-6 text-blue-500" />
              </div>
              <h3 className="text-xl font-bold mb-3">AI Intelligence</h3>
              <p className="text-muted leading-relaxed">Smart algorithms automatically match community problems with the right volunteers and NGO resources.</p>
            </div>
            <div className="glass p-8 rounded-2xl">
              <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center mb-6">
                <Globe className="w-6 h-6 text-purple-500" />
              </div>
              <h3 className="text-xl font-bold mb-3">Community Command</h3>
              <p className="text-muted leading-relaxed">A unified dashboard that gives you complete oversight of local infrastructure challenges and health crises.</p>
            </div>
        </section>

        <section className="py-20 bg-surface border-y border-border/40">
          <div className="max-w-6xl mx-auto px-8 grid md:grid-cols-2 gap-10 items-start">
            <div className="glass p-8 rounded-2xl">
              <h2 className="text-3xl font-bold mb-4">About Us</h2>
              <p className="text-muted leading-relaxed mb-4">
                SevaSetu is a civic coordination platform that connects NGOs, volunteers, and community contributors to solve real-world problems faster.
                The website helps teams report field issues, assign tasks, track funds, and monitor progress in one unified workflow.
              </p>
              <p className="text-muted leading-relaxed">
                Our mission is to bridge community needs with the right people and resources. From donation tracking to volunteer onboarding,
                SevaSetu is built to keep every action transparent, accountable, and impact-driven.
              </p>
            </div>

            <div className="glass p-8 rounded-2xl">
              <h2 className="text-3xl font-bold mb-4">Website Highlights</h2>
              <ul className="space-y-3 text-muted leading-relaxed">
                <li>Unified NGO operations dashboard for tasks, resources, and crisis response.</li>
                <li>Public problem feed where anyone can donate money or volunteer to contribute.</li>
                <li>Role-based access for NGOs, members, and volunteers with secure authentication.</li>
                <li>Financial visibility through structured ledger and donation records.</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="py-20 px-8 max-w-6xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold">Our Team</h2>
            <p className="text-muted mt-2">Built by engineers focused on practical social impact technology.</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass p-8 rounded-2xl">
              <h3 className="text-2xl font-bold text-foreground">Vansh Agarwal</h3>
              <p className="text-primary font-semibold mt-1">Backend Engineer</p>
              <p className="text-muted mt-4 leading-relaxed">
                Designs and maintains the API architecture, authentication flows, data models, and operational reliability for SevaSetu.
                Focused on secure, scalable backend systems that support real-time NGO operations.
              </p>
            </div>

            <div className="glass p-8 rounded-2xl">
              <h3 className="text-2xl font-bold text-foreground">Ayush Gupta</h3>
              <p className="text-primary font-semibold mt-1">Frontend Engineer</p>
              <p className="text-muted mt-4 leading-relaxed">
                Crafts the user experience across dashboards and public pages, ensuring the platform is intuitive, responsive,
                and accessible for NGOs, volunteers, and contributors.
              </p>
            </div>
          </div>
        </section>
      </main>

      {showContributeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-surface border border-white/10 rounded-2xl shadow-xl w-full max-w-2xl p-6">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="text-xl font-bold text-foreground">Contribute to this Problem</h3>
                <p className="text-sm text-muted mt-1">{selectedProblem?.title}</p>
              </div>
              <button onClick={() => setShowContributeModal(false)} className="text-muted hover:text-foreground">Close</button>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mt-6">
              <form onSubmit={handleDonate} className="glass rounded-xl p-4 space-y-3">
                <div className="flex items-center gap-2 text-foreground font-semibold">
                  <HandCoins className="w-4 h-4 text-primary" />
                  Donate Money
                </div>
                <p className="text-xs text-muted">Enter NGO ID and amount to create a donation for this cause.</p>
                <input
                  type="number"
                  min={1}
                  required
                  value={donationNgoId}
                  onChange={(e) => setDonationNgoId(e.target.value)}
                  placeholder="NGO ID"
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
                <input
                  type="number"
                  min={1}
                  required
                  value={donationAmount}
                  onChange={(e) => setDonationAmount(e.target.value)}
                  placeholder="Amount (INR)"
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
                <button
                  type="submit"
                  disabled={contributeLoading}
                  className="w-full px-4 py-2 rounded-lg bg-primary text-white font-medium hover:bg-primary-hover transition-colors disabled:opacity-50"
                >
                  {contributeLoading ? 'Processing...' : 'Donate Now'}
                </button>
              </form>

              <form onSubmit={handleVolunteer} className="glass rounded-xl p-4 space-y-3">
                <div className="flex items-center gap-2 text-foreground font-semibold">
                  <HeartHandshake className="w-4 h-4 text-primary" />
                  Volunteer
                </div>
                {token ? (
                  <>
                    <p className="text-xs text-muted">Use one click to join as a volunteer and start helping.</p>
                    <button
                      type="submit"
                      disabled={contributeLoading}
                      className="w-full px-4 py-2 rounded-lg border border-border text-foreground font-medium hover:bg-slate-100 transition-colors disabled:opacity-50"
                    >
                      {contributeLoading ? 'Submitting...' : 'Join as Volunteer'}
                    </button>
                  </>
                ) : (
                  <>
                    <p className="text-xs text-muted">Create a volunteer account to contribute on ground.</p>
                    <input
                      type="text"
                      required
                      value={volunteerForm.name}
                      onChange={(e) => setVolunteerForm({ ...volunteerForm, name: e.target.value })}
                      placeholder="Full name"
                      className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                    <input
                      type="email"
                      required
                      value={volunteerForm.email}
                      onChange={(e) => setVolunteerForm({ ...volunteerForm, email: e.target.value })}
                      placeholder="Email"
                      className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                    <input
                      type="text"
                      value={volunteerForm.phone}
                      onChange={(e) => setVolunteerForm({ ...volunteerForm, phone: e.target.value })}
                      placeholder="Phone (optional)"
                      className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                    <input
                      type="password"
                      required
                      value={volunteerForm.password}
                      onChange={(e) => setVolunteerForm({ ...volunteerForm, password: e.target.value })}
                      placeholder="Create password"
                      className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                    <button
                      type="submit"
                      disabled={contributeLoading}
                      className="w-full px-4 py-2 rounded-lg border border-border text-foreground font-medium hover:bg-slate-100 transition-colors disabled:opacity-50"
                    >
                      {contributeLoading ? 'Submitting...' : 'Register as Volunteer'}
                    </button>
                  </>
                )}
              </form>
            </div>

            {contributeMessage && (
              <div className="mt-4 p-3 rounded-lg bg-slate-100 text-sm text-foreground border border-border/60">{contributeMessage}</div>
            )}
          </div>
        </div>
      )}
      
      <footer className="py-8 text-center text-muted border-t border-border/40 text-sm">
        &copy; {new Date().getFullYear()} SevaSetu. Coordinating NGOs, volunteers, and resources.
      </footer>
    </div>
  )
}
