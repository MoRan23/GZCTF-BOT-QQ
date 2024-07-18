from nonebot import on_command, get_bot
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from nonebot import require
from nonebot.adapters import Message
from nonebot.params import CommandArg
from .rule import *
from .all_tools import *
from .config import Config

CONFIG = get_plugin_config(Config).CONFIG
GAME_LIST = []
if CONFIG.get("GAME_LIST"):
    for gameName in CONFIG.get("GAME_LIST"):
        GAME_LIST = getGameList(name=gameName)
else:
    GAME_LIST = getGameList()
H = require("nonebot_plugin_apscheduler").scheduler
STATUS = False
BAN_STATUS = False
GAMENOTICE = {}
GAMECHEATS = {}
for gameInfo in GAME_LIST:
    GAMENOTICE[f"gameId_{str(gameInfo['id'])}"] = getGameNotice(gameInfo['id'])


helpMsg = """=======================
************公共功能**************
/help: 获取帮助
/game: 获取比赛列表
************管理功能**************
/open: 开启播报
/close: 关闭播报
/openb: 开启自动封禁
/closeb: 关闭自动封禁
======================="""
msgList = {
    "Normal": "【公告更新】",
    "FirstBlood": "【一血】",
    "SecondBlood": "【二血】",
    "ThirdBlood": "【三血】",
    "NewHint": "【提示更新】",
    "NewChallenge": "【上题目啦】"
}
msgTemp_blood = """========{type}========
比赛: {gameName}
时间: {time}
恭喜队伍 {team} 拿下赛题 {challenge}
======================="""
msgTemp_all = """======{type}======
比赛: {gameName}
时间: {time}
内容: {content}
======================="""
msgTemp_hint = """======{type}======
比赛: {gameName}
时间: {time}
赛题: {challenge}
提示: {hint}
======================="""
msgTemp_new = """====={type}=====
比赛: {gameName}
时间: {time}
类型: {challenge_type}
赛题: {challenge}
======================="""
msgTemp_ban = """========{type}========
比赛: {gameName}
时间: {time}
赛题: {challenge}
提交队伍: {team}
flag所属队伍: {flagOwner}
状态: 已封禁
请各位参赛队伍不要以任何形式作弊！
======================="""

helpCmd = on_command("help", rule=checkIfListenOrPrivate)
game = on_command("game", rule=checkIfListenOrPrivate)
open = on_command("open", rule=checkIfListenOrPrivate, permission=SUPERUSER)
close = on_command("close", rule=checkIfListenOrPrivate, permission=SUPERUSER)
openb = on_command("openb", rule=checkIfListenOrPrivate, permission=SUPERUSER)
closeb = on_command("closeb", rule=checkIfListenOrPrivate, permission=SUPERUSER)
unlock = on_command("unlock", rule=to_me() & checkIfPrivate)
get = on_command("get")


@helpCmd.handle()
async def helpCmd_handle(bot, event):
    try:
        await bot.send(event, helpMsg)
    except Exception as e:
        print(e)
        await bot.send(event, "Error")


