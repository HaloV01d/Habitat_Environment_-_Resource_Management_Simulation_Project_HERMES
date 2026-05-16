import sqlite3
from pathlib import Path


DB_NAME = "hermes.db"
DB_PATH = Path(__file__).parent / DB_NAME


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    # sqlite does not enforce foreign keys unless this is enabled
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


def initialize_database():
    connection = get_connection()

    try:
        create_tables(connection)
        seed_initial_data(connection)
        connection.commit()
    except sqlite3.Error as error:
        print(f"Database error: {error}")
    finally:
        connection.close()


def create_tables(connection):
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            role_id INTEGER,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            duration_days INTEGER NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mission_id INTEGER NOT NULL,
            state TEXT NOT NULL,
            progress REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (mission_id) REFERENCES missions(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habitat_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            simulation_id INTEGER NOT NULL UNIQUE,
            energy INTEGER NOT NULL,
            oxygen INTEGER NOT NULL,
            integrity INTEGER NOT NULL,
            crew_health INTEGER NOT NULL,
            FOREIGN KEY (simulation_id) REFERENCES simulations(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS narrative_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS narrative_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            energy_impact INTEGER NOT NULL DEFAULT 0,
            oxygen_impact INTEGER NOT NULL DEFAULT 0,
            integrity_impact INTEGER NOT NULL DEFAULT 0,
            crew_health_impact INTEGER NOT NULL DEFAULT 0,
            score_impact REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (event_id) REFERENCES narrative_events(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            simulation_id INTEGER NOT NULL UNIQUE,
            score REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (simulation_id) REFERENCES simulations(id)
        );
    """)


def seed_initial_data(connection):
    cursor = connection.cursor()

    roles = [
        (
            "Habitat Engineer",
            "Responsible for habitat maintenance, infrastructure, and resource systems."
        ),
        (
            "Planetary Scientist",
            "Responsible for exploration tasks, sample collection, and surface analysis."
        ),
        (
            "Medical Officer",
            "Responsible for crew health, medical decisions, and emergency response."
        ),
        (
            "Systems Engineer",
            "Responsible for technical systems, diagnostics, and mission support equipment."
        )
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO roles (name, description)
        VALUES (?, ?);
    """, roles)

    # duration is a placeholder for now because the final mission length has not been implemented yet
    cursor.execute("""
        INSERT OR IGNORE INTO missions (name, duration_days)
        VALUES (?, ?);
    """, ("Ares-Pathfinder", 30))