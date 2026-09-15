"""Regression tests for triage_router.py, the Support Triage Bot routing prototype.

Formalizes the 11 checks from `triage_router.py --self-test`:

  1-8   Each built-in sample email routes to the expected path, category, final
        priority, final tier, route IDs, and escalation mode (ARCH §5.1-§5.4).
  9     Card numbers are masked out of every field of the routing decision (ARCH §3.2 S4).
  10    The AI triage kill switch sends email down the rules-only path with no
        model calls (ARCH §5.1 P3).
  11    With escalation disabled (K3), low-confidence email goes to manual triage
        with a P2 floor (ARCH §5.2 step 4).

Adds the backlog BOT-021 escalation tests (ARCH §5.2):

  12-16 Dedicated payloads that fire exactly one trigger or skip condition:
        T4 (uncertain P1), T4 (uncertain P2), T6 (long thread), K1 (Tier D already
        decided), K2 (rule set P1, R2 runs after the alert).
  17    T6 boundary: a 5-message thread does not fire T6.
  18    Coverage check: every trigger T1-T7 and skip condition K1-K3 implemented
        by the router fires in at least one test payload.

Adds the backlog BOT-021 merge tests (ARCH §5.2 steps 3-4, §6.5):

  19-28 Priority, tier, and churn risk keep the higher of R1 and R2.
  29-34 Category selection matrix: R2 if >= 0.70, else R1 if >= 0.70, else Needs Review.
  35-46 OR truth table for is_complaint, mentions_contract_terms, injection_suspected.
  47-48 Descriptive fields and confidences from R2; unions without duplicates.
  49-54 Invalid R2 payloads are rejected before merging.
  55-63 End to end: merged labels drive rules, queue, draft route, and alerts;
        async (K2) alerts don't change; unavailable or invalid R2 falls back to R1.

Expected values are written out in this file instead of imported from
`triage_router.EXPECTED`. A routing change must be made deliberately here, in the
router, and in 02_tech_architecture/ARCH_support_triage_bot.md in the same change.

Run from the workspace root (see 03_operations_sprints/README.md):

    .venv/bin/python -m pytest 03_operations_sprints -q
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

import pytest

import triage_router as tr


@dataclass(frozen=True)
class ExpectedRoute:
    path: str
    category: str
    final_priority: str
    final_tier: str
    routes: tuple[str, ...]
    escalation: str


# Tests 1-8: one row per built-in sample in triage_router.SAMPLES.
ROUTING_CASES: dict[str, ExpectedRoute] = {
    # Tier A: Haiku triages, drafts, and verifies.
    "general-question": ExpectedRoute("ai", "General Question", "P3", "A", ("R1", "R3", "R7"), "none"),
    # Tier B: Haiku triage, Sonnet (effort low) draft, Haiku verifier.
    "bug-report": ExpectedRoute("ai", "Bug Report", "P3", "B", ("R1", "R4", "R7"), "none"),
    # Tier C: complaint on an Enterprise account; Sonnet (effort medium) draft, Sonnet verifier.
    "billing-dispute": ExpectedRoute("ai", "Billing", "P2", "C", ("R1", "R5", "R8"), "none"),
    # Tier C: P1 outage.
    "urgent-outage": ExpectedRoute("ai", "Urgent Outage", "P1", "C", ("R1", "R5", "R8"), "none"),
    # Low category confidence (T1, T3) triggers a synchronous Sonnet second opinion (R2).
    "ambiguous-low-confidence": ExpectedRoute("ai", "Bug Report", "P3", "B", ("R1", "R2", "R4", "R7"), "sync"),
    # Tier D: security report; rule raises to P1; no model draft.
    "security-report": ExpectedRoute("ai", "Security/Legal", "P1", "D", ("R1", "R6"), "none"),
    # Tier D: injection (T7) is confirmed by R2; still no model draft. Neither R1 nor R2 reaches 0.70
    # category confidence, so the merge sets Needs Review and step 4 raises priority to P2 (ARCH §5.2 steps 3-4).
    "prompt-injection": ExpectedRoute("ai", "Needs Review", "P2", "D", ("R1", "R2", "R6"), "sync"),
    # P0: auto-replies never reach a model.
    "auto-reply": ExpectedRoute("closed_nonactionable", "n/a", "P4", "D", (), "none"),
}


def _actual_route(decision: tr.RoutingDecision) -> ExpectedRoute:
    return ExpectedRoute(
        path=decision.path,
        category=decision.category,
        final_priority=decision.final_priority,
        final_tier=decision.final_tier,
        routes=tuple(route.route_id for route in decision.routes),
        escalation=decision.escalation["mode"],
    )


@pytest.mark.parametrize("sample_name", sorted(tr.SAMPLES))
def test_sample_routes_as_expected(sample_name: str) -> None:
    if sample_name not in ROUTING_CASES:
        pytest.fail(f"Sample {sample_name!r} has no expected route; add it to ROUTING_CASES.")

    decision = tr.route_email(tr.SAMPLES[sample_name])

    assert asdict(_actual_route(decision)) == asdict(ROUTING_CASES[sample_name])


# Test 9
def test_card_number_is_masked_in_every_decision_field() -> None:
    decision = tr.route_email(tr.SAMPLES["billing-dispute"])
    serialized = json.dumps(decision.to_dict(), default=str)

    assert decision.masking_counts["CARD_NUMBER"] == 1
    assert "4111" not in serialized, "raw card digits leaked into the routing decision"
    assert "[CARD_NUMBER]" in decision.summary


# Test 10
def test_ai_triage_kill_switch_routes_rules_only_without_model_calls() -> None:
    decision = tr.route_email(tr.SAMPLES["urgent-outage"], tr.RouterConfig(ai_triage_enabled=False))

    assert decision.path == "rules_only"
    assert decision.routes == []


# Test 11
def test_escalation_disabled_sends_low_confidence_to_manual_triage_with_p2_floor() -> None:
    decision = tr.route_email(tr.SAMPLES["ambiguous-low-confidence"], tr.RouterConfig(escalation_enabled=False))

    assert decision.escalation["mode"] == "skipped"
    assert decision.queue == "manual_triage"
    assert decision.final_priority == "P2"


# --------------------------------------------------------------------------- #
# BOT-021: isolated escalation triggers and skip conditions (ARCH §5.2)
# --------------------------------------------------------------------------- #

VERIFIED = "Authentication-Results: mx.support.example; spf=pass; dkim=pass; dmarc=pass"
CONTOSO_CONTACT = "Sam Ortiz <sam.ortiz@contoso.example>"  # business tier, verified contact
NORTHWIND_CONTACT = "Dana Lee <dana.lee@northwind.example>"  # enterprise tier, renewal in 45 days


def make_email(sender: str, subject: str, body: str, *, verified: bool = True, thread_messages: int | None = None) -> str:
    """Build a raw RFC 5322 email for a test payload."""
    headers = [f"From: {sender}", "To: support@support.example", f"Subject: {subject}"]
    if verified:
        headers.append(VERIFIED)
    if thread_messages is not None:
        headers.append(f"X-Thread-Message-Count: {thread_messages}")
    headers.append("Content-Type: text/plain; charset=utf-8")
    return "\n".join(headers) + f"\n\n{body}\n"


@dataclass(frozen=True)
class EscalationCase:
    payload: str
    triggers: tuple[str, ...]  # exact set of triggers that must fire, in T-order
    mode: str  # sync | async | skipped
    skip_code: str | None  # K1 | K2 | None
    final_priority: str
    final_tier: str
    routes: tuple[str, ...]
    r2_timing: str | None  # inline | async_after_alert | None (R2 not planned)
    r2_status: str  # merged | merged_after_alert | skipped
    why: str


ESCALATION_CASES: dict[str, EscalationCase] = {
    "T4-uncertain-P1": EscalationCase(
        payload=make_email(CONTOSO_CONTACT, "Dashboard", "Our dashboard went down about ten minutes ago."),
        triggers=("T4",), mode="sync", skip_code=None, final_priority="P1", final_tier="C",
        routes=("R1", "R2", "R5", "R8"), r2_timing="inline", r2_status="merged",
        why="One outage signal gives P1 with priority confidence 0.80 (< 0.85); category confidence 0.97 keeps T1-T3 quiet.",
    ),
    "T4-uncertain-P2": EscalationCase(
        payload=make_email(
            CONTOSO_CONTACT, "Report builder",
            "Since the update, the report builder fails with an error and it is blocking our team.",
        ),
        triggers=("T4",), mode="sync", skip_code=None, final_priority="P2", final_tier="C",
        routes=("R1", "R2", "R5", "R8"), r2_timing="inline", r2_status="merged",
        why="A blocking bug gives P2 with priority confidence 0.80 (< 0.85, but not < 0.75, so T2 stays quiet).",
    ),
    "T6-long-thread": EscalationCase(
        payload=make_email(CONTOSO_CONTACT, "Settings page", "We still see the error on the settings page.", thread_messages=6),
        triggers=("T6",), mode="sync", skip_code=None, final_priority="P3", final_tier="C",
        routes=("R1", "R2", "R5", "R8"), r2_timing="inline", r2_status="merged",
        why="Six-message thread with category confidence 0.70: not below T1/T3's 0.70, but below T6's 0.85.",
    ),
    "K1-tier-d-already-decided": EscalationCase(
        payload=make_email(
            "Unknown Sender <billing.question@unverified.example>", "Latest invoice",
            "Since the update there is a problem with our latest invoice.", verified=False,
        ),
        triggers=("T1", "T3"), mode="skipped", skip_code="K1", final_priority="P3", final_tier="D",
        routes=("R1", "R6"), r2_timing=None, r2_status="skipped",
        why="Low confidence fires T1/T3, but an unverified sender (D-UNVER) already fixed Tier D, so R2 would change nothing.",
    ),
    "K2-rule-set-P1": EscalationCase(
        payload=make_email(
            NORTHWIND_CONTACT, "Report builder",
            "Since the update, the report builder fails with an error and it is blocking our finance team. "
            "If this is not fixed this week we will cancel our subscription.",
        ),
        triggers=("T4",), mode="async", skip_code="K2", final_priority="P1", final_tier="C",
        routes=("R1", "R2", "R5", "R8"), r2_timing="async_after_alert", r2_status="merged_after_alert",
        why="Model says P2 (T4 fires), but P-ENT-CHURN raises to P1, so the alert can't wait for R2.",
    ),
}


# Tests 12-16
@pytest.mark.parametrize("case_name", list(ESCALATION_CASES))
def test_escalation_case_fires_only_its_target(case_name: str) -> None:
    case = ESCALATION_CASES[case_name]
    decision = tr.route_email(case.payload)
    escalation = decision.escalation
    skip_reason = escalation["skip_reason"]
    r2_routes = [route for route in decision.routes if route.route_id == "R2"]

    assert decision.path == "ai"
    assert escalation["triggers"] == case.triggers, case.why
    assert escalation["mode"] == case.mode, case.why
    assert (skip_reason.split(":")[0] if skip_reason else None) == case.skip_code, case.why
    assert (decision.final_priority, decision.final_tier) == (case.final_priority, case.final_tier)
    assert tuple(route.route_id for route in decision.routes) == case.routes
    assert (r2_routes[0].timing if r2_routes else None) == case.r2_timing
    assert decision.second_opinion["status"] == case.r2_status


# Test 17
def test_t6_does_not_fire_below_long_thread_threshold() -> None:
    payload = make_email(CONTOSO_CONTACT, "Settings page", "We still see the error on the settings page.", thread_messages=5)
    decision = tr.route_email(payload)

    assert tr.Thresholds().long_thread_messages == 6
    assert decision.escalation["triggers"] == ()
    assert decision.escalation["mode"] == "none"
    assert "R2" not in [route.route_id for route in decision.routes]


# Test 18
def test_every_implemented_trigger_and_skip_condition_is_exercised() -> None:
    fired_triggers: set[str] = set()
    fired_skips: set[str] = set()

    runs = [(raw, tr.RouterConfig()) for raw in tr.SAMPLES.values()]
    runs += [(case.payload, tr.RouterConfig()) for case in ESCALATION_CASES.values()]
    runs.append((tr.SAMPLES["ambiguous-low-confidence"], tr.RouterConfig(escalation_enabled=False)))  # K3

    for raw, config in runs:
        escalation = tr.route_email(raw, config).escalation
        fired_triggers.update(escalation["triggers"])
        if escalation["skip_reason"]:
            fired_skips.add(escalation["skip_reason"].split(":")[0])

    # K4 (escalation share over 20%) needs live traffic metrics; it belongs to Model Client tests.
    assert fired_triggers == {"T1", "T2", "T3", "T4", "T5", "T6", "T7"}
    assert fired_skips == {"K1", "K2", "K3"}


# --------------------------------------------------------------------------- #
# BOT-021: R1 + R2 merge matrix (ARCH §5.2 steps 3-4, §6.5)
# --------------------------------------------------------------------------- #

Category = tr.Category


def triage_result(**overrides: object) -> tr.Classification:
    """A valid triage payload with neutral defaults. Override only the fields a test is about."""
    fields: dict[str, object] = {
        "category": Category.BUG_REPORT,
        "taxonomy_category": "technical_issue",
        "priority": "P3",
        "priority_reasons": ("none",),
        "risk_tier_suggestion": "B",
        "is_complaint": False,
        "sentiment": "neutral",
        "churn_risk": "low",
        "mentions_contract_terms": False,
        "customer_requests": 1,
        "injection_suspected": False,
        "category_confidence": 0.90,
        "priority_confidence": 0.90,
        "tier_confidence": 0.90,
        "matched_signals": (),
        "summary": "summary",
    }
    fields.update(overrides)
    return tr.Classification(**fields)  # type: ignore[arg-type]


def r2_returns(result: tr.Classification) -> tr.SecondOpinionFn:
    return lambda parsed, first_pass: result


# Priority and tier: keep the higher value; R2 can raise but never lower.
@pytest.mark.parametrize(
    ("r1_priority", "r2_priority", "expected"),
    [("P3", "P1", "P1"), ("P1", "P3", "P1"), ("P4", "P2", "P2"), ("P2", "P2", "P2")],
    ids=["r2-raises", "r2-cannot-lower", "r2-raises-two-levels", "agreement"],
)
def test_merge_priority_keeps_higher_value(r1_priority: str, r2_priority: str, expected: str) -> None:
    result = tr.merge_triage(triage_result(priority=r1_priority), triage_result(priority=r2_priority))

    assert result.classification.priority == expected
    assert result.sources["priority"] == "max"


@pytest.mark.parametrize(
    ("r1_tier", "r2_tier", "expected"),
    [("A", "C", "C"), ("D", "B", "D"), ("B", "B", "B")],
    ids=["r2-raises", "r2-cannot-lower-tier-d", "agreement"],
)
def test_merge_tier_keeps_higher_value(r1_tier: str, r2_tier: str, expected: str) -> None:
    result = tr.merge_triage(triage_result(risk_tier_suggestion=r1_tier), triage_result(risk_tier_suggestion=r2_tier))

    assert result.classification.risk_tier_suggestion == expected
    assert result.sources["risk_tier_suggestion"] == "max"


@pytest.mark.parametrize(
    ("r1_churn", "r2_churn", "expected"),
    [("high", "low", "high"), ("low", "medium", "medium"), ("medium", "high", "high")],
    ids=["r1-high-kept", "r2-raises-to-medium", "r2-raises-to-high"],
)
def test_merge_churn_risk_keeps_higher_value(r1_churn: str, r2_churn: str, expected: str) -> None:
    result = tr.merge_triage(triage_result(churn_risk=r1_churn), triage_result(churn_risk=r2_churn))

    assert result.classification.churn_risk == expected


# Category: R2 if confidence >= 0.70, else R1 if >= 0.70, else Needs Review.
@dataclass(frozen=True)
class CategoryCase:
    r1: tuple[tr.Category, str, float]  # category, taxonomy, confidence
    r2: tuple[tr.Category, str, float]
    category: tr.Category
    taxonomy: str
    confidence: float
    source: str
    needs_review: bool


CATEGORY_CASES: dict[str, CategoryCase] = {
    "r2-confident-wins": CategoryCase(
        (Category.BUG_REPORT, "technical_issue", 0.90), (Category.BILLING, "billing", 0.85),
        Category.BILLING, "billing", 0.85, "r2", False,
    ),
    "r2-exactly-at-threshold-wins": CategoryCase(
        (Category.BUG_REPORT, "technical_issue", 0.95), (Category.BILLING, "billing", 0.70),
        Category.BILLING, "billing", 0.70, "r2", False,
    ),
    "r2-below-threshold-r1-kept": CategoryCase(
        (Category.BUG_REPORT, "technical_issue", 0.80), (Category.BILLING, "billing", 0.69),
        Category.BUG_REPORT, "technical_issue", 0.80, "r1", False,
    ),
    "r1-exactly-at-threshold-kept": CategoryCase(
        (Category.BUG_REPORT, "technical_issue", 0.70), (Category.BILLING, "billing", 0.69),
        Category.BUG_REPORT, "technical_issue", 0.70, "r1", False,
    ),
    "both-below-threshold-needs-review": CategoryCase(
        (Category.BUG_REPORT, "technical_issue", 0.69), (Category.BILLING, "billing", 0.50),
        Category.NEEDS_REVIEW, "needs_review", 0.50, "needs_review", True,
    ),
    "taxonomy-follows-kept-category": CategoryCase(
        (Category.BILLING, "billing", 0.60), (Category.SECURITY_LEGAL, "legal_compliance", 0.88),
        Category.SECURITY_LEGAL, "legal_compliance", 0.88, "r2", False,
    ),
}


@pytest.mark.parametrize("case_name", list(CATEGORY_CASES))
def test_merge_category_selection_matrix(case_name: str) -> None:
    case = CATEGORY_CASES[case_name]
    r1 = triage_result(category=case.r1[0], taxonomy_category=case.r1[1], category_confidence=case.r1[2])
    r2 = triage_result(category=case.r2[0], taxonomy_category=case.r2[1], category_confidence=case.r2[2])

    result = tr.merge_triage(r1, r2)

    assert result.classification.category is case.category
    assert result.classification.taxonomy_category == case.taxonomy
    assert result.classification.category_confidence == case.confidence
    assert result.sources["category"] == case.source
    assert result.needs_review is case.needs_review


# Flags: full OR truth table for every merged flag.
@pytest.mark.parametrize("flag", tr.MERGE_FLAGS)
@pytest.mark.parametrize(
    ("r1_value", "r2_value"),
    [(False, False), (True, False), (False, True), (True, True)],
    ids=["neither", "r1-only", "r2-only", "both"],
)
def test_merge_flags_use_or(flag: str, r1_value: bool, r2_value: bool) -> None:
    result = tr.merge_triage(triage_result(**{flag: r1_value}), triage_result(**{flag: r2_value}))

    assert getattr(result.classification, flag) is (r1_value or r2_value)
    assert result.sources[flag] == "or"


def test_merge_takes_descriptive_fields_and_confidences_from_r2() -> None:
    r1 = triage_result(summary="r1 summary", customer_requests=1, sentiment="neutral",
                       priority_confidence=0.95, tier_confidence=0.60)
    r2 = triage_result(summary="r2 summary", customer_requests=3, sentiment="negative",
                       priority_confidence=0.80, tier_confidence=0.75)

    merged = tr.merge_triage(r1, r2).classification

    assert (merged.summary, merged.customer_requests, merged.sentiment) == ("r2 summary", 3, "negative")
    assert (merged.priority_confidence, merged.tier_confidence) == (0.80, 0.75)


def test_merge_unions_priority_reasons_and_signals_without_duplicates() -> None:
    r1 = triage_result(priority_reasons=("outage_reported",), matched_signals=("outage", "error"))
    r2 = triage_result(priority_reasons=("none",), matched_signals=("error", "since_update"))

    merged = tr.merge_triage(r1, r2).classification

    assert merged.priority_reasons == ("outage_reported",)
    assert merged.matched_signals == ("outage", "error", "since_update")
    assert tr.merge_triage(triage_result(), triage_result()).classification.priority_reasons == ("none",)


@pytest.mark.parametrize(
    ("override", "field_name"),
    [
        ({"priority": "P0"}, "priority"),
        ({"risk_tier_suggestion": "E"}, "risk_tier_suggestion"),
        ({"category_confidence": 1.4}, "category_confidence"),
        ({"priority_confidence": float("nan")}, "priority_confidence"),
        ({"customer_requests": -1}, "customer_requests"),
        ({"injection_suspected": "yes"}, "injection_suspected"),
    ],
    ids=["bad-priority", "bad-tier", "confidence-above-1", "confidence-nan", "negative-requests", "non-bool-flag"],
)
def test_merge_rejects_invalid_r2_payloads(override: dict[str, object], field_name: str) -> None:
    with pytest.raises(tr.InvalidTriageResult, match=field_name):
        tr.merge_triage(triage_result(), triage_result(**override))


# End-to-end: the merge drives rules, queue, alerts, and draft routes.
def test_r2_raising_priority_reroutes_to_high_stakes_draft_and_alert() -> None:
    r2 = triage_result(category=Category.URGENT_OUTAGE, priority="P1", priority_reasons=("outage_reported",),
                       risk_tier_suggestion="C", category_confidence=0.93, tier_confidence=0.93)

    decision = tr.route_email(tr.SAMPLES["ambiguous-low-confidence"], second_opinion=r2_returns(r2))

    assert decision.second_opinion["status"] == "merged"
    assert (decision.category, decision.final_priority, decision.final_tier) == ("Urgent Outage", "P1", "C")
    assert [route.route_id for route in decision.routes] == ["R1", "R2", "R5", "R8"]
    assert "#support-urgent" in decision.alerts


def test_r2_cannot_lower_priority_or_tier_end_to_end() -> None:
    r2 = triage_result(category=Category.GENERAL_QUESTION, taxonomy_category="how_to", priority="P4",
                       risk_tier_suggestion="A")

    decision = tr.route_email(ESCALATION_CASES["T4-uncertain-P1"].payload, second_opinion=r2_returns(r2))

    assert (decision.final_priority, decision.final_tier) == ("P1", "C")
    assert "#support-urgent" in decision.alerts


def test_low_confidence_r2_category_keeps_confident_r1_category_end_to_end() -> None:
    r2 = triage_result(category=Category.BILLING, taxonomy_category="billing", priority="P2",
                       category_confidence=0.55, priority_confidence=0.85)

    decision = tr.route_email(ESCALATION_CASES["T4-uncertain-P2"].payload, second_opinion=r2_returns(r2))

    assert decision.category == "Bug Report"
    assert decision.second_opinion["merge_sources"]["category"] == "r1"
    assert decision.queue != "manual_triage"


def test_both_models_unsure_routes_needs_review_to_manual_triage() -> None:
    r2 = triage_result(category=Category.BILLING, taxonomy_category="billing", category_confidence=0.50)

    decision = tr.route_email(tr.SAMPLES["ambiguous-low-confidence"], second_opinion=r2_returns(r2))

    assert decision.category == "Needs Review"
    assert decision.queue == "manual_triage"
    assert (decision.final_priority, decision.final_tier) == ("P2", "B")


def test_injection_flag_from_r2_alone_withholds_the_draft() -> None:
    r2 = triage_result(injection_suspected=True, category_confidence=0.80)

    decision = tr.route_email(tr.SAMPLES["ambiguous-low-confidence"], second_opinion=r2_returns(r2))

    assert decision.injection_suspected is True
    assert decision.final_tier == "D"
    assert [route.route_id for route in decision.routes] == ["R1", "R2", "R6"]


def test_async_r2_refines_labels_but_not_alerts_already_posted() -> None:
    r2 = triage_result(category=Category.BILLING, taxonomy_category="billing", priority="P2",
                       risk_tier_suggestion="C", is_complaint=True)

    decision = tr.route_email(ESCALATION_CASES["K2-rule-set-P1"].payload, second_opinion=r2_returns(r2))

    assert decision.second_opinion["status"] == "merged_after_alert"
    assert decision.category == "Billing"
    assert decision.final_priority == "P1"
    # Alerts come from R1 + rules (posted before R2 finished), so R2's billing label adds no billing alert.
    assert decision.alerts == ["#support-urgent", "csm_dm"]


def test_r2_unavailable_falls_back_to_r1_with_low_confidence_handling() -> None:
    def unavailable(parsed: tr.ParsedEmail, first_pass: tr.Classification) -> tr.Classification:
        raise tr.SecondOpinionUnavailable("R2 timeout after 20 s")

    decision = tr.route_email(tr.SAMPLES["ambiguous-low-confidence"], second_opinion=unavailable)

    assert decision.second_opinion["status"] == "unavailable"
    assert decision.second_opinion["r2"] is None
    assert decision.category == "Bug Report"
    assert (decision.queue, decision.final_priority, decision.final_tier) == ("manual_triage", "P2", "B")


def test_invalid_r2_payload_is_not_merged() -> None:
    decision = tr.route_email(tr.SAMPLES["ambiguous-low-confidence"], second_opinion=r2_returns(triage_result(priority="P0")))

    assert decision.second_opinion["status"] == "unavailable"
    assert "priority" in decision.second_opinion["error"]
    assert (decision.queue, decision.final_priority) == ("manual_triage", "P2")


def test_simulated_second_opinion_is_deterministic_and_confident_on_ambiguous_sample() -> None:
    parsed = tr.parse_email(tr.SAMPLES["ambiguous-low-confidence"])
    first_pass = tr.classify(parsed)

    first_run = tr.simulate_second_opinion(parsed, first_pass)
    second_run = tr.simulate_second_opinion(parsed, first_pass)

    assert first_run == second_run
    assert first_pass.category_confidence < 0.70 <= first_run.category_confidence
    assert tr.merge_triage(first_pass, first_run).sources["category"] == "r2"