@game.handle()
async def game_handle(bot, event):
    global GAME_LIST
    if not CONFIG.get("GAME_LIST"):
        GAME_LIST = getGameList()
    try:
        gameListMsg = """=======================
************比赛列表**************
"""
        for gameInfo in GAME_LIST:
            status = ''
            gameTimeStart = parseTime(gameInfo['start'])
            gameTimeEnd = parseTime(gameInfo['end'])
            current_time = datetime.now()
            start_Time = datetime.strptime(
                f"{gameTimeStart[0]}-{gameTimeStart[1]}-{gameTimeStart[2]} {gameTimeStart[3]}:{gameTimeStart[4]}",
                '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
            end_Time = datetime.strptime(
                f"{gameTimeEnd[0]}-{gameTimeEnd[1]}-{gameTimeEnd[2]} {gameTimeEnd[3]}:{gameTimeEnd[4]}",
                '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
            if current_time.strftime('%Y-%m-%d %H:%M') < start_Time:
                status = '未开始'
            elif end_Time > current_time.strftime('%Y-%m-%d %H:%M') > start_Time:
                status = '进行中'
            else:
                status = '已结束'
            gameListMsg += f"比赛名称: {gameInfo['title']}\n开始时间: {start_Time}\n结束时间: {end_Time}\n比赛状态: {status}\n比赛链接: {CONFIG['GZCTF_URL'].rstrip('/')}/games/{gameInfo['id']}\n************************************\n"
        gameListMsg += "======================="
        await bot.send(event, gameListMsg)
    except Exception as e:
        print(e)
        await bot.send(event, "Error")


@open.handle()
async def open_handle(bot, event):
    global STATUS
    try:
        if STATUS:
            await bot.send(event, "播报本来就开着")
            return
        else:
            STATUS = True
            await bot.send(event, "已开启播报")
    except Exception as e:
        print(e)
        await bot.send(event, "Error")


@close.handle()
async def close_handle(bot, event):
    global STATUS
    try:
        if not STATUS:
            await bot.send(event, "播报本来就关着")
            return
        else:
            STATUS = False
            await bot.send(event, "已关闭播报")
    except Exception as e:
        print(e)
        await bot.send(event, "Error")


@openb.handle()
async def openb_handle(bot, event):
    global BAN_STATUS
    try:
        if BAN_STATUS:
            await bot.send(event, "自动封禁本来就开着")
            return
        else:
            BAN_STATUS = True
            await bot.send(event, "已开启自动封禁")
    except Exception as e:
        print(e)
        await bot.send(event, "Error")


@closeb.handle()
async def closeb_handle(bot, event):
    global BAN_STATUS
    try:
        if not BAN_STATUS:
            await bot.send(event, "自动封禁本来就关着")
            return
        else:
            BAN_STATUS = False
            await bot.send(event, "已关闭自动封禁")
    except Exception as e:
        print(e)
        await bot.send(event, "Error")


@unlock.handle()
async def unlock_handle(bot, event):
    try:
        await bot.send(event, "解锁成功")
    except Exception as e:
        print(e)
        await bot.send(event, "Error")

@get.handle()
async def get_handle(bot, event, args: Message = CommandArg()):
    try:
        a = getGameList()
        args.extract_plain_text()
        await bot.send(event, str(a + args[1].extract_plain_text()))
    except Exception as e:
        print(e)
        await bot.send(event, "Error")


@H.scheduled_job("interval", seconds=20)
async def _():
    global GAME_LIST, STATUS, GAMENOTICE, GAMECHEATS, BAN_STATUS
    bot = get_bot()
    if STATUS:
        if not CONFIG.get("GAME_LIST"):
            tmpGameInfo = getGameList()
            if tmpGameInfo != GAME_LIST:
                GAME_LIST = tmpGameInfo
        for gameInfo in GAME_LIST:
            tmpGameNotice = getGameNotice(gameInfo['id'])
            if tmpGameNotice != GAMENOTICE[f"gameId_{str(gameInfo['id'])}"]:
                tmpNotice = []
                for notice in tmpGameNotice:
                    if notice not in GAMENOTICE[f"gameId_{str(gameInfo['id'])}"]:
                        tmpNotice.append(notice)
                GAMENOTICE[f"gameId_{str(gameInfo['id'])}"] = tmpGameNotice
                tmpNotice.sort()
                for newNotice in tmpNotice:
                    msgTime = parseTime(newNotice['time'])
                    msgType = newNotice['type']
                    msgContent = newNotice['values']
                    challenges = getChallenges(gameInfo['id'])
                    if msgType in msgList.keys():
                        if msgType == "FirstBlood" or msgType == "SecondBlood" or msgType == "ThirdBlood":
                            msg = msgTemp_blood.format(type=msgList[msgType], gameName=gameInfo['title'],
                                                       time=f"{msgTime[0]}-{msgTime[1]}-{msgTime[2]} {msgTime[3]}:{msgTime[4]}:{msgTime[5]}",
                                                       team=msgContent[0], challenge=msgContent[1])
                        elif msgType == "NewHint":
                            challenge_hint = ''
                            for challenge in challenges:
                                if challenge['title'] == msgContent[0]:
                                    challenge_hint = getChallengesInfo(gameInfo['id'], challenge['id'])['hints'][-1]
                                    break
                            msg = msgTemp_hint.format(type=msgList[msgType], gameName=gameInfo['title'],
                                                      time=f"{msgTime[0]}-{msgTime[1]}-{msgTime[2]} {msgTime[3]}:{msgTime[4]}:{msgTime[5]}",
                                                      challenge=msgContent[0], hint=challenge_hint)
                        elif msgType == "NewChallenge":
                            challenge_type = ''
                            for challenge in challenges:
                                if challenge['title'] == msgContent[0]:
                                    challenge_type = challenge['tag']
                                    break
                            msg = msgTemp_new.format(type=msgList[msgType], gameName=gameInfo['title'],
                                                     time=f"{msgTime[0]}-{msgTime[1]}-{msgTime[2]} {msgTime[3]}:{msgTime[4]}:{msgTime[5]}",
                                                     challenge_type=challenge_type, challenge=msgContent[0])
                        else:
                            msg = msgTemp_all.format(type=msgList[msgType], gameName=gameInfo['title'],
                                                     time=f"{msgTime[0]}-{msgTime[1]}-{msgTime[2]} {msgTime[3]}:{msgTime[4]}:{msgTime[5]}",
                                                     content=msgContent[0])
                        for id in CONFIG.get("SEND_LIST"):
                            try:
                                await bot.send_msg(group_id=id, message=msg)
                            except Exception as e:
                                print(e)
                                await bot.send_msg(group_id=id, message="Error")
            GAMECHEATS[f"gameId_{str(gameInfo['id'])}"] = getCheatInfo(gameInfo['id'])
            if BAN_STATUS:
                tmpGameCheats = getCheatInfo(gameInfo['id'])
                if tmpGameCheats != GAMECHEATS[f"gameId_{str(gameInfo['id'])}"]:
                    tmpCheats = []
                    for cheat in tmpGameCheats:
                        if cheat not in GAMECHEATS[f"gameId_{str(gameInfo['id'])}"]:
                            tmpCheats.append(cheat)
                    tmpCheats.sort()
                    for newCheat in tmpCheats:
                        msgTime = parseTime(newCheat['submission']['time'])
                        submitTeam = newCheat['submitTeam']['team']['name']
                        if newCheat['submitTeam']['organization']:
                            submitTeam += f"({newCheat['submitTeam']['organization']})"
                        flagOwner = newCheat['ownedTeam']['team']['name']
                        if newCheat['ownedTeam']['organization']:
                            flagOwner += f"({newCheat['ownedTeam']['organization']})"
                        teamIds = [newCheat['submitTeam']['id'], newCheat['ownedTeam']['id']]
                        msg = msgTemp_ban.format(type="【封禁】", gameName=gameInfo['title'],
                                                 time=f"{msgTime[0]}-{msgTime[1]}-{msgTime[2]} {msgTime[3]}:{msgTime[4]}:{msgTime[5]}",
                                                 challenge=newCheat['submission']['challenge'], team=submitTeam,
                                                 flagOwner=flagOwner)
                        banTeam(teamIds)
                        GAMECHEATS[f"gameId_{str(gameInfo['id'])}"] = getCheatInfo(gameInfo['id'])
                        for id in CONFIG.get("SEND_LIST"):
                            try:
                                await bot.send_msg(group_id=id, message=msg)
                            except Exception as e:
                                print(e)
                                await bot.send_msg(group_id=id, message="Error")
