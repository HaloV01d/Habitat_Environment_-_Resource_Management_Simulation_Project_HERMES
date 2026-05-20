import os
import pyfiglet

from auth import AuthService
from models import User, Mission, Role, Simulation, HabitatState, PerformanceEvaluation
from repositories import (
    UserRepository,
    RoleRepository,
    MissionRepository,
    SimulationRepository,
    HabitatStateRepository,
    PerformanceEvaluationRepository
)

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright foreground colors
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
        performance_evaluation_repository: PerformanceEvaluationRepository
    ):
        self.auth_service = auth_service
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.mission_repository = mission_repository
        self.simulation_repository = simulation_repository
        self.habitat_state_repository = habitat_state_repository
        self.performance_evaluation_repository = performance_evaluation_repository

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

    def _login_user(self):
        self._show_section_header("LOG IN")

        username = input(f"{Colors.CYAN}Username: {Colors.RESET}").strip()
        password = input(f"{Colors.CYAN}Password: {Colors.RESET}")

        result = self.auth_service.login(username, password)
        message_type = "success" if result.success else "error"
        self._show_message(result.message, message_type)

        if result.success and result.user is not None:
            return self._show_user_menu(result.user)

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

    def _select_mission(self):
        missions = self.mission_repository.get_all_missions()

        self._show_section_header("SELECT MISSION")

        if not missions:
            print(f"{Colors.YELLOW}No missions are currently configured.{Colors.RESET}")
            self._show_message("Press Enter to continue.", "info")
            input()
            return None

        for mission in missions:
            print(f"{Colors.BRIGHT_MAGENTA}{mission.id}.{Colors.RESET} {Colors.BOLD}{mission.name}{Colors.RESET} {Colors.BRIGHT_BLACK}({mission.duration_days} days){Colors.RESET}")

        print()
        choice = input(f"{Colors.CYAN}Select a mission (or press Enter to cancel): {Colors.RESET}").strip()

        if not choice:
            return None

        try:
            mission_id = int(choice)
            selected_mission = next((m for m in missions if m.id == mission_id), None)

            if selected_mission:
                self._show_message(f"Mission '{selected_mission.name}' selected.", "success")
                return selected_mission
            else:
                self._show_message("Invalid mission selection.", "error")
                return None
        except ValueError:
            self._show_message("Invalid input. Please enter a number.", "error")
            return None

    def _select_role(self, user: User):
        roles = self.role_repository.get_all_roles()

        self._show_section_header("SELECT ROLE")

        if not roles:
            print(f"{Colors.YELLOW}No roles are currently configured.{Colors.RESET}")
            self._show_message("Press Enter to continue.", "info")
            input()
            return None

        for role in roles:
            print(f"{Colors.BRIGHT_CYAN}{role.id}.{Colors.RESET} {Colors.BOLD}{role.name}{Colors.RESET}")
            print(f"   {Colors.BRIGHT_BLACK}{role.description}{Colors.RESET}")
            print()

        choice = input(f"{Colors.CYAN}Select a role (or press Enter to cancel): {Colors.RESET}").strip()

        if not choice:
            return None

        try:
            role_id = int(choice)
            selected_role = next((r for r in roles if r.id == role_id), None)

            if selected_role:
                self.user_repository.update_user_role(user.id, role_id)
                user.role_id = role_id
                self._show_message(f"Role '{selected_role.name}' assigned.", "success")
                return selected_role
            else:
                self._show_message("Invalid role selection.", "error")
                return None
        except ValueError:
            self._show_message("Invalid input. Please enter a number.", "error")
            return None

    def _show_setup_summary(self, user: User, selected_mission, selected_role):
        self._show_section_header("MISSION SETUP SUMMARY")
        
        print(f"{Colors.CYAN}User:{Colors.RESET} {Colors.BOLD}{user.username}{Colors.RESET}")
        
        if selected_mission:
            print(f"{Colors.CYAN}Mission:{Colors.RESET} {Colors.BOLD}{Colors.GREEN}{selected_mission.name}{Colors.RESET}")
        else:
            print(f"{Colors.CYAN}Mission:{Colors.RESET} {Colors.YELLOW}Not selected{Colors.RESET}")
        
        if selected_role:
            print(f"{Colors.CYAN}Role:{Colors.RESET} {Colors.BOLD}{Colors.GREEN}{selected_role.name}{Colors.RESET}")
        else:
            print(f"{Colors.CYAN}Role:{Colors.RESET} {Colors.YELLOW}Not selected{Colors.RESET}")
        
        print()
        
        if not selected_mission or not selected_role:
            print(f"{Colors.RED}Setup is incomplete. Please select both a mission and a role.{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}Setup is complete and ready for simulation.{Colors.RESET}")
        
        print()
        self._show_message("Press Enter to continue.", "info")
        input()

    def _start_simulation(self, user: User, selected_mission, selected_role):
        self._show_section_header("START SIMULATION")

        # Check if setup is complete
        if not selected_mission:
            self._show_message("Cannot start simulation: No mission selected.", "error")
            return False

        if not selected_role:
            self._show_message("Cannot start simulation: No role selected.", "error")
            return False

        # Create simulation record
        simulation = Simulation(
            id=None,
            user_id=user.id,
            mission_id=selected_mission.id,
            state="ready",
            progress=0.0
        )
        simulation = self.simulation_repository.save(simulation)

        # Create initial habitat state
        habitat_state = HabitatState(
            id=None,
            simulation_id=simulation.id,
            energy=100,
            oxygen=100,
            integrity=100,
            crew_health=100
        )
        self.habitat_state_repository.save(habitat_state)

        # Create initial performance evaluation
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
        print(f"{Colors.YELLOW}Simulation will be fully implemented in Increment 3.{Colors.RESET}")
        print()
        self._show_message("Press Enter to continue.", "info")
        input()
        
        return True

    def _show_section_header(self, title: str) -> None:
        self._clear_screen()
        print()
        # Generate ASCII art using pyfiglet
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
        else:  # info
            color = Colors.CYAN
            symbol = "i"
        
        print(f"{color}{'-' * 60}{Colors.RESET}")
        print(f"{color}{symbol} {message}{Colors.RESET}")
        print(f"{color}{'-' * 60}{Colors.RESET}")

    def _clear_screen(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")