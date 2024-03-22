import os
import struct
# ModuleNotFoundError: No module named 'Cryptodome’
# pip install pycryptodome
# pip install pycryptodomex
from Cryptodome.Cipher import AES
from server.settings.secure import get_share_key
from server.settings.others import long_to_bytes
import base64
import json
from server.settings.message_format import get_message_from_code


class SecureChannel:
    def __init__(self, socket, shared_secret):
        # 设置非阻塞
        socket.setblocking(0)
        self.socket = socket
        self.shared_secret = shared_secret
        return

    def send(self, code, data=None):
        # 数据格式
        code_data = {
            "message_code": code,
            "message_info": get_message_from_code(code),
            "data": data
        }
        print("服务器加密前:")
        print(code_data)
        # iv = Random.new().read(16)
        iv = bytes(os.urandom(16))
        code_data = json.dumps(code_data)
        padding_n = 16 - len(code_data) % 16
        code_data = code_data.encode() + padding_n * b'\0'
        encryption = AES.new(self.shared_secret, AES.MODE_CBC, iv)
        encrypted_data = encryption.encrypt(code_data)
        iv = base64.b64encode(iv).decode()  # str
        encrypted_data = base64.b64encode(encrypted_data).decode()  # str
        print("服务器加密后:")
        print(encrypted_data)
        message = {
            "IV": iv, "padding_n": padding_n, "en_message": encrypted_data
        }
        message = json.dumps(message).encode()
        L = len(message)
        self.socket.send(struct.pack('!L', L) + message)  # len
        return

    def receive(self, message):
        message = bytes.decode(message)
        message = json.loads(message)
        iv = message.get("IV")
        iv = base64.b64decode(iv)  # bytes
        padding_n = message.get("padding_n")  # int
        data = message.get("en_message", "")
        print("服务器解密前:")
        print(data)
        data = base64.b64decode(data)
        decryption = AES.new(self.shared_secret, AES.MODE_CBC, iv)
        try:
            decrypted_data = decryption.decrypt(data)
            if padding_n != 0:
                decrypted_data = decrypted_data[0:-padding_n]
            decrypted_data = bytes.decode(decrypted_data)
            decrypted_data = json.loads(decrypted_data)
            print("服务端解密后：")
            print(decrypted_data)
            return decrypted_data
        except:
            print("密钥匹配失败！！！！请重新启动！！！！")
            return -1

    def close(self):
        self.socket.close()


# 服务器端向客户端发送公钥
def server_to_client(socket):
    conn, addr = socket.accept()

    # 首次连接，客户端会发送diffle hellman密钥
    data = conn.recv(1024)
    toward_pubkey = int.from_bytes(data, byteorder='big')
    print("客户端的公钥:")
    print(hex(toward_pubkey)[2:])
    # 把服务器的diffle hellman密钥发送给客户端
    conn.send(long_to_bytes(get_share_key.pubkey))
    print("我的公钥(服务器):")
    print(hex(get_share_key.pubkey)[2:])
    # 计算出共同密钥
    shared_secert = get_share_key.get_shared_secret(toward_pubkey)
    print("共享密钥:")
    print(hex(int.from_bytes(shared_secert, byteorder='big'))[2:])
    sc = SecureChannel(conn, shared_secert)

    return sc
