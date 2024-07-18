from nonebot.adapters.cqhttp import Event
from nonebot import get_plugin_config

from .config import Config

SEND_LIST: dict = get_plugin_config(Config).CONFIG.get("SEND_LIST")


async def checkIfGroup(event: Event):
    return event.message_type == "group"


async def checkIfPrivate(event: Event):
    return event.message_type == "private"


async def checkIfListen(event: Event):
    global SEND_LIST
    if not SEND_LIST:
        return False
    for id in SEND_LIST:
        if id == event.group_id:
            return True
    return False


async def checkIfListenOrPrivate(event: Event):
    if await checkIfPrivate(event) or await checkIfListen(event):
        return True
    return False
