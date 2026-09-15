# 03 — Operations & Sprints

Workflow automation scripts for keeping this workspace organized and cheap for AI tools to read.

## Contents

| File | What It Is | When to Use It |
|---|---|---|
| [workspace_sweep.sh](workspace_sweep.sh) | Finds, lists, and summarizes Markdown files, with token estimates and flags | After adding, changing, or archiving documents; before giving an AI tool access to the workspace |
| [triage_router.py](triage_router.py) | Offline Support Triage Bot router: parses an email, classifies it, applies ARCH §5 rules and thresholds, and logs the Claude model route with request settings. No API calls. | Testing routing logic and thresholds; prototyping Sprint 2 tasks BOT-021 and BOT-022 |
| [test_triage_router.py](test_triage_router.py) | pytest regression suite for the router (63 tests) | Before every change to routing code, thresholds, or ARCH routing sections; in CI on every pull request |
| [pytest.ini](pytest.ini) | pytest settings; pins the test root to this folder | Read-only unless changing test policy |
| [requirements-dev.txt](requirements-dev.txt) | Pinned test dependencies (`pytest==9.1.1`) | One-time environment setup |

The active sprint plan lives at the workspace root: [`SPRINT_BACKLOG.md`](../SPRINT_BACKLOG.md).

## triage_router.py

```bash
python3 03_operations_sprints/triage_router.py                    # route 8 built-in sample emails
python3 03_operations_sprints/triage_router.py --eml message.eml  # route real .eml files (repeatable)
python3 03_operations_sprints/triage_router.py --stdin < message.eml
python3 03_operations_sprints/triage_router.py --format json      # one JSON decision per line
python3 03_operations_sprints/triage_router.py --no-escalation    # simulate the escalation kill switch
python3 03_operations_sprints/triage_router.py --self-test        # quick check without pytest (see below)
```

- **Requirements:** Python 3.10+, standard library only.
- **Classification:** a deterministic keyword classifier stands in for the Haiku triage call (R1), so thresholds and rules can be tested for zero tokens.
- **Source of truth:** thresholds, route settings, and reservations mirror `02_tech_architecture/ARCH_support_triage_bot.md` §4.3, §5, and §8.2. The architecture doc wins if they disagree.

## Test Suite & Regression Prevention

The pytest suite is the **authoritative** check on routing behavior. `--self-test` covers the original 11 checks (tests 1–11) with no dependencies, for quick local use, but CI and code review rely on pytest.

### One-Time Setup

