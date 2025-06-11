"use client"

import { useAuth } from "@/contexts/auth-context"
import { redirect } from "next/navigation"
import { EnhancedEmailManager } from "@/components/enhanced-email-manager"
import { useEffect } from "react"

export default function EmailsPage() {
  const { user, token } = useAuth()

  useEffect(() => {
    if (!user) {
      redirect("/")
    }
  }, [user])

  if (!user) return null

  return (
    <div className="min-h-screen synthwave-bg">
      <div className="container mx-auto px-4 py-8">
        <EnhancedEmailManager token={token!} user={user} />
      </div>
    </div>
  )
}
