"use client"

import { useEffect, useState } from "react"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { AppHeader } from "@/components/AppHeader"
import { ConversationPanel } from "@/components/ConversationPanel"
import { LearningSidebar } from "@/components/LearningSidebar"
import { useLearningSession } from "@/hooks/use-learning-session"
import { useLlmHealth } from "@/hooks/use-llm-health"

const SIDEBAR_KEY = "mentorai.sidebarOpen"

export function LearningWorkspace() {
  const api = useLearningSession()
  const health = useLlmHealth()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    try {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- restore the saved preference after hydration
      if (window.localStorage.getItem(SIDEBAR_KEY) === "closed") setSidebarOpen(false)
    } catch {
      // storage unavailable; keep the default
    }
  }, [])

  const { failure } = api
  const refreshHealth = health.refresh
  useEffect(() => {
    // A failed request is a good moment to re-check the model connection instead of waiting for the next poll.
    if (failure) void refreshHealth()
  }, [failure, refreshHealth])

  function toggleSidebar() {
    setSidebarOpen((open) => {
      try {
        window.localStorage.setItem(SIDEBAR_KEY, open ? "closed" : "open")
      } catch {
        // ignore
      }
      return !open
    })
  }

  return (
    <div className="flex h-dvh flex-col bg-background">
      <a
        href="#conversation"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground"
      >
        Skip to conversation
      </a>
      <AppHeader
        api={api}
        health={health}
        onRefreshHealth={() => void health.refresh()}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={toggleSidebar}
        onOpenMobileSidebar={() => setMobileOpen(true)}
      />

      <div className="flex min-h-0 flex-1">
        {sidebarOpen && (
          <aside aria-label="Learning progress" className="hidden w-80 shrink-0 flex-col border-r bg-sidebar lg:flex xl:w-96">
            <LearningSidebar api={api} />
          </aside>
        )}
        <main id="conversation" className="flex min-w-0 flex-1 flex-col">
          <ConversationPanel api={api} />
        </main>
      </div>

      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <SheetContent side="left" className="w-[88vw] max-w-sm gap-0 p-0">
          <SheetHeader className="border-b">
            <SheetTitle>Learning progress</SheetTitle>
            <SheetDescription>Your plan, current concept and mastery.</SheetDescription>
          </SheetHeader>
          <LearningSidebar api={api} />
        </SheetContent>
      </Sheet>
    </div>
  )
}