From the workspace root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r 03_operations_sprints/requirements-dev.txt
```

`.venv/` stays local. The workspace sweep ignores it, and it shouldn't be committed.

### Running the Tests

```bash
.venv/bin/python -m pytest 03_operations_sprints                  # full suite
.venv/bin/python -m pytest 03_operations_sprints -v               # one line per test
.venv/bin/python -m pytest 03_operations_sprints -x               # stop at the first failure
.venv/bin/python -m pytest 03_operations_sprints -k masked        # tests whose names match
.venv/bin/python -m pytest 03_operations_sprints -k "outage or billing"
```

**Expected result:** `63 passed` in well under a second. Any other result blocks the change.

The command works the same from the workspace root or from inside `03_operations_sprints/`, because `pytest.ini` pins the test root. Always invoke pytest as `python -m pytest` so it uses the venv's interpreter.

### What the Suite Covers

| # | Test | Guards Against | ARCH Ref |
|---|---|---|---|
| 1–8 | `test_sample_routes_as_expected[<sample>]`, one per sample email | Changes to path, category, final priority, final tier, route IDs (Haiku vs. Sonnet), or escalation mode | §5.1–§5.4 |
| 9 | `test_card_number_is_masked_in_every_decision_field` | Raw card digits appearing anywhere in a routing decision or log | §3.2 S4 |
| 10 | `test_ai_triage_kill_switch_routes_rules_only_without_model_calls` | Model calls when `bot_ai_triage_enabled` is off | §5.1 P3 |
| 11 | `test_escalation_disabled_sends_low_confidence_to_manual_triage_with_p2_floor` | Low-confidence email slipping through without review when escalation is off | §5.2 K3, step 4 |
| 12–16 | `test_escalation_case_fires_only_its_target[<case>]`, one dedicated payload per escalation trigger or skip condition | A trigger or skip condition firing when it shouldn't, failing to fire, running R2 at the wrong time, or reporting the wrong second-opinion status | §5.2 T4, T6, K1, K2 |
| 17 | `test_t6_does_not_fire_below_long_thread_threshold` | T6's thread threshold drifting from 6 messages | §5.2 T6 |
| 18 | `test_every_implemented_trigger_and_skip_condition_is_exercised` | A trigger or skip condition losing all test coverage (e.g., a payload edit silently stops firing it) | §5.2 T1–T7, K1–K3 |
| 19–22 | `test_merge_priority_keeps_higher_value[...]` | R2 lowering priority, or not raising it | §5.2 step 3 |
| 23–25 | `test_merge_tier_keeps_higher_value[...]` | R2 lowering the risk tier (including out of Tier D) | §5.2 step 3 |
| 26–28 | `test_merge_churn_risk_keeps_higher_value[...]` | Churn risk being lowered by R2 | §5.2 step 3 |
| 29–34 | `test_merge_category_selection_matrix[...]` | Wrong category source at and around the 0.70 boundary; taxonomy not following the kept category; missing Needs Review | §5.2 step 3 |
| 35–46 | `test_merge_flags_use_or[<pair>-<flag>]`, full truth table × 3 flags | A complaint, contract-terms, or injection flag from either model being dropped | §5.2 step 3 |
| 47–48 | Descriptive fields from R2; union of priority reasons and signals | Wrong source for summary/requests/sentiment/confidences; lost or duplicated signals | §5.2 step 3 |
| 49–54 | `test_merge_rejects_invalid_r2_payloads[...]` | Out-of-range or malformed R2 values (bad enum, confidence > 1 or NaN, negative requests, non-boolean flag) being merged | §5.2 step 3, §6.5 |
| 55–63 | End-to-end merge tests with injected R2 payloads | Merged labels not driving rules, queue, draft route, and alerts; K2 alerts changing after they've posted; unavailable or invalid R2 not falling back to R1 + step 4; non-deterministic simulation | §5.2 steps 3–4, §6.5 |

**Merge matrix** (tests 19–54). R1 is Haiku's first pass, R2 is Sonnet's second opinion:

| Field | Rule | Boundary / Edge Cases Tested |
|---|---|---|
| `priority`, `risk_tier_suggestion`, `churn_risk` | Higher value | R2 raises; R2 tries to lower (incl. out of Tier D); agreement |
| `category` + taxonomy | R2 if ≥ 0.70 → R1 if ≥ 0.70 → Needs Review | R2 at exactly 0.70; R2 at 0.69 with R1 at exactly 0.70; both below |
| `is_complaint`, `mentions_contract_terms`, `injection_suspected` | OR | All four true/false combinations for each flag |
| `summary`, `customer_requests`, `sentiment`, priority/tier confidence | From R2 | R1 and R2 values differ |
| Category confidence | From the kept category's model | Covered in the category matrix |
| `priority_reasons`, matched signals | Union, R1 first, no duplicates | `none` placeholder dropped when a real reason exists |
| Invalid R2 payload | Rejected (`InvalidTriageResult`) → R1 + step 4 | Six malformed payloads + one end-to-end |

To test a specific R2 payload, pass `second_opinion=` to `route_email`. The end-to-end tests use a small `r2_returns(...)` helper, and raising `SecondOpinionUnavailable` simulates an R2 outage.

**Escalation case map** (tests 12–16). Each payload fires exactly the listed triggers:

| Case | Triggers | Mode | Why It Fires | Final Priority / Tier | Routes |
|---|---|---|---|---|---|
| `T4-uncertain-P1` | T4 | sync | One outage signal: P1 at priority confidence 0.80 (< 0.85) | P1 / C | R1 → R2 → R5 → R8 |
| `T4-uncertain-P2` | T4 | sync | Blocking bug: P2 at 0.80 (< 0.85, but ≥ 0.75 so T2 stays quiet) | P2 / C | R1 → R2 → R5 → R8 |
| `T6-long-thread` | T6 | sync | 6-message thread, category confidence 0.70 (≥ T1/T3's 0.70, < T6's 0.85) | P3 / C | R1 → R2 → R5 → R8 |
| `K1-tier-d-already-decided` | T1, T3 → **skipped (K1)** | skipped | Unverified sender already fixed Tier D; R2 can't change the outcome | P3 / D | R1 → R6 |
| `K2-rule-set-P1` | T4 → **async (K2)** | async | Enterprise churn rule raised P2 → P1; the alert posts before R2 runs | P1 / C | R1 → R2 (after alert) → R5 → R8 |

**Trigger and skip coverage:**

| Condition | Fired By | Isolated? |
|---|---|---|
| T1, T3 | `ambiguous-low-confidence`, `prompt-injection`, `K1-tier-d-already-decided` | Always together: the prototype derives tier confidence from category confidence, so they can't be separated until R1 returns its own tier confidence |
| T2, T5, T7 | `prompt-injection` | No, they fire together in that sample |
| T4 | `T4-uncertain-P1`, `T4-uncertain-P2`, `K2-rule-set-P1` | Yes |
| T6 | `T6-long-thread` (+ boundary test 17) | Yes |
| K1 | `K1-tier-d-already-decided` | Yes |
| K2 | `K2-rule-set-P1` | Yes |
| K3 | Test 11 | Yes |
| K4 | Not implemented in the prototype | Model Client test (needs live traffic share) |

**Sample-to-route map** (tests 1–8):

| Sample | Final Priority / Tier | Routes | Why It Matters |
|---|---|---|---|
| `general-question` | P3 / A | R1 → R3 → R7 (all Haiku) | Only path where Haiku drafts; guards against under-tiering |
| `bug-report` | P3 / B | R1 → R4 (Sonnet `low`) → R7 | Standard tier |
| `billing-dispute` | P2 / C | R1 → R5 (Sonnet `medium`) → R8 | Complaint + Enterprise floors |
| `urgent-outage` | P1 / C | R1 → R5 → R8 | P1 outage path |
| `ambiguous-low-confidence` | P3 / B | R1 → **R2** → R4 → R7 | T1/T3 escalation thresholds |
| `security-report` | P1 / D | R1 → R6 (no model) | Tier D, raise-only priority rule |
| `prompt-injection` | P2 / D (Needs Review) | R1 → **R2** → R6 | T7 confirmation, no draft; neither model is confident, so the merge sets Needs Review and step 4 raises priority to P2 |
| `auto-reply` | — | none | No tokens spent on auto-replies |

### When to Run

| Trigger | Command |
|---|---|
| Before committing any change to `triage_router.py` or `test_triage_router.py` | Full suite |
| Before changing ARCH §4.3, §5, or §8.2 (thresholds, rules, routes, token limits) | Full suite, before **and** after the change |
| After bake-off calibration produces new thresholds (backlog BOT-030) | Full suite, plus new boundary cases (below) |
| Every push and pull request to `main` | Automatic in CI (`.github/workflows/ci.yml`, below) |

### Continuous Integration

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs the suite on GitHub Actions for every push and pull request to `main`.

| Step | What It Does |
|---|---|
| Check out repository | `actions/checkout` v7.0.1, pinned to its commit SHA; credentials aren't persisted |
| Set up Python 3.14 | `actions/setup-python` v7.0.0, pinned; pip download cache keyed on `requirements-dev.txt` |
| Create virtual environment | `python -m venv .venv`, then puts `.venv/bin` first on PATH for later steps |
| Install test dependencies | `pip install --requirement 03_operations_sprints/requirements-dev.txt` |
| Verify virtual environment | Fails if Python isn't running inside `.venv`; prints Python and pytest versions |
| Run regression suite | `python -m pytest 03_operations_sprints -q`; any failure fails the job |

**Safeguards:** read-only token (`contents: read`), a 10-minute job timeout, and a pinned `ubuntu-24.04` runner. A new push to a pull request cancels its outdated run, but runs on `main` are never cancelled.

**To make CI block merges:** in the GitHub repository settings, add a branch protection rule (or ruleset) for `main` that requires the **Regression tests (pytest)** status check to pass.

**Updating the pinned actions:** replace the commit SHA and the version comment together. Look up a tag's SHA with `git ls-remote --tags https://github.com/actions/setup-python`.

