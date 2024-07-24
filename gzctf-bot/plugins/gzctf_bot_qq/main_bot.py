from nonebot import on_command, get_bot
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
        if not GAME_LIST:
            print(f"赛事 {gameName} 不存在!")
            exit()
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
/unlock [队名] <队伍ID>: 解锁队伍
/rank <比赛名(默认为监听的比赛)> <组织名(默认为空)>:
获取比赛总排行榜、组织排行榜前20名
/trank [队伍名] <比赛名(默认为监听的比赛)> <队伍ID>:
获取队伍排名
************管理功能**************
/open: 开启播报
/close: 关闭播报
/openb: 开启自动封禁
/closeb: 关闭自动封禁
***********************************
参数需使用 [ ] 包裹起来！
队伍 ID 为队伍邀请码中两个 : 之间的数字
以上示例 [ ] 包裹为必要参数，不可省略
< > 包裹为非必要参数，可省略，自动填充默认值
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
open = on_command("open", rule=checkIfListenOrPrivate, permission=SUPERUSER)
close = on_command("close", rule=checkIfListenOrPrivate, permission=SUPERUSER)
openb = on_command("openb", rule=checkIfListenOrPrivate, permission=SUPERUSER)
closeb = on_command("closeb", rule=checkIfListenOrPrivate, permission=SUPERUSER)


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


@rank.handle()
async def rank_handle(bot, event, args: Message = CommandArg()):
    global GAME_LIST
    arg = args.extract_plain_text().strip()
    args = parseArgs(arg)
    if len(args) == 0:
        if CONFIG.get("GAME_LIST"):
            for gameName in CONFIG.get("GAME_LIST"):
                GAME_LIST = getGameList(name=gameName)
        else:
            GAME_LIST = getGameList()
        for gameInfo in GAME_LIST:
            gameRank = getRank(gameInfo['id'])
            if gameRank:
                rankMsg = f"==={gameInfo['title']}(总)===\n"
                for rank in gameRank:
                    rankMsg += f"{str(rank['rank'])}. {rank['teamName']} || {str(rank['score'])}\n"
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
                    await bot.send(event, f"赛事 {gameInfo['title']} 暂无排行榜")
                except Exception as e:
                    print(e)
                    await bot.send(event, "Error")
    elif len(args) == 1:
        gamelist = getGameList(name=args[0])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 {args[0]} 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        gameInfo = gamelist[0]
        gameRank = getRank(gameInfo['id'])
        if gameRank:
            rankMsg = f"==={gameInfo['title']}(总)===\n"
            for rank in gameRank:
                rankMsg += f"{str(rank['rank'])}. {rank['teamName']} || {str(rank['score'])}\n"
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
                await bot.send(event, f"赛事 {gameInfo['title']} 暂无排行榜")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
    elif len(args) == 2:
        gamelist = getGameList(name=args[0])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 {args[0]} 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        gameInfo = gamelist[0]
        gameRank = getRankWithOrg(gameInfo['id'], args[1])
        if gameRank:
            rankMsg = f"==={gameInfo['title']}({args[1]})===\n"
            for rank in gameRank:
                rankMsg += f"{str(rank['rank'])}. {rank['teamName']} || {str(rank['score'])}\n"
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
                await bot.send(event, f"组织名错误或赛事 {gameInfo['title']} 暂无排行榜")
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
        if CONFIG.get("GAME_LIST"):
            for gameName in CONFIG.get("GAME_LIST"):
                GAME_LIST = getGameList(name=gameName)
        else:
            GAME_LIST = getGameList()
        teamInfo = getTeamInfoWithName(args[0])
        if not teamInfo:
            try:
                await bot.send(event, f"队伍 {args[0]} 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        elif len(teamInfo) > 1:
            try:
                await bot.send(event, f"队伍 {args[0]} 不唯一，请添加队伍 ID 参数获取精准数据")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        for info in teamInfo:
            for gameInfo in GAME_LIST:
                teamRank = getRankWithTeamId(gameInfo['id'], info['id'])
                if teamRank:
                    rankMsg = f"=={gameInfo['title']}==\n"
                    rankMsg += f"队名: {args[0]}\n"
                    if len(teamInfo) > 1:
                        rankMsg += f"队伍ID: {info['id']}\n"
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
                        await bot.send(event, f"赛事 {gameInfo['title']} 暂无队伍 {args[0]} : {info['id']} 排名")
                    except Exception as e:
                        print(e)
                        await bot.send(event, "Error")
    elif len(args) == 2:
        gamelist = getGameList(name=args[1])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 {args[1]} 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        teamInfo = getTeamInfoWithName(args[0])
        if not teamInfo:
            try:
                await bot.send(event, f"队伍 {args[0]} 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        elif len(teamInfo) > 1:
            try:
                await bot.send(event, f"队伍 {args[0]} 不唯一，请添加队伍 ID 参数获取精准数据")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
        gameInfo = gamelist[0]
        for info in teamInfo:
            teamRank = getRankWithTeamId(gameInfo['id'], info['id'])
            if teamRank:
                rankMsg = f"=={gameInfo['title']}==\n"
                rankMsg += f"队名: {args[0]}\n"
                if len(teamInfo) > 1:
                    rankMsg += f"队伍ID: {info['id']}\n"
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
                    await bot.send(event, f"赛事 {gameInfo['title']} 暂无队伍 {args[0]} : {info['id']} 排名")
                except Exception as e:
                    print(e)
                    await bot.send(event, "Error")
    elif len(args) == 3:
        gamelist = getGameList(name=args[1])
        if not gamelist:
            try:
                await bot.send(event, f"赛事 {args[1]} 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        teamInfo = getTeamInfoWithName(args[0])
        if not teamInfo:
            try:
                await bot.send(event, f"队伍 {args[0]} 不存在")
            except Exception as e:
                print(e)
                await bot.send(event, "Error")
            return
        gameInfo = gamelist[0]
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
                await bot.send(event, f"赛事 {gameInfo['title']} 暂无队伍 {args[0]} : {args[2]} 排名")
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
                await bot.send(event, f"队伍 {args[0]} 不唯一，请添加队伍 ID 参数")
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
