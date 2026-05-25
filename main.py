from database import initialize_database, get_connection
from repositories import (
    UserRepository,
    RoleRepository,
    MissionRepository,
    SimulationRepository,
    HabitatStateRepository,
    PerformanceEvaluationRepository,
    NarrativeEventRepository,
    NarrativeOptionRepository
)
from auth import AuthService
from interface import TerminalInterface
from narrative import NarrativeManager
from simulation import SimulationRunner


def main():
    connection = None

    try:
        initialize_database()
        connection = get_connection()

        user_repository = UserRepository(connection)
        role_repository = RoleRepository(connection)
        mission_repository = MissionRepository(connection)
        simulation_repository = SimulationRepository(connection)
        habitat_state_repository = HabitatStateRepository(connection)
        performance_evaluation_repository = PerformanceEvaluationRepository(connection)
        narrative_event_repository = NarrativeEventRepository(connection)
        narrative_option_repository = NarrativeOptionRepository(connection)

        auth_service = AuthService(user_repository)

        narrative_manager = NarrativeManager(
            event_repository=narrative_event_repository,
            option_repository=narrative_option_repository
        )

        simulation_runner = SimulationRunner(
            narrative_manager=narrative_manager,
            event_repository=narrative_event_repository,
            habitat_state_repository=habitat_state_repository,
            simulation_repository=simulation_repository,
            performance_evaluation_repository=performance_evaluation_repository
        )

        terminal_interface = TerminalInterface(
            auth_service,
            user_repository,
            role_repository,
            mission_repository,
            simulation_repository,
            habitat_state_repository,
            performance_evaluation_repository,
            simulation_runner
        )

        terminal_interface.start()

    except KeyboardInterrupt:
        print("\n\nProject HERMES closed.")

    except Exception as error:
        print(f"\nUnexpected error: {error}")

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()