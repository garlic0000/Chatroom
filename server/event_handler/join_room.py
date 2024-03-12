from server.settings.message_format import MessageCode
import server.data
from server import database
from server.settings.add_type import add_target_type


def run(sc, room_id):
    user_id = server.data.sc_to_user_id[sc]
    if database.in_room(user_id, room_id):
        sc.send(MessageCode.general_failure, '已经在群里了')
        return
    room = database.get_room(room_id)
    if room is None:
        sc.send(MessageCode.general_failure, '群不存在')
        return
    # (user_id, room_id, room_manager=0):
    # 非群主
    database.add_to_room(user_id, room_id)
    # 添加到用户列表
    sc.send(MessageCode.contact_info, add_target_type(room, 1))
