"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Shield, Zap, Eye, Server, Brain, Lock } from "lucide-react"

export function LandingPage() {
  return (
    <div className="text-center mb-12">
      <div className="fade-in-up">
        <h1 className="text-5xl md:text-7xl font-bold orbitron mb-6">
          <span className="text-neon-pink glow-text">🤖 AI-Enhanced</span>
          <br />
          <span className="text-electric-blue glow-text">Secure Email</span>
          <br />
          <span className="text-deep-purple glow-text">Server</span>
        </h1>
        <p className="text-xl md:text-2xl text-gray-300 mb-8 rajdhani max-w-4xl mx-auto">
          Advanced Data Communication and Networks (DCN) Project featuring real-time protocol visualization, AI-powered
          threat detection, and military-grade encryption
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-12 fade-in-up" style={{ animationDelay: "0.3s" }}>
        <Card className="synthwave-card">
          <CardContent className="p-6 text-center">
            <Shield className="w-12 h-12 text-neon-pink mx-auto mb-4" />
            <h3 className="text-lg font-bold orbitron text-neon-pink mb-2">TLS Encryption</h3>
            <p className="text-gray-400 text-sm">End-to-end encryption with TLS 1.3 protocol</p>
          </CardContent>
        </Card>

        <Card className="synthwave-card">
          <CardContent className="p-6 text-center">
            <Brain className="w-12 h-12 text-electric-blue mx-auto mb-4" />
            <h3 className="text-lg font-bold orbitron text-electric-blue mb-2">AI Detection</h3>
            <p className="text-gray-400 text-sm">Advanced spam and phishing detection algorithms</p>
          </CardContent>
        </Card>

        <Card className="synthwave-card">
          <CardContent className="p-6 text-center">
            <Eye className="w-12 h-12 text-deep-purple mx-auto mb-4" />
            <h3 className="text-lg font-bold orbitron text-deep-purple mb-2">Real-time DCN</h3>
            <p className="text-gray-400 text-sm">Live protocol monitoring and visualization</p>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap justify-center gap-3 fade-in-up" style={{ animationDelay: "0.6s" }}>
        <Badge className="protocol-smtp">SMTP Protocol</Badge>
        <Badge className="protocol-imap">IMAP Protocol</Badge>
        <Badge className="protocol-pop3">POP3 Protocol</Badge>
        <Badge className="bg-purple-500/20 text-purple-300 border-purple-500/50">
          <Lock className="w-3 h-3 mr-1" />
          TLS 1.3
        </Badge>
        <Badge className="bg-green-500/20 text-green-300 border-green-500/50">
          <Zap className="w-3 h-3 mr-1" />
          AI Powered
        </Badge>
        <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/50">
          <Server className="w-3 h-3 mr-1" />
          Real-time
        </Badge>
      </div>
    </div>
  )
}
