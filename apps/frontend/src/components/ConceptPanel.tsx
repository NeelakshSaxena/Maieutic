"use client"

import { ChevronDownIcon, TargetIcon } from "lucide-react"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import type { LearningPlan } from "@/lib/api"
import type { Progress } from "@/lib/learning"

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-1.5">
      <h3 className="text-xs font-medium tracking-wide text-muted-foreground uppercase">{title}</h3>
      {children}
    </section>
  )
}

export function ConceptPanel({ progress, plan }: { progress: Progress; plan: LearningPlan | null }) {
  if (!plan || progress.total === 0) {
    return (
      <p className="rounded-lg border border-dashed p-4 text-sm text-muted-foreground">
        Concept details appear here once your plan has been created.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-5">
      {progress.objective && (
        <Section title="Learning objective">
          <p className="text-sm leading-relaxed">{progress.objective}</p>
        </Section>
      )}

      {progress.concept ? (
        <>
          <Section title="Current concept">
            <p className="text-sm font-medium">{progress.concept.name}</p>
            <p className="text-sm leading-relaxed text-muted-foreground">{progress.concept.description}</p>
          </Section>
          <Section title="Prerequisites">
            {progress.prerequisites.length > 0 ? (
              <ul className="flex flex-col gap-1 text-sm">
                {progress.prerequisites.map((p) => (
                  <li key={p.id}>{p.name}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">None listed for this concept.</p>
            )}
          </Section>
        </>
      ) : (
        <p className="text-sm text-muted-foreground">
          {progress.isComplete ? "Every concept in this plan has been verified." : "No current concept."}
        </p>
      )}

      {progress.current && (
        <Section title="Current task">
          <div className="flex gap-2 rounded-lg border border-primary/30 bg-accent/50 p-3">
            <TargetIcon className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
            <p className="text-sm leading-relaxed">{progress.current.checkpoint.task}</p>
          </div>
        </Section>
      )}

      <Section title="All concepts in this plan">
        <ul className="flex flex-col gap-2">
          {plan.concepts.map((c) => {
            const prereqs = plan.dependencies
              .filter((d) => d.concept_id === c.id)
              .map((d) => plan.concepts.find((x) => x.id === d.prerequisite_id)?.name)
              .filter(Boolean)
            const isCurrent = c.id === progress.concept?.id
            return (
              <li key={c.id}>
                <Collapsible>
                  <CollapsibleTrigger className="group flex w-full items-center justify-between gap-2 rounded-lg border bg-card px-3 py-2 text-left text-sm outline-none transition-colors hover:bg-muted focus-visible:ring-3 focus-visible:ring-ring/50">
                    <span className="truncate font-medium">
                      {c.name}
                      {isCurrent && <span className="ml-2 text-xs font-normal text-primary">current</span>}
                    </span>
                    <ChevronDownIcon className="size-4 shrink-0 text-muted-foreground transition-transform group-aria-expanded:rotate-180" aria-hidden="true" />
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <div className="flex flex-col gap-1.5 px-1 pt-2 text-sm">
                      <p className="leading-relaxed text-muted-foreground">{c.description}</p>
                      {prereqs.length > 0 && <p className="text-xs">Builds on: {prereqs.join(", ")}</p>}
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </li>
            )
          })}
        </ul>
      </Section>
    </div>
  )
}
