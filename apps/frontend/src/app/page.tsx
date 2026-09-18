"use client"

import { useState, useEffect } from "react"
import { ChatInterface } from "@/components/ChatInterface"
import { LearningPlanSidebar, Checkpoint } from "@/components/LearningPlanSidebar"
import { MasteryDashboard } from "@/components/MasteryDashboard"
import { GraduationCap } from "lucide-react"

export default function Home() {
  const [sessionId] = useState<string>("session-default")
  const [userId] = useState<string>("user-default")
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([])
  const [currentCheckpointId, setCurrentCheckpointId] = useState<string | null>(null)

  // Fetch initial session state
  useEffect(() => {
    async function fetchSession() {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"
        const response = await fetch(`${baseUrl}/session/${sessionId}`)
        if (response.ok) {
          const data = await response.json()
          if (data.learning_plan && data.learning_plan.checkpoints) {
            setCheckpoints(data.learning_plan.checkpoints)
            setCurrentCheckpointId(data.current_checkpoint_id)
          }
        }
      } catch (e) {
        console.error("Failed to fetch session", e)
      }
    }
    fetchSession()
  }, [sessionId])

  const handleCheckpointChange = (checkpoint: Checkpoint) => {
    if (!checkpoint) return
    
    setCheckpoints(prev => {
      const exists = prev.find(p => p.id === checkpoint.id)
      if (exists) {
        return prev.map(p => p.id === checkpoint.id ? checkpoint : p)
      }
      return [...prev, checkpoint]
    })
    
    if (checkpoint.status === "pending") {
      setCurrentCheckpointId(checkpoint.id)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-slate-50">
      <header className="flex items-center px-6 py-4 bg-white border-b shadow-sm shrink-0">
        <div className="flex items-center space-x-2 text-indigo-600">
          <GraduationCap className="w-8 h-8" />
          <h1 className="text-xl font-bold">MentorAI</h1>
        </div>
        <div className="ml-auto flex items-center space-x-4">
          <div className="text-sm font-medium text-gray-500">Student: {userId}</div>
        </div>
      </header>

      <main className="flex-1 overflow-hidden p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full max-w-7xl mx-auto">
          {/* Left Column - Dashboards */}
          <div className="lg:col-span-1 flex flex-col space-y-6 overflow-hidden">
            <div className="flex-1 min-h-[300px]">
              <LearningPlanSidebar 
                checkpoints={checkpoints} 
                currentCheckpointId={currentCheckpointId} 
              />
            </div>
            <div className="flex-1 min-h-[300px]">
              <MasteryDashboard userId={userId} />
            </div>
          </div>

          {/* Right Column - Chat */}
          <div className="lg:col-span-3 h-full">
            <ChatInterface 
              sessionId={sessionId} 
              userId={userId} 
              onCheckpointChange={handleCheckpointChange} 
            />
          </div>
        </div>
      </main>
    </div>
  )
}
