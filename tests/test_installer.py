import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Patch tkinter.messagebox before importing installer (GUI dependency)
import unittest.mock as mock
mock_messagebox = MagicMock()
sys.modules.setdefault("tkinter", MagicMock())
sys.modules.setdefault("tkinter.messagebox", mock_messagebox)

from installer import (
    copy_mods,
    modify_launch_script,
    restore_backup,
    verify_bat_modification,
)

VALID_BAT_CONTENT = (
    "@echo off\n"
    "REM Some header\n"
    "\n"
    "start \"Don't Starve Together Overworld\" "
    '/D "%~dp0.." "%~dp0..\\dontstarve_dedicated_server_nullrenderer.exe"'
    " -cluster Cluster_1 -console -shard Master\n"
    "start \"Don't Starve Together Caves\"     "
    '/D "%~dp0.." "%~dp0..\\dontstarve_dedicated_server_nullrenderer.exe"'
    " -cluster Cluster_1 -console -shard Caves\n"
)


def _make_bat_file(directory, content=""):
    """Create a fake launch_preconfigured_servers.bat at the expected path."""
    scripts_dir = Path(directory) / "bin" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    bat = scripts_dir / "launch_preconfigured_servers.bat"
    bat.write_text(content, encoding="utf-8")
    return bat


class TestVerifyBatModification(unittest.TestCase):
    def test_valid_content_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bat = _make_bat_file(tmp, VALID_BAT_CONTENT)
            ok, msg = verify_bat_modification(bat)
            self.assertTrue(ok)
            self.assertIn("通过", msg)

    def test_missing_shard_master_fails(self):
        content = VALID_BAT_CONTENT.replace("-shard Master", "")
        with tempfile.TemporaryDirectory() as tmp:
            bat = _make_bat_file(tmp, content)
            ok, msg = verify_bat_modification(bat)
            self.assertFalse(ok)

    def test_missing_shard_caves_fails(self):
        content = VALID_BAT_CONTENT.replace("-shard Caves", "")
        with tempfile.TemporaryDirectory() as tmp:
            bat = _make_bat_file(tmp, content)
            ok, msg = verify_bat_modification(bat)
            self.assertFalse(ok)

    def test_nonexistent_file_returns_error(self):
        ok, msg = verify_bat_modification(Path("/nonexistent/file.bat"))
        self.assertFalse(ok)


class TestRestoreBackup(unittest.TestCase):
    def test_backup_restored_successfully(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.bat"
            backup = Path(tmp) / "backup.bat"
            backup.write_text("backup content", encoding="utf-8")
            target.write_text("original content", encoding="utf-8")
            restore_backup(target, backup)
            self.assertEqual(target.read_text(encoding="utf-8"), "backup content")

    def test_missing_backup_does_not_raise(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.bat"
            backup = Path(tmp) / "nonexistent.bak"
            target.write_text("original", encoding="utf-8")
            # Should not raise; prints an error message instead
            restore_backup(target, backup)


class TestModifyLaunchScript(unittest.TestCase):
    def _make_original_bat(self, directory):
        content = (
            "@echo off\n"
            "REM Header line 1\n"
            "REM Header line 2\n"
            "REM LAUNCH\n"
            "start something old\n"
        )
        return _make_bat_file(directory, content)

    def test_modifies_bat_and_returns_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_original_bat(tmp)
            ok, msg = modify_launch_script(tmp)
            self.assertTrue(ok, msg)

    def test_creates_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            bat = self._make_original_bat(tmp)
            modify_launch_script(tmp)
            backup = bat.with_name("launch_preconfigured_servers.bak")
            self.assertTrue(backup.exists())

    def test_returns_false_when_bat_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok, msg = modify_launch_script(tmp)
            self.assertFalse(ok)


class TestCopyMods(unittest.TestCase):
    def test_copies_files_to_target(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as server:
            (Path(src) / "mod_file.lua").write_text("mod content", encoding="utf-8")
            ok, msg = copy_mods(src, server)
            self.assertTrue(ok, msg)
            self.assertTrue((Path(server) / "mods" / "mod_file.lua").exists())

    def test_copies_subdirectory(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as server:
            sub = Path(src) / "workshop-12345"
            sub.mkdir()
            (sub / "modinfo.lua").write_text("info", encoding="utf-8")
            ok, msg = copy_mods(src, server)
            self.assertTrue(ok, msg)
            self.assertTrue((Path(server) / "mods" / "workshop-12345" / "modinfo.lua").exists())

    def test_returns_false_when_source_missing(self):
        with tempfile.TemporaryDirectory() as server:
            ok, msg = copy_mods("/nonexistent/mods", server)
            self.assertFalse(ok)
            self.assertIn("不存在", msg)

    def test_creates_target_mods_directory(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as server:
            ok, msg = copy_mods(src, server)
            self.assertTrue(ok, msg)
            self.assertTrue((Path(server) / "mods").exists())


if __name__ == "__main__":
    unittest.main()
