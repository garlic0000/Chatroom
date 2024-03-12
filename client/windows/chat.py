import datetime
import json
from tkinter import *

import client.data
from client.socket_listener import *
from client.settings.message_format import *
from tkinter.scrolledtext import ScrolledText
from tkinter import colorchooser
from tkinter import simpledialog
from tkinter import filedialog
from PIL import Image, ImageTk
from io import BytesIO
from client import socket_listener
import binascii


class ChatForm(Frame):
    font_color = "#000000"
    font_size = 20
    user_list = []
    tag_i = 0

    def remove_listener_and_close(self):
        remove_message_listener(self.message_listener)
        client.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()
        if self.target['id'] in client.data.window_instance[self.target['type']]:
            del client.data.window_instance[self.target['type']][self.target['id']]

    def message_listener(self, data):
        self.digest_message(data)

    def socket_listener(self, data):
        # print("聊天界面")
        # print(data)
        message_code = data.get("message_code")
        # 请求群成员结果  群成员
        # {'message_code': 212, 'message_info': 'query_room_users_result', 'data': '{"room_members": [{"user_id": 1, "online": true, "username": "user1", "room_manager": 1}, {"user_id": 2, "online": false, "username": "\\u4eca\\u5929", "room_manager": 0}], "room_id": 1}'}
        if message_code == MessageCode.query_room_users_result:
            data1 = data.get("data")
            data1 = json.loads(data1)
            # {'id': 1, 'room_name': '开心每一天', 'type': 1, 'last_timestamp': 0, 'last_message': '<--没有消息-->'}
            if data1.get("room_id") != self.target['id']:
                return
            # "room_members": [{"user_id": 1, "online": true, "username": "user1", "room_manager": 1}, {"user_id": 2, "online": false, "username": "\\u4eca\\u5929", "room_manager": 0}]
            self.user_list = data1.get("room_members")
            self.refresh_user_listbox()

        # {'message_code': 213, 'message_info': 'room_user_on_off_line', 'data': '{"room_id": 1, "user_id": 2, "online": true}'}
        if message_code == MessageCode.room_user_on_off_line:
            # print(data)
            # [room_id, user_id, online]
            data1 = data.get("data")
            data1 = json.loads(data1)
            if data1.get("room_id") != self.target['id']:
                return
            for userlist in self.user_list:
                if userlist.get("user_id") == data1.get("user_id"):
                    self.user_list[self.user_list.index(userlist)]["online"] = data1.get("online")

            self.refresh_user_listbox()

    def refresh_user_listbox(self):
        # [{"user_id": 1, "online": true, "username": "user1"}, {"user_id": 2, "online": true, "username": "\\u4eca\\u5929"}]
        # [id, online, username]
        # [1, True, 'user1']
        self.user_listbox.delete(0, END)
        # self.user_list = data.get("room_members")
        # ???
        # self.user_list.sort(key=lambda x: x[2])
        # [{"user_id": 1, "online": true, "username": "user1", "room_manager": 1}, {"user_id": 2, "online": false, "username": "\\u4eca\\u5929", "room_manager": 0}]
        for user in self.user_list:
            # {"user_id": 1, "online": true, "username": "user1"}
            # [1, True, 'user1']
            show_name = ''
            if user.get("online"):
                show_name = user.get("username") + "(在线)"
            else:
                show_name = user.get("username") + "(离线)"
            if user.get("room_manager"):
                show_name += '----[管理员]'

            self.user_listbox.insert(0, show_name)
            self.user_listbox.itemconfig(0, {'fg': ("black" if user.get("online") else "#999")})

    # 将聊天记录以对应的格式添加到显示区
    def digest_message(self, data):
        time = datetime.datetime.fromtimestamp(
            int(data['time']) / 1000
        ).strftime('%Y-%m-%d %H:%M:%S')
        # tags = ''
        if client.data.current_user['id'] == data['sender_id']:
            tags1 = 'my_time'
            tags2 = 'my_message'
            self.append_to_chat_box(time + "  " + data['sender_name'] + '\n\n', tags1)
        else:
            tags1 = 'their_time'
            tags2 = 'their_message'
            self.append_to_chat_box(data['sender_name'] + "  " + time + '\n\n', tags1)

        self.append_to_chat_box(data['message'] + '\n\n', tags2)

    def user_listbox_double_click(self, _):
        if len(self.user_listbox.curselection()) == 0:
            return None
        index = self.user_listbox.curselection()[0]
        # print(self.user_list[len(self.user_list) - 1 - index])
        # [2, False, 'user2']
        selected_user_id = self.user_list[len(self.user_list) - 1 - index].get("user_id")
        selected_user_username = self.user_list[len(self.user_list) - 1 - index].get("username")
        if selected_user_id == client.data.current_user['id']:
            # 点到自己的名称
            return
        client.data.contact_window[0].try_open_user_id(selected_user_id,
                                                       selected_user_username)
        # pprint(selected_user_id)
        return

    def __init__(self, target, master=None):
        super().__init__(master)
        self.master = master
        master.resizable(width=True, height=True)
        master.geometry('660x500')
        # master.minsize(520, 370)
        self.target = target
        background_color = "white"
        self.master.iconbitmap("client\data\si.ico")
        self.master.configure(background=background_color)
        # 群成员用户列表
        self.user_listbox = Listbox(self, bg='white')
        client.socket_listener.add_listener(self.socket_listener)
        client.data.unread_message_count[self.target['type']][self.target['id']] = 0
        client.data.contact_window[0].refresh_contacts()

        self.sc = client.data.sc

        # 与用户聊天时，标题显示该联系人名称
        if self.target['type'] == 0:
            self.master.title(self.target['username'])
        # 在群中聊天时，标题显示群id
        if self.target['type'] == 1:
            # "群:" + str(self.target['id']) + " " +
            self.master.title(self.target['room_name'])
            self.sc.send(MessageCode.query_room_users, self.target['id'])

        self.right_frame = Frame(self, bg='white')

        # 双击群内用户跳转至聊天界面后添加好友界面
        self.user_listbox.bind('<Double-Button-1>', self.user_listbox_double_click)
        if self.target['type'] == 1:
            # 群中用户列表
            self.user_listbox.pack(side=RIGHT, expand=False, fill=BOTH)
        # 发送消息的区域
        self.right_frame.pack(side=LEFT, expand=True, fill=BOTH)
        # 输入消息并发送的区域
        self.input_frame = Frame(self.right_frame, bg='white')

        # 发送消息的区域
        self.input_textbox = ScrolledText(self.right_frame, height=10)
        # 发送消息绑定快捷键
        self.input_textbox.bind("<Control-Return>", self.send_message)
        # 发送消息的按键
        self.send_btn = Button(self.input_frame, text='发送消息', command=self.send_message, width=12, height=2)
        self.send_btn.pack(side=RIGHT, expand=False)
        # 显示消息，聊天记录的地方
        self.chat_box = ScrolledText(self.right_frame, bg='white')
        self.input_frame.pack(side=BOTTOM, fill=X, expand=False)
        self.input_textbox.pack(side=BOTTOM, fill=X, expand=False, padx=(0, 0), pady=(0, 0))
        self.chat_box.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.chat_box.bind("<Key>", lambda e: "break")
        # 自己的名称为绿色,其他人的为蓝色，消息为黑色，系统的为灰色
        # 自己发的消息在右边
        self.chat_box.tag_config("default", lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_box.tag_config("my_time", foreground="green", spacing1='5', justify='right')
        self.chat_box.tag_config("my_message", foreground="black", spacing1='0', justify='right', font=(None, 12))
        self.chat_box.tag_config("their_time", foreground="blue", spacing1='5')
        self.chat_box.tag_config("their_message", foreground="black", spacing1='5', font=(None, 12))
        self.chat_box.tag_config("system", foreground="grey", spacing1='0',
                                 justify='center',
                                 font=(None, 8))

        self.pack(expand=True, fill=BOTH)

        add_message_listener(self.target['type'], self.target['id'], self.message_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_listener_and_close)

        # 历史消息显示
        if target['id'] in client.data.chat_history[self.target['type']]:
            for msg in client.data.chat_history[self.target['type']][target['id']]:
                self.digest_message(msg)

            self.append_to_chat_box('<-----以上是历史消息----->\n', 'system')

    def append_to_chat_box(self, message, tags):
        self.chat_box.insert(END, message, [tags, 'default'])
        self.chat_box.update()
        self.chat_box.see(END)

    def send_message(self, _=None):
        message = self.input_textbox.get("1.0", END)
        if not message or message.replace(" ", "").replace("\r", "").replace("\n", "") == '':
            return
        self.sc.send(MessageCode.send_message,
                     # type => 0：用户 1：群
                     {'target_type': self.target['type'], 'target_id': self.target['id'],
                      'message': message.strip().strip('\n')
                      })
        self.input_textbox.delete("1.0", END)
        return 'break'
