"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useToast } from "@/hooks/use-toast"
import { FileText, RefreshCw, Trash2 } from "lucide-react"

interface LogEntry {
  _id: string
  timestamp: string
  activity_type: string
  details: string
  severity?: string
}

export function SystemLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    loadLogs()
    const interval = setInterval(loadLogs, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const loadLogs = async () => {
    setLoading(true)
    try {
      const response = await fetch("http://localhost:5000/api/logs")
      if (response.ok) {
        const data = await response.json()
        setLogs(data.logs || [])
      }
    } catch (error) {
      console.error("Failed to load logs:", error)
    } finally {
      setLoading(false)
    }
  }

  const clearLogs = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/logs/clear", {
        method: "POST",
      })

      if (response.ok) {
        toast({
          title: "Success",
          description: "Logs cleared successfully",
        })
        loadLogs()
      } else {
        toast({
          title: "Error",
          description: "Failed to clear logs",
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

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case "error":
        return "text-red-400"
      case "warning":
        return "text-yellow-400"
      case "info":
        return "text-blue-400"
      default:
        return "text-gray-300"
    }
  }

  return (
    <Card className="synthwave-card">
      <CardHeader>
        <CardTitle className="orbitron text-yellow-400 flex items-center gap-2">
          <FileText className="w-5 h-5" />📋 System Activity Logs
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-4">
          <Button
            onClick={loadLogs}
            disabled={loading}
            size="sm"
            variant="outline"
            className="border-blue-500/50 text-blue-300 hover:bg-blue-500/20"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh Logs
          </Button>
          <Button
            onClick={clearLogs}
            size="sm"
            variant="outline"
            className="border-red-500/50 text-red-300 hover:bg-red-500/20"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Clear Logs
          </Button>
        </div>

        <ScrollArea className="h-80 w-full rounded-md border border-gray-700 bg-black/50 p-4 font-mono text-sm">
          {logs.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No system logs available</p>
            </div>
          ) : (
            <div className="space-y-2">
              {logs.map((log) => (
                <div key={log._id} className="flex items-start gap-2 text-xs">
                  <span className="text-gray-500 whitespace-nowrap">
                    [{new Date(log.timestamp).toLocaleTimeString()}]
                  </span>
                  <span className={`font-semibold ${getSeverityColor(log.severity || "info")}`}>
                    {log.activity_type}:
                  </span>
                  <span className="text-gray-300 flex-1">{log.details}</span>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
