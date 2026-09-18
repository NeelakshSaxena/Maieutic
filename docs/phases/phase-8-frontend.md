# Phase 8: Web Frontend

## Objective
To build a modern, interactive user interface that allows students to converse with the MentorAI system, view their learning plans, and track their mastery.

## Implementation Details

1. **Framework:**
   - Next.js (App Router) using TypeScript and Tailwind CSS.
   - Initialized in `apps/frontend`.

2. **UI Library:**
   - Integrated `shadcn/ui` for accessible, styled components (Cards, Buttons, Inputs, Avatars, Progress bars, Scroll Areas).

3. **Core Components:**
   - **ChatInterface:** The central messaging component. Handles user input, displays AI checkpoints, hints, and feedback. Manages loading states while waiting for the LLM to process.
   - **LearningPlanSidebar:** Displays the overarching learning goal, current plan status, and the list of generated checkpoints/sub-goals.
   - **MasteryDashboard:** Provides visual feedback on the student's mastery level for specific concepts (using progress bars).

4. **API Integration:**
   - Connected the frontend to the FastAPI backend (`http://localhost:8000`) using native fetch.
   - Environment variables (`NEXT_PUBLIC_API_URL`) govern the connection endpoint.

5. **Dockerization:**
   - Updated `next.config.ts` to output a standalone build (`output: "standalone"`).
   - Created a multi-stage `Dockerfile` to build and serve the optimized static and Node.js assets.
   - Added the frontend service to `docker-compose.yml`, exposing it on port 3000.

## Status
**Completed.** The web application is fully functional, styled, and orchestrated alongside the backend database and API layers.
