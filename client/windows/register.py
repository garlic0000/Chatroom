import json
import tkinter as tk
from tkinter import messagebox
from client.settings.message_format import MessageCode
import tkinter.font as tkFont
import client.socket_listener
import client.data
from tkinter import *


class RegisterForm(tk.Frame):
    def socket_listener(self, data):
        # data为字典
        if data.get("message_code") == MessageCode.username_taken:
            messagebox.showerror('出错了', '用户名已被使用，请换一个')
            return
        # {'message_code': 201, 'data': 2}
        if data.get("message_code") == MessageCode.register_successful:
            messagebox.showinfo('注册', '注册成功，您的用户ID为：' + str(data.get("data")))
            self.remove_socket_listener_and_close()
            return

    def remove_socket_listener_and_close(self):
        client.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()

    def do_register(self):
        username = self.username.get()
        password = self.password.get()
        password_confirmation = self.password_confirmation.get()
        if not username:
            messagebox.showerror("出错了", "用户名不能为空")
            return
        if not password:
            messagebox.showerror("出错了", "密码不能为空")
            return
        if password != password_confirmation:
            messagebox.showerror("出错了", "两次密码输入不一致")
            return
        if len(password) < 8 or len(password) > 16:
            messagebox.showerror("出错了", "密码长度为8~16位")
            return
        data = {
            "username": username,
            "password": password
        }
        self.sc.send(MessageCode.register, json.dumps(data))

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        screen_width = client.data.tk_root.winfo_screenwidth()
        screen_height = client.data.tk_root.winfo_screenheight()
        w = 370
        h = 480
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.sc = client.data.sc
        self.master.iconbitmap("client\data\si.ico")
        self.master.title('注册')
        background_color = "white"
        self.master.configure(background=background_color)
        self.font = tkFont.Font(family='Fixdsys', size=10)

        ft = tkFont.Font(family='Fixdsys', size=20, weight=tkFont.BOLD)
        self.label_login = Label(self.master, text="注册", font=ft, bg=background_color).place(x=150, y=44)

        entryBackGroundColor = "#F3F3F4"
        self.label_username = Label(self.master, text='请输入用户名:', font=self.font, bg=background_color).place(x=20, y=115)
        self.label_password = Label(self.master, text='请输入8~16位密码:', font=self.font, bg=background_color).place(x=20,
                                                                                                                y=185)
        self.label_password_confirmation = Label(self.master, text='请确认密码:', font=self.font, bg=background_color).place(
            x=20, y=245)
        # 头像！！！！
        self.username = Entry(self.master, highlightthickness=1, bg=entryBackGroundColor)
        self.username.place(x=20, y=145, width=320, height=30)

        self.password = Entry(self.master, highlightthickness=1, bg=entryBackGroundColor, show='*')
        self.password.place(x=20, y=215, width=320, height=30)

        self.password_confirmation = Entry(self.master, highlightthickness=1, bg=entryBackGroundColor, show='*')
        self.password_confirmation.place(x=20, y=275, width=320, height=30)

        self.registerbtn = Button(self.master, text='注册', font=('Fixdsys', 14, 'bold'), fg='white', bg="#0081FF",
                                  command=self.do_register)
        self.registerbtn.place(x=60, y=330)

        self.quitbtn = Button(self.master, text="取消", font=('Fixdsys', 14, 'bold'), fg='white', bg="#FFA500",
                              command=self.click_quit)
        self.quitbtn.place(x=215, y=330)

        self.sc = client.data.sc
        client.socket_listener.add_listener(self.socket_listener)
        # 处理窗口关闭事件
        master.protocol("WM_DELETE_WINDOW", self.remove_socket_listener_and_close)

    def click_quit(self):
        self.remove_socket_listener_and_close()
