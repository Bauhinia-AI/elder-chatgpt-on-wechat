# encoding:utf-8

import os
import signal
import sys
import time
from bridge.context import Context, ContextType
from bridge.reply import Reply, ReplyType
from channel.wechat.wechat_channel import WechatChannel
from channel.wechat.wechat_message import WechatMessage
from flask import Flask, request
from channel import channel_factory
from common import const
from config import load_config
from plugins import *
import threading

app = Flask(__name__)

@app.route('/startchat', methods=['POST'])
def handle_post():
    data = request.get_json()
    # Now you can use the data
    print(data)
    try:
        user_id = WechatChannel().get_user_id(data["user_id"])
        print(data["user_id"], "'s user_id:", user_id)
        # msg = {'MsgId': '1551450074908259044', 'FromUserName': '@2aab8d186e25b15da56444978c919ea5199f8ea674f40ce10da200c44cd492f9', 'ToUserName': user_id, 'MsgType': 1, 'Content': 'bot 今天有什么事吗', 'Status': 3, 'ImgStatus': 1, 'CreateTime': int(time.time()), 'VoiceLength': 0, 'PlayLength': 0, 'FileName': '', 'FileSize': '', 'MediaId': '', 'Url': '', 'AppMsgType': 0, 'StatusNotifyCode': 0, 'StatusNotifyUserName': '', 'RecommendInfo': {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0}, 'ForwardFlag': 0, 'AppInfo': {'AppID': '', 'Type': 0}, 'HasProductId': 0, 'Ticket': '', 'ImgHeight': 0, 'ImgWidth': 0, 'SubMsgType': 0, 'NewMsgId': 1551450074908259044, 'OriContent': '', 'EncryFileName': '', 'User': {'MemberList': [], 'Uin': 0, 'UserName': user_id, 'NickName': 'Yu', 'HeadImgUrl': '', 'ContactFlag': 3, 'MemberCount': 0, 'RemarkName': '邵琦', 'HideInputBarFlag': 0, 'Sex': 0, 'Signature': '', 'VerifyFlag': 0, 'OwnerUin': 0, 'PYInitial': 'YU', 'PYQuanPin': 'Yu', 'RemarkPYInitial': 'SQ', 'RemarkPYQuanPin': 'shaoqi', 'StarFriend': 0, 'AppAccountFlag': 0, 'Statues': 0, 'AttrStatus': 104549, 'Province': '', 'City': '', 'Alias': '', 'SnsFlag': 257, 'UniFriend': 0, 'DisplayName': '', 'ChatRoomId': 0, 'KeyWord': '', 'EncryChatRoomId': '', 'IsOwner': 0}, 'Type': 'Text', 'Text': data["query"]}
        # cmsg = WechatMessage(msg, False)
        context = Context(ContextType.TEXT, data["query"], {"user_id": user_id, "isgroup": False, "session_id": user_id, "receiver": user_id, "channel": wechatChannel})
        WechatChannel().send(Reply(ReplyType.TEXT, data["query"]),context)
        return {"success": True, "error": ""}
    except Exception as e:
        print(e)
        return {"error": str(e), "success": False}


def run_flask_app():
    app.run(host='0.0.0.0', port=8088)
    
def sigterm_handler_wrap(_signo):
    old_handler = signal.getsignal(_signo)

    def func(_signo, _stack_frame):
        logger.info("signal {} received, exiting...".format(_signo))
        conf().save_user_datas()
        if callable(old_handler):  #  check old_handler
            return old_handler(_signo, _stack_frame)
        sys.exit(0)

    signal.signal(_signo, func)


def start_channel(channel_name: str):
    global wechatChannel
    wechatChannel = channel_factory.create_channel(channel_name)
    if channel_name in ["wx", "wxy", "terminal", "wechatmp", "wechatmp_service", "wechatcom_app", "wework",
                        const.FEISHU, const.DINGTALK]:
        PluginManager().load_plugins()

    if conf().get("use_linkai"):
        try:
            from common import linkai_client
            threading.Thread(target=linkai_client.start, args=(channel,)).start()
        except Exception as e:
            pass
    wechatChannel.startup()


def run():
    try:
        flask_thread = threading.Thread(target=run_flask_app)
        flask_thread.start()
        # load config
        load_config()
        # ctrl + c
        sigterm_handler_wrap(signal.SIGINT)
        # kill signal
        sigterm_handler_wrap(signal.SIGTERM)

        # create channel
        channel_name = conf().get("channel_type", "wx")

        if "--cmd" in sys.argv:
            channel_name = "terminal"

        if channel_name == "wxy":
            os.environ["WECHATY_LOG"] = "warn"

        start_channel(channel_name)
        while True:
            time.sleep(1)
    except Exception as e:
        logger.error("App startup failed!")
        logger.exception(e)


if __name__ == "__main__":
    run()
