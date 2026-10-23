"use client"

import { ChevronDownIcon, CircleCheckIcon, LockIcon, TargetIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import type { Checkpoint, Concept } from "@/lib/api"
import type { CheckpointState } from "@/lib/learning"
import { cn } from "@/lib/utils"

const STATE_LABEL: Record<CheckpointState, string> = {
  completed: "Completed",
  current: "Current task",
  upcoming: "Locked",
}

export function CheckpointCard({
  checkpoint,
  concept,
  position,
  total,
  state,
  heading,
}: {
  checkpoint: Checkpoint
  concept?: Concept
  /** 1-based position in the plan, when known. */
  position?: number
  total?: number
  state?: CheckpointState
  heading?: string
}) {
  const isCurrent = state === "current"
  return (
    <Card size="sm" className={cn("w-full max-w-xl", isCurrent && "ring-2 ring-primary/30")}>
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={isCurrent ? "default" : "secondary"}>
            {state === "completed" ? (
              <CircleCheckIcon data-icon="inline-start" />
            ) : state === "upcoming" ? (
              <LockIcon data-icon="inline-start" />
            ) : (
              <TargetIcon data-icon="inline-start" />
            )}
            {heading ?? (state ? STATE_LABEL[state] : "Checkpoint")}
          </Badge>
          {position && total ? (
            <span className="text-xs text-muted-foreground">
              Checkpoint {position} of {total}
            </span>
          ) : null}
        </div>
        {concept && (
          <>
            <CardTitle>{concept.name}</CardTitle>
            <CardDescription>{concept.description}</CardDescription>
          </>
        )}
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <div>
          <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">Your task</p>
          <p className="mt-1 text-sm leading-relaxed">{checkpoint.task}</p>
        </div>
        <Collapsible>
          <CollapsibleTrigger className="group flex items-center gap-1 rounded-sm text-xs font-medium text-muted-foreground outline-none hover:text-foreground focus-visible:ring-3 focus-visible:ring-ring/50">
            <ChevronDownIcon className="size-3.5 transition-transform group-aria-expanded:rotate-180" aria-hidden="true" />
            What a strong answer includes
          </CollapsibleTrigger>
          <CollapsibleContent>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{checkpoint.success_criteria}</p>
          </CollapsibleContent>
        </Collapsible>
      </CardContent>
    </Card>
  )
}
