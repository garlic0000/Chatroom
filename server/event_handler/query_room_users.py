from server.settings.message_format import MessageCode
import server.data
from server import database
import json

# {'message_code': <MessageCode.query_room_users: 110>, 'message_info': 'query_room_users', 'data': 1}
def run(sc, datas):
    room_id = datas
    user_id = server.data.sc_to_user_id[sc]
    if not database.in_room(user_id, room_id):
        sc.send(MessageCode.general_failure, '不在群里')
        return
    all = {
        "room_members": database.get_room_members(room_id),
        "room_id": room_id
    }
    sc.send(MessageCode.query_room_users_result, json.dumps(all))
