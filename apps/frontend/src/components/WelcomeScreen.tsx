"use client"

import { useState } from "react"
import { GraduationCapIcon, MessageCircleQuestionIcon, RouteIcon, SparklesIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

const SUGGESTIONS = [
  "Help me understand what a Python variable is.",
  "I want to learn how binary search works.",
  "Teach me how to solve linear equations.",
  "Help me understand recursion.",
]

const APPROACH = [
  { icon: RouteIcon, title: "A path, not a lecture", text: "Your goal becomes a short plan of checkpoints, ordered by prerequisites." },
  { icon: MessageCircleQuestionIcon, title: "Questions that guide", text: "You answer each task in your own words. I check it against clear criteria." },
  { icon: SparklesIcon, title: "Hints when you need them", text: "If you are stuck, hints get gradually stronger. You only move on once you show understanding." },
]

export function WelcomeScreen({ onStart, disabled }: { onStart: (topic: string) => void; disabled?: boolean }) {
  const [topic, setTopic] = useState("")
  const canStart = topic.trim().length > 0 && !disabled

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-8 px-4 py-10 sm:py-14">
      <div className="flex flex-col items-center gap-3 text-center">
        <span className="flex size-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <GraduationCapIcon className="size-6" aria-hidden="true" />
        </span>
        <h1 className="text-2xl font-semibold tracking-tight text-balance">What would you like to learn today?</h1>
        <p className="max-w-lg text-sm text-muted-foreground text-pretty">
          I&apos;m your Socratic tutor. I won&apos;t just give you answers. I&apos;ll help you work them out, so they stay with you.
        </p>
      </div>

      <ul className="grid gap-3 sm:grid-cols-3">
        {APPROACH.map(({ icon: Icon, title, text }) => (
          <li key={title} className="flex flex-col gap-1.5 rounded-lg border bg-card p-3">
            <Icon className="size-4 text-primary" aria-hidden="true" />
            <p className="text-sm font-medium">{title}</p>
            <p className="text-xs leading-relaxed text-muted-foreground">{text}</p>
          </li>
        ))}
      </ul>

      <form
        className="flex flex-col gap-3"
        onSubmit={(e) => {
          e.preventDefault()
          if (canStart) onStart(topic.trim())
        }}
      >
        <label htmlFor="topic-input" className="text-sm font-medium">
          Your learning topic
        </label>
        <Textarea
          id="topic-input"
          value={topic}
          rows={2}
          disabled={disabled}
          onChange={(e) => setTopic(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault()
              if (canStart) onStart(topic.trim())
            }
          }}
          placeholder="For example: I want to understand how loops work in Python"
          className="min-h-20 resize-none bg-card"
        />
        <div className="flex flex-col gap-2">
          <p className="text-xs text-muted-foreground">Suggestions. Click one to edit it before you start.</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <Button key={s} type="button" variant="outline" size="sm" onClick={() => setTopic(s)}>
                {s}
              </Button>
            ))}
          </div>
        </div>
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs text-muted-foreground">Building your plan can take a minute or two on a local model.</p>
          <Button type="submit" disabled={!canStart}>
            Start learning
          </Button>
        </div>
      </form>
    </div>
  )
}
