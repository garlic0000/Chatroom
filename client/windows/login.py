from client.settings.message_format import MessageCode
import client.data
from client.windows.register import RegisterForm
from client.windows.contacts import ContactsForm
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import *
import tkinter as tk
import client.socket_listener
import json


# 继承Frame
class LoginForm(tk.Frame):
    def __init__(self, master=None):
        # 登录界面的配置
        super().__init__(master)
        self.master = master
        screen_width = client.data.tk_root.winfo_screenwidth()
        screen_height = client.data.tk_root.winfo_screenheight()
        w = 370
        h = 460
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        # D:/PycharmProjects/Chatroom/client/data/si.ico
        # 图标
        self.master.iconbitmap("../client/data/si.ico")

        self.master.title('登录')
        background_color = "white"

        self.master.configure(background=background_color)
        self.font = tkFont.Font(family='Fixdsys', size=10)

        ft = tkFont.Font(family='Fixdsys', size=20, weight=tkFont.BOLD)
        self.label_login = Label(self.master, text="登录", font=ft, bg=background_color)
        self.label_login.place(x=150, y=44)

        entryBackGroundColor = "#F3F3F4"
        self.label_username = Label(self.master, text='请输入用户名:', font=self.font, bg=background_color)
        self.label_username.place(x=20, y=120)

        self.label_password = Label(self.master, text='请输入密码:', font=self.font, bg=background_color)
        self.label_password.place(x=20, y=190)

        self.username = Entry(self.master, highlightthickness=1, bg=entryBackGroundColor)
        self.username.place(x=20, y=150, width=320, height=30)

        self.password = Entry(self.master, highlightthickness=1, bg=entryBackGroundColor, show='*')
        self.password.place(x=20, y=220, width=320, height=30)

        self.logbtn = Button(self.master, text='立即登录', font=('Fixdsys', 14, 'bold'), width=28, fg='white',
                             bg="#0081FF",
                             command=self.do_login)
        self.logbtn.place(x=20, y=280)

        tk.Label(self.master, text='没有账号？', font=self.font, bg=background_color).place(x=20, y=325)
        self.registerbtn = Button(self.master, text='立即注册', font=self.font, bg=background_color, fg="#FFA500",
                                  command=self.show_register)
        self.registerbtn.place(x=103, y=324)

        self.quitbtn = Button(self.master, text="取消", font=self.font, bg=background_color, fg="#FFA500",
                              command=self.click_quit)
        self.quitbtn.place(x=175, y=324)

        self.sc = client.data.sc
        # 把当前
        client.socket_listener.add_listener(self.socket_listener)

    def remove_socket_listener_and_close(self):
        # 关闭当前的
        client.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()

    # 关闭窗口并退出
    def destroy_window(self):
        # 关闭界面
        client.data.tk_root.destroy()

    def socket_listener(self, data):
        if data.get("message_code") == MessageCode.login_failed:
            messagebox.showerror('登录失败', '用户名或密码错误')
            return
        # # {'message_code': 200, 'data': '{"id": 1, "username": "user1", "online": true}'}
        if data.get("message_code") == MessageCode.login_successful:
            # current_user = {"id": 0, "username": ""}
            userinfo = data.get("data")
            userinfo = json.loads(userinfo)
            client.data.current_user = {"id": userinfo.get("id"), "username": userinfo.get("username")}
            # 当前的界面关闭
            self.remove_socket_listener_and_close()
            # 跳转到用户列表界面
            # 聚焦
            contacts = Toplevel(client.data.tk_root, takefocus=True)
            ContactsForm(contacts)
            return

    def do_login(self):
        # 点击登录按钮进行登录
        username = self.username.get()
        password = self.password.get()
        if not username:
            messagebox.showerror("出错了", "用户名不能为空")
            return
        if not password:
            messagebox.showerror("出错了", "密码不能为空")
            return
        # 未注册的情况
        # {"username": username, "password": password}
        # message_code:

        data = {
            "username": username,
            "password": password
        }

        data = json.dumps(data)
        # 将数据发送给服务器端进行验证
        self.sc.send(MessageCode.login, data)

    def show_register(self):
        # 点击注册按钮后 弹出注册界面
        register_form = Toplevel()
        RegisterForm(register_form)

    def click_quit(self):
        # 点击取消
        self.remove_socket_listener_and_close()
        self.destroy_window()
