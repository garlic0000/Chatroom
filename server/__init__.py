import socket
from server.settings import config
from server.settings.secure.secure_channel import server_to_client
from server.event_handler import handle_event
from server.data import *
import server.data
from server.settings.message_format import MessageCode
import select
from server import database
from pprint import pprint
import struct
import sys
import traceback
from tkinter import messagebox
import json


def run():
    # TCP/IP – IPv4  TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((config.server['bind_ip'], config.server['bind_port']))
    s.listen(1)

    print("Server listening on " + config.server['bind_ip'] + ":" + str(config.server['bind_port']))

    bytes_to_receive = {}
    bytes_received = {}
    data_buffer = {}

    while True:
        # 1.rlist：list类型，监听其中的socket或者文件描述符是否变为可读状态，返回那些可读的socket或者文件描述符组成的list
        # 2.wlist：list类型，监听其中的socket或者文件描述符是否变为可写状态，返回那些可写的socket或者文件描述符组成的list
        # 3.xlist：list类型，监听其中的socket或者文件描述符是否出错，返回那些出错的socket或者文件描述符组成的list
        rlist, wlist, xlist = select.select(list(map(lambda x: x.socket, scs)) + [s], [], [])

        for i in rlist:

            if i == s:
                # 监听socket为readable，说明有新的客户要连入
                sc = server_to_client(s)  # 协商共享密钥 返回安全连接
                socket_to_sc[sc.socket] = sc
                scs.append(sc)
                bytes_to_receive[sc] = 0
                bytes_received[sc] = 0
                data_buffer[sc] = bytes()
                continue

            # 如果不是监听socket，就是旧的客户发消息过来了
            sc = socket_to_sc[i]

            if bytes_to_receive[sc] == 0 and bytes_received[sc] == 0:
                # 一次新的接收
                conn_ok = True
                first_4_bytes = ''
                try:
                    first_4_bytes = sc.socket.recv(4)
                except ConnectionError:
                    conn_ok = False

                if first_4_bytes == "" or len(first_4_bytes) < 4:
                    conn_ok = False

                if not conn_ok:
                    sc.close()

                    if sc in sc_to_user_id:
                        user_id = sc_to_user_id[sc]
                        # 通知他的好友他下线了

                        frs = database.get_friends(user_id)
                        for fr in frs:
                            if fr['id'] in user_id_to_sc:
                                offline = {
                                    "user_id": user_id,
                                    "online": False
                                }
                                user_id_to_sc[fr['id']].send(MessageCode.friend_on_off_line, json.dumps(offline))

                        # 通知群聊里的人
                        # [room_id, user_id, online]
                        rooms_id = database.get_user_rooms_id(user_id)
                        for room_id in rooms_id:
                            users_id = database.get_room_members_id(room_id)
                            for _user_id in users_id:
                                if _user_id in user_id_to_sc and user_id != _user_id:
                                    offline = {
                                        "user_id": user_id,
                                        "room_id": room_id,
                                        "online": False
                                    }
                                    user_id_to_sc[_user_id].send(MessageCode.room_user_on_off_line,
                                                                 json.dumps(offline))

                    # 把他的连接信息移除
                    remove_sc_from_socket_mapping(sc)

                else:
                    data_buffer[sc] = bytes()
                    bytes_to_receive[sc] = struct.unpack('!L', first_4_bytes)[0]   # 读取数据的长度

            buffer = sc.socket.recv(bytes_to_receive[sc] - bytes_received[sc])
            data_buffer[sc] += buffer
            bytes_received[sc] += len(buffer)

            if bytes_received[sc] == bytes_to_receive[sc] and bytes_received[sc] != 0:
                # 当一个数据包接收完毕
                bytes_to_receive[sc] = 0
                bytes_received[sc] = 0
                try:
                    # 解密
                    data = sc.receive(data_buffer[sc])
                    if data == -1:
                        messagebox.showerror("出错了", "密钥不匹配")
                        # 让其他已连接的----退出
                        return
                    # 解密后根据消息码转到对应的功能
                    # eg: {"message_code": 100, "data": {"username": "user1", "password": "1234567890"}}
                    # 有时只发送消息码
                    # data为字符串
                    # 之前dumps过
                    handle_event(sc, data.get("message_code"), data.get("data", ""))
                except:
                    pprint(sys.exc_info())
                    traceback.print_exc(file=sys.stdout)
                    pass
                data_buffer[sc] = bytes()
