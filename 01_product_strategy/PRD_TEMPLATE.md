# PRD Template: AI / LLM Features

An enterprise PRD template for AI-powered features. It covers model selection, fallback UX, latency tolerances, evaluation, safety, and cost.

**How to use this template**

1. Copy everything below the line into a new file named `PRD-<YYYY>-<NNN>-<short-feature-name>.md`.
2. Replace every `[placeholder]`. If a section doesn't apply, write **N/A** and give a one-line reason. Don't delete it.
3. Anything marked 🔒 is a **launch gate**: it must be done and signed off before the feature goes to general availability (GA).
4. Put technical design details in `02_tech_architecture/` and link to them from Section 9.

---

# PRD: [Feature Name]

## 0. Document Control

| Field | Value |
|---|---|
| PRD ID | PRD-[YYYY]-[NNN] |
| Status | Draft · In Review · Approved · In Build · Launched · Deprecated |
| Version | [0.1] |
| Product Owner | [Name, role] |
| Engineering Lead | [Name, role] |
| ML / AI Lead | [Name, role] |
| Design Lead | [Name, role] |
| Trust & Safety / Legal | [Name, role] |
| Created / Last Updated | [YYYY-MM-DD] / [YYYY-MM-DD] |
| Target Launch | [Quarter or date] |
| Related Docs | [Architecture doc] · [Eval plan] · [Research] · [Jira epic] |

### Change Log

| Version | Date | Author | Summary of Changes |
|---|---|---|---|
| 0.1 | [YYYY-MM-DD] | [Name] | Initial draft |

---

## 1. Executive Summary

> 3–5 sentences. Say what we're building, who it's for, what problem it solves, why now, and the single most important success metric.

[Summary]

---

## 2. Problem & Opportunity

### 2.1 Problem Statement
[Describe the user or business problem in plain language. Leave the solution out of this section.]

### 2.2 Evidence
| Source | Finding | Link |
|---|---|---|
| User research | [e.g., 7 of 10 interviewees spend over 2 hrs/week on X] | [link] |
| Product analytics | [e.g., 38% drop-off at step Y] | [link] |
| Support tickets | [e.g., 1,200 tickets/month tagged Z] | [link] |
| Market / competitive | [e.g., competitor A shipped similar capability] | [link] |

