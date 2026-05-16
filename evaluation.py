from typing import Dict

from models import HabitatState, PerformanceEvaluation


MIN_SCORE = 0.0
MAX_SCORE = 100.0


class PerformanceEvaluator:
    def __init__(self, starting_score: float = 0.0):
        self.score = self._clamp_score(starting_score)

    def create_evaluation_draft(
        self,
        simulation_id: int,
        score: float = 0.0
    ) -> PerformanceEvaluation:
        # creates the object only, saving happens through the repository
        return PerformanceEvaluation(
            id=None,
            simulation_id=simulation_id,
            score=self._clamp_score(score)
        )

    def set_score(self, score: float) -> float:
        self.score = self._clamp_score(score)
        return self.score

    def add_points(self, points: float) -> float:
        self.score = self._clamp_score(self.score + points)
        return self.score

    def subtract_points(self, points: float) -> float:
        self.score = self._clamp_score(self.score - points)
        return self.score

    def update_score(self, points: float) -> float:
        # simple alias for the wording used in the design
        return self.add_points(points)

    def calculate_habitat_score(self, habitat_state: HabitatState) -> float:
        # basic average, final formula can be changed later
        total = (
            habitat_state.energy +
            habitat_state.oxygen +
            habitat_state.integrity +
            habitat_state.crew_health
        )

        return self._clamp_score(total / 4)

    def generate_result(self, score: float = None) -> Dict[str, object]:
        final_score = self.score if score is None else self._clamp_score(score)

        return {
            "score": round(final_score, 2),
            "status": self.get_status(final_score)
        }

    def get_status(self, score: float) -> str:
        if score >= 85:
            return "Excellent"

        if score >= 70:
            return "Successful"

        if score >= 50:
            return "Needs improvement"

        return "Failed"

    def _clamp_score(self, score: float) -> float:
        return max(MIN_SCORE, min(MAX_SCORE, float(score)))