"use client"

import { useCallback, useEffect, useState } from "react"
import { getLlmHealth, type LlmHealth } from "@/lib/api"

export type HealthState = "checking" | "ok" | "error"

const POLL_MS = 60_000

/** Real LLM connectivity from /health/llm (model listed by the configured endpoint). Not an inference test. */
export function useLlmHealth() {
  const [state, setState] = useState<HealthState>("checking")
  const [data, setData] = useState<LlmHealth | null>(null)

  const refresh = useCallback(async () => {
    setState((s) => (s === "ok" ? s : "checking"))
    const result = await getLlmHealth()
    setData(result)
    setState(result.status === "ok" ? "ok" : "error")
  }, [])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- initial fetch on mount
    void refresh()
    const id = setInterval(() => void refresh(), POLL_MS)
    return () => clearInterval(id)
  }, [refresh])

  return { state, data, refresh }
}
