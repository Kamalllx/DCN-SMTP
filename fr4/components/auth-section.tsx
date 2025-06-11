"use client"

import type React from "react"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/hooks/use-toast"
import { useAuth } from "@/contexts/auth-context"
import { Loader2, Shield, Lock } from "lucide-react"

export function AuthSection() {
  const [isSignUp, setIsSignUp] = useState(false)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  })
  const { toast } = useToast()
  const { login } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.email || !formData.password) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        variant: "destructive",
      })
      return
    }

    setLoading(true)

    try {
      console.log(`[AUTH] Attempting ${isSignUp ? "sign up" : "sign in"} for:`, formData.email)

      const endpoint = isSignUp ? "/api/auth/signup" : "/api/auth/signin"
      const response = await fetch(`http://localhost:5000${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      console.log(`[AUTH] Response status:`, response.status)

      if (response.ok) {
        const data = await response.json()
        console.log(`[AUTH] Response data:`, data)

        if (isSignUp) {
          toast({
            title: "Success",
            description: "Account created successfully! Please sign in.",
          })
          setIsSignUp(false)
          setFormData({ email: "", password: "" })
        } else {
          // Sign in successful
          console.log(`[AUTH] ✅ Sign in successful, calling login with:`, {
            email: formData.email,
            token: data.token ? "present" : "missing",
          })

          toast({
            title: "Welcome",
            description: "Successfully signed in with TLS encryption",
          })

          // Call the login function from context
          login(formData.email, data.token)

          console.log(`[AUTH] Login function called, should redirect to dashboard`)
        }
      } else {
        const errorData = await response.json().catch(() => ({ error: "Unknown error" }))
        console.error(`[AUTH] ❌ Authentication failed:`, errorData)

        toast({
          title: "Error",
          description: errorData.error || "Authentication failed",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error(`[AUTH] ❌ Connection error:`, error)
      toast({
        title: "Error",
        description: "Connection failed. Please check if the backend server is running on localhost:5000",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <Card className="synthwave-card">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl orbitron flex items-center justify-center gap-2">
            <Shield className="w-6 h-6 text-neon-pink" />
            Secure Authentication
            <Lock className="w-6 h-6 text-electric-blue" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-8">
            {/* Sign Up */}
            <div className={`space-y-4 ${!isSignUp ? "opacity-50" : ""}`}>
              <h3 className="text-xl font-semibold text-neon-pink rajdhani">📝 Sign Up</h3>
              <form onSubmit={isSignUp ? handleSubmit : (e) => e.preventDefault()} className="space-y-4">
                <div>
                  <Label htmlFor="signup-email">Email Address</Label>
                  <Input
                    id="signup-email"
                    type="email"
                    placeholder="your@email.com"
                    value={isSignUp ? formData.email : ""}
                    onChange={(e) => isSignUp && setFormData({ ...formData, email: e.target.value })}
                    className="bg-black/50 border-neon-pink/30 focus:border-neon-pink"
                    disabled={!isSignUp || loading}
                  />
                </div>
                <div>
                  <Label htmlFor="signup-password">Password</Label>
                  <Input
                    id="signup-password"
                    type="password"
                    placeholder="8+ chars, mixed case, numbers, special chars"
                    value={isSignUp ? formData.password : ""}
                    onChange={(e) => isSignUp && setFormData({ ...formData, password: e.target.value })}
                    className="bg-black/50 border-neon-pink/30 focus:border-neon-pink"
                    disabled={!isSignUp || loading}
                  />
                </div>
                <Button
                  type={isSignUp ? "submit" : "button"}
                  className="w-full bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 neon-glow"
                  disabled={loading || !isSignUp}
                  onClick={() => !isSignUp && setIsSignUp(true)}
                >
                  {loading && isSignUp ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                  Create Account with TLS Protection
                </Button>
              </form>
            </div>

            {/* Sign In */}
            <div className={`space-y-4 ${isSignUp ? "opacity-50" : ""}`}>
              <h3 className="text-xl font-semibold text-electric-blue rajdhani">🔑 Sign In</h3>
              <form onSubmit={!isSignUp ? handleSubmit : (e) => e.preventDefault()} className="space-y-4">
                <div>
                  <Label htmlFor="signin-email">Email Address</Label>
                  <Input
                    id="signin-email"
                    type="email"
                    placeholder="your@email.com"
                    value={!isSignUp ? formData.email : ""}
                    onChange={(e) => !isSignUp && setFormData({ ...formData, email: e.target.value })}
                    className="bg-black/50 border-electric-blue/30 focus:border-electric-blue"
                    disabled={isSignUp || loading}
                  />
                </div>
                <div>
                  <Label htmlFor="signin-password">Password</Label>
                  <Input
                    id="signin-password"
                    type="password"
                    placeholder="Enter password"
                    value={!isSignUp ? formData.password : ""}
                    onChange={(e) => !isSignUp && setFormData({ ...formData, password: e.target.value })}
                    className="bg-black/50 border-electric-blue/30 focus:border-electric-blue"
                    disabled={isSignUp || loading}
                  />
                </div>
                <Button
                  type={!isSignUp ? "submit" : "button"}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 electric-glow"
                  disabled={loading || isSignUp}
                  onClick={() => isSignUp && setIsSignUp(false)}
                >
                  {loading && !isSignUp ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                  Sign In with TLS Authentication
                </Button>
              </form>
            </div>
          </div>

          <div className="mt-6 text-center">
            <Button
              variant="ghost"
              onClick={() => {
                setIsSignUp(!isSignUp)
                setFormData({ email: "", password: "" })
              }}
              className="text-gray-400 hover:text-white"
              disabled={loading}
            >
              {isSignUp ? "Already have an account? Sign In" : "Need an account? Sign Up"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
