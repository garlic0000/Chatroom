import sqlite3
from server.data import *
import json
from Cryptodome.Cipher import AES
import base64
from hashlib import md5 as _md5

conn = sqlite3.connect('server/database/chat_room.db', isolation_level=None)

# 绝对路径
# conn = sqlite3.connect('D:/project/chatroom7/server/database/chat_room.db', isolation_level=None)


# D:\project\chatroom7\server\database

def get_cursor():
    return conn.cursor()


def commit():
    return conn.commit()


# 获取用户信息
def get_user(user_id):
    c = get_cursor()
    fields = ['id', 'username']
    row = c.execute('SELECT ' + ','.join(fields) + ' FROM users WHERE id=?', [user_id]).fetchall()
    if len(row) == 0:
        return None
    else:
        user = dict(zip(fields, row[0]))
        user['online'] = user_id in user_id_to_sc
        return user


# 未处理的好友请求
def get_pending_friend_request(user_id):
    c = get_cursor()
    users = []
    rows = c.execute('SELECT from_user_id FROM friends WHERE to_user_id=? AND NOT accepted', [user_id]).fetchall()
    for row in rows:
        uid = row[0]
        users.append(get_user(uid))
    return users


# 获取好友
def get_friends(user_id):
    c = get_cursor()
    users = []
    rows = c.execute('SELECT to_user_id FROM friends WHERE from_user_id=? AND accepted', [user_id]).fetchall()
    # print(rows)
    # [(3,), (4,)]
    for row in rows:
        uid = row[0]
        # pprint([uid, type(uid)])
        users.append(get_user(uid))
    return users


# 获取用户所加入的群
def get_user_rooms(user_id):
    c = get_cursor()
    rooms = []
    rows = c.execute('SELECT room_id FROM room_user WHERE user_id=?', [user_id]).fetchall()
    for row in rows:
        room_id = row[0]
        rooms.append(get_room(room_id))
    return rooms


# 用户加入的所有群的群id
def get_user_rooms_id(user_id):
    c = get_cursor()
    rooms = []
    rows = c.execute('SELECT room_id FROM room_user WHERE user_id=?', [user_id]).fetchall()
    for row in rows:
        room_id = row[0]
        rooms.append(room_id)
    return rooms


# 判断好友关系
def is_friend_with(from_user_id, to_user_id):
    c = get_cursor()
    r = c.execute('SELECT 1 FROM friends WHERE from_user_id=? AND to_user_id=? AND accepted=1',
                  [from_user_id, to_user_id]).fetchall()
    return len(r) > 0


# 通过群id获取群名
def get_room(room_id):
    c = get_cursor()
    fields = ['id', 'room_name']
    row = c.execute('SELECT ' + ','.join(fields) + ' FROM rooms WHERE id=?', [room_id]).fetchall()
    if len(row) == 0:
        return None
    else:
        room = dict(zip(fields, row[0]))
        return room


# 是否为群成员
def in_room(user_id, room_id):
    c = get_cursor()
    r = c.execute('SELECT 1 FROM room_user WHERE user_id=? AND room_id=? ',
                  [user_id, room_id]).fetchall()
    return len(r) > 0


# 添加群
def add_to_room(user_id, room_id, room_manager=0):
    c = get_cursor()
    c.execute('INSERT INTO room_user (user_id,room_id, room_manager) VALUES (?,?,?) ',
              [user_id, room_id, room_manager])


# 退群 删除群中某一个成员
def del_user_from_room(user_id, room_id):
    c = get_cursor()
    c.execute('delete from room_user where user_id=? and room_id=?',
              [user_id, room_id])


# 退群 删除群中某成员的聊天记录
def del_user_chat_history_from_room(user_id, room_id):
    c = get_cursor()
    c.execute('delete from  chat_history where user_id=? and target_id=? and target_type=?',
              [user_id, room_id, 1])


# 删除群
def del_room(room_id):
    c = get_cursor()
    c.execute('delete from rooms where id=?', [room_id])


# 解散群 删除所有成员
def del_all_users_from_room(room_id):
    c = get_cursor()
    c.execute('delete from room_user where room_id=?',
              [room_id])


# 解散群 删除所有群聊天记录
def del_all_chat_history_from_room(room_id):
    c = get_cursor()
    c.execute('delete from  chat_history where target_id=? and target_type=?',
              [room_id, 1])


# 判断成员是否为群主
def is_room_manager(user_id, room_id):
    c = get_cursor()
    rows = c.execute('select room_manager from room_user where user_id=? and room_id=?',
                     [user_id, room_id])
    # 群主 1 群成员 0
    # 只有一条记录
    for row in rows:
        return row[0]


# 获得群中所有的用户id
def get_room_members_id(room_id):
    c = get_cursor()
    rows = c.execute('SELECT user_id FROM room_user WHERE room_id=?', [room_id]).fetchall()
    all_ids = []
    for row in rows:
        all_ids.append(row[0])
    # return list(map(lambda x: x[0], get_cursor().execute('SELECT user_id FROM room_user WHERE room_id=?',
    #                                                      [room_id]).fetchall()))
    return all_ids


# 获取群中所有用户的id 用户名 状态
def get_room_members(room_id):
    # 管理员
    # [id, online, username]
    # [1, True, 'user1']
    # {"user_id": , "online": , "username": }
    return list(
        map(lambda x: {"user_id": x[0], "online": x[0] in user_id_to_sc, "username": x[1], "room_manager": x[2]},
            get_cursor().execute(
                'SELECT user_id,username, room_manager FROM room_user LEFT JOIN users ON users.id=user_id WHERE room_id=?',
                [room_id]).fetchall()))
    # 返回列表


