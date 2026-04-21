import React from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bell, CheckCircle2, Info, AlertTriangle, Clock } from 'lucide-react'
import { api } from '../lib/api'
import { cn } from '../lib/utils'

export function Notifications() {
  const queryClient = useQueryClient()
  const { data: notifications, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: api.getNotifications,
    retry: 1
  })

  const markAsReadMutation = useMutation({
    mutationFn: (id: string) => api.markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    }
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  const sortedNotifications = notifications?.sort((a: any, b: any) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ) || []

  return (
    <div className="space-y-6 pb-20">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground/90">Notifications</h1>
          <p className="text-muted text-sm mt-1">Stay updated with the latest activity</p>
        </div>
      </div>

      <div className="glass rounded-2xl overflow-hidden divide-y divide-white/10">
        {sortedNotifications.length === 0 ? (
          <div className="p-10 text-center text-muted">
            <Bell className="w-10 h-10 mx-auto mb-4 opacity-20" />
            <p>No notifications yet</p>
          </div>
        ) : (
          sortedNotifications.map((notification: any) => (
            <div 
              key={notification.id} 
              className={cn(
                "p-5 flex gap-4 transition-colors",
                notification.status !== 'sent' ? 'bg-primary/5' : 'hover:bg-white/[0.02]'
              )}
            >
              <div className={cn(
                "p-2 rounded-lg shrink-0",
                notification.type === 'sms' ? 'bg-blue-500/10 text-blue-500' :
                notification.type === 'whatsapp' ? 'bg-green-500/10 text-green-500' :
                "bg-blue-500/10 text-blue-500"
              )}>
                {notification.status === 'failed' ? <AlertTriangle className="w-5 h-5" /> :
                 notification.status === 'sent' ? <CheckCircle2 className="w-5 h-5" /> :
                 <Info className="w-5 h-5" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <h3 className="font-semibold text-foreground/90 truncate">{notification.title}</h3>
                  <span className="text-[10px] text-muted flex items-center gap-1 whitespace-nowrap">
                    <Clock className="w-3 h-3" />
                    {new Date(notification.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-muted leading-relaxed">{notification.message}</p>
              </div>
              {notification.status !== 'sent' && (
                <button 
                  onClick={() => markAsReadMutation.mutate(String(notification.id))}
                  className="px-3 py-1 text-xs font-medium text-primary hover:bg-primary/10 rounded-md transition-colors h-fit"
                >
                  Mark read
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
