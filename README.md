# AI Ops Triage Framework

A working prototype of how I run AI features like an operations leader: spec it, route it to the cheapest model capable of the job, test the routing rules, and gate every change behind CI.

Built by Kristen Estes, a Director of Content Operations with 20 years in creative and content ops and a PMP, as a public proof-of-work for senior AI Product and AI Operations roles. [LinkedIn](https://www.linkedin.com/in/kris10estes)

## What's in the box

**Product spec:** an AI-native PRD template plus a full spec for a customer support triage agent, covering model selection, fallback behavior, latency tolerances, and data masking rules. See `01_product_strategy/`.

**Architecture:** a system design for the same feature, including ingestion, PII masking, account matching, a two-tier model routing table, escalation triggers, and error handling. See `02_tech_architecture/`.

**Routing engine:** `triage_router.py`, a deterministic prototype of the routing logic. It parses an inbound email, masks card numbers and credentials, classifies the request, applies priority and tier rules, and logs which model handles each step and the worst-case cost of the decision.

**Test suite:** 63 table-driven pytest cases covering every escalation trigger, every skip condition, and every merge rule between the first-pass model and the second opinion. Mutation checks confirm the suite fails when a threshold is moved.

**CI:** a GitHub Actions workflow pinned to commit SHAs and a fixed Ubuntu image, running the full suite on every push and pull request.

**Token governance:** `workspace_sweep.sh`, a bash tool for auditing how much context a workspace costs an AI agent to read. Refactoring against its report cut this repo's active footprint by 37 percent.

## The routing idea in one paragraph

Every email gets a first pass from a small, fast model. A larger model is called only when a defined trigger fires: low classification confidence, an enterprise account, an outage signal, a long thread, or a priority the rules cannot settle. When both models weigh in, the merge keeps the higher priority and tier, ORs the risk flags, and takes the category from whichever model cleared the confidence bar. Security reports and suspected prompt injection get no AI-drafted reply at all. The point is margin protection without sacrificing the cases where the expensive model earns its cost.

## How to run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r 03_operations_sprints/requirements-dev.txt
python -m pytest 03_operations_sprints -q
python 03_operations_sprints/triage_router.py --self-test
./03_operations_sprints/workspace_sweep.sh
```

## What it is not

This is a prototype. The model calls are simulated so the tests run in a tenth of a second and cost nothing. Two backlog items are open on purpose: the live traffic kill switch (K4) needs real traffic data, and the merge logic needs re-checking against real model output in shadow mode. Both are logged in `SPRINT_BACKLOG.md`.

## Built with

Claude Code in the terminal. The specs, thresholds, merge rules, and test expectations are my decisions, and every one of them got read and checked before it landed in the repo. Directing the tool is the job.
