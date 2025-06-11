"use client"

import { useAuth } from "@/contexts/auth-context"
import { redirect } from "next/navigation"
import { EmailManager } from "@/components/email-manager"
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
    <div className="container mx-auto px-4 py-8">
      <div className="fade-in-up">
        <h1 className="text-4xl font-bold orbitron text-center mb-8">
          <span className="text-electric-blue glow-text">Email Management</span>
        </h1>
      </div>

      <div className="fade-in-up" style={{ animationDelay: "0.2s" }}>
        <EmailManager token={token!} user={user} />
      </div>
    </div>
  )
}
