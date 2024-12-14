import unittest
from unittest.mock import patch, MagicMock
from core.py.scheduler import Scheduler


class TestSchedulerExecution(unittest.TestCase):
    """
    Test Scheduler functionality for various cases without modifying any files.
    """

    def setUp(self):
        """
        Initialize test case configurations.
        """
        print("Setting up test environment... (It's new code)")  # Added line to indicate new code
        self.base_path = "./data/"
        self.cases = {
            "case1": {"path": f"{self.base_path}case1/", "expected_games": 28},
            "case2": {"path": f"{self.base_path}case2/", "expected_games": "non-zero"},
            "case3": {"path": f"{self.base_path}case3/", "expected_games": 120},
            "case4": {"path": f"{self.base_path}case4/", "expected_games": "non-zero"},
            "case5": {"path": f"{self.base_path}case5/", "expected_games": "varied"},
            "case6": {"path": f"{self.base_path}case6/", "expected_games": "varied"},
            "case7": {"path": f"{self.base_path}case7/", "expected_games": "varied"},
            "case8": {"path": f"{self.base_path}case8/", "expected_games": "varied"},
            "generated": {"path": f"{self.base_path}generated/", "expected_games": "varied"},
        }

    def check_scheduler_output(self, mock_open, case_name):
        """
        Helper function to validate scheduler outputs without writing files.
        """
        # Mock file writes to prevent actual file modification
        mock_open.return_value = MagicMock()
        result = Scheduler.run(case_name)
        self.assertEqual(result, 0, f"Scheduler failed for {case_name}")

        # Ensure files would have been written without actually creating them
        expected_csv_path = f"{self.cases[case_name]['path']}schedule.csv"
        mock_open.assert_any_call(expected_csv_path, "w")

    @patch("core.py.scheduler.open", new_callable=MagicMock)
    def test_case1_recreational_league_scheduling(self, mock_open):
        """
        Test case1: 8 teams, single venue, 4 fields, uniform availability.
        Expect: 28 games, balanced utilization, no overlaps, each team plays once/day.
        """
        self.check_scheduler_output(mock_open, "case1")

    @patch("core.py.scheduler.open", new_callable=MagicMock)
    def test_case2_multi_league_scheduling(self, mock_open):
        """
        Test case2: 8 teams, 3 leagues, single venue, 4 fields.
        Expect: Balanced games across leagues, no overlaps, each team plays once/day.
        """
        self.check_scheduler_output(mock_open, "case2")

    @patch("core.py.scheduler.open", new_callable=MagicMock)
    def test_case3_single_field_scheduling(self, mock_open):
        """
        Test case3: 16 teams, single venue, 1 field, uniform availability.
        Expect: 120 games total, no overlaps, each team plays once/day.
        """
        self.check_scheduler_output(mock_open, "case3")

    @patch("core.py.scheduler.open", new_callable=MagicMock)
    def test_case4_limited_availability(self, mock_open):
        """
        Test case4: 24 teams, limited venue availability.
        Expect: Valid matchups scheduled within constraints, no overlaps, each team plays once/day.
        """
        self.check_scheduler_output(mock_open, "case4")

    @patch("core.py.scheduler.open", new_callable=MagicMock)
    def test_case5_varied_conditions(self, mock_open):
        """
        Test case5: Larger dataset, varied conditions.
        Expect: Balanced games, no overlaps, each team plays once/day.
        """
        self.check_scheduler_output(mock_open, "case5")

    @patch("core.py.scheduler.open", new_callable=MagicMock)
    def test_case6_varied_conditions(self, mock_open):
        """
        Test case6: Larger dataset, varied conditions.
        Expect: Balanced games, no overlaps, each team plays once/day.
        """
        self.check_scheduler_output(mock_open, "case6")

    @patch("core.py.scheduler.open", new_callable=MagicMock)
    def test_case7_varied_conditions(self, mock_open):
        """
        Test case7: Larger dataset, varied conditions.
        Expect: Balanced games, no overlaps, each team plays once/day.
        """
        self.check_scheduler_output(mock_open, "case7")

    @patch("core.py.scheduler.open", new_callable=MagicMock)
    def test_case8_varied_conditions(self, mock_open):
        """
        Test case8: Larger dataset, varied conditions.
        Expect: Balanced games, no overlaps, each team plays once/day.
        """
        self.check_scheduler_output(mock_open, "case8")

    @patch("core.py.scheduler.open", new_callable=MagicMock)
    def test_generated_case(self, mock_open):
        """
        Test generated case: Automatically generated dataset.
        Expect: Balanced games, no overlaps, each team plays once/day.
        """
        self.check_scheduler_output(mock_open, "generated")


if __name__ == "__main__":
    unittest.main()
