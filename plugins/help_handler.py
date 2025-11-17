from botpy import logging

_log = logging.get_logger()

async def handle_help(client, message, space=None):

    user_input = message.content.strip()
    _log.info(f"[handle_help] 收到訊息：{user_input}")

    result = (
    "🎯 可用指令一览（群聊中@机器人后接指令使用）：\n\n"
    "📌 常用功能：\n"
    "👉 /天气 —— 获取当前天气状况\n"
    "👉 /图片 —— 随机获取一张图片\n"
    "👉 /help 或 /帮助 —— 显示本帮助菜单\n\n"
    "📊 成绩功能：\n"
    "👉 /绑 + 二维码解析内容 —— 绑定查分器账号（Arcade）\n"
    "👉 /水鱼 + token —— 绑定水鱼查分器 token（DivingFish）\n"
    "👉 /水鱼名 + username —— 绑定水鱼查分器用户名\n"
    "👉 /导 —— 上传已绑定账号的成绩至查分器\n"
    "👉 /b50 —— 查询你的 B50 分数列表(还在做)\n\n"
    "👉 /在哪mai —— 查询舞萌dx足迹\n"
    "🔮 其他趣味功能：\n"
    "👉 /今日运势 —— 获取你的今日运势签文\n\n"
    "📎 小提示：\n"
    "部分指令如 /绑、/水鱼 后面需要跟具体内容，例：`/绑 SGW...`\n"
    "绑定一次后即可使用 /导 上传成绩。"
)

    await message._api.post_group_message(
        group_openid=message.group_openid,
        msg_type=0,
        msg_id=message.id,
        content=result
    )