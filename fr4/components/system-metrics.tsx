"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp } from "lucide-react"

interface SystemMetricsProps {
  metrics: {
    total_emails: number
    spam_detected: number
    encryption_rate: string
    tls_connections: number
  }
}

export function SystemMetrics({ metrics }: SystemMetricsProps) {
  return (
    <Card className="synthwave-card">
      <CardHeader>
        <CardTitle className="orbitron text-neon-pink flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />📈 System Performance Metrics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-600/20 border border-blue-500/30">
            <div className="text-3xl font-bold text-electric-blue mb-2">{metrics.total_emails}</div>
            <div className="text-sm text-gray-400">Total Emails Processed</div>
          </div>

          <div className="text-center p-4 rounded-lg bg-gradient-to-br from-red-500/20 to-pink-600/20 border border-red-500/30">
            <div className="text-3xl font-bold text-neon-pink mb-2">{metrics.spam_detected}</div>
            <div className="text-sm text-gray-400">Spam/Phishing Blocked</div>
          </div>

          <div className="text-center p-4 rounded-lg bg-gradient-to-br from-green-500/20 to-emerald-600/20 border border-green-500/30">
            <div className="text-3xl font-bold text-green-400 mb-2">{metrics.encryption_rate}</div>
            <div className="text-sm text-gray-400">Encryption Rate</div>
          </div>

          <div className="text-center p-4 rounded-lg bg-gradient-to-br from-yellow-500/20 to-orange-600/20 border border-yellow-500/30">
            <div className="text-3xl font-bold text-yellow-400 mb-2">{metrics.tls_connections}</div>
            <div className="text-sm text-gray-400">TLS Connections</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
