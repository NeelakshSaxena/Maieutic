"use client"

import { useRef, useState } from "react"
import { CircleAlertIcon, HistoryIcon, PlusIcon, RefreshCwIcon } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Marker, MarkerContent, MarkerIcon } from "@/components/ui/marker"
import {
  MessageScroller,
  MessageScrollerButton,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerProvider,
  MessageScrollerViewport,
} from "@/components/ui/message-scroller"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import { ChatComposer } from "@/components/ChatComposer"
import { CheckpointCard } from "@/components/CheckpointCard"
import { StudentMessage, TutorMessage } from "@/components/MessageBubble"
import { ThinkingIndicator } from "@/components/ThinkingIndicator"
import { WelcomeScreen } from "@/components/WelcomeScreen"
import type { LearningSessionApi } from "@/hooks/use-learning-session"
import type { Progress as LearningProgress } from "@/lib/learning"

function ContextBar({ progress }: { progress: LearningProgress }) {
  if (progress.total === 0) return null
  const position = progress.current ? progress.current.index + 1 : progress.total
  const pct = Math.round((progress.completed / progress.total) * 100)
  return (
    <div className="border-b bg-card/60 px-4 py-2.5">
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-1.5">
        <div className="flex items-center justify-between gap-3 text-xs">
          <span className="min-w-0 truncate font-medium">
            {progress.isComplete
              ? "Plan complete"
              : `Checkpoint ${position} of ${progress.total}${progress.concept ? ` · ${progress.concept.name}` : ""}`}
          </span>
          <span className="shrink-0 text-muted-foreground tabular-nums">
            {progress.completed} of {progress.total} verified
          </span>
        </div>
        <Progress
          value={pct}
          aria-label={`Plan progress: ${progress.completed} of ${progress.total} checkpoints verified`}
          className="gap-0 [&_[data-slot=progress-track]]:h-1.5"
        />
        {progress.current && (
          <p className="line-clamp-2 text-sm text-muted-foreground">
            <span className="font-medium text-foreground">Task:</span> {progress.current.checkpoint.task}
          </p>
        )}
      </div>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4 px-4 py-8" aria-busy="true" aria-label="Loading session">
      <Skeleton className="h-16 w-3/5" />
      <Skeleton className="ml-auto h-10 w-2/5" />
      <Skeleton className="h-32 w-4/5" />
    </div>
  )
}

