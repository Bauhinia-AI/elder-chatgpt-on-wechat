from bridge.reply import Reply, ReplyType
from bot.bot import Bot
import requests

class AIAgentBot(Bot):
    def __init__(self):
        super().__init__()

    def reply(self, query, context=None):
        try: 
            url = "http://47.95.21.135:8014/chat"
            data = {"user_id": context.getRemarkName(), "query": query}
            # data = {"user_id": "邵琦", "query": query}
            response = requests.post(url, json=data)
            print("Chat Response:", response.json()["response"])
            return Reply(ReplyType.TEXT, response.json()["response"])
        except Exception as e:
            return Reply(ReplyType.TEXT, "I'm sorry, please try again later.")
    