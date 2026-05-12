import json
import os
from botpy import logging
import time

from maimai_py import PlayerIdentifier, ArcadeProvider, DivingFishProvider
from .maimai_client import maimai

_log = logging.get_logger()

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

async def search_songs(client, message, content, sender=None):
    ctx = content.strip()
    _log.info(f"[search_songs] 收到 {sender} 对于 {ctx} 的歌曲查询需求")

    songs = await maimai.songs(provider=divingfish, curve_provider=divingfish)

    try:
        # Try to interpret ctx as an integer song ID
        song_id = int(ctx)
        song = await songs.by_id(song_id)
    except ValueError:
        # If not an integer, try searching by alias and title using ctx
        try:
            song = await songs.by_alias(ctx)
        except Exception:
            try:
                song = await songs.by_title(ctx)
            except Exception:
                return f"[search_songs] 未找到相关歌曲: {ctx}"
    except Exception as e:
        _log.error(f"[search_songs] 查询歌曲时发生错误: {e}")
        return "[search_songs] 查询过程中发生错误"

    if not song:
        return f"[search_songs] 未找到相关歌曲: {ctx}"
    
    await makesongchart(song)


async def makesongchart(song):
    try:
        chart = await song.chart()
        if not chart:
            return "[makesongchart] 未找到相关谱面"

        # Format the song chart information
        chart_info = f"🎵 歌曲: {song.title}\n" \
                     f"🎤 艺术家: {song.artist}\n" \
                     f"📊 谱面: {chart.difficulty} - {chart.level}\n" \
                     f"🔗 链接: {chart.url}"

        return chart_info
    except Exception as e:
        _log.error(f"[makesongchart] 生成谱面信息时发生错误: {e}")
        return "[makesongchart] 生成谱面信息时发生错误"
