"""Tests for check_ohtani.py"""
import unittest
from unittest.mock import patch, Mock, mock_open
import sys
import os
import json
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


OHTANI_GAME = {
    'dates': [{
        'date': '2026-05-05',
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

OTHER_PITCHER_GAME = {
    'dates': [{
        'date': '2026-05-05',
        'games': [{
            'teams': {
                'away': {
                    'team': {'id': 119, 'name': 'Los Angeles Dodgers'},
                    'probablePitcher': {'id': 999999, 'fullName': 'Walker Buehler'}
                },
                'home': {
                    'team': {'id': 138, 'name': 'St. Louis Cardinals'}
                }
            }
        }]
    }]
}

NO_PITCHER_GAME = {
    'dates': [{
        'date': '2026-05-05',
        'games': [{
            'teams': {
                'away': {
                    'team': {'id': 119, 'name': 'Los Angeles Dodgers'}
                },
                'home': {
                    'team': {'id': 138, 'name': 'St. Louis Cardinals'}
                }
            }
        }]
    }]
}


def make_api_mock(data):
    mock_response = Mock()
    mock_response.json.return_value = data
    mock_response.status_code = 200
    return mock_response


class TestNotification(unittest.TestCase):

    @patch('check_ohtani.save_state')
    @patch('check_ohtani.load_state', return_value={"last_notified_date": None, "failure_count": 0})
    @patch('check_ohtani.get_pt_date', return_value='2026-05-05')
    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_sends_notification_when_ohtani_pitching(self, mock_get, mock_post, mock_date, mock_load, mock_save):
        mock_get.return_value = make_api_mock(OHTANI_GAME)
        import check_ohtani
        check_ohtani.main()
        mock_post.assert_called_once()
        self.assertIn('Shohei Ohtani', mock_post.call_args[1].get('data', ''))

    @patch('check_ohtani.save_state')
    @patch('check_ohtani.load_state', return_value={"last_notified_date": None, "failure_count": 0})
    @patch('check_ohtani.get_pt_date', return_value='2026-05-05')
    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_no_notification_when_other_pitcher(self, mock_get, mock_post, mock_date, mock_load, mock_save):
        mock_get.return_value = make_api_mock(OTHER_PITCHER_GAME)
        import check_ohtani
        check_ohtani.main()
        mock_post.assert_not_called()

    @patch('check_ohtani.save_state')
    @patch('check_ohtani.load_state', return_value={"last_notified_date": None, "failure_count": 0})
    @patch('check_ohtani.get_pt_date', return_value='2026-05-05')
    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_no_notification_when_no_game(self, mock_get, mock_post, mock_date, mock_load, mock_save):
        mock_get.return_value = make_api_mock({'dates': []})
        import check_ohtani
        check_ohtani.main()
        mock_post.assert_not_called()

    @patch('check_ohtani.save_state')
    @patch('check_ohtani.load_state', return_value={"last_notified_date": None, "failure_count": 0})
    @patch('check_ohtani.get_pt_date', return_value='2026-05-05')
    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_no_notification_when_pitcher_not_announced(self, mock_get, mock_post, mock_date, mock_load, mock_save):
        mock_get.return_value = make_api_mock(NO_PITCHER_GAME)
        import check_ohtani
        check_ohtani.main()
        mock_post.assert_not_called()


class TestIdempotency(unittest.TestCase):

    @patch('check_ohtani.requests.get')
    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.load_state', return_value={"last_notified_date": "2026-05-05", "failure_count": 0})
    @patch('check_ohtani.get_pt_date', return_value='2026-05-05')
    def test_skips_if_already_notified_today(self, mock_date, mock_load, mock_post, mock_get):
        import check_ohtani
        check_ohtani.main()
        mock_get.assert_not_called()
        mock_post.assert_not_called()


class TestRetryLogic(unittest.TestCase):

    @patch('check_ohtani.save_state')
    @patch('check_ohtani.load_state', return_value={"last_notified_date": None, "failure_count": 0})
    @patch('check_ohtani.get_pt_date', return_value='2026-05-05')
    @patch('check_ohtani.time.sleep')
    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_retries_and_succeeds(self, mock_get, mock_post, mock_sleep, mock_date, mock_load, mock_save):
        mock_get.side_effect = [
            requests.ConnectionError("fail"),
            requests.ConnectionError("fail"),
            make_api_mock(OHTANI_GAME),
        ]
        import check_ohtani
        check_ohtani.main()
        self.assertEqual(mock_get.call_count, 3)
        mock_post.assert_called_once()

    @patch('check_ohtani.save_state')
    @patch('check_ohtani.load_state', return_value={"last_notified_date": None, "failure_count": 0})
    @patch('check_ohtani.get_pt_date', return_value='2026-05-05')
    @patch('check_ohtani.time.sleep')
    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_gives_up_after_max_retries(self, mock_get, mock_post, mock_sleep, mock_date, mock_load, mock_save):
        mock_get.side_effect = requests.ConnectionError("fail")
        import check_ohtani
        check_ohtani.main()
        self.assertEqual(mock_get.call_count, 3)
        mock_post.assert_not_called()


class TestFailureTracking(unittest.TestCase):

    @patch('check_ohtani.get_pt_date', return_value='2026-05-05')
    @patch('check_ohtani.time.sleep')
    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_failure_count_increments(self, mock_get, mock_post, mock_sleep, mock_date):
        mock_get.side_effect = requests.ConnectionError("fail")
        saved = {}

        def capture_save(state):
            saved.update(state)

        import check_ohtani
        with patch('check_ohtani.load_state', return_value={"last_notified_date": None, "failure_count": 0}):
            with patch('check_ohtani.save_state', side_effect=capture_save):
                check_ohtani.main()

        self.assertEqual(saved.get('failure_count'), 1)
        mock_post.assert_not_called()

    @patch('check_ohtani.get_pt_date', return_value='2026-05-05')
    @patch('check_ohtani.time.sleep')
    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_sends_alert_on_third_consecutive_failure(self, mock_get, mock_post, mock_sleep, mock_date):
        mock_get.side_effect = requests.ConnectionError("fail")
        saved = {}

        def capture_save(state):
            saved.update(state)

        import check_ohtani
        with patch('check_ohtani.load_state', return_value={"last_notified_date": None, "failure_count": 2}):
            with patch('check_ohtani.save_state', side_effect=capture_save):
                check_ohtani.main()

        mock_post.assert_called_once()
        self.assertIn('3 consecutive days', mock_post.call_args[1].get('data', ''))
        self.assertEqual(saved.get('failure_count'), 0)

    @patch('check_ohtani.save_state')
    @patch('check_ohtani.get_pt_date', return_value='2026-05-05')
    @patch('check_ohtani.requests.post')
    @patch('check_ohtani.requests.get')
    def test_failure_count_resets_on_success(self, mock_get, mock_post, mock_date, mock_save):
        mock_get.return_value = make_api_mock({'dates': []})
        saved = {}
        mock_save.side_effect = lambda s: saved.update(s)

        import check_ohtani
        with patch('check_ohtani.load_state', return_value={"last_notified_date": None, "failure_count": 2}):
            check_ohtani.main()

        self.assertEqual(saved.get('failure_count'), 0)
        mock_post.assert_not_called()


if __name__ == '__main__':
    unittest.main()
