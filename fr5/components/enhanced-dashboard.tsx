"use client"

import { useAuth } from "@/contexts/auth-context"
import { UserInfo } from "@/components/user-info"
import { SystemMetrics } from "@/components/system-metrics"
import { QuickActions } from "@/components/quick-actions"
import { PageTransition } from "@/components/page-transition"
import { LoadingSpinner } from "@/components/loading-spinner"
import { motion } from "framer-motion"
import { useEffect, useState } from "react"

export function EnhancedDashboard() {
  const { user, token, logout, isLoading } = useAuth()
  const [metrics, setMetrics] = useState({
    total_emails: 0,
    spam_detected: 0,
    encryption_rate: "100%",
    tls_connections: 0,
  })
  const [metricsLoading, setMetricsLoading] = useState(true)

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
    } finally {
      setMetricsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen synthwave-bg flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen synthwave-bg flex items-center justify-center">
        <LoadingSpinner size="lg" text="Redirecting..." />
      </div>
    )
  }

  return (
    <PageTransition className="min-h-screen synthwave-bg">
      <div className="container mx-auto px-4 py-8 space-y-8">
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          <h1 className="text-4xl md:text-6xl font-bold orbitron mb-4">
            <span className="text-neon-pink glow-text">📊 Dashboard</span>
          </h1>
          <p className="text-xl text-gray-300 rajdhani">Welcome to your secure email management center</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <UserInfo user={user} onLogout={logout} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          {metricsLoading ? (
            <div className="flex justify-center py-8">
              <LoadingSpinner text="Loading system metrics..." />
            </div>
          ) : (
            <SystemMetrics metrics={metrics} />
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <QuickActions />
        </motion.div>
      </div>
    </PageTransition>
  )
}
