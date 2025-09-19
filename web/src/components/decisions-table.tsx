// components/decisions-table.tsx
"use client"

import * as React from "react"
import { useMemo, useState } from "react"
import { usePathname, useRouter, useSearchParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ArrowLeft, ArrowRight, RefreshCw, Filter, Download, AlertCircle, CheckCircle, XCircle } from "lucide-react"

export interface Decision {
  id: string
  event_id?: string
  decision: "allow" | "deny" | "review"
  risk_score?: number
  reasons: string[]
  rules_fired: string[]
  created_at: string
}

export interface DecisionsResponse {
  decisions: Decision[]
  total: number
  page: number
  limit: number
}

type Props = {
  initialData: DecisionsResponse
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

function getDecisionBadgeVariant(decision: string) {
  switch (decision) {
    case "allow":
      return "default"
    case "deny":
      return "destructive"
    case "review":
      return "secondary"
    default:
      return "outline"
  }
}

function getDecisionColor(decision: string) {
  switch (decision) {
    case "allow":
      return "text-green-600"
    case "deny":
      return "text-red-600"
    case "review":
      return "text-yellow-600"
    default:
      return "text-gray-600"
  }
}

function getDecisionIcon(decision: string) {
  switch (decision) {
    case "allow":
      return <CheckCircle className="w-4 h-4" />
    case "deny":
      return <XCircle className="w-4 h-4" />
    case "review":
      return <AlertCircle className="w-4 h-4" />
    default:
      return null
  }
}

export default function DecisionsTable({ initialData }: Props) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  // Local state for client-side controls
  const [isLoading, setIsLoading] = useState(false)
  const [data, setData] = useState<DecisionsResponse>(initialData)
  const [query, setQuery] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Read page/limit from URL so controls stay in sync with server state & shareable
  const page = useMemo(() => Number(searchParams.get("page") || initialData.page || 1), [searchParams, initialData.page])
  const limit = useMemo(() => Number(searchParams.get("limit") || initialData.limit || 20), [searchParams, initialData.limit])

  const totalPages = Math.max(1, Math.ceil((data.total ?? 0) / (data.limit || limit)))

  // Clear messages after a delay
  React.useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [error])

  React.useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 3000)
      return () => clearTimeout(timer)
    }
  }, [successMessage])

  // Fetcher that respects current page/limit and optional query
  const fetchPage = React.useCallback(
    async (nextPage: number, nextLimit = limit, q = query) => {
      setIsLoading(true)
      setError(null)
      try {
        const qs = new URLSearchParams({ page: String(nextPage), page_size: String(nextLimit) })
        if (q.trim()) qs.set("q", q.trim())
        
        const res = await fetch(`${API_BASE}/api/proxy/decisions?${qs.toString()}`, { 
          cache: "no-store",
          headers: {
            'Content-Type': 'application/json',
          }
        })
        
        if (!res.ok) {
          const errorText = await res.text()
          throw new Error(`Failed to fetch decisions: ${res.status} ${errorText}`)
        }
        
        const json = (await res.json()) as DecisionsResponse
        setData(json)

        // Update URL (shallow) so back/forward works and page is shareable
        const newURL = new URL(window.location.href)
        newURL.searchParams.set("page", String(json.page || nextPage))
        newURL.searchParams.set("limit", String(json.limit || nextLimit))
        if (q.trim()) newURL.searchParams.set("q", q.trim())
        else newURL.searchParams.delete("q")
        router.replace(newURL.toString())
        
        setSuccessMessage(`Loaded page ${json.page} of decisions`)
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : 'An unexpected error occurred'
        setError(errorMessage)
        console.error('Error fetching decisions:', e)
      } finally {
        setIsLoading(false)
      }
    },
    [limit, query, router]
  )

  // Actions
  const onPrev = () => {
    if (page <= 1 || isLoading) return
    fetchPage(page - 1)
  }

  const onNext = () => {
    if (page >= totalPages || isLoading) return
    fetchPage(page + 1)
  }

  const onRefresh = async () => {
    setIsLoading(true)
    setError(null)
    try {
      // Next.js app router: reloading same URL is enough to refetch (no-store)
      router.refresh()
      await fetchPage(page)
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : 'Failed to refresh data'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const onSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (isLoading) return
    // Jump back to page 1 when applying a new query
    await fetchPage(1, limit, query)
  }

  const onExportCSV = () => {
    if (data.decisions.length === 0) return
    
    try {
      const headers = ["decision_id", "event_id", "decision", "risk_score", "reasons", "rules_fired", "created_at"]
      const rows = data.decisions.map((d) => [
        d.id,
        d.event_id || "",
        d.decision,
        d.risk_score != null ? String(d.risk_score) : "",
        (d.reasons || []).join("; "),
        (d.rules_fired || []).join("; "),
        d.created_at,
      ])

      const csv = [headers, ...rows].map((r) =>
        r
          .map((cell) => {
            const s = String(cell ?? "")
            // CSV-escape
            return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
          })
          .join(",")
      ).join("\n")

      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `decisions_page-${page}_${new Date().toISOString().split('T')[0]}.csv`
      a.setAttribute('aria-label', `Download decisions from page ${page} as CSV`)
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
      
      setSuccessMessage(`Exported ${data.decisions.length} decisions to CSV`)
    } catch (e) {
      setError('Failed to export CSV file')
      console.error('CSV export error:', e)
    }
  }

  return (
    <Card>
      <CardHeader className="space-y-2">
        <div className="flex items-center justify-between">
          <CardTitle>Recent Decisions</CardTitle>
          <div className="flex gap-2">
            <form onSubmit={onSearch} className="hidden md:flex items-center gap-2">
              <Input
                placeholder="Search (id, reason...)"
                value={query}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
                className="w-56"
                disabled={isLoading}
                aria-label="Search decisions"
              />
              <Button type="submit" variant="outline" size="sm" disabled={isLoading}>
                <Filter className="w-4 h-4 mr-2" />
                Apply
              </Button>
            </form>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onExportCSV} 
              disabled={data.decisions.length === 0 || isLoading}
              aria-label={`Export ${data.decisions.length} decisions to CSV`}
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onRefresh} 
              disabled={isLoading}
              aria-label="Refresh decisions data"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Mobile search */}
        <form onSubmit={onSearch} className="md:hidden">
          <div className="flex gap-2">
            <Input
              placeholder="Search (id, reason...)"
              value={query}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
              disabled={isLoading}
              aria-label="Search decisions"
            />
            <Button type="submit" variant="outline" size="sm" disabled={isLoading}>
              <Filter className="w-4 h-4" />
            </Button>
          </div>
        </form>

        {/* Error and success messages */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {successMessage && (
          <Alert className="border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">{successMessage}</AlertDescription>
          </Alert>
        )}
      </CardHeader>

      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full" role="table" aria-label="Fraud detection decisions">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-medium text-gray-600" scope="col">Decision ID</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600" scope="col">Event ID</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600" scope="col">Decision</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600" scope="col">Risk Score</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600" scope="col">Reasons</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600" scope="col">Created</th>
              </tr>
            </thead>
            <tbody>
              {data.decisions.map((decision) => (
                <tr key={decision.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4 font-mono text-sm text-gray-900">
                    <span title={decision.id}>{decision.id.slice(0, 8)}…</span>
                  </td>
                  <td className="py-3 px-4 font-mono text-sm text-gray-600">
                    {decision.event_id ? (
                      <span title={decision.event_id}>{decision.event_id.slice(0, 8)}…</span>
                    ) : (
                      <span className="text-gray-400" aria-label="No event ID">—</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={getDecisionBadgeVariant(decision.decision)} className="flex items-center gap-1 w-fit">
                      {getDecisionIcon(decision.decision)}
                      {decision.decision.toUpperCase()}
                    </Badge>
                  </td>
                  <td className="py-3 px-4">
                    {decision.risk_score != null ? (
                      <span className={`font-medium ${getDecisionColor(decision.decision)}`}>
                        {(decision.risk_score * 100).toFixed(1)}%
                      </span>
                    ) : (
                      <span className="text-gray-400" aria-label="No risk score">—</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <div className="max-w-xs">
                      {decision.reasons && decision.reasons.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {decision.reasons.slice(0, 2).map((reason, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {reason}
                            </Badge>
                          ))}
                          {decision.reasons.length > 2 && (
                            <Badge variant="outline" className="text-xs" title={`${decision.reasons.length - 2} more reasons`}>
                              +{decision.reasons.length - 2} more
                            </Badge>
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-400" aria-label="No reasons provided">—</span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600">
                    <time dateTime={decision.created_at} title={new Date(decision.created_at).toISOString()}>
                      {new Date(decision.created_at).toLocaleString(undefined, {
                        year: "numeric",
                        month: "short",
                        day: "2-digit",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </time>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {data.decisions.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <div className="text-gray-500 text-lg">No decisions found</div>
            <p className="text-gray-400 mt-2">
              {query ? 'Try adjusting your search terms' : 'Decisions will appear here as events are processed'}
            </p>
          </div>
        )}

        {isLoading && (
          <div className="text-center py-12">
            <div className="flex items-center justify-center gap-2 text-gray-500">
              <RefreshCw className="w-4 h-4 animate-spin" />
              Loading decisions...
            </div>
          </div>
        )}

        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-6">
            <div className="text-sm text-gray-600">
              Showing {Math.min((data.page - 1) * data.limit + 1, data.total)} to{" "}
              {Math.min(data.page * data.limit, data.total)} of {data.total} decisions
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                disabled={page <= 1 || isLoading} 
                onClick={onPrev}
                aria-label="Go to previous page"
              >
                <ArrowLeft className="w-4 h-4 mr-1" />
                Previous
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                disabled={page >= totalPages || isLoading} 
                onClick={onNext}
                aria-label="Go to next page"
              >
                Next
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
