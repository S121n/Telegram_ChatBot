waiting_users = []  # صف انتظار
active_chats = {}   # چت‌های فعال: user_id -> partner_id


def is_in_chat(user_id: int) -> bool:
    return user_id in active_chats


def add_to_waiting(user_data: dict):
    waiting_users.append(user_data)


def find_match(user_data: dict):
    for other in waiting_users:
        if other["gender"] == user_data["target_gender"] and \
           user_data["gender"] == other["target_gender"]:
            waiting_users.remove(other)
            return other
    return None


def start_chat(user1_id: int, user2_id: int):
    active_chats[user1_id] = user2_id
    active_chats[user2_id] = user1_id


def end_chat(user_id: int):
    partner = active_chats.pop(user_id, None)
    if partner:
        active_chats.pop(partner, None)
    return partner
