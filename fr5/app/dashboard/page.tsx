"use client"

import { useAuth } from "@/contexts/auth-context"
import { useRouter } from "next/navigation"
import { EnhancedDashboard } from "@/components/enhanced-dashboard"
import { useEffect } from "react"

export default function DashboardPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    console.log("[DASHBOARD] Auth state:", {
      user: user ? "present" : "none",
      isLoading,
    })

    if (!isLoading && !user) {
      console.log("[DASHBOARD] ❌ No user, redirecting to home")
      router.push("/")
      return
    }
  }, [user, isLoading, router])

  return <EnhancedDashboard />
}
