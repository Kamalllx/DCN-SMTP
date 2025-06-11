"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useToast } from "@/hooks/use-toast"
import { X, Shield, AlertTriangle, Search, FileText, Zap, Copy } from "lucide-react"

interface EmailReportProps {
  emailId: string
  token: string
  onClose: () => void
}

interface EmailReportData {
  email_data: {
    _id: string
    from: string
    to: string[]
    subject: string
    content: string
    created_at: string
    tls_used: boolean
    is_encrypted: boolean
    encryption_version?: string
    ai_analysis?: {
      spam_analysis?: {
        is_spam: boolean
        confidence: number
        threat_level: string
        reasons?: string[]
      }
      keyword_analysis?: {
        keywords_detected: number
        keywords_found: string[]
        keywords?: string[]
        risk_level: string
        risk_assessment: string
      }
      security_analysis?: {
        is_phishing: boolean
        risk_level: string
        indicators?: string[]
        recommendations?: string[]
      }
      categorization?: {
        category: string
        priority: string
        action_required: boolean
      }
      highlighted_content?: string
      summary?: string
      action_items?: {
        action_items: Array<{
          task: string
          priority: string
        }>
      }
    }
  }
}

export function EmailReport({ emailId, token, onClose }: EmailReportProps) {
  const [report, setReport] = useState<EmailReportData | null>(null)
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadReport()
  }, [emailId, token])

  const loadReport = async () => {
    try {
      console.log(`[EMAIL REPORT] Fetching report for email ID: ${emailId}`)

      const response = await fetch(`http://localhost:5000/api/email/${emailId}/report`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        console.log(`[EMAIL REPORT] ✅ Report fetched successfully:`, data)
        setReport(data)
      } else {
        const errorText = await response.text()
        console.error(`[EMAIL REPORT] ❌ Failed to fetch report:`, errorText)
        toast({
          title: "Error",
          description: "Failed to load email report",
          variant: "destructive",
        })
        onClose()
      }
    } catch (error) {
      console.error(`[EMAIL REPORT] ❌ Connection error:`, error)
      toast({
        title: "Error",
        description: "Connection failed",
        variant: "destructive",
      })
      onClose()
    } finally {
      setLoading(false)
    }
  }

  const getThreatLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case "high":
        return "threat-high"
      case "medium":
        return "threat-medium"
      case "low":
        return "threat-low"
      default:
        return "bg-gray-500/20 text-gray-300 border-gray-500/50"
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "Copied",
      description: "Content copied to clipboard",
    })
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
        <Card className="synthwave-card w-full max-w-2xl mx-4">
          <CardContent className="p-8 text-center">
            <div className="animate-spin w-8 h-8 border-2 border-neon-pink border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-400">Loading comprehensive email analysis...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!report) return null

  const { email_data } = report
  const ai_analysis = email_data.ai_analysis || {}

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <Card className="synthwave-card w-full max-w-6xl max-h-[90vh] overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="orbitron text-electric-blue flex items-center gap-2">
            <FileText className="w-5 h-5" />📋 Comprehensive Email Analysis Report
          </CardTitle>
          <Button
            onClick={onClose}
            variant="destructive"
            size="sm"
            className="bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700"
          >
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[75vh] pr-4">
            <div className="space-y-6">
              {/* Email Details */}
              <div className="p-4 rounded-lg bg-black/30 border border-gray-700">
                <h3 className="text-lg font-semibold text-neon-pink mb-3 flex items-center gap-2">
                  <Shield className="w-4 h-4" />📧 Email Details
                </h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <strong>From:</strong> {email_data.from}
                  </div>
                  <div>
                    <strong>To:</strong> {email_data.to?.join(", ") || "N/A"}
                  </div>
                  <div>
                    <strong>Subject:</strong> {email_data.subject}
                  </div>
                  <div>
                    <strong>Date:</strong> {new Date(email_data.created_at).toLocaleString()}
                  </div>
                  <div className="flex items-center gap-2">
                    <strong>Content Encryption:</strong>
                    {email_data.is_encrypted ? (
                      <Badge className="bg-green-500/20 text-green-300 border-green-500/50">
                        ✅ Encrypted in database
                      </Badge>
                    ) : (
                      <Badge className="bg-red-500/20 text-red-300 border-red-500/50">❌ Not encrypted</Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <strong>TLS Transport:</strong>
                    {email_data.tls_used ? (
                      <Badge className="bg-green-500/20 text-green-300 border-green-500/50">
                        ✅ Transmitted over TLS
                      </Badge>
                    ) : (
                      <Badge className="bg-red-500/20 text-red-300 border-red-500/50">❌ Plain text transmission</Badge>
                    )}
                  </div>
                  {email_data.encryption_version && (
                    <div>
                      <strong>Encryption Version:</strong> {email_data.encryption_version}
                    </div>
                  )}
                </div>
              </div>

              {/* AI Spam Analysis */}
              {ai_analysis.spam_analysis && (
                <div className="p-4 rounded-lg bg-black/30 border border-gray-700">
                  <h3 className="text-lg font-semibold text-electric-blue mb-3 flex items-center gap-2">
                    <Zap className="w-4 h-4" />🤖 AI Spam Analysis
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <strong>Spam Detection:</strong>
                      {ai_analysis.spam_analysis.is_spam ? (
                        <Badge className="threat-high">🚨 SPAM DETECTED</Badge>
                      ) : (
                        <Badge className="threat-low">✅ Not spam</Badge>
                      )}
                    </div>
                    <div>
                      <strong>Confidence:</strong> {(ai_analysis.spam_analysis.confidence * 100).toFixed(1)}%
                    </div>
                    <div className="flex items-center gap-2">
                      <strong>Threat Level:</strong>
                      <Badge className={getThreatLevelColor(ai_analysis.spam_analysis.threat_level)}>
                        {ai_analysis.spam_analysis.threat_level?.toUpperCase() || "UNKNOWN"}
                      </Badge>
                    </div>
                    {ai_analysis.spam_analysis.reasons && ai_analysis.spam_analysis.reasons.length > 0 && (
                      <div>
                        <strong>Detection Reasons:</strong>
                        <ul className="list-disc list-inside mt-1 text-gray-300">
                          {ai_analysis.spam_analysis.reasons.map((reason, index) => (
                            <li key={index}>{reason}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Enhanced Keyword Analysis */}
              {ai_analysis.keyword_analysis && (
                <div className="p-4 rounded-lg bg-black/30 border border-gray-700">
                  <h3 className="text-lg font-semibold text-deep-purple mb-3 flex items-center gap-2">
                    <Search className="w-4 h-4" />🔍 Enhanced Spam Keyword Analysis
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <strong>Keywords Detected:</strong> {ai_analysis.keyword_analysis.keywords_detected || 0}
                      </div>
                      <div className="flex items-center gap-2">
                        <strong>Risk Level:</strong>
                        <Badge className={getThreatLevelColor(ai_analysis.keyword_analysis.risk_level)}>
                          {ai_analysis.keyword_analysis.risk_level?.toUpperCase() || "UNKNOWN"}
                        </Badge>
                      </div>
                    </div>

                    {ai_analysis.keyword_analysis.risk_assessment && (
                      <div>
                        <strong>Risk Assessment:</strong>
                        <p className="text-gray-300 mt-1">{ai_analysis.keyword_analysis.risk_assessment}</p>
                      </div>
                    )}

                    {(ai_analysis.keyword_analysis.keywords_found || ai_analysis.keyword_analysis.keywords) &&
                    (ai_analysis.keyword_analysis.keywords_found?.length > 0 ||
                      ai_analysis.keyword_analysis.keywords?.length > 0) ? (
                      <div>
                        <strong>Suspicious Keywords Found:</strong>
                        <div className="mt-2 p-3 bg-black/50 rounded border border-red-500/30">
                          {(
                            ai_analysis.keyword_analysis.keywords_found ||
                            ai_analysis.keyword_analysis.keywords ||
                            []
                          ).map((keyword, index) => (
                            <span key={index} className="spam-keyword mr-2 mb-1 inline-block">
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <p className="text-green-400">✅ No suspicious keywords detected.</p>
                    )}

                    {ai_analysis.highlighted_content && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <strong>Content with Highlighted Keywords:</strong>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => copyToClipboard(ai_analysis.highlighted_content || "")}
                            className="border-gray-600 text-gray-300 hover:bg-gray-700"
                          >
                            <Copy className="w-3 h-3 mr-1" />
                            Copy
                          </Button>
                        </div>
                        <div
                          className="mt-2 p-3 bg-white/5 border border-gray-600 rounded max-h-48 overflow-y-auto text-gray-300"
                          dangerouslySetInnerHTML={{ __html: ai_analysis.highlighted_content }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Security Analysis */}
              {ai_analysis.security_analysis && (
                <div className="p-4 rounded-lg bg-black/30 border border-gray-700">
                  <h3 className="text-lg font-semibold text-yellow-400 mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" />
                    🛡️ Security Analysis
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <strong>Phishing Risk:</strong>
                      {ai_analysis.security_analysis.is_phishing ? (
                        <Badge className="threat-high">🚨 HIGH RISK</Badge>
                      ) : (
                        <Badge className="threat-low">✅ Low risk</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <strong>Security Score:</strong>
                      <Badge className={getThreatLevelColor(ai_analysis.security_analysis.risk_level)}>
                        {ai_analysis.security_analysis.risk_level?.toUpperCase() || "Unknown"}
                      </Badge>
                    </div>
                    {ai_analysis.security_analysis.indicators &&
                      ai_analysis.security_analysis.indicators.length > 0 && (
                        <div>
                          <strong>Security Indicators:</strong>
                          <ul className="list-disc list-inside mt-1 text-gray-300">
                            {ai_analysis.security_analysis.indicators.map((indicator, index) => (
                              <li key={index}>{indicator}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    {ai_analysis.security_analysis.recommendations &&
                      ai_analysis.security_analysis.recommendations.length > 0 && (
                        <div>
                          <strong>Security Recommendations:</strong>
                          <ul className="list-disc list-inside mt-1 text-gray-300">
                            {ai_analysis.security_analysis.recommendations.map((rec, index) => (
                              <li key={index}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                  </div>
                </div>
              )}

              {/* Additional Analysis */}
              {ai_analysis.categorization && (
                <div className="p-4 rounded-lg bg-black/30 border border-gray-700">
                  <h3 className="text-lg font-semibold text-green-400 mb-3">📊 Additional Analysis</h3>
                  <div className="grid md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <strong>Category:</strong> {ai_analysis.categorization.category || "Unknown"}
                    </div>
                    <div>
                      <strong>Priority:</strong> {ai_analysis.categorization.priority || "Unknown"}
                    </div>
                    <div>
                      <strong>Action Required:</strong> {ai_analysis.categorization.action_required ? "Yes" : "No"}
                    </div>
                  </div>
                  {ai_analysis.summary && (
                    <div className="mt-3">
                      <strong>AI Summary:</strong>
                      <p className="text-gray-300 mt-1">{ai_analysis.summary}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Action Items */}
              {ai_analysis.action_items?.action_items && ai_analysis.action_items.action_items.length > 0 && (
                <div className="p-4 rounded-lg bg-black/30 border border-gray-700">
                  <h3 className="text-lg font-semibold text-orange-400 mb-3">📋 Extracted Action Items</h3>
                  <div className="space-y-2">
                    {ai_analysis.action_items.action_items.map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-black/20 rounded">
                        <span className="text-gray-300">{item.task || "No description"}</span>
                        <Badge className={getThreatLevelColor(item.priority || "low")}>
                          {(item.priority || "low").toUpperCase()}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Raw Email Content */}
              <div className="p-4 rounded-lg bg-black/30 border border-gray-700">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-400">📄 Email Content</h3>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => copyToClipboard(email_data.content)}
                    className="border-gray-600 text-gray-300 hover:bg-gray-700"
                  >
                    <Copy className="w-3 h-3 mr-1" />
                    Copy Content
                  </Button>
                </div>
                <div className="p-3 bg-black/50 border border-gray-600 rounded max-h-40 overflow-y-auto">
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap">{email_data.content}</pre>
                </div>
              </div>
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  )
}
