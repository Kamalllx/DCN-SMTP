"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { Mail, Activity, Server, Brain } from "lucide-react"

export function QuickActions() {
  const router = useRouter()

  const actions = [
    {
      title: "Send Test Email",
      description: "Send a test email with AI analysis",
      icon: Mail,
      color: "from-blue-500 to-purple-600",
      action: () => router.push("/emails"),
    },
    {
      title: "Monitor DCN",
      description: "View real-time protocol activity",
      icon: Activity,
      color: "from-green-500 to-emerald-600",
      action: () => router.push("/dcn-monitor"),
    },
    {
      title: "Manage Servers",
      description: "Control email server operations",
      icon: Server,
      color: "from-orange-500 to-red-600",
      action: () => router.push("/servers"),
    },
    {
      title: "AI Analysis",
      description: "Run comprehensive AI analysis",
      icon: Brain,
      color: "from-pink-500 to-purple-600",
      action: () => router.push("/ai-analysis"),
    },
  ]

  return (
    <Card className="synthwave-card">
      <CardHeader>
        <CardTitle className="orbitron text-center text-2xl">
          <span className="text-electric-blue glow-text">Quick Actions</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {actions.map((action, index) => {
            const Icon = action.icon
            return (
              <Button
                key={action.title}
                onClick={action.action}
                className={`h-auto p-6 flex flex-col items-center gap-3 bg-gradient-to-r ${action.color} hover:scale-105 transition-transform`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <Icon className="w-8 h-8" />
                <div className="text-center">
                  <div className="font-semibold">{action.title}</div>
                  <div className="text-xs opacity-80">{action.description}</div>
                </div>
              </Button>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
