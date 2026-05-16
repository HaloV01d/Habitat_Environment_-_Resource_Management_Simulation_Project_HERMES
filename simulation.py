from typing import List, Optional, Tuple

from models import User, Role, Mission, Simulation, HabitatState


STATE_NOT_STARTED = "not_started"
STATE_RUNNING = "running"
STATE_PAUSED = "paused"
STATE_FINISHED = "finished"

DEFAULT_PROGRESS = 0.0

DEFAULT_ENERGY = 100
DEFAULT_OXYGEN = 100
DEFAULT_INTEGRITY = 100
DEFAULT_CREW_HEALTH = 100


class AresPathfinderSimulator:
    def __init__(
        self,
        simulation_repository=None,
        habitat_state_repository=None,
        evaluation_repository=None
    ):
        self.simulation_repository = simulation_repository
        self.habitat_state_repository = habitat_state_repository
        self.evaluation_repository = evaluation_repository

    def can_start_simulation(
        self,
        user: Optional[User],
        mission: Optional[Mission],
        role: Optional[Role]
    ) -> Tuple[bool, List[str]]:
        errors = []

        if user is None:
            errors.append("A logged-in user is required.")

        if mission is None:
            errors.append("A mission must be selected before starting the simulation.")

        if role is None:
            errors.append("A professional role must be selected before starting the simulation.")

        return len(errors) == 0, errors

    def build_start_summary(
        self,
        user: User,
        mission: Optional[Mission],
        role: Optional[Role]
    ) -> str:
        mission_name = mission.name if mission else "No mission selected"
        role_name = role.name if role else "No role selected"

        return (
            "Simulation Setup\n"
            f"User: {user.username}\n"
            f"Mission: {mission_name}\n"
            f"Role: {role_name}"
        )

    def create_simulation_draft(self, user_id: int, mission_id: int) -> Simulation:
        # creates the object only, saving it to the database happens later
        return Simulation(
            id=None,
            user_id=user_id,
            mission_id=mission_id,
            state=STATE_NOT_STARTED,
            progress=DEFAULT_PROGRESS
        )

    def create_default_habitat_state(
        self,
        simulation_id: Optional[int] = None
    ) -> HabitatState:
        return HabitatState(
            id=None,
            simulation_id=simulation_id,
            energy=DEFAULT_ENERGY,
            oxygen=DEFAULT_OXYGEN,
            integrity=DEFAULT_INTEGRITY,
            crew_health=DEFAULT_CREW_HEALTH
        )

    def start(self, simulation: Simulation) -> Simulation:
        simulation.state = STATE_RUNNING
        simulation.progress = max(simulation.progress, 0.0)
        return simulation

    def pause(self, simulation: Simulation) -> Simulation:
        simulation.state = STATE_PAUSED
        return simulation

    def resume(self, simulation: Simulation) -> Simulation:
        simulation.state = STATE_RUNNING
        return simulation

    def finish(self, simulation: Simulation) -> Simulation:
        simulation.state = STATE_FINISHED
        simulation.progress = 100.0
        return simulation