from datetime import datetime

class MessageContext:
    def __init__(self, message):
        self.chat_id = message.chat.id
        # self.message_id = message.message_id
        # self.text = message.text
        # self.username = message.chat.username
        # self.fisrt_name = message.chat.first_name
        # self.last_name = message.chat.last_name
        # self.name = f"{self.fisrt_name} {self.last_name}".strip()
        # self.timestamp = datetime.now()
        self.serched = {}
        self.user_free = True

    # def __repr__(self):
    #     return (f"MessageContext(chat_id={self.chat_id}, message_id={self.message_id}, "
    #             f"text={self.text}, username={self.username}, name={self.name}, "
    #             f"timestamp={self.timestamp})")