# AI Software Company Platform Roadmap

This roadmap turns the current `ai-software-company` prototype into a usable multi-agent platform for teams, shared agents, and safe AI-driven execution.

## Current state

The repository already contains a strong conceptual foundation:

- multi-agent workflow with LangGraph-like orchestration
- CEO / researcher / architect / developer / QA flow
- Redis-based episodic memory
- Chroma-based semantic memory
- Docker sandbox model
- local Ollama integration
- release and workflow orchestration primitives

However, it is still a prototype. The next work should focus on making the system reliable, multi-user, model-flexible, and safe.

---

## Strategic direction

The product direction is not just "AI agents write code". The real product is:

- a shared AI workforce
- dynamic task orchestration
- provider-agnostic model access
- team/project memory
- safe execution with approvals
- reusable agents and tools
- observability and evaluation

---

## Roadmap overview

### Phase 0: Stabilize the foundation

Goal: make the current repo reliable and testable.

Planned work:
- finalize `.env.example` and environment validation
- add startup health checks for Redis, Ollama, Docker, ChromaDB
- standardize logging and error handling
- add unit tests for:
  - state transitions in the graph
  - memory save/load behavior
  - sandbox execution failures
  - model routing selection
- add a `make` or script-based startup flow for local development
- document exact prerequisites and setup reproducibility

Deliverables:
- one-command local startup
- deterministic setup instructions
- simple CI smoke tests

Definition of done:
- a developer can clone, install, start services, and run a sample workflow with minimal friction

---

### Phase 1: Model Gateway and Provider Routing

Goal: support multiple AI providers and dynamic model selection.

Planned work:
- introduce a provider abstraction layer:
  - Ollama
  - OpenAI
  - Anthropic
  - Gemini
  - Azure OpenAI
- add model routing by task type:
  - research = web + reasoning model
  - architecture = high reasoning model
  - coding = coding-specialized model
  - QA = strict evaluator model
- add per-user and per-team model quotas
- add failover logic when a provider is unavailable
- add cost tracking and usage attribution

Deliverables:
- `app/providers/` module with common interface
- `app/router.py` for task-to-model selection
- usage and quota tracking data model

Definition of done:
- routing policy chooses the correct model automatically
- cost and usage is visible per project/user
- failures fail over safely without system outage

---

### Phase 2: Multi-user platform and task lifecycle

Goal: move from a demo script to a platform with real task ownership.

Planned work:
- add `User`, `Team`, `Project`, `Task`, `Session`, and `AuditLog` models
- add async execution via a task queue (Celery/RQ/Arq or equivalent)
- persist: task state, status, request metadata, results, errors, agent history
- support cancellation, retries, and status polling
- add historical audit trails for every tool call and decision
- add project-level runtime configuration and secrets isolation

Deliverables:
- project workspace abstraction
- task queue + worker lifecycle
- full execution history for each run

Definition of done:
- one user can create a project, start a task, get progress updates, and review results
- every run is traceable and reviewable

---

### Phase 3: Shared Agent Registry and Tool Marketplace

Goal: turn static agent roles into reusable, configurable agent entities.

Planned work:
- add an agent registry with metadata:
  - name
  - role
  - capabilities
  - model preference
  - permissions
  - tools
  - trust score
  - owner
  - visibility
- support shared, team-owned, and private agents
- implement a capability-matching layer for task routing
- allow agents to be forked and modified by other users
- define a standard tool interface with input/output schemas

Deliverables:
- `app/agents/registry.py`
- `app/tools/` abstraction layer
- `agent cards` schema and metadata serialization

Definition of done:
- the orchestrator can dynamically select the best available specialized agent for a task
- users can share reusable agents across teams

---

### Phase 4: Safe execution, approvals, and sandbox hardening

Goal: ensure the platform is safe enough for real use.

Planned work:
- add execution policy engine:
  - allowed commands
  - read-only vs write mode
  - max runtime
  - network restrictions
  - resource quotas
- add human review gates before:
  - repo mutation
  - infrastructure changes
  - deployment actions
  - external API calls with side effects
- improve sandbox isolation and artifact cleanup
- support explicit approval states and notifications

