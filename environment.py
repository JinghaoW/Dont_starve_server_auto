from pathlib import Path


def check_steamcmd(path):
    """检查 SteamCMD 是否安装"""
    steamcmd_path = Path(path)
    return any(steamcmd_path.joinpath(f).exists() for f in ["steamcmd.exe", "steamcmd.sh"])


def check_server(path):
    """检查服务器文件是否完整"""
    server_dir = Path(path)
    required_files = [
        "bin/dontstarve_dedicated_server_nullrenderer.exe",
        "bin/scripts/launch_preconfigured_servers.bat",
    ]

    missing = [f for f in required_files if not server_dir.joinpath(f).exists()]
    return len(missing) == 0, missing


def check_cluster(path):
    """检查存档配置是否存在"""
    return Path(path).joinpath("Cluster_1").exists()


def check_mods_directory(server_path):
    """检查服务器 mods 目录是否存在"""
    mods_dir = Path(server_path) / "mods"
    return mods_dir.exists()