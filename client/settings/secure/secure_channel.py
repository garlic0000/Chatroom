import math
import os
import socket
import struct
from Cryptodome.Cipher import AES
from client.settings.secure import get_share_key
from client.settings.others import long_to_bytes
from client.settings import config
from client.settings.message_format import get_message_from_code
import base64
import json


class SecureChannel:
    def __init__(self, socket, shared_secret):
        # 设置非阻塞
        socket.setblocking(0)
        self.socket = socket
        self.shared_secret = shared_secret
        return

    def send(self, code, data):
        # 数据格式
        # 增加消息
        code_data = {
            "message_code": code,
            "message_info": get_message_from_code(code),
            "data": data
        }
        print("客户端加密前:")
        print(code_data)
        # iv = Random.new().read(16)
        iv = bytes(os.urandom(16))
        code_data = json.dumps(code_data)
        padding_n = 16 - len(code_data) % 16
        code_data = code_data.encode() + padding_n * b'\0'
        encryption = AES.new(self.shared_secret, AES.MODE_CBC, iv)
        encrypted_data = encryption.encrypt(code_data)
        iv = base64.b64encode(iv).decode()  # 将IV进行base64编码后转字符串进行传输
        encrypted_data = base64.b64encode(encrypted_data).decode()  # str
        print("客户端加密后:")
        print(encrypted_data)
        message = {
            "IV": iv, "padding_n": padding_n, "en_message": encrypted_data
        }
        message = json.dumps(message).encode()
        L = len(message)
        self.socket.send(struct.pack('!L', L) + message)
        return

    def receive(self, message):
        message = bytes.decode(message)
        message = json.loads(message)
        iv = message.get("IV")
        iv = base64.b64decode(iv)
        padding_n = message.get("padding_n")  # int
        data = message.get("en_message", "")
        print("客户端解密前:")
        print(data)
        data = base64.b64decode(data)
        decryption = AES.new(self.shared_secret, AES.MODE_CBC, iv)
        try:  # 密钥匹配失败
            decrypted_data = decryption.decrypt(data)
            if padding_n != 0:
                decrypted_data = decrypted_data[0:-padding_n]
            decrypted_data = bytes.decode(decrypted_data)
            decrypted_data = json.loads(decrypted_data)
            print("客户端解密后：")
            print(decrypted_data)
            return decrypted_data
        except:
            # 密钥不同 重新登录
            print("密钥匹配失败！！！！")

    def close(self):
        self.socket.close()


# 客户端向服务器端发送公钥
def client_to_server():
    # 创建TCP/IPv4套接字
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连接服务器
    s.connect((config.client['server_ip'], int(config.client['server_port'])))

    # 首次连接，用diffle hellman交换密钥
    print("我的公钥(客户端):")
    print(hex(get_share_key.pubkey)[2:])
    s.send(long_to_bytes(get_share_key.pubkey))

    # 首次连接，收到服务器diffle hellman交换密钥
    data = s.recv(1024)
    toward_pubkey = int.from_bytes(data, byteorder='big')
    print("服务器的公钥:")
    print(hex(toward_pubkey)[2:])
    # 计算出共同密钥
    shared_secret = get_share_key.get_shared_secret(toward_pubkey)
    print("共享密钥")
    print(hex(int.from_bytes(shared_secret, byteorder='big'))[2:])
    sc = SecureChannel(s, shared_secret)

    return sc
