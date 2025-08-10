"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Bot, 
  Brain, 
  MessageCircle, 
  Sparkles, 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw,
  Send,
  Loader2
} from "lucide-react"
import DashboardLayout from "@/components/dashboard-layout"
import { MarkdownRenderer } from "@/components/markdown-renderer"

interface LLMStatus {
  available: boolean
  provider: string
  model: string
  features: string[]
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface ThreatExplanation {
  alert_id: string
  explanation: {
    summary: string
    details: string
    risk_level: string
    impact: string
    recommendations: string
  }
  generated_at: string
  model: string
}

export default function AIPage() {
  const [llmStatus, setLlmStatus] = useState<LLMStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [currentMessage, setCurrentMessage] = useState("")
  const [isChatLoading, setIsChatLoading] = useState(false)
  
  // Threat explanation state
  const [alertId, setAlertId] = useState("")
  const [threatExplanation, setThreatExplanation] = useState<ThreatExplanation | null>(null)
  const [isExplaining, setIsExplaining] = useState(false)

  useEffect(() => {
    fetchLLMStatus()
  }, [])

  const fetchLLMStatus = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch('/api/v1/llm/status')
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      setLlmStatus(data)
    } catch (err) {
      console.error('Failed to fetch LLM status:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch LLM status')
    } finally {
      setIsLoading(false)
    }
  }

  const sendChatMessage = async () => {
    if (!currentMessage.trim() || isChatLoading) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: currentMessage,
      timestamp: new Date().toISOString()
    }

    setChatMessages(prev => [...prev, userMessage])
    setCurrentMessage("")
    setIsChatLoading(true)

    try {
      const response = await fetch('/api/v1/llm/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentMessage,
          context: {}
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString()
      }

      setChatMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      console.error('Failed to send message:', err)
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString()
      }
      setChatMessages(prev => [...prev, errorMessage])
    } finally {
      setIsChatLoading(false)
    }
  }

  const explainThreat = async () => {
    if (!alertId.trim() || isExplaining) return

    setIsExplaining(true)
    setThreatExplanation(null)

    try {
      const response = await fetch(`/api/v1/llm/explain-threat/${alertId}`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      setThreatExplanation(data)
    } catch (err) {
      console.error('Failed to explain threat:', err)
      // Handle error - could show error message
    } finally {
      setIsExplaining(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendChatMessage()
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">AI Security Assistant</h1>
            <p className="text-muted-foreground mt-2">
              AI-powered threat analysis and conversational security insights
            </p>
          </div>
          <Button 
            onClick={fetchLLMStatus}
            disabled={isLoading}
            variant="outline"
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* LLM Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              LLM Service Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Checking LLM service...</span>
              </div>
            ) : llmStatus ? (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  {llmStatus.available ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertTriangle className="h-5 w-5 text-red-500" />
                  )}
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">
                        {llmStatus.available ? 'Available' : 'Unavailable'}
                      </span>
                      {llmStatus.available && (
                        <Badge variant="secondary">
                          {llmStatus.provider}
                        </Badge>
                      )}
                    </div>
                    {llmStatus.available && (
                      <div className="text-sm text-muted-foreground">
                        Model: {llmStatus.model}
                      </div>
                    )}
                  </div>
                </div>
                
                {llmStatus.available && llmStatus.features.length > 0 && (
                  <div className="flex gap-2">
                    {llmStatus.features.map((feature) => (
                      <Badge key={feature} variant="outline" className="text-xs">
                        {feature === 'threat_explanation' && <Sparkles className="mr-1 h-3 w-3" />}
                        {feature === 'chat_interface' && <MessageCircle className="mr-1 h-3 w-3" />}
                        {feature.replace('_', ' ')}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-muted-foreground">
                Unable to connect to LLM service
              </div>
            )}
          </CardContent>
        </Card>

        {/* Main Content */}
        {llmStatus?.available ? (
          <Tabs defaultValue="chat" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="chat" className="flex items-center gap-2">
                <MessageCircle className="h-4 w-4" />
                Security Chat
              </TabsTrigger>
              <TabsTrigger value="threats" className="flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                Threat Explanations
              </TabsTrigger>
            </TabsList>

            <TabsContent value="chat" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5" />
                    AI Security Assistant
                  </CardTitle>
                  <CardDescription>
                    Ask questions about your security data, threats, and monitoring insights
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Chat Messages */}
                  <div className="h-64 overflow-y-auto border rounded-md p-4 space-y-3">
                    {chatMessages.length === 0 ? (
                      <div className="text-center text-muted-foreground">
                        <Bot className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>Start a conversation about your security data</p>
                        <p className="text-sm mt-1">
                          Try asking: &quot;What are the latest threats?&quot; or &quot;Explain my security alerts&quot;
                        </p>
                      </div>
                    ) : (
                      chatMessages.map((message, index) => (
                        <div
                          key={index}
                          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-[80%] p-3 rounded-lg ${
                              message.role === 'user'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted'
                            }`}
                          >
                            {message.role === 'assistant' ? (
                              <MarkdownRenderer 
                                content={message.content}
                                className="text-sm"
                              />
                            ) : (
                              <p className="text-sm">{message.content}</p>
                            )}
                            <p className="text-xs opacity-70 mt-1">
                              {new Date(message.timestamp).toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                    {isChatLoading && (
                      <div className="flex justify-start">
                        <div className="bg-muted p-3 rounded-lg">
                          <Loader2 className="h-4 w-4 animate-spin" />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Chat Input */}
                  <div className="flex gap-2">
                    <Textarea
                      placeholder="Ask about security threats, user behavior, or monitoring insights..."
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="min-h-[50px]"
                      disabled={isChatLoading}
                    />
                    <Button 
                      onClick={sendChatMessage}
                      disabled={!currentMessage.trim() || isChatLoading}
                      size="lg"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="threats" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Threat Explanation
                  </CardTitle>
                  <CardDescription>
                    Get business-friendly explanations for security alerts
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Enter Alert ID (e.g., alert:123456)"
                      value={alertId}
                      onChange={(e) => setAlertId(e.target.value)}
                      disabled={isExplaining}
                    />
                    <Button 
                      onClick={explainThreat}
                      disabled={!alertId.trim() || isExplaining}
                    >
                      {isExplaining ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <Sparkles className="mr-2 h-4 w-4" />
                      )}
                      Explain
                    </Button>
                  </div>

                  {threatExplanation && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">
                          Alert Analysis: {threatExplanation.alert_id}
                        </CardTitle>
                        <CardDescription>
                          Generated by {threatExplanation.model} on{' '}
                          {new Date(threatExplanation.generated_at).toLocaleString()}
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <h4 className="font-semibold mb-2">Summary</h4>
                          <MarkdownRenderer 
                            content={threatExplanation.explanation.summary}
                            className="text-sm text-muted-foreground"
                          />
                        </div>
                        
                        <div>
                          <h4 className="font-semibold mb-2 flex items-center gap-2">
                            Risk Level
                            <Badge variant={
                              threatExplanation.explanation.risk_level === 'high' ? 'destructive' :
                              threatExplanation.explanation.risk_level === 'medium' ? 'default' : 'secondary'
                            }>
                              {threatExplanation.explanation.risk_level}
                            </Badge>
                          </h4>
                        </div>

                        <div>
                          <h4 className="font-semibold mb-2">Business Impact</h4>
                          <MarkdownRenderer 
                            content={threatExplanation.explanation.impact}
                            className="text-sm text-muted-foreground"
                          />
                        </div>

                        <div>
                          <h4 className="font-semibold mb-2">Recommendations</h4>
                          <MarkdownRenderer 
                            content={threatExplanation.explanation.recommendations}
                            className="text-sm text-muted-foreground"
                          />
                        </div>

                        <div>
                          <h4 className="font-semibold mb-2">Technical Details</h4>
                          <MarkdownRenderer 
                            content={threatExplanation.explanation.details}
                            className="text-sm text-muted-foreground"
                          />
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        ) : (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center space-y-3">
                <AlertTriangle className="h-12 w-12 mx-auto text-muted-foreground" />
                <h3 className="font-medium">LLM Service Unavailable</h3>
                <p className="text-sm text-muted-foreground">
                  The AI-powered features require an active LLM service connection. 
                  Please check your configuration and ensure the API key is properly set.
                </p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={fetchLLMStatus}
                  className="mt-3"
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Retry Connection
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}
