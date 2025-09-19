import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowLeft, ArrowRight, RefreshCw, Filter, Download } from "lucide-react"

interface Decision {
  id: string
  event_id?: string
  decision: 'allow' | 'deny' | 'review'
  risk_score?: number
  reasons: string[]
  rules_fired: string[]
  created_at: string
}

interface DecisionsResponse {
  decisions: Decision[]
  total: number
  page: number
  limit: number
}

async function getDecisions(page = 1): Promise<DecisionsResponse> {
  try {
    const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/proxy/decisions?page=${page}&page_size=20`, { 
      cache: 'no-store' 
    })
    if (!r.ok) throw new Error('Failed to fetch decisions')
    return await r.json()
  } catch (error) {
    console.error('Error fetching decisions:', error)
    return { decisions: [], total: 0, page: 1, limit: 20 }
  }
}

function getDecisionBadgeVariant(decision: string) {
  switch (decision) {
    case 'allow': return 'default'
    case 'deny': return 'destructive'
    case 'review': return 'secondary'
    default: return 'outline'
  }
}

function getDecisionColor(decision: string) {
  switch (decision) {
    case 'allow': return 'text-green-600'
    case 'deny': return 'text-red-600'
    case 'review': return 'text-yellow-600'
    default: return 'text-gray-600'
  }
}

export default async function DecisionsPage() {
  const data = await getDecisions(1)
  const totalPages = Math.ceil(data.total / data.limit)

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Fraud Decisions</h1>
              <p className="mt-2 text-gray-600">
                Real-time fraud detection decisions and risk assessments
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Filter className="w-4 h-4 mr-2" />
                Filter
              </Button>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Decisions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{data.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Allowed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {data.decisions.filter(d => d.decision === 'allow').length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Denied</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {data.decisions.filter(d => d.decision === 'deny').length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Under Review</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {data.decisions.filter(d => d.decision === 'review').length}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recent Decisions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Decision ID</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Event ID</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Decision</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Risk Score</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Reasons</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Created</th>
                  </tr>
                </thead>
        <tbody>
                  {data.decisions.map((decision) => (
                    <tr key={decision.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-sm text-gray-900">
                        {decision.id.slice(0, 8)}...
                      </td>
                      <td className="py-3 px-4 font-mono text-sm text-gray-600">
                        {decision.event_id ? decision.event_id.slice(0, 8) + '...' : '-'}
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={getDecisionBadgeVariant(decision.decision)}>
                          {decision.decision.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        {decision.risk_score ? (
                          <span className={`font-medium ${getDecisionColor(decision.decision)}`}>
                            {(decision.risk_score * 100).toFixed(1)}%
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <div className="max-w-xs">
                          {decision.reasons.length > 0 ? (
                            <div className="flex flex-wrap gap-1">
                              {decision.reasons.slice(0, 2).map((reason, idx) => (
                                <Badge key={idx} variant="outline" className="text-xs">
                                  {reason}
                                </Badge>
                              ))}
                              {decision.reasons.length > 2 && (
                                <Badge variant="outline" className="text-xs">
                                  +{decision.reasons.length - 2} more
                                </Badge>
                              )}
                            </div>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {new Date(decision.created_at).toLocaleString()}
                      </td>
            </tr>
          ))}
        </tbody>
      </table>
            </div>

            {data.decisions.length === 0 && (
              <div className="text-center py-12">
                <div className="text-gray-500 text-lg">No decisions found</div>
                <p className="text-gray-400 mt-2">Decisions will appear here as events are processed</p>
              </div>
            )}

            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-gray-600">
                  Showing {((data.page - 1) * data.limit) + 1} to {Math.min(data.page * data.limit, data.total)} of {data.total} decisions
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" disabled={data.page <= 1}>
                    <ArrowLeft className="w-4 h-4 mr-1" />
                    Previous
                  </Button>
                  <Button variant="outline" size="sm" disabled={data.page >= totalPages}>
                    Next
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
