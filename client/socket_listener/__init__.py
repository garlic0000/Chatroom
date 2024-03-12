import select
from pprint import pprint
from tkinter import messagebox
from client.settings.message_format import MessageCode
import client.data
import struct
import sys
import traceback

callback_funcs = []

# [{target_id,target_type,func}]
message_listeners = []


# 获取最新消息
def gen_last_message(obj):
    prefix = ''
    if obj['target_type'] == 1:
        prefix = obj['sender_name'] + ':'
    # 需要更改
    if obj['message']:
        # 聊天记录
        # print(obj['message'])
        return prefix + obj['message'].replace('\n', ' ')


def socket_listener_thread(sc, tk_root):
    bytes_to_receive = 0
    bytes_received = 0
    data_buffer = bytes()
    while True:
        rlist, wlist, xlist = select.select([sc.socket], [sc.socket], [])
        if len(rlist):

            if bytes_to_receive == 0 and bytes_received == 0:
                # 一次新的接收
                conn_ok = True
                first_4_bytes = ''
                try:
                    # ？？？
                    # 端口号放前四个字节
                    first_4_bytes = sc.socket.recv(4)
                except ConnectionError:
                    conn_ok = False

                if first_4_bytes == "" or len(first_4_bytes) < 4:
                    conn_ok = False

                if not conn_ok:
                    print('服务器已被关闭')
                    # messagebox.showerror("出错了", "服务器已经被关闭")
                    tk_root.destroy()
                else:
                    data_buffer = bytes()
                    bytes_to_receive = struct.unpack('!L', first_4_bytes)[0]  # 读取数据的长度

            # 接收数据、拼成块
            buffer = sc.socket.recv(bytes_to_receive - bytes_received)
            data_buffer += buffer
            bytes_received += len(buffer)

            if bytes_received == bytes_to_receive:
                # 当一个数据包接收完毕
                bytes_to_receive = 0
                bytes_received = 0

                try:
                    # {'message_code': 301, 'data': None}
                    data = sc.receive(data_buffer)
                    # if data == -1:
                    #     messagebox.showerror("出错了", "密钥匹配失败，退出重新登录")
                    message_code = data.get("message_code")
                    # 处理general failure
                    if message_code == MessageCode.general_failure:
                        data1 = data.get("data")
                        messagebox.showerror("出错了", data1)

                    # 处理general message
                    if message_code == MessageCode.general_msg:
                        data1 = data.get("data")
                        messagebox.showinfo("消息", data1)

                    if message_code == MessageCode.server_kick:
                        messagebox.showerror("出错了", '您的账户在别处登入')
                        client.data.tk_root.destroy()

                    # 处理on_new_message
                    # {'message_code': 210, 'message_info': 'on_new_message', 'data': {'message': '你好', 'sender_id': 2, 'sender_name': 'user2', 'target_type': 0, 'time': 1621185780902, 'target_id': 1}}
                    if message_code == MessageCode.on_new_message:
                        data1 = data.get("data")
                        digest_message(data1)

                    for func in callback_funcs:
                        func(data)

                except:
                    pprint(sys.exc_info())
                    traceback.print_exc(file=sys.stdout)
                    pass


# 获取聊天记录
# 未读消息
# {'message': '你好', 'sender_id': 2, 'sender_name': 'user2', 'target_type': 0, 'time': 1621185780902, 'target_id': 1}
def digest_message(data, update_unread_count=True):
    # 放入 本地chat_history
    if data['target_id'] not in client.data.chat_history[
        data['target_type']]:
        client.data.chat_history[data['target_type']][
            data['target_id']] = []
    client.data.chat_history[data['target_type']][
        data['target_id']].append(data)
    # 更新 last_message
    client.data.last_message[data['target_type']][
        data['target_id']] = gen_last_message(
        data)
    # 更新 last_message_timestamp
    client.data.last_message_timestamp[data['target_type']][
        data['target_id']] = data[
        'time']
    # 更新 unread_message_count
    if data['target_id'] not in client.data.unread_message_count[
        data['target_type']]:
        client.data.unread_message_count[data['target_type']][
            data['target_id']] = 0
    if data['target_id'] not in client.data.window_instance[
        data['target_type']]:
        if update_unread_count:
            client.data.unread_message_count[data['target_type']][
                data['target_id']] += 1

    # 更新contacts
    client.data.contact_window[0].refresh_contacts()
    # 通知聊天窗口
    for item in message_listeners:
        if item['target_type'] == data['target_type'] and item['target_id'] == \
                data['target_id']:
            item['func'](data)


def add_listener(func):
    callback_funcs.append(func)


def remove_listener(func):
    callback_funcs.remove(func)


func_to_tuple = {}


def add_message_listener(target_type, target_id, func):
    func_to_tuple[func] = {'target_type': target_type, 'target_id': target_id, 'func': func}
    message_listeners.append(func_to_tuple[func])


def remove_message_listener(func):
    if func in func_to_tuple:
        message_listeners.remove(func_to_tuple[func])