# 添加聊天记录
def add_to_chat_history(user_id, target_id, target_type, datas, sent):
    # 聊天记录加密存储？？？
    chated = chat_ED()
    datas, padding_n = chated.chat_encode(datas)
    c = get_cursor()
    c.execute('INSERT INTO chat_history (user_id,target_id,target_type,datas,sent,padding_n) VALUES (?,?,?,?,?,?)',
              [user_id, target_id, target_type, datas, sent, padding_n])


# 获取聊天记录
def get_chat_history(user_id):
    c = get_cursor()
    chated = chat_ED()
    ret = list(map(lambda x: {"datas": chated.chat_decode(x[0], x[2]), "sent": x[1]},
                   c.execute('SELECT datas,sent,padding_n FROM chat_history WHERE user_id=?',
                             [user_id]).fetchall()))
    c = get_cursor()
    # ?
    c.execute('UPDATE chat_history SET sent=1 WHERE user_id=?', [user_id])
    return ret


# def del_chat_history():
def find_by_username(username):
    c = get_cursor()
    r = c.execute('SELECT * from users where username=?', [username])
    return r.fetchall()


def verify_by_username_password(username, password):
    c = get_cursor()
    r = c.execute('SELECT * from users where username=? and password=?', [username, md5(password)])
    rows = r.fetchall()
    if len(rows) != 0:
        return True
    else:
        return False


def find_by_userid(user_id):
    c = get_cursor()
    r = c.execute('SELECT * from users where id=?', [user_id]).fetchall()
    return r


def add_user(user_id, username, password):
    c = get_cursor()
    c.execute('INSERT into users (id, username,password) values (?,?,?)',
              [user_id, username, md5(password)])


# 添加好友请求
def add_friend_request(from_user_id, to_user_id):
    c = get_cursor()
    c.execute('insert into friends (from_user_id,to_user_id,accepted) values (?,?,0)', [from_user_id, to_user_id])


# 是否已是好友
def is_friend(from_user_id, to_user_id):
    c = get_cursor()
    r = c.execute('SELECT 1 from friends where from_user_id=? and to_user_id=? and accepted=1',
                  [from_user_id, to_user_id]).fetchall()
    if len(r) != 0:
        return True
    else:
        return False


# 通过用户名查找id
def get_userid_by_username(username):
    c = get_cursor()
    r = c.execute('SELECT id from users where username=?', [username]).fetchall()
    # 只有一条记录
    return r[0][0]


def del_friend(user_id, uid):
    c = get_cursor()
    c.execute('delete from  friends where from_user_id=? and to_user_id=?', [user_id, uid])
    c.execute('delete from  friends where from_user_id=? and to_user_id=?', [uid, user_id])


def del_chat_history_with_friend(user_id, uid):
    c = get_cursor()
    c.execute('delete from  chat_history where user_id=? and target_id=? and target_type=?',
              [user_id, uid, 0])
    c.execute('delete from  chat_history where user_id=? and target_id=? and target_type=?',
              [uid, user_id, 0])


def resolve_friend_request(user_id, uid):
    c = get_cursor()
    # 将对方 --- > 我  置为允许
    c.execute('update friends set accepted=1 where from_user_id=? and to_user_id=? and accepted=0',
              [uid, user_id])
    # 将 我 ----- > 对方 置为允许
    c.execute('insert into friends (from_user_id,to_user_id,accepted) values (?,?,1)', [user_id, uid])


def del_friend_request(user_id, uid):
    c = get_cursor()
    # 将对方 --- > 我  删除
    c.execute('delete from friends where from_user_id=? and to_user_id=? and accepted=0', [uid, user_id])


def find_friend_request(user_id, uid):
    c = get_cursor()
    # 对方 ---> 我 还未允许
    r = c.execute('SELECT 1 from friends where from_user_id=? and to_user_id=? and accepted=0', [uid, user_id])
    return r.fetchall()


def find_by_roomname(room_id):
    c = get_cursor()
    r = c.execute('SELECT * from rooms where id=?', [room_id])
    return r.fetchall()


def create_room(room_id, room_name):
    c = get_cursor()
    c.execute("insert into rooms (id,room_name) values (?,?)", [room_id, room_name])


class chat_ED:
    def __init__(self):
        # 自己设置key可能有问题
        self.__key = "64ded850be3feb9c2c962e4cb156022f".encode()
        self.__iv = b'\0' * 16
        self.__padding_n = 0

    # 聊天加密函数
    def chat_encode(self, datas):
        print("聊天记录加密前:")
        print(datas)
        datas = json.dumps(datas)
        self.__padding_n = 16 - len(datas) % 16
        datas = datas.encode() + self.__padding_n * b'\0'
        encryption = AES.new(self.__key, AES.MODE_CBC, self.__iv)
        encrypted_data = encryption.encrypt(datas)
        encrypted_data = base64.b64encode(encrypted_data).decode()
        print("聊天记录加密后:")
        print(encrypted_data)
        return encrypted_data, self.__padding_n

    # 聊天解密函数
    def chat_decode(self, datas, padding_n):
        print("聊天记录解密前:")
        print(datas)
        datas = base64.b64decode(datas)
        self.__padding_n = padding_n
        decryption = AES.new(self.__key, AES.MODE_CBC, self.__iv)
        decrypted_data = decryption.decrypt(datas)
        if self.__padding_n != 0:
            decrypted_data = decrypted_data[0:-self.__padding_n]
        decrypted_data = bytes.decode(decrypted_data)
        decrypted_data = json.loads(decrypted_data)
        print("聊天记录解密后:")
        print(decrypted_data)
        return decrypted_data


def md5(text):
    m = _md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()
