// Typed client for the MentorAI backend. Shapes mirror apps/api/app/schemas and routers.py.
// Calls go to the same-origin Next.js proxy ("/api", "/health/llm"); no secrets live in the browser.

export type VerificationStatus = "correct" | "incorrect" | "incomplete" | "off_topic"
export type ChatResponseType = VerificationStatus | "new_plan" | "completed" | "error"

export interface Concept {
  id: string
  name: string
  description: string
}

export interface Dependency {
  prerequisite_id: string
  concept_id: string
}

export interface Checkpoint {
  id: string
  concept_id: string
  task: string
  success_criteria: string
}

export interface LearningPlan {
  learning_objectives: string
  concepts: Concept[]
  dependencies: Dependency[]
  checkpoints: Checkpoint[]
}

export interface SessionDetail {
  id: string
  goal: string
  status: string // "active" | "completed"
  current_checkpoint_id: string | null
  learning_plan: LearningPlan | null
  created_at?: string
  updated_at?: string
}

export interface SessionSummary {
  id: string
  goal: string
  status: string
  current_checkpoint_id: string | null
  checkpoint_count: number
  completed_checkpoints: number
  created_at: string
  updated_at: string
}

export interface CriterionEvaluation {
  criterion: string
  met: boolean
  evidence: string
}

export interface VerificationResult {
  is_correct: boolean
  status: VerificationStatus
  criteria_evaluation: CriterionEvaluation[]
  misconceptions: { name: string; description: string; evidence: string }[]
  mastery_score: number
  explanation: string
}

export interface HintResult {
  level_used: "1" | "2" | "3" | "4"
  hint_text: string
  target: string
  rationale: string
  was_answer_revealed: boolean
}

export interface ChatResponse {
  type: ChatResponseType
  message: string | null
  next_checkpoint: Checkpoint | null
  hint: HintResult | null
  verification: VerificationResult | null
}

export interface StoredMessage {
  id: string
  role: "student" | "tutor"
  content: string
  payload: ChatResponse | null
  created_at: string
}

export interface MasteryState {
  concept_id: string
  historical_mastery: number
  attempts: number
  misconceptions_observed: string[]
}

export interface LlmHealth {
  status: string
  message?: string
  model?: string
  available_models?: string[]
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api"
const HEALTH_URL = process.env.NEXT_PUBLIC_HEALTH_URL || "/health/llm"

/** An HTTP error from the backend, with the server-provided `detail` when present. */
export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number
  ) {
    super(message)
    this.name = "ApiError"
  }
}

async function readDetail(res: Response): Promise<string> {
  try {
    const body = await res.json()
    if (typeof body?.detail === "string") return body.detail
    if (typeof body?.message === "string") return body.message
  } catch {
    // not JSON
  }
  return `Request failed (HTTP ${res.status})`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_BASE}${path}`, init)
  } catch {
    throw new ApiError("Could not reach the MentorAI service. Check that the stack is running.", 0)
  }
  if (!res.ok) {
    // 502 comes from the Next.js proxy when the FastAPI container is down.
    if (res.status === 502) {
      throw new ApiError("Could not reach the MentorAI backend. Check that the API container is running, then try again.", 502)
    }
    throw new ApiError(await readDetail(res), res.status)
  }
  return (await res.json()) as T
}

/** Returns null when the session does not exist yet (HTTP 404); throws for any other failure. */
export async function getSession(sessionId: string): Promise<SessionDetail | null> {
  try {
    return await request<SessionDetail>(`/session/${encodeURIComponent(sessionId)}`)
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null
    throw e
  }
}

export async function getMessages(sessionId: string): Promise<StoredMessage[]> {
  const data = await request<{ messages: StoredMessage[] }>(
    `/session/${encodeURIComponent(sessionId)}/messages`
  )
  return data.messages
}

export async function listSessions(userId: string): Promise<SessionSummary[]> {
  const data = await request<{ sessions: SessionSummary[] }>(
    `/sessions?user_id=${encodeURIComponent(userId)}`
  )
  return data.sessions
}

export async function getMastery(userId: string): Promise<MasteryState[]> {
  const data = await request<{ mastery_states: MasteryState[] }>(`/brain/${encodeURIComponent(userId)}`)
  return data.mastery_states ?? []
}

export function sendChat(userId: string, sessionId: string, message: string): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, session_id: sessionId, message }),
  })
}

export async function getLlmHealth(): Promise<LlmHealth> {
  let res: Response
  try {
    res = await fetch(HEALTH_URL, { cache: "no-store" })
  } catch {
    return { status: "error", message: "The MentorAI service is unreachable." }
  }
  try {
    return (await res.json()) as LlmHealth
  } catch {
    return { status: "error", message: `Health check failed (HTTP ${res.status}).` }
  }
}

/** Unique session id; falls back when crypto.randomUUID is unavailable (non-secure contexts). */
export function newSessionId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return `session-${crypto.randomUUID()}`
  }
  return `session-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`
}
