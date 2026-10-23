"use client"

import { CircleAlertIcon, GraduationCapIcon, PartyPopperIcon } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bubble, BubbleContent } from "@/components/ui/bubble"
import { Message, MessageAvatar, MessageContent, MessageFooter } from "@/components/ui/message"
import { CheckpointCard } from "@/components/CheckpointCard"
import { MarkdownContent } from "@/components/MarkdownContent"
import { HintCard, VerificationCard } from "@/components/TutorCards"
import type { Checkpoint } from "@/lib/api"
import type { Progress } from "@/lib/learning"
import type { UiMessage } from "@/hooks/use-learning-session"

function Timestamp({ iso }: { iso?: string }) {
  if (!iso) return null
  const d = new Date(iso.endsWith("Z") || /[+-]\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`)
  if (Number.isNaN(d.getTime())) return null
  return (
    <time dateTime={d.toISOString()} title={d.toLocaleString()}>
      {d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}
    </time>
  )
}

export function StudentMessage({ message }: { message: UiMessage }) {
  return (
    <Message align="end">
      <MessageContent>
        <Bubble variant="default" align="end">
          <BubbleContent className="whitespace-pre-wrap">{message.content}</BubbleContent>
        </Bubble>
        <MessageFooter>
          {message.delivery === "failed" ? (
            <span className="inline-flex items-center gap-1 text-destructive">
              <CircleAlertIcon className="size-3.5" aria-hidden="true" />
              Not delivered
            </span>
          ) : (
            <Timestamp iso={message.createdAt} />
          )}
        </MessageFooter>
      </MessageContent>
    </Message>
  )
}

function CheckpointFor({ checkpoint, progress, heading }: { checkpoint: Checkpoint; progress: Progress; heading?: string }) {
  const step = progress.steps.find((s) => s.checkpoint.id === checkpoint.id)
  return (
    <CheckpointCard
      checkpoint={checkpoint}
      concept={step?.concept}
      position={step ? step.index + 1 : undefined}
      total={step ? progress.total : undefined}
      state={step?.state}
      heading={heading}
    />
  )
}

export function TutorMessage({
  message,
  progress,
  isLatest,
  onRevise,
}: {
  message: UiMessage
  progress: Progress
  isLatest: boolean
  onRevise?: () => void
}) {
  const r = message.response
  const currentTask = isLatest ? progress.current?.checkpoint.task : undefined

  let body: React.ReactNode
  if (!r) {
    body = message.content ? (
      <Bubble variant="muted">
        <BubbleContent>
          <MarkdownContent>{message.content}</MarkdownContent>
        </BubbleContent>
      </Bubble>
    ) : null
  } else {
    switch (r.type) {
      case "new_plan":
        body = (
          <>
            <Bubble variant="muted">
              <BubbleContent>
                <div className="flex flex-col gap-1.5">
                  <p>
                    I&apos;ve mapped out a learning path
                    {progress.total > 0 ? ` with ${progress.total} checkpoints` : ""}. We&apos;ll go one step at a time, and I&apos;ll
                    guide you with questions instead of handing you the answers.
                  </p>
                  {progress.objective && <p className="text-muted-foreground">Goal: {progress.objective}</p>}
                </div>
              </BubbleContent>
            </Bubble>
            {r.next_checkpoint && <CheckpointFor checkpoint={r.next_checkpoint} progress={progress} heading="First task" />}
          </>
        )
        break
      case "correct":
        body = (
          <>
            {r.verification && <VerificationCard verification={r.verification} />}
            {r.next_checkpoint && <CheckpointFor checkpoint={r.next_checkpoint} progress={progress} heading="Next checkpoint unlocked" />}
          </>
        )
        break
      case "completed":
        body = (
          <>
            {r.verification && <VerificationCard verification={r.verification} />}
            <Alert className="w-full max-w-xl border-success/40 bg-success/5 text-foreground">
              <PartyPopperIcon className="text-success" aria-hidden="true" />
              <AlertTitle>Learning plan complete</AlertTitle>
              <AlertDescription>
                You have verified every checkpoint in this plan. Start a new session to learn something else.
              </AlertDescription>
            </Alert>
          </>
        )
        break
      case "incorrect":
      case "incomplete":
        body = (
          <>
            {r.verification && <VerificationCard verification={r.verification} />}
            {r.hint && <HintCard hint={r.hint} task={currentTask} onRevise={isLatest ? onRevise : undefined} />}
          </>
        )
        break
      case "off_topic":
        body = (
          <Bubble variant="muted">
            <BubbleContent>
              <div className="flex flex-col gap-1.5">
                <p>{r.message || "Let's stay focused on the current task."}</p>
                {currentTask && <p className="text-xs text-muted-foreground">Current task: {currentTask}</p>}
              </div>
            </BubbleContent>
          </Bubble>
        )
        break
      default:
        body = (
          <Bubble variant="muted">
            <BubbleContent>
              <MarkdownContent>{r.message || message.content || "The tutor returned an empty response."}</MarkdownContent>
            </BubbleContent>
          </Bubble>
        )
    }
  }

  return (
    <Message align="start">
      <MessageAvatar>
        <Avatar>
          <AvatarFallback className="bg-primary/10 text-primary">
            <GraduationCapIcon className="size-4" />
          </AvatarFallback>
        </Avatar>
      </MessageAvatar>
      <MessageContent>
        <div className="flex min-w-0 flex-col items-start gap-3 px-0.5 py-0.5">{body}</div>
        <MessageFooter>
          <Timestamp iso={message.createdAt} />
        </MessageFooter>
      </MessageContent>
    </Message>
  )
}
