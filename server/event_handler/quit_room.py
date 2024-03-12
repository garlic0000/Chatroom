from server.settings.message_format import MessageCode
from server import database
from server.data import *
from server.settings.add_type import add_target_type


def run(sc, datas):
    room_id = datas
    user_id = sc_to_user_id[sc]
    room = database.get_room(room_id)
    if room is None:
        sc.send(MessageCode.general_failure, '群不存在')
        return
    if not database.in_room(user_id, room_id):
        sc.send(MessageCode.general_failure, '不在该群里了')
        return
    # 如果是群主退出群----解散
    is_room_manager = database.is_room_manager(user_id, room_id)
    if is_room_manager == 1:
        database.del_room(room_id)
        database.del_all_chat_history_from_room(room_id)
        # 给群中的每一个用户发消息
        for uid in database.get_room_members_id(room_id):
            if uid in user_id_to_sc.keys():
                user_id_to_sc[uid].send(MessageCode.del_from_room, add_target_type(room, 1))
        # 先给群成员发消息，再删除群成员
        database.del_all_users_from_room(room_id)
        return
    else:
        # 删除群中用户
        database.del_user_from_room(user_id, room_id)
        # 删除聊天记录
        database.del_user_chat_history_from_room(user_id, room_id)
        sc.send(MessageCode.del_from_room, add_target_type(room, 1))
