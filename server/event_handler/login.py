import json
from server.settings.message_format import MessageCode
from server import database
from server.settings.add_type import add_target_type
from server.data import *


# {"message_code": 100, "data": {"username": "user1", "password": "1234567890"}}
# {"username": "user1", "password": "1234567890"}
def run(sc, data):
    # 用户名
    data = json.loads(data)
    username = data.get("username")
    password = data.get("password")
    #
    verify = database.verify_by_username_password(username, password)
    if not verify:
        sc.send(MessageCode.login_failed)
        return

    user_id = database.get_userid_by_username(username)
    # 已经登入，踢下线
    if user_id in user_id_to_sc.keys():
        sc_old = user_id_to_sc[user_id]
        sc_old.send(MessageCode.server_kick)
        sc_old.close()
        remove_sc_from_socket_mapping(sc_old)

    # 记录在线信息，将用户id与线程绑定
    sc_to_user_id[sc] = user_id
    user_id_to_sc[user_id] = sc
    user = database.get_user(user_id)
    # user {'id': 1, 'username': 'user1', 'online': True}
    user = json.dumps(user)
    sc.send(MessageCode.login_successful, user)

    login_bundle = {}

    # 发送群列表
    rms = database.get_user_rooms(user_id)
    login_bundle['rooms'] = list(map(lambda x: add_target_type(x, 1), rms))
    # for rm in rms:
    #     sc.send(MessageCode.contact_info, add_target_type(rm, 1))
    # 发送好友请求
    frs = database.get_pending_friend_request(user_id)

    for fr in frs:
        sc.send(MessageCode.incoming_friend_request, json.dumps(fr))

    # 发送好友列表
    frs = database.get_friends(user_id)
    login_bundle['friends'] = list(map(lambda x: add_target_type(x, 0), frs))

    for fr in frs:
        # sc.send(MessageCode.contact_info, add_target_type(fr, 0))
        # 通知他的好友他上线了
        if fr['id'] in user_id_to_sc:
            fr_online = {
                "user_id": user_id,
                "online": True
            }
            user_id_to_sc[fr['id']].send(MessageCode.friend_on_off_line, json.dumps(fr_online))

    # 通知群聊里的人他上线了
    # [room_id, user_id, online]
    rooms_id = database.get_user_rooms_id(user_id)
    for room_id in rooms_id:
        users_id = database.get_room_members_id(room_id)
        for _user_id in users_id:
            if _user_id in user_id_to_sc and user_id != _user_id:
                # 每项每项通知
                r_u_o = {
                    "room_id": room_id,
                    "user_id": user_id,
                    "online": True
                }
                user_id_to_sc[_user_id].send(MessageCode.room_user_on_off_line,
                                             json.dumps(r_u_o))

    messages = database.get_chat_history(user_id)
    login_bundle['messages'] = messages

    sc.send(MessageCode.login_bundle, json.dumps(login_bundle))
