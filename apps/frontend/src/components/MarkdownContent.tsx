"use client"

import { Children, isValidElement, useEffect, useRef, useState, type ReactElement, type ReactNode } from "react"
import ReactMarkdown, { type Components } from "react-markdown"
import remarkGfm from "remark-gfm"
import { CheckIcon, CopyIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

function CodeBlock({ code, language }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(
    () => () => {
      if (timer.current) clearTimeout(timer.current)
    },
    []
  )

  async function copy() {
    try {
      await navigator.clipboard.writeText(code)
    } catch {
      const ta = document.createElement("textarea")
      ta.value = code
      ta.setAttribute("readonly", "")
      ta.style.position = "fixed"
      ta.style.opacity = "0"
      document.body.appendChild(ta)
      ta.select()
      try {
        document.execCommand("copy")
      } finally {
        document.body.removeChild(ta)
      }
    }
    setCopied(true)
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => setCopied(false), 1800)
  }

  return (
    <div className="overflow-hidden rounded-lg border bg-muted/60">
      <div className="flex items-center justify-between gap-2 border-b bg-muted px-3 py-1">
        <span className="font-mono text-xs text-muted-foreground">{language || "code"}</span>
        <Button type="button" variant="ghost" size="xs" onClick={copy} aria-label={copied ? "Code copied" : "Copy code"}>
          {copied ? <CheckIcon data-icon="inline-start" /> : <CopyIcon data-icon="inline-start" />}
          {copied ? "Copied" : "Copy"}
        </Button>
      </div>
      <pre className="overflow-x-auto p-3 text-[0.8125rem] leading-relaxed" tabIndex={0}>
        <code className="font-mono">{code}</code>
      </pre>
    </div>
  )
}

function textOf(node: ReactNode): string {
  if (typeof node === "string" || typeof node === "number") return String(node)
  if (Array.isArray(node)) return node.map(textOf).join("")
  if (isValidElement(node)) return textOf((node as ReactElement<{ children?: ReactNode }>).props.children)
  return ""
}

// react-markdown does not render raw HTML by default, and unsafe URL schemes are stripped.
// Images are dropped so model output cannot trigger third-party requests.
const components: Components = {
  p: ({ children }) => <p className="leading-relaxed">{children}</p>,
  ul: ({ children }) => <ul className="flex list-disc flex-col gap-1 pl-5 marker:text-muted-foreground">{children}</ul>,
  ol: ({ children }) => <ol className="flex list-decimal flex-col gap-1 pl-5 marker:text-muted-foreground">{children}</ol>,
  h1: ({ children }) => <h3 className="text-base font-semibold">{children}</h3>,
  h2: ({ children }) => <h3 className="text-base font-semibold">{children}</h3>,
  h3: ({ children }) => <h4 className="text-sm font-semibold">{children}</h4>,
  h4: ({ children }) => <h4 className="text-sm font-semibold">{children}</h4>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-primary/40 pl-3 text-muted-foreground">{children}</blockquote>
  ),
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer nofollow" className="text-primary underline underline-offset-2">
      {children}
    </a>
  ),
  img: ({ alt }) => <span className="text-muted-foreground">{alt ? `[image: ${alt}]` : "[image]"}</span>,
  table: ({ children }) => (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-left text-sm">{children}</table>
    </div>
  ),
  th: ({ children }) => <th className="border-b px-2 py-1 font-medium">{children}</th>,
  td: ({ children }) => <td className="border-b px-2 py-1">{children}</td>,
  hr: () => <hr className="border-border" />,
  pre: ({ children }) => {
    const child = Children.toArray(children)[0]
    const className = isValidElement(child) ? ((child as ReactElement<{ className?: string }>).props.className ?? "") : ""
    const language = /language-([\w-]+)/.exec(className)?.[1]
    return <CodeBlock code={textOf(children).replace(/\n$/, "")} language={language} />
  },
  code: ({ children, className }) => (
    <code className={cn("rounded bg-muted px-1.5 py-0.5 font-mono text-[0.85em]", className)}>{children}</code>
  ),
}

export function MarkdownContent({ children, className }: { children: string; className?: string }) {
  return (
    <div className={cn("flex min-w-0 flex-col gap-3 text-sm wrap-break-word", className)}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {children}
      </ReactMarkdown>
    </div>
  )
}
