import os
from typing import List, Optional, Tuple

from models import User, Role, Mission, Simulation, HabitatState


STATE_NOT_STARTED = "not_started"
STATE_RUNNING = "running"
STATE_PAUSED = "paused"
STATE_FINISHED = "finished"
STATE_CANCELLED = "cancelled"

DEFAULT_PROGRESS = 0.0

DEFAULT_ENERGY = 100
DEFAULT_OXYGEN = 100
DEFAULT_INTEGRITY = 100
DEFAULT_CREW_HEALTH = 100


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


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
        # creates the object only, saving happens through the repository
        return Simulation(
            id=None,
            user_id=user_id,
            mission_id=mission_id,
            state=STATE_NOT_STARTED,
            progress=DEFAULT_PROGRESS,
            current_event_index=0
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


class SimulationRunner:
    def __init__(
        self,
        narrative_manager,
        event_repository,
        habitat_state_repository,
        simulation_repository,
        performance_evaluation_repository,
    ):
        self.narrative_manager = narrative_manager
        self.event_repository = event_repository
        self.habitat_state_repository = habitat_state_repository
        self.simulation_repository = simulation_repository
        self.performance_evaluation_repository = performance_evaluation_repository

    def run(self, simulation: Simulation, role: Role) -> dict:
        habitat_state = self.habitat_state_repository.get_by_simulation(simulation.id)

        if habitat_state is None:
            return {"status": "error", "error": "Habitat state was not found."}

        evaluation = self.performance_evaluation_repository.get_by_simulation(
            simulation.id
        )

        if evaluation is None:
            return {"status": "error", "error": "Performance evaluation was not found."}

        events = self.event_repository.get_for_role(role.id)

        if not events:
            return {"status": "error", "error": "No narrative events are configured for this role."}

        if simulation.current_event_index >= len(events):
            return self._build_finished_result(
                evaluation.score,
                len(events),
                len(events),
                habitat_state
            )

        simulation.resume()
        self.simulation_repository.update_progress(
            simulation.id,
            simulation.state,
            simulation.progress,
            simulation.current_event_index
        )

        total_score = evaluation.score
        total_events = len(events)

        self._show_intro(simulation, role, total_events)

        for event_index in range(simulation.current_event_index, total_events):
            event = events[event_index]

            event_result = self._play_event(
                event,
                event_index + 1,
                total_events,
                habitat_state,
                simulation.progress,
                total_score
            )

            if event_result["action"] == "save":
                simulation.pause()
                self.simulation_repository.update_progress(
                    simulation.id,
                    simulation.state,
                    simulation.progress,
                    simulation.current_event_index
                )

                return {
                    "status": "saved",
                    "message": "Progress saved. You can resume this simulation later.",
                    "events_completed": simulation.current_event_index,
                    "total_events": total_events,
                    "habitat_state": habitat_state,
                    "score": total_score,
                    "rating": self._rating_for(total_score)
                }

            if event_result["action"] == "exit":
                simulation.state = STATE_CANCELLED
                self.simulation_repository.update_progress(
                    simulation.id,
                    simulation.state,
                    simulation.progress,
                    simulation.current_event_index
                )

                return {
                    "status": "cancelled",
                    "message": "Simulation exited without saving a resume point.",
                    "events_completed": simulation.current_event_index,
                    "total_events": total_events,
                    "habitat_state": habitat_state,
                    "score": total_score,
                    "rating": self._rating_for(total_score)
                }

            chosen_option = event_result["option"]
            previous_state = self._copy_habitat_state(habitat_state)

            habitat_state = self.narrative_manager.apply_option(
                chosen_option,
                habitat_state
            )

            self.habitat_state_repository.update_state(habitat_state)

            total_score += chosen_option.score_impact
            evaluation.update(total_score)
            self.performance_evaluation_repository.update_score(
                evaluation.id,
                evaluation.score
            )

            simulation.current_event_index = event_index + 1
            simulation.progress = round(
                (simulation.current_event_index / total_events) * 100.0,
                1
            )

            self.simulation_repository.update_progress(
                simulation.id,
                simulation.state,
                simulation.progress,
                simulation.current_event_index
            )

            self._show_decision_result(
                chosen_option,
                previous_state,
                habitat_state,
                total_score,
                simulation.progress
            )

        simulation.finish()
        simulation.current_event_index = total_events

        self.simulation_repository.update_progress(
            simulation.id,
            simulation.state,
            simulation.progress,
            simulation.current_event_index
        )

        return self._build_finished_result(
            evaluation.generate_result(),
            simulation.current_event_index,
            total_events,
            habitat_state
        )

    def _play_event(
        self,
        event,
        event_number: int,
        total_events: int,
        habitat_state: HabitatState,
        progress: float,
        current_score: float
    ) -> dict:
        loaded_event, options = self.narrative_manager.get_event_with_options(
            event.id
        )

        if loaded_event is None or not options:
            return {"action": "skip", "option": None}

        while True:
            self._clear_screen()
            self._show_event_header(event_number, total_events)
            self._show_habitat_state(habitat_state, progress, current_score)

            print(f"{Colors.BOLD}{Colors.BRIGHT_WHITE}Mission Situation:{Colors.RESET}")
            print(loaded_event.description)
            print()

            print(f"{Colors.BOLD}{Colors.BRIGHT_WHITE}Available Actions:{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}0.{Colors.RESET} Pause simulation")

            for option_index, option in enumerate(options, start=1):
                print(
                    f"{Colors.BRIGHT_CYAN}{option_index}.{Colors.RESET} "
                    f"{option.description}"
                )

            print()
            choice = input(
                f"{Colors.BRIGHT_CYAN}Select an action: {Colors.RESET}"
            ).strip()

            if choice == "0":
                pause_result = self._show_pause_menu()

                if pause_result == "resume":
                    continue

                if pause_result == "save":
                    return {"action": "save", "option": None}

                if pause_result == "exit":
                    return {"action": "exit", "option": None}

            chosen_option = self.narrative_manager.validate_option_choice(
                choice,
                options
            )

            if chosen_option is not None:
                return {"action": "choice", "option": chosen_option}

            self._show_message("Invalid option. Please try again.", "error")
            input(f"{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")

    def _show_pause_menu(self) -> str:
        while True:
            self._clear_screen()
            self._show_title("SIMULATION PAUSED")

            print(f"{Colors.BRIGHT_GREEN}1.{Colors.RESET} Resume simulation")
            print(f"{Colors.BRIGHT_YELLOW}2.{Colors.RESET} Save progress and return to user menu")
            print(f"{Colors.BRIGHT_RED}3.{Colors.RESET} Exit to user menu without saving a resume point")
            print()

            choice = input(
                f"{Colors.BRIGHT_CYAN}Select an option: {Colors.RESET}"
            ).strip()

            if choice == "1":
                return "resume"

            if choice == "2":
                return "save"

            if choice == "3":
                return "exit"

            self._show_message("Invalid option. Please try again.", "error")
            input(f"{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")

    def _show_intro(self, simulation: Simulation, role: Role, total_events: int) -> None:
        self._clear_screen()
        self._show_title("MISSION START")

        if simulation.current_event_index > 0:
            print(f"{Colors.BRIGHT_YELLOW}Resuming saved simulation.{Colors.RESET}")
            print()

        print(f"{Colors.CYAN}Role:{Colors.RESET} {Colors.BOLD}{role.name}{Colors.RESET}")
        print(f"{Colors.CYAN}Events completed:{Colors.RESET} {simulation.current_event_index} / {total_events}")
        print(f"{Colors.CYAN}Progress:{Colors.RESET} {simulation.progress}%")
        print()
        print(
            f"{Colors.BRIGHT_YELLOW}"
            "Each decision will affect habitat status and final performance."
            f"{Colors.RESET}"
        )
        print()
        input(f"{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")

    def _show_event_header(self, event_number: int, total_events: int) -> None:
        self._show_title(f"EVENT {event_number} OF {total_events}")

    def _show_decision_result(
        self,
        option,
        previous_state: HabitatState,
        current_state: HabitatState,
        total_score: float,
        progress: float
    ) -> None:
        self._clear_screen()
        self._show_title("DECISION RESULT")

        print(f"{Colors.BOLD}{Colors.BRIGHT_WHITE}Selected action:{Colors.RESET}")
        print(option.description)
        print()

        print(f"{Colors.BOLD}{Colors.BRIGHT_WHITE}Habitat changes:{Colors.RESET}")
        self._print_change("Energy", previous_state.energy, current_state.energy)
        self._print_change("Oxygen", previous_state.oxygen, current_state.oxygen)
        self._print_change("Integrity", previous_state.integrity, current_state.integrity)
        self._print_change("Crew health", previous_state.crew_health, current_state.crew_health)

        print()
        print(
            f"{Colors.CYAN}Score impact:{Colors.RESET} "
            f"{self._format_signed_number(option.score_impact)}"
        )
        print(f"{Colors.CYAN}Current score:{Colors.RESET} {total_score}")
        print(f"{Colors.CYAN}Simulation progress:{Colors.RESET} {progress}%")
        print()

        input(f"{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")

    def _show_habitat_state(
        self,
        habitat_state: HabitatState,
        progress: float,
        current_score: float
    ) -> None:
        print(f"{Colors.BOLD}{Colors.BRIGHT_WHITE}Current Habitat State:{Colors.RESET}")
        print(f"  {Colors.CYAN}Energy:{Colors.RESET}      {habitat_state.energy}")
        print(f"  {Colors.CYAN}Oxygen:{Colors.RESET}      {habitat_state.oxygen}")
        print(f"  {Colors.CYAN}Integrity:{Colors.RESET}   {habitat_state.integrity}")
        print(f"  {Colors.CYAN}Crew health:{Colors.RESET} {habitat_state.crew_health}")
        print()
        print(f"{Colors.CYAN}Current score:{Colors.RESET} {current_score}")
        print(f"{Colors.CYAN}Progress:{Colors.RESET} {progress}%")
        print()

    def _print_change(self, label: str, old_value: int, new_value: int) -> None:
        change = new_value - old_value

        if change > 0:
            color = Colors.GREEN
        elif change < 0:
            color = Colors.RED
        else:
            color = Colors.BRIGHT_BLACK

        print(
            f"  {Colors.CYAN}{label}:{Colors.RESET} "
            f"{old_value} -> {new_value} "
            f"{color}({self._format_signed_number(change)}){Colors.RESET}"
        )

    def _build_finished_result(
        self,
        score: float,
        events_completed: int,
        total_events: int,
        habitat_state: HabitatState
    ) -> dict:
        return {
            "status": "finished",
            "score": score,
            "events_completed": events_completed,
            "total_events": total_events,
            "habitat_state": habitat_state,
            "rating": self._rating_for(score)
        }

    def _show_title(self, title: str) -> None:
        print()
        print(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{title.center(60)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'=' * 60}{Colors.RESET}")
        print()

    def _show_message(self, message: str, message_type: str = "info") -> None:
        if message_type == "success":
            color = Colors.GREEN
            symbol = "✓"
        elif message_type == "error":
            color = Colors.RED
            symbol = "✗"
        elif message_type == "warning":
            color = Colors.YELLOW
            symbol = "!"
        else:
            color = Colors.CYAN
            symbol = "i"

        print()
        print(f"{color}{'-' * 60}{Colors.RESET}")
        print(f"{color}{symbol} {message}{Colors.RESET}")
        print(f"{color}{'-' * 60}{Colors.RESET}")

    def _copy_habitat_state(self, habitat_state: HabitatState) -> HabitatState:
        return HabitatState(
            id=habitat_state.id,
            simulation_id=habitat_state.simulation_id,
            energy=habitat_state.energy,
            oxygen=habitat_state.oxygen,
            integrity=habitat_state.integrity,
            crew_health=habitat_state.crew_health
        )

    def _format_signed_number(self, value) -> str:
        if value > 0:
            return f"+{value}"

        return str(value)

    def _rating_for(self, score: float) -> str:
        if score >= 60:
            return "Excellent"

        if score >= 30:
            return "Satisfactory"

        if score >= 0:
            return "Needs improvement"

        return "Insufficient"

    def _clear_screen(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")