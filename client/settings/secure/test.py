from Cryptodome.Cipher import AES
from Cryptodome import Random
import base64


def aes_encode_cbc(key, data):
    iv = Random.new().read(16)
    padding_n = 16 - len(data) % 16
    data = data + padding_n * b'\0'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    di = cipher.encrypt(data)
    di = base64.b64encode(di)
    return di, iv, padding_n


# b'rBVmR1vpsfsTYiEt7yaBDg==', b'<\xa2{l\x9d\xe15\xd4\xf9(#\xa3\xf6\xc6\xff\xcb', 12
def aes_decode_cbc(key, data, iv, padding_n):
    textcipher = AES.new(key, AES.MODE_CBC, iv)
    hu = textcipher.decrypt(data)
    hu = hu[0:-padding_n]
    return hu


if __name__ == "__main__":
    key = "qwertyuiopasdfghjklzxcvbnm123456".encode()  # 转为字节
    # data = "test".encode()
    # print(aes_encode_cbc(key, data))
    data = b'rBVmR1vpsfsTYiEt7yaBDg=='
    data = base64.b64decode(data)
    iv = b'<\xa2{l\x9d\xe15\xd4\xf9(#\xa3\xf6\xc6\xff\xcb'
    padding_n = 12
    print(aes_decode_cbc(key, data, iv, padding_n))
