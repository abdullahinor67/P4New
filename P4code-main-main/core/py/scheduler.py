import pandas as pd
from itertools import combinations
from core.py.interval_tree import IntervalTree, Interval

class Scheduler:
    GAME_DURATION = 2  # Duration of each game in hours

    @staticmethod
    def run(case: str = "case1") -> int:
        """
        Main function to schedule games based on input files and write to CSV/JSON.
        """
        # File paths
        input_teams = f"./data/{case}/team.csv"
        input_venues = f"./data/{case}/venue.csv"
        input_leagues = f"./data/{case}/league.csv"
        output_schedule_csv = f"./data/{case}/schedule.csv"
        output_schedule_json = f"./data/{case}/schedule.json"

        # Load input data
        try:
            team_df = pd.read_csv(input_teams)
            venue_df = pd.read_csv(input_venues)
            league_df = pd.read_csv(input_leagues)
        except FileNotFoundError as e:
            print(f"Error loading files for {case}: {e}")
            return -1

        # Prepare scheduling
        games = []
        interval_tree_map = {}  # Separate interval trees for each field

        # Determine scheduling logic based on case
        # For cases 5-8, we attempt a more data-driven approach.
        # We'll check if 'numberOfGames' column exists in league_df
        has_number_of_games = 'numberOfGames' in league_df.columns

        # Schedule games for each league
        league_ids = team_df["leagueId"].unique()
        for league_id in league_ids:
            teams_in_league = team_df[team_df["leagueId"] == league_id]
            team_combinations = list(combinations(teams_in_league["name"], 2))
            league_name = league_df[league_df["leagueId"] == league_id]["leagueName"].iloc[0]

            # Determine game_limit
            if case == "case1":
                # 8 Teams, 1 league, you previously set a fixed limit of 28 games
                game_limit = 28
            elif case == "case2":
                # Distribute 84 games across leagues
                # If we have multiple leagues, this divides 84 by the number_of_leagues
                game_limit = 84 // len(league_ids)
            elif case == "case3":
                # 16 teams -> C(16,2)=120 unique combinations, you mentioned schedule all 120
                game_limit = 120
            elif case == "case4":
                # 24 teams -> C(24,2)=276 unique combinations, you used that exact number
                game_limit = 276
            else:
                # Cases 5-8: Try to use numberOfGames from the league.csv if available
                if has_number_of_games:
                    league_info = league_df[league_df["leagueId"] == league_id].iloc[0]
                    league_number_of_games = league_info.get("numberOfGames", None)
                    if pd.isna(league_number_of_games) or league_number_of_games <= 0:
                        # If invalid, schedule all combinations
                        game_limit = len(team_combinations)
                    else:
                        # Use min of provided numberOfGames and available matchups
                        game_limit = min(int(league_number_of_games), len(team_combinations))
                else:
                    # If no numberOfGames column is found, schedule all combinations
                    game_limit = len(team_combinations)

            # Limit the team combinations
            team_combinations = team_combinations[:game_limit]

            # Attempt to schedule each game pair
            for team1, team2 in team_combinations:
                scheduled = Scheduler.schedule_team_pair(
                    team1, team2, league_name, venue_df, interval_tree_map, games, case
                )
                if not scheduled:
                    print(f"Could not schedule game between {team1} and {team2} for {league_name}")

        # Save schedule to files
        Scheduler.save_schedule(games, output_schedule_csv, output_schedule_json)
        print(f"Schedule for {case} successfully saved to {output_schedule_csv} and {output_schedule_json}.")
        return 0

    @staticmethod
    def schedule_team_pair(team1, team2, league_name, venue_df, interval_tree_map, games, case):
        """
        Schedule a pair of teams by iterating through weeks, days, and venues.
        For case 3, we force only one field.
        """
        for _, venue_row in venue_df.iterrows():
            fields_available = 1 if case == "case3" else int(venue_row["field"])
            # Iterate weeks available for this venue
            for week in range(venue_row["seasonStart"], venue_row["seasonEnd"] + 1):
                # Iterate days of the week
                for day in range(1, 8):
                    scheduled = Scheduler.try_schedule_game(
                        team1, team2, league_name, week, day, venue_row, interval_tree_map, case, fields_available
                    )
                    if scheduled:
                        games.append(scheduled)
                        return True
        return False

    @staticmethod
    def try_schedule_game(team1, team2, league_name, week, day, venue_row, interval_tree_map, case, fields_available):
        """
        Attempt to schedule a game at a specific venue on a given day and time.
        Two fixed time slots: 9-11 AM and 2-4 PM
        """
        game_slots = [(9, 11), (14, 16)]

        for field_id in range(1, fields_available + 1):
            if field_id not in interval_tree_map:
                interval_tree_map[field_id] = IntervalTree()

            interval_tree = interval_tree_map[field_id]

            for start, end in game_slots:
                interval = Interval(start=start, end=end, day=day, week=week)
                # Check if no overlap
                if not interval_tree.overlap(interval):
                    interval_tree.insert(interval)
                    return {
                        "team1Name": team1,
                        "team2Name": team2,
                        "week": week,
                        "day": day,
                        "start": start,
                        "end": end,
                        "season": venue_row["seasonYear"],
                        "league": league_name,
                        "location": f"{venue_row['name']} Field #{field_id}",
                    }
        return None

    @staticmethod
    def save_schedule(games, csv_path, json_path):
        """
        Save the schedule to CSV and JSON files.
        """
        if not games:
            print("No games were scheduled.")
            # Create empty schedule files
            pd.DataFrame([]).to_csv(csv_path, index=False)
            pd.DataFrame([]).to_json(json_path, orient="records", indent=2)
            return

        schedule_df = pd.DataFrame(games)
        schedule_df.to_csv(csv_path, index=False)
        schedule_df.to_json(json_path, orient="records", indent=2)


if __name__ == "__main__":
    # Run all cases
    Scheduler.run("case1")
    Scheduler.run("case2")
    Scheduler.run("case3")
    Scheduler.run("case4")
    Scheduler.run("case5")
    Scheduler.run("case6")
    Scheduler.run("case7")
    Scheduler.run("case8")
    Scheduler.run("generated")
