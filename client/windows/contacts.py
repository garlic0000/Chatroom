import json
from tkinter import messagebox
import client.data
from tkinter import *
from client.settings.message_format import MessageCode
from client.windows.vertical_scrolled_frame import VerticalScrolledFrame
from client.windows.contact_item import ContactItem
from client.windows.chat import ChatForm
from tkinter import Toplevel
import datetime
import client.socket_listener
from tkinter import simpledialog
from client.settings.secure.get_share_key import pubkey_str16, prikey_str16


class ContactsForm(Frame):
    bundle_process_done = False

    def remove_socket_listener_and_close(self):
        client.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()
        client.data.tk_root.destroy()

    def socket_listener(self, data):
        # 聊天界面数据
        message_code = data.get("message_code")
        if message_code == MessageCode.login_bundle:
            # {'message_code': 214, 'data': '{"rooms": [], "friends": [], "messages": []}'}
            bundle = data.get("data")
            bundle = json.loads(bundle)
            friends = bundle.get('friends', [])
            rooms = bundle.get('rooms', [])
            messages = bundle.get('messages', [])
            for friend in friends:
                self.handle_new_contact(friend)
            for room in rooms:
                self.handle_new_contact(room)
            # "messages": [{"datas": {"message": "\\u4f60\\u597d", "sender_id": 2, "sender_name": "\\u4eca\\u5929", "target_type": 0, "time": 1621238075480, "target_id": 2}, "sent": 1}, {"datas": {"message": "dfnghn", "sender_id": 1, "sender_name": "user1", "target_type": 0, "time": 1621238119777, "target_id": 2}, "sent": 1}, {"datas": {"message": "\\u5f52\\u8fd8\\u501f\\u6b3e\\uff0c\\u3002", "sender_id": 1, "sender_name": "user1", "target_type": 0, "time": 1621238123962, "target_id": 2}, "sent": 1}]
            for item in messages:
                # 获取消息读取状态
                # ret[str(i)] = {"data": data, "sent": sent}
                # 暂时
                sent = item.get("sent", None)
                # 反序列化
                # 获取所有的消息，包括未读消息
                # message = _deserialize_any(item[0])
                # 未读消息
                message = item.get("datas", "")
                client.socket_listener.digest_message(message, not sent)

            # 数据读取完毕
            self.bundle_process_done = True
            self.refresh_contacts()

        # 收到好友请求
        #  再次登录时收到好友请求
        # {'message_code': 202, 'message_info': '收到好友请求', 'data': '{"ifr": {"user_id": 1, "username": "user1", "online": true}}'}
        # {'message_code': 202, 'message_info': '收到好友请求', 'data': '{"id": 6, "username": "\\u4f60\\u597d", "online": true}'}
        # 在线时收到好友请求
        # {'message_code': 202, 'message_info': '收到好友请求', 'data': {'id': 1, 'username': 'user1', 'online': True}}
        if message_code == MessageCode.incoming_friend_request:
            # print(data)
            # 可能有多个好友请求
            data1 = data.get("data")
            if type(data1) == str:
                data1 = json.loads(data1)
                if data1.get("ifr", {}):
                    data = data1.get("ifr")
            # f = d.get("incoming_friend_request")
            # 离线好友请求？？  再次请求？？？
            username = data1.get("username")
            id = data1.get("id")
            # 在线用户添加好友 将窗口放置于后台则不会弹出提示
            result = messagebox.askyesnocancel("好友请求", "  " + username + "  " + "请求加您为好友")
            if result == None:
                return
            # 同意添加好友，转到好友处理
            self.sc.send(MessageCode.resolve_friend_request, [id, result])

        # 新增好友或群聊
        # {'message_code': 203, 'message_info': '联系列表信息', 'data': {'id': 1, 'username': 'user1', 'online': True, 'type': 0}}
        if message_code == MessageCode.contact_info:
            self.handle_new_contact(data.get('data'))
            return
        # 删除好友
        # {'message_code': 206, 'message_info': '删除好友结果', 'data': {'id': 2, 'username': '今天', 'online': True, 'type': 0}}
        # {'message_code': 206, 'message_info': '删除好友结果', 'data': {'id': 4, 'username': '昨天', 'online': False, 'type': 0}}
        if message_code == MessageCode.del_friend_request:
            self.handle_del_friend(data['data'])
            # 当前用户要删除本地chat_history
            return
        # 给一个非群主的用户-----退出群
        # 给群中所有人----解散群
        # 群主退出群----解散

        if message_code == MessageCode.del_from_room:
            self.handle_del_from_room(data["data"])
            # self.refresh_contacts()
            return
        # {'message_code': 205, 'data': [False, '用户名不存在']}
        if message_code == MessageCode.add_friend_result:
            if data['data'][0]:
                messagebox.showinfo('添加好友', '好友请求已发送')
            else:
                messagebox.showerror('添加好友失败', data['data'][1])
            return

        # 好友在线/离线状态改变
        # 有问题==列表
        # {'message_code': 208, 'message_info': 'friend_on_off_line', 'data': '{"user_id": 2, "online": true}'}
        if message_code == MessageCode.friend_on_off_line:
            data1 = data.get("data")
            data1 = json.loads(data1)
            friend_user_id = data1.get("user_id")
            for contract in self.contacts:
                if contract.get("id") == friend_user_id and contract.get("type") == 0:
                    self.contacts[self.contacts.index(contract)]["online"] = data1.get("online")
                    break
            # for i in range(0, len(self.contacts)):
            #     if self.contacts[i]['id'] == friend_user_id and self.contacts[i]['type'] == 0:
            #         self.contacts[i]['online'] = data['parameters'][0]
            #         break

            self.refresh_contacts()
            return

    # 新加好友,没有任何聊天记录
    # 显示在列表上
    def handle_new_contact(self, data):
        # 有问题
        data['last_timestamp'] = 0
        data['last_message'] = '<--没有消息-->'
        # 显示在列表上
        self.contacts.insert(0, data)
        self.refresh_contacts()

    # 删除好友
    # 获取列表，找到要删除的username
    # 'data': {'id': 4, 'username': '昨天', 'online': False, 'type': 0}}
    def handle_del_friend(self, data):
        for contract in self.contacts:
            if contract.get("username", "") == data["username"]:
                self.contacts.remove(contract)
                break
        self.refresh_contacts()

    def handle_del_from_room(self, data):
        # 退出群
        # print(data)
        # {'id': 1, 'room_name': 'group1', 'type': 1}
        # print(self.contacts)
        # {'id': 3, 'room_name': 'group1', 'type': 1, 'last_timestamp': 0, 'last_message': '<--没有消息-->'}
        # {'id': 1, 'username': 'user1', 'online': True, 'type': 0, 'last_timestamp': 0, 'last_message': '<--没有消息-->'}
        for contract in self.contacts:
            if contract.get("type", "") == 1 and contract.get("id", "") == data["id"]:
                self.contacts.remove(contract)
                break
        self.refresh_contacts()

    # 点击某一个联系人或群组就会跳转到具体的界面
    def on_frame_click(self, e):
        item_id = e.widget.item['id']
        if item_id in client.data.window_instance[e.widget.item['type']]:
            client.data.window_instance[e.widget.item['type']][item_id].master.deiconify()
            return
        # 具体页面
        form = Toplevel(client.data.tk_root, takefocus=True)
        client.data.window_instance[e.widget.item['type']][item_id] = ChatForm(e.widget.item, form)

    def on_add_friend(self):
        result = simpledialog.askstring('添加好友', '请输入用户名')  # str
        if (not result):
            return
        self.sc.send(MessageCode.add_friend, result)

    def on_add_room(self):
        result = simpledialog.askstring('添加群', '请输入群号')  # str
        if (not result):
            return
        self.sc.send(MessageCode.join_room, result)

    def on_create_room(self):
        result = simpledialog.askstring('创建群', '请输入群名称')
        if (not result):
            return
        self.sc.send(MessageCode.create_room, result)

    def on_del_friend(self):
        result = simpledialog.askstring('删除好友', '请输入好友名称')
        if (not result):
            return
        self.sc.send(MessageCode.del_friend, result)

    def get_myinfo(self):

        data = """
        我的姓名:{0}
        我的ID:{1}
        我的公钥:{2}
        我的私钥:{3}
        """.format(client.data.current_user["username"], client.data.current_user["id"], pubkey_str16, prikey_str16)
        simpledialog.messagebox.showinfo('我的信息', data)

    def quit_room(self):
        result = simpledialog.askstring('退出群组', '请输入群号')
        if (not result):
            return
        self.sc.send(MessageCode.quit_from_room, result)

    def dissolve_room(self):
        result = simpledialog.askstring('解散群组', '请输入群号')
        if (not result):
            return
        self.sc.send(MessageCode.dissolve_room, result)

    class my_event:
        widget = None

        def __init__(self, widget):
            self.widget = widget

    # 在群聊天时，群内的用户列表中，点击就会跳转至聊天界面
    # 若不是好友，就会出现好友申请
    def try_open_user_id(self, id, username):

        for i in range(0, len(self.pack_objs)):
            frame = self.pack_objs[i]
            # ??
            if frame.item['id'] == id and frame.item['type'] == 0:
                self.on_frame_click(self.my_event(frame))
                return
        result = messagebox.askyesno("添加好友", username + "不在您的好友列表中，是否加好友？")
        if result:
            self.sc.send(MessageCode.add_friend, username)

    pack_objs = []

    # 刷新联系人列表
    def refresh_contacts(self):
        # 数据已读取完毕
        if not self.bundle_process_done:
            return

        for pack_obj in self.pack_objs:
            # pack_forget不会破坏任何东西,它只是使它不可见
            # 删除控件
            pack_obj.pack_forget()
            # 销毁控件
            pack_obj.destroy()

        self.pack_objs = []
        # 列表时间戳排序
        self.contacts.sort(key=lambda x: -client.data.last_message_timestamp[x['type']].get(x['id'], 0))
        for item in self.contacts:
            contact = ContactItem(self.scroll.interior, self.on_frame_click)
            contact.pack(fill=BOTH, expand=True)
            contact.item = item
            # 每一个用户或群组为一个按钮
            contact.bind("<Button>", self.on_frame_click)
            if (item['type'] == 0):
                # 联系人
                contact.title.config(text=item['username'] + (' [在线]' if item['online'] else ' [离线]'))
                contact.title.config(fg='black' if item['online'] else '#999')
            if (item['type'] == 1):
                # 群
                contact.title.config(text='[群号:' + str(item['id']) + '] ' + item['room_name'])
                contact.title.config(fg='black')
            # 增加控件
            self.pack_objs.append(contact)
            time_message = datetime.datetime.fromtimestamp(
                item['last_timestamp']
            ).strftime('%Y-%m-%d %H:%M:%S')

            contact.last_message_time.config(text=time_message)

            contact.last_message.config(text=client.data.last_message[item['type']].get(item['id'], '<--没有消息-->'))
            contact.last_message_time.config(text=datetime.datetime.fromtimestamp(
                int(client.data.last_message_timestamp[item['type']].get(item['id'], 0)) / 1000
            ).strftime('%Y-%m-%d %H:%M:%S'))
            # 未读消息数
            unread_count = client.data.unread_message_count[item['type']].get(item['id'], 0)
            contact.unread_message_count.pack_forget()
            if unread_count != 0:
                contact.last_message.pack_forget()
                contact.unread_message_count.pack(side=RIGHT, anchor=E, fill=None, expand=False, ipadx=4)
                contact.last_message.pack(side=LEFT, fill=X, expand=True, anchor=W)
                contact.unread_message_count.config(text=str(unread_count))

    def __init__(self, master=None):
        # contact_window = []
        client.data.contact_window.append(self)
        super().__init__(master)
        self.master = master
        self.master.iconbitmap("../client/data/si.ico")
        screen_width = client.data.tk_root.winfo_screenwidth()
        screen_height = client.data.tk_root.winfo_screenheight()
        x = screen_width - 450
        y = (screen_height / 2) - 400
        master.geometry('%dx%d+%d+%d' % (400, 600, x, y))
        self.button_frame = Frame(self)

        self.add_friend = Button(self.button_frame, text="我的信息", command=self.get_myinfo, bg="white")
        self.add_friend.pack(side=LEFT, expand=True, fill=X)
        self.add_friend = Button(self.button_frame, text="添加好友", command=self.on_add_friend, bg="white")
        self.add_friend.pack(side=LEFT, expand=True, fill=X)
        self.add_friend = Button(self.button_frame, text="删除好友", command=self.on_del_friend, bg="white")
        self.add_friend.pack(side=LEFT, expand=True, fill=X)
        self.create_room = Button(self.button_frame, text="创建群", command=self.on_create_room, bg="white")
        self.create_room.pack(side=LEFT, expand=True, fill=X)
        self.add_room = Button(self.button_frame, text="添加群", command=self.on_add_room, bg="white")
        self.add_room.pack(side=LEFT, expand=True, fill=X)
        self.add_room = Button(self.button_frame, text="退出群", command=self.quit_room, bg="white")
        self.add_room.pack(side=LEFT, expand=True, fill=X)
        self.add_room = Button(self.button_frame, text="解散群", command=self.dissolve_room, bg="white")
        self.add_room.pack(side=LEFT, expand=True, fill=X)

        self.button_frame.pack(expand=False, fill=X)
        self.scroll = VerticalScrolledFrame(self)
        self.scroll.pack(fill=BOTH, expand=True)
        self.pack(side=TOP, fill=BOTH, expand=True)

        self.contacts = []

        self.master.title(client.data.current_user['username'] + " - 联系人列表")
        self.sc = client.data.sc
        client.socket_listener.add_listener(self.socket_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_socket_listener_and_close)
