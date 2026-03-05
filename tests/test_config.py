import json
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DEFAULT_PATHS, load_config, save_config


class TestLoadConfig(unittest.TestCase):
    def test_returns_defaults_when_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = load_config()
        self.assertEqual(result, DEFAULT_PATHS)

    def test_returns_defaults_when_json_is_invalid(self):
        m = mock_open(read_data="not valid json")
        with patch("builtins.open", m):
            result = load_config()
        self.assertEqual(result, DEFAULT_PATHS)

    def test_returns_loaded_values(self):
        data = {
            "steamcmd_path": "C:/SteamCMD",
            "server_path": "C:/DST",
            "cluster_path": "C:/Klei",
            "mods_path": "C:/Mods",
        }
        m = mock_open(read_data=json.dumps(data))
        with patch("builtins.open", m):
            result = load_config()
        self.assertEqual(result["steamcmd_path"], "C:/SteamCMD")
        self.assertEqual(result["server_path"], "C:/DST")

    def test_missing_keys_filled_with_defaults(self):
        """A partial config file should have missing keys filled from DEFAULT_PATHS."""
        partial = {"steamcmd_path": "C:/SteamCMD"}
        m = mock_open(read_data=json.dumps(partial))
        with patch("builtins.open", m):
            result = load_config()
        self.assertEqual(result["steamcmd_path"], "C:/SteamCMD")
        self.assertEqual(result["server_path"], DEFAULT_PATHS["server_path"])
        self.assertEqual(result["cluster_path"], DEFAULT_PATHS["cluster_path"])
        self.assertEqual(result["mods_path"], DEFAULT_PATHS["mods_path"])


class TestSaveConfig(unittest.TestCase):
    def test_writes_json_with_indent(self):
        config = {"steamcmd_path": "C:/SteamCMD"}
        m = mock_open()
        with patch("builtins.open", m):
            save_config(config)
        handle = m()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        parsed = json.loads(written)
        self.assertEqual(parsed["steamcmd_path"], "C:/SteamCMD")

    def test_uses_utf8_encoding(self):
        config = {}
        m = mock_open()
        with patch("builtins.open", m) as mock_file:
            save_config(config)
        mock_file.assert_called_once_with("dst_tool_config.json", "w", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
