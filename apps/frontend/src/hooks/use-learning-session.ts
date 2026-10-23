"use client"

import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import {
  getMastery,
  getMessages,
  getSession,
  listSessions,
  newSessionId,
  sendChat,
  type ChatResponse,
  type MasteryState,
  type SessionDetail,
  type SessionSummary,
  type StoredMessage,
} from "@/lib/api"
import { deriveProgress } from "@/lib/learning"

/** The backend has no authentication; every browser acts as this one student. */
export const USER_ID = "user-default"
const ACTIVE_SESSION_KEY = "mentorai.activeSessionId"

export interface UiMessage {
  id: string
  role: "student" | "tutor"
  content: string
  /** Tutor turns: the full backend response, so cards render identically after a restore. */
  response?: ChatResponse | null
  createdAt?: string
  /** Student turns only. */
  delivery?: "sent" | "failed"
}

export type LoadState = "loading" | "new" | "ready" | "error"

export interface SendFailure {
  messageId: string
  text: string
  detail: string
}

function readStoredSessionId(): string | null {
  try {
    return window.localStorage.getItem(ACTIVE_SESSION_KEY)
  } catch {
    return null
  }
}

function storeSessionId(id: string) {
  try {
    window.localStorage.setItem(ACTIVE_SESSION_KEY, id)
  } catch {
    // storage unavailable (private mode); the session still works for this tab
  }
}

function fromStored(m: StoredMessage): UiMessage {
  return {
    id: m.id,
    role: m.role,
    content: m.content,
    response: m.role === "tutor" ? m.payload : undefined,
    createdAt: m.created_at,
    delivery: m.role === "student" ? "sent" : undefined,
  }
}

function errorText(e: unknown): string {
  return e instanceof Error ? e.message : "Something went wrong."
}