export function ConversationPanel({ api }: { api: LearningSessionApi }) {
  const [draft, setDraft] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { loadState, messages, isPending, pendingSince, failure, progress, historyError } = api

  function focusComposer() {
    setTimeout(() => textareaRef.current?.focus(), 0)
  }

  function handleSubmit(text: string) {
    setDraft("")
    void api.send(text)
  }

  function handleRevise() {
    setDraft(api.lastStudentText)
    focusComposer()
  }

  function handleEditFailed() {
    setDraft(api.discardFailure())
    focusComposer()
  }

  if (loadState === "loading") {
    return (
      <section aria-label="Conversation" className="flex min-h-0 flex-1 flex-col">
        <LoadingState />
      </section>
    )
  }

  if (loadState === "error") {
    return (
      <section aria-label="Conversation" className="flex min-h-0 flex-1 flex-col p-4">
        <Alert variant="destructive" className="mx-auto max-w-xl">
          <CircleAlertIcon aria-hidden="true" />
          <AlertTitle>This session could not be loaded</AlertTitle>
          <AlertDescription className="flex flex-col gap-3">
            <span>{api.loadError}</span>
            <span className="text-foreground/80">
              This is a connection problem, not an empty session. Nothing was changed. Check that the stack is running, then try again.
            </span>
            <div className="flex flex-wrap gap-2">
              <Button size="sm" variant="outline" onClick={api.reload}>
                <RefreshCwIcon data-icon="inline-start" />
                Try again
              </Button>
              <Button size="sm" variant="ghost" onClick={api.startNewSession}>
                <PlusIcon data-icon="inline-start" />
                Start a new session
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      </section>
    )
  }

  const showWelcome = loadState === "new" && messages.length === 0 && !isPending
  if (showWelcome) {
    return (
      <section aria-label="Conversation" className="flex min-h-0 flex-1 flex-col overflow-y-auto">
        <WelcomeScreen onStart={(topic) => void api.send(topic)} />
      </section>
    )
  }

  const lastTutorId = [...messages].reverse().find((m) => m.role === "tutor")?.id
  const noRecordedHistory = loadState === "ready" && messages.length === 0 && !historyError && !isPending

  return (
    <section aria-label="Conversation" className="flex min-h-0 flex-1 flex-col">
      <ContextBar progress={progress} />

      <div className="relative min-h-0 flex-1">
        <MessageScrollerProvider autoScroll>
          <MessageScroller>
            <MessageScrollerViewport>
              <MessageScrollerContent className="mx-auto w-full max-w-3xl px-4 py-6">
                {historyError && (
                  <MessageScrollerItem messageId="history-error">
                    <Alert variant="destructive">
                      <CircleAlertIcon aria-hidden="true" />
                      <AlertTitle>The earlier conversation could not be loaded</AlertTitle>
                      <AlertDescription className="flex flex-col gap-2">
                        <span>{historyError}</span>
                        <div>
                          <Button size="sm" variant="outline" onClick={api.reload}>
                            <RefreshCwIcon data-icon="inline-start" />
                            Reload session
                          </Button>
                        </div>
                      </AlertDescription>
                    </Alert>
                  </MessageScrollerItem>
                )}

                {noRecordedHistory && (
                  <MessageScrollerItem messageId="no-history">
                    <div className="flex flex-col gap-4">
                      <Marker variant="separator">
                        <MarkerIcon>
                          <HistoryIcon />
                        </MarkerIcon>
                        <MarkerContent>This session&apos;s earlier messages were not recorded</MarkerContent>
                      </Marker>
                      {progress.current ? (
                        <CheckpointCard
                          checkpoint={progress.current.checkpoint}
                          concept={progress.current.concept}
                          position={progress.current.index + 1}
                          total={progress.total}
                          state="current"
                        />
                      ) : (
                        <p className="text-sm text-muted-foreground">
                          {progress.isComplete ? "This learning plan is complete." : "Send a message to continue."}
                        </p>
                      )}
                    </div>
                  </MessageScrollerItem>
                )}

                {messages.map((m) => (
                  <MessageScrollerItem key={m.id} messageId={m.id}>
                    {m.role === "student" ? (
                      <StudentMessage message={m} />
                    ) : (
                      <TutorMessage
                        message={m}
                        progress={progress}
                        isLatest={m.id === lastTutorId && !isPending}
                        onRevise={handleRevise}
                      />
                    )}
                  </MessageScrollerItem>
                ))}

                {isPending && pendingSince !== null && (
                  <MessageScrollerItem messageId="thinking">
                    <ThinkingIndicator since={pendingSince} />
                  </MessageScrollerItem>
                )}

                {failure && (
                  <MessageScrollerItem messageId="send-failure">
                    <Alert variant="destructive" role="alert">
                      <CircleAlertIcon aria-hidden="true" />
                      <AlertTitle>Your message was not answered</AlertTitle>
                      <AlertDescription className="flex flex-col gap-3">
                        <span>{failure.detail}</span>
                        <span className="text-foreground/80">
                          If the tutor had already scored your answer before failing, sending it again counts as another attempt.
                          Nothing is resent unless you choose to.
                        </span>
                        <div className="flex flex-wrap gap-2">
                          <Button size="sm" variant="outline" onClick={() => void api.retry()}>
                            <RefreshCwIcon data-icon="inline-start" />
                            Send again
                          </Button>
                          <Button size="sm" variant="ghost" onClick={handleEditFailed}>
                            Edit message
                          </Button>
                        </div>
                      </AlertDescription>
                    </Alert>
                  </MessageScrollerItem>
                )}
              </MessageScrollerContent>
            </MessageScrollerViewport>
            <MessageScrollerButton />
          </MessageScroller>
        </MessageScrollerProvider>
      </div>

      <div className="border-t bg-background px-4 pt-3 pb-4">
        <div className="mx-auto w-full max-w-3xl">
          {progress.isComplete ? (
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-card p-3">
              <p className="text-sm text-muted-foreground">This learning plan is complete. Start a new session to learn something else.</p>
              <Button size="sm" onClick={api.startNewSession}>
                <PlusIcon data-icon="inline-start" />
                New session
              </Button>
            </div>
          ) : (
            <ChatComposer
              value={draft}
              onChange={setDraft}
              onSubmit={handleSubmit}
              isPending={isPending}
              textareaRef={textareaRef}
            />
          )}
        </div>
      </div>
    </section>
  )
}
