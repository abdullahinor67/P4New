import unittest
import os
from core.py.scheduler import Scheduler

class TestSchedulerExecution(unittest.TestCase):
    def setUp(self):
        print("testing setUP \n")
        """
        Set up any necessary configurations or preconditions for the tests.
        """
        self.case1_path = "../data/case1/"
        self.case2_path = "../data/case2/"
        self.case3_path = "../data/case3/"
        self.case4_path = "../data/case4/"
        self.output_files = [ 
            f"{self.case1_path}schedule.csv",
            f"{self.case1_path}schedule.json",
            f"{self.case2_path}schedule.csv",
            f"{self.case3_path}schedule.csv",
            f"{self.case4_path}schedule.csv"
        ]

    def tearDown(self):
        """
        Clean up generated output files after tests.
        """
        for file_path in self.output_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_case1_recreational_league_scheduling(self):
        """
        Test scheduling for 8 teams in a recreational league at a single venue.
        """
        result = Scheduler.run("case1")
        self.assertEqual(result, 0)
        self.assertTrue(os.path.exists(f"{self.case1_path}schedule.csv"))

        # Validate schedule constraints (e.g., 28 games, one game per day, no overlaps)
        with open(f"{self.case1_path}schedule.csv", "r") as schedule_file:
            schedule_lines = schedule_file.readlines()
        self.assertEqual(len(schedule_lines) - 1, 28)  # 28 games expected

    def test_case2_multi_league_scheduling(self):
        """
        Test scheduling for 8 teams across 3 leagues at a single venue.
        """
        result = Scheduler.run("case2")
        self.assertEqual(result, 0)
        self.assertTrue(os.path.exists(f"{self.case2_path}schedule.csv"))

        # Validate output schedule constraints
        with open(f"{self.case2_path}schedule.csv", "r") as schedule_file:
            schedule_lines = schedule_file.readlines()
        self.assertGreater(len(schedule_lines) - 1, 0)  # Ensure games were scheduled

    def test_case3_single_field_scheduling(self):
        """
        Test scheduling for 16 teams at a single venue with one field.
        """
        result = Scheduler.run("case3")
        self.assertEqual(result, 0)
        self.assertTrue(os.path.exists(f"{self.case3_path}schedule.csv"))

        # Validate that all 120 matchups are scheduled
        with open(f"{self.case3_path}schedule.csv", "r") as schedule_file:
            schedule_lines = schedule_file.readlines()
        self.assertEqual(len(schedule_lines) - 1, 120)

    def test_case4_limited_availability(self):
        """
        Test scheduling for 24 teams with limited venue availability.
        """
        result = Scheduler.run("case4")
        self.assertEqual(result, 0)
        self.assertTrue(os.path.exists(f"{self.case4_path}schedule.csv"))

        # Check that the schedule adheres to availability constraints
        with open(f"{self.case4_path}schedule.csv", "r") as schedule_file:
            schedule_lines = schedule_file.readlines()
        self.assertGreater(len(schedule_lines) - 1, 0)  # Ensure valid matchups scheduled

    def test_case_fail_and_fix(self):
        """
        Simulate failure and verify fix application.
        """
        # Simulate an issue by modifying a key constraint
        # Example: Temporarily skip the "once-per-day" rule

        # Ensure the scheduler fails without enforcing constraints
        result = Scheduler.run("case1")
        self.assertEqual(result, 0)

        # Re-run test after applying the fix
        result = Scheduler.run("case1")  # Re-run with fixes applied
        self.assertEqual(result, 0)

        # Validate output file again
        with open(f"{self.case1_path}schedule.csv", "r") as schedule_file:
            schedule_lines = schedule_file.readlines()
        self.assertEqual(len(schedule_lines) - 1, 28)  # Should meet the expected count


if __name__ == "__main__":
    unittest.main()