export function useLearningSession() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [loadState, setLoadState] = useState<LoadState>("loading")
  const [loadError, setLoadError] = useState<string | null>(null)
  const [session, setSession] = useState<SessionDetail | null>(null)
  const [messages, setMessages] = useState<UiMessage[]>([])
  const [historyError, setHistoryError] = useState<string | null>(null)
  const [pendingSince, setPendingSince] = useState<number | null>(null)
  const [failure, setFailure] = useState<SendFailure | null>(null)
  const [syncError, setSyncError] = useState<string | null>(null)
  const [mastery, setMastery] = useState<MasteryState[]>([])
  const [masteryError, setMasteryError] = useState<string | null>(null)
  const [sessions, setSessions] = useState<SessionSummary[] | null>(null)
  const [sessionsError, setSessionsError] = useState<string | null>(null)

  const busy = useRef(false)
  const activeId = useRef<string | null>(null)
  const loadToken = useRef(0)

  const refreshMastery = useCallback(async () => {
    try {
      setMastery(await getMastery(USER_ID))
      setMasteryError(null)
    } catch (e) {
      setMasteryError(errorText(e))
    }
  }, [])

  const openSession = useCallback(
    async (id: string) => {
      const token = ++loadToken.current
      activeId.current = id
      storeSessionId(id)
      setSessionId(id)
      setLoadState("loading")
      setLoadError(null)
      setSession(null)
      setMessages([])
      setHistoryError(null)
      setFailure(null)
      setSyncError(null)
      void refreshMastery()

      let detail: SessionDetail | null
      try {
        detail = await getSession(id)
      } catch (e) {
        if (token !== loadToken.current) return
        setLoadError(errorText(e))
        setLoadState("error")
        return
      }
      if (token !== loadToken.current) return
      if (!detail) {
        // 404: a genuinely new session (the backend creates it on the first message).
        setLoadState("new")
        return
      }
      setSession(detail)
      setLoadState("ready")
      try {
        const stored = await getMessages(id)
        if (token !== loadToken.current) return
        setMessages(stored.map(fromStored))
      } catch (e) {
        if (token !== loadToken.current) return
        setHistoryError(errorText(e))
      }
    },
    [refreshMastery]
  )

  // Restore the last active session on mount, or begin a fresh one. Never reuses a fixed id.
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time restore from localStorage after hydration
    void openSession(readStoredSessionId() ?? newSessionId())
  }, [openSession])

  const send = useCallback(
    async (rawText: string): Promise<boolean> => {
      const text = rawText.trim()
      const sid = activeId.current
      if (!text || !sid || busy.current) return false
      busy.current = true

      const studentId = `local-${Date.now()}-s`
      setFailure(null)
      setMessages((prev) => [
        ...prev,
        { id: studentId, role: "student", content: text, delivery: "sent", createdAt: new Date().toISOString() },
      ])
      setPendingSince(Date.now())

      try {
        const response = await sendChat(USER_ID, sid, text)
        if (activeId.current !== sid) return true
        setMessages((prev) => [
          ...prev,
          {
            id: `local-${Date.now()}-t`,
            role: "tutor",
            content: response.message ?? "",
            response,
            createdAt: new Date().toISOString(),
          },
        ])
        // Progress comes from the backend, never from the response type alone.
        try {
          const detail = await getSession(sid)
          if (activeId.current === sid) {
            setSession(detail)
            setLoadState(detail ? "ready" : "new")
            setSyncError(null)
          }
        } catch (e) {
          setSyncError(`Reply received, but the learning plan could not be refreshed: ${errorText(e)}`)
        }
        void refreshMastery()
        return true
      } catch (e) {
        if (activeId.current === sid) {
          setMessages((prev) => prev.map((m) => (m.id === studentId ? { ...m, delivery: "failed" } : m)))
          setFailure({ messageId: studentId, text, detail: errorText(e) })
        }
        return false
      } finally {
        busy.current = false
        setPendingSince(null)
      }
    },
    [refreshMastery]
  )

  /** Explicit user action: resend the failed text. Replaces the failed bubble instead of duplicating it. */
  const retry = useCallback(async () => {
    if (!failure || busy.current) return
    const { messageId, text } = failure
    setMessages((prev) => prev.filter((m) => m.id !== messageId))
    setFailure(null)
    await send(text)
  }, [failure, send])

  /** Remove the failed bubble and hand the text back so the learner can edit it. */
  const discardFailure = useCallback((): string => {
    if (!failure) return ""
    const { messageId, text } = failure
    setMessages((prev) => prev.filter((m) => m.id !== messageId))
    setFailure(null)
    return text
  }, [failure])

  const startNewSession = useCallback(() => {
    if (busy.current) return
    void openSession(newSessionId())
  }, [openSession])

  const switchSession = useCallback(
    (id: string) => {
      if (busy.current || id === activeId.current) return
      void openSession(id)
    },
    [openSession]
  )

  const reload = useCallback(() => {
    if (activeId.current && !busy.current) void openSession(activeId.current)
  }, [openSession])

  const refreshSessions = useCallback(async () => {
    setSessionsError(null)
    try {
      setSessions(await listSessions(USER_ID))
    } catch (e) {
      setSessionsError(errorText(e))
    }
  }, [])

  const progress = useMemo(() => deriveProgress(session), [session])
  const isPending = pendingSince !== null

  /** The learner's most recent answer, so "Revise my answer" can reuse it. */
  const lastStudentText = useMemo(() => [...messages].reverse().find((m) => m.role === "student")?.content ?? "", [messages])

  return {
    userId: USER_ID,
    sessionId,
    loadState,
    loadError,
    session,
    messages,
    historyError,
    isPending,
    pendingSince,
    failure,
    syncError,
    mastery,
    masteryError,
    sessions,
    sessionsError,
    progress,
    lastStudentText,
    send,
    retry,
    discardFailure,
    startNewSession,
    switchSession,
    reload,
    refreshSessions,
    refreshMastery,
  }
}

export type LearningSessionApi = ReturnType<typeof useLearningSession>
