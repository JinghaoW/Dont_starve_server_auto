import unittest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from environment import check_steamcmd, check_cluster, check_mods_directory, check_server


class TestCheckSteamcmd(unittest.TestCase):
    def test_returns_true_when_steamcmd_exe_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "steamcmd.exe").touch()
            self.assertTrue(check_steamcmd(tmp))

    def test_returns_true_when_steamcmd_sh_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "steamcmd.sh").touch()
            self.assertTrue(check_steamcmd(tmp))

    def test_returns_false_when_no_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(check_steamcmd(tmp))

    def test_returns_false_for_nonexistent_directory(self):
        self.assertFalse(check_steamcmd("/nonexistent/path/steamcmd"))


class TestCheckServer(unittest.TestCase):
    def _make_server_dir(self, tmp, include_exe=True, include_bat=True):
        """Create a fake server directory structure."""
        bin_scripts = Path(tmp) / "bin" / "scripts"
        bin_scripts.mkdir(parents=True)
        if include_exe:
            (Path(tmp) / "bin" / "dontstarve_dedicated_server_nullrenderer.exe").touch()
        if include_bat:
            (bin_scripts / "launch_preconfigured_servers.bat").touch()

    def test_returns_true_when_all_files_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_server_dir(tmp)
            ok, missing = check_server(tmp)
            self.assertTrue(ok)
            self.assertEqual(missing, [])

    def test_returns_false_when_exe_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_server_dir(tmp, include_exe=False)
            ok, missing = check_server(tmp)
            self.assertFalse(ok)
            self.assertIn("bin/dontstarve_dedicated_server_nullrenderer.exe", missing)

    def test_returns_false_when_bat_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_server_dir(tmp, include_bat=False)
            ok, missing = check_server(tmp)
            self.assertFalse(ok)
            self.assertIn("bin/scripts/launch_preconfigured_servers.bat", missing)

    def test_returns_false_when_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok, missing = check_server(tmp)
            self.assertFalse(ok)
            self.assertEqual(len(missing), 2)


class TestCheckCluster(unittest.TestCase):
    def test_returns_true_when_cluster_1_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "Cluster_1").mkdir()
            self.assertTrue(check_cluster(tmp))

    def test_returns_false_when_cluster_1_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(check_cluster(tmp))


class TestCheckModsDirectory(unittest.TestCase):
    def test_returns_true_when_mods_dir_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "mods").mkdir()
            self.assertTrue(check_mods_directory(tmp))

    def test_returns_false_when_mods_dir_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(check_mods_directory(tmp))


if __name__ == "__main__":
    unittest.main()
