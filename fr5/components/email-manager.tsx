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
import { Mail, Shield, Lock, AlertTriangle, RefreshCw, Send, FileText, Reply, Eye, Loader2 } from "lucide-react"
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

export function EmailManager({ token, user }: EmailManagerProps) {
  const [emails, setEmails] = useState<Email[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedEmail, setSelectedEmail] = useState<string | null>(null)
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
      console.log("[EMAIL MANAGER] 📤 Sending email:", {
        from: user,
        to: quickSend.to,
        subject: quickSend.subject,
        priority: quickSend.priority,
      })

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
        console.log("[EMAIL MANAGER] ✅ Email sent successfully:", result)

        toast({
          title: "Success",
          description: `Email sent and encrypted successfully! ${result.keywords_detected ? `⚠️ ${result.keywords_detected} suspicious keywords detected` : ""}`,
        })

        setQuickSend({ to: "", subject: "", content: "", priority: "medium", encryption: "standard" })
        loadEmails()
      } else {
        const data = await response.json()
        console.error("[EMAIL MANAGER] ❌ Failed to send email:", data)
        toast({
          title: "Error",
          description: data.error || "Failed to send email",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("[EMAIL MANAGER] ❌ Connection error:", error)
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
      console.log(`[EMAIL MANAGER] 💬 Generating reply for email: ${emailId}`)

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
        console.log(`[EMAIL MANAGER] ✅ Reply generated:`, result)

        setReplyData((prev) => ({ ...prev, [emailId]: result }))

        // Also populate the compose form
        setQuickSend({
          to: email.from,
          subject: `Re: ${email.subject}`,
          content:
            result.reply ||
            `\n\n--- Original Message ---\nFrom: ${email.from}\nSubject: ${email.subject}\n\n${email.content}`,
          priority: "medium",
          encryption: "standard",
        })

        // Scroll to compose section
        document.getElementById("compose-section")?.scrollIntoView({ behavior: "smooth" })

        toast({
          title: "Reply Generated",
          description: "Smart reply generated and populated in compose form",
        })
      } else {
        const data = await response.json()
        console.error(`[EMAIL MANAGER] ❌ Failed to generate reply:`, data)
        toast({
          title: "Error",
          description: data.error || "Failed to generate reply",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error(`[EMAIL MANAGER] ❌ Reply generation error:`, error)
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
      console.log(`[EMAIL MANAGER] 🔒 Viewing decrypted content for email: ${emailId}`)

      // Email content is already decrypted when fetched from API
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

      console.log(`[EMAIL MANAGER] ✅ Decrypted content available:`, {
        from: decrypted.from,
        subject: decrypted.subject,
        contentLength: decrypted.content.length,
        encrypted: decrypted.is_encrypted,
        tls: decrypted.tls_used,
      })

      toast({
        title: "Content Decrypted",
        description: "Email content is now visible below",
      })
    } catch (error) {
      console.error(`[EMAIL MANAGER] ❌ Decrypt error:`, error)
      toast({
        title: "Error",
        description: "Failed to decrypt content",
        variant: "destructive",
      })
    } finally {
      setLoadingStates((prev) => ({ ...prev, [`decrypt_${emailId}`]: false }))
    }
  }

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
        console.log("[EMAIL MANAGER] ✨ AI writing assistance:", result)

        // Show AI suggestions in a toast or modal
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
    <>
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Email Inbox */}
        <Card className="synthwave-card">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2 orbitron text-electric-blue">
                <Mail className="w-5 h-5" />📬 Your Encrypted Email Inbox
              </span>
              <div className="flex gap-2">
                <Button
                  onClick={loadEmails}
                  disabled={loading}
                  size="sm"
                  variant="outline"
                  className="border-electric-blue/50 text-electric-blue hover:bg-electric-blue/20"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                  Refresh
                </Button>
              </div>
            </CardTitle>
            <div className="flex gap-2 mt-2">
              <Button
                onClick={() => setLoadHistory(!loadHistory)}
                size="sm"
                variant={loadHistory ? "default" : "outline"}
                className={
                  loadHistory ? "bg-neon-pink text-white" : "border-neon-pink/50 text-neon-pink hover:bg-neon-pink/20"
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
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-96 w-full rounded-md border border-gray-700 bg-black/50">
              {emails.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <Mail className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>📭 No emails found. Send a test email to get started!</p>
                </div>
              ) : (
                <div className="p-4 space-y-4">
                  <p className="text-sm text-gray-400 mb-4">📧 Showing {emails.length} emails (encrypted and secure)</p>
                  {emails.map((email, index) => (
                    <div
                      key={email._id}
                      className="p-4 rounded-lg border border-gray-700 hover:border-neon-pink/50 transition-colors bg-black/30"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2 flex-wrap">
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

                      {/* Action Buttons */}
                      <div className="flex flex-wrap gap-2 mt-3">
                        <Button
                          size="sm"
                          onClick={() => setSelectedEmail(email._id)}
                          className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                        >
                          <FileText className="w-3 h-3 mr-1" />📋 Report
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleReply(email)}
                          disabled={loadingStates[`reply_${email._id}`]}
                          className="border-orange-500/50 text-orange-300 hover:bg-orange-500/20"
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
                          className="border-green-500/50 text-green-300 hover:bg-green-500/20"
                        >
                          {loadingStates[`decrypt_${email._id}`] ? (
                            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                          ) : (
                            <Eye className="w-3 h-3 mr-1" />
                          )}
                          🔒 View
                        </Button>
                      </div>

                      {/* Display Reply Data */}
                      {replyData[email._id] && (
                        <div className="mt-3 p-3 bg-orange-500/10 border border-orange-500/30 rounded">
                          <h4 className="font-semibold text-orange-300 mb-2">💬 Generated Reply:</h4>
                          <p className="text-sm text-gray-300">{replyData[email._id].reply}</p>
                          <p className="text-xs text-gray-400 mt-1">Tone: {replyData[email._id].tone}</p>
                        </div>
                      )}

                      {/* Display Decrypted Content */}
                      {decryptedContent[email._id] && (
                        <div className="mt-3 p-3 bg-green-500/10 border border-green-500/30 rounded">
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
                              <strong>TLS:</strong> {decryptedContent[email._id].tls_used ? "✅ Yes" : "❌ No"}
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
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Enhanced Quick Send */}
        <Card className="synthwave-card" id="compose-section">
          <CardHeader>
            <CardTitle className="orbitron text-deep-purple flex items-center gap-2">
              <Send className="w-5 h-5" />📤 Send Encrypted Email
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="quick-to">📬 To</Label>
                  <Input
                    id="quick-to"
                    type="email"
                    placeholder="recipient@example.com"
                    value={quickSend.to}
                    onChange={(e) => setQuickSend({ ...quickSend, to: e.target.value })}
                    className="bg-black/50 border-deep-purple/30 focus:border-deep-purple"
                  />
                </div>
                <div>
                  <Label htmlFor="quick-subject">📝 Subject</Label>
                  <Input
                    id="quick-subject"
                    placeholder="Email subject"
                    value={quickSend.subject}
                    onChange={(e) => setQuickSend({ ...quickSend, subject: e.target.value })}
                    className="bg-black/50 border-deep-purple/30 focus:border-deep-purple"
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
                  className="bg-black/50 border-deep-purple/30 focus:border-deep-purple"
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <Button
                  onClick={sendQuickEmail}
                  disabled={sendingEmail}
                  className="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700"
                >
                  {sendingEmail ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
                  🔒 Send Encrypted Email
                </Button>
                <Button
                  onClick={getAIWritingHelp}
                  variant="outline"
                  className="border-electric-blue/50 text-electric-blue hover:bg-electric-blue/20"
                >
                  ✨ Get AI Writing Help
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Email Report Modal */}
      {selectedEmail && <EmailReport emailId={selectedEmail} token={token} onClose={() => setSelectedEmail(null)} />}
    </>
  )
}
