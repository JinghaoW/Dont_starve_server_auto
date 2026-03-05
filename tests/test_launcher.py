import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Patch tkinter.messagebox before importing launcher
sys.modules.setdefault("tkinter", MagicMock())
sys.modules.setdefault("tkinter.messagebox", MagicMock())

from launcher import launch_server


class TestLaunchServer(unittest.TestCase):
    def _make_bat(self, directory):
        scripts = Path(directory) / "bin" / "scripts"
        scripts.mkdir(parents=True)
        bat = scripts / "launch_preconfigured_servers.bat"
        bat.write_text("@echo off\n", encoding="utf-8")
        return bat

    def test_returns_false_when_bat_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok = launch_server(tmp)
            self.assertFalse(ok)

    def test_returns_true_when_bat_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_bat(tmp)
            with patch("os.startfile", create=True) as mock_startfile:
                ok = launch_server(tmp)
                self.assertTrue(ok)
                mock_startfile.assert_called_once()

    def test_returns_false_when_startfile_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_bat(tmp)
            with patch("os.startfile", create=True, side_effect=OSError("startfile not supported")):
                ok = launch_server(tmp)
                self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
