import enum


class MessageCode(enum.IntEnum):
    login = 100
    register = 101
    add_friend = 102
    resolve_friend_request = 103
    send_message = 104
    join_room = 105
    create_room = 106

    del_friend = 107
    quit_from_room = 108
    dissolve_room = 109
    query_room_users = 110


    login_successful = 200
    register_successful = 201
    incoming_friend_request = 202
    contact_info = 203
    chat_history = 204
    add_friend_result = 205
    del_friend_request = 206
    del_from_room = 207
    friend_on_off_line = 208
    notify_chat_history = 209
    on_new_message = 210
    server_kick = 211
    query_room_users_result = 212
    room_user_on_off_line = 213
    login_bundle = 214



    login_failed = 300
    username_taken = 301
    general_failure = 302
    general_msg = 303


Messageinfo = dict(

    登录请求=100,
    注册请求=101,
    添加好友=102,
    好友请求处理=103,
    发送消息请求=104,
    添加群请求=105,
    创建群请求=106,
    删除好友请求=107,
    退出群请求=108,
    解散群请求=109,
    query_room_users=110,


    登录成功=200,
    注册成功=201,
    收到好友请求=202,
    联系列表信息=203,
    聊天历史=204,
    添加好友结果=205,
    删除好友结果=206,
    退出群结果=207,
    好友在线状态处理=208,
    notify_chat_history=209,
    发送新消息处理=210,
    客户端占用下线=211,
    query_room_users_result=212,
    群成员在线状态处理=213,
    登录后信息获取=214,


    登录失败=300,
    用户名占用=301,
    错误=302,
    消息=303
)


def get_message_from_code(code):
    # print(Messageinfo)
    for m, n in Messageinfo.items():
        if n == code:
            return m



