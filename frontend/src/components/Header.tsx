import { Search, Bell } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { api, clearAuthStorage } from '../lib/api'
import { ThemeToggle } from './ThemeToggle'

export function Header() {
  const navigate = useNavigate()
  const userName = localStorage.getItem('user_name') || 'Operator'

  const handleLogout = async () => {
    try {
      await api.logout()
    } catch {
      // Ignore logout API failures and clear local session anyway.
    } finally {
      clearAuthStorage()
      navigate('/login')
    }
  }

  return (
    <header className="h-16 flex items-center justify-between px-6 glass border-x-0 border-t-0 sticky top-0 z-20">
      <div className="flex-1 max-w-md relative group">
        <Search className="w-4 h-4 text-muted absolute left-3 top-1/2 -translate-y-1/2 group-focus-within:text-primary transition-colors" />
        <input
          type="text"
          placeholder="Search everywhere... (Ctrl+K)"
          className="w-full bg-white border border-border rounded-full py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all placeholder:text-muted text-foreground shadow-sm"
        />
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
          <kbd className="hidden sm:inline-block bg-slate-100 border border-border rounded px-1.5 py-0.5 text-[10px] font-medium text-muted">Ctrl</kbd>
          <kbd className="hidden sm:inline-block bg-slate-100 border border-border rounded px-1.5 py-0.5 text-[10px] font-medium text-muted">K</kbd>
        </div>
      </div>

      <div className="flex items-center gap-4 ml-4">
        <ThemeToggle className="px-2.5 py-1.5 text-xs shadow-none" />
        <Link to="/notifications" className="relative p-2 rounded-full hover:bg-slate-100 text-muted hover:text-foreground transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full ring-2 ring-white"></span>
        </Link>
        <div className="hidden md:block text-xs text-muted">Signed in as {userName}</div>
        <button
          type="button"
          onClick={handleLogout}
          className="px-3 py-1.5 rounded-lg bg-slate-100 text-xs font-medium text-foreground hover:bg-slate-200 transition-colors"
        >
          Logout
        </button>
      </div>
    </header>
  )
}
