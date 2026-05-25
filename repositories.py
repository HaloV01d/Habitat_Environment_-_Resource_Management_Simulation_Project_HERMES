import sqlite3
from abc import ABC, abstractmethod
from typing import Optional, List

from models import (
    User,
    Role,
    Mission,
    Simulation,
    HabitatState,
    NarrativeEvent,
    NarrativeOption,
    PerformanceEvaluation
)


class IRepository(ABC):
    # basic repository interface from the design

    @abstractmethod
    def save(self, obj):
        pass

    @abstractmethod
    def get(self, object_id):
        pass


class UserRepository(IRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, user: User) -> User:
        return self.save_user(user)

    def get(self, user_id: int) -> Optional[User]:
        return self.get_user(user_id)

    def save_user(self, user: User) -> User:
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO users (username, password_hash, password_salt, role_id)
            VALUES (?, ?, ?, ?);
        """, (
            user.username,
            user.password_hash,
            user.password_salt,
            user.role_id
        ))

        self.connection.commit()
        user.id = cursor.lastrowid

        return user

    def get_user(self, user_id: int) -> Optional[User]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, username, password_hash, password_salt, role_id
            FROM users
            WHERE id = ?;
        """, (user_id,))

        return self._row_to_user(cursor.fetchone())

    def get_user_by_username(self, username: str) -> Optional[User]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, username, password_hash, password_salt, role_id
            FROM users
            WHERE username = ?;
        """, (username,))

        return self._row_to_user(cursor.fetchone())

    def get_all_users(self) -> List[User]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, username, password_hash, password_salt, role_id
            FROM users
            ORDER BY id;
        """)

        return [self._row_to_user(row) for row in cursor.fetchall()]

    def update_user_role(self, user_id: int, role_id: int) -> None:
        cursor = self.connection.cursor()

        cursor.execute("""
            UPDATE users
            SET role_id = ?
            WHERE id = ?;
        """, (role_id, user_id))

        self.connection.commit()

    def _row_to_user(self, row) -> Optional[User]:
        if row is None:
            return None

        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            password_salt=row["password_salt"],
            role_id=row["role_id"]
        )


class RoleRepository(IRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, role: Role) -> Role:
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO roles (name, description)
            VALUES (?, ?);
        """, (role.name, role.description))

        self.connection.commit()
        role.id = cursor.lastrowid

        return role

    def get(self, role_id: int) -> Optional[Role]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, name, description
            FROM roles
            WHERE id = ?;
        """, (role_id,))

        return self._row_to_role(cursor.fetchone())

    def get_all_roles(self) -> List[Role]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, name, description
            FROM roles
            ORDER BY id;
        """)

        return [self._row_to_role(row) for row in cursor.fetchall()]

    def get_role_by_name(self, name: str) -> Optional[Role]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, name, description
            FROM roles
            WHERE name = ?;
        """, (name,))

        return self._row_to_role(cursor.fetchone())

    def _row_to_role(self, row) -> Optional[Role]:
        if row is None:
            return None

        return Role(
            id=row["id"],
            name=row["name"],
            description=row["description"]
        )


class MissionRepository(IRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, mission: Mission) -> Mission:
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO missions (name, duration_days)
            VALUES (?, ?);
        """, (mission.name, mission.duration_days))

        self.connection.commit()
        mission.id = cursor.lastrowid

        return mission

    def get(self, mission_id: int) -> Optional[Mission]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, name, duration_days
            FROM missions
            WHERE id = ?;
        """, (mission_id,))

        return self._row_to_mission(cursor.fetchone())

    def get_all_missions(self) -> List[Mission]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, name, duration_days
            FROM missions
            ORDER BY id;
        """)

        return [self._row_to_mission(row) for row in cursor.fetchall()]

    def get_mission_by_name(self, name: str) -> Optional[Mission]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, name, duration_days
            FROM missions
            WHERE name = ?;
        """, (name,))

        return self._row_to_mission(cursor.fetchone())

    def _row_to_mission(self, row) -> Optional[Mission]:
        if row is None:
            return None

        return Mission(
            id=row["id"],
            name=row["name"],
            duration_days=row["duration_days"]
        )


