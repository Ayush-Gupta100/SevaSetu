import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Wallet as WalletIcon, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { api } from '../lib/api'

export function Finance() {
  const storedId = localStorage.getItem('ngo_id')
  const ngoId = storedId && storedId !== 'null' ? parseInt(storedId, 10) : 0
  const { data: walletData } = useQuery({ queryKey: ['wallet', ngoId], queryFn: () => api.getWallet(ngoId.toString()), enabled: ngoId > 0, retry: 1 })
  const { data: ledgerData } = useQuery({ queryKey: ['ledger', ngoId], queryFn: () => api.getLedger(ngoId.toString()), enabled: ngoId > 0, retry: 1 })

  const balance = Number(walletData?.balance ?? 0)
  const ledger = Array.isArray(ledgerData) ? ledgerData : []

  return (
    <div className="space-y-6 pb-20">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground/90">Financial Ledger</h1>
        <p className="text-muted text-sm mt-1">Transparent fund tracking and donations</p>
      </div>

      <div className="glass rounded-2xl p-8 max-w-md relative overflow-hidden group">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-50" />
        <div className="relative z-10">
          <div className="flex items-center gap-3 text-muted mb-4">
            <WalletIcon className="w-5 h-5 text-primary" />
            <h3 className="font-medium">NGO Wallet Balance</h3>
          </div>
          <div className="text-5xl font-bold tracking-tighter text-foreground">
            <span className="text-muted mr-2">$</span>
            {balance.toLocaleString()}
          </div>
          <button className="mt-6 w-full py-2.5 bg-primary/20 text-primary hover:bg-primary/30 font-medium rounded-lg transition-colors border border-primary/20">
            Withdraw Funds
          </button>
        </div>
      </div>

      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
        <div className="glass rounded-xl overflow-hidden">
          {ledger.length === 0 ? (
            <div className="p-6 text-sm text-muted">No ledger entries found.</div>
          ) : (
            ledger.map((tx: any, i: number) => (
              <div key={tx.id} className={`flex items-center justify-between p-4 ${i !== ledger.length - 1 ? 'border-b border-white/5' : ''} hover:bg-white/[0.02]`}>
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-full ${tx.type === 'credit' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                    {tx.type === 'credit' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                  </div>
                  <div>
                    <p className="font-medium text-foreground/90">{`${tx.reference_type || 'entry'} #${tx.reference_id ?? tx.id}`}</p>
                    <p className="text-xs text-muted">{new Date(tx.created_at).toLocaleString()}</p>
                  </div>
                </div>
                <div className={`font-semibold ${tx.type === 'credit' ? 'text-green-500' : 'text-foreground/90'}`}>
                  {tx.type === 'credit' ? '+' : '-'}${Number(tx.amount || 0).toLocaleString()}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
