# Sprint Backlog: Support Triage Bot

Engineering execution plan for the Support Triage Bot.

| Field | Value |
|---|---|
| Feature | Support Triage Bot |
| Requirements | `01_product_strategy/PRD_support_triage_bot.md` (PRD-2026-002) |
| Architecture | `02_tech_architecture/ARCH_support_triage_bot.md` |
| Cadence | 2-week sprints, Wednesday → Tuesday; planning Wednesday, review + retro Tuesday |
| Last Updated | 2026-09-15 |
| Owner | [Engineering Lead] |

**Assumed team:** Engineering Lead, 3 backend engineers (BE1–BE3), 1 frontend engineer (FE), 1 ML engineer (ML), 1 platform/SRE engineer (PLT), plus part-time QA analyst, Support Ops (labeling), Security, and PM. Estimates are in ideal engineering days (d); plan about 8 focus days per person per sprint. **If the team differs, re-plan Sprints 1–2 before committing to the Phase 1 date.**

---

## 1. Decisions Needed This Week

| # | Decision | Options | Recommendation | Owner | Due |
|---|---|---|---|---|---|
| DEC-1 | **Schedule:** PRD Phase 1 (shadow mode) must run 14 days and exit 2026-10-30, so the full pipeline must be live in shadow by **2026-10-16**, four and a half weeks from today. | **A.** Staggered shadow: triage shadow from 10-16 (14 days), draft shadow from 10-23 (7 days); PRD dates unchanged. **B.** Slip Phase 1 exit and pilot start by 1 week (pilot exit 12-04); GA unchanged. | **A**, with a hard checkpoint at the Sprint 2 review (10-13): if triage isn't shadow-ready, switch to **B** automatically. | PM + Eng Lead | 2026-09-18 |
| DEC-2 | Confirm Claude Haiku 4.5 / Claude Sonnet 5 in place of the retired 3.5 models | Confirm / propose alternative | Confirm; nothing else is needed for Sprint 1 | Product Owner + ML Lead (PRD OQ-1) | 2026-09-22 |
| DEC-3 | Pre-launch token budget (§4) | Approve / adjust | Approve ≈ $2,800 pre-GA cap through pilot exit (Phases 0–2 + dev/staging) | Budget owner + FinOps | 2026-09-18 |

---

## 2. Phase Milestones & Gates

| Milestone | Target Date | Gate Owner | Exit Criteria (all required) | Source |
|---|---|---|---|---|
| **M0 Foundations ready** | 2026-09-29 (end Sprint 1) | Eng Lead | API keys + hard caps in dev/staging; model readiness checks pass; schemas v2 merged; S0–S7 ingestion running on replayed fixtures; Model Client v0 passes error-matrix unit tests | ARCH §3, §6 |
| **M1 Phase 0 exit: bake-off complete** | 2026-10-09 | ML Lead | Golden set v1.0 labeled with κ targets met; bake-off hypotheses 1–3 decided; T1–T5 calibrated; §10.1 launch thresholds met on chosen routes; decision memo filed | PRD §9.3, §10.1, §17.1 |
| **M2 Shadow-ready: triage** | 2026-10-15 | Eng Lead + Security | R1/R2 + rules + routing in shadow mode; zero writes, posts, or pages verified; §6.8 chaos scenarios pass; alerts live; DPIA approved; PRD OQ-1/3/4 closed | ARCH §5, §6.8, §9.2 |
| **M3 Shadow-ready: drafts** | 2026-10-22 | ML Lead | R3–R8 in shadow; verifier guardrails pass tests; cache reads confirmed on all cached prefixes | ARCH §4.2, §5.4–§5.5 |
| **M4 Phase 1 exit: shadow complete** | 2026-10-30 | PM + ML Lead | 14 days triage shadow (7 days drafts under DEC-1 option A): online ≥ offline − 2 pts; P1 recall ≥ 98%; under-tiering ≤ 2%; R2 share ≈ 10%; cost per email within 20% of $0.031 | PRD §17.1 |
| **M5 Pilot start** | 2026-11-05 | PM + Support Ops | Sidebar app + send gating + Slack/CSM alerts live for pilot queues; training complete; every kill switch tested in production-like staging | PRD §17.1 Phase 2 |
| **M6 Phase 2 exit: pilot complete** | 2026-11-27 | PM | 21 days; no Sev-1/2; acceptance A ≥ 60%, B ≥ 50%, C ≥ 40%; alert precision ≥ 60%; agent satisfaction ≥ 4/5 | PRD §17.1 |
| **M7 Limited GA (A/B) start** | 2026-12-07 | PM + Eng Lead | All 🔒 gates closed (PRD Appendix B); queue-level flags; 10% Tier A holdout to R4 | PRD §17.1 Phase 3 |
| **M8 Phase 3 exit** | 2027-01-15 | PM + Data Science | ≥ 21 days of comparable traffic (holiday weeks excluded from analysis); §5.3 targets; guardrails hold; statistically significant handle-time gain | PRD §17.1 |
| **M9 GA** | 2027-02-01 | Product Owner | Phase 3 exit; Finance approves $2,600/month run-rate | PRD §17.1 |

