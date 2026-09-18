import { CheckCircle2, Circle } from "lucide-react"

export interface Checkpoint {
  id: string
  task: string
  status: "pending" | "passed" | "failed"
}

export function LearningPlanSidebar({ 
  checkpoints = [], 
  currentCheckpointId 
}: { 
  checkpoints?: Checkpoint[]
  currentCheckpointId?: string | null 
}) {
  return (
    <div className="flex flex-col h-full bg-white border rounded-xl overflow-hidden shadow-sm">
      <div className="p-4 border-b bg-gray-50/50">
        <h2 className="font-semibold text-gray-800">Learning Plan</h2>
        <p className="text-sm text-gray-500">Your path to mastery</p>
      </div>
      
      <div className="p-4 flex-1 overflow-y-auto">
        {checkpoints.length === 0 ? (
          <div className="flex items-center justify-center h-full text-sm text-gray-400">
            No plan generated yet. Tell the agent what you want to learn!
          </div>
        ) : (
          <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-200 before:to-transparent">
            {checkpoints.map((cp, idx) => {
              const isCurrent = cp.id === currentCheckpointId
              const isPassed = cp.status === "passed"
              
              return (
                <div key={cp.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                  {/* Marker */}
                  <div className={`flex items-center justify-center w-6 h-6 rounded-full border-2 bg-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 ${
                    isPassed ? "border-green-500 text-green-500" : isCurrent ? "border-blue-500 text-blue-500" : "border-gray-300 text-gray-300"
                  }`}>
                    {isPassed ? <CheckCircle2 className="w-4 h-4" /> : <Circle className="w-4 h-4" />}
                  </div>
                  
                  {/* Card */}
                  <div className={`w-[calc(100%-2.5rem)] md:w-[calc(50%-1.5rem)] p-3 rounded-lg border shadow-sm ${
                    isCurrent ? "bg-blue-50 border-blue-200" : "bg-white border-gray-200"
                  }`}>
                    <div className="flex items-center justify-between space-x-2 mb-1">
                      <div className={`font-medium text-sm ${isCurrent ? "text-blue-800" : "text-gray-800"}`}>
                        Step {idx + 1}
                      </div>
                      <div className={`text-xs px-2 py-0.5 rounded-full ${
                        isPassed ? "bg-green-100 text-green-700" : isCurrent ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600"
                      }`}>
                        {cp.status}
                      </div>
                    </div>
                    <div className="text-sm text-gray-600">{cp.task}</div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
