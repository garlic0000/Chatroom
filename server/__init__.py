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
    # 创建TCP/IPv4套接字
    # AF_INET IPv4  AF_INET6 IPv6 SOCK_STREAM TCP SOCK_DGRAM UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 端口复用 把多个套接字绑定在一个端口上
    # SOL_SOCKET 套接字描述符 SO_REUSEADDR 取1 打开复用功能
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定 指定的ip地址和端口号
    s.bind((config.server['bind_ip'], config.server['bind_port']))
    # 开始监听
    s.listen(5)  # 为什么设置为5？ https://blog.csdn.net/wanxuexiang/article/details/84075884

    print("服务端绑定IP和端口为" + config.server['bind_ip'] + ":" + str(config.server['bind_port']))
    print("等待客户端的连接...")

    bytes_to_receive = {}  # 对应的连接: 要接受的字节数
    bytes_received = {}  # 对应的连接: 已经接受的字节数
    data_buffer = {}  # 对应的连接: 数据块

    while True:
        # rlist: 监听socket是否变为可读状态
        # wlist: 监听socket是否变为可写状态
        # xlist: 监听socket是否出错
        # select函数阻塞进程，直到x.socket被触发
        # 监听服务器套接字和获得的客户端套接字
        rlist, wlist, xlist = select.select(list(map(lambda x: x.socket, scs)) + [s], [], [])

        for i in rlist:  # 可读

            # 服务器端套接字被触发（监听到有客户端连接服务器）
            if i == s:
                sc = server_to_client(s)  # 协商共享密钥 返回安全连接
                socket_to_sc[sc.socket] = sc  # 记住对应的连接
                scs.append(sc)  # 增加一个新的连接
                # 数据初始化
                bytes_to_receive[sc] = 0
                bytes_received[sc] = 0
                data_buffer[sc] = bytes()
                continue

            # 不是服务器端socket被触发,则是已连接的客户端发送消息
            # 对对应的套接字进行操作
            sc = socket_to_sc[i]

            if bytes_to_receive[sc] == 0 and bytes_received[sc] == 0:
                # 一次新的接收
                conn_ok = True
                first_4_bytes = ''
                try:
                    # 前4个字节为数据长度
                    first_4_bytes = sc.socket.recv(4)
                except ConnectionError:
                    conn_ok = False

                if first_4_bytes == "" or len(first_4_bytes) < 4:
                    conn_ok = False

                if not conn_ok:
                    # 连接未成功
                    sc.close()

                    if sc in sc_to_user_id:
                        # 获取该连接对应的用户id
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
                                    # 群成员在线 该成员不是本人
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
                    # 连接成功
                    # 初始化数据块 准备接受数据
                    data_buffer[sc] = bytes()
                    # 读取要接受的数据的长度
                    bytes_to_receive[sc] = struct.unpack('!L', first_4_bytes)[0]

            # 数据还未接受完 继续接受
            buffer = sc.socket.recv(bytes_to_receive[sc] - bytes_received[sc])
            data_buffer[sc] += buffer
            bytes_received[sc] += len(buffer)

            if bytes_received[sc] == bytes_to_receive[sc] and bytes_received[sc] != 0:
                # 数据接收完毕
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
                    # 根据message_code进行事件处理
                    handle_event(sc, data.get("message_code"), data.get("data", ""))
                except:
                    pprint(sys.exc_info())
                    traceback.print_exc(file=sys.stdout)
                    pass
                # 数据块清空
                data_buffer[sc] = bytes()


if __name__ == "__main__":
    run()
