"use client"

import { useAuth } from "@/contexts/auth-context"
import { useRouter } from "next/navigation"
import { UserInfo } from "@/components/user-info"
import { SystemMetrics } from "@/components/system-metrics"
import { QuickActions } from "@/components/quick-actions"
import { useEffect, useState } from "react"

export default function DashboardPage() {
  const { user, token, logout, isLoading } = useAuth()
  const router = useRouter()
  const [metrics, setMetrics] = useState({
    total_emails: 0,
    spam_detected: 0,
    encryption_rate: "100%",
    tls_connections: 0,
  })

  useEffect(() => {
    console.log("[DASHBOARD] Auth state:", {
      user: user ? "present" : "none",
      token: token ? "present" : "none",
      isLoading,
    })

    if (!isLoading && !user) {
      console.log("[DASHBOARD] ❌ No user, redirecting to home")
      router.push("/")
      return
    }
  }, [user, token, isLoading, router])

  useEffect(() => {
    if (token) {
      loadMetrics()
      const interval = setInterval(loadMetrics, 30000)
      return () => clearInterval(interval)
    }
  }, [token])

  const loadMetrics = async () => {
    try {
      console.log("[DASHBOARD] 📊 Loading metrics...")
      const response = await fetch("http://localhost:5000/api/metrics")
      if (response.ok) {
        const data = await response.json()
        setMetrics(data)
        console.log("[DASHBOARD] ✅ Metrics loaded:", data)
      } else {
        console.error("[DASHBOARD] ❌ Failed to load metrics:", response.status)
      }
    } catch (error) {
      console.error("[DASHBOARD] ❌ Metrics error:", error)
    }
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen synthwave-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-neon-pink border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  // Redirect if no user
  if (!user) {
    return (
      <div className="min-h-screen synthwave-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-electric-blue border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-400">Redirecting...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen synthwave-bg">
      <div className="container mx-auto px-4 py-8 space-y-8">
        <div className="fade-in-up">
          <h1 className="text-4xl font-bold orbitron text-center mb-8">
            <span className="text-neon-pink glow-text">📊 Dashboard</span>
          </h1>
        </div>

        <div className="fade-in-up" style={{ animationDelay: "0.2s" }}>
          <UserInfo user={user} onLogout={logout} />
        </div>

        <div className="fade-in-up" style={{ animationDelay: "0.4s" }}>
          <SystemMetrics metrics={metrics} />
        </div>

        <div className="fade-in-up" style={{ animationDelay: "0.6s" }}>
          <QuickActions />
        </div>
      </div>
    </div>
  )
}
