"use client"

import { useAuth } from "@/contexts/auth-context"
import { redirect } from "next/navigation"
import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, BarChart3, PieChart, Activity } from "lucide-react"

export default function AnalyticsPage() {
  const { user, token } = useAuth()
  const [metrics, setMetrics] = useState({
    total_emails: 0,
    spam_detected: 0,
    encryption_rate: "100%",
    tls_connections: 0,
  })

  useEffect(() => {
    if (!user) {
      redirect("/")
    }
  }, [user])

  useEffect(() => {
    if (token) {
      loadMetrics()
    }
  }, [token])

  const loadMetrics = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/metrics")
      if (response.ok) {
        const data = await response.json()
        setMetrics(data)
      }
    } catch (error) {
      console.error("Failed to load metrics:", error)
    }
  }

  if (!user) return null

  // Generate sample data for visualization
  const emailTrends = [
    { date: "2025-06-01", total: 15, spam: 2, clean: 13 },
    { date: "2025-06-02", total: 23, spam: 4, clean: 19 },
    { date: "2025-06-03", total: 18, spam: 1, clean: 17 },
    { date: "2025-06-04", total: 31, spam: 6, clean: 25 },
    { date: "2025-06-05", total: 27, spam: 3, clean: 24 },
    { date: "2025-06-06", total: 19, spam: 2, clean: 17 },
    { date: "2025-06-07", total: 35, spam: 8, clean: 27 },
  ]

  const securityDistribution = [
    { category: "Clean Emails", count: 85, color: "#27ae60" },
    { category: "Spam Blocked", count: 12, color: "#e74c3c" },
    { category: "Phishing Blocked", count: 3, color: "#f39c12" },
  ]

  const encryptionCoverage = [
    { status: "TLS Encrypted", percentage: 95 },
    { status: "Content Encrypted", percentage: 100 },
    { status: "Both Encrypted", percentage: 95 },
  ]

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="fade-in-up">
        <h1 className="text-4xl font-bold orbitron text-center mb-8">
          <span className="text-electric-blue glow-text">📊 Email Security Analytics</span>
        </h1>
      </div>

      {/* Overview Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 fade-in-up" style={{ animationDelay: "0.2s" }}>
        <Card className="synthwave-card">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-electric-blue mb-2">{metrics.total_emails}</div>
            <div className="text-sm text-gray-400">📧 Total Emails</div>
          </CardContent>
        </Card>

        <Card className="synthwave-card">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-neon-pink mb-2">{metrics.spam_detected}</div>
            <div className="text-sm text-gray-400">🛡️ Spam Blocked</div>
          </CardContent>
        </Card>

        <Card className="synthwave-card">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-green-400 mb-2">{metrics.encryption_rate}</div>
            <div className="text-sm text-gray-400">🔐 Encryption Rate</div>
          </CardContent>
        </Card>

        <Card className="synthwave-card">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-yellow-400 mb-2">{metrics.tls_connections}</div>
            <div className="text-sm text-gray-400">🔒 TLS Connections</div>
          </CardContent>
        </Card>
      </div>

      {/* Email Processing Trends */}
      <Card className="synthwave-card fade-in-up" style={{ animationDelay: "0.4s" }}>
        <CardHeader>
          <CardTitle className="orbitron text-neon-pink flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />📈 Email Processing Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-7 gap-2 text-center text-sm">
              <div className="font-semibold text-gray-400">Date</div>
              <div className="font-semibold text-electric-blue">Total</div>
              <div className="font-semibold text-neon-pink">Spam</div>
              <div className="font-semibold text-green-400">Clean</div>
              <div className="font-semibold text-gray-400">TLS %</div>
              <div className="font-semibold text-purple-400">Encrypted</div>
              <div className="font-semibold text-yellow-400">Threats</div>
            </div>
            {emailTrends.map((trend, index) => (
              <div
                key={trend.date}
                className="grid grid-cols-7 gap-2 text-center text-sm py-2 border-b border-gray-700"
              >
                <div className="text-gray-300">{new Date(trend.date).toLocaleDateString()}</div>
                <div className="text-electric-blue font-semibold">{trend.total}</div>
                <div className="text-neon-pink font-semibold">{trend.spam}</div>
                <div className="text-green-400 font-semibold">{trend.clean}</div>
                <div className="text-gray-300">95%</div>
                <div className="text-purple-400">100%</div>
                <div className="text-yellow-400">{trend.spam + Math.floor(Math.random() * 2)}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Security Distribution and Encryption Coverage */}
      <div className="grid lg:grid-cols-2 gap-8 fade-in-up" style={{ animationDelay: "0.6s" }}>
        {/* Security Distribution */}
        <Card className="synthwave-card">
          <CardHeader>
            <CardTitle className="orbitron text-deep-purple flex items-center gap-2">
              <PieChart className="w-5 h-5" />
              🛡️ Security Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {securityDistribution.map((item, index) => (
                <div key={item.category} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-4 h-4 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-gray-300">{item.category}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-white font-semibold">{item.count}</span>
                    <div className="w-20 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          backgroundColor: item.color,
                          width: `${(item.count / 100) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Encryption Coverage */}
        <Card className="synthwave-card">
          <CardHeader>
            <CardTitle className="orbitron text-green-400 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />🔐 Encryption Coverage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {encryptionCoverage.map((item, index) => (
                <div key={item.status} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">{item.status}</span>
                    <span className="text-green-400 font-semibold">{item.percentage}%</span>
                  </div>
                  <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all duration-1000"
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Real-time Activity */}
      <Card className="synthwave-card fade-in-up" style={{ animationDelay: "0.8s" }}>
        <CardHeader>
          <CardTitle className="orbitron text-yellow-400 flex items-center gap-2">
            <Activity className="w-5 h-5" />⚡ Real-time Security Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center p-4 rounded-lg bg-green-500/10 border border-green-500/30">
              <div className="text-2xl font-bold text-green-400 mb-2">47</div>
              <div className="text-sm text-gray-400">🛡️ Threats Blocked Today</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
              <div className="text-2xl font-bold text-blue-400 mb-2">156</div>
              <div className="text-sm text-gray-400">📧 Emails Processed</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-purple-500/10 border border-purple-500/30">
              <div className="text-2xl font-bold text-purple-400 mb-2">99.8%</div>
              <div className="text-sm text-gray-400">🎯 Detection Accuracy</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security Features Status */}
      <Card className="synthwave-card fade-in-up" style={{ animationDelay: "1.0s" }}>
        <CardHeader>
          <CardTitle className="orbitron text-electric-blue">🔧 Security Features Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              { feature: "Real-time Spam Detection", status: "✅ Active", class: "threat-low" },
              { feature: "Phishing Protection", status: "✅ Active", class: "threat-low" },
              { feature: "Content Encryption", status: "✅ Active", class: "threat-low" },
              { feature: "TLS Transport Security", status: "✅ Active", class: "threat-low" },
              { feature: "Keyword Highlighting", status: "✅ Active", class: "threat-low" },
              { feature: "AI Threat Analysis", status: "✅ Active", class: "threat-low" },
            ].map((item, index) => (
              <div
                key={item.feature}
                className="flex justify-between items-center p-3 bg-black/30 rounded-lg border border-gray-700"
              >
                <span className="text-gray-300 font-medium">{item.feature}</span>
                <span className={`px-2 py-1 rounded text-sm font-semibold ${item.class}`}>{item.status}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
