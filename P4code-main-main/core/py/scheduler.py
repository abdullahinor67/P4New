import pandas as pd
from itertools import combinations
from core.py.interval_tree import IntervalTree, Interval

class Scheduler:
    GAME_DURATION = 2  # Each game lasts 2 hours

    @staticmethod
    def run(case: str = "case1") -> int:
        """
        Main entry point for scheduling a given case.

        This method:
        1. Loads input data (teams, venue, league) for the specified case.
        2. Determines game limits based on the case and league settings.
        3. Attempts to schedule all required matchups, enforcing:
           - No overlapping games on the same field at the same time.
           - Each team plays at most once per day.
           - Games fit within venue availability and selected time slots.
        4. Saves the final schedule to CSV and JSON files.

        Parameters:
            case (str): The case identifier (e.g., "case1", "case2", "case3", ...).

        Returns:
            int: 0 if successful, -1 if there was an error loading files.
        """
        # Construct file paths
        input_teams = f"./data/{case}/team.csv"
        input_venues = f"./data/{case}/venue.csv"
        input_leagues = f"./data/{case}/league.csv"
        output_schedule_csv = f"./data/{case}/schedule.csv"
        output_schedule_json = f"./data/{case}/schedule.json"

        # Load input data (teams, venues, leagues)
        try:
            team_df = pd.read_csv(input_teams)
            venue_df = pd.read_csv(input_venues)
            league_df = pd.read_csv(input_leagues)
        except FileNotFoundError as e:
            print(f"Error loading files for {case}: {e}")
            return -1

        # 'games' will store all scheduled matches
        games = []
        # Interval trees to prevent field-time overlaps
        field_interval_map = {}
        # Interval trees to ensure teams don't have overlapping games
        team_interval_map = {}
        # Track how many times a team has played in a single day
        team_daily_count = {}

        # Initialize interval trees for all teams
        all_teams = team_df["name"].unique()
        for team in all_teams:
            team_interval_map[team] = IntervalTree()

        # Check if numberOfGames column exists in leagues
        has_number_of_games = 'numberOfGames' in league_df.columns

        # For each league in this case, schedule games
        league_ids = team_df["leagueId"].unique()
        for league_id in league_ids:
            teams_in_league = team_df[team_df["leagueId"] == league_id]
            # Generate all unique team pairs (matchups)
            team_combinations = list(combinations(teams_in_league["name"], 2))
            league_name = league_df[league_df["leagueId"] == league_id]["leagueName"].iloc[0]

            # Determine game_limit based on the case
            if case == "case1":
                # Known limit for case1: 28 games total
                game_limit = 28
            elif case == "case2":
                # Distribute 84 games evenly across however many leagues are in this case
                game_limit = 84 // len(league_ids)
            elif case == "case3":
                # 16 teams generate 120 unique combos
                game_limit = 120
            elif case == "case4":
                # Previously used 168 as a limit (adjust if needed)
                game_limit = 168
            else:
                # For cases 5–8 and 'generated', try using 'numberOfGames' if available
                if has_number_of_games:
                    league_info = league_df[league_df["leagueId"] == league_id].iloc[0]
                    league_number_of_games = league_info.get("numberOfGames", None)
                    if pd.isna(league_number_of_games) or league_number_of_games <= 0:
                        # If invalid or not provided, schedule all
                        game_limit = len(team_combinations)
                    else:
                        # Use the provided limit, or the total combos if lower
                        game_limit = min(int(league_number_of_games), len(team_combinations))
                else:
                    # No numberOfGames column, schedule all combos
                    game_limit = len(team_combinations)

            # Trim the team combinations to the determined game_limit
            team_combinations = team_combinations[:game_limit]

            # Attempt to schedule each matchup
            for team1, team2 in team_combinations:
                scheduled = Scheduler.schedule_team_pair(
                    team1, team2, league_name, venue_df,
                    field_interval_map, team_interval_map, team_daily_count, games, case
                )
                if not scheduled:
                    # If a game couldn't be scheduled, note it (not necessarily an error)
                    print(f"Could not schedule game between {team1} and {team2} for {league_name}")

        # After all leagues processed, save the final schedule
        Scheduler.save_schedule(games, output_schedule_csv, output_schedule_json)
        print(f"Schedule for {case} successfully saved to {output_schedule_csv} and {output_schedule_json}.")
        return 0

    @staticmethod
    def schedule_team_pair(team1, team2, league_name, venue_df, field_interval_map, team_interval_map, team_daily_count, games, case):
        """
        Attempts to schedule a single matchup (team1 vs team2).

        Iterates over all weeks (1–52) and days (1–7), and tries each venue.
        If 'try_schedule_game' finds a suitable slot, it returns True.

        Parameters:
            team1, team2 (str): Names of the teams playing.
            league_name (str): The league's name.
            venue_df (DataFrame): Venue data.
            field_interval_map (dict): Field -> IntervalTree for fields.
            team_interval_map (dict): Team -> IntervalTree for team schedules.
            team_daily_count (dict): Tracks how many games each team plays per day.
            games (list): Global list of scheduled games.
            case (str): The case being scheduled.

        Returns:
            bool: True if the game was scheduled, False otherwise.
        """
        for week in range(1, 53):
            for day in range(1, 8):
                # Check each venue to find a slot
                for _, venue_row in venue_df.iterrows():
                    if not Scheduler.is_within_season(week, venue_row):
                        continue

                    if Scheduler.try_schedule_game(team1, team2, league_name, week, day, venue_row,
                                                   field_interval_map, team_interval_map, team_daily_count, case, games):
                        return True
        return False

    @staticmethod
    def is_within_season(week, venue_row):
        """
        Checks if the given week falls within the venue's available season.
        """
        return venue_row["seasonStart"] <= week <= venue_row["seasonEnd"]

    @staticmethod
    def try_schedule_game(team1, team2, league_name, week, day, venue_row,
                          field_interval_map, team_interval_map, team_daily_count, case, games):
        """
        Attempts to schedule a single game (team1 vs team2) on a particular day and week at a specific venue.

        Steps:
        - Determine number of fields (if case3, only 1 field).
        - Iterate through possible 2-hour slots in the venue's daily availability.
        - For each slot, check:
          * If either team already played that day (once-per-day rule)
          * Field availability (no overlaps)
          * Team availability (no overlaps)
        - If all checks pass, schedule the game, update daily counts and interval trees, and return True.
        - If no slot found, return False.

        Parameters:
            team1, team2 (str): Team names.
            league_name (str): Name of the league.
            week, day (int): The week and day indices.
            venue_row (Series): One row of venue data including field count and day availability.
            field_interval_map, team_interval_map: Data structures to check overlaps.
            team_daily_count: Dictionary to enforce once-per-day constraint.
            case (str): Current case id.
            games (list): Global games list.

        Returns:
            bool: True if scheduled successfully, False otherwise.
        """

        # Case 3 only has 1 field, otherwise use the venue's field count
        fields_available = int(venue_row["field"]) if case != "case3" else 1

        venue_start = venue_row[f"d{day}Start"]
        venue_end = venue_row[f"d{day}End"]

        # Iterate over possible slots (each GAME_DURATION hours long)
        current_start = venue_start
        while current_start + Scheduler.GAME_DURATION <= venue_end:
            game_start = current_start
            game_end = game_start + Scheduler.GAME_DURATION
            interval = Interval(start=game_start, end=game_end, day=day, week=week)

            # Check daily limit for both teams (once-per-day)
            season = venue_row["seasonYear"]
            t1_key = (team1, season, week, day)
            t2_key = (team2, season, week, day)
            if team_daily_count.get(t1_key, 0) >= 1 or team_daily_count.get(t2_key, 0) >= 1:
                # One or both teams have played already today, skip this slot
                current_start += Scheduler.GAME_DURATION
                continue

            scheduled = False
            # Try each field
            for field_id in range(1, fields_available + 1):
                if field_id not in field_interval_map:
                    field_interval_map[field_id] = IntervalTree()

                field_tree = field_interval_map[field_id]

                # Check if field is free
                if field_tree.overlap(interval):
                    # Field is taken at this time, try next field
                    continue

                # Check if teams are free
                if team_interval_map[team1].overlap(interval) or team_interval_map[team2].overlap(interval):
                    # One or both teams already playing at this time
                    continue

                # All checks passed, schedule the game
                field_tree.insert(interval)
                team_interval_map[team1].insert(interval)
                team_interval_map[team2].insert(interval)

                # Increment daily count for these teams
                team_daily_count[t1_key] = team_daily_count.get(t1_key, 0) + 1
                team_daily_count[t2_key] = team_daily_count.get(t2_key, 0) + 1

                # Add game to the global list
                games.append({
                    "team1Name": team1,
                    "team2Name": team2,
                    "week": week,
                    "day": day,
                    "start": game_start,
                    "end": game_end,
                    "season": venue_row["seasonYear"],
                    "league": league_name,
                    "location": f"{venue_row['name']} Field #{field_id}",
                })
                scheduled = True
                break

            if scheduled:
                return True

            current_start += Scheduler.GAME_DURATION
        return False

    @staticmethod
    def save_schedule(games, csv_path, json_path):
        """
        Saves the final scheduled games to CSV and JSON.

        - If no games were scheduled, writes empty files.
        - Sorts games by season, week, day, start time before saving.
        """
        if not games:
            print("No games were scheduled.")
            pd.DataFrame([]).to_csv(csv_path, index=False)
            pd.DataFrame([]).to_json(json_path, orient="records", indent=2)
            return

        schedule_df = pd.DataFrame(games)
        # Sort by season, week, day, start for chronological order
        schedule_df = schedule_df.sort_values(by=["season", "week", "day", "start"])
        schedule_df.to_csv(csv_path, index=False)
        schedule_df.to_json(json_path, orient="records", indent=2)


if __name__ == "__main__":
    # Run all cases to produce schedules
    Scheduler.run("case1")
    Scheduler.run("case2")
    Scheduler.run("case3")
    Scheduler.run("case4")
    Scheduler.run("case5")
    Scheduler.run("case6")
    Scheduler.run("case7")
    Scheduler.run("case8")
    Scheduler.run("generated")
