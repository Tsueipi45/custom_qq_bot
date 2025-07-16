import json
import os
from botpy import logging
import time

from maimai_py import MaimaiClient, PlayerIdentifier, ArcadeProvider, DivingFishProvider

_log = logging.get_logger()
maimai = MaimaiClient()

USERDATA_PATH = "userdata.json"
SETTINGS_PATH = "settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        raise FileNotFoundError("找不到 settings.json")
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    
settings = load_settings()
DIVINGFISH_TOKEN = settings.get("diving_fish_dev")
divingfish = DivingFishProvider(developer_token=DIVINGFISH_TOKEN)

def load_user_credentials(sender_id: str):
    try:
        with open(USERDATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            user_data = data.get(sender_id)
            if not user_data:
                raise ValueError("未找到用户绑定数据")

            arcade_credentials = user_data.get("arcade_credentials")
            divingfish_token = user_data.get("divingfish_update_token")

            if not arcade_credentials or not divingfish_token:
                raise ValueError("绑定信息不完整")

            return arcade_credentials, divingfish_token
    except Exception as e:
        _log.warning(f"[b50] 加载失败：{e}")
        return None, None


async def b50(client, message, space=None, sender=None):
    if not sender:
        return "[ERROR] 未提供 sender ID，无法上传"
    _log.info(f"[b50] 收到 {sender} 的上传请求")

    start_time = time.perf_counter()  # 开始计时

    arcade_credentials, divingfish_token = load_user_credentials(sender)

    if not arcade_credentials or not divingfish_token:
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content="❌ 请先完成 /绑 \"qrcode解析内容\""
        )
        return

    _log.info(f"[b50] 绑定信息加载成功")

    try:
        # 拉取成绩
        arcade_id = PlayerIdentifier(credentials=arcade_credentials)
        scores = await maimai.scores(arcade_id, provider=ArcadeProvider())

        # 上传到查分器
        diving_id = PlayerIdentifier(credentials=divingfish_token)
        await maimai.updates(diving_id, scores.scores, provider=divingfish)

        elapsed = time.perf_counter() - start_time  # 计算耗时

        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content=f"成绩已成功上传至查分器！共上传 {len(scores.scores)} 条记录\n 耗时：{elapsed:.2f} 秒"
        )

        _log.info(f"[b50] {sender} 成功上传了 {len(scores.scores)} 条成绩，用时 {elapsed:.2f} 秒")

    except Exception as e:
        _log.warning(f"[b50] 上传失败：{e}")
        elapsed = time.perf_counter() - start_time  # 出错也记录耗时
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content=f"❌ 成绩上传失败，请稍后再试\n错误信息：{e}\n耗时：{elapsed:.2f} 秒"
        )