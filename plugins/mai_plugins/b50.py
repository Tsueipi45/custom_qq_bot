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

            username = user_data.get("nickname")

            if not username:
                raise ValueError("绑定信息不完整")

            return username
    except Exception as e:
        _log.warning(f"[b50] 加载失败：{e}")
        return None


async def b50(client, message, space=None, sender=None):
    if not sender:
        return "[ERROR] 未提供 sender ID，无法上传"
    _log.info(f"[b50] 收到 {sender} 的请求")

    start_time = time.perf_counter()  # 开始计时

    df_username = load_user_credentials(sender)

    if not df_username:
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content="❌ 请先完成 /昵称 \"水鱼用户名\""
        )
        return

    _log.info(f"[b50] 绑定信息加载成功")

    try:
        # 拉取成绩
        id = PlayerIdentifier(username=df_username)
        scores = await maimai.scores(id, provider=divingfish)
        
        score = scores.scores_b35 + scores.scores_b15

        elapsed = time.perf_counter() - start_time  # 计算耗时

        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content=f"成绩已成功查询！共查询到 {len(scores.scores)} 条记录\n 耗时：{elapsed:.2f} 秒"
        )

        _log.info(f"[b50] {sender} 成功下载了 {len(scores.scores)} 条成绩，用时 {elapsed:.2f} 秒")

    except Exception as e:
        _log.warning(f"[b50] 下载失败：{e}")
        elapsed = time.perf_counter() - start_time  # 出错也记录耗时
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content=f"❌ 成绩下载失败，请稍后再试\n错误信息：{e}\n耗时：{elapsed:.2f} 秒"
        )