"use client"

import { useState } from "react"
import { usePathname, useRouter } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/auth-context"
import { Home, Mail, Activity, Server, Brain, LogOut, Menu, X, Shield, BarChart3, Lock } from "lucide-react"

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/emails", label: "Emails", icon: Mail },
  { href: "/dcn-monitor", label: "DCN Monitor", icon: Activity },
  { href: "/servers", label: "Servers", icon: Server },
  { href: "/ai-analysis", label: "AI Analysis", icon: Brain },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/security", label: "Security", icon: Lock },
]

export function Navigation() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuth()

  const handleNavigation = (href: string) => {
    console.log(`[NAVIGATION] Navigating to: ${href}`)
    router.push(href)
    setIsMobileMenuOpen(false)
  }

  const handleLogout = () => {
    console.log(`[NAVIGATION] Logout clicked`)
    logout()
  }

  // Don't show navigation if no user
  if (!user) {
    return null
  }

  return (
    <>
      {/* Desktop Navigation */}
      <Card className="synthwave-card m-4 hidden md:block">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="w-8 h-8 text-neon-pink" />
              <span className="text-xl font-bold orbitron text-neon-pink">AI Email System</span>
            </div>

            <nav className="flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                return (
                  <button
                    key={item.href}
                    onClick={() => handleNavigation(item.href)}
                    className={`nav-link ${isActive ? "active" : ""}`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.label}
                  </button>
                )
              })}
            </nav>

            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400 rajdhani">Welcome, {user}</span>
              <Button
                onClick={handleLogout}
                variant="destructive"
                size="sm"
                className="bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Mobile Navigation */}
      <Card className="synthwave-card m-4 md:hidden">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="w-6 h-6 text-neon-pink" />
              <span className="text-lg font-bold orbitron text-neon-pink">AI Email</span>
            </div>

            <Button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} variant="ghost" size="sm">
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>

          {isMobileMenuOpen && (
            <div className="mt-4 pt-4 border-t border-gray-700">
              <nav className="space-y-2">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const isActive = pathname === item.href
                  return (
                    <button
                      key={item.href}
                      onClick={() => handleNavigation(item.href)}
                      className={`w-full text-left nav-link ${isActive ? "active" : ""}`}
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {item.label}
                    </button>
                  )
                })}
                <button onClick={handleLogout} className="w-full text-left nav-link text-red-400 hover:text-red-300">
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </button>
              </nav>
            </div>
          )}
        </CardContent>
      </Card>
    </>
  )
}
