"use client"

import { useAuth } from "@/contexts/auth-context"
import { redirect } from "next/navigation"
import { ServerControls } from "@/components/server-controls"
import { SystemLogs } from "@/components/system-logs"
import { useEffect } from "react"

export default function ServersPage() {
  const { user } = useAuth()

  useEffect(() => {
    if (!user) {
      redirect("/")
    }
  }, [user])

  if (!user) return null

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="fade-in-up">
        <h1 className="text-4xl font-bold orbitron text-center mb-8">
          <span className="text-yellow-400 glow-text">Server Management</span>
        </h1>
      </div>

      <div className="fade-in-up" style={{ animationDelay: "0.2s" }}>
        <ServerControls />
      </div>

      <div className="fade-in-up" style={{ animationDelay: "0.4s" }}>
        <SystemLogs />
      </div>
    </div>
  )
}
