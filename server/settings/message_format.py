import enum


class MessageCode(enum.IntEnum):
    # === Client Action 100-199
    # [username, password]
    login = 100
    # [username, password]
    register = 101
    # username:str
    add_friend = 102
    resolve_friend_request = 103
    # {target_type:int(0=私聊 1=群聊),target_id:int,message:str}
    send_message = 104
    # id:int
    join_room = 105
    # name:str
    create_room = 106

    del_friend = 107
    quit_from_room = 108
    dissolve_room = 109
    # id:int
    query_room_users = 110


    # === Server Action 200-299
    login_successful = 200
    register_successful = 201
    incoming_friend_request = 202
    contact_info = 203
    chat_history = 204
    # [successful:bool,err_msg:str]
    add_friend_result = 205
    # [online:bool,friend_user_id:int]
    del_friend_request = 206
    del_from_room = 207
    friend_on_off_line = 208
    notify_chat_history = 209
    # [target_type:int(0=私聊 1=群聊),target_id:int,message:str,sender_id:int,sender_name:str,time:int]
    on_new_message = 210
    server_kick = 211
    query_room_users_result = 212
    # [room_id, user_id, online]
    room_user_on_off_line = 213
    login_bundle = 214
    # del_all_from_room = 116

    # === Failure 300-399
    login_failed = 300
    username_taken = 301
    # err_msg:str
    general_failure = 302
    # msg:str
    general_msg = 303


Messageinfo = dict(
    # === Client Action 100-199
    # [username, password]
    登录请求=100,
    # [username, password]
    注册请求=101,
    # username:str
    添加好友=102,
    处理好友请求=103,
    # {target_type:int(0=私聊 1=群聊),target_id:int,message:str}
    发送消息请求=104,
    # id:int
    添加群请求=105,
    # name:str
    创建群请求=106,

    删除好友请求=107,
    退出群请求=108,
    解散群请求=109,
    # id:int
    query_room_users=110,

    # === Server Action 200-299
    登录成功=200,
    注册成功=201,
    收到好友请求=202,
    联系列表信息=203,
    聊天历史=204,
    # [successful:bool,err_msg:str]
    添加好友结果=205,
    # [online:bool,friend_user_id:int]
    删除好友结果=206,
    退出群结果=207,
    好友在线状态处理=208,
    notify_chat_history=209,
    # [target_type:int(0=私聊 1=群聊),target_id:int,message:str,sender_id:int,sender_name:str,time:int]
    发送新消息处理=210,
    server_kick=211,
    query_room_users_result=212,
    # [room_id, user_id, online]
    群成员在线状态处理=213,
    登录后信息获取=214,
    # del_all_from_room=116,

    # === Failure 300-399
    登录失败=300,
    用户名占用=301,
    # err_msg:str
    错误=302,
    # msg:str
    错误消息=303
)


def get_message_from_code(code):
    # print(Messageinfo)
    for m, n in Messageinfo.items():
        if n == code:
            return m


# g = get_message_from_code(103)
# print(g)