### Changing Thresholds Without Regressions

Model thresholds will change as calibration data arrives. Follow these steps for every change:

1. **Update the architecture doc first.** Change the value in `ARCH_support_triage_bot.md` (§5.2 thresholds, §5.3 rules, §4.3/§8.2 route settings). It's the source of truth.
2. **Update the code.** Change `Thresholds`, `ROUTES`, or the rule functions in `triage_router.py` to match.
3. **Run the suite and classify every failure.**
   - **Intended consequence** (e.g., a stricter threshold now escalates the ambiguous sample): update that row in `ROUTING_CASES` and add a comment saying which ARCH change caused it.
   - **Unintended consequence:** that's a regression. Fix the code, not the test.
4. **Add boundary tests.** For each threshold you changed, add one sample just above and one just below the new value, so the next change can't move the boundary silently.
5. **Ship architecture doc, code, and tests in one pull request**, reviewed by the ML Lead and an engineer.

**Rules:**
- **Never edit an expected value just to make a test pass.** Every change to `ROUTING_CASES` needs a matching change in the architecture doc.
- **Never delete or skip a failing test to unblock a merge.** Fix the code, or revert the change.
- **Keep `EXPECTED` in `triage_router.py` in sync** with `ROUTING_CASES` while `--self-test` exists.
- **A sample without an expectation fails the suite.** Adding one to `SAMPLES` without a `ROUTING_CASES` row fails with "has no expected route".

