"use client"

import { useState, useEffect } from "react"
import { UserInfo } from "@/components/user-info"
import { DCNMonitor } from "@/components/dcn-monitor"
import { EmailManager } from "@/components/email-manager"
import { SystemMetrics } from "@/components/system-metrics"
import { ServerControls } from "@/components/server-controls"
import { SystemLogs } from "@/components/system-logs"
import { useToast } from "@/hooks/use-toast"
import type { Socket } from "socket.io-client"

interface DashboardProps {
  user: string
  token: string
  socket: Socket | null
  onLogout: () => void
}

export function Dashboard({ user, token, socket, onLogout }: DashboardProps) {
  const [metrics, setMetrics] = useState({
    total_emails: 0,
    spam_detected: 0,
    encryption_rate: "100%",
    tls_connections: 0,
  })
  const { toast } = useToast()

  useEffect(() => {
    loadMetrics()
    const interval = setInterval(loadMetrics, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [token])

  useEffect(() => {
    if (socket) {
      socket.on("new_email", (data) => {
        toast({
          title: "📧 New Email",
          description: `From: ${data.from}`,
          variant: data.is_spam ? "destructive" : "default",
        })
        loadMetrics()
      })

      socket.on("security_alert", (data) => {
        toast({
          title: "🚨 Security Alert",
          description: data.message,
          variant: "destructive",
        })
      })

      return () => {
        socket.off("new_email")
        socket.off("security_alert")
      }
    }
  }, [socket, toast])

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

  return (
    <div className="space-y-8">
      {/* User Info */}
      <UserInfo user={user} onLogout={onLogout} />

      {/* DCN Monitor */}
      <DCNMonitor socket={socket} />

      {/* Email Manager */}
      <EmailManager token={token} user={user} />

      {/* System Metrics */}
      <SystemMetrics metrics={metrics} />

      {/* Server Controls */}
      <ServerControls />

      {/* System Logs */}
      <SystemLogs />
    </div>
  )
}
