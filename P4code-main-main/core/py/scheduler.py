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

        games = []
        field_interval_map = {}
        team_interval_map = {}

        # Initialize interval trees for all teams
        all_teams = team_df["name"].unique()
        for team in all_teams:
            team_interval_map[team] = IntervalTree()

        # For daily constraints in all cases:
        team_daily_count = {}  # key: (team, season, week, day), value: count of games that day

        has_number_of_games = 'numberOfGames' in league_df.columns

        league_ids = team_df["leagueId"].unique()
        for league_id in league_ids:
            teams_in_league = team_df[team_df["leagueId"] == league_id]
            team_combinations = list(combinations(teams_in_league["name"], 2))
            league_name = league_df[league_df["leagueId"] == league_id]["leagueName"].iloc[0]

            # Determine game_limit based on the case
            if case == "case1":
                game_limit = 28
            elif case == "case2":
                game_limit = 84 // len(league_ids)
            elif case == "case3":
                game_limit = 120
            elif case == "case4":
                game_limit = 168
            else:
                # Cases 5–8 and generated
                if has_number_of_games:
                    league_info = league_df[league_df["leagueId"] == league_id].iloc[0]
                    league_number_of_games = league_info.get("numberOfGames", None)
                    if pd.isna(league_number_of_games) or league_number_of_games <= 0:
                        game_limit = len(team_combinations)
                    else:
                        game_limit = min(int(league_number_of_games), len(team_combinations))
                else:
                    game_limit = len(team_combinations)

            team_combinations = team_combinations[:game_limit]

            for team1, team2 in team_combinations:
                scheduled = Scheduler.schedule_team_pair(
                    team1, team2, league_name, venue_df,
                    field_interval_map, team_interval_map, team_daily_count, games, case
                )
                if not scheduled:
                    print(f"Could not schedule game between {team1} and {team2} for {league_name}")

        Scheduler.save_schedule(games, output_schedule_csv, output_schedule_json)
        print(f"Schedule for {case} successfully saved to {output_schedule_csv} and {output_schedule_json}.")
        return 0

    @staticmethod
    def schedule_team_pair(team1, team2, league_name, venue_df, field_interval_map, team_interval_map, team_daily_count, games, case):
        for week in range(1, 53):
            for day in range(1, 8):
                for _, venue_row in venue_df.iterrows():
                    if not Scheduler.is_within_season(week, venue_row):
                        continue

                    if Scheduler.try_schedule_game(team1, team2, league_name, week, day, venue_row,
                                                   field_interval_map, team_interval_map, team_daily_count, case, games):
                        return True
        return False

    @staticmethod
    def is_within_season(week, venue_row):
        return venue_row["seasonStart"] <= week <= venue_row["seasonEnd"]

    @staticmethod
    def try_schedule_game(team1, team2, league_name, week, day, venue_row,
                          field_interval_map, team_interval_map, team_daily_count, case, games):

        fields_available = int(venue_row["field"]) if case != "case3" else 1

        venue_start = venue_row[f"d{day}Start"]
        venue_end = venue_row[f"d{day}End"]

        # Iterate over possible time slots
        current_start = venue_start
        while current_start + Scheduler.GAME_DURATION <= venue_end:
            game_start = current_start
            game_end = game_start + Scheduler.GAME_DURATION
            interval = Interval(start=game_start, end=game_end, day=day, week=week)

            # Check daily limit for both teams
            season = venue_row["seasonYear"]
            t1_key = (team1, season, week, day)
            t2_key = (team2, season, week, day)
            if team_daily_count.get(t1_key, 0) >= 1 or team_daily_count.get(t2_key, 0) >= 1:
                # One of the teams already played this day
                current_start += Scheduler.GAME_DURATION
                continue

            scheduled = False
            for field_id in range(1, fields_available + 1):
                if field_id not in field_interval_map:
                    field_interval_map[field_id] = IntervalTree()

                field_tree = field_interval_map[field_id]

                # Check field overlap
                if field_tree.overlap(interval):
                    continue

                # Check team overlap in time
                if team_interval_map[team1].overlap(interval) or team_interval_map[team2].overlap(interval):
                    continue

                # If everything is clear, schedule the game
                field_tree.insert(interval)
                team_interval_map[team1].insert(interval)
                team_interval_map[team2].insert(interval)

                # Record daily play count for both teams
                team_daily_count[t1_key] = team_daily_count.get(t1_key, 0) + 1
                team_daily_count[t2_key] = team_daily_count.get(t2_key, 0) + 1

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
        if not games:
            print("No games were scheduled.")
            pd.DataFrame([]).to_csv(csv_path, index=False)
            pd.DataFrame([]).to_json(json_path, orient="records", indent=2)
            return

        schedule_df = pd.DataFrame(games)
        # Sort by season, week, day, start
        schedule_df = schedule_df.sort_values(by=["season", "week", "day", "start"])
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
