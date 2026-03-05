import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config import load_config, save_config
from environment import check_steamcmd, check_server, check_cluster, check_mods_directory
from installer import install_steamcmd, install_server, copy_mods
from launcher import launch_server

class PathSelector(ttk.Frame):
    def __init__(self, parent, title, path_var):
        super().__init__(parent)
        self.path_var = path_var

        ttk.Label(self, text=title).grid(row=0, column=0, sticky='w')
        ttk.Entry(self, textvariable=path_var, width=40).grid(row=0, column=1)
        ttk.Button(self, text="浏览", command=self.browse).grid(row=0, column=2)

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

class DSTInstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("饥荒服务器管理器")
        self.config = load_config()

        self.mods_path = tk.StringVar(value=self.config.get("mods_path", ""))

        self.steamcmd_path = tk.StringVar(value=self.config["steamcmd_path"])
        self.server_path = tk.StringVar(value=self.config["server_path"])
        self.cluster_path = tk.StringVar(value=self.config["cluster_path"])

        self.create_widgets()
        self.update_status()

    def create_widgets(self):
        PathSelector(self, "SteamCMD路径:", self.steamcmd_path).pack(pady=5, fill='x')
        PathSelector(self, "服务器路径:", self.server_path).pack(pady=5, fill='x')
        PathSelector(self, "存档路径:", self.cluster_path).pack(pady=5, fill='x')

        # 新增模组路径选择
        PathSelector(self, "模组路径:", self.mods_path).pack(pady=5, fill='x')

        # 状态显示
        self.status_frame = ttk.LabelFrame(self, text="系统状态")
        self.steamcmd_status = ttk.Label(self.status_frame, text="正在检测SteamCMD...")
        self.server_status = ttk.Label(self.status_frame, text="正在检测服务器...")
        self.cluster_status = ttk.Label(self.status_frame, text="正在检测存档...")
        self.mods_status = ttk.Label(self.status_frame, text="正在检测模组...")

        self.steamcmd_status.pack(anchor='w')
        self.server_status.pack(anchor='w')
        self.cluster_status.pack(anchor='w')
        self.mods_status.pack(anchor='w')
        self.status_frame.pack(pady=10, fill='x')

        # 操作按钮
        btn_frame = ttk.Frame(self)
        ttk.Button(btn_frame, text="安装SteamCMD", command=self.handle_steamcmd).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="安装服务器", command=self.handle_server).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="启动服务器", command=self.handle_launch).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="拷贝模组", command=self.handle_copy_mods).pack(side='left', padx=5)
        btn_frame.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_status(self):
        # 原有状态检测
        steam_ok = check_steamcmd(self.steamcmd_path.get())
        server_ok, _ = check_server(self.server_path.get())
        cluster_ok = check_cluster(self.cluster_path.get())
        mods_ok = check_mods_directory(self.server_path.get())

        self.steamcmd_status.config(
            text=f"SteamCMD: {'✓' if steam_ok else '✗'}",
            foreground="green" if steam_ok else "red"
        )
        self.server_status.config(
            text=f"服务器文件: {'✓' if server_ok else '✗'}",
            foreground="green" if server_ok else "red"
        )
        self.cluster_status.config(
            text=f"存档配置: {'✓' if cluster_ok else '✗'}",
            foreground="green" if cluster_ok else "red"
        )

        # 模组状态检测

        self.mods_status.config(
            text=f"模组目录: {'✓' if mods_ok else '✗'}",
            foreground="green" if mods_ok else "red"
        )

    def handle_copy_mods(self):
        """处理模组拷贝"""
        mods_source = self.mods_path.get()
        server_path = self.server_path.get()

        if not mods_source:
            messagebox.showerror("错误", "请先选择模组源目录")
            return

        success, msg = copy_mods(mods_source, server_path)
        if success:
            messagebox.showinfo("成功", msg)
        else:
            messagebox.showerror("失败", msg)

        self.update_status()


    def handle_steamcmd(self):
        if install_steamcmd(self.steamcmd_path.get()):
            self.update_status()

    def handle_server(self):
        if install_server(self.steamcmd_path.get(), self.server_path.get()):
            self.update_status()

    def handle_launch(self):
        if launch_server(self.server_path.get()):
            messagebox.showinfo("成功", "服务器启动命令已执行，请查看控制台窗口")

    def on_close(self):
        save_config({
            "steamcmd_path": self.steamcmd_path.get(),
            "server_path": self.server_path.get(),
            "cluster_path": self.cluster_path.get(),
            "mods_path": self.mods_path.get()
        })
        self.destroy()

