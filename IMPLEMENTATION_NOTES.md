# Implementation Notes

This file is just a quick guide for the next increments.

## Where things are

### main.py

Starts the product.

This file should stay simple. It initializes the database, creates the repositories/services, and starts the terminal interface.

Try not to put project logic here.

### database.py

Creates the SQLite database and all the tables.

It also adds the starting data:

- Ares-Pathfinder mission
- the four professional roles

The database file is generated automatically as:

```text
hermes.db
```

Do not commit `hermes.db` to GitHub. It is ignored on purpose.

### models.py

Contains the data classes:

- User
- Role
- Mission
- Simulation
- HabitatState
- NarrativeEvent
- NarrativeOption
- PerformanceEvaluation

These should mostly stay as simple data classes. Avoid stuffing a bunch of database or menu logic in here.

### repositories.py

This is where database access goes.

If you need to save, get, or update something from SQLite, do it through one of the repository classes.

Current repositories:

- UserRepository
- RoleRepository
- MissionRepository
- SimulationRepository
- HabitatStateRepository
- NarrativeEventRepository
- NarrativeOptionRepository
- PerformanceEvaluationRepository

### auth.py

Handles:

- account creation
- login
- password hashing
- password verification

This is already working. Most likely, you should not need to change this unless we add more user/account features.

### interface.py

Handles the terminal menus and user input.

Right now, this is where the user can:

- create account
- log in
- view available missions
- view professional roles
- see simulation placeholder
- log out

Future menu options should probably be added here, but the actual logic should still be handled by services/repositories when possible.

### simulation.py

Placeholder for simulation logic.

Use this later for setup flow, mission execution, pause/resume, landing interaction, and simulation state changes.

### narrative.py

Placeholder for narrative logic.

Use this later for mission situations, options, and consequences.

### evaluation.py

Placeholder for final scoring/evaluation logic.

Use this later for calculating and showing the user's performance result.

## What is currently a placeholder

### Mission selection

Current behavior:

- the product displays the available mission
- the user cannot actually select/save a mission yet

Useful method:

```python
MissionRepository.get_all_missions()
```

### Role selection

Current behavior:

- the product displays the available professional roles
- the user cannot actually select/save a role yet

Useful methods:

```python
RoleRepository.get_all_roles()
UserRepository.update_user_role(user_id, role_id)
```

### Simulation setup

Current behavior:

- no simulation record is created yet
- no habitat state is created yet
- no starting evaluation is created yet

Useful repositories:

```python
SimulationRepository
HabitatStateRepository
PerformanceEvaluationRepository
```

### Simulation execution

Current behavior:

- selecting "Start simulation" only prints a placeholder message

Useful files:

```text
simulation.py
interface.py
repositories.py
```

### Narrative events

Current behavior:

- no actual narrative events are loaded or presented yet

Useful repositories:

```python
NarrativeEventRepository
NarrativeOptionRepository
```

### Performance evaluation

Current behavior:

- no real score is calculated yet

Useful repository:

```python
PerformanceEvaluationRepository
```

## Suggested plan for Increment 2

Increment 2 should focus on mission setup.

The goal is to take the user from “logged in” to “ready to start the simulation.”

It should not run the full simulation yet.

Recommended order:

1. Let the user select a mission from the missions table.
2. Store the selected mission during the current session.
3. Let the user select a professional role from the roles table.
4. Save the selected role to the user record.
5. Add a setup summary before continuing.
6. Let the user confirm or change the setup.
7. After confirmation, create the starting simulation record.
8. Create the starting habitat state.
9. Create the starting performance evaluation.
10. Block the user from starting if the setup is incomplete.

Useful methods/repositories:

```python
MissionRepository.get_all_missions()
RoleRepository.get_all_roles()
UserRepository.update_user_role(user.id, role_id)
SimulationRepository
HabitatStateRepository
PerformanceEvaluationRepository
```

Suggested starting simulation values:

```text
state: ready
progress: 0.0
```

Suggested starting habitat values:

```text
energy: 100
oxygen: 100
integrity: 100
crew_health: 100
```

Suggested starting evaluation value:

```text
score: 0
```

Example setup summary:

```text
Mission Setup Summary

User: example_user
Mission: Ares-Pathfinder
Role: Habitat Engineer

1. Confirm setup
2. Change mission
3. Change role
4. Return to user menu
```

By the end of Increment 2, the product should let the user log in, select the mission, select a role, confirm the setup, and prepare the database records needed for the simulation.

## Suggested plan for Increment 3

Increment 3 should focus on actually running the simulation.

The goal is to take a prepared simulation and let the user play through mission situations.

Recommended order:

1. Load the prepared simulation record.
2. Load the current habitat state.
3. Add narrative events to the database.
4. Add options for each narrative event.
5. Present one event at a time through the terminal.
6. Let the user choose an option.
7. Apply the option's impact to the habitat state.
8. Update the performance score.
9. Add the simplified Ares-Lander landing interaction.
10. Generate and save the final performance result.

Useful repositories:

```python
SimulationRepository
HabitatStateRepository
NarrativeEventRepository
NarrativeOptionRepository
PerformanceEvaluationRepository
```

Useful files:

```text
simulation.py
narrative.py
evaluation.py
interface.py
```

Possible event format:

```text
The habitat oxygen system reports unstable pressure.

1. Run a full diagnostic.
2. Reduce oxygen flow temporarily.
3. Ignore the warning and continue the mission.
```

Possible option impact format:

```text
energy:-5, oxygen:+10, integrity:0, crew_health:0, score:+10
```

That format is just a suggestion. If a different format is easier, use that, but keep it simple.

By the end of Increment 3, the product should let the user run through mission events, make decisions, update habitat values, update the score, and receive a final evaluation.

## Important reminders

Keep the terminal interface simple.

Keep database access inside repositories.

Do not put project logic in `main.py`.

Do not commit `hermes.db` to the repository.
