import _thread
import tkinter as tk
from tkinter import messagebox

import client.data
import client.socket_listener
from client.windows.login import LoginForm
from client.settings.secure.secure_channel import client_to_server


def run():
    root = tk.Tk()
    client.data.tk_root = root

    try:
        # 建立安全连接
        client.data.sc = client_to_server()

    except ConnectionError:
        messagebox.showerror("出错了", "无法连接到服务器")
        exit(1)

    # 连接服务器开启新进程
    # 新进程开启安全连接
    _thread.start_new_thread(client.socket_listener.socket_listener_thread, (client.data.sc, root))
    # 打开登录界面
    login = tk.Toplevel()
    LoginForm(master=login)

    root.withdraw()
    root.mainloop()
    try:
        root.destroy()
    except tk.TclError:
        pass
