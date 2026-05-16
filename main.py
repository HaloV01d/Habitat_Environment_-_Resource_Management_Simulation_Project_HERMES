from database import initialize_database, get_connection
from repositories import UserRepository, RoleRepository, MissionRepository
from auth import AuthService
from interface import TerminalInterface


def main():
    connection = None

    try:
        initialize_database()
        connection = get_connection()

        user_repository = UserRepository(connection)
        role_repository = RoleRepository(connection)
        mission_repository = MissionRepository(connection)

        auth_service = AuthService(user_repository)

        terminal_interface = TerminalInterface(
            auth_service,
            role_repository,
            mission_repository
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