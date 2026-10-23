"use client"

import { CircleAlertIcon } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ConceptPanel } from "@/components/ConceptPanel"
import { LearningJourney } from "@/components/LearningJourney"
import { MasteryPanel } from "@/components/MasteryPanel"
import type { LearningSessionApi } from "@/hooks/use-learning-session"

/** Learning context: journey, current concept and mastery. Used in the desktop column and the mobile sheet. */
export function LearningSidebar({ api }: { api: LearningSessionApi }) {
  const { progress, session, mastery, masteryError, messages, syncError } = api
  const pct = progress.total ? Math.round((progress.completed / progress.total) * 100) : 0

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex flex-col gap-2 border-b px-4 py-3">
        <div className="flex items-baseline justify-between gap-2">
          <h2 className="text-sm font-semibold">Your progress</h2>
          <span className="text-xs text-muted-foreground tabular-nums">
            {progress.total ? `${progress.completed} of ${progress.total} checkpoints verified` : "No plan yet"}
          </span>
        </div>
        <Progress
          value={pct}
          aria-label={
            progress.total
              ? `Plan progress: ${progress.completed} of ${progress.total} checkpoints verified`
              : "Plan progress: no plan yet"
          }
          className="gap-0 [&_[data-slot=progress-track]]:h-2"
        />
        {syncError && (
          <Alert variant="destructive" className="mt-1">
            <CircleAlertIcon aria-hidden="true" />
            <AlertDescription>{syncError}</AlertDescription>
          </Alert>
        )}
      </div>

      <Tabs defaultValue="journey" className="min-h-0 flex-1 gap-0">
        <div className="border-b px-4 py-2">
          <TabsList className="w-full">
            <TabsTrigger value="journey">Journey</TabsTrigger>
            <TabsTrigger value="concept">Concept</TabsTrigger>
            <TabsTrigger value="mastery">Mastery</TabsTrigger>
          </TabsList>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4">
          <TabsContent value="journey">
            <LearningJourney progress={progress} />
          </TabsContent>
          <TabsContent value="concept">
            <ConceptPanel progress={progress} plan={session?.learning_plan ?? null} />
          </TabsContent>
          <TabsContent value="mastery">
            <MasteryPanel
              plan={session?.learning_plan ?? null}
              mastery={mastery}
              error={masteryError}
              messages={messages}
              onRetry={() => void api.refreshMastery()}
            />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  )
}
