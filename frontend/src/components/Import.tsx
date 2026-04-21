import React, { useState } from 'react'
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { api } from '../lib/api'

function parseCsv(text: string): Array<Record<string, string>> {
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0)

  if (lines.length < 2) {
    return []
  }

  const headers = lines[0].split(',').map((h) => h.trim())
  return lines.slice(1).map((line) => {
    const values = line.split(',').map((v) => v.trim())
    return headers.reduce<Record<string, string>>((acc, key, idx) => {
      acc[key] = values[idx] || ''
      return acc
    }, {})
  })
}

export function DataImport() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [previewData, setPreviewData] = useState<any>(null)
  const [importId, setImportId] = useState<string | null>(null)
  const [importing, setImporting] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    try {
      if (!file.name.toLowerCase().endsWith('.csv')) {
        throw new Error('Please upload a CSV file. Excel parsing is not enabled yet.')
      }

      const csvText = await file.text()
      const rows = parseCsv(csvText)
      const res = await api.importUpload({ file_name: file.name, rows })
      setImportId(res.import_id)
      
      // Fetch preview
      const preview = await api.importPreview(res.import_id)
      setPreviewData(preview)
    } catch (err: any) {
      alert('Upload failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setUploading(false)
    }
  }

  const handleConfirm = async () => {
    if (!importId) return
    setImporting(true)
    try {
      await api.importConfirm(importId)
      alert('Data imported successfully!')
      setFile(null)
      setPreviewData(null)
      setImportId(null)
    } catch (err: any) {
      alert('Import failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setImporting(false)
    }
  }

  return (
    <div className="space-y-6 pb-20">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground/90">Data Import</h1>
        <p className="text-muted text-sm mt-1">Bulk upload NGOs, resources, or community data via CSV</p>
      </div>

      <div className="glass rounded-2xl p-8 text-center border-dashed border-2 border-white/10 hover:border-primary/50 transition-colors">
        {!previewData ? (
          <div className="max-w-md mx-auto">
            <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-xl font-bold mb-2">Upload your file</h3>
            <p className="text-muted mb-6">Select a CSV file to begin the import process.</p>
            
            <input 
              type="file" 
              id="file-upload" 
              className="hidden" 
              onChange={handleFileChange}
              accept=".csv"
            />
            <label 
              htmlFor="file-upload"
              className="px-6 py-3 bg-white border border-border text-foreground font-medium rounded-full hover:bg-slate-50 transition-colors cursor-pointer inline-flex items-center gap-2 mb-4"
            >
              <FileText className="w-4 h-4" />
              {file ? file.name : 'Choose File'}
            </label>

            {file && (
              <button 
                onClick={handleUpload}
                disabled={uploading}
                className="w-full py-3 bg-primary text-white font-bold rounded-xl hover:bg-primary-hover transition-all flex items-center justify-center gap-2 shadow-lg shadow-primary/20"
              >
                {uploading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Analyze File'}
              </button>
            )}
          </div>
        ) : (
          <div className="text-left">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3 text-green-500">
                <CheckCircle2 className="w-6 h-6" />
                <h3 className="text-xl font-bold text-foreground">Preview Analysis Complete</h3>
              </div>
              <div className="flex gap-3">
                <button onClick={() => setPreviewData(null)} className="px-4 py-2 border border-border rounded-lg text-sm hover:bg-white/5">
                  Cancel
                </button>
                <button 
                  onClick={handleConfirm}
                  disabled={importing}
                  className="px-6 py-2 bg-primary text-white font-bold rounded-lg hover:bg-primary-hover flex items-center gap-2"
                >
                  {importing ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Confirm Import'}
                </button>
              </div>
            </div>

            <div className="bg-background/50 rounded-xl overflow-hidden border border-white/5">
              <table className="w-full text-sm text-left">
                <thead className="bg-white/5 text-muted">
                  <tr>
                    {Object.keys(previewData.preview?.[0] || {}).map(key => (
                      <th key={key} className="px-4 py-3 font-medium capitalize">{key.replace('_', ' ')}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {previewData.preview?.map((row: any, i: number) => (
                    <tr key={i} className="hover:bg-white/[0.02]">
                      {Object.values(row).map((val: any, j: number) => (
                        <td key={j} className="px-4 py-3 text-foreground/80">{val?.toString()}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-4 text-sm text-muted flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Showing first {previewData.preview?.length || 0} records. Total records detected: {previewData.rows_count}
            </p>
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass p-6 rounded-2xl">
          <h4 className="font-bold mb-4">Supported Formats</h4>
          <ul className="space-y-3 text-sm text-muted">
            <li className="flex items-center gap-2 italic">• NGO registry CSV</li>
            <li className="flex items-center gap-2 italic">• Resource inventory CSV</li>
            <li className="flex items-center gap-2 italic">• Volunteer list CSV</li>
          </ul>
        </div>
        <div className="glass p-6 rounded-2xl">
          <h4 className="font-bold mb-4">Import Guidelines</h4>
          <p className="text-sm text-muted leading-relaxed">
            Ensure your columns match our templates. The AI will attempt to map headers automatically, but human verification is required before final commit.
          </p>
        </div>
      </div>
    </div>
  )
}
