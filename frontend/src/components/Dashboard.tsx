import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { ArrowUpRight, ArrowDownRight, Calendar, Filter, Loader2, Bell } from 'lucide-react'
import { cn } from '../lib/utils'
import { api } from '../lib/api'
import { useFeedback } from '../lib/feedback'

export function Dashboard() {
  const { showError, showSuccess } = useFeedback()
  const storedId = localStorage.getItem('ngo_id');
  const ngoId = storedId && storedId !== 'null' ? parseInt(storedId, 10) : 0;

  // 1. Fetch Wallet Data
  const { data: walletData, isLoading: isWalletLoading } = useQuery({
    queryKey: ['wallet', ngoId],
    queryFn: () => api.getWallet(ngoId.toString()),
    enabled: ngoId > 0,
    retry: 1 
  });

  // 2. Fetch Donations Data
  const { data: donationsData, isLoading: isDonationsLoading } = useQuery({
    queryKey: ['donations'],
    queryFn: api.getDonations,
    retry: 1
  });

  const { data: notificationsData } = useQuery({
    queryKey: ['notifications_dashboard'],
    queryFn: api.getNotifications,
    retry: 1,
  })

  const parseAmount = (value: unknown) => {
    const amount = Number(value)
    return Number.isFinite(amount) ? amount : 0
  }

  const allDonations = Array.isArray(donationsData) ? donationsData : []
  const completedDonations = allDonations.filter((donation: any) => donation.status === 'completed')
  const totalDonationAmount = completedDonations.reduce(
    (sum: number, donation: any) => sum + parseAmount(donation.amount),
    0,
  )

  const walletBalance = parseAmount(walletData?.balance)
  const successRate = allDonations.length > 0 ? (completedDonations.length / allDonations.length) * 100 : 0
  const averageDonation = completedDonations.length > 0 ? totalDonationAmount / completedDonations.length : 0

  const displayStats = [
    {
      title: 'Wallet Balance',
      value: walletBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
      change: `${completedDonations.length} completed`,
      trend: 'up',
    },
    {
      title: 'Total Donations',
      value: allDonations.length.toString(),
      change: `${allDonations.length - completedDonations.length} pending/failed`,
      trend: 'up',
    },
    {
      title: 'Donation Success Rate',
      value: `${successRate.toFixed(1)}%`,
      change: `${completedDonations.length}/${allDonations.length || 0}`,
      trend: 'up',
    },
    {
      title: 'Average Donation',
      value: averageDonation.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
      change: 'Live backend data',
      trend: 'up',
    },
  ]

  const recentDonations = [...completedDonations]
    .sort((a: any, b: any) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    .slice(-7)

  const barData = recentDonations.map((donation: any) => ({
    name: new Date(donation.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    donations: parseAmount(donation.amount),
  }))

  let runningTotal = 0
  const areaData = barData.map((point) => {
    runningTotal += point.donations
    return { name: point.name, cumulative: runningTotal }
  })

  const recentNotifications = (Array.isArray(notificationsData) ? notificationsData : [])
    .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const userId = (form.elements.namedItem('userId') as HTMLInputElement).value;
    const role = (form.elements.namedItem('role') as HTMLSelectElement).value;
    try {
      await api.addNgoMember(ngoId.toString(), { user_id: parseInt(userId, 10), role });
      showSuccess('Member added successfully!');
      form.reset();
    } catch (err: any) {
      showError('Failed to add member: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="space-y-6 pb-20">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold tracking-tight text-foreground/90">Nonprofit Dashboard</h1>
          {(isWalletLoading || isDonationsLoading) && (
            <Loader2 className="w-5 h-5 text-primary animate-spin" />
          )}
        </div>
        
        <div className="flex items-center gap-3">
          <div className="glass rounded-lg p-1 flex items-center bg-surface/50">
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md hover:bg-white/5 transition-colors">
              <Calendar className="w-4 h-4 text-muted" />
              This Week
            </button>
          </div>
          <div className="glass rounded-lg p-1 flex items-center bg-surface/50">
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md hover:bg-white/5 transition-colors">
              Services: All
              <Filter className="w-3 h-3 text-muted ml-1" />
            </button>
          </div>
          <div className="glass rounded-lg p-1 flex items-center bg-surface/50">
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md hover:bg-white/5 transition-colors">
              Posts: All
              <Filter className="w-3 h-3 text-muted ml-1" />
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {displayStats.map((stat: any, i: number) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1, duration: 0.4 }}
            className="glass rounded-2xl p-5 hover:bg-white/[0.07] transition-all duration-300 relative overflow-hidden group"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <h3 className="text-xs font-medium text-muted mb-3 relative z-10">{stat.title}</h3>
            <div className="flex flex-col gap-1 relative z-10">
              <span className="text-2xl md:text-3xl font-bold tracking-tight">{stat.value}</span>
              <div className="flex items-center gap-1">
                {stat.trend === 'up' ? (
                  <ArrowUpRight className="w-3 h-3 text-primary" />
                ) : (
                  <ArrowDownRight className="w-3 h-3 text-red-500" />
                )}
                <span className={cn("text-xs font-medium", stat.trend === 'up' ? "text-primary" : "text-red-500")}>
                  {stat.change}
                </span>
              </div>
            </div>
            <p className="text-[10px] text-muted/70 mt-4 relative z-10">vs previous 7 days</p>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
          className="glass rounded-2xl p-6 h-[400px] flex flex-col"
        >
          <div className="mb-6">
            <h3 className="text-sm font-medium text-muted">Budget vs Actuals</h3>
          </div>
          <div className="flex-1 w-full relative">
            {areaData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={areaData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCumulative" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00d1b2" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#00d1b2" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="name" stroke="rgba(255,255,255,0.2)" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="rgba(255,255,255,0.2)" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(10, 10, 10, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Area type="monotone" dataKey="cumulative" stroke="#00d1b2" strokeWidth={2} fillOpacity={1} fill="url(#colorCumulative)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-muted">No donation trend data yet.</div>
            )}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.5 }}
          className="glass rounded-2xl p-6 h-[400px] flex flex-col"
        >
          <div className="mb-6">
            <h3 className="text-sm font-medium text-muted">Donations Over Time</h3>
          </div>
          <div className="flex-1 w-full relative">
            {barData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }} barSize={32}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="name" stroke="rgba(255,255,255,0.2)" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="rgba(255,255,255,0.2)" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    contentStyle={{ backgroundColor: 'rgba(10, 10, 10, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  />
                  <Bar dataKey="donations" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-muted">No donation records yet.</div>
            )}
          </div>
        </motion.div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.75, duration: 0.5 }}
          className="glass rounded-2xl p-6"
        >
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
              <Bell className="w-5 h-5 text-primary" />
              Recent Notifications
            </h3>
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
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.5 }}
          className="glass rounded-2xl p-6"
        >
          <div className="mb-6 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-foreground">Team Management</h3>
          </div>
          <form className="flex flex-col sm:flex-row gap-4 items-end" onSubmit={handleAddMember}>
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-muted mb-1">User ID</label>
              <input name="userId" type="number" required placeholder="Enter Volunteer/Member User ID" className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-muted mb-1">Role</label>
              <select name="role" required className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary">
                <option value="field_worker">Field Worker</option>
                <option value="manager">Manager</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <button type="submit" className="w-full sm:w-auto px-6 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors">
              Add Member
            </button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
