from server.settings.message_format import MessageCode
from server import database
from server.data import *


def run(sc, data):
    user_id = sc_to_user_id[sc]

    # data = username
    username = data.strip().lower()
    print(username)
    rows = database.find_by_username(username)
    if len(rows) == 0:
        sc.send(MessageCode.add_friend_result, [False, '用户名不存在'])
        return
    uid = database.get_userid_by_username(username)
    if uid == user_id:
        sc.send(MessageCode.add_friend_result, [False, '不能加自己为好友'])
        return

    is_friend = database.is_friend(user_id, uid)
    if is_friend:
        sc.send(MessageCode.add_friend_result, [False, '已经是好友/已经发送过好友请求'])
        return

    database.add_friend_request(user_id, uid)
    sc.send(MessageCode.add_friend_result, [True, '发送好友请求成功'])

    # 发送好友请求
    # 好友在线上
    if uid in user_id_to_sc.keys():
        user_id_to_sc[uid].send(MessageCode.incoming_friend_request, database.get_user(user_id))
