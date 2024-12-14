
# SPORTS Scheduling System

## Overview

This project implements a basic scheduling system (SPORTS system) that generates a match schedule given input data (teams, leagues, venues). It respects per-league `numberOfGames` limits (if given) and ensures no overlapping matches on the same field. The result is a `schedule.csv` file.

---

## Setup & Running

### 1. Set Up Environment

Run the following commands:

```bash
./bin/build-env
source ./bin/run-env
```

---

### 2. Launch the Server

Run the server using:

```bash
./bin/launch
```

This runs the Python-based server by default.

---

### 3. Access the Web UI

Open your browser and go to:

```plaintext
https://localhost:8000/
```

---

### 4. Login Credentials

Use the following credentials to log in:

```plaintext
Email: user@example.com  
Password: password
```

---

## Scheduling via Web UI

1. Log in to the Web UI.  
2. Navigate to the **Schedule** page.  
3. You will see buttons for each test case (e.g., **Case 1** through **Case 8**, plus **Generated**).  
4. Click a button (e.g., "Case 1") to run that test case’s scheduler.  
5. The page will display the scheduled games or indicate if the test failed.

---

## Navigating the Server Interface

- At the top, select a case (e.g., **Case 3**) to run the scheduler for that scenario.
- Once completed, the schedule appears below with each match’s **Date, Time, League, Teams, and Location**.

### Schedule Format

- **Date/Time**: Shown in a human-readable format (e.g., `Tuesday, March 19th, 2024`, `9:00am - 11:00am`).
- **League**: Identifies which league the match belongs to.
- **Teams**: Displays the two competing teams (Team 1 vs Team 2).
- **Location**: Venue and field number where the game takes place.

> **Note:** If `numberOfGames` is invalid or missing, the scheduler will attempt to schedule all possible matchups. If a game cannot be scheduled without overlap, it will be skipped and logged.

---

## Output & Verification

- The final schedule is saved as `schedule.csv` in:

```plaintext
data/<case>/
```

- You can verify the output by:
  - Examining the `schedule.csv` file.
  - Re-running the test case.

---

## License

[Specify license here, if applicable]