---

## 3. Sprint Plan

### Sprint 1: Foundations & Ingestion (2026-09-16 → 2026-09-29)

**Sprint goal:** An email replayed from a fixture flows through S0–S7 into a `NormalizedEmail`. The Model Client can call both models with deadlines and classified errors. The bake-off harness and golden-set labeling are underway.

| ID | Task | Owner | Est. | Depends On | Acceptance Criteria | ARCH / PRD Ref |
|---|---|---|---|---|---|---|
| BOT-001 | Service skeleton, CI pipeline, dev/staging environments | PLT | 2d | — | Deploys to dev and staging from main; CI runs unit tests and lint | — |
| BOT-002 | Claude API keys per environment in model gateway; one API workspace per environment; hard caps set (§4.1) | PLT | 1d | DEC-3 | Dev and staging calls succeed through gateway only; direct provider egress blocked; caps enforced | ARCH §8.3 |
| BOT-003 | Model catalog + readiness check for `claude-haiku-4-5`, `claude-sonnet-5`, `claude-opus-5` via Models API | PLT | 0.5d | BOT-002 | Worker fails readiness if any configured model is unavailable | ARCH §4.3 |
| BOT-004 | Create `02_tech_architecture/schemas/` with `normalized_email`, `triage_output`, `draft_output`, `verifier_output`, `events` (v2) + contract tests | BE1 | 2d | — | Schemas match PRD §7.2 / ARCH §3.4, §7.3; `additionalProperties: false`; tests in CI | ARCH §7.3 |
| BOT-005 | Create `02_tech_architecture/adr/` with ADR-0001 to ADR-0009 (Proposed) | Eng Lead | 1.5d | — | All nine ADRs drafted with options and consequences | ARCH §10 |
| BOT-006 | S0 webhook receiver: HMAC + timestamp verification, 7-day dedupe, `202` before processing | BE1 | 2d | BOT-001 | Duplicate, bad-signature, and out-of-order events pass tests | ARCH §3.2 |
| BOT-007 | S1 fetch (ordered per ticket) + S2 message type + S2F forward unwrap | BE2 | 3d | BOT-006 | Auto-reply/bounce/list precision ≥ 99% on 1,000 historical emails | ARCH §3.2 |
| BOT-008 | S3 normalization: HTML → text, quote/signature/**disclaimer** stripping | BE2 | 3d | BOT-007 | Fixture suite of 1,000 corporate emails; ≤ 2% need manual correction | ARCH §3.2 |
| BOT-009 | S4 masker incl. `[CC_EMAIL]`; failure → `rules_only` | BE3 | 3d | BOT-001 | Seeded recall ≥ 99.5% per token type; masker exception test routes `rules_only` | ARCH §3.2 |
| BOT-010 | S5 authentication parsing + S6 account resolver + S7 facts + CRM domain cache | BE3 | 4d | CRM service account; OQ-A5 lists | Resolver ≥ 97% correct on 1,000 labeled emails; 0 wrong high-confidence matches | ARCH §3.3 |
| BOT-011 | **Model Client v0**: SDK `max_retries = 0`, per-attempt timeouts, route deadlines, error classification (§6.3/§6.4), usage recording, `request_id` capture | BE1 | 4d | BOT-002 | Unit tests cover every §6.3 status and §6.4 `stop_reason` row | ARCH §6.1–§6.4 |
| BOT-012 | Fault-injecting model proxy for tests and staging (status codes, `retry-after`, latency, `stop_reason`, malformed JSON) | PLT | 2d | BOT-002 | Proxy scenarios configurable per model and route | ARCH §6.8 |
| BOT-013 | Golden set labeling tool + guide (category, priority, tier, account) | ML | 2d | — | Support Ops labeling starts by 09-21 | PRD §10.1 |
| BOT-014 | Support Ops labeling: 2,000 triage emails (tier + account labels), 600 drafting cases, double-labeled subset for κ | Support Ops | ~80 agent-hrs | BOT-013 | 50% done by 09-29; 100% and κ computed by 10-05 | PRD §10.1 |
| BOT-015 | Bake-off harness: fixture replay through candidate bundles; quality runs via Message Batches; judge submission | ML | 3d | BOT-004, BOT-011 | Dry run on 50 emails produces scored report and cost | ARCH §9.3 |
| BOT-016 | Prompts `triage@1` and `draft_a@1` + CI check: Haiku prefixes ≥ 4,300 tokens (token-counting endpoint) | ML | 2.5d | BOT-002 | CI fails a prompt under threshold; counts recorded in registry | ARCH §4.2 |
| BOT-017 | Trace spans + event envelope (`events.v2`) | PLT | 1.5d | BOT-004 | Spans visible end to end on replayed email | ARCH §9.2 |
| BOT-018 | Threat model workshop + DPIA technical inputs | Security + Eng Lead | 1d | — | Threat model draft filed; DPIA inputs sent to Privacy | PRD §12 |

### Sprint 2: Routing, Resilience & Bake-off (2026-09-30 → 2026-10-13)

**Sprint goal:** Triage runs end to end in shadow mode, with R1/R2, rules, routing, breakers, and budgets. The Phase 0 bake-off exits on 10-09. Draft routes run in staging.

| ID | Task | Owner | Est. | Depends On | Acceptance Criteria | ARCH / PRD Ref |
|---|---|---|---|---|---|---|
| BOT-020 | S8 pre-filter (P0–P8) + S9 sizing + S10 emit | BE2 | 2d | BOT-010 | Each path condition unit-tested in order | ARCH §5.1 |
| BOT-021 | Triage Router: R1, escalation T1–T7, skip K1–K4, merge rules, low-confidence handling | BE1 | 3d | BOT-011, BOT-016 | Table-driven tests for every T/K row and merge field | ARCH §5.2 |
| BOT-022 | Rules & Tier Engine: Tier D/C/B floors, Tier A eligibility, priority floors | BE3 | 3d | BOT-004 | Property test: rules never lower priority or tier; 100% of 250 unit cases | ARCH §5.3 |
| BOT-023 | Router: queue map, label writes, reconciliation job, shadow store writes | BE2 | 2d | BOT-022 | Shadow mode produces zero helpdesk writes (verified by audit log) | ARCH §5.7, §6.7 |
| BOT-024 | Index macros + policy/SLA clauses with tier and SLA filters; Tier D templates by ID | ML + PLT | 3d | Policy clause library tagged (Support Ops + Legal) | Retrieval filters return only applicable, in-effect clauses on test accounts | ARCH §3.5 |
| BOT-025 | Draft Router: R3/R4/R5/R6 with per-tier fallback chains and deadlines; `draft_bc@1` prompt | BE1 + ML | 5d | BOT-021, BOT-024 | Fault-proxy tests walk every chain in ARCH §6.5 to its non-model end | ARCH §5.4, §6.5 |
| BOT-026 | Verifier R7/R8 + deterministic guardrails + release/withhold thresholds | BE3 | 3d | BOT-025 | Tests for each §5.5 row, including senior-review fallback | ARCH §5.5 |
| BOT-027 | Circuit breakers per model × route class; adaptive concurrency on `429` | BE2 | 2d | BOT-011 | Breaker open/half-open/close and immediate-open cases tested | ARCH §6.2, §6.6 |
| BOT-028 | Budget Controller integration: route budgets, atomic reservations, fail-closed, §5.6 budget-driven routing | PLT | 3d | BOT-002 | Staging tests hit each threshold; controller outage → fail closed | ARCH §5.6, §8 |
| BOT-029 | Shadow run mode + shadow store + nightly join with human labels | BE2 | 2d | BOT-023 | Shadow report generated from staging replay | ARCH §9.3 |
| BOT-030 | **Bake-off runs** (≤ 5 iterations), threshold calibration, decision memo | ML | 5d | BOT-014, BOT-015 | M1 criteria met by 10-09; spend ≤ Phase 0 cap | PRD §9.3 |
| BOT-031 | Fault-proxy test suite for all §6.3/§6.4 rows in CI | BE3 + QA | 2d | BOT-012, BOT-027 | Suite blocks merges on failure | ARCH §6.3–§6.4 |
| BOT-032 | Alerts + dashboards v0: route mix, errors by status, breakers, latency, cost per route/tier, cache-read share | PLT | 2d | BOT-017 | All ARCH §9.2 alerts fire in staging tests | ARCH §9.2 |
| BOT-033 | Chaos scenarios (ARCH §6.8 table) in staging | PLT + QA | 2d | BOT-012, BOT-028 | All eight scenarios pass; results filed | ARCH §6.8 |
| BOT-034 | Backlog re-triage job (live API, rate-capped, raise-only) | BE3 | 1.5d | BOT-021 | Simulated 2-hr outage backlog cleared ≤ 30 min in staging | ARCH §6.8 |

**Sprint 2 review checkpoint (10-13):** go/no-go for M2 on 10-15. If no-go, DEC-1 switches to option B.

### Sprint 3: Shadow Mode & Agent Surfaces (2026-10-14 → 2026-10-27)

**Sprint goal:** Triage shadow runs from 10-16 and draft shadow from 10-23. The sidebar app and Slack alerts are built for the pilot.

| ID | Task | Owner | Est. | Depends On | Acceptance Criteria |
|---|---|---|---|---|---|
| BOT-040 | Launch triage shadow on all support mailboxes (M2) | Eng Lead | 0.5d | M2 gate | Shadow running; daily metrics report |
| BOT-041 | Launch draft shadow (M3); verify cache reads across Sonnet effort levels (OQ-A2) | ML + PLT | 1d | BOT-025, BOT-026 | Cache-read share ≥ 70% per prefix, or ADR-0008 revised |
| BOT-042 | Daily shadow review: P1 recall, under-tiering, R2 share, cost per email | ML + QA | 0.5d/day | BOT-029 | Issues triaged within 24 hrs |
| BOT-043 | Alert Manager + Slack app: channels, threading, digest, incident clustering, Claim/Not urgent, unclaimed → page | BE2 | 5d | Slack app approval | End-to-end tests in pilot channel |
| BOT-044 | CSM DMs with opt-out (PRD OQ-7) | BE2 | 1d | BOT-043 | DM sent only when mapping exists and opted in |
| BOT-045 | Sidebar app: assist payload, tier badge, account panel, overrides, feedback | FE | 6d | BOT-004 | Design-approved; WCAG 2.2 AA checks pass |
| BOT-046 | Send gating on unconfirmed commitments (OQ-A3) | FE + BE1 | 3d | OQ-A3 answer (09-30) | Send is impossible with unconfirmed commitments |
| BOT-047 | R9 Regenerate + R10 Upgrade (SSE) with per-agent limits | BE1 | 3d | BOT-025 | Streaming works; limits enforced; previous draft kept on failure |
| BOT-048 | Red-team, fairness, and contract-language suites in CI | ML | 3d | BOT-030 | Suites block releases on critical failures |
| BOT-049 | Kill switches (all PRD §11.2 flags) + ops console for breakers | BE3 | 2d | BOT-027 | Each flag verified to disable its feature in ≤ 5 min |

### Sprint 4: Shadow Exit & Pilot Launch (2026-10-28 → 2026-11-10)

| ID | Task | Owner | Acceptance Criteria |
|---|---|---|---|
| BOT-050 | Phase 1 exit review (M4) and threshold adjustments from shadow data | PM + ML Lead | M4 criteria met; config bundle `bot@2` released through regression suite |
| BOT-051 | Pilot configuration: pilot queues, pilot Slack channels, CSM list | Support Ops + BE2 | Only pilot queues show AI output |
| BOT-052 | Agent training (25 min) + quick reference + escalation runbook | PM + Support Ops | 100% of pilot agents trained before 11-05 |
| BOT-053 | Production fault-injection rehearsal (off-hours, flags) | PLT | Rollback ≤ 5 min (flags) and ≤ 15 min (bundle) demonstrated |
| BOT-054 | Pilot launch (M5) | Eng Lead | Live 11-05; on-call rota staffed |

### Sprints 5–10: Pilot → A/B → GA (2026-11-11 → 2027-02-02)

| Sprint | Dates | Focus | Key Deliverables |
|---|---|---|---|
| 5 | 11-11 → 11-24 | Pilot operations | Weekly QA sample (50 A / 75 B / 75 C); prompt and threshold iterations via config bundles; dashboards v1 |
| 6 | 11-25 → 12-08 | Pilot exit (M6, 11-27) + A/B readiness | Queue-level flags; 10% Tier A holdout to R4; all 🔒 gates closed; M7 on 12-07 |
| 7 | 12-09 → 12-22 | Limited GA (A/B) | Daily guardrail monitoring; capacity check against rate limits at 50% traffic |
| 8 | 12-23 → 01-05 | Holiday: reduced staffing | Change freeze except fixes; holiday weeks excluded from A/B analysis |
| 9 | 01-06 → 01-19 | A/B completion (M8, 01-15) | Experiment readout; GA readiness review; Finance run-rate approval |
| 10 | 01-20 → 02-02 | GA (M9, 02-01) | 100% rollout; 30-day retro scheduled (03-03) |

---

## 4. Token Budget Constraints

### 4.1 Environment & Phase Caps

Each environment uses its own API key and workspace, with caps enforced by the Budget Controller as hard stops. Estimates are at list prices as of 2026-09-15.

| Scope | Cap | Type | Estimate | Basis |
|---|---|---|---|---|
| Dev | $50 / month | Hard | < $30 | Unit and integration tests use the fault proxy or recorded fixtures; real calls limited to smoke tests |
| Staging | $150 / month | Hard | ~$100 | Chaos tests use the fault proxy; one real-model smoke load of ≤ 500 emails per sprint (~$15) |
| Phase 0 bake-off | $1,000 one-time | Hard | ~$180 per full iteration × ≤ 5 = ~$900 | 2,000 triage × Haiku + Sonnet; 600 drafting cases × 2–3 candidates; verifiers; Opus 5 judge via Batches. Quality runs via Batches cut generation cost ~50%; latency measured on a 200-email live sample. |
| Phase 1 shadow (14 days) | $900 one-time | Hard | ~$720 production traffic + ~$40 judge sampling | ~23,300 emails × $0.031 |
| Phase 2 pilot (21 days) | $400 one-time | Hard | ~$160 + regenerate/upgrade overhead | ~15% of traffic × $0.031 |
| Phase 3 A/B | $1,200 / month | Soft $1,000 / hard $1,200 | ~$770 + evals $350 | 50% of traffic |
| GA | $2,600 / month | Per PRD §16 | ~$1,540 + evals | 50,000 emails × $0.031 |
| **Pre-GA total through M6 (11-27)** | **≈ $2,800** | — | — | Phases 0–2 caps $2,300 + dev/staging ≈ $500 (2.5 months × $200). Approval requested in DEC-3. |

**No full-volume load test on real models.** A 3× burst of 4,000 emails would cost about $120 per run and gives no information that the fault proxy and a 500-email smoke test don't. Load and capacity tests run against the fault proxy at recorded latency distributions.

### 4.2 Per-Route Engineering Limits (non-negotiable)

These values are enforced in code and config. A change requires an ARCH update and a regression pass.

| Route | Model | Max Input | Max Output | Attempt Timeout | Deadline | Worst-Case Reservation |
|---|---|---|---|---|---|---|
| R1 Triage | `claude-haiku-4-5` | 17,000 | 1,024 | 10 s | 20 s | $0.0221 |
| R1 fallback / R2 escalation | `claude-sonnet-5` (`low`) | 17,000 | 2,000 | 10 s / 20 s | 20 s | $0.0540 |
| R3 Tier A | `claude-haiku-4-5` | 20,000 | 2,000 | 20 s | 45 s | $0.0300 |
| R4 Tier B | `claude-sonnet-5` (`low`) | 20,000 | 4,000 | 45 s | 70 s | $0.0800 |
| R5 Tier C | `claude-sonnet-5` (`medium`) | 24,000 | 8,000 | 90 s | 135 s | $0.1280 |
| R7 Verify A/B | `claude-haiku-4-5` | 16,000 | 512 | 10 s | 12 s | $0.0186 |
| R8 Verify C | `claude-sonnet-5` (`low`) | 16,000 | 2,000 | 20 s | 32 s | $0.0520 |

### 4.3 Engineering Rules

1. **No unbounded calls.** Every request sets `max_tokens`, a timeout, and route tags; the gateway rejects anything else.
2. **SDK retries off.** `max_retries = 0`; retries and fallbacks happen only in the Model Client.
3. **Reserve before spending.** Atomic reservation per attempt; retries, repair attempts, and fallbacks each reserve.
4. **Cache minimums in CI.** Haiku prefixes (R1, R3) must count ≥ 4,300 tokens; prompts that fall below fail CI.
5. **No dynamic content in system prompts** (timestamps, IDs, names). A cache-read share below 70% is a bug.
6. **Batches for anything nobody is waiting on:** bake-off quality runs, judge scoring, backfills. Never for outage recovery.
7. **Fixtures over live calls in tests.** Unit and integration tests use recorded responses or the fault proxy; real-model tests are tagged and run only in smoke suites.
8. **Cost visibility per PR.** Any PR changing prompts, retrieval top-k, `max_tokens`, effort, or routing thresholds includes an estimated cost-per-email delta from the bake-off harness.
9. **Budget alerts go to people.** 50/75/90/100% alerts route to the budget owner and Eng Lead for every cap in §4.1.

---

## 5. Dependencies & Blockers

| Dependency | Needed By | Owner | Status | Blocks |
|---|---|---|---|---|
| Confirm Haiku 4.5 / Sonnet 5 (PRD OQ-1) | 09-22 | Product Owner + ML Lead | Open | Nothing in Sprint 1; M1 decision memo |
| Pre-launch budget approval (DEC-3) | 09-18 | Budget owner | Open | BOT-002 caps |
| CRM service account + domain/contact data cleanup | 09-23 | Revenue Systems | Open | BOT-010 |
| Public-provider and role-address lists (ARCH OQ-A5) | 09-25 | Support Ops | Open | BOT-010 |
| Send gating feasibility in helpdesk (ARCH OQ-A3) | 09-30 | Support Tooling | Open | BOT-046 |
| Rate-limit tier per model (ARCH OQ-A1) | 10-02 | AI Platform + Procurement | Open | M2 capacity sign-off |
| Policy & SLA clause library tagged by tier | 10-02 | Support Ops + Legal | Not started | BOT-024; Tier C draft quality |
| Mail gateway authentication headers visible in helpdesk | 09-25 | IT / Email Infra | To confirm | BOT-010 (S5) |
| Golden set labeling capacity (~80 agent-hours) | 09-21 → 10-05 | Support Ops Lead | Scheduling | BOT-014, M1 |
| Customer terms / eval data use (PRD OQ-3) | 10-09 | Privacy Counsel | Open | M2 |
| Retention configuration, EU region (PRD OQ-4) | 10-16 → **needed 10-15 for M2** | Security + Procurement | Open | M2; PRD date is one day late for option A |
| DPIA approval | 10-15 | Privacy | Not started | M2 |
| Slack app approval | 10-14 | IT / Collaboration Tools | Not started | BOT-043 |

---

## 6. Risks

| Risk | Likelihood | Impact | Mitigation | Trigger to Act |
|---|---|---|---|---|
| Sprint 1–2 scope too large for the 10-16 shadow start | H | M | DEC-1 option A (staggered shadow) with automatic switch to option B | Sprint 2 review 10-13 |
| Legal/privacy approvals (OQ-3, OQ-4, DPIA) land after 10-15 | M | H | Escalate this week; ask Legal to prioritize shadow-mode scope (no customer-visible output) | Not closed by 10-09 |
| Policy clause library not ready → weak Tier C drafts | M | M | Start Tier C shadow with KB + macros only; measure `no_context` rate | Library < 50% tagged by 10-02 |
| Haiku fails Tier A bar (hypothesis 1) | M | L | Collapse Tier A to R4; cost rises to ~$0.035/email (within target) | M1 memo |
| Sonnet cache not shared across effort levels (OQ-A2) | M | L | Separate R5 prefix; ~$0.001/email more | Shadow week 1 |
| Rate limits insufficient at 3× peak | L | H | Request tier increase early (OQ-A1); adaptive concurrency; cross-model fallbacks | Any sustained 429 > 5% in shadow |
| Holiday traffic reduces A/B power | H | M | Exclude holiday weeks; extend Phase 3 to 01-15 as planned | Power check 01-06 |
| Golden set label quality below κ targets | M | H | Clarify tier definitions; adjudicate; delay M1 by ≤ 3 days rather than proceed with bad labels | κ below target on 10-05 |

---

## 7. Definition of Done

A backlog item is done when:

- [ ] Code merged with unit tests; table-driven tests for every routing or error row it touches
- [ ] Fault-proxy tests pass for any change to model calls, retries, or fallbacks
- [ ] Config changes (prompts, thresholds, rules, routing) released as a versioned bundle that passes the regression suite
- [ ] Traces, events, and metrics emitted per ARCH §9.2
- [ ] Token limits, reservations, and cost tags in place for any new model call (§4.2–§4.3)
- [ ] Shadow-mode safety verified: no writes, posts, DMs, or pages when `run_mode = shadow`
- [ ] Docs updated: ARCH section and schemas if behavior changed; runbook if on-call is affected
- [ ] Deployed to staging and demoed at sprint review
