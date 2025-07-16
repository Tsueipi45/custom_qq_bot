import os
import json

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage
from botpy.user import Member

import maimai_py
from maimai_py import MaimaiClient, MaimaiPlates, MaimaiScores, MaimaiSongs, PlayerIdentifier, DivingFishProvider

from plugins import weather_handler, shutdown_handler, fortune_handler, picture_handler, chat_handler, help_handler
from plugins.mai_plugins import b50, bind, upload, where

_log = logging.get_logger()

with open("settings.json", "r", encoding="utf-8") as f1:
    config = json.load(f1)

with open("userdata.json", "r", encoding="utf-8") as f2:
    udata = json.load(f2)

maimai = MaimaiClient()
divingfish = DivingFishProvider(developer_token=config['diving_fish_dev'])

simple_handlers = {
    "/天气": weather_handler.handle_weather,
    "/shutdown": shutdown_handler.handle_shutdown,
    "/图片": picture_handler.handle_picture,
    "/help": help_handler.handle_help,
    "/帮助": help_handler.handle_help,
}

extended_handlers = {
    "/今日运势": fortune_handler.handle_fortune,
    "/b50": b50.b50,
    "/绑": bind.bind_qrcode_element,
    "/水鱼": bind.bind_divingfish_token,
    "/导": upload.upload_scores,
    "/在哪mai": where.where_mai,
}


class MyClient(botpy.Client):
    async def on_ready(self):
        robot_name = self.robot.name if self.robot and hasattr(self.robot, "name") else "Unknown"
        _log.info(f"robot 「{robot_name}」 on_ready!")

    async def on_group_at_message_create(self, message: GroupMessage):
        print(repr(message))  # 日志记录完整消息
        msg = message.content.strip()
        _log.info(f"收到消息：{msg}")

        # 优先查找 simple_handlers
        command_key = next((key for key in simple_handlers if msg.startswith(key)), None)
        if command_key:
            handler = simple_handlers[command_key]
            args = msg[len(command_key):].strip()
            await handler(self, message, args)
            _log.info(f"[处理完成] 使用 simple_handler 处理：{msg}")
            return

        # 再查找 extended_handlers
        command_key = next((key for key in extended_handlers if msg.startswith(key)), None)
        if command_key:
            handler = extended_handlers[command_key]
            args = msg[len(command_key):].strip()
            sender = message.author.member_openid
            await handler(self, message, args, sender)
            _log.info(f"[处理完成] 使用 extended_handler 处理：{msg}")
            return

        # 如果都没有匹配到，走 chat handler
        result = chat_handler.handle_chat(self, message)
        if hasattr(result, "__await__"):
            await result
        _log.info(f"[处理完成] 默认聊天处理：{msg}")

if __name__ == "__main__":
    intents = botpy.Intents(public_messages=True, guild_members=True)
    client = MyClient(intents=intents, is_sandbox=True)
    client.run(appid=config['appid'], secret=config['appsecret'])
