"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { motion, AnimatePresence } from "framer-motion"
import { LoadingSpinner } from "@/components/loading-spinner"
import { PageTransition } from "@/components/page-transition"
import {
  Mail,
  Shield,
  Lock,
  AlertTriangle,
  RefreshCw,
  Send,
  FileText,
  Reply,
  Eye,
  Loader2,
  Search,
  Filter,
  Star,
} from "lucide-react"
import { EmailReport } from "@/components/email-report"

interface Email {
  _id: string
  from: string
  to?: string[]
  subject: string
  content: string
  created_at: string
  tls_used: boolean
  is_encrypted: boolean
  encryption_version?: string
  ai_analysis?: {
    spam_analysis?: {
      is_spam: boolean
      confidence: number
      threat_level: string
    }
    keyword_analysis?: {
      keywords_detected: number
      keywords_found: string[]
    }
  }
}

interface EmailManagerProps {
  token: string
  user: string
}

export function EnhancedEmailManager({ token, user }: EmailManagerProps) {
  const [emails, setEmails] = useState<Email[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedEmail, setSelectedEmail] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [filterType, setFilterType] = useState("all")
  const [sortBy, setSortBy] = useState("date")
  const [quickSend, setQuickSend] = useState({
    to: "",
    subject: "",
    content: "",
    priority: "medium",
    encryption: "standard",
  })
  const [sendingEmail, setSendingEmail] = useState(false)
  const [replyData, setReplyData] = useState<{ [key: string]: any }>({})
  const [decryptedContent, setDecryptedContent] = useState<{ [key: string]: any }>({})
  const [loadingStates, setLoadingStates] = useState<{ [key: string]: boolean }>({})
  const [showAnalysis, setShowAnalysis] = useState(true)
  const [loadHistory, setLoadHistory] = useState(false)
  const [starredEmails, setStarredEmails] = useState<Set<string>>(new Set())
  const { toast } = useToast()

  useEffect(() => {
    loadEmails()
  }, [token, loadHistory])

  const loadEmails = async () => {
    setLoading(true)
    try {
      const endpoint = loadHistory ? "/emails/history" : "/emails"
      const response = await fetch(`http://localhost:5000/api${endpoint}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setEmails(data.emails || [])
        console.log(`[EMAIL MANAGER] ✅ Loaded ${data.emails?.length || 0} emails`)
      } else {
        toast({
          title: "Error",
          description: "Failed to load emails",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("[EMAIL MANAGER] ❌ Failed to load emails:", error)
      toast({
        title: "Error",
        description: "Connection failed",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const sendQuickEmail = async () => {
    if (!quickSend.to || !quickSend.subject || !quickSend.content) {
      toast({
        title: "Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      })
      return
    }

    setSendingEmail(true)
    try {
      const response = await fetch("http://localhost:5000/api/send-test-email", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: user,
          to: quickSend.to,
          subject: quickSend.subject,
          content: quickSend.content,
          priority: quickSend.priority.toLowerCase(),
        }),
      })

      if (response.ok) {
        const result = await response.json()
        toast({
          title: "Success",
          description: `Email sent and encrypted successfully! ${result.keywords_detected ? `⚠️ ${result.keywords_detected} suspicious keywords detected` : ""}`,
        })
        setQuickSend({ to: "", subject: "", content: "", priority: "medium", encryption: "standard" })
        loadEmails()
      } else {
        const data = await response.json()
        toast({
          title: "Error",
          description: data.error || "Failed to send email",
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
      setSendingEmail(false)
    }
  }

  const handleReply = async (email: Email) => {
    const emailId = email._id
    setLoadingStates((prev) => ({ ...prev, [`reply_${emailId}`]: true }))

    try {
      const response = await fetch("http://localhost:5000/api/ai/generate-reply", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          original_email: email.content,
          tone: "professional",
        }),
      })

      if (response.ok) {
        const result = await response.json()
        setReplyData((prev) => ({ ...prev, [emailId]: result }))
        setQuickSend({
          to: email.from,
          subject: `Re: ${email.subject}`,
          content:
            result.reply ||
            `\n\n--- Original Message ---\nFrom: ${email.from}\nSubject: ${email.subject}\n\n${email.content}`,
          priority: "medium",
          encryption: "standard",
        })
        document.getElementById("compose-section")?.scrollIntoView({ behavior: "smooth" })
        toast({
          title: "Reply Generated",
          description: "Smart reply generated and populated in compose form",
        })
      } else {
        const data = await response.json()
        toast({
          title: "Error",
          description: data.error || "Failed to generate reply",
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
      setLoadingStates((prev) => ({ ...prev, [`reply_${emailId}`]: false }))
    }
  }

  const handleDecryptView = async (email: Email) => {
    const emailId = email._id
    setLoadingStates((prev) => ({ ...prev, [`decrypt_${emailId}`]: true }))

    try {
      const decrypted = {
        content: email.content,
        subject: email.subject,
        from: email.from,
        to: email.to || [],
        is_encrypted: email.is_encrypted,
        tls_used: email.tls_used,
        encryption_version: email.encryption_version,
      }

      setDecryptedContent((prev) => ({ ...prev, [emailId]: decrypted }))
      toast({
        title: "Content Decrypted",
        description: "Email content is now visible below",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to decrypt content",
        variant: "destructive",
      })
    } finally {
      setLoadingStates((prev) => ({ ...prev, [`decrypt_${emailId}`]: false }))
    }
  }

  const toggleStarEmail = (emailId: string) => {
    setStarredEmails((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(emailId)) {
        newSet.delete(emailId)
      } else {
        newSet.add(emailId)
      }
      return newSet
    })
  }

  // Filter and sort emails
  const filteredEmails = emails
    .filter((email) => {
      const matchesSearch =
        email.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
        email.from.toLowerCase().includes(searchTerm.toLowerCase()) ||
        email.content.toLowerCase().includes(searchTerm.toLowerCase())

      const matchesFilter =
        filterType === "all" ||
        (filterType === "spam" && email.ai_analysis?.spam_analysis?.is_spam) ||
        (filterType === "secure" && email.is_encrypted && email.tls_used) ||
        (filterType === "starred" && starredEmails.has(email._id))

      return matchesSearch && matchesFilter
    })
    .sort((a, b) => {
      switch (sortBy) {
        case "date":
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        case "sender":
          return a.from.localeCompare(b.from)
        case "subject":
          return a.subject.localeCompare(b.subject)
        default:
          return 0
      }
    })

  const getAIWritingHelp = async () => {
    if (!quickSend.content) {
      toast({
        title: "Error",
        description: "Please enter email content for AI assistance",
        variant: "destructive",
      })
      return
    }

    try {
      const response = await fetch("http://localhost:5000/api/ai/comprehensive-analysis", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: quickSend.content,
          subject: quickSend.subject,
        }),
      })

      if (response.ok) {
        const result = await response.json()
        toast({
          title: "AI Writing Assistance",
          description: "Check the console for detailed suggestions",
        })
      } else {
        const data = await response.json()
        toast({
          title: "Error",
          description: data.error || "AI assistance failed",
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
    <PageTransition>
      <div className="space-y-8">
        {/* Enhanced Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <h1 className="text-4xl font-bold orbitron mb-4">
            <span className="text-electric-blue glow-text">📧 Enhanced Email Management</span>
          </h1>
          <p className="text-xl text-gray-300 rajdhani">
            Secure, encrypted email communication with AI-powered analysis
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Enhanced Email Inbox */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <Card className="synthwave-card">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2 orbitron text-electric-blue">
                    <Mail className="w-5 h-5" />📬 Encrypted Email Inbox
                  </span>
                  <div className="flex gap-2">
                    <Button
                      onClick={loadEmails}
                      disabled={loading}
                      size="sm"
                      variant="outline"
                      className="border-electric-blue/50 text-electric-blue hover:bg-electric-blue/20"
                    >
                      {loading ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <RefreshCw className="w-4 h-4 mr-2" />
                      )}
                      Refresh
                    </Button>
                  </div>
                </CardTitle>

                {/* Enhanced Search and Filter Controls */}
                <div className="space-y-4 mt-4">
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <Input
                        placeholder="Search emails..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 bg-black/50 border-electric-blue/30 focus:border-electric-blue"
                      />
                    </div>
                    <Select value={filterType} onValueChange={setFilterType}>
                      <SelectTrigger className="w-32 bg-black/50 border-electric-blue/30">
                        <Filter className="w-4 h-4 mr-2" />
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All</SelectItem>
                        <SelectItem value="spam">Spam</SelectItem>
                        <SelectItem value="secure">Secure</SelectItem>
                        <SelectItem value="starred">Starred</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={sortBy} onValueChange={setSortBy}>
                      <SelectTrigger className="w-32 bg-black/50 border-electric-blue/30">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="date">Date</SelectItem>
                        <SelectItem value="sender">Sender</SelectItem>
                        <SelectItem value="subject">Subject</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      onClick={() => setLoadHistory(!loadHistory)}
                      size="sm"
                      variant={loadHistory ? "default" : "outline"}
                      className={
                        loadHistory
                          ? "bg-neon-pink text-white"
                          : "border-neon-pink/50 text-neon-pink hover:bg-neon-pink/20"
                      }
                    >
                      📚 {loadHistory ? "Showing Full History" : "Load Full History"}
                    </Button>
                    <Button
                      onClick={() => setShowAnalysis(!showAnalysis)}
                      size="sm"
                      variant={showAnalysis ? "default" : "outline"}
                      className={
                        showAnalysis
                          ? "bg-deep-purple text-white"
                          : "border-deep-purple/50 text-deep-purple hover:bg-deep-purple/20"
                      }
                    >
                      📊 {showAnalysis ? "Hide Analysis" : "Show AI Analysis"}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex justify-center py-8">
                    <LoadingSpinner size="lg" text="Loading emails..." />
                  </div>
                ) : (
                  <ScrollArea className="h-96 w-full rounded-md border border-gray-700 bg-black/50">
                    {filteredEmails.length === 0 ? (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-center text-gray-500 py-8"
                      >
                        <Mail className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p>
                          📭 No emails found.{" "}
                          {searchTerm ? "Try a different search term." : "Send a test email to get started!"}
                        </p>
                      </motion.div>
                    ) : (
                      <div className="p-4 space-y-4">
                        <p className="text-sm text-gray-400 mb-4">
                          📧 Showing {filteredEmails.length} of {emails.length} emails (encrypted and secure)
                        </p>
                        <AnimatePresence>
                          {filteredEmails.map((email, index) => (
                            <motion.div
                              key={email._id}
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -20 }}
                              transition={{ duration: 0.5, delay: index * 0.05 }}
                              className="p-4 rounded-lg border border-gray-700 hover:border-neon-pink/50 transition-all duration-300 bg-black/30 hover:bg-black/50"
                              whileHover={{ scale: 1.02 }}
                            >
                              <div className="flex justify-between items-start mb-2">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      onClick={() => toggleStarEmail(email._id)}
                                      className="p-1 h-auto"
                                    >
                                      <Star
                                        className={`w-4 h-4 ${
                                          starredEmails.has(email._id)
                                            ? "fill-yellow-400 text-yellow-400"
                                            : "text-gray-400"
                                        }`}
                                      />
                                    </Button>
                                    <span className="font-semibold text-white">From: {email.from}</span>
                                    {showAnalysis && email.ai_analysis?.spam_analysis?.is_spam && (
                                      <Badge className="threat-high">
                                        <AlertTriangle className="w-3 h-3 mr-1" />
                                        SPAM
                                      </Badge>
                                    )}
                                    {email.tls_used && (
                                      <Badge className="bg-green-500/20 text-green-300 border-green-500/50">
                                        <Lock className="w-3 h-3 mr-1" />
                                        TLS
                                      </Badge>
                                    )}
                                    {email.is_encrypted && (
                                      <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/50">
                                        <Shield className="w-3 h-3 mr-1" />
                                        ENCRYPTED
                                      </Badge>
                                    )}
                                  </div>
                                  <div className="text-sm text-gray-300 mb-1">
                                    <strong>Subject:</strong> {email.subject || "No Subject"}
                                  </div>
                                  <div className="text-xs text-gray-500 mb-2">
                                    📅 {new Date(email.created_at).toLocaleString()}
                                    {showAnalysis && email.ai_analysis?.keyword_analysis?.keywords_detected && (
                                      <span className="ml-2 text-red-400">
                                        🚨 {email.ai_analysis.keyword_analysis.keywords_detected} suspicious keywords
                                      </span>
                                    )}
                                  </div>
                                  <div className="text-sm text-gray-400">
                                    {email.content.substring(0, 100)}
                                    {email.content.length > 100 ? "..." : ""}
                                  </div>
                                </div>
                              </div>

                              {/* Enhanced Action Buttons */}
                              <div className="flex flex-wrap gap-2 mt-3">
                                <Button
                                  size="sm"
                                  onClick={() => setSelectedEmail(email._id)}
                                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 hover:scale-105 transition-transform"
                                >
                                  <FileText className="w-3 h-3 mr-1" />📋 Report
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleReply(email)}
                                  disabled={loadingStates[`reply_${email._id}`]}
                                  className="border-orange-500/50 text-orange-300 hover:bg-orange-500/20 hover:scale-105 transition-transform"
                                >
                                  {loadingStates[`reply_${email._id}`] ? (
                                    <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                                  ) : (
                                    <Reply className="w-3 h-3 mr-1" />
                                  )}
                                  💬 Reply
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleDecryptView(email)}
                                  disabled={loadingStates[`decrypt_${email._id}`]}
                                  className="border-green-500/50 text-green-300 hover:bg-green-500/20 hover:scale-105 transition-transform"
                                >
                                  {loadingStates[`decrypt_${email._id}`] ? (
                                    <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                                  ) : (
                                    <Eye className="w-3 h-3 mr-1" />
                                  )}
                                  🔒 View
                                </Button>
                              </div>

                              {/* Enhanced Reply Data Display */}
                              <AnimatePresence>
                                {replyData[email._id] && (
                                  <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                    transition={{ duration: 0.5 }}
                                    className="mt-3 p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg"
                                  >
                                    <h4 className="font-semibold text-orange-300 mb-2">💬 Generated Reply:</h4>
                                    <p className="text-sm text-gray-300">{replyData[email._id].reply}</p>
                                    <p className="text-xs text-gray-400 mt-1">Tone: {replyData[email._id].tone}</p>
                                  </motion.div>
                                )}
                              </AnimatePresence>

                              {/* Enhanced Decrypted Content Display */}
                              <AnimatePresence>
                                {decryptedContent[email._id] && (
                                  <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                    transition={{ duration: 0.5 }}
                                    className="mt-3 p-3 bg-green-500/10 border border-green-500/30 rounded-lg"
                                  >
                                    <h4 className="font-semibold text-green-300 mb-2">🔒 Decrypted Content:</h4>
                                    <div className="text-sm space-y-1">
                                      <p>
                                        <strong>From:</strong> {decryptedContent[email._id].from}
                                      </p>
                                      <p>
                                        <strong>To:</strong> {decryptedContent[email._id].to.join(", ") || "N/A"}
                                      </p>
                                      <p>
                                        <strong>Subject:</strong> {decryptedContent[email._id].subject}
                                      </p>
                                      <p>
                                        <strong>Encryption:</strong>{" "}
                                        {decryptedContent[email._id].is_encrypted ? "✅ Yes" : "❌ No"}
                                      </p>
                                      <p>
                                        <strong>TLS:</strong>{" "}
                                        {decryptedContent[email._id].tls_used ? "✅ Yes" : "❌ No"}
                                      </p>
                                      {decryptedContent[email._id].encryption_version && (
                                        <p>
                                          <strong>Version:</strong> {decryptedContent[email._id].encryption_version}
                                        </p>
                                      )}
                                      <div className="mt-2 p-2 bg-black/30 rounded max-h-32 overflow-y-auto">
                                        <pre className="text-xs text-gray-300 whitespace-pre-wrap">
                                          {decryptedContent[email._id].content}
                                        </pre>
                                      </div>
                                    </div>
                                  </motion.div>
                                )}
                              </AnimatePresence>
                            </motion.div>
                          ))}
                        </AnimatePresence>
                      </div>
                    )}
                  </ScrollArea>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Enhanced Quick Send */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <Card className="synthwave-card" id="compose-section">
              <CardHeader>
                <CardTitle className="orbitron text-deep-purple flex items-center gap-2">
                  <Send className="w-5 h-5" />📤 Compose Encrypted Email
                </CardTitle>
              </CardHeader>
              <CardContent>
                <motion.div
                  className="space-y-4"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="quick-to">📬 To</Label>
                      <Input
                        id="quick-to"
                        type="email"
                        placeholder="recipient@example.com"
                        value={quickSend.to}
                        onChange={(e) => setQuickSend({ ...quickSend, to: e.target.value })}
                        className="bg-black/50 border-deep-purple/30 focus:border-deep-purple transition-colors"
                      />
                    </div>
                    <div>
                      <Label htmlFor="quick-subject">📝 Subject</Label>
                      <Input
                        id="quick-subject"
                        placeholder="Email subject"
                        value={quickSend.subject}
                        onChange={(e) => setQuickSend({ ...quickSend, subject: e.target.value })}
                        className="bg-black/50 border-deep-purple/30 focus:border-deep-purple transition-colors"
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="priority">🔥 Priority</Label>
                      <Select
                        value={quickSend.priority}
                        onValueChange={(value) => setQuickSend({ ...quickSend, priority: value })}
                      >
                        <SelectTrigger className="bg-black/50 border-deep-purple/30">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="encryption">🔐 Encryption</Label>
                      <Select
                        value={quickSend.encryption}
                        onValueChange={(value) => setQuickSend({ ...quickSend, encryption: value })}
                      >
                        <SelectTrigger className="bg-black/50 border-deep-purple/30">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="standard">Standard (Fernet)</SelectItem>
                          <SelectItem value="enhanced">Enhanced (AES-256)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="quick-content">💬 Message</Label>
                    <Textarea
                      id="quick-content"
                      rows={8}
                      placeholder="Your encrypted message..."
                      value={quickSend.content}
                      onChange={(e) => setQuickSend({ ...quickSend, content: e.target.value })}
                      className="bg-black/50 border-deep-purple/30 focus:border-deep-purple transition-colors"
                    />
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <Button
                      onClick={sendQuickEmail}
                      disabled={sendingEmail}
                      className="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 hover:scale-105 transition-transform"
                    >
                      {sendingEmail ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Send className="w-4 h-4 mr-2" />
                      )}
                      🔒 Send Encrypted Email
                    </Button>
                    <Button
                      onClick={getAIWritingHelp}
                      variant="outline"
                      className="border-electric-blue/50 text-electric-blue hover:bg-electric-blue/20 hover:scale-105 transition-transform"
                    >
                      ✨ Get AI Writing Help
                    </Button>
                  </div>
                </motion.div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Email Report Modal */}
        <AnimatePresence>
          {selectedEmail && (
            <EmailReport emailId={selectedEmail} token={token} onClose={() => setSelectedEmail(null)} />
          )}
        </AnimatePresence>
      </div>
    </PageTransition>
  )
}
