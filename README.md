# Project HERMES

Habitat Environment & Resource Management Simulation

Project HERMES is a terminal-based Python prototype for an astronaut training simulation. The fictional mission used in the prototype is Ares-Pathfinder, a manned Mars landing mission created for an academic software engineering project.

The product allows users to create an account, log in, select a mission, select a professional role, run a mission simulation, make decisions during narrative events, pause and save progress, resume a saved simulation, and receive a final performance evaluation.

## Current Version

This version includes the completed implementation of the main prototype flow:

- Increment 1: Product base
- Increment 2: Mission and role setup
- Increment 3: Mission simulation, narrative events, pause/save/resume, and final evaluation

## Features

The current prototype includes:

- terminal main menu
- user registration
- user login
- salted password hashing
- local SQLite database storage
- mission selection
- professional role selection
- setup review before starting the simulation
- role-specific narrative events
- shared mission events
- decision-based habitat state changes
- score accumulation
- final performance evaluation
- pause menu during simulation
- save progress and return to user menu
- resume saved simulation after logging back in
- ASCII art menu titles using `pyfiglet`

## How to Run

Make sure Python is installed.

Install the required dependencies:

```bash
pip install -r requirements.txt
```

From the project folder, run:

```bash
python main.py
```

The local SQLite database file will be created automatically as:

```text
hermes.db
```

## Main Menu

When the product starts, the user can:

```text
1. Create account
2. Log in
3. Exit
```

## User Menu

After logging in, the user can:

```text
1. Select mission
2. Select role
3. Review setup
4. Start simulation
5. Log out
```

If a saved simulation exists, the user will be given the option to resume it before starting a new one.

## Simulation Flow

During the simulation, the user is presented with mission events and must choose from a list of available actions.

Each decision can affect:

- habitat energy
- oxygen level
- habitat integrity
- crew health
- performance score

Each event screen also includes a pause option:

```text
0. Pause simulation
```

The pause menu allows the user to:

```text
1. Resume simulation
2. Save progress and return to user menu
3. Exit to user menu without saving a resume point
```

Saved simulations can be resumed later after logging back into the same user account.

## Professional Roles

The prototype includes four professional roles:

- Habitat Engineer
- Planetary Scientist
- Medical Officer
- Systems Engineer

Each role receives shared mission events plus role-specific narrative events.

## Mission

The prototype currently includes one mission:

- Ares-Pathfinder

Ares-Pathfinder is a fictional manned Mars landing mission used as the training scenario for this prototype.

## Database

The product uses a local SQLite database. The database is created automatically when the product runs.

The database stores:

- users
- roles
- missions
- simulations
- habitat states
- narrative events
- narrative options
- performance evaluations

The database also stores simulation progress so that paused simulations can be resumed later.

## Seed Data

The database starts with:

- four professional roles
- one mission
- shared narrative events
- role-specific narrative events
- decision options with habitat and score impacts

## Password Storage

Passwords are not stored as plaintext.

The product uses salted password hashing through Python standard library tools:

- `os.urandom()` to generate a random salt
- `hashlib.pbkdf2_hmac()` to hash the password
- `hmac.compare_digest()` to safely compare password hashes during login

## Technologies Used

- Python
- SQLite
- pyfiglet

## Notes

Project HERMES is an academic prototype. It is not intended to represent real NASA operational software, real Mars physics, classified aerospace procedures, or a production-level training platform.

The prototype runs locally through the terminal and does not require a web server, graphical interface, external API, or multiplayer functionality.