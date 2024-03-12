import server.event_handler.login
import server.event_handler.send_message
import server.event_handler.register
import server.event_handler.resolve_friend_request
import server.event_handler.add_friend
import server.event_handler.join_room
import server.event_handler.create_room
import server.event_handler.query_room_users
import server.event_handler.del_friend
import server.event_handler.quit_room
import server.event_handler.dissovle_room
from server.settings.message_format import MessageCode


event_handler_map = {
    # 运行某个文件
    MessageCode.login: login,
    MessageCode.send_message: send_message,
    MessageCode.register: register,
    MessageCode.resolve_friend_request: resolve_friend_request,
    MessageCode.add_friend: add_friend,
    MessageCode.join_room: join_room,
    MessageCode.create_room: create_room,
    MessageCode.query_room_users: query_room_users,
    MessageCode.del_friend: del_friend,
    MessageCode.quit_from_room: quit_room,
    MessageCode.dissolve_room: dissovle_room
}


def handle_event(sc, event_type, datas):
    event_handler_map[event_type].run(sc, datas)
