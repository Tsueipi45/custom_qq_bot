import json
from openai import OpenAI
from botpy import logging

_log = logging.get_logger()

# 读取 settings.json 取得 Qwen API Key
with open("settings.json", "r", encoding="utf-8") as f:
    config = json.load(f)

client = OpenAI(
    api_key=config["qwen_apikey"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

async def handle_chat(client_instance, message):
    user_input = message.content.strip()
    _log.info(f"[chat_handler] 收到訊息：{user_input}")

    try:
        completion = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {'role': 'system', 'content': '你是一个QQ群助手,旨在简洁但又不失幽默的方式回答问题'},
                {'role': 'user', 'content': user_input}
            ]
        )
        content = completion.choices[0].message.content
        if content:
            reply = content.strip()
        else:
            reply = "❌ 回應內容為空。"
    except Exception as e:
        _log.error(f"[chat_handler] 調用API出錯：{e}")
        reply = "❌ 發生錯誤，請稍後再試。"

    await message._api.post_group_message(
        group_openid=message.group_openid,
        msg_type=0,
        msg_id=message.id,
        content=reply
    )

    _log.info(f"[chat_handler] 已回應：{reply}")
