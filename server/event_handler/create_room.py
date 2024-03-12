import random
from server.settings.message_format import MessageCode
import server.data
from server import database
from server.settings.add_type import add_target_type


def run(sc, room_name):
    user_id = server.data.sc_to_user_id[sc]
    # 查询所有群 群允许群名称重复
    while True:
        uid = random.randint(10000, 10000000)
        # r = c.execute('SELECT * from rooms where id=?', [str(uid)])
        # rows = r.fetchall()
        rows = database.find_by_roomname(str(uid))
        if len(rows) == 0:
            break
    database.create_room(str(uid), room_name)
    # c.execute("insert into rooms (id,room_name) values (?,?)", [str(uid), room_name])
    sc.send(MessageCode.contact_info, add_target_type(database.get_room(str(uid)), 1))
    # 1 代表群主
    # 把当前用户添加至该群中
    database.add_to_room(user_id, str(uid), 1)
    sc.send(MessageCode.general_msg, '创建成功，群号为：' + str(uid))
