import sqlite3
from pathlib import Path


DB_NAME = "hermes.db"
DB_PATH = Path(__file__).parent / DB_NAME


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    # sqlite only enforces foreign keys when this is enabled
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


def initialize_database():
    connection = get_connection()

    try:
        create_tables(connection)
        ensure_database_schema(connection)
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
            current_event_index INTEGER NOT NULL DEFAULT 0,
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
            description TEXT NOT NULL,
            role_id INTEGER,
            FOREIGN KEY (role_id) REFERENCES roles(id)
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


def ensure_database_schema(connection):
    # older databases may be missing Increment 3 columns
    if not column_exists(connection, "narrative_events", "role_id"):
        connection.execute("""
            ALTER TABLE narrative_events
            ADD COLUMN role_id INTEGER;
        """)

    if not column_exists(connection, "simulations", "current_event_index"):
        connection.execute("""
            ALTER TABLE simulations
            ADD COLUMN current_event_index INTEGER NOT NULL DEFAULT 0;
        """)


def column_exists(connection, table_name: str, column_name: str) -> bool:
    cursor = connection.cursor()

    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    return any(column["name"] == column_name for column in columns)


def seed_initial_data(connection):
    seed_roles(connection)
    seed_missions(connection)
    seed_narrative_events(connection)


def seed_roles(connection):
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


def seed_missions(connection):
    cursor = connection.cursor()

    # duration is still a simple placeholder for this prototype
    cursor.execute("""
        INSERT OR IGNORE INTO missions (name, duration_days)
        VALUES (?, ?);
    """, ("Ares-Pathfinder", 30))


def seed_narrative_events(connection):
    cursor = connection.cursor()

    # do not seed again if events already exist
    cursor.execute("SELECT COUNT(*) AS count FROM narrative_events;")
    if cursor.fetchone()["count"] > 0:
        return

    role_ids = get_role_ids_by_name(connection)
    events = build_narrative_seed_data(role_ids)

    for event in events:
        cursor.execute("""
            INSERT INTO narrative_events (description, role_id)
            VALUES (?, ?);
        """, (event["description"], event["role_id"]))

        event_id = cursor.lastrowid

        for option in event["options"]:
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
                event_id,
                option["description"],
                option["energy_impact"],
                option["oxygen_impact"],
                option["integrity_impact"],
                option["crew_health_impact"],
                option["score_impact"]
            ))


