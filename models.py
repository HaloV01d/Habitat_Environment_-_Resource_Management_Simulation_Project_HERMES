from dataclasses import dataclass
from typing import Optional, List


# core data classes for Project HERMES
# most logic is handled by services, repositories, and managers


@dataclass
class User:
    id: Optional[int]
    username: str
    password_hash: str
    password_salt: str
    role_id: Optional[int] = None


@dataclass
class Role:
    id: Optional[int]
    name: str
    description: str

    def get_tasks(self) -> List[str]:
        # role-specific tasks are handled through narrative events
        return []


@dataclass
class Mission:
    id: Optional[int]
    name: str
    duration_days: int

    def start(self) -> str:
        return f"Mission '{self.name}' started."

    def finish(self) -> str:
        return f"Mission '{self.name}' finished."


@dataclass
class Simulation:
    id: Optional[int]
    user_id: int
    mission_id: int
    state: str
    progress: float

    def execute(self) -> None:
        self.state = "running"

    def pause(self) -> None:
        self.state = "paused"

    def resume(self) -> None:
        self.state = "running"

    def finish(self) -> None:
        self.state = "finished"
        self.progress = 100.0


@dataclass
class HabitatState:
    id: Optional[int]
    simulation_id: Optional[int]
    energy: int
    oxygen: int
    integrity: int
    crew_health: int

    def update(
        self,
        energy: int,
        oxygen: int,
        integrity: int,
        crew_health: int
    ) -> None:
        self.energy = energy
        self.oxygen = oxygen
        self.integrity = integrity
        self.crew_health = crew_health


@dataclass
class NarrativeEvent:
    id: Optional[int]
    description: str
    role_id: Optional[int] = None

    def present(self) -> str:
        return self.description


@dataclass
class NarrativeOption:
    id: Optional[int]
    event_id: int
    description: str
    energy_impact: int = 0
    oxygen_impact: int = 0
    integrity_impact: int = 0
    crew_health_impact: int = 0
    score_impact: float = 0.0

    def apply(self, habitat_state: HabitatState) -> HabitatState:
        # actual impact handling is done by NarrativeManager
        return habitat_state


@dataclass
class PerformanceEvaluation:
    id: Optional[int]
    simulation_id: int
    score: float

    def update(self, score: float) -> None:
        self.score = score

    def generate_result(self) -> float:
        return self.score