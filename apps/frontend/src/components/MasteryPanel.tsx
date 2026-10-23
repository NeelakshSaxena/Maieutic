"use client"

import { CircleAlertIcon, InfoIcon, RefreshCwIcon } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import type { LearningPlan, MasteryState } from "@/lib/api"
import { formatConceptId, masteryFor } from "@/lib/learning"
import type { UiMessage } from "@/hooks/use-learning-session"

const RECENT_LABEL = {
  correct: "Correct",
  incomplete: "Partly there",
  incorrect: "Not yet",
  off_topic: "Off topic",
} as const

function InfoTip({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <button
            type="button"
            aria-label={label}
            className="rounded-full text-muted-foreground outline-none hover:text-foreground focus-visible:ring-3 focus-visible:ring-ring/50"
          />
        }
      >
        <InfoIcon className="size-3.5" aria-hidden="true" />
      </TooltipTrigger>
      <TooltipContent className="max-w-64">{children}</TooltipContent>
    </Tooltip>
  )
}

export function MasteryPanel({
  plan,
  mastery,
  error,
  messages,
  onRetry,
}: {
  plan: LearningPlan | null
  mastery: MasteryState[]
  error: string | null
  messages: UiMessage[]
  onRetry: () => void
}) {
  const concepts = plan?.concepts ?? []
  const recent = messages
    .filter((m) => m.role === "tutor" && m.response?.verification && m.response.type !== "off_topic")
    .slice(-5)
    .reverse()

  return (
    <div className="flex flex-col gap-5">
      {error && (
        <Alert variant="destructive">
          <CircleAlertIcon aria-hidden="true" />
          <AlertDescription className="flex flex-col gap-2">
            <span>Mastery data could not be loaded: {error}</span>
            <div>
              <Button size="sm" variant="outline" onClick={onRetry}>
                <RefreshCwIcon data-icon="inline-start" />
                Retry
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      <section className="flex flex-col gap-3">
        <div className="flex items-center gap-1.5">
          <h3 className="text-xs font-medium tracking-wide text-muted-foreground uppercase">Concept mastery</h3>
          <InfoTip label="How mastery is calculated">
            Mastery is a moving average of the verifier&apos;s scores for a concept; each new answer counts for 30%. It is kept per
            student and concept, so it can carry across sessions.
          </InfoTip>
        </div>

        {concepts.length === 0 ? (
          <p className="rounded-lg border border-dashed p-4 text-sm text-muted-foreground">
            Mastery appears here once you have a plan and answer your first checkpoint.
          </p>
        ) : (
          <ul className="flex flex-col gap-3">
            {concepts.map((c) => {
              const m = masteryFor(mastery, c.id)
              const pct = m ? Math.round(m.historical_mastery * 100) : 0
              return (
                <li key={c.id} className="flex flex-col gap-2 rounded-lg border bg-card p-3">
                  <div className="flex items-baseline justify-between gap-2">
                    <span className="min-w-0 truncate text-sm font-medium">{c.name}</span>
                    <span className="shrink-0 text-sm tabular-nums text-muted-foreground">{m ? `${pct}%` : "Not started"}</span>
                  </div>
                  <Progress
                    value={pct}
                    aria-label={m ? `Mastery of ${c.name}: ${pct} percent` : `Mastery of ${c.name}: no attempts yet`}
                    className="gap-0 [&_[data-slot=progress-track]]:h-2"
                  />
                  {m && (
                    <div className="flex flex-col gap-1.5">
                      <p className="text-xs text-muted-foreground">
                        {m.attempts} {m.attempts === 1 ? "attempt" : "attempts"}
                      </p>
                      {m.misconceptions_observed.length > 0 && (
                        <div className="flex flex-wrap items-center gap-1.5">
                          <span className="text-xs text-muted-foreground">Misconceptions seen:</span>
                          {m.misconceptions_observed.map((x) => (
                            <Badge key={x} variant="outline" className="font-normal">
                              {x}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </li>
              )
            })}
          </ul>
        )}
      </section>

      {recent.length > 0 && (
        <section className="flex flex-col gap-2">
          <h3 className="text-xs font-medium tracking-wide text-muted-foreground uppercase">Recent answers</h3>
          <ul className="flex flex-col gap-1.5">
            {recent.map((m) => {
              const v = m.response!.verification!
              return (
                <li key={m.id} className="flex items-center justify-between gap-2 text-sm">
                  <Badge variant={v.status === "correct" ? "secondary" : "outline"}>{RECENT_LABEL[v.status]}</Badge>
                  <span className="tabular-nums text-muted-foreground">Score {Math.round(v.mastery_score * 100)}%</span>
                </li>
              )
            })}
          </ul>
        </section>
      )}

      {mastery.length > 0 && concepts.length > 0 && !mastery.some((m) => concepts.some((c) => c.id === m.concept_id)) && (
        <p className="text-xs text-muted-foreground">
          Other concepts you have studied are tracked too ({mastery.map((m) => formatConceptId(m.concept_id)).join(", ")}).
        </p>
      )}
    </div>
  )
}
