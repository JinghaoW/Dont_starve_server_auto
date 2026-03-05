import zipfile
import subprocess
from tkinter import messagebox
from urllib.request import urlretrieve
from pathlib import Path
from environment import check_server
import shutil
import re
import os

STEAMCMD_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"


def install_steamcmd(path):
    """安装 SteamCMD"""
    try:
        install_dir = Path(path)
        install_dir.mkdir(parents=True, exist_ok=True)

        # Skip download and extraction if steamcmd is already installed
        if any((install_dir / f).exists() for f in ["steamcmd.exe", "steamcmd.sh"]):
            return True

        zip_path = install_dir / "steamcmd.zip"
        if not zip_path.exists():
            urlretrieve(STEAMCMD_URL, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_dir)

        return any((install_dir / f).exists() for f in ["steamcmd.exe", "steamcmd.sh"])
    except Exception as e:
        messagebox.showerror("安装失败", f"SteamCMD 安装错误: {str(e)}")
        return False


def install_server(steamcmd_path, server_path):
    """安装饥荒服务器"""
    try:
        steamcmd_exe = Path(steamcmd_path) / "steamcmd.exe"
        server_dir = Path(server_path)

        if not steamcmd_exe.exists():
            raise FileNotFoundError("未找到 SteamCMD 可执行文件")

        cmd = [
            str(steamcmd_exe),
            "+force_install_dir", str(server_dir),
            "+login", "anonymous",
            "+app_update", "343050", "validate",
            "+quit"
        ]

        subprocess.run(cmd, check=True)

        # 修改启动脚本
        success, msg = modify_launch_script(server_path)
        if not success:
            raise RuntimeError(msg)

        return True
    except Exception as e:
        messagebox.showerror("安装错误", str(e))
        return False


def modify_launch_script(server_path):
    """修改启动脚本"""
    try:
        bat_path = Path(server_path) / "bin" / "scripts" / "launch_preconfigured_servers.bat"

        if not bat_path.exists():
            raise FileNotFoundError(f"未找到启动脚本: {bat_path}")

        # 创建备份
        backup_path = bat_path.with_name("launch_preconfigured_servers.bak")
        if not backup_path.exists():
            shutil.copy2(bat_path, backup_path)

        # 读取原始内容
        with open(bat_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        # 保留头部配置
        header_lines = []
        for idx, line in enumerate(lines):
            if line.strip().startswith('REM LAUNCH'):
                header_lines = lines[:idx]
                break
        else:
            header_lines = lines[:6]  # 回退方案

        # 构建新内容
        new_content = [
            *header_lines,
            '\n',
            'start "Don\'t Starve Together Overworld" /D "%~dp0.." "%~dp0..\\dontstarve_dedicated_server_nullrenderer.exe" -cluster Cluster_1 -console -shard Master\n',
            'start "Don\'t Starve Together Caves"     /D "%~dp0.." "%~dp0..\\dontstarve_dedicated_server_nullrenderer.exe" -cluster Cluster_1 -console -shard Caves\n'
        ]

        # 写入文件
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content)

        # 验证修改
        verify_result, message = verify_bat_modification(bat_path)
        if not verify_result:
            restore_backup(bat_path, backup_path)
            raise RuntimeError(f"验证失败: {message}")

        return True, "修改成功"
    except Exception as e:
        if 'backup_path' in locals():
            restore_backup(bat_path, backup_path)
        return False, f"修改失败: {str(e)}"


def verify_bat_modification(bat_path):
    """验证 bat 文件修改是否成功"""
    required_patterns = [
        r'^start "Don\'t Starve Together Overworld"',
        r'^start "Don\'t Starve Together Caves"',
        r'-cluster Cluster_1',
        r'-shard Master',
        r'-shard Caves'
    ]

    try:
        with open(bat_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        missing = [p for p in required_patterns if not re.search(p, content, re.M)]
        if missing:
            return False, f"缺失关键模式: {', '.join(missing)}"

        return True, "验证通过"
    except Exception as e:
        return False, f"验证异常: {str(e)}"


def restore_backup(target_path, backup_path):
    """恢复备份文件"""
    try:
        shutil.copy2(backup_path, target_path)
        print(f"已从备份恢复: {backup_path} -> {target_path}")
    except Exception as e:
        print(f"恢复备份失败: {str(e)}")


def copy_mods(mods_source_path, server_path):
    """
    将模组从源目录拷贝到服务器的 mods 目录
    返回：(是否成功, 错误信息)
    """
    try:
        source_dir = Path(mods_source_path)
        target_dir = Path(server_path) / "mods"

        # 检查源目录
        if not source_dir.exists():
            return False, f"模组源目录不存在: {source_dir}"

        # 创建目标目录
        target_dir.mkdir(parents=True, exist_ok=True)

        # 拷贝模组文件
        for item in source_dir.glob("*"):
            if item.is_file():
                shutil.copy2(item, target_dir)
            elif item.is_dir():
                shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)

        return True, f"成功拷贝模组到: {target_dir}"
    except Exception as e:
        return False, f"模组拷贝失败: {str(e)}"