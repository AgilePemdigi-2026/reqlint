from typing import List, Dict, Any, Optional

PENALTY_MAP = {
    "AMBIGUITY": 8.0,
    "PASSIVE_VOICE": 6.0,
    "WEAK_DIRECTIVE": 5.0,
    "TIDAK_LENGKAP": 15.0
}

SEVERITY_MULTIPLIER = {
    "LOW": 0.5,
    "MEDIUM": 1.0,
    "HIGH": 1.5
}

class ScoringService:
    @staticmethod
    def calculate_score(
        stories: List[Dict[str, Any]],
        findings: List[Dict[str, Any]],
        invest_results: Optional[Dict[str, Optional[bool]]] = None
    ) -> Dict[str, Any]:
        """
        Calculates quality score (0..100) and ISO 29148 / INVEST breakdown.
        For multi-story drafts, score is the average of each story's score.
        """
        if not stories:
            return {
                "skor_kualitas": 100.0,
                "breakdown": ScoringService.default_breakdown(stage2_done=False)
            }

        # Calculate penalty per story
        num_stories = max(len(stories), 1)
        story_penalties = {i: 0.0 for i in range(num_stories)}

        for f in findings:
            cat = f.get("kategori_cacat", "")
            base_pen = PENALTY_MAP.get(cat, 5.0)
            sev = f.get("severity", "MEDIUM")
            mult = SEVERITY_MULTIPLIER.get(sev, 1.0)
            s_idx = f.get("story_index", 0)
            if s_idx not in story_penalties:
                story_penalties[s_idx] = 0.0
            story_penalties[s_idx] += (base_pen * mult)

        story_scores = []
        for s_idx, pen in story_penalties.items():
            s_score = max(0.0, min(100.0, 100.0 - pen))
            story_scores.append(s_score)

        avg_score = sum(story_scores) / len(story_scores)

        # Stage 2 penalties (INVEST criteria failed)
        if invest_results:
            failed_invest_count = sum(1 for val in invest_results.values() if val is False or val == 0)
            avg_score = max(0.0, avg_score - (failed_invest_count * 4.0))

        final_score = round(avg_score, 1)

        # Calculate Breakdown
        breakdown = ScoringService.compute_breakdown(findings, invest_results)

        return {
            "skor_kualitas": final_score,
            "breakdown": breakdown
        }

    @staticmethod
    def compute_breakdown(
        findings: List[Dict[str, Any]],
        invest_results: Optional[Dict[str, Optional[bool]]] = None
    ) -> Dict[str, Any]:
        # Count findings per characteristic
        ambiguity_count = sum(1 for f in findings if f.get("kategori_cacat") == "AMBIGUITY")
        tidak_lengkap_count = sum(1 for f in findings if f.get("kategori_cacat") == "TIDAK_LENGKAP")
        directive_count = sum(1 for f in findings if f.get("kategori_cacat") == "WEAK_DIRECTIVE")
        passive_count = sum(1 for f in findings if f.get("kategori_cacat") == "PASSIVE_VOICE")

        unambiguous = max(0, 100 - (ambiguity_count * 25))
        complete = max(0, 100 - (tidak_lengkap_count * 30))
        verifiable = max(0, 100 - (directive_count * 20 + passive_count * 15))
        consistent = 90 if ambiguity_count == 0 else max(40, 90 - (ambiguity_count * 10))
        modifiable = 80
        correct = max(30, 95 - (len(findings) * 8))

        iso_29148 = {
            "unambiguous": unambiguous,
            "complete": complete,
            "consistent": consistent,
            "verifiable": verifiable,
            "modifiable": modifiable,
            "traceable": None if not invest_results else 85,
            "ranked": None,
            "correct": correct
        }

        # P0/FUNC-12 & UI-48 & ML-07: INVEST breakdown is driven by the actual
        # per-criterion evaluation result. Missing (None) data is represented as
        # None ("not evaluated") — never as a passing value. The six INVEST
        # criteria are preserved.
        def _invest_value(flag: Any, passed_value: float, failed_value: float, derived_pass: Optional[float] = None) -> Optional[float]:
            if flag is None:
                return None
            if flag is False or flag == 0:
                return failed_value
            return derived_pass if derived_pass is not None else passed_value

        def _flag(key: str) -> Any:
            if not invest_results:
                return None
            return invest_results.get(key)

        invest = {
            "independent": _invest_value(_flag("independent"), 90, 40),
            "negotiable": _invest_value(_flag("negotiable"), 80, 45),
            "valuable": _invest_value(_flag("valuable"), 85, 35),
            "estimable": _invest_value(_flag("estimable"), 85, 20, derived_pass=max(20, 85 - (ambiguity_count * 15))),
            "small": _invest_value(_flag("small"), 85, 30),
            "testable": _invest_value(_flag("testable"), 85, 20, derived_pass=max(20, verifiable - 10)),
        }

        return {
            "iso_29148": iso_29148,
            "invest": invest
        }

    @staticmethod
    def default_breakdown(stage2_done: bool = False) -> Dict[str, Any]:
        # P0/UI-48: with no evaluation data, INVEST criteria are "not evaluated"
        # (None) — never fabricated passing values.
        return {
            "iso_29148": {
                "unambiguous": 100, "complete": 100, "consistent": 100, "verifiable": 100,
                "modifiable": 100, "traceable": 85 if stage2_done else None,
                "ranked": None, "correct": 100
            },
            "invest": {
                "independent": None, "negotiable": None, "valuable": None,
                "estimable": None, "small": None, "testable": None
            }
        }
