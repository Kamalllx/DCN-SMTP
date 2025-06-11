"use client"

import { useState, useEffect } from "react"

export function useAuth() {
  const [user, setUser] = useState<string | null>(null)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    // Check for stored auth data on mount
    const storedUser = localStorage.getItem("user")
    const storedToken = localStorage.getItem("token")

    if (storedUser && storedToken) {
      setUser(storedUser)
      setToken(storedToken)
    }
  }, [])

  const login = (email: string, authToken: string) => {
    setUser(email)
    setToken(authToken)
    localStorage.setItem("user", email)
    localStorage.setItem("token", authToken)
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem("user")
    localStorage.removeItem("token")
  }

  return { user, token, login, logout }
}
