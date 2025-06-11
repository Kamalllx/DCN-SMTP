"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { motion, AnimatePresence } from "framer-motion"
import {
  Activity,
  Zap,
  Play,
  Pause,
  RotateCcw,
  Network,
  Info,
  ChevronRight,
  ChevronLeft,
  Mail,
  Database,
  Lock,
  Globe,
  Bot,
  Key,
  Download,
  Upload,
  Archive,
  Trash2,
  Eye,
  EyeOff,
} from "lucide-react"
import type { Socket } from "socket.io-client"

interface DCNProcess {
  protocol: string
  stage: string
  details: string
  timestamp: string
  data?: any
  process_id?: string
}

interface InteractiveDCNMonitorProps {
  socket: Socket | null
}

interface ProtocolNode {
  id: string
  name: string
  icon: React.ReactNode
  color: string
  description: string
  position: { x: number; y: number }
  connections: string[]
  active: boolean
  processes: DCNProcess[]
}

export function InteractiveDCNMonitor({ socket }: InteractiveDCNMonitorProps) {
  const [processes, setProcesses] = useState<DCNProcess[]>([])
  const [persistentProcesses, setPersistentProcesses] = useState<DCNProcess[]>([])
  const [isPlaying, setIsPlaying] = useState(false)
  const [isPaused, setIsPaused] = useState(true)
  const [currentStoryStep, setCurrentStoryStep] = useState(0)
  const [showExplanation, setShowExplanation] = useState(true)
  const [selectedProtocol, setSelectedProtocol] = useState<string | null>(null)
  const [recentEvents, setRecentEvents] = useState<DCNProcess[]>([])
  const [simulationSpeed, setSimulationSpeed] = useState(1)
  const [showProcessDetails, setShowProcessDetails] = useState(true)
  const containerRef = useRef<HTMLDivElement>(null)

  // Enhanced protocol nodes including IMAP and POP3
  const protocolNodes: ProtocolNode[] = [
    {
      id: "smtp",
      name: "SMTP",
      icon: <Mail className="w-6 h-6" />,
      color: "#ff0080",
      description: "Simple Mail Transfer Protocol handles outgoing email transmission and delivery between servers.",
      position: { x: 0, y: 0 },
      connections: ["tls"],
      active: false,
      processes: [],
    },
    {
      id: "imap",
      name: "IMAP",
      icon: <Download className="w-6 h-6" />,
      color: "#ffa500",
      description: "Internet Message Access Protocol allows clients to access and manage emails stored on the server.",
      position: { x: 1, y: 0 },
      connections: ["tls"],
      active: false,
      processes: [],
    },
    {
      id: "pop3",
      name: "POP3",
      icon: <Upload className="w-6 h-6" />,
      color: "#00ff80",
      description: "Post Office Protocol v3 downloads emails from server to client for offline access.",
      position: { x: 2, y: 0 },
      connections: ["tls"],
      active: false,
      processes: [],
    },
    {
      id: "tls",
      name: "TLS Security",
      icon: <Lock className="w-6 h-6" />,
      color: "#8a2be2",
      description: "Transport Layer Security encrypts all communications to protect data in transit.",
      position: { x: 1, y: 1 },
      connections: ["tcp"],
      active: false,
      processes: [],
    },
    {
      id: "tcp",
      name: "TCP/IP",
      icon: <Globe className="w-6 h-6" />,
      color: "#00ffff",
      description: "Transmission Control Protocol ensures reliable delivery of data packets across networks.",
      position: { x: 1, y: 2 },
      connections: ["ai"],
      active: false,
      processes: [],
    },
    {
      id: "ai",
      name: "AI Analysis",
      icon: <Bot className="w-6 h-6" />,
      color: "#ff69b4",
      description: "AI engine analyzes emails for threats, spam, phishing, and content classification.",
      position: { x: 0, y: 3 },
      connections: ["crypto"],
      active: false,
      processes: [],
    },
    {
      id: "crypto",
      name: "Encryption",
      icon: <Key className="w-6 h-6" />,
      color: "#ffd700",
      description: "Advanced encryption protects email content before database storage using AES-256.",
      position: { x: 1, y: 3 },
      connections: ["database"],
      active: false,
      processes: [],
    },
    {
      id: "database",
      name: "Database",
      icon: <Database className="w-6 h-6" />,
      color: "#9370db",
      description: "Secure storage system for encrypted emails with redundancy and backup capabilities.",
      position: { x: 2, y: 3 },
      connections: [],
      active: false,
      processes: [],
    },
  ]

  // Enhanced story steps including all protocols
  const storySteps = [
    {
      title: "Email Reception",
      subtitle: "SMTP Server",
      description: "SMTP server receives incoming emails and initiates the processing pipeline.",
      focusProtocol: "smtp",
      detailedExplanation:
        "The SMTP server acts as the primary entry point for incoming emails. It validates sender credentials, checks email format compliance, performs initial spam filtering based on sender reputation, and establishes secure connections with sending servers.",
      animationDuration: 2,
    },
    {
      title: "Email Retrieval",
      subtitle: "IMAP Protocol",
      description: "IMAP allows clients to access and synchronize emails stored on the server.",
      focusProtocol: "imap",
      detailedExplanation:
        "IMAP enables multiple devices to access the same mailbox simultaneously. It supports server-side email management, folder synchronization, partial message downloading, and maintains email state across different clients.",
      animationDuration: 2,
    },
    {
      title: "Email Download",
      subtitle: "POP3 Protocol",
      description: "POP3 downloads emails from server to client for offline access and local storage.",
      focusProtocol: "pop3",
      detailedExplanation:
        "POP3 provides a simple mechanism for downloading emails to local devices. It's ideal for single-device access scenarios and helps reduce server storage requirements by transferring emails to the client.",
      animationDuration: 2,
    },
    {
      title: "Secure Transmission",
      subtitle: "TLS Encryption",
      description: "TLS encryption secures all email communications during transmission.",
      focusProtocol: "tls",
      detailedExplanation:
        "TLS creates encrypted tunnels for all email protocols (SMTP, IMAP, POP3). It negotiates the strongest available encryption, establishes secure handshakes, and protects against eavesdropping and tampering.",
      animationDuration: 2,
    },
    {
      title: "Network Transport",
      subtitle: "TCP/IP Protocol",
      description: "TCP/IP ensures reliable delivery of email data across complex network infrastructures.",
      focusProtocol: "tcp",
      detailedExplanation:
        "TCP/IP handles packet routing, error detection, retransmission of lost data, flow control, and congestion management. It ensures emails arrive complete and in the correct order across diverse network paths.",
      animationDuration: 2,
    },
    {
      title: "Threat Analysis",
      subtitle: "AI Engine",
      description: "Advanced AI analyzes emails for security threats and content classification.",
      focusProtocol: "ai",
      detailedExplanation:
        "The AI engine employs machine learning algorithms to detect spam, phishing attempts, malware, and suspicious patterns. It analyzes text content, link destinations, attachment types, and sender behavior patterns.",
      animationDuration: 2,
    },
    {
      title: "Content Protection",
      subtitle: "Encryption Process",
      description: "Email content is encrypted using military-grade algorithms before storage.",
      focusProtocol: "crypto",
      detailedExplanation:
        "The encryption system uses AES-256 with unique keys for each email. It implements key rotation, secure key management, and ensures that stored data remains protected even if database access is compromised.",
      animationDuration: 2,
    },
    {
      title: "Secure Storage",
      subtitle: "Database",
      description: "Encrypted emails are stored in a highly secure, redundant database system.",
      focusProtocol: "database",
      detailedExplanation:
        "The database implements multiple security layers including access controls, audit logging, encryption at rest, automated backups, and disaster recovery capabilities. It's designed for high availability and data integrity.",
      animationDuration: 2,
    },
  ]

  useEffect(() => {
    if (socket) {
      socket.on("dcn_process", (data: DCNProcess) => {
        // Always add to persistent processes for analysis
        setPersistentProcesses((prev) => [data, ...prev])

        if (isPlaying && !isPaused) {
          // Add to real-time processes with controlled speed
          setTimeout(() => {
            setProcesses((prev) => [data, ...prev.slice(0, 99)]) // Keep more processes visible

            // Add to recent events with slower pace
            setTimeout(() => {
              setRecentEvents((prev) => [data, ...prev.slice(0, 9)]) // Keep more events
            }, 1000 / simulationSpeed)

            // Update protocol nodes
            const updatedNodes = [...protocolNodes]
            const nodeIndex = updatedNodes.findIndex((n) => n.id === data.protocol.toLowerCase())
            if (nodeIndex >= 0) {
              updatedNodes[nodeIndex].active = true
              updatedNodes[nodeIndex].processes.unshift(data)
              if (updatedNodes[nodeIndex].processes.length > 10) {
                updatedNodes[nodeIndex].processes = updatedNodes[nodeIndex].processes.slice(0, 10)
              }
            }
          }, 500 / simulationSpeed)
        }
      })

      return () => {
        socket.off("dcn_process")
      }
    }
  }, [socket, isPlaying, isPaused, simulationSpeed])

  const simulateProcess = () => {
    if (socket) {
      // Generate multiple processes for better demonstration
      for (let i = 0; i < 5; i++) {
        setTimeout(() => {
          socket.emit("request_dcn_demo")
        }, i * 1000)
      }
    }
  }

  const clearProcessHistory = () => {
    setProcesses([])
    setPersistentProcesses([])
    setRecentEvents([])
  }

  const startStoryMode = () => {
    setIsPlaying(true)
    setIsPaused(false)
    setCurrentStoryStep(0)
    setShowExplanation(true)
  }

  const goToNextStep = () => {
    if (currentStoryStep < storySteps.length - 1) {
      setCurrentStoryStep(currentStoryStep + 1)
      setShowExplanation(true)
    } else {
      setIsPlaying(false)
      setIsPaused(true)
    }
  }

  const goToPrevStep = () => {
    if (currentStoryStep > 0) {
      setCurrentStoryStep(currentStoryStep - 1)
      setShowExplanation(true)
    }
  }

  const togglePlayPause = () => {
    setIsPaused(!isPaused)
  }

  const resetVisualization = () => {
    setIsPlaying(false)
    setIsPaused(true)
    setCurrentStoryStep(0)
    setShowExplanation(true)
    setSelectedProtocol(null)
  }

  const handleProtocolSelect = (protocolId: string) => {
    setSelectedProtocol(selectedProtocol === protocolId ? null : protocolId)
  }

  const currentStep = storySteps[currentStoryStep]
  const currentProtocol = protocolNodes.find((node) => node.id === currentStep?.focusProtocol)

  return (
    <motion.div
      ref={containerRef}
      className="w-full min-h-screen p-4 md:p-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      {/* Enhanced Header Section */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="mb-8 text-center"
      >
        <h1 className="text-4xl md:text-6xl font-bold orbitron mb-4">
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-neon-pink via-electric-blue to-deep-purple glow-text">
            Interactive DCN Monitor
          </span>
        </h1>
        <motion.p
          className="text-xl text-gray-300 rajdhani max-w-3xl mx-auto"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Visualize and understand the complete Data Communication Network protocols in real-time
        </motion.p>
      </motion.div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Enhanced Left Panel - Controls & Info */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <Card className="synthwave-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-electric-blue">
                <Activity className="w-5 h-5" />
                DCN Visualization Controls
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Story Mode Controls */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-neon-pink">Story Mode</h3>
                <div className="flex flex-wrap gap-2">
                  <Button
                    onClick={startStoryMode}
                    className="bg-gradient-to-r from-green-500 to-emerald-600 hover:scale-105 transition-transform"
                    disabled={isPlaying && !isPaused}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Start Tour
                  </Button>
                  <Button onClick={togglePlayPause} variant="outline" disabled={!isPlaying}>
                    {isPaused ? <Play className="w-4 h-4 mr-2" /> : <Pause className="w-4 h-4 mr-2" />}
                    {isPaused ? "Resume" : "Pause"}
                  </Button>
                  <Button onClick={resetVisualization} variant="outline">
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Reset
                  </Button>
                </div>

                {/* Progress Indicator */}
                {isPlaying && (
                  <motion.div
                    className="space-y-2"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                  >
                    <div className="flex justify-between text-sm">
                      <span>Progress:</span>
                      <span>
                        {currentStoryStep + 1} of {storySteps.length}
                      </span>
                    </div>
                    <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-neon-pink to-electric-blue"
                        initial={{ width: 0 }}
                        animate={{ width: `${((currentStoryStep + 1) / storySteps.length) * 100}%` }}
                        transition={{ duration: 0.8, ease: "easeInOut" }}
                      />
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Enhanced Simulation Controls */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-electric-blue">Simulation Controls</h3>
                <div className="space-y-3">
                  <Button
                    onClick={simulateProcess}
                    className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:scale-105 transition-transform"
                  >
                    <Zap className="w-4 h-4 mr-2" />
                    Simulate DCN Process
                  </Button>

                  <div className="space-y-2">
                    <label className="text-sm text-gray-400">Simulation Speed: {simulationSpeed}x</label>
                    <input
                      type="range"
                      min="0.5"
                      max="3"
                      step="0.5"
                      value={simulationSpeed}
                      onChange={(e) => setSimulationSpeed(Number.parseFloat(e.target.value))}
                      className="w-full accent-neon-pink"
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button onClick={clearProcessHistory} size="sm" variant="outline" className="flex-1">
                      <Trash2 className="w-4 h-4 mr-1" />
                      Clear History
                    </Button>
                    <Button
                      onClick={() => setShowProcessDetails(!showProcessDetails)}
                      size="sm"
                      variant="outline"
                      className="flex-1"
                    >
                      {showProcessDetails ? <EyeOff className="w-4 h-4 mr-1" /> : <Eye className="w-4 h-4 mr-1" />}
                      {showProcessDetails ? "Hide" : "Show"} Details
                    </Button>
                  </div>
                </div>
              </div>

              {/* Enhanced Recent Events */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-yellow-400">Recent Events</h3>
                  <Badge className="bg-yellow-500/20 text-yellow-300">{recentEvents.length} events</Badge>
                </div>
                <ScrollArea className="h-[250px] w-full rounded-md border border-gray-700 bg-black/50 p-3">
                  <AnimatePresence>
                    {recentEvents.length > 0 ? (
                      recentEvents.map((event, index) => (
                        <motion.div
                          key={`${event.timestamp}-${index}`}
                          initial={{ opacity: 0, x: -20, scale: 0.9 }}
                          animate={{ opacity: 1, x: 0, scale: 1 }}
                          exit={{ opacity: 0, x: 20, scale: 0.9 }}
                          transition={{ duration: 0.6, delay: index * 0.1 }}
                          className="p-3 mb-2 rounded-lg bg-black/40 border border-gray-600 hover:border-neon-pink/50 transition-colors"
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <Badge
                              className="text-xs font-bold"
                              style={{
                                backgroundColor: protocolNodes.find((n) => n.id === event.protocol.toLowerCase())
                                  ?.color,
                                color: "white",
                              }}
                            >
                              {event.protocol}
                            </Badge>
                            <span className="text-gray-400 text-xs">
                              {new Date(event.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <div className="text-white font-medium text-sm mb-1">{event.stage}</div>
                          <div className="text-gray-300 text-xs">{event.details}</div>
                          {showProcessDetails && event.data && (
                            <motion.div
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: "auto" }}
                              className="mt-2 text-xs text-gray-400 bg-black/30 p-2 rounded font-mono"
                            >
                              {JSON.stringify(event.data, null, 2)}
                            </motion.div>
                          )}
                        </motion.div>
                      ))
                    ) : (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-center text-gray-500 py-8"
                      >
                        <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p>No recent events. Start the tour or simulate a process.</p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </ScrollArea>
              </div>

              {/* Process History */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-deep-purple">Process History</h3>
                  <Badge className="bg-deep-purple/20 text-deep-purple">{persistentProcesses.length} total</Badge>
                </div>
                <ScrollArea className="h-[200px] w-full rounded-md border border-gray-700 bg-black/50 p-3">
                  <AnimatePresence>
                    {persistentProcesses.length > 0 ? (
                      persistentProcesses.map((process, index) => (
                        <motion.div
                          key={`${process.timestamp}-${index}`}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.05 }}
                          className="p-2 mb-1 rounded bg-black/30 border border-gray-700 text-xs"
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <Badge
                              className="text-xs"
                              style={{
                                backgroundColor: protocolNodes.find((n) => n.id === process.protocol.toLowerCase())
                                  ?.color,
                                color: "white",
                              }}
                            >
                              {process.protocol}
                            </Badge>
                            <span className="text-gray-400">{new Date(process.timestamp).toLocaleTimeString()}</span>
                          </div>
                          <div className="text-gray-300">{process.stage}</div>
                        </motion.div>
                      ))
                    ) : (
                      <div className="text-center text-gray-500 py-4">
                        <Archive className="w-6 h-6 mx-auto mb-2 opacity-50" />
                        <p>No process history available.</p>
                      </div>
                    )}
                  </AnimatePresence>
                </ScrollArea>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Enhanced Center Panel - Main Visualization */}
        <motion.div
          className="lg:col-span-2"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <Card className="synthwave-card h-full">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-neon-pink">
                  <Network className="w-5 h-5" />
                  DCN Protocol Flow
                </span>
                {isPlaying && (
                  <div className="flex items-center gap-2">
                    <Button size="sm" variant="outline" onClick={goToPrevStep} disabled={currentStoryStep === 0}>
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <span className="text-sm text-gray-400">
                      Step {currentStoryStep + 1}/{storySteps.length}
                    </span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={goToNextStep}
                      disabled={currentStoryStep === storySteps.length - 1}
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="relative h-[600px] overflow-hidden">
              {/* Enhanced Protocol Flow Visualization */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative w-full max-w-4xl h-full">
                  {/* Connection Lines */}
                  <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 0 }}>
                    {protocolNodes.map((node) =>
                      node.connections.map((targetId) => {
                        const target = protocolNodes.find((n) => n.id === targetId)
                        if (!target) return null

                        // Enhanced positioning for better layout
                        const startX = node.position.x * 30 + 15
                        const startY = node.position.y * 20 + 15
                        const endX = target.position.x * 30 + 15
                        const endY = target.position.y * 20 + 15

                        const isActive =
                          isPlaying &&
                          !isPaused &&
                          (node.id === currentStep?.focusProtocol || targetId === currentStep?.focusProtocol)

                        return (
                          <motion.line
                            key={`${node.id}-${targetId}`}
                            x1={`${startX}%`}
                            y1={`${startY}%`}
                            x2={`${endX}%`}
                            y2={`${endY}%`}
                            stroke={isActive ? node.color : "#444"}
                            strokeWidth={isActive ? 4 : 2}
                            strokeDasharray={isActive ? "none" : "8,4"}
                            initial={{ pathLength: 0, opacity: 0.3 }}
                            animate={{
                              pathLength: isActive ? 1 : 0.5,
                              opacity: isActive ? 1 : 0.4,
                              strokeWidth: isActive ? 4 : 2,
                            }}
                            transition={{ duration: 1.5, ease: "easeInOut" }}
                          />
                        )
                      }),
                    )}
                  </svg>

                  {/* Enhanced Protocol Nodes */}
                  <div className="grid grid-cols-3 gap-6 relative z-10 h-full">
                    {protocolNodes.map((node) => {
                      const isActive = isPlaying && !isPaused && node.id === currentStep?.focusProtocol
                      const isSelected = selectedProtocol === node.id

                      return (
                        <motion.div
                          key={node.id}
                          className={`p-4 rounded-xl cursor-pointer transition-all duration-500 ${
                            isActive || isSelected ? "ring-4" : "ring-1"
                          }`}
                          style={{
                            gridColumn: node.position.x + 1,
                            gridRow: node.position.y + 1,
                            backgroundColor: `${node.color}15`,
                            borderColor: node.color,
                            boxShadow: isActive ? `0 0 25px ${node.color}60` : "none",
                            border: `2px solid ${isActive || isSelected ? node.color : node.color + "40"}`,
                          }}
                          onClick={() => handleProtocolSelect(node.id)}
                          whileHover={{ scale: 1.05, y: -5 }}
                          whileTap={{ scale: 0.95 }}
                          animate={{
                            scale: isActive ? 1.1 : 1,
                            boxShadow: isActive ? `0 0 30px ${node.color}80` : "none",
                            y: isActive ? -10 : 0,
                          }}
                          transition={{ duration: 0.5, ease: "easeInOut" }}
                        >
                          <div className="flex flex-col items-center text-center gap-3">
                            <motion.div
                              className="w-16 h-16 rounded-full flex items-center justify-center"
                              style={{ backgroundColor: `${node.color}30` }}
                              animate={{
                                backgroundColor: isActive ? `${node.color}50` : `${node.color}30`,
                              }}
                            >
                              {node.icon}
                            </motion.div>
                            <h3 className="font-bold text-white text-sm">{node.name}</h3>
                            <AnimatePresence>
                              {node.processes.length > 0 && (
                                <motion.div
                                  initial={{ opacity: 0, scale: 0 }}
                                  animate={{ opacity: 1, scale: 1 }}
                                  exit={{ opacity: 0, scale: 0 }}
                                >
                                  <Badge className="bg-neon-pink text-white text-xs">
                                    {node.processes.length} active
                                  </Badge>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
                        </motion.div>
                      )
                    })}
                  </div>

                  {/* Enhanced Data Flow Animation */}
                  {isPlaying && !isPaused && currentStep && (
                    <DataFlowAnimation
                      currentStep={currentStoryStep}
                      protocolNodes={protocolNodes}
                      storySteps={storySteps}
                    />
                  )}
                </div>
              </div>

              {/* Enhanced Step Explanation Overlay */}
              <AnimatePresence>
                {isPlaying && showExplanation && currentStep && (
                  <motion.div
                    initial={{ opacity: 0, y: 100 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 100 }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                    className="absolute bottom-0 left-0 right-0 p-6 bg-black/80 backdrop-blur-lg rounded-t-xl border-t border-neon-pink/30"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-1">
                        <motion.h3
                          className="text-2xl font-bold text-white mb-2"
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.2 }}
                        >
                          {currentStep.title}
                          <span className="text-neon-pink ml-3">• {currentStep.subtitle}</span>
                        </motion.h3>
                        <motion.p
                          className="text-gray-300 mb-3 text-lg"
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.3 }}
                        >
                          {currentStep.description}
                        </motion.p>
                        <Button
                          size="sm"
                          variant="link"
                          onClick={() => setShowExplanation(false)}
                          className="text-electric-blue p-0 hover:text-neon-pink transition-colors"
                        >
                          Hide explanation
                        </Button>
                      </div>
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.4 }}
                      >
                        <Button
                          onClick={goToNextStep}
                          disabled={currentStoryStep === storySteps.length - 1}
                          className="bg-gradient-to-r from-neon-pink to-electric-blue hover:scale-105 transition-transform"
                          size="lg"
                        >
                          {currentStoryStep === storySteps.length - 1 ? "Finish Tour" : "Next Step"}
                          <ChevronRight className="w-5 h-5 ml-2" />
                        </Button>
                      </motion.div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Enhanced Detailed Information Panel */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.6 }}
      >
        <Card className="synthwave-card mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-deep-purple">
              <Info className="w-5 h-5" />
              Detailed Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <AnimatePresence mode="wait">
              {selectedProtocol ? (
                <ProtocolDetails
                  key="protocol"
                  protocol={protocolNodes.find((n) => n.id === selectedProtocol)!}
                  processes={persistentProcesses.filter((p) => p.protocol.toLowerCase() === selectedProtocol)}
                />
              ) : isPlaying && currentStep ? (
                <StepDetails key="step" step={currentStep} />
              ) : (
                <SystemOverview key="overview" protocolNodes={protocolNodes} processes={persistentProcesses} />
              )}
            </AnimatePresence>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}

// Enhanced Data Flow Animation Component
function DataFlowAnimation({
  currentStep,
  protocolNodes,
  storySteps,
}: {
  currentStep: number
  protocolNodes: ProtocolNode[]
  storySteps: any[]
}) {
  const step = storySteps[currentStep]
  const protocol = protocolNodes.find((p) => p.id === step.focusProtocol)

  if (!protocol) return null

  const nextProtocolId = protocol.connections[0]
  const nextProtocol = protocolNodes.find((p) => p.id === nextProtocolId)

  if (!nextProtocol) return null

  const startX = protocol.position.x * 30 + 15
  const startY = protocol.position.y * 20 + 15
  const endX = nextProtocol.position.x * 30 + 15
  const endY = nextProtocol.position.y * 20 + 15

  return (
    <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 20, pointerEvents: "none" }}>
      <defs>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <motion.circle
        r="10"
        fill={protocol.color}
        filter="url(#glow)"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <animateMotion
          dur={`${step.animationDuration}s`}
          repeatCount="indefinite"
          path={`M ${startX}% ${startY}% L ${endX}% ${endY}%`}
        />
      </motion.circle>

      {/* Additional particles for enhanced effect */}
      {[...Array(3)].map((_, i) => (
        <motion.circle
          key={i}
          r="4"
          fill={protocol.color}
          opacity="0.6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.6 }}
          transition={{ duration: 0.5, delay: i * 0.2 }}
        >
          <animateMotion
            dur={`${step.animationDuration + i * 0.5}s`}
            repeatCount="indefinite"
            path={`M ${startX}% ${startY}% L ${endX}% ${endY}%`}
            begin={`${i * 0.3}s`}
          />
        </motion.circle>
      ))}
    </svg>
  )
}

