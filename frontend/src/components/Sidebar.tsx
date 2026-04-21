import React from 'react'
import { NavLink } from 'react-router-dom'
import { LayoutDashboard, AlertCircle, CheckSquare, Package, Wallet, BrainCircuit, Hexagon, Bell, FileUp, Users } from 'lucide-react'
import { cn } from '../lib/utils'

export function Sidebar() {
  const userName = localStorage.getItem('user_name') || 'NGO Member'
  const userRole = localStorage.getItem('user_role') || 'operator'
  const isAdminView = userRole === 'ngo_admin'
  const navItems = isAdminView
    ? [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
        { icon: Users, label: 'Team', path: '/team' },
        { icon: AlertCircle, label: 'Problems', path: '/problems' },
        { icon: CheckSquare, label: 'Tasks', path: '/tasks' },
        { icon: Package, label: 'Inventory', path: '/inventory' },
        { icon: Wallet, label: 'Finance', path: '/finance' },
        { icon: BrainCircuit, label: 'AI Insights', path: '/insights' },
        { icon: Bell, label: 'Notifications', path: '/notifications' },
        { icon: FileUp, label: 'Data Import', path: '/import' },
      ]
    : [
        { icon: LayoutDashboard, label: 'My Dashboard', path: '/member-dashboard' },
        { icon: AlertCircle, label: 'Problems', path: '/problems' },
        { icon: CheckSquare, label: 'My Tasks', path: '/tasks' },
        { icon: Bell, label: 'Notifications', path: '/notifications' },
      ]

  return (
    <aside className="w-64 flex-shrink-0 glass border-y-0 border-l-0 flex flex-col h-full z-10">
      <div className="h-16 flex items-center px-6 border-b border-border/50">
        <Hexagon className="w-8 h-8 text-primary" />
        <span className="ml-3 font-bold text-lg tracking-wide text-foreground">Seva<span className="text-primary">Setu</span></span>
      </div>
      
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                "flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group relative",
                isActive
                  ? "text-primary bg-primary/10"
                  : "text-muted hover:text-foreground hover:bg-slate-100"
              )
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-primary rounded-r-full" />
                )}
                <item.icon className={cn("w-5 h-5 mr-3", isActive ? "text-primary" : "text-muted group-hover:text-primary")} />
                {item.label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-border/50">
        <div className="bg-slate-50 border border-border/50 rounded-lg p-4 flex items-center">
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-sm">
            AG
          </div>
          <div className="ml-3 flex-1 overflow-hidden">
            <p className="text-sm font-medium text-foreground truncate">{userName}</p>
            <p className="text-xs text-muted truncate">{userRole.replace('_', ' ')}</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
