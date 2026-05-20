# Project HERMES

Habitat Environment & Resource Management Simulation

Project HERMES is a terminal-based Python prototype for an astronaut training simulation. The fictional mission used in the prototype is Ares-Pathfinder, a manned Mars landing mission created for an academic software engineering project.

This version contains Increment 1, which builds the base structure of the product.

## Increment 1: Product Base

This increment implements:

- terminal main menu
- user registration
- user login
- password hashing
- local SQLite database storage
- initial database schema
- seeded mission and professional roles
- repository layer for database access
- placeholder modules for future simulation, narrative, and evaluation work

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

## Current Features

When the product starts, the user can:

```text
1. Create account
2. Log in
3. Exit
```

After logging in, the user can:

```text
1. View available missions
2. View professional roles
3. Start simulation
4. Log out
```

Mission selection, role selection, and simulation execution are currently placeholders for later increments.

## Database

The product uses a local SQLite database. The database is created automatically when the product runs.

The database includes tables for:

- users
- roles
- missions
- simulations
- habitat states
- narrative events
- narrative options
- performance evaluations

Increment 1 only uses the authentication-related functionality directly, but the full base schema is prepared so later increments can build on it.

## Seed Data

The database starts with these professional roles:

- Habitat Engineer
- Planetary Scientist
- Medical Officer
- Systems Engineer

The database also starts with one mission:

- Ares-Pathfinder

## Password Storage

Passwords are not stored as plaintext.

The product uses salted password hashing through Python standard library tools:

- `os.urandom()` to generate a random salt
- `hashlib.pbkdf2_hmac()` to hash the password
- `hmac.compare_digest()` to safely compare password hashes during login

## Technologies Used

- Python
- SQLite
- pyfiglet (for ASCII art menu titles)