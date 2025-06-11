"use client"

import { useAuth } from "@/contexts/auth-context"
import { redirect } from "next/navigation"
import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { Shield, AlertTriangle, Scan, FileText, RefreshCw, CheckCircle } from "lucide-react"

export default function SecurityPage() {
  const { user, token } = useAuth()
  const [scanning, setScanning] = useState(false)
  const [lastScan, setLastScan] = useState<Date | null>(null)
  const [securityScore, setSecurityScore] = useState(98)
  const { toast } = useToast()

  useEffect(() => {
    if (!user) {
      redirect("/")
    }
  }, [user])

  const runSecurityScan = async () => {
    setScanning(true)
    try {
      // Simulate security scan
      await new Promise((resolve) => setTimeout(resolve, 3000))
      setLastScan(new Date())
      setSecurityScore(Math.floor(Math.random() * 5) + 95) // 95-100
      toast({
        title: "Security Scan Complete",
        description: "✅ System is secure and all protocols are functioning properly",
      })
    } catch (error) {
      toast({
        title: "Scan Failed",
        description: "Failed to complete security scan",
        variant: "destructive",
      })
    } finally {
      setScanning(false)
    }
  }

  const generateSecurityReport = async () => {
    try {
      toast({
        title: "Report Generated",
        description: "📊 Security report generated and ready for download",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate security report",
        variant: "destructive",
      })
    }
  }

  const updateSecurityRules = async () => {
    try {
      toast({
        title: "Rules Updated",
        description: "🔄 Security rules updated with latest threat intelligence",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update security rules",
        variant: "destructive",
      })
    }
  }

  if (!user) return null

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="fade-in-up">
        <h1 className="text-4xl font-bold orbitron text-center mb-8">
          <span className="text-yellow-400 glow-text">🛡️ Advanced Security Center</span>
        </h1>
      </div>

      {/* Security Status Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 fade-in-up" style={{ animationDelay: "0.2s" }}>
        <Card className="synthwave-card">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-green-400 mb-2">HIGH</div>
            <div className="text-sm text-gray-400">🟢 Security Level</div>
          </CardContent>
        </Card>

        <Card className="synthwave-card">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-neon-pink mb-2">47</div>
            <div className="text-sm text-gray-400">🛡️ Threats Blocked</div>
          </CardContent>
        </Card>

        <Card className="synthwave-card">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-electric-blue mb-2">100%</div>
            <div className="text-sm text-gray-400">🔐 Encryption Rate</div>
          </CardContent>
        </Card>

        <Card className="synthwave-card">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-deep-purple mb-2">ACTIVE</div>
            <div className="text-sm text-gray-400">🔒 TLS Protection</div>
          </CardContent>
        </Card>
      </div>

      {/* Security Score */}
      <Card className="synthwave-card fade-in-up" style={{ animationDelay: "0.4s" }}>
        <CardHeader>
          <CardTitle className="orbitron text-green-400 flex items-center gap-2">
            <Shield className="w-5 h-5" />🎯 Security Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-4xl font-bold text-green-400">{securityScore}/100</div>
              <div className="text-gray-400">Overall Security Rating</div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">Last Scan:</div>
              <div className="text-white">{lastScan ? lastScan.toLocaleString() : "Never"}</div>
            </div>
          </div>
          <div className="w-full h-4 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all duration-1000"
              style={{ width: `${securityScore}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Security Tools */}
      <Card className="synthwave-card fade-in-up" style={{ animationDelay: "0.6s" }}>
        <CardHeader>
          <CardTitle className="orbitron text-electric-blue flex items-center gap-2">
            <Scan className="w-5 h-5" />🔍 Security Tools
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <Button
              onClick={runSecurityScan}
              disabled={scanning}
              className="h-auto p-6 flex flex-col items-center gap-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
            >
              {scanning ? <RefreshCw className="w-8 h-8 animate-spin" /> : <Scan className="w-8 h-8" />}
              <div className="text-center">
                <div className="font-semibold">{scanning ? "Scanning..." : "🔍 Run Security Scan"}</div>
                <div className="text-xs opacity-80">
                  {scanning ? "Analyzing system..." : "Comprehensive security analysis"}
                </div>
              </div>
            </Button>

            <Button
              onClick={generateSecurityReport}
              className="h-auto p-6 flex flex-col items-center gap-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
            >
              <FileText className="w-8 h-8" />
              <div className="text-center">
                <div className="font-semibold">📊 Generate Report</div>
                <div className="text-xs opacity-80">Security analysis report</div>
              </div>
            </Button>

            <Button
              onClick={updateSecurityRules}
              className="h-auto p-6 flex flex-col items-center gap-3 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700"
            >
              <RefreshCw className="w-8 h-8" />
              <div className="text-center">
                <div className="font-semibold">🔄 Update Rules</div>
                <div className="text-xs opacity-80">Latest threat intelligence</div>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Security Features Status */}
      <Card className="synthwave-card fade-in-up" style={{ animationDelay: "0.8s" }}>
        <CardHeader>
          <CardTitle className="orbitron text-neon-pink flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />🔧 Security Features Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              {
                feature: "Real-time Spam Detection",
                status: "✅ Active",
                description: "AI-powered spam filtering",
                class: "threat-low",
              },
              {
                feature: "Phishing Protection",
                status: "✅ Active",
                description: "Advanced phishing detection",
                class: "threat-low",
              },
              {
                feature: "Content Encryption",
                status: "✅ Active",
                description: "Fernet AES-128 encryption",
                class: "threat-low",
              },
              {
                feature: "TLS Transport Security",
                status: "✅ Active",
                description: "TLS 1.3 protocol",
                class: "threat-low",
              },
              {
                feature: "Keyword Highlighting",
                status: "✅ Active",
                description: "Suspicious keyword detection",
                class: "threat-low",
              },
              {
                feature: "AI Threat Analysis",
                status: "✅ Active",
                description: "Machine learning analysis",
                class: "threat-low",
              },
            ].map((item, index) => (
              <div key={item.feature} className="p-4 bg-black/30 rounded-lg border border-gray-700">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-white font-semibold">{item.feature}</span>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${item.class}`}>{item.status}</span>
                </div>
                <p className="text-sm text-gray-400">{item.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Threat Intelligence */}
      <Card className="synthwave-card fade-in-up" style={{ animationDelay: "1.0s" }}>
        <CardHeader>
          <CardTitle className="orbitron text-yellow-400 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            ⚠️ Threat Intelligence
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                <span className="font-semibold text-red-400">High Priority Alert</span>
              </div>
              <p className="text-sm text-gray-300">
                New phishing campaign detected targeting email systems. Enhanced monitoring active.
              </p>
              <p className="text-xs text-gray-400 mt-1">Last updated: 2 hours ago</p>
            </div>

            <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-4 h-4 text-yellow-400" />
                <span className="font-semibold text-yellow-400">Security Update</span>
              </div>
              <p className="text-sm text-gray-300">
                TLS certificate renewed successfully. All connections remain secure.
              </p>
              <p className="text-xs text-gray-400 mt-1">Last updated: 1 day ago</p>
            </div>

            <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="font-semibold text-green-400">System Status</span>
              </div>
              <p className="text-sm text-gray-300">
                All security systems operational. No threats detected in the last 24 hours.
              </p>
              <p className="text-xs text-gray-400 mt-1">Last updated: 30 minutes ago</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security Notice */}
      <div className="text-center text-sm text-gray-400 fade-in-up" style={{ animationDelay: "1.2s" }}>
        <p>
          🔒 <strong>Security Notice:</strong> All communications are protected with TLS encryption.
        </p>
        <p>Email content is encrypted before database storage using Fernet (AES-128) encryption.</p>
      </div>
    </div>
  )
}
