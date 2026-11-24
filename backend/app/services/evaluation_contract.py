"""Task 06: standardized evaluation-result contract + INVEST scoring framework.

All three evaluators (rule_based, traditional_ml, llm) produce an
EvaluationResult dict via :func:`build_evaluation_result`. Each evaluator keeps
its own internal mechanism; this module only normalizes the shape and computes
the shared INVEST framework score (equal weighting, 0-100, IE excluded).

Scoring-framework decision (Task 06 design update):
- Six INVEST dimensions, overall quality scale 0-100, initial equal weighting.
- Dimensions an evaluator cannot genuinely assess are reported as
  INSUFFICIENT_EVIDENCE with rationale EVALUATOR_UNSUPPORTED_DIMENSION —
  never fabricated.
- The overall 0-100 score is produced by each evaluator's own mechanism:
  rule_based keeps its internal penalty score; traditional_ml / llm use the
  equal-weighted framework score over their six genuine dimension verdicts.
- The three evaluators are never averaged with each other.
"""
from typing import Any, Dict, List, Optional

CRITERIA = ["independent", "negotiable", "valuable", "estimable", "small", "testable"]
EVALUATORS = {"rule_based", "traditional_ml", "multimodel_router", "llm"}
VALID_LABELS = {"PASS", "FAIL", "INSUFFICIENT_EVIDENCE"}

# Initial equal weighting (Task 06 scoring decision). Kept as an explicit map
# so future weighting changes are a one-line, documented change.
WEIGHTS: Dict[str, float] = {c: 1.0 / len(CRITERIA) for c in CRITERIA}


class InvalidEvaluationContract(ValueError):
    """Raised when an evaluation result violates the shared contract."""


def _norm_label(label: Any) -> str:
    return str(label).strip().upper()


def build_dimensions(
    labels: Dict[str, Any],
    confidences: Optional[Dict[str, Optional[float]]] = None,
    rationales: Optional[Dict[str, Optional[str]]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Normalize per-criterion labels into contract dimensions.

    labels: {criterion: "PASS" | "FAIL" | "INSUFFICIENT_EVIDENCE"}
    """
    confidences = confidences or {}
    rationales = rationales or {}
    dims: Dict[str, Dict[str, Any]] = {}
    for crit in CRITERIA:
        raw = labels.get(crit)
        if raw is None:
            label = "INSUFFICIENT_EVIDENCE"
            rationale = rationales.get(crit) or "EVALUATOR_UNSUPPORTED_DIMENSION"
        else:
            label = _norm_label(raw)
            if label not in VALID_LABELS:
                raise InvalidEvaluationContract(
                    f"invalid label for {crit}: {raw!r} (expected one of {sorted(VALID_LABELS)})"
                )
            rationale = rationales.get(crit)
        confidence = confidences.get(crit)
        if confidence is not None:
            confidence = round(float(confidence), 4)
            if not (0.0 <= confidence <= 1.0):
                raise InvalidEvaluationContract(f"confidence for {crit} out of range: {confidence}")
        dims[crit] = {
            "label": label,
            "confidence": confidence,
            "rationale": rationale,
        }
    return dims


def framework_score(dimensions: Dict[str, Dict[str, Any]], weights: Optional[Dict[str, float]] = None) -> Optional[float]:
    """Equal-weighted 0-100 score over assessed dimensions.

    INSUFFICIENT_EVIDENCE dimensions are excluded and the remaining weights are
    renormalized. Returns None when no dimension was assessed.
    """
    w = weights or WEIGHTS
    gained = 0.0
    possible = 0.0
    for crit in CRITERIA:
        dim = dimensions.get(crit)
        if not dim:
            continue
        label = dim["label"]
        if label == "INSUFFICIENT_EVIDENCE":
            continue
        weight = w.get(crit, 1.0 / len(CRITERIA))
        possible += weight
        if label == "PASS":
            gained += weight
    if possible <= 0.0:
        return None
    return round(100.0 * gained / possible, 1)


def overall_verdict(dimensions: Dict[str, Dict[str, Any]]) -> str:
    """Overall verdict derived from assessed dimensions (no invented threshold):
    any assessed FAIL -> FAIL; no PASS/FAIL dimension at all (only IE or empty)
    -> INSUFFICIENT_EVIDENCE; else PASS.
    """
    assessed = [
        d["label"] for d in dimensions.values()
        if d.get("label") in ("PASS", "FAIL")
    ]
    if not assessed:
        return "INSUFFICIENT_EVIDENCE"
    if "FAIL" in assessed:
        return "FAIL"
    return "PASS"


def build_evaluation_result(
    evaluator: str,
    verdict: str,
    score: Optional[float],
    dimensions: Dict[str, Dict[str, Any]],
    model_version: Optional[str] = None,
    confidence: Optional[float] = None,
    findings: Optional[List[Dict[str, Any]]] = None,
    evidence: Optional[List[Dict[str, Any]]] = None,
    breakdown: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if evaluator not in EVALUATORS:
        raise InvalidEvaluationContract(f"unknown evaluator: {evaluator!r}")
    verdict = _norm_label(verdict)
    if verdict not in VALID_LABELS:
        raise InvalidEvaluationContract(f"invalid overall verdict: {verdict!r}")
    if score is not None:
        score = round(float(score), 1)
        if not (0.0 <= score <= 100.0):
            raise InvalidEvaluationContract(f"score out of range: {score}")
    assessed = [c for c in CRITERIA if dimensions.get(c, {}).get("label") != "INSUFFICIENT_EVIDENCE"]
    return {
        "evaluator": evaluator,
        "model_version": model_version,
        "verdict": verdict,
        "score": score,
        "confidence": round(float(confidence), 4) if confidence is not None else None,
        "dimensions": dimensions,
        "assessed_dimensions": assessed,
        "invest_framework_score": framework_score(dimensions),
        "findings": findings or [],
        "evidence": evidence or [],
        "breakdown": breakdown or {},
        "metadata": metadata or {},
    }
