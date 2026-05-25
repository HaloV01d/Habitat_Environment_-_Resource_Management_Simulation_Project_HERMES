import os
import pyfiglet

from auth import AuthService
from models import User, Simulation, HabitatState, PerformanceEvaluation
from repositories import (
    UserRepository,
    RoleRepository,
    MissionRepository,
    SimulationRepository,
    HabitatStateRepository,
    PerformanceEvaluationRepository
)


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class TerminalInterface:
    def __init__(
        self,
        auth_service: AuthService,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        mission_repository: MissionRepository,
        simulation_repository: SimulationRepository,
        habitat_state_repository: HabitatStateRepository,
        performance_evaluation_repository: PerformanceEvaluationRepository,
        simulation_runner
    ):
        self.auth_service = auth_service
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.mission_repository = mission_repository
        self.simulation_repository = simulation_repository
        self.habitat_state_repository = habitat_state_repository
        self.performance_evaluation_repository = performance_evaluation_repository
        self.simulation_runner = simulation_runner

    def start(self) -> None:
        pending_message = None

        while True:
            self._show_main_menu()

            if pending_message:
                self._show_message(pending_message, "success")
                pending_message = None

            option = input(f"{Colors.BRIGHT_CYAN}Select an option: {Colors.RESET}").strip()

            if option == "1":
                self._register_user()
            elif option == "2":
                logout_message = self._login_user()

                if logout_message:
                    pending_message = logout_message
            elif option == "3":
                self._clear_screen()
                self._show_message("Exiting Project HERMES...", "info")
                break
            else:
                self._show_message("Invalid option. Please try again.", "error")
                self._pause()

    def _show_main_menu(self) -> None:
        self._show_section_header("PROJECT HERMES")
        print(f"{Colors.BRIGHT_GREEN}1.{Colors.RESET} Create account")
        print(f"{Colors.BRIGHT_BLUE}2.{Colors.RESET} Log in")
        print(f"{Colors.BRIGHT_RED}3.{Colors.RESET} Exit")
        print()

    def _register_user(self) -> None:
        self._show_section_header("CREATE ACCOUNT")

        username = input(f"{Colors.CYAN}Username: {Colors.RESET}").strip()
        password = input(f"{Colors.CYAN}Password: {Colors.RESET}")

        result = self.auth_service.register(username, password)
        message_type = "success" if result.success else "error"

        self._show_message(result.message, message_type)
        self._pause()

    def _login_user(self):
        self._show_section_header("LOG IN")

        username = input(f"{Colors.CYAN}Username: {Colors.RESET}").strip()
        password = input(f"{Colors.CYAN}Password: {Colors.RESET}")

        result = self.auth_service.login(username, password)
        message_type = "success" if result.success else "error"

        self._show_message(result.message, message_type)

        if result.success and result.user is not None:
            self._pause()
            return self._show_user_menu(result.user)

        self._pause()
        return None

    def _show_user_menu(self, user: User):
        selected_mission = None
        selected_role = None

        while True:
            self._show_section_header("USER MENU")
            print(f"{Colors.BOLD}{Colors.YELLOW}Logged in as: {user.username}{Colors.RESET}")
            print()
            print(f"{Colors.BRIGHT_MAGENTA}1.{Colors.RESET} Select mission")
            print(f"{Colors.BRIGHT_CYAN}2.{Colors.RESET} Select role")
            print(f"{Colors.BRIGHT_YELLOW}3.{Colors.RESET} Review setup")
            print(f"{Colors.BRIGHT_GREEN}4.{Colors.RESET} Start simulation")
            print(f"{Colors.BRIGHT_RED}5.{Colors.RESET} Log out")
            print()

            option = input(f"{Colors.BRIGHT_CYAN}Select an option: {Colors.RESET}").strip()

            if option == "1":
                selected_mission = self._select_mission()
            elif option == "2":
                selected_role = self._select_role(user)
            elif option == "3":
                self._show_setup_summary(user, selected_mission, selected_role)
            elif option == "4":
                self._start_simulation(user, selected_mission, selected_role)
            elif option == "5":
                return "Logged out successfully."
            else:
                self._show_message("Invalid option. Please try again.", "error")
                self._pause()

    def _select_mission(self):
        missions = self.mission_repository.get_all_missions()

        self._show_section_header("SELECT MISSION")

        if not missions:
            print(f"{Colors.YELLOW}No missions are currently configured.{Colors.RESET}")
            self._pause()
            return None

        for mission in missions:
            print(
                f"{Colors.BRIGHT_MAGENTA}{mission.id}.{Colors.RESET} "
                f"{Colors.BOLD}{mission.name}{Colors.RESET} "
                f"{Colors.BRIGHT_BLACK}({mission.duration_days} days){Colors.RESET}"
            )

        print()
        choice = input(
            f"{Colors.CYAN}Select a mission (or press Enter to cancel): {Colors.RESET}"
        ).strip()

        if not choice:
            self._show_message("Mission selection cancelled.", "info")
            self._pause()
            return None

        try:
            mission_id = int(choice)
            selected_mission = next((m for m in missions if m.id == mission_id), None)

            if selected_mission:
                self._show_message(
                    f"Mission '{selected_mission.name}' selected.",
                    "success"
                )
                self._pause()
                return selected_mission

            self._show_message("Invalid mission selection.", "error")
            self._pause()
            return None

        except ValueError:
            self._show_message("Invalid input. Please enter a number.", "error")
            self._pause()
            return None

    def _select_role(self, user: User):
        roles = self.role_repository.get_all_roles()

        self._show_section_header("SELECT ROLE")

        if not roles:
            print(f"{Colors.YELLOW}No roles are currently configured.{Colors.RESET}")
            self._pause()
            return None

        for role in roles:
            print(f"{Colors.BRIGHT_CYAN}{role.id}.{Colors.RESET} {Colors.BOLD}{role.name}{Colors.RESET}")
            print(f"   {Colors.BRIGHT_BLACK}{role.description}{Colors.RESET}")
            print()

        choice = input(
            f"{Colors.CYAN}Select a role (or press Enter to cancel): {Colors.RESET}"
        ).strip()

        if not choice:
            self._show_message("Role selection cancelled.", "info")
            self._pause()
            return None

        try:
            role_id = int(choice)
            selected_role = next((r for r in roles if r.id == role_id), None)

            if selected_role:
                self.user_repository.update_user_role(user.id, role_id)
                user.role_id = role_id

                self._show_message(
                    f"Role '{selected_role.name}' assigned.",
                    "success"
                )
                self._pause()
                return selected_role

            self._show_message("Invalid role selection.", "error")
            self._pause()
            return None

        except ValueError:
            self._show_message("Invalid input. Please enter a number.", "error")
            self._pause()
            return None

    def _show_setup_summary(self, user: User, selected_mission, selected_role):
        self._show_section_header("MISSION SETUP SUMMARY")

        print(f"{Colors.CYAN}User:{Colors.RESET} {Colors.BOLD}{user.username}{Colors.RESET}")

        if selected_mission:
            print(
                f"{Colors.CYAN}Mission:{Colors.RESET} "
                f"{Colors.BOLD}{Colors.GREEN}{selected_mission.name}{Colors.RESET}"
            )
        else:
            print(f"{Colors.CYAN}Mission:{Colors.RESET} {Colors.YELLOW}Not selected{Colors.RESET}")

        if selected_role:
            print(
                f"{Colors.CYAN}Role:{Colors.RESET} "
                f"{Colors.BOLD}{Colors.GREEN}{selected_role.name}{Colors.RESET}"
            )
        else:
            print(f"{Colors.CYAN}Role:{Colors.RESET} {Colors.YELLOW}Not selected{Colors.RESET}")

        print()

        if not selected_mission or not selected_role:
            print(f"{Colors.RED}Setup is incomplete. Please select both a mission and a role.{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}Setup is complete and ready for simulation.{Colors.RESET}")

        self._pause()

    def _start_simulation(self, user: User, selected_mission, selected_role):
        paused_simulation = self.simulation_repository.get_latest_paused_by_user(
            user.id
        )

        if paused_simulation is not None:
            resume_choice = self._show_saved_simulation_prompt(user, paused_simulation)

            if resume_choice == "resume":
                return self._resume_simulation(user, paused_simulation)

            if resume_choice == "cancel":
                return False

        return self._start_new_simulation(user, selected_mission, selected_role)

    def _show_saved_simulation_prompt(
        self,
        user: User,
        paused_simulation: Simulation
    ) -> str:
        mission = self.mission_repository.get(paused_simulation.mission_id)
        role = self.role_repository.get(user.role_id) if user.role_id else None

        while True:
            self._show_section_header("SAVED SIMULATION")

            print(f"{Colors.BRIGHT_YELLOW}A saved simulation was found.{Colors.RESET}")
            print()

            print(f"{Colors.CYAN}User:{Colors.RESET} {Colors.BOLD}{user.username}{Colors.RESET}")

            if mission:
                print(f"{Colors.CYAN}Mission:{Colors.RESET} {Colors.BOLD}{mission.name}{Colors.RESET}")
            else:
                print(f"{Colors.CYAN}Mission:{Colors.RESET} {Colors.RED}Unknown{Colors.RESET}")

            if role:
                print(f"{Colors.CYAN}Role:{Colors.RESET} {Colors.BOLD}{role.name}{Colors.RESET}")
            else:
                print(f"{Colors.CYAN}Role:{Colors.RESET} {Colors.RED}Unknown{Colors.RESET}")

            print(f"{Colors.CYAN}Progress:{Colors.RESET} {paused_simulation.progress}%")
            print(f"{Colors.CYAN}Completed events:{Colors.RESET} {paused_simulation.current_event_index}")
            print()

            print(f"{Colors.BRIGHT_GREEN}1.{Colors.RESET} Resume saved simulation")
            print(f"{Colors.BRIGHT_YELLOW}2.{Colors.RESET} Start new simulation")
            print(f"{Colors.BRIGHT_RED}3.{Colors.RESET} Cancel")
            print()

            choice = input(f"{Colors.BRIGHT_CYAN}Select an option: {Colors.RESET}").strip()

            if choice == "1":
                return "resume"

            if choice == "2":
                return "new"

            if choice == "3":
                return "cancel"

            self._show_message("Invalid option. Please try again.", "error")
            self._pause()

    def _resume_simulation(self, user: User, paused_simulation: Simulation):
        self._show_section_header("RESUME SIMULATION")

        mission = self.mission_repository.get(paused_simulation.mission_id)
        role = self.role_repository.get(user.role_id) if user.role_id else None

        if mission is None:
            self._show_message("Cannot resume simulation: mission was not found.", "error")
            self._pause()
            return False

        if role is None:
            self._show_message("Cannot resume simulation: role was not found.", "error")
            self._pause()
            return False

        print(f"{Colors.GREEN}Ready to resume saved simulation.{Colors.RESET}")
        print()
        print(f"{Colors.CYAN}Mission:{Colors.RESET} {Colors.BOLD}{mission.name}{Colors.RESET}")
        print(f"{Colors.CYAN}Role:{Colors.RESET} {Colors.BOLD}{role.name}{Colors.RESET}")
        print(f"{Colors.CYAN}Progress:{Colors.RESET} {paused_simulation.progress}%")
        print(f"{Colors.CYAN}Completed events:{Colors.RESET} {paused_simulation.current_event_index}")
        print()

        self._pause("Press Enter to resume the mission...")

        result = self.simulation_runner.run(paused_simulation, role)

        self._show_simulation_result(result)
        return True

    def _start_new_simulation(self, user: User, selected_mission, selected_role):
        self._show_section_header("START SIMULATION")

        if not selected_mission:
            self._show_message("Cannot start simulation: No mission selected.", "error")
            self._pause()
            return False

        if not selected_role:
            self._show_message("Cannot start simulation: No role selected.", "error")
            self._pause()
            return False

        simulation = Simulation(
            id=None,
            user_id=user.id,
            mission_id=selected_mission.id,
            state="ready",
            progress=0.0,
            current_event_index=0
        )

        simulation = self.simulation_repository.save(simulation)

        habitat_state = HabitatState(
            id=None,
            simulation_id=simulation.id,
            energy=100,
            oxygen=100,
            integrity=100,
            crew_health=100
        )

        self.habitat_state_repository.save(habitat_state)

        evaluation = PerformanceEvaluation(
            id=None,
            simulation_id=simulation.id,
            score=0
        )

        self.performance_evaluation_repository.save(evaluation)

        print(f"{Colors.GREEN}Simulation initialized successfully!{Colors.RESET}")
        print()
        print(f"{Colors.CYAN}Mission:{Colors.RESET} {Colors.BOLD}{selected_mission.name}{Colors.RESET}")
        print(f"{Colors.CYAN}Role:{Colors.RESET} {Colors.BOLD}{selected_role.name}{Colors.RESET}")
        print()
        print(f"{Colors.BRIGHT_YELLOW}The mission begins now. Make your decisions carefully.{Colors.RESET}")
        print()

        self._pause("Press Enter to begin the mission...")

        result = self.simulation_runner.run(simulation, selected_role)

        self._show_simulation_result(result)
        return True

    def _show_simulation_result(self, result) -> None:
        status = result.get("status", "finished")

        if status == "saved":
            self._show_section_header("SIMULATION SAVED")
            self._show_message(result["message"], "success")
            self._show_partial_result(result)
            self._pause()
            return

        if status == "cancelled":
            self._show_section_header("SIMULATION EXITED")
            self._show_message(result["message"], "warning")
            self._show_partial_result(result)
            self._pause()
            return

        self._show_section_header("MISSION RESULT")

        if status == "error" or "error" in result:
            self._show_message(result["error"], "error")
            self._pause()
            return

        self._show_full_result(result)
        self._pause()

    def _show_partial_result(self, result) -> None:
        habitat = result["habitat_state"]

        print()
        print(f"{Colors.CYAN}Events completed:{Colors.RESET} "
              f"{result['events_completed']} / {result['total_events']}")
        print(f"{Colors.CYAN}Current score:{Colors.RESET} {result['score']}")
        print(f"{Colors.CYAN}Current rating:{Colors.RESET} {result['rating']}")
        print()

        print(f"{Colors.BOLD}Current habitat state:{Colors.RESET}")
        print(f"  {Colors.CYAN}Energy:{Colors.RESET}      {habitat.energy}")
        print(f"  {Colors.CYAN}Oxygen:{Colors.RESET}      {habitat.oxygen}")
        print(f"  {Colors.CYAN}Integrity:{Colors.RESET}   {habitat.integrity}")
        print(f"  {Colors.CYAN}Crew health:{Colors.RESET} {habitat.crew_health}")

    def _show_full_result(self, result) -> None:
        habitat = result["habitat_state"]

        print(f"{Colors.CYAN}Events completed:{Colors.RESET} "
              f"{result['events_completed']} / {result['total_events']}")
        print()

        print(f"{Colors.BOLD}Final habitat state:{Colors.RESET}")
        print(f"  {Colors.CYAN}Energy:{Colors.RESET}      {habitat.energy}")
        print(f"  {Colors.CYAN}Oxygen:{Colors.RESET}      {habitat.oxygen}")
        print(f"  {Colors.CYAN}Integrity:{Colors.RESET}   {habitat.integrity}")
        print(f"  {Colors.CYAN}Crew health:{Colors.RESET} {habitat.crew_health}")
        print()

        print(f"{Colors.BOLD}{Colors.BRIGHT_GREEN}Performance score: "
              f"{result['score']}{Colors.RESET}")
        print(f"{Colors.BOLD}Rating: {result['rating']}{Colors.RESET}")

    def _show_section_header(self, title: str) -> None:
        self._clear_screen()
        print()

        ascii_art = pyfiglet.figlet_format(title, font="slant")

        print(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{ascii_art}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'=' * 60}{Colors.RESET}")
        print()

    def _show_message(self, message: str, message_type: str = "info") -> None:
        print()

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

        print(f"{color}{'-' * 60}{Colors.RESET}")
        print(f"{color}{symbol} {message}{Colors.RESET}")
        print(f"{color}{'-' * 60}{Colors.RESET}")

    def _pause(self, message: str = "Press Enter to continue.") -> None:
        print()
        input(f"{Colors.BRIGHT_CYAN}{message}{Colors.RESET}")

    def _clear_screen(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")