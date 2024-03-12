from server.settings.message_format import MessageCode
from server import database
from server.data import *
import time


# {target_type:int(0=私聊 1=群聊),target_id:int,message:str}
# {'target_type': 1, 'target_id': 1, 'message': '是法国'}
def run(sc, data):
    print(data)
    user_id = sc_to_user_id[sc]
    sender = database.get_user(user_id)
    print(sender)
    # target只是dispatch用

    # target_id延后做，对于发送方和接收方不一样
    # message 加密？？？
    # {'id': 1, 'username': 'user1', 'online': True}
    message = {"message": data.get('message', ""), 'sender_id': user_id,
               'sender_name': sender.get('username'),
               'target_type': data.get('target_type'),
               'time': int(round(time.time() * 1000))}

    if data.get('target_type') == 0:
        # 私聊
        if not database.is_friend_with(user_id, data.get('target_id')):
            sc.send(MessageCode.general_failure, '还不是好友')
            return
        # BLOB ---dict----str
        # 给发送方发回执
        message['target_id'] = data['target_id']
        user_id_to_sc[user_id].send(MessageCode.on_new_message, message)
        # sent
        database.add_to_chat_history(user_id, message['target_id'], message['target_type'], message, 1)

        # 给接收方发消息，存入聊天记录
        message['target_id'] = user_id
        # sent
        sent = 0
        if data['target_id'] in user_id_to_sc:
            # sent
            sent = 1
            user_id_to_sc[data['target_id']].send(MessageCode.on_new_message, message)

        database.add_to_chat_history(data['target_id'], message['target_id'], message['target_type'],
                                     message,
                                     sent)

    if data.get('target_type') == 1:
        # 群聊
        message['target_id'] = data['target_id']
        if not database.in_room(user_id, data['target_id']):
            sc.send(MessageCode.general_failure, '还没有加入该群')
            return

        users_id = database.get_room_members_id(data['target_id'])

        for user_id in users_id:
            # sent
            sent = 0
            if user_id in user_id_to_sc.keys():
                user_id_to_sc[user_id].send(MessageCode.on_new_message, message)
                # sent
                sent = 1
            database.add_to_chat_history(user_id, message['target_id'], message['target_type'],
                                         message,
                                         sent)
