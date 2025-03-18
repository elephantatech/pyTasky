import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from pytasky import PyTaskyApp


class TestPyTaskyApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = PyTaskyApp(self.root)

    def tearDown(self):
        self.root.destroy()

    @patch("pytasky.get_session")
    def test_add_task(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        self.app.title_entry.insert(0, "Test Task")
        self.app.notes_entry.insert(0, "Test Notes")
        self.app.tag_entry.insert(0, "Test Tag")
        self.app.status_combo.set("todo")

        self.app.add_task()

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        self.assertEqual(self.app.title_entry.get(), "")
        self.assertEqual(self.app.notes_entry.get(), "")
        self.assertEqual(self.app.tag_entry.get(), "")
        self.assertEqual(self.app.status_combo.get(), "todo")

    @patch("pytasky.get_session")
    def test_update_task_list(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.title = "Test Task"
        mock_task.status = "todo"
        mock_task.created_at = None
        mock_task.last_updated = None
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_task
        ]

        self.app.update_task_list()

        self.assertEqual(self.app.task_list.size(), 1)
        self.assertIn(
            "1. Test Task [todo - Created: N/A - Updated: N/A]",
            self.app.task_list.get(0),
        )

    @patch("pytasky.get_session")
    def test_update_done_list(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.title = "Test Task"
        mock_task.status = "done"
        mock_task.created_at = None
        mock_task.completed_at = None
        mock_task.last_updated = None
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_task
        ]

        self.app.update_done_list()

        self.assertEqual(self.app.done_list.size(), 1)
        self.assertIn(
            "1. Test Task [done - Created: N/A - Completed: N/A - Updated: N/A]",
            self.app.done_list.get(0),
        )

    def test_set_custom_pomodoro(self):
        self.app.custom_entry.delete(0, tk.END)
        self.app.custom_entry.insert(0, "30")
        self.app.set_custom_pomodoro()
        self.assertEqual(self.app.custom_pomodoro, 30)
        self.assertEqual(self.app.time_left, 1800)
        self.assertEqual(self.app.time_label.cget("text"), "30:00")

    def test_start_timer(self):
        self.app.start_timer()
        self.assertTrue(self.app.running)

    def test_stop_timer(self):
        self.app.running = True
        self.app.stop_timer()
        self.assertFalse(self.app.running)

    def test_set_break(self):
        self.app.set_break(5)
        self.assertEqual(self.app.time_left, 300)
        self.assertEqual(self.app.time_label.cget("text"), "05:00")


if __name__ == "__main__":
    unittest.main()
