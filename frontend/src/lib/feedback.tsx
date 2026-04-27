import React, { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react'
import { cn } from './utils'

type ToastType = 'success' | 'error' | 'info'

type ToastItem = {
  id: number
  type: ToastType
  message: string
  title?: string
}

type FeedbackContextValue = {
  showSuccess: (message: string, title?: string) => void
  showError: (message: string, title?: string) => void
  showInfo: (message: string, title?: string) => void
}

const FeedbackContext = createContext<FeedbackContextValue | null>(null)

function ToastIcon({ type }: { type: ToastType }) {
  if (type === 'success') return <CheckCircle2 className="w-5 h-5" />
  if (type === 'error') return <AlertCircle className="w-5 h-5" />
  return <Info className="w-5 h-5" />
}

function ToastHost({ toasts, onClose }: { toasts: ToastItem[]; onClose: (id: number) => void }) {
  return (
    <div className="fixed top-4 right-4 z-[100] flex w-[calc(100%-2rem)] max-w-sm flex-col gap-3 pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            'pointer-events-auto glass rounded-xl border p-4 shadow-xl backdrop-blur-md transition-all duration-300',
            toast.type === 'success' && 'border-emerald-400/30 bg-emerald-500/10 text-emerald-100',
            toast.type === 'error' && 'border-rose-400/30 bg-rose-500/10 text-rose-100',
            toast.type === 'info' && 'border-blue-400/30 bg-blue-500/10 text-blue-100',
          )}
          role="status"
          aria-live="polite"
        >
          <div className="flex items-start gap-3">
            <div className="mt-0.5 shrink-0">
              <ToastIcon type={toast.type} />
            </div>
            <div className="flex-1">
              {toast.title && <div className="text-sm font-semibold leading-5">{toast.title}</div>}
              <p className="text-sm leading-5 text-white/90">{toast.message}</p>
            </div>
            <button
              type="button"
              onClick={() => onClose(toast.id)}
              className="rounded-md p-1 text-white/70 hover:bg-white/10 hover:text-white transition-colors"
              aria-label="Dismiss notification"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

export function FeedbackProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((item) => item.id !== id))
  }, [])

  const pushToast = useCallback((type: ToastType, message: string, title?: string) => {
    const id = Date.now() + Math.floor(Math.random() * 1000)
    setToasts((prev) => [...prev, { id, type, message, title }])
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((item) => item.id !== id))
    }, 4200)
  }, [])

  const value = useMemo<FeedbackContextValue>(
    () => ({
      showSuccess: (message, title) => pushToast('success', message, title),
      showError: (message, title) => pushToast('error', message, title),
      showInfo: (message, title) => pushToast('info', message, title),
    }),
    [pushToast],
  )

  return (
    <FeedbackContext.Provider value={value}>
      {children}
      <ToastHost toasts={toasts} onClose={removeToast} />
    </FeedbackContext.Provider>
  )
}

export function useFeedback() {
  const context = useContext(FeedbackContext)
  if (!context) {
    throw new Error('useFeedback must be used within FeedbackProvider')
  }
  return context
}