### 2.3 Opportunity Sizing
- **Addressable users:** [#]
- **Expected impact:** [e.g., hours saved, conversion lift, cost reduction]
- **Strategic alignment:** [Company OKR / pillar this supports]

### 2.4 Why Now?
[Triggers such as new model capabilities, customer demand, competitive pressure, or a cost inflection point.]

---

## 3. AI Fit Assessment 🔒

> Show that AI is the right tool for this problem. If a deterministic solution would work, write that down here.

| Question | Answer |
|---|---|
| Could rules, search, or standard software solve this well enough? | [Yes/No + reasoning] |
| Does the task tolerate probabilistic or imperfect output? | [Yes/No + reasoning] |
| What does a wrong answer cost? (Low / Medium / High / Critical) | [Rating + example] |
| Is a human in the loop before output has real-world effect? | [Yes/No/Partial] |
| Do we have (or can we get) data to ground and evaluate the system? | [Yes/No + source] |
| Does unit economics work at projected scale? (see §16) | [Yes/No/TBD] |

**AI Pattern:** ☐ Generation ☐ Summarization ☐ Extraction / Classification ☐ Retrieval-Augmented Q&A ☐ Conversational Assistant ☐ Agentic / Tool-Using Workflow ☐ Recommendation ☐ Other: [ ]

**Autonomy Level:**
- ☐ **L1 – Suggest:** AI drafts, and a human decides and acts.
- ☐ **L2 – Assist:** AI acts only after explicit human approval.
- ☐ **L3 – Automate with oversight:** AI acts on its own, and humans audit and can reverse.
- ☐ **L4 – Fully autonomous:** needs executive and Trust & Safety sign-off.

---

## 4. Users & Use Cases

### 4.1 Target Personas
| Persona | Description | Primary Job-to-be-Done | AI Literacy (Low/Med/High) |
|---|---|---|---|
| [Persona A] | [Role, context] | [JTBD] | [ ] |

### 4.2 Core Use Cases
| ID | Use Case | Persona | Frequency | Priority |
|---|---|---|---|---|
| UC-01 | [Description] | [ ] | [Daily/Weekly] | P0 |
| UC-02 | [Description] | [ ] | [ ] | P1 |

### 4.3 Explicitly Unsupported Use Cases
[Uses we won't design for or will actively block, e.g., medical diagnosis or legal advice.]

---

## 5. Goals, Non-Goals & Success Metrics

### 5.1 Goals
1. [Goal]
2. [Goal]

### 5.2 Non-Goals
1. [What this release will deliberately not do]

### 5.3 Success Metrics 🔒

| Category | Metric | Baseline | Target | Measurement Method |
|---|---|---|---|---|
| **North Star** | [e.g., Tasks completed with AI assist / week] | [ ] | [ ] | [Analytics event] |
| **Adoption** | [e.g., % of eligible users who try the feature in 30 days] | [ ] | [ ] | [ ] |
| **Engagement** | [e.g., Suggestion acceptance rate] | [ ] | [ ] | [ ] |
| **Quality (offline)** | [e.g., Eval pass rate on golden set] | [ ] | [≥ X%] | [Eval harness] |
| **Quality (online)** | [e.g., Thumbs-up ratio, edit distance on accepted output] | [ ] | [ ] | [ ] |
| **Business** | [e.g., Support ticket deflection, revenue] | [ ] | [ ] | [ ] |
| **Efficiency** | [e.g., Cost per successful task] | — | [≤ $X] | [Token metering] |
| **Performance** | [e.g., p95 time-to-first-token] | — | [Per §15.1 tolerance] | [APM / RUM] |

### 5.4 Guardrail Metrics (must not regress)
| Metric | Threshold | Action if Breached |
|---|---|---|
| Harmful / policy-violating output rate | [≤ X%] | [Auto-disable via feature flag] |
| Hallucination / factual error rate | [≤ X%] | [Rollback to previous prompt/model] |
| Core product conversion / retention | [No stat-sig drop] | [Pause rollout] |
| Cost per day | [≤ $X] | [Throttle / degrade — see §16] |

---

## 6. Functional Requirements

### 6.1 User Stories
| ID | As a… | I want to… | So that… | Acceptance Criteria | Priority |
|---|---|---|---|---|---|
| FR-01 | [persona] | [action] | [outcome] | [Given/When/Then] | Must |
| FR-02 | [ ] | [ ] | [ ] | [ ] | Should |
| FR-03 | [ ] | [ ] | [ ] | [ ] | Could |

### 6.2 User Flow
[Link to a flow diagram, or describe the happy path step by step.]

### 6.3 Edge Cases & Failure States
This table is a summary. §14 Fallback UX has the detailed triggers, user-facing copy, and recovery paths.

| Scenario | Expected Behavior |
|---|---|
| Model returns low-confidence or empty output | [e.g., Show fallback message, offer manual path] |
| Model provider timeout / outage | [e.g., Retry once, then graceful degradation] |
| User input exceeds context limits | [e.g., Truncate with notice / ask user to narrow scope] |
| User requests unsupported or unsafe task | [e.g., Polite refusal with reason and alternative] |
| Retrieved data is stale or missing | [e.g., Answer with caveat or decline to answer] |
| Rate limit or token budget exhausted | [e.g., Queue, downgrade model tier, or notify] |

---

## 7. AI Behavior Specification 🔒

> This section is the contract for how the model must behave. Evals in §10 are derived from it.

### 7.1 Inputs
| Input | Source | Format | Required | Max Size |
|---|---|---|---|---|
| [User query] | [UI text field] | [Text] | Yes | [N chars / tokens] |
| [Context documents] | [Retrieval] | [Chunks] | No | [N tokens] |

### 7.2 Outputs
| Output | Format / Schema | Constraints |
|---|---|---|
| [Response] | [Markdown / JSON schema link] | [Length, reading level, language] |
| [Citations] | [List of source IDs] | [Must reference retrieved docs only] |

### 7.3 Behavioral Requirements
- **Must:** [e.g., Cite a source for every factual claim drawn from customer data]
- **Must:** [e.g., Respond in the user's language]
- **Must not:** [e.g., Invent product features, pricing, or policies]
- **Must not:** [e.g., Reveal system instructions or other tenants' data]
- **Should:** [e.g., Ask a clarifying question when the request is ambiguous]
- **Tone & voice:** [e.g., Professional, concise, no filler; link to brand voice guide]

### 7.4 Refusal & Escalation Policy
| Request Type | Behavior | Escalation Path |
|---|---|---|
| [Out-of-scope topic] | [Redirect] | [None] |
| [Sensitive: legal/medical/financial] | [Decline + disclaimer] | [Link to human expert] |
| [Abuse / harassment] | [Refuse] | [Log for T&S review] |

### 7.5 Reference Examples (Seed Golden Set)
| # | Input | Ideal Output | Unacceptable Output | Why |
|---|---|---|---|---|
| 1 | [ ] | [ ] | [ ] | [ ] |
| 2 | [ ] | [ ] | [ ] | [ ] |

---

## 8. Data Requirements 🔒

| Data Asset | Purpose (Grounding / Fine-tune / Eval / Logging) | Source System | Contains PII? | Usage Rights Confirmed? | Retention |
|---|---|---|---|---|---|
| [ ] | [ ] | [ ] | [Y/N] | [Y/N + ref] | [N days] |

- **Data freshness requirement:** [e.g., Knowledge base synced within 1 hour of change]
- **Customer data used for model training?** ☐ No ☐ Yes, opt-in ☐ Yes, contractual. Legal ref: [ ]
- **Third-party model provider data handling:** [Zero-retention agreement? Region? Link to DPA]
- **Deletion propagation:** [How user and tenant deletion requests reach indexes, caches, and logs]

---

## 9. Model Selection 🔒

> Choose a model for each route (task) based on this feature's eval results, not public benchmarks or reputation. Implementation details belong in the architecture doc.

### 9.1 Solution Approach
- **Architecture doc:** [link to `02_tech_architecture/...`]
- **Approach:** ☐ Prompted foundation model ☐ RAG ☐ Fine-tuned model ☐ Agent with tools ☐ Hybrid
- **Build vs. buy rationale:** [ ]
- **Key tools/integrations the AI can access:** [List, with read vs. write permissions]

### 9.2 Selection Criteria & Weights
| Criterion | Weight | How Measured | Minimum Bar |
|---|---|---|---|
| Task quality | [35%] | Golden-set and groundedness pass rate (§10.1) | [≥ X%] |
| Safety & policy adherence | [15%] | Red-team and refusal-policy suites (§10.1) | [0 critical failures] |
| Latency | [15%] | TTFT and end-to-end p95 on production-sized prompts | [Within §15.1 tolerance] |
| Cost | [15%] | Cost per successful task (§16) | [≤ $X] |
| Capabilities | [10%] | Tool use, structured output, vision, languages, reasoning controls | [Required features present] |
| Context fit | [10%] | p99 assembled prompt + reserved output fits the context limit with margin | [Pass] |
| Data handling & compliance | Gate | Retention terms, region availability, DPA, certifications (§8, §12) | [Pass, or model is excluded] |
| Vendor viability | Gate | SLA, rate-limit headroom, deprecation policy, support | [Pass, or model is excluded] |

### 9.3 Candidate Comparison
| Candidate (model @ version) | Hosting (API / cloud / self-hosted, region) | Quality | Safety | TTFT p95 | E2E p95 | Cost / Task | Context Fit | Gates | Weighted Score |
|---|---|---|---|---|---|---|---|---|---|
| [Model A @ ver] | [ ] | [ %] | [ ] | [ ms] | [ s] | [$ ] | [✓/✗] | [✓/✗] | [ ] |
| [Model B @ ver] | [ ] | [ %] | [ ] | [ ms] | [ s] | [$ ] | [✓/✗] | [✓/✗] | [ ] |
| [Model C @ ver] | [ ] | [ %] | [ ] | [ ms] | [ s] | [$ ] | [✓/✗] | [✓/✗] | [ ] |

**Test conditions:** eval dataset version [ ], prompt version [ ], run date [ ], region [ ], concurrency [ ].

### 9.4 Route-to-Model Assignment
| Route / Task | Primary Model (pinned) | Fallback Model / Path | Rationale for Tier | Max Input / Output Tokens | Reasoning Budget |
|---|---|---|---|---|---|
| [e.g., Intent classification] | [Small tier @ ver] | [Rules-based classifier] | [ ] | [ ] / [ ] | [None] |
| [e.g., Grounded answer] | [Medium tier @ ver] | [Alternate-provider medium tier] | [ ] | [ ] / [ ] | [ ] |
| [e.g., Multi-step agent task] | [Large tier @ ver] | [Medium tier with reduced scope] | [ ] | [ ] / [ ] | [ ] |

Every fallback model must pass the same launch thresholds in §10 before it can serve traffic.

### 9.5 Customization Decision
- **Chosen level:** ☐ Prompting only ☐ Prompting + retrieval ☐ Fine-tuning ☐ Distillation to a smaller model
- **Justification:** [If customizing, show why prompting + retrieval didn't meet the §9.2 bars]
- **Training data source, rights, and refresh cadence:** [ ]

### 9.6 Model Lifecycle Policy
| Policy | Requirement |
|---|---|
| Version pinning | Production uses pinned model versions only, never floating "latest" aliases |
| Re-evaluation triggers | New model version available · provider deprecation notice · online quality drift · price change > [X]% · latency SLO breach > [7] days |
| Migration window | Migration evals start ≥ [N] days before the provider's end-of-life date |
| Switch criteria | Candidate meets every §9.2 minimum bar with no guardrail regression (§5.4) |
| Approvals | ML Lead + Product Owner; add Security and Legal if the provider or hosting changes |

---

## 10. Evaluation Plan 🔒

### 10.1 Offline Evaluation
| Eval Suite | What It Measures | Dataset (size, source) | Method | Launch Threshold |
|---|---|---|---|---|
| Golden set | Task correctness | [N examples, curated] | [Exact match / rubric / LLM-as-judge] | [≥ X%] |
| Groundedness | Claims supported by context | [N] | [LLM-as-judge + human spot check] | [≥ X%] |
| Safety / red team | Harmful output, jailbreaks, prompt injection | [N adversarial prompts] | [Automated + manual] | [0 critical failures] |
| Bias & fairness | Output parity across groups | [N paired prompts] | [Statistical comparison] | [Δ ≤ X%] |
| Regression | No degradation vs. current prod | [Full suite] | [Automated in CI] | [No stat-sig drop] |

### 10.2 Human Evaluation
- **Reviewers:** [Internal SMEs / vendor / customers]
- **Rubric:** [Link. Define 1–5 scales for accuracy, helpfulness, safety, tone]
- **Sample size & inter-rater agreement target:** [N samples, κ ≥ X]

### 10.3 Online Evaluation
- **Experiment design:** [A/B test, holdout %, minimum detectable effect, duration]
- **Implicit signals:** [Accept / edit / regenerate / abandon]
- **Explicit signals:** [Thumbs up/down, free-text feedback]

### 10.4 Change Management
Any change to a prompt, model version, retrieval config, or tool definition **must pass the full regression suite** before it's deployed.

---

## 11. Responsible AI, Trust & Safety 🔒

### 11.1 Risk Register
| ID | Risk | Likelihood (L/M/H) | Impact (L/M/H/Critical) | Mitigation | Owner | Residual Risk |
|---|---|---|---|---|---|---|
| R-01 | Hallucinated facts presented as authoritative | [ ] | [ ] | [Grounding, citations, confidence UI] | [ ] | [ ] |
| R-02 | Prompt injection via retrieved content or user input | [ ] | [ ] | [Input/output filtering, privilege separation] | [ ] | [ ] |
| R-03 | Leakage of PII or cross-tenant data | [ ] | [ ] | [Tenant-scoped retrieval, output PII scan] | [ ] | [ ] |
| R-04 | Biased or unfair outcomes | [ ] | [ ] | [Fairness evals, human review] | [ ] | [ ] |
| R-05 | Over-reliance / automation bias by users | [ ] | [ ] | [UX friction, disclosure, confidence cues] | [ ] | [ ] |
| R-06 | Agent takes unintended irreversible action | [ ] | [ ] | [Confirmation step, scoped permissions, undo] | [ ] | [ ] |

### 11.2 Safeguards
- **Input moderation:** [Tooling / policy]
- **Output moderation:** [Tooling / policy]
- **Human oversight:** [Where humans review, approve, or can override]
- **Kill switch:** [Feature flag name, who can flip it, target time-to-disable]
- **Incident response:** [Runbook link, severity definitions, on-call rotation]

---

## 12. Privacy, Security & Compliance 🔒

| Requirement | Applicable? | Notes / Evidence |
|---|---|---|
| Privacy impact assessment (PIA / DPIA) | [Y/N] | [Link] |
| Security review / threat model | [Y/N] | [Link] |
| GDPR / CCPA / other regional privacy law | [Y/N] | [ ] |
| EU AI Act risk classification | [Minimal / Limited / High / Prohibited] | [Rationale] |
| Sector regulation (HIPAA, FINRA, FERPA, etc.) | [Y/N] | [ ] |
| SOC 2 / ISO 27001 control mapping | [Y/N] | [ ] |
| Data residency requirements | [Regions] | [ ] |
| Vendor / subprocessor approval for model provider | [Y/N] | [ ] |
| Audit logging of AI inputs, outputs, and actions | [Y/N] | [Retention period] |

---

## 13. UX & Transparency Requirements

- **AI disclosure:** [How users know content is AI-generated, e.g., label or icon]
- **Explainability:** [Citations, "why am I seeing this", reasoning summary]
- **Confidence communication:** [How uncertainty is shown]
- **User control:** [Edit, regenerate, undo, opt out, report issue]
- **Feedback capture:** [Thumbs, categories, free text, and where the data goes]
- **Loading & latency UX:** see §15.3
- **Failure states:** see §14
- **Accessibility:** [WCAG 2.2 AA; screen-reader behavior for streamed content]
- **Onboarding / education:** [First-run experience, capability and limitation messaging]
- **Design artifacts:** [Figma / wireframe links]

---

## 14. Fallback UX 🔒

> Define what the user sees when the AI path is slow, wrong, unavailable, or not permitted. Every P0 use case needs a fallback that still lets the user get the job done.

### 14.1 Fallback Principles
1. **No dead ends.** Every failure state offers a next step: retry, a manual path, or a human handoff.
2. **Keep the user's work.** An AI failure never discards inputs, drafts, or partial output.
3. **Be honest, not technical.** Say what happened and what to do next in plain language. Don't show raw errors, stack traces, or provider names.
4. **Fail safe.** If an output's safety or correctness is in doubt, show less rather than more.
5. **Degrade before blocking.** Prefer a smaller model, a shorter answer, or a cached result over an error.

### 14.2 Fallback Matrix
| Trigger | Detection | Fallback Behavior | User-Facing Message (draft) | Recovery Action | Event Name |
|---|---|---|---|---|---|
| Primary model timeout | Hard timeout reached (§15.1) | Retry once on fallback model (§9.4), then non-AI path | "This is taking longer than usual. [Try again] or [do it manually]." | Retry, manual workflow | `fallback.timeout` |
| Provider outage / 5xx errors | Circuit breaker open | Route to fallback model; if that's also down, disable the AI entry point | "AI assistance is temporarily unavailable. You can still [manual action]." | Auto-restores when healthy | `fallback.outage` |
| Rate limit or budget exhausted | Token Budget Controller | Smaller tier or queue, then notice | "You've reached today's AI usage limit. It resets at [time]." | Contact admin / upgrade | `fallback.budget` |
| Low confidence or failed validation | Confidence score, schema or grounding check | Show partial result with caveat, or suppress output | "I'm not confident in this answer. Here's what I found: [sources]." | Regenerate, edit, ask a human | `fallback.low_confidence` |
| No relevant context found | Empty or below-threshold retrieval | State it plainly; don't guess | "I couldn't find this in [source]. Try rephrasing or [search manually]." | Suggested queries | `fallback.no_context` |
| Safety filter block | Input or output moderation | Refuse with a reason category and an alternative | "I can't help with that here. [Alternative / policy link]" | Report a false positive | `fallback.safety_block` |
| Input too large | Pre-flight token count | Ask the user to narrow scope, or summarize first with consent | "That's more than I can process at once. Select a section or [summarize first]." | Scope selector | `fallback.input_too_large` |
| Stream interrupted | Stream error or heartbeat loss | Keep the partial text and mark it incomplete | "The response was interrupted. [Continue] [Regenerate]" | Continue from partial | `fallback.stream_interrupted` |
| Tool / integration failure (agents) | Tool error or permission denial | Stop before further side effects; summarize what completed | "I finished steps 1–2 but couldn't [step 3]. Nothing else was changed." | Resume, undo, manual step | `fallback.tool_failure` |
| Feature disabled by kill switch | Feature flag | Hide or disable AI entry points | "[Feature] is paused while we make improvements." | None | `fallback.kill_switch` |

### 14.3 Fallback Tiers
| Tier | Experience | Typical Trigger |
|---|---|---|
| T0 – Full | Primary model, full context, full output | Normal operation |
| T1 – Degraded AI | Fallback or smaller model, reduced context, shorter output | Budget ≥ 90%, provider latency elevated |
| T2 – Cached / Static | Cached answers, pre-generated content, templates | Provider outage on repeatable queries |
| T3 – Non-AI | Manual workflow, standard search, forms | Full outage, kill switch |
| T4 – Human handoff | Route to a support agent or subject-matter expert | High-stakes request, repeated failures, user request |

### 14.4 Fallback Acceptance Criteria
- [ ] Every trigger in §14.2 has an approved design: [Figma link]
- [ ] User-facing copy reviewed by content design (and Legal where relevant)
- [ ] Fault injection in staging covers timeouts, 5xx errors, budget exhaustion, empty retrieval, and interrupted streams
- [ ] Fallback rate per trigger is instrumented and appears on the §18 dashboard
- [ ] Failure and retry states are announced to screen readers

---

## 15. Latency Tolerances & Non-Functional Requirements 🔒

> Set latency targets from what the user's task can tolerate, not from what the current model happens to achieve. Measure at p95 on production-sized prompts, from the user's device.

### 15.1 Latency Tolerance by Interaction Type
Keep the rows that apply to this feature and delete the rest. Placeholder numbers are starting points for discussion, not recommendations.

| Interaction Type | Example | TTFT p50 / p95 | Full Response p95 | Hard Timeout → Action | Streaming |
|---|---|---|---|---|---|
| Inline / keystroke | Autocomplete, inline suggestions | [≤ 150 ms / ≤ 300 ms] | [≤ 500 ms] | [1 s → silently skip] | No |
| Interactive chat | Assistant Q&A | [≤ 700 ms / ≤ 1.5 s] | [≤ 8 s] | [30 s → fallback §14.2] | Required |
| On-demand generation | Draft an email, summarize a document | [≤ 1 s / ≤ 2 s] | [≤ 15 s] | [60 s → fallback §14.2] | Required |
| Agentic multi-step | Research, multi-tool workflows | [First status update ≤ 2 s] | [≤ 2 min] | [5 min → return partial result] | Step-level progress |
| Background / async | Batch enrichment, scheduled reports | N/A | [≤ N min] | [Job SLA → retry / alert] | No; notify on completion |

### 15.2 End-to-End Latency Budget (this feature)
| Stage | p95 Budget (ms) | Notes |
|---|---|---|
| Client → API gateway | [ ] | Network, authentication |
| Input guardrails | [ ] | Moderation, PII scan |
| Retrieval + reranking | [ ] | |
| Context assembly + token counting | [ ] | |
| Model time-to-first-token | [ ] | Grows with input size; improves with prefix-cache hits |
| Generation to completion | [ ] | Grows roughly with output tokens |
| Output guardrails | [ ] | Must work incrementally if streaming |
| **User-perceived TTFT** | **[ ]** | Must meet §15.1 |
| **End-to-end total** | **[ ]** | Must meet §15.1 |

### 15.3 Perceived-Performance Requirements
- **Acknowledgement:** visible response to user action within [100 ms]
- **Streaming:** required for any response expected to take longer than [2 s]
- **Progress:** step-level status for agentic flows (e.g., "Searching docs…", "Drafting…")
- **Cancel:** users can stop generation at any time, and cancelling also stops token spend on the server
- **Skeletons / optimistic UI:** [where applicable]

### 15.4 Latency Breach Behavior
| Condition | Behavior | Owner |
|---|---|---|
| TTFT exceeds [X] s on a request | Show a "still working" state with a cancel option | Frontend |
| Hard timeout reached | Trigger the matching fallback in §14.2 | Orchestrator |
| p95 above tolerance for [15 min] | Page on-call; router may shift traffic to a faster tier | SRE / AI Platform |
| p95 above tolerance for [7 days] | Product review: revisit model choice (§9.6) or scope | Product + ML Lead |

### 15.5 Latency Levers & Trade-offs
| Lever | Typical Latency Gain | Trade-off to Evaluate |
|---|---|---|
| Faster / smaller model tier | High | Quality; re-run §10 evals |
| Lower or no reasoning budget | High | Weaker performance on complex tasks |
| Response caching | Very high on cache hits | Staleness; unsuitable for personalized answers |
| Prompt-prefix caching | Medium–high on long prompts | Constrains prompt structure |
| Less retrieved context | Medium | Recall loss |
| Shorter max output / concise style | Medium | Less detail |
| Parallel retrieval and tool calls | Medium | Engineering complexity |

### 15.6 Other Non-Functional Requirements
| Category | Requirement |
|---|---|
| Availability | [99.X]% monthly, including degraded-mode behavior (§14.3) |
| Throughput | [N] requests/min at peak; [N] concurrent sessions |
| Scalability | Support [N]× growth over [12] months without re-architecture |
| Internationalization | Languages: [list]; quality parity target: [ ]; latency parity across regions: [ ] |
| Reproducibility | Model version, prompt version, and retrieval snapshot logged per request |
| Portability | Ability to switch model providers within [N] weeks |

---

## 16. Cost & Unit Economics 🔒

| Item | Assumption | Value |
|---|---|---|
| Avg input tokens / request | [ ] | [ ] |
| Avg output tokens / request | [ ] | [ ] |
| Requests / active user / day | [ ] | [ ] |
| Blended cost / 1M tokens | [Per model tier] | [$ ] |
| Cache hit rate (prompt + response) | [ ] | [ ]% |
| **Cost per request** | | [$ ] |
| **Cost per successful task** | Cost ÷ task success rate | [$ ] |
| **Monthly cost at launch / at 12-mo scale** | | [$ ] / [$ ] |
| Revenue or savings per task | [ ] | [$ ] |
| **Gross margin impact** | | [ ]% |

- **Budget owner:** [Name / cost center]
- **Monthly budget cap:** [$ ]. Alerts at 50% / 80% / 100%.
- **Cost controls:** see `02_tech_architecture/ARCHITECTURE_BLUEPRINT.md` §5

---

## 17. Launch Plan

### 17.1 Rollout Phases
| Phase | Audience | Exposure | Entry Criteria | Exit Criteria | Date |
|---|---|---|---|---|---|
| Internal dogfood | Employees | 100% internal | Offline evals pass | [N] days, no Sev-1/2 | [ ] |
| Private beta | [N] design partners | [ ] | Dogfood exit met | Quality + CSAT targets | [ ] |
| Limited GA | [X]% of users | Feature flag | Beta exit met; 🔒 gates closed | Guardrails hold [N] days | [ ] |
| GA | All eligible | 100% | Limited GA exit met | — | [ ] |

### 17.2 Rollback Plan
[Triggers, e.g., a guardrail breach from §5.4; the mechanism (flag, model pin, prompt revert); owner; and target time to roll back.]

### 17.3 Go-to-Market
- **Pricing / packaging:** [Included / add-on / usage-based]
- **Enablement:** [Sales, support, and docs readiness]
- **Communications:** [Changelog, blog, in-app announcement]

---

## 18. Post-Launch Monitoring & Iteration

| Signal | Tool / Dashboard | Review Cadence | Owner |
|---|---|---|---|
| Quality metrics (online evals, feedback) | [ ] | Weekly | [ ] |
| Fallback rate by trigger (§14.2) | [ ] | Weekly | [ ] |
| Latency vs. tolerance (§15.1) | [ ] | Real-time alerts + weekly review | [ ] |
| Safety incidents / flagged outputs | [ ] | Daily | [ ] |
| Cost & token usage vs. budget | [ ] | Weekly | [ ] |
| Latency & error rates | [ ] | Real-time alerts | [ ] |
| Model / data drift | [ ] | Monthly | [ ] |
| Provider model deprecations | [ ] | Monthly | [ ] |

- **Feedback loop:** [How production failures become new eval cases]
- **Retrospective date:** [30 / 60 / 90 days post-GA]

---

## 19. Dependencies, Assumptions & Open Questions

### 19.1 Dependencies
| Dependency | Team / Vendor | Status | Risk if Delayed |
|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] |

### 19.2 Assumptions
1. [Assumption, and how/when we'll validate it]

### 19.3 Open Questions
| # | Question | Owner | Due | Resolution |
|---|---|---|---|---|
| 1 | [ ] | [ ] | [ ] | [ ] |

---

## 20. Approvals 🔒

| Role | Name | Decision (Approve / Approve w/ conditions / Reject) | Date | Conditions |
|---|---|---|---|---|
| Product | [ ] | [ ] | [ ] | [ ] |
| Engineering | [ ] | [ ] | [ ] | [ ] |
| ML / AI | [ ] | [ ] | [ ] | [ ] |
| Design | [ ] | [ ] | [ ] | [ ] |
| Security | [ ] | [ ] | [ ] | [ ] |
| Privacy / Legal | [ ] | [ ] | [ ] | [ ] |
| Trust & Safety / Responsible AI | [ ] | [ ] | [ ] | [ ] |
| Finance (if cost > [$ threshold]) | [ ] | [ ] | [ ] | [ ] |

---

## Appendix

### A. Glossary
| Term | Definition |
|---|---|
| Golden set | Curated input/output pairs used as the source of truth for evaluating quality |
| Groundedness | Degree to which output claims are supported by the provided context |
| RAG | Retrieval-Augmented Generation: fetching relevant data and adding it to the model's context |
| TTFT | Time-to-first-token: latency until the first streamed output appears |
| LLM-as-judge | Using a model to grade outputs against a rubric, calibrated against human ratings |

### B. Pre-Launch Gate Checklist
- [ ] §3 AI Fit Assessment completed and reviewed
- [ ] §5.3 Success metrics instrumented and baselined
- [ ] §7 Behavior spec approved; golden set ≥ [N] examples
- [ ] §8 Data rights, PII handling, and retention confirmed
- [ ] §9 Models selected per route, versions pinned, fallback models evaluated
- [ ] §10 All offline evals meet launch thresholds
- [ ] §11 Risk register reviewed; kill switch tested
- [ ] §12 Privacy, security, and compliance reviews complete
- [ ] §14 Every fallback trigger designed and fault-injection tested
- [ ] §15 Latency budget met at p95 on production-sized prompts
- [ ] §16 Unit economics approved; budget alerts configured
- [ ] §20 All required approvals recorded
