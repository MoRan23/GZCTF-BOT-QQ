from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from . import main_bot
from .config import Config
# from .all_tools import getLogin, checkConfig

__plugin_meta__ = PluginMetadata(
    name="GZCTF-BOT-QQ",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

CONFIG = config.CONFIG

# if CONFIG.get("GZ_USER") != "" and CONFIG.get("GZ_PASS") != "":
#     getLogin()
#
# if not checkConfig(config=CONFIG):
#     print("Config Must Set All Items in [\"SEND_LIST\",\"LISTEN_LIST\"]")
#     exit()