// Enhanced Protocol Details Component
function ProtocolDetails({ protocol, processes }: { protocol: ProtocolNode; processes: DCNProcess[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div className="flex items-center gap-4">
        <motion.div
          className="w-20 h-20 rounded-full flex items-center justify-center"
          style={{ backgroundColor: `${protocol.color}40` }}
          whileHover={{ scale: 1.1, rotate: 5 }}
        >
          {protocol.icon}
        </motion.div>
        <div>
          <h3 className="text-3xl font-bold text-white">{protocol.name}</h3>
          <Badge className="text-white mt-2" style={{ backgroundColor: protocol.color }}>
            {processes.length} total processes
          </Badge>
        </div>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <h4 className="text-xl font-semibold text-gray-300 mb-3">Description</h4>
        <p className="text-gray-400 text-lg leading-relaxed">{protocol.description}</p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <h4 className="text-xl font-semibold text-gray-300 mb-3">Process History</h4>
        <ScrollArea className="h-[400px] w-full rounded-md border border-gray-700 bg-black/50 p-4">
          <div className="space-y-3">
            {processes.length > 0 ? (
              processes.map((process, index) => (
                <motion.div
                  key={`${process.timestamp}-${index}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.05 }}
                  className="p-4 rounded-lg bg-black/40 border border-gray-600 hover:border-neon-pink/50 transition-colors"
                >
                  <div className="flex justify-between items-center mb-2">
                    <div className="font-semibold text-white text-lg">{process.stage}</div>
                    <div className="text-sm text-gray-400">{new Date(process.timestamp).toLocaleString()}</div>
                  </div>
                  <div className="text-gray-300 mb-2">{process.details}</div>
                  {process.data && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      className="text-xs text-gray-400 bg-black/30 p-3 rounded font-mono"
                    >
                      {JSON.stringify(process.data, null, 2)}
                    </motion.div>
                  )}
                </motion.div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-8">
                <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg">No process history for this protocol.</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </motion.div>
    </motion.div>
  )
}

// Enhanced Step Details Component
function StepDetails({ step }: { step: any }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}>
        <h3 className="text-3xl font-bold text-white mb-2">
          {step.title}
          <span className="text-neon-pink ml-3">• {step.subtitle}</span>
        </h3>
        <Badge className="bg-electric-blue text-white text-lg px-4 py-2">Protocol: {step.focusProtocol}</Badge>
      </motion.div>

      <motion.div
        className="p-6 rounded-xl bg-black/40 border border-gray-600"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
      >
        <h4 className="text-xl font-semibold text-electric-blue mb-3">Detailed Explanation</h4>
        <p className="text-gray-300 text-lg leading-relaxed">{step.detailedExplanation}</p>
      </motion.div>

      <div className="grid md:grid-cols-2 gap-6">
        <motion.div
          className="p-6 rounded-xl bg-black/40 border border-gray-600"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h4 className="text-xl font-semibold text-neon-pink mb-4">Key Features</h4>
          <ul className="list-disc list-inside text-gray-300 space-y-2 text-lg">
            <li>End-to-end encryption for maximum security</li>
            <li>Real-time threat detection and prevention</li>
            <li>Automatic protocol negotiation</li>
            <li>Comprehensive logging and monitoring</li>
          </ul>
        </motion.div>
        <motion.div
          className="p-6 rounded-xl bg-black/40 border border-gray-600"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h4 className="text-xl font-semibold text-yellow-400 mb-4">Security Measures</h4>
          <ul className="list-disc list-inside text-gray-300 space-y-2 text-lg">
            <li>TLS 1.3 with perfect forward secrecy</li>
            <li>AES-256 encryption for stored data</li>
            <li>AI-powered anomaly detection</li>
            <li>Regular security audits and updates</li>
          </ul>
        </motion.div>
      </div>
    </motion.div>
  )
}

// Enhanced System Overview Component
function SystemOverview({ protocolNodes, processes }: { protocolNodes: ProtocolNode[]; processes: DCNProcess[] }) {
  const activeProtocols = protocolNodes.filter((n) => n.active).length
  const totalProcesses = processes.length
  const protocolStats = protocolNodes.map((node) => ({
    ...node,
    count: processes.filter((p) => p.protocol.toLowerCase() === node.id).length,
  }))

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Processes", value: totalProcesses, color: "neon-pink" },
          { label: "Active Protocols", value: activeProtocols, color: "electric-blue" },
          { label: "System Uptime", value: "100%", color: "green-400" },
          { label: "Security Alerts", value: "0", color: "yellow-400" },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            className={`p-6 rounded-xl bg-black/40 border border-${stat.color}/30 text-center`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05, y: -5 }}
          >
            <div className={`text-4xl font-bold text-${stat.color} mb-2`}>{stat.value}</div>
            <div className="text-sm text-gray-400">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <h3 className="text-2xl font-semibold text-gray-300 mb-6">Protocol Activity Overview</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {protocolStats.map((stat, index) => (
            <motion.div
              key={stat.id}
              initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="flex items-center justify-between p-4 rounded-xl bg-black/40 border border-gray-600 hover:border-neon-pink/50 transition-colors"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-center gap-4">
                <motion.div
                  className="w-12 h-12 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: `${stat.color}40` }}
                  whileHover={{ rotate: 10 }}
                >
                  {stat.icon}
                </motion.div>
                <div>
                  <div className="font-semibold text-white text-lg">{stat.name}</div>
                  <div className="text-sm text-gray-400">{stat.count} processes</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-24 bg-gray-700 h-3 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ backgroundColor: stat.color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${(stat.count / Math.max(1, totalProcesses)) * 100}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                  />
                </div>
                <Badge className="text-white" style={{ backgroundColor: stat.active ? stat.color : "#666" }}>
                  {stat.active ? "Active" : "Idle"}
                </Badge>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
        <h3 className="text-2xl font-semibold text-gray-300 mb-4">System Information</h3>
        <div className="p-6 rounded-xl bg-black/40 border border-gray-600">
          <p className="text-gray-300 mb-4 text-lg leading-relaxed">
            The DCN Monitor provides comprehensive visualization of the complete email processing pipeline, from initial
            reception through multiple security layers to final encrypted storage. Each protocol plays a critical role
            in ensuring secure, reliable, and efficient communication.
          </p>
          <p className="text-gray-300 text-lg leading-relaxed">
            Click on any protocol node to view detailed information and process history, or use the Story Mode to take a
            guided tour through the entire process flow with detailed explanations at each step.
          </p>
        </div>
      </motion.div>
    </motion.div>
  )
}
