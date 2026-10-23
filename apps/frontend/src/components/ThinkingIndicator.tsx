"use client"

import { useEffect, useState } from "react"
import { GraduationCapIcon } from "lucide-react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bubble, BubbleContent } from "@/components/ui/bubble"
import { Message, MessageAvatar, MessageContent } from "@/components/ui/message"
import { Spinner } from "@/components/ui/spinner"

function formatElapsed(totalSeconds: number) {
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  return m > 0 ? `${m}m ${String(s).padStart(2, "0")}s` : `${s}s`
}

/** Shown while a chat request is in flight. Shows only elapsed time; never invents partial output. */
export function ThinkingIndicator({ since }: { since: number }) {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const id = setInterval(() => setElapsed(Math.floor((Date.now() - since) / 1000)), 1000)
    return () => clearInterval(id)
  }, [since])

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
        <Bubble variant="muted">
          <BubbleContent>
            <div role="status" aria-live="polite" className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <Spinner className="size-3.5 text-primary" aria-hidden="true" />
                <span className="shimmer">Thinking through your response…</span>
                <span className="text-xs tabular-nums text-muted-foreground">{formatElapsed(elapsed)}</span>
              </div>
              {elapsed >= 15 && (
                <p className="text-xs text-muted-foreground">
                  Local models can take a minute or two. Keep this tab open; the reply will appear here.
                </p>
              )}
            </div>
          </BubbleContent>
        </Bubble>
      </MessageContent>
    </Message>
  )
}
