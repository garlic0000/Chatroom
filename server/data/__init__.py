# 对应的安全连接: 用户id
sc_to_user_id = {}
# 用户id: 对应的安全连接
user_id_to_sc = {}
# 服务器与客户端连接的套接字：对应的安全连接
socket_to_sc = {}

# 所有的连接
# 只要有客户端成功连接服务器 加入此列表
scs = []

chat_history = []


def remove_sc_from_socket_mapping(sc):
    if sc in sc_to_user_id.keys():
        uid = sc_to_user_id[sc]
        # sc_to_user_id中删除
        del sc_to_user_id[sc]
        if uid in user_id_to_sc.keys():
            # user_id_to_sc中删除
            del user_id_to_sc[uid]

    if sc in scs:
        # 删除连接
        scs.remove(sc)

    if sc.socket in socket_to_sc:
        # socket_to_sc中删除
        del socket_to_sc[sc.socket]
