"use client"

import { useAuth } from "@/contexts/auth-context"
import { AuthSection } from "@/components/auth-section"
import { LandingPage } from "@/components/landing-page"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function Home() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    console.log("[HOME PAGE] Auth state:", {
      user: user ? "present" : "none",
      isLoading,
    })

    // If user is authenticated, redirect to dashboard
    if (user && !isLoading) {
      console.log("[HOME PAGE] ✅ User authenticated, redirecting to dashboard")
      router.push("/dashboard")
    }
  }, [user, isLoading, router])

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen synthwave-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-neon-pink border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  // If user is authenticated, show loading while redirecting
  if (user) {
    return (
      <div className="min-h-screen synthwave-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-electric-blue border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-400">Redirecting to dashboard...</p>
        </div>
      </div>
    )
  }

  // Show auth page for non-authenticated users
  return (
    <div className="min-h-screen synthwave-bg">
      <div className="container mx-auto px-4 py-8">
        <LandingPage />
        <AuthSection />
      </div>
    </div>
  )
}
