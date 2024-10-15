from nonebot import on_command, get_bot
from nonebot.permission import SUPERUSER
from nonebot import require
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageSegment
from datetime import datetime, timedelta, timezone
from .rule import *
from .all_tools import *
from .config import Config

CONFIG = get_plugin_config(Config).CONFIG
GAME_LIST = []
if CONFIG.get("GAME_LIST"):
    for gameName in CONFIG.get("GAME_LIST"):
        TEMP_LIST = getGameList(name=gameName)
        if not TEMP_LIST:
            print(f"赛事 [{gameName}] 不存在!")
            exit()
        GAME_LIST.append(TEMP_LIST[0])
else:
    GAME_LIST = getGameList()
H = require("nonebot_plugin_apscheduler").scheduler
STATUS = False
BAN_STATUS = False
GAMENOTICE = {}
GAMECHEATS = {}
for gameInfo in GAME_LIST:
    GAMENOTICE[f"gameId_{str(gameInfo['id'])}"] = getGameNotice(gameInfo['id'])
UTC8 = timezone(timedelta(hours=8))
GZCTF_URL = CONFIG["GZCTF_URL"].rstrip('/')
LISTEN_GROUP = CONFIG["SEND_LIST"]
SEND_GAME_LIST = {}
for gameInfo in GAME_LIST:
    SEND_GAME_LIST[gameInfo['title']] = []

