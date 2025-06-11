"use client"

import { useAuth } from "@/contexts/auth-context"
import { redirect } from "next/navigation"
import { AIAnalysisTools } from "@/components/ai-analysis-tools"
import { useEffect } from "react"

export default function AIAnalysisPage() {
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
          <span className="text-green-400 glow-text">AI Analysis Tools</span>
        </h1>
      </div>

      <div className="fade-in-up" style={{ animationDelay: "0.2s" }}>
        <AIAnalysisTools token={token!} />
      </div>
    </div>
  )
}
