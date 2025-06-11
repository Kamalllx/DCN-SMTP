"use client"

import { useAuth } from "@/contexts/auth-context"
import { useSocket } from "@/hooks/use-socket"
import { redirect } from "next/navigation"
import { InteractiveDCNMonitor } from "@/components/interactive-dcn-monitor"
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
    <div className="min-h-screen synthwave-bg">
      <InteractiveDCNMonitor socket={socket} />
    </div>
  )
}
