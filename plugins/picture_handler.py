from plugins.picture_api import get_random_picture_path, encode_image_base64
from botpy import logging

import os

_log = logging.get_logger()

PICTURE_FOLDER = "./pictures"

async def handle_picture(client, message, group_name=None, is_group=True, msg_seq=1):
    user_input = message.content.strip()
    _log.info(f"[picture_handler] 收到訊息：{user_input}")

    if not group_name:
        group = "mygo"
        _log.info("[picture_handler] 未指定, 设定为mygo")
    else:
        group = group_name
        _log.info(f"[picture_handler] 设定为{group}")

    image_path = get_random_picture_path(group)

    if not image_path:
        await send_text_message(client, message, "❌ 找不到图片文件", is_group, msg_seq)
        return

    file_data = encode_image_base64(image_path)
    if not file_data:
        await send_text_message(client, message, "❌ 图片编码失败", is_group, msg_seq)
        return

    try:
        _log.info(f"[picture_handler] 发送随机图片：{os.path.basename(image_path)}")


        if is_group:
            upload_result = await message._api.post_group_base64file(
                group_openid=message.group_openid,
                file_type=1,
                file_data=file_data
            )

            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=7,
                msg_id=message.id,
                msg_seq=msg_seq,
                media=upload_result
            )
        else:
            upload_result = await message._api.post_c2c_base64file(
                openid=message.author.user_openid,
                file_type=1,
                file_data=file_data
            )

            await message._api.post_c2c_message(
                openid=message.author.user_openid,
                msg_type=7,
                msg_id=message.id,
                msg_seq=msg_seq,
                media=upload_result
            )

        _log.info("[picture_handler] ✅ 图片发送成功")

    except Exception as e:
        _log.error(f"[picture_handler] ❌ 图片发送失败: {e}")
        await send_text_message(client, message, "发送图片失败", is_group, msg_seq + 1)
        
async def send_text_message(client, message, content, is_group, msg_seq):
    try:
        if is_group:
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                msg_seq=msg_seq,
                content=content
            )
        else:
            await message._api.post_c2c_message(
                openid=message.author.user_openid,
                msg_type=0,
                msg_id=message.id,
                msg_seq=msg_seq,
                content=content
            )
    except Exception as e:
        _log.error(f"[picture_handler] 发送文本消息失败: {e}")
