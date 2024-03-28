current_user = {"id": "", "username": ""}
sc = None
# 用户窗口
tk_root = None

window_instance = [{}, {}]
contact_window = []

# chat_history[target_type][target_id] =
chat_history = [{}, {}]

# unread_message_count[target_type][target_id] = int
unread_message_count = [{}, {}]

# last_message[target_type][target_id] = str
last_message = [{}, {}]

# last_message_timestamp[target_type][target_id] = int
last_message_timestamp = [{}, {}]
