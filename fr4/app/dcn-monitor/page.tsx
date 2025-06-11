"use client"

import { useAuth } from "@/contexts/auth-context"
import { useSocket } from "@/hooks/use-socket"
import { redirect } from "next/navigation"
import { DCNMonitor } from "@/components/dcn-monitor"
import { useEffect } from "react"

export default function DCNMonitorPage() {
  const { user, token } = useAuth()
  const { socket } = useSocket(token)

  useEffect(() => {
    if (!user) {
      redirect("/")
    }
  }, [user])

  if (!user) return null

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="fade-in-up">
        <h1 className="text-4xl font-bold orbitron text-center mb-8">
          <span className="text-deep-purple glow-text">DCN Protocol Monitor</span>
        </h1>
      </div>

      <div className="fade-in-up" style={{ animationDelay: "0.2s" }}>
        <DCNMonitor socket={socket} />
      </div>
    </div>
  )
}
