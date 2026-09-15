# 01 — Product Strategy

PRDs and product requirements for AI-powered features.

## Contents

| File | What It Is | When to Use It |
|---|---|---|
| [PRD_TEMPLATE.md](PRD_TEMPLATE.md) | Enterprise PRD template for AI/LLM features (20 sections + appendix) | Starting any new AI feature |

## Starting a New PRD

1. Copy `PRD_TEMPLATE.md` to `PRD-<YYYY>-<NNN>-<short-feature-name>.md` in this folder.
2. Replace every `[placeholder]`. Mark sections that don't apply as **N/A** with a reason.
3. Sections marked 🔒 are launch gates. See the checklist in the template's Appendix B.
4. Link the feature's architecture design (from `02_tech_architecture/`) in §9.

## Template Map

Read only the sections you need instead of loading the whole template.

| Area | Sections |
|---|---|
| Problem, users, goals, metrics | §1–§5 |
| Requirements & AI behavior spec | §6–§7 |
| Data, model selection, evaluation | §8–§10 🔒 |
| Safety, privacy & compliance | §11–§12 🔒 |
| UX, fallback UX, latency tolerances | §13–§15 🔒 |
| Cost, launch, monitoring | §16–§18 |
| Dependencies & approvals | §19–§20 |

## PRDs

| ID | Feature | Status | Owner |
|---|---|---|---|
| PRD-2026-002 | [Support Triage Bot](PRD_support_triage_bot.md): tiered Haiku 4.5 / Sonnet 5 routing matrix | Draft v0.1 (current) | [Product Owner] |
| PRD-2026-001 | [Customer Support Triage Agent](../archive/01_product_strategy/PRD_customer_support_triage.md) | Superseded by PRD-2026-002; archived 2026-09-15 | [Product Owner] |
