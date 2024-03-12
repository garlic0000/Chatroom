from server.settings.message_format import MessageCode
from server import database
from server.data import *
from server.settings.add_type import add_target_type


def run(sc, datas):
    user_id = sc_to_user_id[sc]
    username = datas.strip().lower()
    rows = database.find_by_username(username)
    if len(rows) == 0:
        sc.send(MessageCode.add_friend_result, [False, '用户名不存在'])
        return
    uid = database.get_userid_by_username(username)
    if uid == user_id:
        sc.send(MessageCode.add_friend_result, [False, '不能删除自己'])
        return

    is_friend = database.is_friend(user_id, uid)
    if not is_friend:
        sc.send(MessageCode.add_friend_result, [False, '不是好友关系'])
        return

    database.del_friend(user_id, uid)
    ## 从数据库删除聊天记录
    database.del_chat_history_with_friend(user_id, uid)
    # 通知列表更新
    # 被删除的好友
    sc.send(MessageCode.del_friend_request, add_target_type(database.get_user(uid), 0))
    # 给被删好友也发送删除的请求
    if uid in user_id_to_sc.keys():
        user_id_to_sc[uid].send(MessageCode.del_friend_request, add_target_type(database.get_user(user_id), 0))
