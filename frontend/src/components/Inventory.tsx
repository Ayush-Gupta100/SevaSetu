import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Package } from 'lucide-react'
import { api } from '../lib/api'
import { useFeedback } from '../lib/feedback'

export function Inventory() {
  const { showError, showSuccess } = useFeedback()
  const { data, refetch } = useQuery({ queryKey: ['inventory'], queryFn: api.getInventory, retry: 1 })
  const inventory = Array.isArray(data) ? data : []

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState({ resource_type_id: 1, quantity_total: '', address: '' })
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const geo = await api.geocode({ address: formData.address, country: 'India' })
      await api.addInventory({
        resource_type_id: formData.resource_type_id,
        quantity_total: parseFloat(formData.quantity_total),
        location_id: geo.location_id,
      })
      showSuccess('Resource added successfully!')
      setIsModalOpen(false)
      setFormData({ resource_type_id: 1, quantity_total: '', address: '' })
      refetch()
    } catch (err: any) {
      showError('Failed to add resource: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6 pb-20 relative">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground/90">Resource Intelligence</h1>
          <p className="text-muted text-sm mt-1">Real-time inventory and allocation</p>
        </div>
        <button onClick={() => setIsModalOpen(true)} className="px-4 py-2 bg-primary/20 text-primary hover:bg-primary/30 font-medium text-sm rounded-lg transition-colors border border-primary/20">
          + Add Resource
        </button>
      </div>

      <div className="glass rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface/50 border-b border-white/10 text-muted">
            <tr>
              <th className="px-6 py-4 font-medium">Resource ID / Name</th>
              <th className="px-6 py-4 font-medium">Type</th>
              <th className="px-6 py-4 font-medium">Quantity Available</th>
              <th className="px-6 py-4 font-medium">Location</th>
              <th className="px-6 py-4 font-medium text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {inventory.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-6 text-center text-sm text-muted">No inventory records found.</td>
              </tr>
            )}

            {inventory.map((item: any) => (
              <tr key={item.id} className="hover:bg-white/[0.02] transition-colors">
                <td className="px-6 py-4 font-medium text-foreground/90 flex items-center gap-3">
                  <Package className="w-4 h-4 text-primary" />
                  {item.name || `Type ID: ${item.resource_type_id}`}
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 rounded bg-white/5 text-xs uppercase tracking-wider">{item.type || item.owner_type}</span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-full max-w-[100px] h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary"
                        style={{
                          width: `${Math.max(
                            0,
                            Math.min(
                              100,
                              Number(item.quantity_total || 0) > 0
                                ? (Number(item.quantity_available || 0) / Number(item.quantity_total || 0)) * 100
                                : 0,
                            ),
                          )}%`,
                        }}
                      />
                    </div>
                    <span className="font-mono">{item.quantity_available}</span>
                    <span className="text-muted text-xs">{item.unit || 'units'}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-muted">{item.location_address || 'Unknown Location'}</td>
                <td className="px-6 py-4 text-right">
                  <button className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded text-xs transition-colors">
                    Allocate
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-surface border border-white/10 rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 className="text-xl font-bold text-foreground mb-4">Add Inventory</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Resource Type ID</label>
                <input type="number" required value={formData.resource_type_id} onChange={e => setFormData({...formData, resource_type_id: parseInt(e.target.value)})} className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary" placeholder="1" />
                <p className="text-xs text-muted mt-1">Hint: Use ID 1 (Financial), 2 (Material), or 3 (Human).</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Total Quantity</label>
                <input type="number" step="0.01" required value={formData.quantity_total} onChange={e => setFormData({...formData, quantity_total: e.target.value})} className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary" placeholder="100" />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted mb-1">Resource Location Address (Mandatory)</label>
                <input type="text" required value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary" placeholder="Street, city, state" />
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setIsModalOpen(false)} className="flex-1 px-4 py-2 border border-border text-foreground font-medium rounded-lg hover:bg-white/5 transition-colors">
                  Cancel
                </button>
                <button type="submit" disabled={submitting} className="flex-1 px-4 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-hover transition-colors disabled:opacity-50">
                  {submitting ? 'Adding...' : 'Add Resource'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