### Reading a Failure

The routing tests compare every field at once, so pytest shows exactly what moved. For example, if the T1/T3 category-confidence threshold were lowered from 0.70 to 0.50:

```text
FAILED test_triage_router.py::test_sample_routes_as_expected[ambiguous-low-confidence]
E   Differing items:
E   {'escalation': 'none'} != {'escalation': 'sync'}
E   {'routes': ('R1', 'R4', 'R7')} != {'routes': ('R1', 'R2', 'R4', 'R7')}
```

Read it as actual `!=` expected: the email no longer gets a Sonnet second opinion (R2), so a low-confidence label would reach drafting unchecked. That's a regression unless the architecture doc changed the threshold on purpose.

### Adding a Test Case

1. Add a raw email to `SAMPLES` in `triage_router.py` with the `_sample(...)` helper, and its row to `EXPECTED`.
2. Add the same expectation to `ROUTING_CASES` in `test_triage_router.py`, with a one-line comment on what it protects.
3. Run the suite. The parametrized test picks the new sample up automatically.

### Known Gaps vs. Backlog BOT-021 / BOT-022

| Backlog Requirement | Status | Coverage | Still Needed |
|---|---|---|---|
| BOT-021: table-driven tests for every escalation trigger (T1–T7) | **Met in the prototype** | Every trigger fires in at least one payload (test 18). T4 and T6 have dedicated cases. | Isolated T2, T5, and T7 payloads; separate T1 and T3 once R1 returns its own tier confidence |
| BOT-021: every skip condition (K1–K4) | **K1–K3 met; K4 open** | K1, K2 dedicated cases; K3 test 11 | K4 (escalation share > 20%) needs traffic metrics, so it goes in the Model Client tests (BOT-011) |
| BOT-021: every merge field | **Met in the prototype** | Every ARCH §5.2 step 3 field, boundaries, invalid payloads, and end-to-end effects (tests 19–63) | Re-run against real R2 payloads once the Model Client exists |
| BOT-022: property test that rules never lower priority or tier; 250 unit cases | Open | Indirect, through samples | Property-based tests over generated classifications |

**BOT-021 status:** core requirements are met in the prototype. Escalation triggers T1–T7, skip conditions K1–K3, and every merge field are tested. Two items remain before production sign-off:
- **K4** (escalation share over 20%) needs live traffic metrics, so it belongs in the Model Client tests (BOT-011).
- **Real model calls:** the tests use deterministic stand-ins for Haiku and Sonnet, so they verify routing and merge logic, not model quality. Production merge behavior must be re-verified in the bake-off harness (BOT-030) and shadow mode.

## workspace_sweep.sh

## workspace_sweep.sh

