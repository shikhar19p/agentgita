from typing import List, Any
from src.core.state import SystemState, Contradiction


class ContradictionDetector:

    TENSION_INDICATORS = {
        "action_vs_renunciation": {
            "keywords": ["karma", "action", "sannyasa", "renunciation", "akarma"],
            "themes": ["action", "detachment", "non_doership"],
        },
        "devotion_vs_knowledge": {
            "keywords": ["bhakti", "jnana", "devotion", "knowledge"],
            "themes": ["devotion", "wisdom", "knowledge"],
        },
        "duty_vs_compassion": {
            "keywords": ["dharma", "duty", "ahimsa", "compassion"],
            "themes": ["duty", "compassion", "non_violence"],
        },
        "self_effort_vs_divine_will": {
            "keywords": ["daiva", "karma", "effort", "surrender"],
            "themes": ["action", "surrender", "responsibility"],
        },
        "surrender_vs_autonomy": {
            "keywords": ["sharanam", "prapadyante", "svadharma", "effort"],
            "themes": ["surrender", "duty", "self_mastery"],
        },
    }

    def detect(self, state: SystemState) -> SystemState:
        state.add_trace("CONTRADICTION_DETECTION", "Starting contradiction detection")

        if len(state.retrieved_verses) < 2:
            state.add_trace("CONTRADICTION_DETECTION", "Insufficient verses for contradiction detection")
            return state

        contradictions = self._detect_thematic_tensions(state.retrieved_verses)
        contradictions.extend(self._detect_scope_conflicts(state.retrieved_verses))
        state.contradictions.extend(contradictions)

        state.add_trace("CONTRADICTION_DETECTION", f"Detected {len(contradictions)} potential tensions")
        state.mark_step("contradiction_detection")
        return state

    def _detect_thematic_tensions(self, retrieved_verses: List[Any]) -> List[Contradiction]:
        contradictions = []
        for tension_type, indicators in self.TENSION_INDICATORS.items():
            matched_ids = [
                rv.verse_id for rv in retrieved_verses
                if (
                    any(kw in rv.verse_data.get("keywords", []) for kw in indicators["keywords"])
                    or any(th in rv.verse_data.get("themes", []) for th in indicators["themes"])
                )
            ]
            if len(matched_ids) >= 2:
                contradictions.append(Contradiction(
                    verse_ids=matched_ids,
                    description=f"Potential tension: {tension_type.replace('_', ' ')}",
                    severity="moderate",
                ))
        return contradictions

    def _detect_scope_conflicts(self, retrieved_verses: List[Any]) -> List[Contradiction]:
        scopes: dict = {}
        for rv in retrieved_verses:
            scope = rv.verse_data.get("interpretive_notes", {}).get("scope")
            if scope:
                scopes.setdefault(scope, []).append(rv.verse_id)

        if len(scopes) >= 3:
            all_ids = [vid for ids in scopes.values() for vid in ids]
            return [Contradiction(
                verse_ids=all_ids,
                description="Multiple interpretive scopes detected (metaphysical, ethical, devotional, etc.)",
                severity="low",
            )]
        return []
