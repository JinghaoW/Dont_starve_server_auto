import json
from pathlib import Path

CONFIG_FILE = "dst_tool_config.json"

DEFAULT_PATHS = {
    "steamcmd_path": str(Path.home() / "SteamCMD"),
    "server_path": str(Path.home() / "DST_Server"),
    "cluster_path": str(Path.home() / "Documents" / "Klei" / "DoNotStarveTogether"),
    "mods_path": ""  # 默认模组路径为空
}

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        # Merge with defaults so missing keys fall back to their default values
        config = dict(DEFAULT_PATHS)
        config.update(loaded)
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_PATHS)

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)