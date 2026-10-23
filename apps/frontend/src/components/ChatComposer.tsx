"use client"

import type { Ref } from "react"
import { SendHorizontalIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

/**
 * Controlled composer. While the tutor is replying, drafting stays possible but sending is blocked,
 * so a slow reply can never lead to a duplicate submission.
 */
export function ChatComposer({
  value,
  onChange,
  onSubmit,
  isPending,
  disabled = false,
  placeholder,
  textareaRef,
}: {
  value: string
  onChange: (value: string) => void
  onSubmit: (text: string) => void
  isPending: boolean
  disabled?: boolean
  placeholder?: string
  textareaRef?: Ref<HTMLTextAreaElement>
}) {
  const canSend = !disabled && !isPending && value.trim().length > 0

  function submit() {
    if (!canSend) return
    onSubmit(value.trim())
  }

  return (
    <form
      className="flex flex-col gap-2"
      onSubmit={(e) => {
        e.preventDefault()
        submit()
      }}
    >
      <div className="flex items-end gap-2 rounded-xl border bg-card p-2 shadow-xs focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/30">
        <label htmlFor="composer-input" className="sr-only">
          Your response to the tutor
        </label>
        <Textarea
          id="composer-input"
          ref={textareaRef}
          value={value}
          disabled={disabled}
          rows={1}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault()
              submit()
            }
          }}
          placeholder={
            placeholder ?? (isPending ? "The tutor is replying. You can draft your next message." : "Type your answer or question")
          }
          className="max-h-44 min-h-10 resize-none border-0 bg-transparent px-2 py-2 shadow-none focus-visible:ring-0 dark:bg-transparent"
        />
        <Button type="submit" size="icon-lg" disabled={!canSend} aria-label="Send message">
          <SendHorizontalIcon />
        </Button>
      </div>
      <p className="px-1 text-xs text-muted-foreground">
        <kbd className="font-sans">Enter</kbd> to send, <kbd className="font-sans">Shift</kbd>+<kbd className="font-sans">Enter</kbd> for a new line
      </p>
    </form>
  )
}
