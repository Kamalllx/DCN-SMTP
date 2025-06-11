"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { User, Shield, LogOut, Mail, Send } from "lucide-react"

interface UserInfoProps {
  user: string
  onLogout: () => void
}

export function UserInfo({ user, onLogout }: UserInfoProps) {
  const { toast } = useToast()

  const sendTestEmail = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/send-test-email", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: user,
          to: user,
          subject: "Test Email from AI Email System",
          content:
            "This is a test email to verify the system is working correctly. The email is encrypted and transmitted over TLS.",
        }),
      })

      if (response.ok) {
        const result = await response.json()
        toast({
          title: "Success",
          description: `Test email sent successfully! ${result.keywords_detected ? `⚠️ ${result.keywords_detected} keywords detected` : ""}`,
        })
      } else {
        const data = await response.json()
        toast({
          title: "Error",
          description: data.error || "Failed to send test email",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Connection failed",
        variant: "destructive",
      })
    }
  }

  return (
    <Card className="synthwave-card">
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-pink-500 to-purple-600 flex items-center justify-center">
              <User className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold orbitron text-neon-pink">👤 Welcome, {user}</h2>
              <p className="text-gray-400 rajdhani">
                🔒 TLS encrypted session active • Last login: {new Date().toLocaleString()}
              </p>
              <div className="flex gap-2 mt-2">
                <Badge className="bg-green-500/20 text-green-300 border-green-500/50">
                  <Shield className="w-3 h-3 mr-1" />
                  TLS 1.3
                </Badge>
                <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/50">
                  <Mail className="w-3 h-3 mr-1" />
                  Encrypted
                </Badge>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={sendTestEmail}
              className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700"
            >
              <Send className="w-4 h-4 mr-2" />📤 Send Test Email
            </Button>
            <Button
              variant="destructive"
              onClick={onLogout}
              className="bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
