"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useRouter } from "next/navigation"

interface AuthContextType {
  user: string | null
  token: string | null
  login: (email: string, authToken: string) => void
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<string | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check for stored auth data on mount
    try {
      const storedUser = localStorage.getItem("user")
      const storedToken = localStorage.getItem("token")

      console.log("[AUTH CONTEXT] Checking stored auth:", {
        user: storedUser ? "present" : "none",
        token: storedToken ? "present" : "none",
      })

      if (storedUser && storedToken) {
        setUser(storedUser)
        setToken(storedToken)
        console.log("[AUTH CONTEXT] ✅ Restored auth from localStorage")
      }
    } catch (error) {
      console.error("[AUTH CONTEXT] ❌ Error reading from localStorage:", error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const login = (email: string, authToken: string) => {
    console.log("[AUTH CONTEXT] 🔐 Login called with:", {
      email,
      token: authToken ? "present" : "missing",
    })

    try {
      setUser(email)
      setToken(authToken)
      localStorage.setItem("user", email)
      localStorage.setItem("token", authToken)

      console.log("[AUTH CONTEXT] ✅ Auth state updated, redirecting to dashboard")

      // Force redirect to dashboard
      setTimeout(() => {
        router.push("/dashboard")
        router.refresh()
      }, 100)
    } catch (error) {
      console.error("[AUTH CONTEXT] ❌ Error during login:", error)
    }
  }

  const logout = () => {
    console.log("[AUTH CONTEXT] 🚪 Logout called")

    try {
      setUser(null)
      setToken(null)
      localStorage.removeItem("user")
      localStorage.removeItem("token")

      console.log("[AUTH CONTEXT] ✅ Logged out, redirecting to home")
      router.push("/")
      router.refresh()
    } catch (error) {
      console.error("[AUTH CONTEXT] ❌ Error during logout:", error)
    }
  }

  return <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