def get_role_ids_by_name(connection) -> dict:
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name
        FROM roles;
    """)

    rows = cursor.fetchall()
    return {row["name"]: row["id"] for row in rows}


def build_narrative_seed_data(role_ids: dict) -> list:
    return [
        {
            "description": "The habitat oxygen system reports unstable pressure levels.",
            "role_id": None,
            "options": [
                {
                    "description": "Run a full diagnostic on the oxygen system.",
                    "energy_impact": -5,
                    "oxygen_impact": 15,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 10
                },
                {
                    "description": "Temporarily reduce oxygen flow to stabilize pressure.",
                    "energy_impact": 0,
                    "oxygen_impact": 5,
                    "integrity_impact": 0,
                    "crew_health_impact": -5,
                    "score_impact": 5
                },
                {
                    "description": "Ignore the warning and continue the mission.",
                    "energy_impact": 0,
                    "oxygen_impact": -15,
                    "integrity_impact": 0,
                    "crew_health_impact": -10,
                    "score_impact": -10
                }
            ]
        },
        {
            "description": "A Martian dust storm is approaching the habitat.",
            "role_id": None,
            "options": [
                {
                    "description": "Seal all habitat modules and wait for the storm to pass.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 10,
                    "crew_health_impact": 0,
                    "score_impact": 10
                },
                {
                    "description": "Reinforce only the most critical structures.",
                    "energy_impact": -5,
                    "oxygen_impact": 0,
                    "integrity_impact": 5,
                    "crew_health_impact": 0,
                    "score_impact": 5
                },
                {
                    "description": "Continue normal operations during the storm.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": -15,
                    "crew_health_impact": -5,
                    "score_impact": -10
                }
            ]
        },
        {
            "description": "Communication with mission control on Earth has been lost.",
            "role_id": None,
            "options": [
                {
                    "description": "Follow the established emergency communication protocol.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 5,
                    "score_impact": 10
                },
                {
                    "description": "Attempt an immediate antenna repair.",
                    "energy_impact": -10,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 5
                },
                {
                    "description": "Wait and take no immediate action.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": -10,
                    "score_impact": -10
                }
            ]
        },

        {
            "description": "A micrometeorite has punctured the habitat outer wall.",
            "role_id": role_ids["Habitat Engineer"],
            "options": [
                {
                    "description": "Apply an emergency sealant patch.",
                    "energy_impact": -5,
                    "oxygen_impact": 0,
                    "integrity_impact": 15,
                    "crew_health_impact": 0,
                    "score_impact": 10
                },
                {
                    "description": "Isolate the affected module.",
                    "energy_impact": 0,
                    "oxygen_impact": -5,
                    "integrity_impact": 10,
                    "crew_health_impact": 0,
                    "score_impact": 5
                },
                {
                    "description": "Delay the repair until later.",
                    "energy_impact": 0,
                    "oxygen_impact": -10,
                    "integrity_impact": -15,
                    "crew_health_impact": -5,
                    "score_impact": -10
                }
            ]
        },
        {
            "description": "The airlock seal is showing signs of degradation.",
            "role_id": role_ids["Habitat Engineer"],
            "options": [
                {
                    "description": "Replace the seal immediately.",
                    "energy_impact": -5,
                    "oxygen_impact": 0,
                    "integrity_impact": 15,
                    "crew_health_impact": 0,
                    "score_impact": 10
                },
                {
                    "description": "Apply lubricant and monitor the seal closely.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 5,
                    "crew_health_impact": 0,
                    "score_impact": 5
                },
                {
                    "description": "Keep using the airlock normally.",
                    "energy_impact": 0,
                    "oxygen_impact": -10,
                    "integrity_impact": -10,
                    "crew_health_impact": -5,
                    "score_impact": -10
                }
            ]
        },
        {
            "description": "The landing caused structural stress in the main habitat module.",
            "role_id": role_ids["Habitat Engineer"],
            "options": [
                {
                    "description": "Perform a full structural inspection.",
                    "energy_impact": -5,
                    "oxygen_impact": 0,
                    "integrity_impact": 15,
                    "crew_health_impact": 0,
                    "score_impact": 10
                },
                {
                    "description": "Reinforce only the visibly affected areas.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 5,
                    "crew_health_impact": 0,
                    "score_impact": 5
                },
                {
                    "description": "Assume the structure will hold.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": -15,
                    "crew_health_impact": -10,
                    "score_impact": -10
                }
            ]
        },

        {
            "description": "A promising sample collection site has been detected inside a crater.",
            "role_id": role_ids["Planetary Scientist"],
            "options": [
                {
                    "description": "Organize a careful sample collection procedure.",
                    "energy_impact": -5,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 10
                },
                {
                    "description": "Collect quick samples near the habitat instead.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 5
                },
                {
                    "description": "Skip sample collection at this site.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": -10
                }
            ]
        },
        {
            "description": "A terrain analysis instrument needs calibration.",
            "role_id": role_ids["Planetary Scientist"],
            "options": [
                {
                    "description": "Calibrate the instrument using the full protocol.",
                    "energy_impact": -5,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 10
                },
                {
                    "description": "Run a quick approximate calibration.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 5
                },
                {
                    "description": "Use the instrument without calibration.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": -10
                }
            ]
        },
        {
            "description": "An unusual mineral formation has been observed in the distance.",
            "role_id": role_ids["Planetary Scientist"],
            "options": [
                {
                    "description": "Plan a field expedition to study it.",
                    "energy_impact": -10,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": -5,
                    "score_impact": 10
                },
                {
                    "description": "Document the formation from the habitat.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 5
                },
                {
                    "description": "Ignore the mineral formation.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": -10
                }
            ]
        },

        {
            "description": "A crew member is showing symptoms of severe fatigue.",
            "role_id": role_ids["Medical Officer"],
            "options": [
                {
                    "description": "Order rest and begin medical monitoring.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 15,
                    "score_impact": 10
                },
                {
                    "description": "Give a light treatment and let the crew member keep working.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 5,
                    "score_impact": 5
                },
                {
                    "description": "Ask the crew member to continue normal duties.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": -15,
                    "score_impact": -10
                }
            ]
        },
        {
            "description": "Sensors detect elevated radiation inside one habitat module.",
            "role_id": role_ids["Medical Officer"],
            "options": [
                {
                    "description": "Evacuate the module and check the crew for exposure.",
                    "energy_impact": 0,
                    "oxygen_impact": -5,
                    "integrity_impact": 0,
                    "crew_health_impact": 15,
                    "score_impact": 10
                },
                {
                    "description": "Limit crew exposure time in the affected area.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 5,
                    "score_impact": 5
                },
                {
                    "description": "Continue operations without changes.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": -15,
                    "score_impact": -10
                }
            ]
        },
        {
            "description": "The habitat medical inventory is low on a critical supply.",
            "role_id": role_ids["Medical Officer"],
            "options": [
                {
                    "description": "Ration the supply and report the shortage.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 10,
                    "score_impact": 10
                },
                {
                    "description": "Use an available substitute.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 5,
                    "score_impact": 5
                },
                {
                    "description": "Continue using the supply without control.",
                    "energy_impact": 0,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": -10,
                    "score_impact": -10
                }
            ]
        },

        {
            "description": "Solar panel efficiency has dropped significantly.",
            "role_id": role_ids["Systems Engineer"],
            "options": [
                {
                    "description": "Clean and reorient the solar panels.",
                    "energy_impact": 15,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 10
                },
                {
                    "description": "Reduce nonessential energy consumption.",
                    "energy_impact": 5,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 5
                },
                {
                    "description": "Keep current energy usage unchanged.",
                    "energy_impact": -15,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": -5,
                    "score_impact": -10
                }
            ]
        },
        {
            "description": "The life support system reports an electronic failure.",
            "role_id": role_ids["Systems Engineer"],
            "options": [
                {
                    "description": "Repair the affected circuit immediately.",
                    "energy_impact": -5,
                    "oxygen_impact": 15,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 10
                },
                {
                    "description": "Switch to the backup life support system.",
                    "energy_impact": -5,
                    "oxygen_impact": 5,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 5
                },
                {
                    "description": "Restart the system and wait.",
                    "energy_impact": 0,
                    "oxygen_impact": -15,
                    "integrity_impact": 0,
                    "crew_health_impact": -10,
                    "score_impact": -10
                }
            ]
        },
        {
            "description": "The crew must decide how to use the backup power generator.",
            "role_id": role_ids["Systems Engineer"],
            "options": [
                {
                    "description": "Reserve it for critical emergencies only.",
                    "energy_impact": 10,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 10
                },
                {
                    "description": "Use it moderately to support habitat operations.",
                    "energy_impact": 5,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": 0,
                    "score_impact": 5
                },
                {
                    "description": "Run it at maximum output immediately.",
                    "energy_impact": -10,
                    "oxygen_impact": 0,
                    "integrity_impact": 0,
                    "crew_health_impact": -5,
                    "score_impact": -10
                }
            ]
        }
    ]