Deliverables:
- safe tool execution policy manager
- approval workflow UI/API integration
- action trace and policy logs

Definition of done:
- dangerous actions require approval
- the platform enforces isolation and resource limits
- risky workflows can be reviewed before execution

---

### Phase 5: Multi-tier memory and learning loops

Goal: make the system improve from real experience.

Planned work:
- separate memory types:
  - session memory
  - project/team memory
  - global lessons memory
  - agent performance memory
- store not just chat text but also:
  - what failed
  - what worked
  - which prompts were effective
  - which model/provider succeeded best
- add a lesson ranking system for task similarity
- add procedural memory for workflow optimization
- add prompt and orchestration tuning based on past runs

Deliverables:
- advanced memory management layer
- semantic retrieval for similar tasks
- working knowledge graph or lesson store

Definition of done:
- repeated task patterns produce reusable lessons
- the system improves over time without manual intervention

---

### Phase 6: Observability, evaluation, and production quality

Goal: make the platform measurable and enterprise-ready.

Planned work:
- integrate tracing and observability:
  - OpenTelemetry
  - Langfuse or Arize Phoenix
  - per-step execution logs
- add cost and token dashboards
- add evaluation framework:
  - code correctness checks
  - lint/test execution
  - security scanning
  - regression prompt evaluation
- add benchmarks for agent performance and reliability

Deliverables:
- tracing + metrics dashboards
- automated evaluation harness
- runner-level telemetry collection

Definition of done:
- a task can be replayed, benchmarked, and analyzed in detail
- model/provider performance is visible and measurable

---

### Phase 7: Enterprise controls and governance

Goal: prepare the platform for real teams and sensitive workloads.

Planned work:
- RBAC and organization-level policies
- DLP and secret redaction for prompts and tool calls
- audit logging for all tool actions and agent decisions
- access restrictions for external tools and data sources
- tenant isolation and resource limits
- governance dashboards for compliance and usage

Deliverables:
- role-based governance system
- audit trail and compliance layer
- tenant-safe execution boundaries

Definition of done:
- operations teams can track activity, enforce policy, and audit changes

---

### Phase 8: Productization and UI

Goal: turn the system into a usable product.

Planned work:
- dashboard for tasks, agents, memory, and model performance
- project view with workflows and sessions
- marketplace UI for agent discovery and sharing
- API layer for external integration
- webhook support and event stream consumers

Deliverables:
- frontend or admin dashboard
- task board and agent registry UI
- API / webhook surface

Definition of done:
- non-engineering users can launch tasks, review outputs, and manage agents

---

## Recommended implementation order

If we want the fastest value with the least risk, the first milestone order should be:

1. Phase 0: foundation stabilization
2. Phase 1: multi-provider model gateway
3. Phase 2: multi-user task lifecycle
4. Phase 3: shared agent registry
5. Phase 4: sandbox safety and approvals
6. Phase 5: memory and learning layer
7. Phase 6: observability and evaluation
8. Phase 7: governance
9. Phase 8: product UI

This is the best sequence for this repository because it follows the architecture already present today.

---

## Immediate next actions (first sprint)

The following should be the first concrete implementation tasks:

- [ ] create a robust service health check script
- [ ] validate `docker-compose.yml` against the app entrypoints
- [ ] add `app/providers/` abstraction for Ollama and a generic LLM client
- [ ] add `app/router.py` for model selection by task type
- [ ] add `app/task_queue.py` for async execution
- [ ] add `app/models/` for `User`, `Team`, `Project`, `Task`, `Session`
- [ ] add `app/agent_registry.py` with `AgentSpec` metadata
- [ ] create a simple `roadmap.md` / backlog to track these steps

---

## Product thesis

This repo should evolve from a single-user AI demo into a platform where:

- many users can run tasks
- many agents can collaborate
- providers can be swapped dynamically
- memory improves learning over time
- tasks are auditable and safe
- agent capabilities can be shared and reused

That is the real differentiator for the project.

---

## Summary

The best short version of the strategy is:

- make the system reliable
- make it multi-user
- make it model-flexible
- make it agent-shareable
- make it safe and observable

Once those are in place, the repository becomes a real AI software company platform instead of a prototype.
