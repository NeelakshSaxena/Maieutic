"use client"

import { useState } from "react"
import { CheckIcon, ChevronDownIcon, CopyIcon, HistoryIcon, InfoIcon, ListIcon, PlusIcon, RefreshCwIcon } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/components/ui/empty"
import { Skeleton } from "@/components/ui/skeleton"
import type { LearningSessionApi } from "@/hooks/use-learning-session"
import { cn } from "@/lib/utils"

function formatDate(iso?: string) {
  if (!iso) return "Unknown"
  const d = new Date(iso.endsWith("Z") || /[+-]\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`)
  return Number.isNaN(d.getTime()) ? "Unknown" : d.toLocaleString([], { dateStyle: "medium", timeStyle: "short" })
}

function CopyId({ value }: { value: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <Button
      type="button"
      size="icon-xs"
      variant="ghost"
      aria-label={copied ? "Session ID copied" : "Copy session ID"}
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(value)
          setCopied(true)
          setTimeout(() => setCopied(false), 1500)
        } catch {
          // clipboard unavailable; the id is selectable text
        }
      }}
    >
      {copied ? <CheckIcon /> : <CopyIcon />}
    </Button>
  )
}

function SessionsDialog({ api, open, onOpenChange }: { api: LearningSessionApi; open: boolean; onOpenChange: (o: boolean) => void }) {
  const { sessions, sessionsError, sessionId } = api
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Your sessions</DialogTitle>
          <DialogDescription>Switching keeps every session and its progress. Nothing is deleted.</DialogDescription>
        </DialogHeader>
        <div className="flex max-h-[60vh] flex-col gap-2 overflow-y-auto">
          {sessionsError ? (
            <Alert variant="destructive">
              <AlertDescription className="flex flex-col gap-2">
                <span>Sessions could not be loaded: {sessionsError}</span>
                <div>
                  <Button size="sm" variant="outline" onClick={() => void api.refreshSessions()}>
                    <RefreshCwIcon data-icon="inline-start" />
                    Retry
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          ) : sessions === null ? (
            <div className="flex flex-col gap-2" aria-busy="true">
              <Skeleton className="h-14" />
              <Skeleton className="h-14" />
              <Skeleton className="h-14" />
            </div>
          ) : sessions.length === 0 ? (
            <Empty>
              <EmptyHeader>
                <EmptyTitle>No saved sessions yet</EmptyTitle>
                <EmptyDescription>A session is saved when you send your first message.</EmptyDescription>
              </EmptyHeader>
            </Empty>
          ) : (
            <ul className="flex flex-col gap-2">
              {sessions.map((s) => {
                const isCurrent = s.id === sessionId
                return (
                  <li key={s.id}>
                    <button
                      type="button"
                      disabled={api.isPending}
                      onClick={() => {
                        api.switchSession(s.id)
                        onOpenChange(false)
                      }}
                      className={cn(
                        "flex w-full flex-col gap-1 rounded-lg border bg-card px-3 py-2 text-left outline-none transition-colors hover:bg-muted focus-visible:ring-3 focus-visible:ring-ring/50 disabled:opacity-60",
                        isCurrent && "border-primary/50 bg-accent/50"
                      )}
                    >
                      <span className="flex items-start justify-between gap-2">
                        <span className="line-clamp-2 text-sm font-medium">{s.goal || "Untitled session"}</span>
                        <span className="flex shrink-0 gap-1">
                          {isCurrent && <Badge>Current</Badge>}
                          <Badge variant={s.status === "completed" ? "secondary" : "outline"}>
                            {s.status === "completed" ? "Completed" : "In progress"}
                          </Badge>
                        </span>
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {s.completed_checkpoints} of {s.checkpoint_count} checkpoints verified · updated {formatDate(s.updated_at)}
                      </span>
                    </button>
                  </li>
                )
              })}
            </ul>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

function DetailsDialog({ api, open, onOpenChange }: { api: LearningSessionApi; open: boolean; onOpenChange: (o: boolean) => void }) {
  const { session, sessionId, userId } = api
  const rows: [string, React.ReactNode][] = [
    ["Session ID", <span key="id" className="flex items-center gap-1"><code className="font-mono text-xs break-all">{sessionId}</code>{sessionId && <CopyId value={sessionId} />}</span>],
    ["Student ID", <code key="u" className="font-mono text-xs">{userId}</code>],
    ["Status", session ? (session.status === "completed" ? "Completed" : "In progress") : "Not started yet"],
    ["Goal", session?.goal ?? "Set by your first message"],
    ["Created", session ? formatDate(session.created_at) : "Not saved yet"],
    ["Last updated", session ? formatDate(session.updated_at) : "Not saved yet"],
  ]
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Session details</DialogTitle>
          <DialogDescription>Technical details for this session. MentorAI has no sign-in, so the student ID is shared by this app.</DialogDescription>
        </DialogHeader>
        <dl className="flex flex-col gap-3 text-sm">
          {rows.map(([k, v]) => (
            <div key={k} className="flex flex-col gap-0.5">
              <dt className="text-xs text-muted-foreground">{k}</dt>
              <dd>{v}</dd>
            </div>
          ))}
        </dl>
      </DialogContent>
    </Dialog>
  )
}

export function SessionSwitcher({ api }: { api: LearningSessionApi }) {
  const [sessionsOpen, setSessionsOpen] = useState(false)
  const [detailsOpen, setDetailsOpen] = useState(false)
  const waiting = api.isPending

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger render={<Button variant="outline" size="sm" aria-label="Session menu" />}>
          <HistoryIcon data-icon="inline-start" />
          <span className="hidden sm:inline">Sessions</span>
          <ChevronDownIcon data-icon="inline-end" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-60">
          <DropdownMenuGroup>
            <DropdownMenuLabel>{waiting ? "Waiting for the tutor to reply" : "Learning sessions"}</DropdownMenuLabel>
            <DropdownMenuItem disabled={waiting} onClick={api.startNewSession}>
              <PlusIcon />
              New session
            </DropdownMenuItem>
            <DropdownMenuItem
              disabled={waiting}
              onClick={() => {
                setSessionsOpen(true)
                void api.refreshSessions()
              }}
            >
              <ListIcon />
              All sessions
            </DropdownMenuItem>
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <DropdownMenuItem onClick={() => setDetailsOpen(true)}>
              <InfoIcon />
              Session details
            </DropdownMenuItem>
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>
      <SessionsDialog api={api} open={sessionsOpen} onOpenChange={setSessionsOpen} />
      <DetailsDialog api={api} open={detailsOpen} onOpenChange={setDetailsOpen} />
    </>
  )
}
