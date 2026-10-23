"use client"

import { CircleAlertIcon, CircleCheckIcon, CircleDashedIcon, InfoIcon, LightbulbIcon, PencilLineIcon } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { MarkdownContent } from "@/components/MarkdownContent"
import type { HintResult, VerificationResult } from "@/lib/api"
import { cn } from "@/lib/utils"

const STATUS: Record<VerificationResult["status"], { label: string; icon: typeof CircleCheckIcon; tone: string; iconTone: string }> = {
  correct: { label: "Correct", icon: CircleCheckIcon, tone: "border-success/40 bg-success/5", iconTone: "text-success" },
  incomplete: { label: "Partly there", icon: CircleDashedIcon, tone: "border-warning/40 bg-warning/5", iconTone: "text-warning" },
  incorrect: { label: "Not quite yet", icon: CircleAlertIcon, tone: "border-destructive/30 bg-destructive/5", iconTone: "text-destructive" },
  off_topic: { label: "Off topic", icon: InfoIcon, tone: "bg-muted/50", iconTone: "text-muted-foreground" },
}

/** The verifier's judgement of one answer, straight from the backend response. */
export function VerificationCard({ verification }: { verification: VerificationResult }) {
  const s = STATUS[verification.status]
  const Icon = s.icon
  const score = Math.round(verification.mastery_score * 100)
  const met = verification.criteria_evaluation.filter((c) => c.met).length
  const total = verification.criteria_evaluation.length

  return (
    <Alert className={cn("w-full max-w-xl text-foreground", s.tone)}>
      <Icon className={s.iconTone} aria-hidden="true" />
      <AlertTitle className="flex flex-wrap items-center gap-2">
        {s.label}
        <Tooltip>
          <TooltipTrigger
            render={
              <Badge variant="outline" className="cursor-help font-normal tabular-nums">
                Score {score}%
              </Badge>
            }
          />
          <TooltipContent>
            The verifier&apos;s score for this answer. It feeds your concept mastery, which is a moving average of recent scores.
          </TooltipContent>
        </Tooltip>
      </AlertTitle>
      <AlertDescription className="flex flex-col gap-2 text-foreground/90">
        {verification.explanation && <MarkdownContent>{verification.explanation}</MarkdownContent>}
        {verification.misconceptions.length > 0 && (
          <ul className="flex flex-col gap-1 text-sm">
            {verification.misconceptions.map((m) => (
              <li key={m.name}>
                <span className="font-medium">Misconception: {m.name}.</span> {m.description}
              </li>
            ))}
          </ul>
        )}
        {total > 0 && (
          <Collapsible>
            <CollapsibleTrigger className="rounded-sm text-xs font-medium underline underline-offset-2 outline-none focus-visible:ring-3 focus-visible:ring-ring/50">
              Criteria checked ({met} of {total} met)
            </CollapsibleTrigger>
            <CollapsibleContent>
              <ul className="mt-2 flex flex-col gap-2">
                {verification.criteria_evaluation.map((c) => (
                  <li key={c.criterion} className="flex gap-2">
                    {c.met ? (
                      <CircleCheckIcon className="mt-0.5 size-4 shrink-0 text-success" aria-label="Met" />
                    ) : (
                      <CircleDashedIcon className="mt-0.5 size-4 shrink-0 text-muted-foreground" aria-label="Not met" />
                    )}
                    <span>
                      {c.criterion}
                      {c.evidence && <span className="block text-xs text-muted-foreground">{c.evidence}</span>}
                    </span>
                  </li>
                ))}
              </ul>
            </CollapsibleContent>
          </Collapsible>
        )}
      </AlertDescription>
    </Alert>
  )
}

/** A hint the backend generated automatically after an incorrect or incomplete answer. */
export function HintCard({
  hint,
  task,
  onRevise,
}: {
  hint: HintResult
  /** The question the hint relates to, kept visible beside the hint. */
  task?: string
  onRevise?: () => void
}) {
  return (
    <Alert className="w-full max-w-xl border-primary/25 bg-accent/60">
      <LightbulbIcon className="text-primary" aria-hidden="true" />
      <AlertTitle className="flex flex-wrap items-center gap-2">
        Hint
        <Badge variant="secondary">Level {hint.level_used} of 4</Badge>
        <Badge variant="outline" className="font-normal">
          Guidance, not a verified answer
        </Badge>
      </AlertTitle>
      <AlertDescription className="flex flex-col gap-3 text-foreground/90">
        <MarkdownContent>{hint.hint_text}</MarkdownContent>
        {hint.was_answer_revealed && (
          <p className="text-xs text-muted-foreground">The tutor flagged that this hint may reveal part of the answer.</p>
        )}
        {task && (
          <p className="border-l-2 border-primary/30 pl-3 text-xs text-muted-foreground">
            <span className="font-medium">Still working on:</span> {task}
          </p>
        )}
        {onRevise && (
          <div>
            <Button type="button" size="sm" variant="outline" onClick={onRevise}>
              <PencilLineIcon data-icon="inline-start" />
              Revise my answer
            </Button>
          </div>
        )}
      </AlertDescription>
    </Alert>
  )
}
