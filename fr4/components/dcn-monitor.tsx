"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Activity, Zap, Trash2 } from "lucide-react"
import type { Socket } from "socket.io-client"

interface DCNProcess {
  protocol: string
  stage: string
  details: string
  timestamp: string
  data?: any
  process_id?: string
}

interface DCNMonitorProps {
  socket: Socket | null
}

export function DCNMonitor({ socket }: DCNMonitorProps) {
  const [processes, setProcesses] = useState<DCNProcess[]>([])

  useEffect(() => {
    if (socket) {
      socket.on("dcn_process", (data: DCNProcess) => {
        setProcesses((prev) => [data, ...prev.slice(0, 49)]) // Keep last 50 entries
      })

      return () => {
        socket.off("dcn_process")
      }
    }
  }, [socket])

  const clearLogs = () => {
    setProcesses([])
  }

  const simulateProcess = () => {
    if (socket) {
      socket.emit("request_dcn_demo")
    }
  }

  const getProtocolColor = (protocol: string) => {
    switch (protocol.toLowerCase()) {
      case "smtp":
        return "protocol-smtp"
      case "imap":
        return "protocol-imap"
      case "pop3":
        return "protocol-pop3"
      case "tls":
        return "bg-purple-500/20 text-purple-300 border-purple-500/50"
      case "tcp":
        return "bg-gray-500/20 text-gray-300 border-gray-500/50"
      case "ai":
        return "bg-pink-500/20 text-pink-300 border-pink-500/50"
      case "crypto":
        return "bg-yellow-500/20 text-yellow-300 border-yellow-500/50"
      case "database":
        return "bg-indigo-500/20 text-indigo-300 border-indigo-500/50"
      default:
        return "bg-blue-500/20 text-blue-300 border-blue-500/50"
    }
  }

  return (
    <Card className="synthwave-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 orbitron text-electric-blue">
          <Activity className="w-5 h-5" />📡 Real-time DCN Process Visualization
        </CardTitle>
        <p className="text-gray-400 rajdhani">Watch live SMTP, IMAP, and POP3 protocol operations as they happen</p>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-4">
          <Button
            onClick={clearLogs}
            variant="outline"
            size="sm"
            className="border-red-500/50 text-red-300 hover:bg-red-500/20"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Clear DCN Logs
          </Button>
          <Button
            onClick={simulateProcess}
            size="sm"
            className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
          >
            <Zap className="w-4 h-4 mr-2" />
            Simulate DCN Process
          </Button>
        </div>

        <ScrollArea className="h-80 w-full rounded-md border border-gray-700 bg-black/50 p-4">
          {processes.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No DCN processes yet. Click "Simulate DCN Process" to see activity.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {processes.map((process, index) => (
                <div
                  key={`${process.timestamp}-${index}`}
                  className={`p-3 rounded-lg border-l-4 ${
                    process.protocol.toLowerCase() === "smtp"
                      ? "border-l-red-500 bg-red-500/10"
                      : process.protocol.toLowerCase() === "imap"
                        ? "border-l-orange-500 bg-orange-500/10"
                        : process.protocol.toLowerCase() === "pop3"
                          ? "border-l-green-500 bg-green-500/10"
                          : process.protocol.toLowerCase() === "tls"
                            ? "border-l-purple-500 bg-purple-500/10"
                            : process.protocol.toLowerCase() === "tcp"
                              ? "border-l-gray-500 bg-gray-500/10"
                              : process.protocol.toLowerCase() === "ai"
                                ? "border-l-pink-500 bg-pink-500/10"
                                : process.protocol.toLowerCase() === "crypto"
                                  ? "border-l-yellow-500 bg-yellow-500/10"
                                  : process.protocol.toLowerCase() === "database"
                                    ? "border-l-indigo-500 bg-indigo-500/10"
                                    : "border-l-blue-500 bg-blue-500/10"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={`protocol-badge ${getProtocolColor(process.protocol)}`}>
                          {process.protocol}
                        </Badge>
                        <span className="text-sm text-gray-400">
                          {new Date(process.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="font-semibold text-white mb-1">{process.stage}</div>
                      <div className="text-sm text-gray-300">{process.details}</div>
                      {process.data && (
                        <div className="mt-2 text-xs text-gray-400 bg-black/30 p-2 rounded font-mono">
                          {JSON.stringify(process.data, null, 2)}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
