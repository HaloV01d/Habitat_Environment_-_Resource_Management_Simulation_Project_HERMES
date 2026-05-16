import os

from auth import AuthService
from models import User
from repositories import RoleRepository, MissionRepository


class TerminalInterface:
    def __init__(
        self,
        auth_service: AuthService,
        role_repository: RoleRepository,
        mission_repository: MissionRepository
    ):
        self.auth_service = auth_service
        self.role_repository = role_repository
        self.mission_repository = mission_repository

    def start(self) -> None:
        clear_menu = True
        pending_message = None

        while True:
            self._show_main_menu(clear_screen=clear_menu)

            if pending_message:
                self._show_message(pending_message)
                pending_message = None

            option = input("Select an option: ").strip()

            if option == "1":
                self._register_user()
                clear_menu = False
            elif option == "2":
                logout_message = self._login_user()

                if logout_message:
                    pending_message = logout_message
                    clear_menu = True
                else:
                    clear_menu = False
            elif option == "3":
                self._clear_screen()
                self._show_message("Exiting Project HERMES...")
                break
            else:
                self._show_message("Invalid option. Please try again.")
                clear_menu = False

    def _show_main_menu(self, clear_screen: bool = False) -> None:
        self._show_section_header("PROJECT HERMES", clear_screen)
        print("1. Create account")
        print("2. Log in")
        print("3. Exit")
        print()

    def _register_user(self) -> None:
        self._show_section_header("CREATE ACCOUNT", clear_screen=True)

        username = input("Username: ").strip()
        password = input("Password: ")

        result = self.auth_service.register(username, password)
        self._show_message(result.message)

    def _login_user(self):
        self._show_section_header("LOG IN", clear_screen=True)

        username = input("Username: ").strip()
        password = input("Password: ")

        result = self.auth_service.login(username, password)
        self._show_message(result.message)

        if result.success and result.user is not None:
            return self._show_user_menu(result.user)

        return None

    def _show_user_menu(self, user: User):
        clear_menu = True

        while True:
            self._show_section_header("USER MENU", clear_screen=clear_menu)
            print(f"Logged in as: {user.username}")
            print()
            print("1. View available missions")
            print("2. View professional roles")
            print("3. Start simulation")
            print("4. Log out")
            print()

            option = input("Select an option: ").strip()

            if option == "1":
                self._show_available_missions()
                clear_menu = False
            elif option == "2":
                self._show_available_roles()
                clear_menu = False
            elif option == "3":
                self._simulation_placeholder()
                clear_menu = False
            elif option == "4":
                return "Logged out successfully."
            else:
                self._show_message("Invalid option. Please try again.")
                clear_menu = False

    def _show_available_missions(self) -> None:
        missions = self.mission_repository.get_all_missions()

        self._show_section_header("AVAILABLE MISSIONS")

        if not missions:
            print("No missions are currently configured.")
        else:
            for mission in missions:
                print(f"{mission.id}. {mission.name} ({mission.duration_days} days)")

        print()
        print("Mission selection will be implemented in the next increment.")

    def _show_available_roles(self) -> None:
        roles = self.role_repository.get_all_roles()

        self._show_section_header("PROFESSIONAL ROLES")

        if not roles:
            print("No roles are currently configured.")
        else:
            for role in roles:
                print(f"{role.id}. {role.name}")
                print(f"   {role.description}")

        print()
        print("Role selection will be implemented in the next increment.")

    def _simulation_placeholder(self) -> None:
        self._show_section_header("SIMULATION")
        print("Simulation execution will be implemented in a later increment.")

    def _show_section_header(self, title: str, clear_screen: bool = False) -> None:
        if clear_screen:
            self._clear_screen()

        print()
        print("=" * 50)
        print(title)
        print("=" * 50)

    def _show_message(self, message: str) -> None:
        print()
        print("-" * 50)
        print(message)
        print("-" * 50)

    def _clear_screen(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")