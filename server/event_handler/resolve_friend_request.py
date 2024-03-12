from server.data import *
from server import database
from server.settings.message_format import MessageCode
from server.settings.add_type import add_target_type

# 处理好友请求
# 对方发来好友请求
def run(sc, data):
    user_id = sc_to_user_id[sc]
    # 对方
    uid = data[0]
    # 我是否允许加好友
    accepted = data[1]
    # 对方 ---> 我 还未允许
    # r = c.execute('SELECT 1 from friends where from_user_id=? and to_user_id=? and accepted=0', [uid, user_id])
    # rows = r.fetchall()
    rows = database.find_friend_request(user_id, uid)
    if len(rows) == 0:
        return
    # 不允许加好友
    if not accepted:
        database.del_friend_request(user_id, uid)
        # c = database.get_cursor()
        # c.execute('delete from friends where from_user_id=? and to_user_id=? and accepted=0', [uid, user_id])
        return
    # 允许加好友
    if accepted:
        database.resolve_friend_request(user_id, uid)
        # c = database.get_cursor()
        # # 将对方 --- > 我  置为允许
        # c.execute('update friends set accepted=1 where from_user_id=? and to_user_id=? and accepted=0', [uid, user_id])
        # c = database.get_cursor()
        # # 将 我 ----- > 对方 置为允许
        # c.execute('insert into friends (from_user_id,to_user_id,accepted) values (?,?,1)', [user_id, uid])

        # 用户---0

        # 将用户增加到自己的列表上
        sc.send(MessageCode.contact_info, add_target_type(database.get_user(uid), 0))

        # 用户将自己增加到它的列表上
        if uid in user_id_to_sc.keys():
            user_id_to_sc[uid].send(MessageCode.contact_info, add_target_type(database.get_user(user_id), 0))
