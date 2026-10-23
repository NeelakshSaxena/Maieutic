"use client"

import { GraduationCapIcon, PanelLeftCloseIcon, PanelLeftOpenIcon, PanelLeftIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ConnectionStatus } from "@/components/ConnectionStatus"
import { SessionSwitcher } from "@/components/SessionSwitcher"
import type { HealthState } from "@/hooks/use-llm-health"
import type { LearningSessionApi } from "@/hooks/use-learning-session"
import type { LlmHealth } from "@/lib/api"

export function AppHeader({
  api,
  health,
  onRefreshHealth,
  sidebarOpen,
  onToggleSidebar,
  onOpenMobileSidebar,
}: {
  api: LearningSessionApi
  health: { state: HealthState; data: LlmHealth | null }
  onRefreshHealth: () => void
  sidebarOpen: boolean
  onToggleSidebar: () => void
  onOpenMobileSidebar: () => void
}) {
  const title = api.session?.goal

  return (
    <header className="flex h-14 shrink-0 items-center gap-2 border-b bg-card px-3 sm:px-4">
      <Button variant="ghost" size="icon" className="lg:hidden" onClick={onOpenMobileSidebar} aria-label="Open learning progress">
        <PanelLeftIcon />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="hidden lg:inline-flex"
        onClick={onToggleSidebar}
        aria-label={sidebarOpen ? "Collapse learning panel" : "Expand learning panel"}
        aria-expanded={sidebarOpen}
      >
        {sidebarOpen ? <PanelLeftCloseIcon /> : <PanelLeftOpenIcon />}
      </Button>

      <div className="flex items-center gap-2">
        <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <GraduationCapIcon className="size-5" aria-hidden="true" />
        </span>
        <span className="hidden text-base font-semibold tracking-tight sm:inline">MentorAI</span>
      </div>

      <Separator orientation="vertical" className="mx-1 hidden h-5 sm:block" />

      <h1 className="min-w-0 flex-1 truncate text-sm text-muted-foreground" title={title}>
        {title ? <span className="font-medium text-foreground">{title}</span> : "New learning session"}
      </h1>

      <div className="flex shrink-0 items-center gap-2">
        <ConnectionStatus state={health.state} data={health.data} onRefresh={onRefreshHealth} />
        <SessionSwitcher api={api} />
      </div>
    </header>
  )
}
