"use client"

import { ChevronDownIcon, CircleCheckIcon, LockIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import type { JourneyStep, Progress } from "@/lib/learning"
import { cn } from "@/lib/utils"

const BADGE: Record<JourneyStep["state"], { label: string; variant: "default" | "secondary" | "outline" }> = {
  completed: { label: "Verified", variant: "secondary" },
  current: { label: "Current", variant: "default" },
  upcoming: { label: "Locked", variant: "outline" },
}

function Marker({ state }: { state: JourneyStep["state"] }) {
  if (state === "completed") return <CircleCheckIcon className="size-5 text-success" aria-hidden="true" />
  if (state === "upcoming") return <LockIcon className="size-4 text-muted-foreground" aria-hidden="true" />
  return <span className="size-3 rounded-full bg-primary ring-4 ring-primary/20" aria-hidden="true" />
}

function Step({ step, isLast }: { step: JourneyStep; isLast: boolean }) {
  const b = BADGE[step.state]
  return (
    <li className="relative flex gap-3">
      <div className="flex w-5 shrink-0 flex-col items-center">
        <span className="flex h-6 items-center justify-center">
          <Marker state={step.state} />
        </span>
        {!isLast && <span className={cn("mt-1 w-px flex-1", step.state === "completed" ? "bg-success/50" : "bg-border")} aria-hidden="true" />}
      </div>
      {/* key remounts the collapsible when its state changes so the current step opens by itself */}
      <Collapsible key={`${step.checkpoint.id}-${step.state}`} defaultOpen={step.state === "current"} className="mb-3 min-w-0 flex-1">
        <CollapsibleTrigger
          className={cn(
            "group flex w-full items-start justify-between gap-2 rounded-lg border bg-card px-3 py-2 text-left outline-none transition-colors hover:bg-muted focus-visible:ring-3 focus-visible:ring-ring/50",
            step.state === "current" && "border-primary/40 bg-accent/50"
          )}
        >
          <span className="min-w-0">
            <span className="block text-xs text-muted-foreground">Checkpoint {step.index + 1}</span>
            <span className="line-clamp-2 text-sm font-medium">{step.concept?.name ?? "Checkpoint"}</span>
          </span>
          <span className="flex shrink-0 items-center gap-1.5">
            <Badge variant={b.variant}>{b.label}</Badge>
            <ChevronDownIcon className="size-4 text-muted-foreground transition-transform group-aria-expanded:rotate-180" aria-hidden="true" />
          </span>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="flex flex-col gap-2 px-1 pt-2 text-sm">
            <p className="leading-relaxed">{step.checkpoint.task}</p>
            <p className="text-xs leading-relaxed text-muted-foreground">
              <span className="font-medium">A strong answer:</span> {step.checkpoint.success_criteria}
            </p>
            {step.state === "upcoming" && (
              <p className="text-xs text-muted-foreground">Unlocks after the checkpoint before it is verified.</p>
            )}
          </div>
        </CollapsibleContent>
      </Collapsible>
    </li>
  )
}

export function LearningJourney({ progress }: { progress: Progress }) {
  if (progress.total === 0) {
    return (
      <p className="rounded-lg border border-dashed p-4 text-sm text-muted-foreground">
        Your learning path appears here once you tell the tutor what you want to learn.
      </p>
    )
  }
  return (
    <ol aria-label="Learning journey" className="flex flex-col">
      {progress.steps.map((s, i) => (
        <Step key={s.checkpoint.id} step={s} isLast={i === progress.steps.length - 1} />
      ))}
    </ol>
  )
}