### Quick Start

Run from the workspace root:

```bash
# Human-readable report in the terminal
./03_operations_sprints/workspace_sweep.sh

# Regenerate the master index that AI tools read first
./03_operations_sprints/workspace_sweep.sh -m -o CONTEXT_INDEX.md
```

### What It Reports

| Section | Contents |
|---|---|
| Header | Root, time generated, file count, total lines, words, bytes, estimated tokens |
| Files | Every Markdown file (`.md`, `.markdown`, `.mdx`) with estimated tokens, lines, words, last modified date |
| Largest files | Top N files by estimated tokens and their share of the total |
| Flags | Files over the token threshold, empty files, files with identical content |
| Summaries | Title (first H1, else front-matter `title`, else filename), first line of prose, and heading count. If that line ends with a colon, the first three list items after it are added. |
| Context tips | Suggestions based on the flags (text output only) |

### Options

| Flag | Meaning | Default |
|---|---|---|
| `-r DIR` | Root directory to scan | Workspace root (parent of this folder) |
| `-n NUM` | How many largest files to list (`0` hides the section) | 10 |
| `-w TOKENS` | Flag files with more estimated tokens than this | 4000 |
| `-x NAME` | Also skip directories with this name (repeatable) | — |
| `-a` | Include `archive/` directories | Off |
| `-s` | Add a heading outline (H1–H3) for each file | Off |
| `-m` | Markdown output instead of plain text | Off |
| `-o FILE` | Write the report to a file instead of the terminal | stdout |
| `-h` | Show help | — |

**Environment variable:** `CHARS_PER_TOKEN` (default `4`) sets the characters-per-token ratio used for estimates.

### What Gets Skipped

- **Directories:** `.git`, `node_modules`, `.venv`, `venv`, `dist`, `build`, `.next`, `__pycache__`, `.cache`, `.pytest_cache`, and `archive` (unless `-a`).
- **Generated indexes:** any file named `CONTEXT_INDEX.md`, plus the file passed to `-o`.

### Common Recipes

```bash
# Index with section outlines, so agents can jump straight to the section they need
./03_operations_sprints/workspace_sweep.sh -m -s -o CONTEXT_INDEX.md

# See only the 5 largest files, flagging anything over 10,000 tokens
./03_operations_sprints/workspace_sweep.sh -n 5 -w 10000

# Include archived documents (e.g., to check what archiving saved)
./03_operations_sprints/workspace_sweep.sh -a

# Scan a single folder
./03_operations_sprints/workspace_sweep.sh -r 02_tech_architecture
```

### Reading the Numbers

- **Token counts are estimates** (bytes ÷ 4). Use them to compare file sizes, not to predict cost. Real counts vary by model and language. For exact Claude counts, use the Anthropic API's token-counting endpoint.
- **"Over threshold" isn't a problem by itself.** Full PRDs and architecture docs are large by design. The fix is to have agents read the folder README section maps or `CONTEXT_INDEX.md` first and then load individual sections, not to shorten the specs.
- **Identical-content flags** compare exact file contents, so near-duplicates aren't detected.

### Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success, including when no Markdown files are found (a message is printed to stderr) |
| `1` | Invalid option or argument, missing root or output directory, or invalid `CHARS_PER_TOKEN` |

### Compatibility

The script runs on macOS (the system bash 3.2 and BSD tools) and on Linux (GNU tools), with no dependencies beyond standard Unix utilities.

## Workspace Conventions

| Convention | Rule |
|---|---|
| Regenerate the index | After any document is added, changed, renamed, or archived, run `./03_operations_sprints/workspace_sweep.sh -m -o CONTEXT_INDEX.md` |
| Test before routing changes | Run `.venv/bin/python -m pytest 03_operations_sprints` before and after any change to routing code or ARCH §4.3/§5/§8.2; ship architecture doc, code, and tests together |
| Archive superseded docs | Mark the document Superseded, move it to `archive/<original folder>/`, update links, and log it in [`archive/README.md`](../archive/README.md) |
| Agent reading order | `CONTEXT_INDEX.md` → folder `README.md` section maps → only the sections needed |
| Keep READMEs short | Folder READMEs are indexes; full content lives in named files |
