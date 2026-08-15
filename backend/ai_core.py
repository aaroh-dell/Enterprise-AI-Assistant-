from backend.agents.supervisor import route_and_respond


def get_ai_response(chat_history, user_input, employee_id, pending_action=None):
    return route_and_respond(chat_history, user_input, employee_id, pending_action)