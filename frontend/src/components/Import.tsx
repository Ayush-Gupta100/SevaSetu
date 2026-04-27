import React, { useState } from 'react'
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { api } from '../lib/api'
import { useFeedback } from '../lib/feedback'
import * as XLSX from 'xlsx'

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
  const { showError, showSuccess } = useFeedback()
  const ngoId = localStorage.getItem('ngo_id') || '0'
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [previewData, setPreviewData] = useState<any>(null)
  const [importId, setImportId] = useState<string | null>(null)
  const [importing, setImporting] = useState(false)
  const templateHeaders = ['name', 'email', 'phone', 'role', 'skills']
  const templateRows = [
    {
      name: 'Aarav Sharma',
      email: 'aarav.sharma@example.org',
      phone: '9876543210',
      role: 'field_worker',
      skills: 'first aid, logistics',
    },
    {
      name: 'Meera Iyer',
      email: 'meera.iyer@example.org',
      phone: '9988776655',
      role: 'manager',
      skills: 'coordination, reporting',
    },
  ]

  const handleDownloadCsvTemplate = () => {
    const csvLines = [
      templateHeaders.join(','),
      ...templateRows.map((row) =>
        templateHeaders
          .map((header) => {
            const value = String((row as any)[header] ?? '')
            if (value.includes(',') || value.includes('"') || value.includes('\n')) {
              return `"${value.replace(/"/g, '""')}"`
            }
            return value
          })
          .join(',')
      ),
    ]
    const blob = new Blob([csvLines.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'ngo-member-import-template.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  const handleDownloadExcelTemplate = () => {
    const workbook = XLSX.utils.book_new()
    const worksheet = XLSX.utils.json_to_sheet(templateRows, { header: templateHeaders })
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Members')
    XLSX.writeFile(workbook, 'ngo-member-import-template.xlsx')
  }

  const parseSheetRows = async (inputFile: File): Promise<Array<Record<string, string>>> => {
    const fileName = inputFile.name.toLowerCase()

    if (fileName.endsWith('.csv')) {
      const csvText = await inputFile.text()
      return parseCsv(csvText)
    }

    if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
      const buffer = await inputFile.arrayBuffer()
      const workbook = XLSX.read(buffer, { type: 'array' })
      const firstSheet = workbook.SheetNames[0]
      if (!firstSheet) {
        return []
      }

      const sheet = workbook.Sheets[firstSheet]
      const jsonRows = XLSX.utils.sheet_to_json<Record<string, any>>(sheet, { defval: '' })
      return jsonRows.map((row) =>
        Object.entries(row).reduce<Record<string, string>>((acc, [key, value]) => {
          acc[String(key)] = String(value ?? '').trim()
          return acc
        }, {})
      )
    }

    throw new Error('Unsupported file format. Use .csv, .xlsx or .xls')
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) return
    if (ngoId === '0') {
      showError('NGO context missing. Please login as NGO admin first.')
      return
    }

    setUploading(true)
    try {
      const rows = await parseSheetRows(file)
      if (!rows.length) {
        throw new Error('No data rows found in the uploaded file.')
      }

      const res = await api.uploadNgoMembersImport(ngoId, { file_name: file.name, rows })
      setImportId(res.import_id)
      
      // Fetch preview
      const preview = await api.previewNgoMembersImport(ngoId, res.import_id)
      setPreviewData(preview)
    } catch (err: any) {
      showError('Upload failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setUploading(false)
    }
  }

  const handleConfirm = async () => {
    if (!importId) return
    if (ngoId === '0') {
      showError('NGO context missing. Please login as NGO admin first.')
      return
    }

    setImporting(true)
    try {
      const result = await api.confirmNgoMembersImport(ngoId, importId)
      const created = result.created_members ?? 0
      const alreadyMembers = result.already_members ?? 0
      const failed = result.failed_rows ?? 0
      const tempCount = (result.temporary_passwords ?? []).length
      showSuccess(`Import completed. Created: ${created}, already members: ${alreadyMembers}, failed: ${failed}, temp passwords issued: ${tempCount}.`)
      setFile(null)
      setPreviewData(null)
      setImportId(null)
    } catch (err: any) {
      showError('Import failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setImporting(false)
    }
  }

  return (
    <div className="space-y-6 pb-20">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground/90">Data Import</h1>
        <p className="text-muted text-sm mt-1">Bulk register NGO members from CSV or Excel with convertible fields only.</p>
      </div>

      <div className="glass rounded-2xl p-8 text-center border-dashed border-2 border-white/10 hover:border-primary/50 transition-colors">
        {!previewData ? (
          <div className="max-w-md mx-auto">
            <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-xl font-bold mb-2">Upload your file</h3>
            <p className="text-muted mb-2">Select CSV or Excel to import NGO members.</p>
            <p className="text-xs text-muted mb-6">Accepted fields: name, email, phone, role, skills. Required: name, email.</p>
            <div className="flex flex-wrap justify-center gap-2 mb-6">
              <button
                type="button"
                onClick={handleDownloadCsvTemplate}
                className="px-3 py-2 rounded-lg border border-border text-xs font-medium text-foreground hover:bg-white/5"
              >
                Download CSV Template
              </button>
              <button
                type="button"
                onClick={handleDownloadExcelTemplate}
                className="px-3 py-2 rounded-lg border border-border text-xs font-medium text-foreground hover:bg-white/5"
              >
                Download Excel Template
              </button>
            </div>
            
            <input 
              type="file" 
              id="file-upload" 
              className="hidden" 
              onChange={handleFileChange}
              accept=".csv,.xlsx,.xls"
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
              Showing first {previewData.preview?.length || 0} valid entries. Total rows: {previewData.total_rows}, valid: {previewData.valid_rows}, invalid: {previewData.invalid_rows}
            </p>

            {!!previewData.invalid_entries?.length && (
              <div className="mt-4 rounded-xl border border-amber-500/30 bg-amber-500/10 p-4">
                <h4 className="text-sm font-semibold text-amber-300">Rows skipped (not convertible)</h4>
                <ul className="mt-2 space-y-1 text-xs text-amber-100">
                  {previewData.invalid_entries.slice(0, 8).map((item: any) => (
                    <li key={item.row_number}>Row {item.row_number}: {item.reason}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass p-6 rounded-2xl">
          <h4 className="font-bold mb-4">Supported Formats</h4>
          <ul className="space-y-3 text-sm text-muted">
            <li className="flex items-center gap-2 italic">• NGO member CSV (.csv)</li>
            <li className="flex items-center gap-2 italic">• NGO member Excel (.xlsx, .xls)</li>
            <li className="flex items-center gap-2 italic">• Columns: name, email, phone, role, skills</li>
          </ul>
        </div>
        <div className="glass p-6 rounded-2xl">
          <h4 className="font-bold mb-4">Import Guidelines</h4>
          <p className="text-sm text-muted leading-relaxed">
            Only convertible entries are accepted. Required fields are name and email. Role defaults to field_worker when missing. Newly created members receive a temporary password and must change it after first login.
          </p>
        </div>
      </div>
    </div>
  )
}
