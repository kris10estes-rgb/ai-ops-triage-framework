# 02 — Tech Architecture

API schemas, system designs, and architecture decision records (ADRs) for AI-powered systems.

## Contents

| File | What It Is | When to Use It |
|---|---|---|
| [ARCHITECTURE_BLUEPRINT.md](ARCHITECTURE_BLUEPRINT.md) | Provider-agnostic reference architecture and design template (11 sections) | Designing any AI feature or platform component |

## Starting a New Design

1. Create `ARCH_<feature_name>.md` in this folder, using the blueprint's structure and reusing its platform components.
2. Replace every `[placeholder]` and link the design from its PRD (§9).
3. Record significant decisions as ADRs (template in blueprint §10).
4. Complete the readiness checklist in blueprint §11 before launch.

## Blueprint Map

Read only the sections you need instead of loading the whole blueprint.

| Area | Sections |
|---|---|
| Principles & system overview | §1–§2 |
| Data pipelines & context ingestion strategies | §3 |
| LLM context strategy (allocation, RAG, memory, caching, overflow) | §4 |
| Token budget controls & strict enforcement rules | §5 |
| Reliability, security, observability | §6–§8 |
| Evaluation infrastructure, ADRs, readiness checklist | §9–§11 |

## Designs & Decisions

| Type | Location | Status |
|---|---|---|
| Feature designs | [ARCH_support_triage_bot.md](ARCH_support_triage_bot.md): email ingestion & account resolution (§3), Haiku vs. Sonnet routing thresholds (§5), API error handling & fallbacks (§6), budgets (§8) | **Draft (current)**, for PRD-2026-002 |
| Archived designs | [archive/02_tech_architecture/ARCH_customer_support_triage.md](../archive/02_tech_architecture/ARCH_customer_support_triage.md) | Superseded by `ARCH_support_triage_bot.md`; archived 2026-09-15 |
| API & tool schemas | `schemas/` | *Not created yet* |
| Architecture decision records | `adr/` | *Not created yet* |
