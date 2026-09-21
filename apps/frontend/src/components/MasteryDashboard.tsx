"use client"

import { useEffect, useState } from "react"
import { Progress } from "@/components/ui/progress"

interface MasteryData {
  concept_id: string
  historical_mastery: number
  attempts: number
  misconceptions_observed: string[]
}

export function MasteryDashboard({ userId }: { userId: string }) {
  const [masteryData, setMasteryData] = useState<MasteryData[]>([])

  useEffect(() => {
    async function fetchData() {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || "/api"
        const response = await fetch(`${baseUrl}/brain/${userId}`)
        if (response.ok) {
          const data = await response.json()
          setMasteryData(data.mastery_states || [])
        }
      } catch (err) {
        console.error("Failed to fetch mastery data", err)
      }
    }
    fetchData()
    const intervalId = setInterval(fetchData, 10000)
    return () => clearInterval(intervalId)
  }, [userId])

  return (
    <div className="flex flex-col bg-white border rounded-xl shadow-sm h-full overflow-hidden">
      <div className="p-4 border-b bg-gray-50/50">
        <h2 className="font-semibold text-gray-800">Concept Mastery</h2>
        <p className="text-sm text-gray-500">Your understanding of topics over time</p>
      </div>
      
      <div className="p-4 flex-1 overflow-y-auto space-y-4">
        {masteryData.length === 0 ? (
          <div className="flex items-center justify-center h-full text-sm text-gray-400">
            No mastery data available yet. Keep learning!
          </div>
        ) : (
          masteryData.map((concept) => (
            <div key={concept.concept_id} className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="font-medium text-gray-700 capitalize">{concept.concept_id.replace(/_/g, " ")}</span>
                <span className="text-gray-500">{Math.round(concept.historical_mastery * 100)}%</span>
              </div>
              <Progress value={concept.historical_mastery * 100} className="h-2" />
              <div className="text-xs text-gray-500 flex justify-between">
                <span>Attempts: {concept.attempts}</span>
                {concept.misconceptions_observed.length > 0 && (
                  <span className="text-red-500 truncate ml-2">
                    Mistakes: {concept.misconceptions_observed.join(", ")}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