class SimulationRepository(IRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, simulation: Simulation) -> Simulation:
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO simulations (
                user_id,
                mission_id,
                state,
                progress,
                current_event_index
            )
            VALUES (?, ?, ?, ?, ?);
        """, (
            simulation.user_id,
            simulation.mission_id,
            simulation.state,
            simulation.progress,
            simulation.current_event_index
        ))

        self.connection.commit()
        simulation.id = cursor.lastrowid

        return simulation

    def get(self, simulation_id: int) -> Optional[Simulation]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                id,
                user_id,
                mission_id,
                state,
                progress,
                current_event_index
            FROM simulations
            WHERE id = ?;
        """, (simulation_id,))

        return self._row_to_simulation(cursor.fetchone())

    def get_by_user(self, user_id: int) -> List[Simulation]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                id,
                user_id,
                mission_id,
                state,
                progress,
                current_event_index
            FROM simulations
            WHERE user_id = ?
            ORDER BY id;
        """, (user_id,))

        return [self._row_to_simulation(row) for row in cursor.fetchall()]

    def get_latest_paused_by_user(self, user_id: int) -> Optional[Simulation]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                id,
                user_id,
                mission_id,
                state,
                progress,
                current_event_index
            FROM simulations
            WHERE user_id = ?
              AND state = 'paused'
            ORDER BY id DESC
            LIMIT 1;
        """, (user_id,))

        return self._row_to_simulation(cursor.fetchone())

    def update_progress(
        self,
        simulation_id: int,
        state: str,
        progress: float,
        current_event_index: Optional[int] = None
    ) -> None:
        cursor = self.connection.cursor()

        if current_event_index is None:
            cursor.execute("""
                UPDATE simulations
                SET state = ?, progress = ?
                WHERE id = ?;
            """, (state, progress, simulation_id))
        else:
            cursor.execute("""
                UPDATE simulations
                SET state = ?, progress = ?, current_event_index = ?
                WHERE id = ?;
            """, (state, progress, current_event_index, simulation_id))

        self.connection.commit()

    def update_current_event_index(
        self,
        simulation_id: int,
        current_event_index: int
    ) -> None:
        cursor = self.connection.cursor()

        cursor.execute("""
            UPDATE simulations
            SET current_event_index = ?
            WHERE id = ?;
        """, (current_event_index, simulation_id))

        self.connection.commit()

    def mark_paused(self, simulation: Simulation) -> None:
        simulation.pause()

        self.update_progress(
            simulation.id,
            simulation.state,
            simulation.progress,
            simulation.current_event_index
        )

    def mark_running(self, simulation: Simulation) -> None:
        simulation.resume()

        self.update_progress(
            simulation.id,
            simulation.state,
            simulation.progress,
            simulation.current_event_index
        )

    def mark_finished(self, simulation: Simulation) -> None:
        simulation.finish()

        self.update_progress(
            simulation.id,
            simulation.state,
            simulation.progress,
            simulation.current_event_index
        )

    def _row_to_simulation(self, row) -> Optional[Simulation]:
        if row is None:
            return None

        return Simulation(
            id=row["id"],
            user_id=row["user_id"],
            mission_id=row["mission_id"],
            state=row["state"],
            progress=row["progress"],
            current_event_index=row["current_event_index"]
        )


