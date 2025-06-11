"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { Brain, Zap, MessageSquare, FileText } from "lucide-react"

interface AIAnalysisToolsProps {
  token: string
}

export function AIAnalysisTools({ token }: AIAnalysisToolsProps) {
  const [analysisContent, setAnalysisContent] = useState("")
  const [analysisSubject, setAnalysisSubject] = useState("")
  const [analysisSender, setAnalysisSender] = useState("")
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const [compositionContent, setCompositionContent] = useState("")
  const [compositionTone, setCompositionTone] = useState("professional")
  const [compositionResult, setCompositionResult] = useState<any>(null)
  const [compositionLoading, setCompositionLoading] = useState(false)

  const [replyContent, setReplyContent] = useState("")
  const [replyTone, setReplyTone] = useState("professional")
  const [replyResult, setReplyResult] = useState<any>(null)
  const [replyLoading, setReplyLoading] = useState(false)

  const { toast } = useToast()

  const runComprehensiveAnalysis = async () => {
    if (!analysisContent) {
      toast({
        title: "Error",
        description: "Please enter content to analyze",
        variant: "destructive",
      })
      return
    }

    setLoading(true)
    try {
      const response = await fetch("http://localhost:5000/api/ai/comprehensive-analysis", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: analysisContent,
          subject: analysisSubject,
          sender: analysisSender,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setAnalysisResult(data)
        toast({
          title: "Success",
          description: "AI analysis completed successfully",
        })
      } else {
        const data = await response.json()
        toast({
          title: "Error",
          description: data.error || "Analysis failed",
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

  const getCompositionHelp = async () => {
    if (!compositionContent) {
      toast({
        title: "Error",
        description: "Please enter content for composition help",
        variant: "destructive",
      })
      return
    }

    setCompositionLoading(true)
    try {
      const response = await fetch("http://localhost:5000/api/ai/composition-help", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: compositionContent,
          tone: compositionTone,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setCompositionResult(data)
        toast({
          title: "Success",
          description: "Composition assistance provided",
        })
      } else {
        const data = await response.json()
        toast({
          title: "Error",
          description: data.error || "Composition help failed",
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
      setCompositionLoading(false)
    }
  }

  const generateReply = async () => {
    if (!replyContent) {
      toast({
        title: "Error",
        description: "Please enter original email content",
        variant: "destructive",
      })
      return
    }

    setReplyLoading(true)
    try {
      const response = await fetch("http://localhost:5000/api/ai/generate-reply", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          original_email: replyContent,
          tone: replyTone,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setReplyResult(data)
        toast({
          title: "Success",
          description: "Smart reply generated",
        })
      } else {
        const data = await response.json()
        toast({
          title: "Error",
          description: data.error || "Reply generation failed",
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
      setReplyLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Comprehensive Analysis */}
      <Card className="synthwave-card">
        <CardHeader>
          <CardTitle className="orbitron text-neon-pink flex items-center gap-2">
            <Brain className="w-5 h-5" />🤖 Comprehensive AI Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="analysis-sender">Sender (Optional)</Label>
              <input
                id="analysis-sender"
                type="email"
                placeholder="sender@example.com"
                value={analysisSender}
                onChange={(e) => setAnalysisSender(e.target.value)}
                className="w-full px-3 py-2 bg-black/50 border border-neon-pink/30 rounded-md text-white placeholder-gray-400 focus:border-neon-pink focus:outline-none"
              />
            </div>
            <div>
              <Label htmlFor="analysis-subject">Subject (Optional)</Label>
              <input
                id="analysis-subject"
                placeholder="Email subject"
                value={analysisSubject}
                onChange={(e) => setAnalysisSubject(e.target.value)}
                className="w-full px-3 py-2 bg-black/50 border border-neon-pink/30 rounded-md text-white placeholder-gray-400 focus:border-neon-pink focus:outline-none"
              />
            </div>
          </div>
          <div>
            <Label htmlFor="analysis-content">Email Content</Label>
            <Textarea
              id="analysis-content"
              rows={6}
              placeholder="Paste email content here for comprehensive AI analysis..."
              value={analysisContent}
              onChange={(e) => setAnalysisContent(e.target.value)}
              className="bg-black/50 border-neon-pink/30 focus:border-neon-pink"
            />
          </div>
          <Button
            onClick={runComprehensiveAnalysis}
            disabled={loading}
            className="w-full bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700"
          >
            {loading ? (
              <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
            ) : (
              <Zap className="w-4 h-4 mr-2" />
            )}
            Run Comprehensive Analysis
          </Button>

          {analysisResult && (
            <div className="mt-6 p-4 bg-black/30 border border-gray-700 rounded-lg">
              <h4 className="font-semibold text-electric-blue mb-3">Analysis Results:</h4>
              <div className="space-y-3 text-sm">
                {analysisResult.spam_analysis && (
                  <div>
                    <strong className="text-neon-pink">Spam Analysis:</strong>
                    <p>Is Spam: {analysisResult.spam_analysis.is_spam ? "Yes" : "No"}</p>
                    <p>Confidence: {(analysisResult.spam_analysis.confidence * 100).toFixed(1)}%</p>
                    <p>Threat Level: {analysisResult.spam_analysis.threat_level}</p>
                  </div>
                )}
                {analysisResult.keyword_analysis && (
                  <div>
                    <strong className="text-electric-blue">Keyword Analysis:</strong>
                    <p>Keywords Detected: {analysisResult.keyword_analysis.keywords_detected}</p>
                    <p>Risk Level: {analysisResult.keyword_analysis.risk_level}</p>
                  </div>
                )}
                {analysisResult.security_analysis && (
                  <div>
                    <strong className="text-yellow-400">Security Analysis:</strong>
                    <p>Phishing Risk: {analysisResult.security_analysis.is_phishing ? "High" : "Low"}</p>
                    <p>Risk Level: {analysisResult.security_analysis.risk_level}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Composition Help */}
      <Card className="synthwave-card">
        <CardHeader>
          <CardTitle className="orbitron text-electric-blue flex items-center gap-2">
            <FileText className="w-5 h-5" />
            ✍️ AI Composition Help
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="composition-content">Draft Content</Label>
              <Textarea
                id="composition-content"
                rows={6}
                placeholder="Enter your draft email content for AI suggestions..."
                value={compositionContent}
                onChange={(e) => setCompositionContent(e.target.value)}
                className="bg-black/50 border-electric-blue/30 focus:border-electric-blue"
              />
            </div>
            <div className="space-y-4">
              <div>
                <Label htmlFor="composition-tone">Desired Tone</Label>
                <Select value={compositionTone} onValueChange={setCompositionTone}>
                  <SelectTrigger className="bg-black/50 border-electric-blue/30">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="professional">Professional</SelectItem>
                    <SelectItem value="friendly">Friendly</SelectItem>
                    <SelectItem value="formal">Formal</SelectItem>
                    <SelectItem value="casual">Casual</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={getCompositionHelp}
                disabled={compositionLoading}
                className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700"
              >
                {compositionLoading ? (
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                ) : (
                  <FileText className="w-4 h-4 mr-2" />
                )}
                Get AI Suggestions
              </Button>
            </div>
          </div>

          {compositionResult && (
            <div className="mt-6 p-4 bg-black/30 border border-gray-700 rounded-lg">
              <h4 className="font-semibold text-electric-blue mb-3">AI Suggestions:</h4>
              <div className="space-y-3 text-sm">
                {compositionResult.suggestions && (
                  <div>
                    <strong className="text-neon-pink">Suggestions:</strong>
                    <p className="text-gray-300">{compositionResult.suggestions}</p>
                  </div>
                )}
                {compositionResult.tone_analysis && (
                  <div>
                    <strong className="text-electric-blue">Tone Analysis:</strong>
                    <p>Current Tone: {compositionResult.tone_analysis.current_tone}</p>
                    <p>Sentiment: {compositionResult.tone_analysis.sentiment}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Smart Reply Generator */}
      <Card className="synthwave-card">
        <CardHeader>
          <CardTitle className="orbitron text-deep-purple flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />💬 Smart Reply Generator
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="reply-content">Original Email</Label>
              <Textarea
                id="reply-content"
                rows={6}
                placeholder="Paste the original email content here..."
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                className="bg-black/50 border-deep-purple/30 focus:border-deep-purple"
              />
            </div>
            <div className="space-y-4">
              <div>
                <Label htmlFor="reply-tone">Reply Tone</Label>
                <Select value={replyTone} onValueChange={setReplyTone}>
                  <SelectTrigger className="bg-black/50 border-deep-purple/30">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="professional">Professional</SelectItem>
                    <SelectItem value="friendly">Friendly</SelectItem>
                    <SelectItem value="formal">Formal</SelectItem>
                    <SelectItem value="casual">Casual</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={generateReply}
                disabled={replyLoading}
                className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700"
              >
                {replyLoading ? (
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                ) : (
                  <MessageSquare className="w-4 h-4 mr-2" />
                )}
                Generate Smart Reply
              </Button>
            </div>
          </div>

          {replyResult && (
            <div className="mt-6 p-4 bg-black/30 border border-gray-700 rounded-lg">
              <h4 className="font-semibold text-deep-purple mb-3">Generated Reply:</h4>
              <div className="space-y-3 text-sm">
                {replyResult.reply && (
                  <div className="p-3 bg-white/5 border border-gray-600 rounded">
                    <p className="text-gray-300 whitespace-pre-wrap">{replyResult.reply}</p>
                  </div>
                )}
                {replyResult.tone && (
                  <p>
                    <strong className="text-deep-purple">Tone Used:</strong> {replyResult.tone}
                  </p>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
