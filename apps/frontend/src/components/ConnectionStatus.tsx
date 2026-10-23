"use client"

import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/ui/spinner"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import type { HealthState } from "@/hooks/use-llm-health"
import type { LlmHealth } from "@/lib/api"
import { cn } from "@/lib/utils"

/** LLM connectivity from the real /health/llm response. Click to re-check. */
export function ConnectionStatus({ state, data, onRefresh }: { state: HealthState; data: LlmHealth | null; onRefresh: () => void }) {
  const label = state === "ok" ? "Connected" : state === "checking" ? "Checking" : "Disconnected"
  const detail =
    state === "ok"
      ? `The model ${data?.model ?? ""} is available. This confirms the connection, not that a reply will succeed.`
      : state === "checking"
        ? "Checking the model connection."
        : (data?.message ?? "The model could not be reached.")

  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Button
            variant="outline"
            size="sm"
            onClick={onRefresh}
            aria-label={`Model status: ${label}. ${detail} Activate to check again.`}
          />
        }
      >
        {state === "checking" ? (
          <Spinner className="size-3" aria-hidden="true" />
        ) : (
          <span
            className={cn("size-2 rounded-full", state === "ok" ? "bg-success" : "bg-destructive")}
            aria-hidden="true"
          />
        )}
        <span className="hidden sm:inline">{label}</span>
        {state === "ok" && data?.model && <span className="hidden max-w-40 truncate font-mono text-xs text-muted-foreground xl:inline">{data.model}</span>}
      </TooltipTrigger>
      <TooltipContent className="max-w-72">{detail}</TooltipContent>
    </Tooltip>
  )
}