helpMsg = """=======================
************公共功能**************
/help: 获取帮助
/game: 获取比赛列表
/unlock [队名] <队伍ID>: 解锁队伍
/rank <比赛名(默认为监听的比赛)> <组织名(默认为空)>:
获取比赛总排行榜、组织排行榜前20名
/trank [队伍名] <比赛名(默认为监听的比赛)> <队伍ID>:
获取队伍排名
/q <比赛名(默认为监听的比赛)> <赛题名(默认为空)>:
获取赛题信息(无参数获取赛题列表)
/team [队伍名]: 获取队伍信息
************管理功能**************
/open <赛事名>: 开启播报
/close <赛事名>: 关闭播报
(以上开关播报功能，在监听群聊使用则开关该群聊的播报，私聊使用则开关所有监听群聊播报。赛事名不填默认所有赛事)
/openb: 开启自动封禁
/closeb: 关闭自动封禁
/qa <比赛名(默认为监听的比赛)>: 查看所有赛题
/ban [name=队伍名/id=队伍ID] <比赛名>: 
封禁队伍(比赛名为空将会在所有开放赛事封禁)
/resetpwd [用户名]: 重置用户密码
/openq [比赛名] [赛题]: 开放赛题
/closeq [比赛名] [赛题]: 关闭赛题
/addnotice [比赛名] [公告]: 添加公告
/addhint [比赛名] [赛题] [提示]: 添加提示
***********************************
参数需使用 [ ] 包裹起来！
队伍 ID 为队伍邀请码中两个 : 之间的数字
以上示例 [ ] 包裹为必要参数，不可省略
< > 包裹为非必要参数，可省略，自动填充默认值
如有特殊表明需要添加如 name= 或 id= 的参数
所有功能均可群聊和私聊使用，私聊需加好友
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
恭喜队伍 [{team}] 拿下赛题 [{challenge}]
======================="""
msgTemp_all = """======{type}======
比赛: {gameName}
时间: {time}
内容: 
{content}
======================="""
msgTemp_hint = """======{type}======
比赛: {gameName}
时间: {time}
赛题: {challenge}
提示: 
{hint}
======================="""
msgTemp_new = """======{type}======
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
unlock = on_command("unlock", rule=checkIfListenOrPrivate)
rank = on_command("rank", rule=checkIfListenOrPrivate)
trank = on_command("trank", rule=checkIfListenOrPrivate)
q = on_command("q", rule=checkIfListenOrPrivate)
team = on_command("team", rule=checkIfListenOrPrivate)
open = on_command("open", rule=checkIfListenOrPrivate, permission=SUPERUSER)
close = on_command("close", rule=checkIfListenOrPrivate, permission=SUPERUSER)
openb = on_command("openb", rule=checkIfListenOrPrivate, permission=SUPERUSER)
closeb = on_command("closeb", rule=checkIfListenOrPrivate, permission=SUPERUSER)
qa = on_command("qa", rule=checkIfListenOrPrivate, permission=SUPERUSER)
ban = on_command("ban", rule=checkIfListenOrPrivate, permission=SUPERUSER)
resetpwd = on_command("resetpwd", rule=checkIfListenOrPrivate, permission=SUPERUSER)
openq = on_command("openq", rule=checkIfListenOrPrivate, permission=SUPERUSER)
closeq = on_command("closeq", rule=checkIfListenOrPrivate, permission=SUPERUSER)
addnotice = on_command("addnotice", rule=checkIfListenOrPrivate, permission=SUPERUSER)
addhint = on_command("addhint", rule=checkIfListenOrPrivate, permission=SUPERUSER)


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
            current_time = datetime.now(UTC8)
            gameAllInfo = getGameInfo(gameInfo['id'])
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
            gameListMsg += f"比赛名称: {gameInfo['title']}\n开始时间: {start_Time}\n结束时间: {end_Time}\n比赛状态: {status}\n"
            if gameAllInfo['organizations']:
                gameListMsg += "参赛组织:"
                for org in gameAllInfo['organizations']:
                    gameListMsg += f" {org},"
                gameListMsg = gameListMsg.rstrip(',')
                gameListMsg += "\n"
            gameListMsg += f"比赛链接: {CONFIG['GZCTF_URL'].rstrip('/')}/games/{gameInfo['id']}\n************************************\n"
        gameListMsg += "======================="
        await bot.send(event, gameListMsg)
    except Exception as e:
        print(e)
        await bot.send(event, "Error")


@open.handle()
async def open_handle(bot, event, args: Message = CommandArg()):
    global STATUS, SEND_GAME_LIST, LISTEN_GROUP
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)

    try:
        if len(args) == 1:
            if STATUS:
                if await checkIfGroup(event):
                    if args[0] in SEND_GAME_LIST:
                        if event.group_id in SEND_GAME_LIST[args[0]]:
                            await bot.send(event, f"群 [{str(event.group_id)}] 对赛事 [{args[0]}] 播报本来就开着")
                            return
                        else:
                            SEND_GAME_LIST[args[0]].append(event.group_id)
                            await bot.send(event, f"群 [{str(event.group_id)}] 对赛事 [{args[0]}] 已开启播报")
                            return
                    else:
                        await bot.send(event, "未找到比赛")
                        return
                else:
                    if args[0] in SEND_GAME_LIST:
                        if SEND_GAME_LIST[args[0]] == LISTEN_GROUP:
                            await bot.send(event, f"所有群对赛事 [{args[0]}] 播报本来就开着")
                            return
                        else:
                            SEND_GAME_LIST[args[0]] = LISTEN_GROUP
                            await bot.send(event, f"已开启群 {str(LISTEN_GROUP)} 对赛事 [{args[0]}] 播报")
                            return
                    else:
                        await bot.send(event, "未找到比赛")
                        return
            else:
                STATUS = True
                if await checkIfGroup(event):
                    SEND_GAME_LIST[args[0]].append(event.group_id)
                    await bot.send(event, f"群 [{str(event.group_id)}] 对赛事 [{args[0]}] 已开启播报")
                    return
                else:
                    SEND_GAME_LIST[args[0]] = LISTEN_GROUP
                    await bot.send(event, f"已开启群 {str(LISTEN_GROUP)} 对赛事 [{args[0]}] 播报")
                    return
        else:
            if STATUS:
                if await checkIfGroup(event):
                    count = 0
                    for g in GAME_LIST:
                        if event.group_id in SEND_GAME_LIST[g['title']]:
                            count += 1
                    if count == len(GAME_LIST):
                        await bot.send(event, f"群 [{str(event.group_id)}] 对所有赛事播报本来就开着")
                        return
                    else:
                        for g in GAME_LIST:
                            if event.group_id not in SEND_GAME_LIST[g['title']]:
                                SEND_GAME_LIST[g['title']].append(event.group_id)
                        await bot.send(event, f"群 [{str(event.group_id)}] 对所有赛事已开启播报")
                        return
                else:
                    for g in GAME_LIST:
                        if SEND_GAME_LIST[g['title']] == LISTEN_GROUP:
                            continue
                        else:
                            SEND_GAME_LIST[g['title']] = LISTEN_GROUP
                    await bot.send(event, f"已开启群 {str(LISTEN_GROUP)} 对所有赛事播报")
                    return
            else:
                STATUS = True
                if await checkIfGroup(event):
                    for g in GAME_LIST:
                        if event.group_id in SEND_GAME_LIST[g['title']]:
                            continue
                        else:
                            SEND_GAME_LIST[g['title']].append(event.group_id)
                    await bot.send(event, f"群 [{str(event.group_id)}] 对所有赛事已开启播报")
                    return
                else:
                    for g in GAME_LIST:
                        SEND_GAME_LIST[g['title']] = LISTEN_GROUP
                    await bot.send(event, f"已开启群 {str(LISTEN_GROUP)} 对所有赛事播报")
                    return
    except Exception as e:
        print(e)
        await bot.send(event, "Error")


@close.handle()
async def close_handle(bot, event, args: Message = CommandArg()):
    global STATUS, SEND_GAME_LIST, LISTEN_GROUP
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)

    try:
        if len(args) == 1:
            if not STATUS:
                await bot.send(event, "群播报本来就关着")
                return
            else:
                if await checkIfGroup(event):
                    if args[0] in SEND_GAME_LIST:
                        if event.group_id in SEND_GAME_LIST[args[0]]:
                            SEND_GAME_LIST[args[0]].remove(event.group_id)
                            await bot.send(event, f"群 [{str(event.group_id)}] 对赛事 [{args[0]}] 已关闭播报")
                            count = 0
                            for g in GAME_LIST:
                                if not SEND_GAME_LIST[g['title']]:
                                    count += 1
                            if count == len(GAME_LIST):
                                STATUS = False
                            return
                        else:
                            await bot.send(event, f"群 [{str(event.group_id)}] 对赛事 [{args[0]}] 播报本来就关着")
                            return
                    else:
                        await bot.send(event, "未找到比赛")
                        return
                else:
                    if args[0] in SEND_GAME_LIST:
                        SEND_GAME_LIST[args[0]] = []
                        count = 0
                        for g in GAME_LIST:
                            if not SEND_GAME_LIST[g['title']]:
                                count += 1
                        if count == len(GAME_LIST):
                            STATUS = False
                        await bot.send(event, f"已关闭群 {str(LISTEN_GROUP)} 对赛事 [{args[0]}] 播报")
                        return
                    else:
                        await bot.send(event, "未找到比赛")
                        return
        else:
            if not STATUS:
                await bot.send(event, "群播报本来就关着")
                return
            else:
                if await checkIfGroup(event):
                    count = 0
                    for g in GAME_LIST:
                        if event.group_id in SEND_GAME_LIST[g['title']]:
                            SEND_GAME_LIST[g['title']].remove(event.group_id)
                        if not SEND_GAME_LIST[g['title']]:
                            count += 1
                    await bot.send(event, f"群 [{str(event.group_id)}] 对所有赛事已关闭播报")
                    if count == len(GAME_LIST):
                        STATUS = False
                    return
                else:
                    for g in GAME_LIST:
                        SEND_GAME_LIST[g['title']] = []
                    await bot.send(event, f"已关闭群 {str(LISTEN_GROUP)} 对所有赛事播报")
                    STATUS = False
                    return
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


@rank.handle()
async def rank_handle(bot, event, args: Message = CommandArg()):
    global GAME_LIST
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if len(args) == 0:
        if not CONFIG.get("GAME_LIST"):
            GAME_LIST = getGameList()
        rankMsg = "=======================\n"
        for gameInfo in GAME_LIST:
            gameRank = getRank(gameInfo['id'])
            if gameRank:
                rankMsg += f"==={gameInfo['title']}(总)===\n"
                if type(gameRank) is dict:
                    rankMsg += f"赛事 [{gameInfo['title']}] 未开始\n"
                    continue
                for rank in gameRank:
                    rankMsg += f"[{str(rank['rank'])}] | [{rank['teamName']}] - {str(rank['score'])}\n"
                    if rank['rank'] == 20:
                        break
            else:
                rankMsg += f"==={gameInfo['title']}===\n"
                rankMsg += f"赛事 [{gameInfo['title']}] 暂无排行榜\n"
        rankMsg += "======================="
        try:
            await bot.send(event, rankMsg)
        except Exception as e:
            print(e)
            await bot.send(event, "Error")
    elif len(args) == 1:
        gamelist = getGameList(name=args[0])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        gameInfo = gamelist[0]
        gameRank = getRank(gameInfo['id'])
        rankMsg = "=======================\n"
        if gameRank:
            if type(gameRank) is dict:
                rankMsg += f"赛事 [{gameInfo['title']}] 未开始\n"
            else:
                rankMsg += f"==={gameInfo['title']}(总)===\n"
                for rank in gameRank:
                    rankMsg += f"[{str(rank['rank'])}] | [{rank['teamName']}] - {str(rank['score'])}\n"
                    if rank['rank'] == 20:
                        break
            rankMsg += "======================="
            try:
                await bot.send(event, rankMsg)
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        else:
            try:
                await bot.send(event, f"赛事 [{gameInfo['title']}] 暂无排行榜")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
    elif len(args) == 2:
        gamelist = getGameList(name=args[0])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        gameInfo = gamelist[0]
        gameRank = getRankWithOrg(gameInfo['id'], args[1])
        rankMsg = "=======================\n"
        if gameRank:
            if type(gameRank) is dict:
                rankMsg += f"赛事 [{gameInfo['title']}] 未开始\n"
            else:
                rankMsg += f"==={gameInfo['title']}({args[1]})===\n"
                for rank in gameRank:
                    rankMsg += f"[{str(rank['rank'])}] | [{rank['teamName']}] - {str(rank['score'])}\n"
                    if rank['rank'] == 20:
                        break
            rankMsg += "======================="
            try:
                await bot.send(event, rankMsg)
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        else:
            try:
                await bot.send(event, f"组织名错误或赛事 [{gameInfo['title']}] 暂无排行榜")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
    else:
        try:
            await bot.send(event,
                           "参数错误!\n使用方法: /rank <比赛名(默认为监听的比赛)> <组织名(默认为空)> \n或使用 /help 查看帮助")
        except Exception as e:
            print(e)
            await bot.send(event, "Error")


@trank.handle()
async def trank_handle(bot, event, args: Message = CommandArg()):
    global GAME_LIST
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if len(args) == 1:
        if not CONFIG.get("GAME_LIST"):
            GAME_LIST = getGameList()
        teamInfo = getTeamInfoWithName(args[0])
        if not teamInfo:
            try:
                await bot.send(event, f"队伍 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        elif len(teamInfo) > 1:
            try:
                await bot.send(event, f"队伍 [{args[0]}] 不唯一，请添加队伍 ID 参数获取精准数据")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        rankMsg = "=======================\n"
        for gameInfo in GAME_LIST:
            gameTimeStart = parseTime(gameInfo['start'])
            current_time = datetime.now(UTC8)
            start_Time = datetime.strptime(
                f"{gameTimeStart[0]}-{gameTimeStart[1]}-{gameTimeStart[2]} {gameTimeStart[3]}:{gameTimeStart[4]}",
                '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
            if current_time.strftime('%Y-%m-%d %H:%M') < start_Time:
                rankMsg += f"赛事 [{gameInfo['title']}] 未开始\n"
                continue
            for info in teamInfo:
                teamRank = getRankWithTeamId(gameInfo['id'], info['id'])
                if teamRank:
                    rankMsg += f"=={gameInfo['title']}==\n"
                    rankMsg += f"队名: {args[0]}\n"
                    if len(teamInfo) > 1:
                        rankMsg += f"队伍ID: {info['id']}\n"
                    rankMsg += f"总分: {str(teamRank['score'])}\n"
                    rankMsg += f"排名: {str(teamRank['rank'])}\n"
                    if teamRank.get('organizationRank'):
                        rankMsg += f"组织排名: {str(teamRank['organizationRank'])}\n"
                else:
                    rankMsg += f"=={gameInfo['title']}==\n"
                    rankMsg += f"赛事 [{gameInfo['title']}] 暂无队伍 [{args[0]}] : [{info['id']}] 排名\n"
        rankMsg += "======================="
        try:
            await bot.send(event, rankMsg)
        except Exception as e:
            print(e)
            await bot.send(event, "Error")
    elif len(args) == 2:
        gamelist = getGameList(name=args[1])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 [{args[1]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        teamInfo = getTeamInfoWithName(args[0])
        if not teamInfo:
            try:
                await bot.send(event, f"队伍 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        elif len(teamInfo) > 1:
            try:
                await bot.send(event, f"队伍 [{args[0]}] 不唯一，请添加队伍 ID 参数获取精准数据")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        gameInfo = gamelist[0]
        gameTimeStart = parseTime(gameInfo['start'])
        current_time = datetime.now(UTC8)
        start_Time = datetime.strptime(
            f"{gameTimeStart[0]}-{gameTimeStart[1]}-{gameTimeStart[2]} {gameTimeStart[3]}:{gameTimeStart[4]}",
            '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        if current_time.strftime('%Y-%m-%d %H:%M') < start_Time:
            try:
                await bot.send(event, f"赛事 [{args[1]}] 未开始")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        rankMsg = ""
        for info in teamInfo:
            teamRank = getRankWithTeamId(gameInfo['id'], info['id'])
            if teamRank:
                rankMsg += f"=={gameInfo['title']}==\n"
                rankMsg += f"队名: {args[0]}\n"
                if len(teamInfo) > 1:
                    rankMsg += f"队伍ID: {info['id']}\n"
                rankMsg += f"总分: {str(teamRank['score'])}\n"
                rankMsg += f"排名: {str(teamRank['rank'])}\n"
                if teamRank.get('organizationRank'):
                    rankMsg += f"组织排名: {str(teamRank['organizationRank'])}\n"
            else:
                rankMsg += f"=={gameInfo['title']}==\n"
                rankMsg += f"赛事 [{gameInfo['title']}] 暂无队伍 [{args[0]}] : [{info['id']}] 排名\n"
        rankMsg += "======================="
        try:
            await bot.send(event, rankMsg)
        except Exception as e:
            print(e)
            await bot.send(event, "Error")

    elif len(args) == 3:
        gamelist = getGameList(name=args[1])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 [{args[1]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        teamInfo = getTeamInfoWithName(args[0])
        if not teamInfo:
            try:
                await bot.send(event, f"队伍 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        gameInfo = gamelist[0]
        gameTimeStart = parseTime(gameInfo['start'])
        current_time = datetime.now(UTC8)
        start_Time = datetime.strptime(
            f"{gameTimeStart[0]}-{gameTimeStart[1]}-{gameTimeStart[2]} {gameTimeStart[3]}:{gameTimeStart[4]}",
            '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        if current_time.strftime('%Y-%m-%d %H:%M') < start_Time:
            try:
                await bot.send(event, f"赛事 [{args[1]}] 未开始")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        teamRank = getRankWithTeamId(gameInfo['id'], int(args[2]))
        if teamRank:
            rankMsg = f"=={gameInfo['title']}==\n"
            rankMsg += f"队名: {args[0]}\n"
            rankMsg += f"总分: {str(teamRank['score'])}\n"
            rankMsg += f"排名: {str(teamRank['rank'])}\n"
            if teamRank.get('organizationRank'):
                rankMsg += f"组织排名: {str(teamRank['organizationRank'])}\n"
            rankMsg += "======================="
            try:
                await bot.send(event, rankMsg)
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        else:
            try:
                await bot.send(event, f"赛事 [{gameInfo['title']}] 暂无队伍 [{args[0]}] : [{args[2]}] 排名")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        return
    else:
        try:
            await bot.send(event,
                           "参数错误!\n使用方法: /trank [队伍名] <比赛名(默认为监听的比赛)> <队伍ID> \n或使用 /help 查看帮助")
        except Exception as e:
            print(e)
            await bot.send(event, "Error")


@unlock.handle()
async def unlock_handle(bot, event, args: Message = CommandArg()):
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if len(args) == 1:
        teamInfo = getTeamInfoWithName(args[0])
        if len(teamInfo) > 1:
            try:
                emsg = f"=======================\n队伍 [{args[0]}] 不唯一，请添加队伍 ID 参数:\n"
                for team in teamInfo:
                    emsg += f"队伍ID: {team['id']}\n队长: {team['members'][0]['userName']}\n"
                    emsg += "-----------------------\n"
                emsg += "======================="
                await bot.send(event, emsg)
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        elif not teamInfo:
            try:
                await bot.send(event, f"队伍 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        teamId = teamInfo[0]['id']
        res = unlockTeam(teamId)
        try:
            if res:
                await bot.send(event, "解锁成功")
                return
            else:
                await bot.send(event, "解锁失败，请检查队名是否正确")
        except Exception as e:
            print(e)
            await bot.send(event, "Error")
    elif len(args) == 2:
        teamInfo = getTeamInfoWithName(args[0])
        if not teamInfo:
            try:
                await bot.send(event, f"队伍 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        check = False
        for info in teamInfo:
            if info['id'] == int(args[1]):
                check = True
                break
        if check:
            res = unlockTeam(int(args[1]))
            try:
                if res:
                    await bot.send(event, "解锁成功")
                    return
                else:
                    await bot.send(event, "解锁失败，请检查队名与队伍 ID 是否正确")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        else:
            try:
                await bot.send(event, f"解锁失败，请检查队名与队伍 ID 是否正确且对应")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
    else:
        await bot.send(event, "参数错误!\n使用方法: /unlock [队名] <队伍ID>\n或使用 /help 查看帮助")
        return


@ban.handle()
async def ban_handle(bot, event, args: Message = CommandArg()):
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    global GAME_LIST
    if not CONFIG.get("GAME_LIST"):
        GAME_LIST = getGameList()
    teamIds = []
    if len(args) == 1:
        teamId, teamName = parseNameOrId(args[0])
        if teamId:
            teams = getTeamInfoWithId(teamId)
            if not teams:
                try:
                    await bot.send(event, f"队伍ID [{teamId}] 不存在")
                except Exception as e:
                    print(e)
                    await bot.send(event, "Error")
                return
            for team in teams:
                if team['id'] == int(teamId):
                    for gameInfo in GAME_LIST:
                        allTeams = getTeamInfoWithGameId(gameInfo['id'])
                        for t in allTeams:
                            if t['team']['id'] == int(teamId):
                                teamIds.append(t['id'])
                                break
                    break
                else:
                    continue
            res = banTeam(teamIds)
            try:
                if res:
                    await bot.send(event, "封禁成功")
                    return
                else:
                    await bot.send(event, "封禁失败，请检查队伍 ID 是否正确")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        elif teamName:
            teamInfo = getTeamInfoWithName(teamName)
            if len(teamInfo) > 1:
                try:
                    emsg = f"=======================\n队伍 [{teamName}] 不唯一，请使用队伍 ID:\n"
                    for team in teamInfo:
                        emsg += f"队伍ID: {team['id']}\n队长: {team['members'][0]['userName']}\n"
                        emsg += "-----------------------\n"
                    emsg += "======================="
                    await bot.send(event, emsg)
                except Exception as e:
                    print(e)
                    await bot.send(event, "Error")
                return
            elif not teamInfo:
                try:
                    await bot.send(event, f"队伍 [{teamName}] 不存在")
                except Exception as e:
                    print(e)
                    await bot.send(event, "Error")
                return
            for gameInfo in GAME_LIST:
                allTeams = getTeamInfoWithGameId(gameInfo['id'])
                for team in allTeams:
                    if team['team']['name'] == teamName:
                        teamIds.append(team['id'])
                        break
            res = banTeam(teamIds)
            try:
                if res:
                    await bot.send(event, "封禁成功")
                    return
                else:
                    await bot.send(event, "封禁失败，请检查队名是否正确")
                    return
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        else:
            await bot.send(event, "参数错误!\n使用方法: /ban [name=队伍名/id=队伍ID] <比赛名>\n或使用 /help 查看帮助")
            return
    elif len(args) == 2:
        gamelist = getGameList(name=args[1])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 [{args[1]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        teamId, teamName = parseNameOrId(args[0])
        if teamId:
            teams = getTeamInfoWithId(teamId)
            if not teams:
                try:
                    await bot.send(event, f"队伍ID [{teamId}] 不存在")
                except Exception as e:
                    print(e)
                    await bot.send(event, "Error")
                return
            for team in teams:
                if team['id'] == int(teamId):
                    for gameInfo in gamelist:
                        allTeams = getTeamInfoWithGameId(gameInfo['id'])
                        for t in allTeams:
                            if t['team']['id'] == int(teamId):
                                teamIds.append(t['id'])
                                break
                    break
                else:
                    continue
            res = banTeam(teamIds)
            try:
                if res:
                    await bot.send(event, "封禁成功")
                    return
                else:
                    await bot.send(event, "封禁失败，请检查队伍 ID 是否正确")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        elif teamName:
            teamInfo = getTeamInfoWithName(teamName)
            if len(teamInfo) > 1:
                try:
                    await bot.send(event, f"队伍 [{teamName}] 不唯一，请使用队伍 ID")
                except Exception as e:
                    print(e)
                    await bot.send(event, "Error")
                return
            elif not teamInfo:
                try:
                    await bot.send(event, f"队伍 [{teamName}] 不存在")
                except Exception as e:
                    print(e)
                    await bot.send(event, "Error")
                return
            for gameInfo in gamelist:
                allTeams = getTeamInfoWithGameId(gameInfo['id'])
                for team in allTeams:
                    if team['team']['name'] == teamName:
                        teamIds.append(team['id'])
                        break
            res = banTeam(teamIds)
            try:
                if res:
                    await bot.send(event, "封禁成功")
                    return
                else:
                    await bot.send(event, "封禁失败，请检查队名是否正确")
                    return
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        else:
            await bot.send(event, "参数错误!\n使用方法: /ban [name=队伍名/id=队伍ID] <比赛名>\n或使用 /help 查看帮助")
            return
    else:
        await bot.send(event, "参数错误!\n使用方法: /ban [name=队伍名/id=队伍ID] <比赛名>\n或使用 /help 查看帮助")
        return


@q.handle()
async def q_handle(bot, event, args: Message = CommandArg()):
    global GAME_LIST
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if len(args) == 0:
        if not CONFIG.get("GAME_LIST"):
            GAME_LIST = getGameList()
        qMsg = "=======================\n"
        for gameInfo in GAME_LIST:
            gameTimeStart = parseTime(gameInfo['start'])
            current_time = datetime.now(UTC8)
            start_Time = datetime.strptime(
                f"{gameTimeStart[0]}-{gameTimeStart[1]}-{gameTimeStart[2]} {gameTimeStart[3]}:{gameTimeStart[4]}",
                '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
            if current_time.strftime('%Y-%m-%d %H:%M') < start_Time:
                qMsg += f"赛事 [{gameInfo['title']}] 未开始\n"
                continue
            challenges = getChallenges(gameInfo['id'])
            if challenges:
                isEnabled = False
                qMsg += f"==={gameInfo['title']}===\n"
                for challenge in challenges:
                    if challenge['isEnabled']:
                        qMsg += f"[{challenge['tag']}] | [{challenge['title']}]\n"
                        isEnabled = True
                if not isEnabled:
                    qMsg += "赛事暂无已开放赛题\n"
                qMsg += "=======================\n"
            else:
                qMsg += f"赛事 [{gameInfo['title']}] 暂无赛题"
        qMsg += "======================="
        try:
            await bot.send(event, qMsg)
        except Exception as e:
            print(e)
            await bot.send(event, "Error")
    elif len(args) == 1:
        gamelist = getGameList(name=args[0])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        gameInfo = gamelist[0]
        gameTimeStart = parseTime(gameInfo['start'])
        current_time = datetime.now(UTC8)
        start_Time = datetime.strptime(
            f"{gameTimeStart[0]}-{gameTimeStart[1]}-{gameTimeStart[2]} {gameTimeStart[3]}:{gameTimeStart[4]}",
            '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        if current_time.strftime('%Y-%m-%d %H:%M') < start_Time:
            try:
                await bot.send(event, f"赛事 [{args[0]}] 未开始")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        challenges = getChallenges(gameInfo['id'])
        isEnabled = False
        if challenges:
            qMsg = f"==={gameInfo['title']}===\n"
            for challenge in challenges:
                if challenge['isEnabled']:
                    qMsg += f"[{challenge['tag']}] | [{challenge['title']}]\n"
                    isEnabled = True
            if not isEnabled:
                qMsg += "赛事暂无已开放赛题\n"
            qMsg += "======================="
            try:
                await bot.send(event, qMsg)
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        else:
            try:
                await bot.send(event, f"赛事 [{gameInfo['title']}] 暂无赛题")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
    elif len(args) == 2:
        gamelist = getGameList(name=args[0])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        gameInfo = gamelist[0]
        gameTimeStart = parseTime(gameInfo['start'])
        current_time = datetime.now(UTC8)
        start_Time = datetime.strptime(
            f"{gameTimeStart[0]}-{gameTimeStart[1]}-{gameTimeStart[2]} {gameTimeStart[3]}:{gameTimeStart[4]}",
            '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        if current_time.strftime('%Y-%m-%d %H:%M') < start_Time:
            try:
                await bot.send(event, f"赛事 [{args[0]}] 未开始")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        challenge = getChallengesInfoByName(gameInfo['id'], args[1])
        if challenge:
            qMsg = f"==={gameInfo['title']}===\n"
            qMsg += f"{challenge['tag']} | {challenge['title']}\n"
            qMsg += f"分值: {str(challenge['score'])}\n"
            qMsg += f"提交数: {str(challenge['solved'])}\n"
            i = 1
            for blood in challenge['bloods']:
                qMsg += f"[{str(i)}] | [{blood['name']}]\n"
                i += 1
            qMsg += "======================="
            try:
                await bot.send(event, qMsg)
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        else:
            try:
                await bot.send(event, f"赛事 [{gameInfo['title']}] 中无赛题 [{args[1]}]")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
    else:
        try:
            await bot.send(event,
                           "参数错误!\n使用方法: /q <比赛名(默认为监听的比赛)> <赛题名>\n或使用 /help 查看帮助")
        except Exception as e:
            print(e)
            await bot.send(event, "Error")


@qa.handle()
async def qa_handle(bot, event, args: Message = CommandArg()):
    global GAME_LIST
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if len(args) == 0:
        if not CONFIG.get("GAME_LIST"):
            GAME_LIST = getGameList()
        qMsg = "=======================\n"
        for gameInfo in GAME_LIST:
            challenges = getChallenges(gameInfo['id'])
            if challenges:
                qMsg += f"==={gameInfo['title']}===\n"
                for challenge in challenges:
                    if challenge['isEnabled']:
                        qMsg += f"[{challenge['tag']}] | [已开放] | [{challenge['title']}]\n"
                    else:
                        qMsg += f"[{challenge['tag']}] | [未开放] | [{challenge['title']}]\n"
                qMsg += "=======================\n"
            else:
                qMsg += f"赛事 [{gameInfo['title']}] 暂无赛题"
        qMsg += "======================="
        try:
            await bot.send(event, qMsg)
        except Exception as e:
            print(e)
            await bot.send(event, "Error")
    elif len(args) == 1:
        gamelist = getGameList(name=args[0])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        gameInfo = gamelist[0]
        challenges = getChallenges(gameInfo['id'])
        if challenges:
            qMsg = f"==={gameInfo['title']}===\n"
            for challenge in challenges:
                if challenge['isEnabled']:
                    qMsg += f"[{challenge['tag']}] | [已开放] | [{challenge['title']}]\n"
                else:
                    qMsg += f"[{challenge['tag']}] | [未开放] | [{challenge['title']}]\n"
            qMsg += "======================="
            try:
                await bot.send(event, qMsg)
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
    else:
        try:
            await bot.send(event,
                           "参数错误!\n使用方法: /qa <比赛名(默认为监听的比赛)>\n或使用 /help 查看帮助")
        except Exception as e:
            print(e)
            await bot.send(event, "Error")


@resetpwd.handle()
async def resetpwd_handle(bot, event, args: Message = CommandArg()):
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if len(args) == 1:
        res = resetPwd(args[0])
        if res:
            try:
                await bot.send(event, f"重置成功!\n新密码: \n{res}")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        else:
            try:
                await bot.send(event, "重置失败，请检查用户名是否正确")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        return
    else:
        await bot.send(event, "参数错误!\n使用方法: /resetpwd [用户名]\n或使用 /help 查看帮助")
        return


@openq.handle()
async def openq_handle(bot, event, args: Message = CommandArg()):
    global GAME_LIST
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if not CONFIG.get("GAME_LIST"):
        GAME_LIST = getGameList()
    if len(args) == 2:
        gameId = 0
        for gameInfo in GAME_LIST:
            if gameInfo['title'] == args[0]:
                gameId = gameInfo['id']
                break
        if gameId == 0:
            try:
                await bot.send(event, f"赛事 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        challenges = getChallenges(gameId)
        for challenge in challenges:
            if challenge['title'] == args[1]:
                res = openOrCloseChallenge(gameId, challenge['id'], True)
                if res:
                    try:
                        await bot.send(event, f"开放赛事 [{args[0]}] 赛题 [{args[1]}] 成功!")
                    except Exception as e:
                        print(e)
                        await bot.send(event, "Error")
                else:
                    try:
                        await bot.send(event, "开放失败，请检查赛事名或赛题名是否正确, 以及赛题是否在赛事中")
                    except Exception as e:
                        print(e)
                        await bot.send(event, "Error")
                return
        try:
            await bot.send(event, f"赛事 [{args[0]}] 中无赛题 [{args[1]}]")
        except Exception as e:
            print(e)
            await bot.send(event, "Error")
        return
    else:
        await bot.send(event, "参数错误!\n使用方法: /openq [比赛名] [赛题名]\n或使用 /help 查看帮助")
        return


@closeq.handle()
async def closeq_handle(bot, event, args: Message = CommandArg()):
    global GAME_LIST
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if not CONFIG.get("GAME_LIST"):
        GAME_LIST = getGameList()
    if len(args) == 2:
        gameId = 0
        for gameInfo in GAME_LIST:
            if gameInfo['title'] == args[0]:
                gameId = gameInfo['id']
                break
        if gameId == 0:
            try:
                await bot.send(event, f"赛事 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        challenges = getChallenges(gameId)
        for challenge in challenges:
            if challenge['title'] == args[1]:
                res = openOrCloseChallenge(gameId, challenge['id'], False)
                if res:
                    try:
                        await bot.send(event, f"关闭赛事 [{args[0]}] 赛题 [{args[1]}] 成功!")
                    except Exception as e:
                        print(e)
                        await bot.send(event, "Error")
                else:
                    try:
                        await bot.send(event, "关闭失败，请检查赛事名或赛题名是否正确, 以及赛题是否在赛事中")
                    except Exception as e:
                        print(e)
                        await bot.send(event, "Error")
                return
        try:
            await bot.send(event, f"赛事 [{args[0]}] 中无赛题 [{args[1]}]")
        except Exception as e:
            print(e)
            await bot.send(event, "Error")
        return
    else:
        await bot.send(event, "参数错误!\n使用方法: /closeq [比赛名] [赛题名]\n或使用 /help 查看帮助")
        return

@addnotice.handle()
async def addnotice_handle(bot, event, args: Message = CommandArg()):
    global GAME_LIST
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if not CONFIG.get("GAME_LIST"):
        GAME_LIST = getGameList()
    if len(args) == 2:
        gameId = 0
        for gameInfo in GAME_LIST:
            if gameInfo['title'] == args[0]:
                gameId = gameInfo['id']
                break
        if gameId == 0:
            try:
                await bot.send(event, f"赛事 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        res = addNotice(gameId, args[1])
        if res:
            try:
                await bot.send(event, f"添加赛事 [{args[0]}] 公告成功!")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        else:
            try:
                await bot.send(event, "添加失败，请检查赛事名是否正确")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        return
    else:
        await bot.send(event, "参数错误!\n使用方法: /addnotice [比赛名] [公告内容]\n或使用 /help 查看帮助")
        return

@addhint.handle()
async def addhint_handle(bot, event, args: Message = CommandArg()):
    global GAME_LIST
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if not CONFIG.get("GAME_LIST"):
        GAME_LIST = getGameList()
    if len(args) == 3:
        gameId = 0
        for gameInfo in GAME_LIST:
            if gameInfo['title'] == args[0]:
                gameId = gameInfo['id']
                break
        if gameId == 0:
            try:
                await bot.send(event, f"赛事 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        challenges = getChallenges(gameId)
        for challenge in challenges:
            if challenge['title'] == args[1]:
                res = addHint(gameId, challenge['id'], args[2])
                if res:
                    try:
                        await bot.send(event, f"添加赛事 [{args[0]}] 赛题 [{args[1]}] 提示成功!")
                    except Exception as e:
                        print(e)
                        await bot.send(event, "Error")
                else:
                    try:
                        await bot.send(event, "添加失败，请检查赛事名或赛题名是否正确, 以及赛题是否在赛事中")
                    except Exception as e:
                        print(e)
                        await bot.send(event, "Error")
                return
        try:
            await bot.send(event, f"赛事 [{args[0]}] 中无赛题 [{args[1]}]")
        except Exception as e:
            print(e)
            await bot.send(event, "Error")
        return
    else:
        await bot.send(event, "参数错误!\n使用方法: /addhint [比赛名] [赛题名] [提示内容]\n或使用 /help 查看帮助")
        return


@team.handle()
async def team_handle(bot, event, args: Message = CommandArg()):
    global GZCTF_URL
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if len(args) == 1:
        teamInfo = getTeamInfoWithName(args[0])
        if not teamInfo:
            try:
                await bot.send(event, f"队伍 [{args[0]}] 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        teamMsg = "=======================\n"
        for info in teamInfo:
            teamMsg += f"==={info['name']}===\n"
            if info['avatar']:
                teamMsg += MessageSegment.image(GZCTF_URL+info['avatar'])
            teamMsg += f"签名: {info['bio']}\n"
            teamMsg += "-----------------------\n"
            for member in info['members']:
                if member['avatar']:
                    teamMsg += MessageSegment.image(GZCTF_URL+member['avatar'])
                if member['captain']:
                    teamMsg += f"队长: {member['userName']}\n"
                else:
                    teamMsg += f"成员: {member['userName']}\n"
                teamMsg += f"签名: {member['bio']}\n"
                teamMsg += "-----------------------\n"
            teamMsg += f"=======================\n"
        try:
            await bot.send(event, teamMsg)
        except Exception as e:
            print(e)
            await bot.send(event, "Error")
    else:
        await bot.send(event, "参数错误!\n使用方法: /team [队伍名]\n或使用 /help 查看帮助")
        return

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
                    GAMENOTICE[f"gameId_{str(gameInfo['id'])}"] = getGameNotice(gameInfo['id'])
        for gameInfo in GAME_LIST:
            tmpGameNotice = getGameNotice(gameInfo['id'])
            if tmpGameNotice != GAMENOTICE[f"gameId_{str(gameInfo['id'])}"]:
                tmpNotice = []
                for notice in tmpGameNotice:
                    if notice not in GAMENOTICE[f"gameId_{str(gameInfo['id'])}"]:
                        tmpNotice.append(notice)
                GAMENOTICE[f"gameId_{str(gameInfo['id'])}"] = tmpGameNotice
                tmpNotice.sort(key=lambda x: x['id'])
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
                        for id in SEND_GAME_LIST[gameInfo['title']]:
                            try:
                                await bot.send_group_msg(group_id=id, message=msg)
                            except Exception as e:
                                print(e)
                                await bot.send_group_msg(group_id=id, message="Error")
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
                        for id in SEND_GAME_LIST[gameInfo['title']]:
                            try:
                                await bot.send_group_msg(group_id=id, message=msg)
                            except Exception as e:
                                print(e)
                                await bot.send_group_msg(group_id=id, message="Error")
