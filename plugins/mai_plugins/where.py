import json
from botpy import logging
import time

_log = logging.get_logger()

USERDATA_PATH = "userdata.json"
REGIONS_UNSUPPORTED_MESSAGE = (
    "⚠️ 当前安装的 maimai-py 版本没有可用的游玩地区数据源，暂时无法查询游玩地区。"
)

def load_user_credentials(sender_id: str):
    try:
        with open(USERDATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            user_data = data.get(sender_id)
            if not user_data:
                raise ValueError("未找到用户绑定数据")

            arcade_credentials = user_data.get("arcade_credentials")

            if not arcade_credentials:
                raise ValueError("绑定信息不完整")

            return arcade_credentials
    except Exception as e:
        _log.warning(f"[b50] 加载失败：{e}")
        return None


async def where_mai(client, message, space=None, sender=None):
    if not sender:
        return "[ERROR] 未提供 sender ID，无法查询"
    _log.info(f"[region] 收到 {sender} 的地区查询请求")

    start_time = time.perf_counter()  # 开始计时

    arcade_credentials = load_user_credentials(sender)

    if not arcade_credentials:
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content="❌ 请先完成 /绑 \"qrcode解析内容\""
        )
        return

    _log.info("[region] 绑定信息加载成功")

    elapsed = time.perf_counter() - start_time
    await message._api.post_group_message(
        group_openid=message.group_openid,
        msg_type=0,
        msg_id=message.id,
        content=f"{REGIONS_UNSUPPORTED_MESSAGE}\n\n⏱️ 查询耗时：{elapsed:.2f} 秒"
    )
