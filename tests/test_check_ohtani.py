"""Tests for check_ohtani.py - TDD Red Phase"""
import unittest
from unittest.mock import patch, Mock
import sys
import os
import json
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestOhtaniCheck(unittest.TestCase):
    """Test cases for Ohtani pitching check script"""

    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_sends_notification_when_ohtani_is_probable_pitcher(self, mock_get, mock_post):
        """Test that ntfy notification is sent when Ohtani is probable pitcher"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'dates': [{
                'date': '2026-05-03',
                'games': [{
                    'teams': {
                        'away': {
                            'team': {'id': 119, 'name': 'Los Angeles Dodgers'},
                            'probablePitcher': {'id': 660271, 'fullName': 'Shohei Ohtani'}
                        },
                        'home': {
                            'team': {'id': 138, 'name': 'St. Louis Cardinals'}
                        }
                    }
                }]
            }]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        import check_ohtani
        check_ohtani.main()
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('Shohei Ohtani', call_args[1].get('data', ''))


class TestNoGameToday(unittest.TestCase):
    """Test behavior when no Dodgers game today"""

    @patch('check_ohtani.requests.get')
    def test_exits_silently_when_no_game_today(self, mock_get):
        """Test that script exits silently when no game today (empty dates)"""
        mock_response = Mock()
        mock_response.json.return_value = {'dates': []}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        import check_ohtani
        check_ohtani.main()


class TestNotOhtaniPitching(unittest.TestCase):
    """Test behavior when Ohtani is not pitching"""

    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_no_notification_when_other_pitcher(self, mock_get, mock_post):
        """Test that no notification is sent when another pitcher is starting"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'dates': [{
                'date': '2026-05-03',
                'games': [{
                    'teams': {
                        'away': {
                            'team': {'id': 119, 'name': 'Los Angeles Dodgers'},
                            'probablePitcher': {'id': 999999, 'fullName': 'Other Pitcher'}
                        },
                        'home': {
                            'team': {'id': 138, 'name': 'St. Louis Cardinals'}
                        }
                    }
                }]
            }]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        import check_ohtani
        check_ohtani.main()
        
        mock_post.assert_not_called()


class TestRetryLogic(unittest.TestCase):
    """Test retry logic for API failures"""

    @patch('check_ohtani.time.sleep')
    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_retries_on_connection_error(self, mock_get, mock_post, mock_sleep):
        """Test that script retries API call on connection failure"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'dates': [{
                'date': '2026-05-03',
                'games': [{
                    'teams': {
                        'away': {
                            'team': {'id': 119, 'name': 'Los Angeles Dodgers'},
                            'probablePitcher': {'id': 660271, 'fullName': 'Shohei Ohtani'}
                        },
                        'home': {
                            'team': {'id': 138, 'name': 'St. Louis Cardinals'}
                        }
                    }
                }]
            }]
        }
        mock_response.status_code = 200
        mock_get.side_effect = [
            requests.ConnectionError("Connection failed"),
            requests.ConnectionError("Connection failed"),
            mock_response
        ]
        
        import check_ohtani
        check_ohtani.main()
        
        self.assertEqual(mock_get.call_count, 3)
        mock_post.assert_called_once()

    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    @patch('check_ohtani.time.sleep')
    def test_gives_up_after_max_retries(self, mock_sleep, mock_get, mock_post):
        """Test that script gives up after max retries"""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        import check_ohtani
        check_ohtani.main()
        
        self.assertEqual(mock_get.call_count, 3)
        mock_post.assert_not_called()


class TestExceptionHandling(unittest.TestCase):
    """Test exception handling with specific exceptions"""

    @patch('check_ohtani.requests.get')
    def test_logs_specific_exception_on_failure(self, mock_get):
        """Test that script logs specific exceptions"""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        import check_ohtani
        try:
            check_ohtani.main()
        except Exception as e:
            self.fail(f"Script raised unhandled exception: {e}")


class TestFailureTracking(unittest.TestCase):
    """Test failure tracking and alerts"""

    def setUp(self):
        """Clean up any existing failure count file"""
        self.failure_file = 'failure_count.json'
        if os.path.exists(self.failure_file):
            os.remove(self.failure_file)

    def tearDown(self):
        """Clean up after test"""
        if os.path.exists(self.failure_file):
            os.remove(self.failure_file)

    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_failure_counter_increments(self, mock_get, mock_post):
        """Test that failure counter increments on API failure"""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        import check_ohtani
        check_ohtani.main()
        
        self.assertTrue(os.path.exists(self.failure_file))
        with open(self.failure_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data.get('count'), 1)
        mock_post.assert_not_called()

    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_sends_notification_after_three_failures(self, mock_get, mock_post):
        """Test that notification is sent after 3 consecutive failures"""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        import check_ohtani
        for i in range(3):
            check_ohtani.main()
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('3 consecutive days', call_args[1].get('data', ''))
        
        with open(self.failure_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data.get('count'), 0)

    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_counter_resets_on_success(self, mock_get, mock_post):
        """Test that failure counter resets when API check succeeds"""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        import check_ohtani
        check_ohtani.main()
        
        with open(self.failure_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data.get('count'), 1)
        
        mock_get.side_effect = None
        mock_response = Mock()
        mock_response.json.return_value = {'dates': []}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        check_ohtani.main()
        
        with open(self.failure_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data.get('count'), 0)
        mock_post.assert_not_called()


if __name__ == '__main__':
    unittest.main()
