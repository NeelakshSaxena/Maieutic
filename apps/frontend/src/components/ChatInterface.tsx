"use client"

import { useState, useRef, useEffect } from "react"
import { Checkpoint } from "@/components/LearningPlanSidebar"
import { Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

export interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
}

export function ChatInterface({ 
  sessionId, 
  userId,
  onCheckpointChange
}: { 
  sessionId: string,
  userId: string,
  onCheckpointChange: (checkpoint: Checkpoint) => void
}) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! What would you like to learn today?"
    }
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return
    
    const userMessage: Message = { id: Date.now().toString(), role: "user", content: input }
    setMessages(prev => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "/api"
      const response = await fetch(`${baseUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          message: userMessage.content
        })
      })

      if (!response.ok) {
        let errorMsg = "Error: Failed to communicate with the learning agent.";
        try {
          const errorData = await response.json();
          if (errorData && errorData.detail) {
            errorMsg = `Error: ${errorData.detail}`;
          }
        } catch (e) {
          // Fallback to generic if not JSON
        }
        throw new Error(errorMsg);
      }
      
      const data = await response.json()
      
      // Update UI with response
      if (data.message) {
        setMessages(prev => [...prev, {
          id: Date.now().toString() + "_resp",
          role: "assistant",
          content: data.message
        }])
      }

      // Propagate checkpoint changes if any
      if (data.next_checkpoint) {
        onCheckpointChange(data.next_checkpoint)
      }

    } catch (error: any) {
      console.error(error)
      setMessages(prev => [...prev, {
        id: Date.now().toString() + "_err",
        role: "system",
        content: error.message || "Error: Failed to communicate with the learning agent."
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-white border rounded-xl overflow-hidden shadow-sm">
      <div className="p-4 border-b bg-gray-50/50">
        <h2 className="font-semibold text-gray-800">Learning Session</h2>
        <p className="text-sm text-gray-500">Session ID: {sessionId}</p>
      </div>

      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="flex flex-col space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`flex max-w-[80%] items-end space-x-2 ${msg.role === "user" ? "flex-row-reverse space-x-reverse" : ""}`}>
                <Avatar className="w-8 h-8">
                  {msg.role === "user" ? (
                    <AvatarFallback className="bg-blue-100 text-blue-600">U</AvatarFallback>
                  ) : msg.role === "system" ? (
                    <AvatarFallback className="bg-red-100 text-red-600">!</AvatarFallback>
                  ) : (
                    <AvatarFallback className="bg-green-100 text-green-600">AI</AvatarFallback>
                  )}
                </Avatar>
                
                <div className={`p-3 rounded-2xl ${
                  msg.role === "user" 
                    ? "bg-blue-600 text-white rounded-br-sm" 
                    : msg.role === "system"
                    ? "bg-red-50 text-red-600 border border-red-200 rounded-bl-sm"
                    : "bg-gray-100 text-gray-800 rounded-bl-sm"
                }`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-end space-x-2">
                <Avatar className="w-8 h-8">
                  <AvatarFallback className="bg-green-100 text-green-600">AI</AvatarFallback>
                </Avatar>
                <div className="p-3 rounded-2xl bg-gray-100 text-gray-800 rounded-bl-sm">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="p-4 bg-white border-t">
        <form 
          className="flex space-x-2" 
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
        >
          <Input 
            value={input} 
            onChange={(e) => setInput(e.target.value)} 
            placeholder="Type your response or question..." 
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}
