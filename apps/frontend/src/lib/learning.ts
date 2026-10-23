import type { Checkpoint, Concept, MasteryState, SessionDetail } from "@/lib/api"

export type CheckpointState = "completed" | "current" | "upcoming"

export interface JourneyStep {
  checkpoint: Checkpoint
  index: number
  state: CheckpointState
  concept: Concept | undefined
}

export interface Progress {
  steps: JourneyStep[]
  total: number
  completed: number
  current: JourneyStep | null
  isComplete: boolean
  concept: Concept | undefined
  prerequisites: Concept[]
  objective: string | null
}

/**
 * Derives progress purely from backend state: a checkpoint is completed only if it comes before
 * `current_checkpoint_id` in the plan, or the session itself is marked completed. Nothing here is
 * ever set by a UI click.
 */
export function deriveProgress(session: SessionDetail | null): Progress {
  const plan = session?.learning_plan
  const checkpoints = plan?.checkpoints ?? []
  const concepts = plan?.concepts ?? []
  const isComplete = session?.status === "completed"
  const currentIdx = isComplete ? -1 : checkpoints.findIndex((c) => c.id === session?.current_checkpoint_id)

  const steps: JourneyStep[] = checkpoints.map((checkpoint, index) => ({
    checkpoint,
    index,
    concept: concepts.find((c) => c.id === checkpoint.concept_id),
    state: isComplete || (currentIdx !== -1 && index < currentIdx)
      ? "completed"
      : index === currentIdx
        ? "current"
        : "upcoming",
  }))

  const current = steps.find((s) => s.state === "current") ?? null
  const concept = current?.concept
  const prerequisites = concept
    ? (plan?.dependencies ?? [])
        .filter((d) => d.concept_id === concept.id)
        .map((d) => concepts.find((c) => c.id === d.prerequisite_id))
        .filter((c): c is Concept => Boolean(c))
    : []

  return {
    steps,
    total: steps.length,
    completed: steps.filter((s) => s.state === "completed").length,
    current,
    isComplete,
    concept,
    prerequisites,
    objective: plan?.learning_objectives ?? null,
  }
}

export function masteryFor(states: MasteryState[], conceptId: string): MasteryState | undefined {
  return states.find((m) => m.concept_id === conceptId)
}

export function formatConceptId(id: string): string {
  return id.replace(/[_-]+/g, " ")
}
