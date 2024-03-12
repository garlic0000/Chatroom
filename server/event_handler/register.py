import json
from server.settings.message_format import MessageCode
from server import database
import random


# {"username": "user1", "password": "1234567890"}
def run(sc, data):
    data = json.loads(data)
    username = data.get("username")
    password = data.get("password")
    # 过滤？可能会有数据库注入的风险
    # c = database.get_cursor()
    # r = c.execute('SELECT * from users where username=?', [username])
    # rows = r.fetchall()
    rows = database.find_by_username(username)
    if len(rows) > 0:
        sc.send(MessageCode.username_taken)
        return

    while True:
        uid = random.randint(1000, 1000000)
        # r = c.execute('SELECT * from users where id=?', [str(uid)])
        # rows = r.fetchall()
        rows = database.find_by_userid(str(uid))
        if len(rows) == 0:
            break
    database.add_user(str(uid), username, password)
    # c.execute('INSERT into users (id, username,password) values (?,?,?)',
    #           [str(uid), username, md5(password)])
    # id是否改为str类型？？？？?
    sc.send(MessageCode.register_successful, str(uid))
