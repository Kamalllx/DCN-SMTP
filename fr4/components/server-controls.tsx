"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Server, Play, Square, RotateCcw } from "lucide-react"

export function ServerControls() {
  const [serverStatus, setServerStatus] = useState({
    smtp: "running",
    imap: "running",
    pop3: "running",
  })
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleServerAction = async (action: "start" | "stop" | "restart") => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:5000/api/servers/${action}`, {
        method: "POST",
      })

      const data = await response.json()

      if (response.ok) {
        toast({
          title: "Success",
          description: data.message,
        })

        if (action === "start") {
          setServerStatus({ smtp: "running", imap: "running", pop3: "running" })
        } else if (action === "stop") {
          setServerStatus({ smtp: "stopped", imap: "stopped", pop3: "stopped" })
        }
      } else {
        toast({
          title: "Error",
          description: data.message || `Failed to ${action} servers`,
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Connection failed",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="synthwave-card">
      <CardHeader>
        <CardTitle className="orbitron text-deep-purple flex items-center gap-2">
          <Server className="w-5 h-5" />
          🖥️ DCN Server Management
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid md:grid-cols-2 gap-6">
          {/* Server Status */}
          <div>
            <h3 className="text-lg font-semibold rajdhani text-electric-blue mb-4">Server Status</h3>
            <div className="space-y-3">
              <div
                className={`p-3 rounded-lg border-l-4 ${
                  serverStatus.smtp === "running"
                    ? "border-l-green-500 bg-green-500/10"
                    : "border-l-red-500 bg-red-500/10"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge className="protocol-smtp">SMTP</Badge>
                    <span className="text-sm">Port 587 - TLS Ready</span>
                  </div>
                  <Badge className={serverStatus.smtp === "running" ? "threat-low" : "threat-high"}>
                    {serverStatus.smtp === "running" ? "🟢 Running" : "🔴 Stopped"}
                  </Badge>
                </div>
              </div>

              <div
                className={`p-3 rounded-lg border-l-4 ${
                  serverStatus.imap === "running"
                    ? "border-l-green-500 bg-green-500/10"
                    : "border-l-red-500 bg-red-500/10"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge className="protocol-imap">IMAP</Badge>
                    <span className="text-sm">Port 993 - SSL Active</span>
                  </div>
                  <Badge className={serverStatus.imap === "running" ? "threat-low" : "threat-high"}>
                    {serverStatus.imap === "running" ? "🟢 Running" : "🔴 Stopped"}
                  </Badge>
                </div>
              </div>

              <div
                className={`p-3 rounded-lg border-l-4 ${
                  serverStatus.pop3 === "running"
                    ? "border-l-green-500 bg-green-500/10"
                    : "border-l-red-500 bg-red-500/10"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge className="protocol-pop3">POP3</Badge>
                    <span className="text-sm">Port 995 - SSL Active</span>
                  </div>
                  <Badge className={serverStatus.pop3 === "running" ? "threat-low" : "threat-high"}>
                    {serverStatus.pop3 === "running" ? "🟢 Running" : "🔴 Stopped"}
                  </Badge>
                </div>
              </div>
            </div>
          </div>

          {/* Server Controls */}
          <div>
            <h3 className="text-lg font-semibold rajdhani text-neon-pink mb-4">Server Controls</h3>
            <div className="space-y-3">
              <Button
                onClick={() => handleServerAction("start")}
                disabled={loading}
                className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
              >
                <Play className="w-4 h-4 mr-2" />🟢 Start All Servers
              </Button>
              <Button
                onClick={() => handleServerAction("stop")}
                disabled={loading}
                variant="destructive"
                className="w-full bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700"
              >
                <Square className="w-4 h-4 mr-2" />🔴 Stop All Servers
              </Button>
              <Button
                onClick={() => handleServerAction("restart")}
                disabled={loading}
                variant="outline"
                className="w-full border-blue-500/50 text-blue-300 hover:bg-blue-500/20"
              >
                <RotateCcw className="w-4 h-4 mr-2" />🔄 Restart Servers
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