class HabitatStateRepository(IRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, habitat_state: HabitatState) -> HabitatState:
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO habitat_states (
                simulation_id,
                energy,
                oxygen,
                integrity,
                crew_health
            )
            VALUES (?, ?, ?, ?, ?);
        """, (
            habitat_state.simulation_id,
            habitat_state.energy,
            habitat_state.oxygen,
            habitat_state.integrity,
            habitat_state.crew_health
        ))

        self.connection.commit()
        habitat_state.id = cursor.lastrowid

        return habitat_state

    def get(self, habitat_state_id: int) -> Optional[HabitatState]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, simulation_id, energy, oxygen, integrity, crew_health
            FROM habitat_states
            WHERE id = ?;
        """, (habitat_state_id,))

        return self._row_to_habitat_state(cursor.fetchone())

    def get_by_simulation(self, simulation_id: int) -> Optional[HabitatState]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, simulation_id, energy, oxygen, integrity, crew_health
            FROM habitat_states
            WHERE simulation_id = ?;
        """, (simulation_id,))

        return self._row_to_habitat_state(cursor.fetchone())

    def update_state(self, habitat_state: HabitatState) -> None:
        cursor = self.connection.cursor()

        cursor.execute("""
            UPDATE habitat_states
            SET energy = ?, oxygen = ?, integrity = ?, crew_health = ?
            WHERE id = ?;
        """, (
            habitat_state.energy,
            habitat_state.oxygen,
            habitat_state.integrity,
            habitat_state.crew_health,
            habitat_state.id
        ))

        self.connection.commit()

    def _row_to_habitat_state(self, row) -> Optional[HabitatState]:
        if row is None:
            return None

        return HabitatState(
            id=row["id"],
            simulation_id=row["simulation_id"],
            energy=row["energy"],
            oxygen=row["oxygen"],
            integrity=row["integrity"],
            crew_health=row["crew_health"]
        )


class NarrativeEventRepository(IRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, event: NarrativeEvent) -> NarrativeEvent:
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO narrative_events (description, role_id)
            VALUES (?, ?);
        """, (event.description, event.role_id))

        self.connection.commit()
        event.id = cursor.lastrowid

        return event

    def get(self, event_id: int) -> Optional[NarrativeEvent]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, description, role_id
            FROM narrative_events
            WHERE id = ?;
        """, (event_id,))

        return self._row_to_event(cursor.fetchone())

    def get_all_events(self) -> List[NarrativeEvent]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, description, role_id
            FROM narrative_events
            ORDER BY id;
        """)

        return [self._row_to_event(row) for row in cursor.fetchall()]

    def get_for_role(self, role_id: int) -> List[NarrativeEvent]:
        # shared events use role_id NULL
        # role-specific events use the selected role id
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, description, role_id
            FROM narrative_events
            WHERE role_id IS NULL OR role_id = ?
            ORDER BY id;
        """, (role_id,))

        return [self._row_to_event(row) for row in cursor.fetchall()]

    def _row_to_event(self, row) -> Optional[NarrativeEvent]:
        if row is None:
            return None

        return NarrativeEvent(
            id=row["id"],
            description=row["description"],
            role_id=row["role_id"]
        )


class NarrativeOptionRepository(IRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, option: NarrativeOption) -> NarrativeOption:
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO narrative_options (
                event_id,
                description,
                energy_impact,
                oxygen_impact,
                integrity_impact,
                crew_health_impact,
                score_impact
            )
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            option.event_id,
            option.description,
            option.energy_impact,
            option.oxygen_impact,
            option.integrity_impact,
            option.crew_health_impact,
            option.score_impact
        ))

        self.connection.commit()
        option.id = cursor.lastrowid

        return option

    def get(self, option_id: int) -> Optional[NarrativeOption]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                id,
                event_id,
                description,
                energy_impact,
                oxygen_impact,
                integrity_impact,
                crew_health_impact,
                score_impact
            FROM narrative_options
            WHERE id = ?;
        """, (option_id,))

        return self._row_to_option(cursor.fetchone())

    def get_by_event(self, event_id: int) -> List[NarrativeOption]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                id,
                event_id,
                description,
                energy_impact,
                oxygen_impact,
                integrity_impact,
                crew_health_impact,
                score_impact
            FROM narrative_options
            WHERE event_id = ?
            ORDER BY id;
        """, (event_id,))

        return [self._row_to_option(row) for row in cursor.fetchall()]

    def _row_to_option(self, row) -> Optional[NarrativeOption]:
        if row is None:
            return None

        return NarrativeOption(
            id=row["id"],
            event_id=row["event_id"],
            description=row["description"],
            energy_impact=row["energy_impact"],
            oxygen_impact=row["oxygen_impact"],
            integrity_impact=row["integrity_impact"],
            crew_health_impact=row["crew_health_impact"],
            score_impact=row["score_impact"]
        )


class PerformanceEvaluationRepository(IRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, evaluation: PerformanceEvaluation) -> PerformanceEvaluation:
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO performance_evaluations (simulation_id, score)
            VALUES (?, ?);
        """, (
            evaluation.simulation_id,
            evaluation.score
        ))

        self.connection.commit()
        evaluation.id = cursor.lastrowid

        return evaluation

    def get(self, evaluation_id: int) -> Optional[PerformanceEvaluation]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, simulation_id, score
            FROM performance_evaluations
            WHERE id = ?;
        """, (evaluation_id,))

        return self._row_to_evaluation(cursor.fetchone())

    def get_by_simulation(self, simulation_id: int) -> Optional[PerformanceEvaluation]:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT id, simulation_id, score
            FROM performance_evaluations
            WHERE simulation_id = ?;
        """, (simulation_id,))

        return self._row_to_evaluation(cursor.fetchone())

    def update_score(self, evaluation_id: int, score: float) -> None:
        cursor = self.connection.cursor()

        cursor.execute("""
            UPDATE performance_evaluations
            SET score = ?
            WHERE id = ?;
        """, (score, evaluation_id))

        self.connection.commit()

    def _row_to_evaluation(self, row) -> Optional[PerformanceEvaluation]:
        if row is None:
            return None

        return PerformanceEvaluation(
            id=row["id"],
            simulation_id=row["simulation_id"],
            score=row["score"]
        )