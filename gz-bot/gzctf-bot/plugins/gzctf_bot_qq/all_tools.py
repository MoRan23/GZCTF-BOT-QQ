import requests
import json
import pytz
import re
from datetime import datetime
from nonebot import get_plugin_config
from .config import Config

CONFIG = get_plugin_config(Config).CONFIG
HEADERS = {"Content-Type": "application/json"}
GZCTF_URL = CONFIG["GZCTF_URL"].rstrip('/')
SESSION = requests.Session()
LOGINDATA = "{" + f'"userName": "{CONFIG["GZ_USER"]}", "password": "{CONFIG["GZ_PASS"]}"' + "}"
UTC_TIMEZONE = pytz.timezone('UTC')
UTC_PLUS_8_TIMEZONE = pytz.timezone('Asia/Shanghai')


def parseArgs(s):
    """
        解析参数
    """
    results = []
    depth = 0
    start = 0
    in_brackets = False

    for i, char in enumerate(s):
        if char == '[':
            if depth == 0:
                start = i + 1
                in_brackets = True
            depth += 1
        elif char == ']':
            depth -= 1
            if depth == 0 and in_brackets:
                results.append(s[start:i])
                in_brackets = False

    return results


def parseNameOrId(s):
    """
        解析队伍名或队伍ID
    """
    id_pattern = r'^id=([^\s&]+)'
    name_pattern = r'^name=([^\s&]+)'

    id_match = re.search(id_pattern, s)
    name_match = re.search(name_pattern, s)

    if id_match:
        id_value = id_match.group(1)
    else:
        id_value = None

    if name_match:
        name_value = name_match.group(1)
    else:
        name_value = None

    return id_value, name_value


def getGameList(name: str = None):
    """
        获取比赛列表
    """
    global HEADERS, SESSION, GZCTF_URL
    API_GAME_LIST_URL = GZCTF_URL + "/api/game"
    if not checkCookieExpired():
        getLogin()
    try:
        game_list = SESSION.get(url=API_GAME_LIST_URL, headers=HEADERS)
    except Exception as e:
        game_list = []
    if name:
        Temp_List = []
        game_list = json.loads(game_list.text)
        for game in game_list:
            if game["title"] == name:
                Temp_List.append(game)
        return Temp_List
    return game_list.json()


def getGameInfo(game_id: int):
    """
        获取比赛信息
    """
    global HEADERS, SESSION, GZCTF_URL
    API_GAME_INFO_URL = GZCTF_URL + f"/api/game/{str(game_id)}"
    if not checkCookieExpired():
        getLogin()
    try:
        game_info = SESSION.get(url=API_GAME_INFO_URL, headers=HEADERS)
    except Exception as e:
        print(e)
        game_info = {}
    return game_info.json()


def getLogin():
    """
        登录
    """
    global LOGINDATA, HEADERS, SESSION, GZCTF_URL
    API_LOGIN_URL = GZCTF_URL + "/api/account/login"
    login = SESSION.post(url=API_LOGIN_URL, data=LOGINDATA, headers=HEADERS)


def checkCookieExpired():
    """
        判断会话的cookie有没有到期
    """
    global SESSION
    for cookie in SESSION.cookies:
        if cookie is not None and cookie.name == "GZCTF_Token":
            headers = {
                "Cookie": f"{cookie.name}={cookie.value}"
            }
            API_CHECK_COOKIE_URL = GZCTF_URL + "/api/admin/config"
            try:
                check = SESSION.get(url=API_CHECK_COOKIE_URL, headers=headers)
            except Exception as e:
                print(e)
                return False
            if check.status_code == 200:
                return True
    return False


def checkConfig(config: dict):
    """
        检测CONFIG
    """
    return True if config.get("SEND_LIST") else False


def parseTime(strTime):
    """
        解析通过 gzctf 平台获取的时间串
    """
    global UTC_TIMEZONE, UTC_PLUS_8_TIMEZONE
    date = datetime.fromisoformat(strTime[:19])
    parsed_date_utc = UTC_TIMEZONE.localize(date)
    date = parsed_date_utc.astimezone(UTC_PLUS_8_TIMEZONE)
    year = date.year
    month = ('0' + str(date.month)) if date.month < 10 else str(date.month)
    day = ('0' + str(date.day)) if date.day < 10 else str(date.day)
    hour = ('0' + str(date.hour)) if date.hour < 10 else str(date.hour)
    minute = ('0' + str(date.minute)) if date.minute < 10 else str(date.minute)
    second = ('0' + str(date.second)) if date.second < 10 else str(date.second)
    nowTime = (year, month, day, hour, minute, second)
    return nowTime


def getGameNotice(game_id: int):
    """
        获取比赛通知
    """
    global HEADERS, SESSION, GZCTF_URL
    API_GAME_NOTICE_URL = GZCTF_URL + f"/api/game/{str(game_id)}/notices"
    if not checkCookieExpired():
        getLogin()
    try:
        game_notice = SESSION.get(url=API_GAME_NOTICE_URL, headers=HEADERS)
    except Exception as e:
        print(e)
        game_notice = []
    return game_notice.json()


def getCheatInfo(game_id: int):
    """
        获取作弊信息
    """
    global HEADERS, SESSION, GZCTF_URL
    API_CHEAT_URL = GZCTF_URL + f"/api/game/{str(game_id)}/CheatInfo"
    if not checkCookieExpired():
        getLogin()
    try:
        cheat_info = SESSION.get(url=API_CHEAT_URL, headers=HEADERS)
    except Exception as e:
        print(e)
        cheat_info = {}
    return cheat_info.json()


def getChallenges(game_id: int):
    """
        获取题目列表
    """
    global HEADERS, SESSION, GZCTF_URL
    API_CHALLENGES_URL = GZCTF_URL + f"/api/edit/games/{str(game_id)}/challenges"
    if not checkCookieExpired():
        getLogin()
    try:
        challenges = SESSION.get(url=API_CHALLENGES_URL, headers=HEADERS)
    except Exception as e:
        print(e)
        challenges = []
    allChallenges = challenges.json()
    allChallenges.sort(key=lambda x: (x["tag"], x["isEnabled"]))
    return allChallenges


def getChallengesInfo(game_id: int, challenge_id: int):
    """
        获取题目信息
    """
    global HEADERS, SESSION, GZCTF_URL
    API_CHALLENGES_INFO_URL = GZCTF_URL + f"/api/game/{str(game_id)}/challenges/{str(challenge_id)}"
    if not checkCookieExpired():
        getLogin()
    try:
        challenges_info = SESSION.get(url=API_CHALLENGES_INFO_URL, headers=HEADERS)
        print(challenges_info.text)
    except Exception as e:
        print(e)
        challenges_info = {}
    return challenges_info.json()


def openOrCloseChallenge(game_id: int, challenge_id: int, isEnable: bool):
    """
        开放/关闭题目
    """
    global HEADERS, SESSION, GZCTF_URL
    if not checkCookieExpired():
        getLogin()
    API_OPEN_CHALLENGE_URL = GZCTF_URL + f"/api/edit/games/{str(game_id)}/challenges/{str(challenge_id)}"
    if isEnable:
        data = "{\"isEnabled\":true}"
    else:
        data = "{\"isEnabled\":false}"
    try:
        oc = SESSION.put(url=API_OPEN_CHALLENGE_URL, headers=HEADERS, data=data)
        if oc.status_code == 200:
            return True
    except Exception as e:
        print(e)
    return False


def banTeam(teamIds: list):
    """
        封禁队伍
    """
    global HEADERS, SESSION, GZCTF_URL
    if not checkCookieExpired():
        getLogin()
    for team_id in teamIds:
        API_BAN_TEAM_URL = GZCTF_URL + f"/api/admin/participation/{str(team_id)}/Suspended"
        try:
            a = SESSION.put(url=API_BAN_TEAM_URL)
            if a.status_code != 200:
                return False
        except Exception as e:
            print(e)
    return True


def unlockTeam(teamId: int):
    """
        解锁队伍
    """
    global HEADERS, SESSION, GZCTF_URL
    if not checkCookieExpired():
        getLogin()
    API_UNLOCK_TEAM_URL = GZCTF_URL + f"/api/admin/teams/{str(teamId)}"
    data = {"locked": False}
    try:
        unlock = SESSION.put(url=API_UNLOCK_TEAM_URL, headers=HEADERS, json=data)
        if unlock.status_code == 200:
            return True
    except Exception as e:
        print(e)
    return False


def getTeamInfoWithName(teamName: str):
    """
        通过队伍名获取队伍ID
    """
    global HEADERS, SESSION, GZCTF_URL
    if not checkCookieExpired():
        getLogin()
    API_TEAM_URL = GZCTF_URL + f"/api/admin/teams/search?hint={teamName}"
    allTeams = []
    try:
        teams = SESSION.post(url=API_TEAM_URL, headers=HEADERS)
    except Exception as e:
        print(e)
        teams = {}
    for team in teams.json()['data']:
        if team['name'] == teamName:
            allTeams.append(team)
    return allTeams


def getTeamInfoWithId(teamId: str):
    """
        通过队伍Id获取队伍Info
    """
    global HEADERS, SESSION, GZCTF_URL
    if not checkCookieExpired():
        getLogin()
    API_TEAM_URL = GZCTF_URL + f"/api/admin/teams/search?hint={teamId}"
    allTeams = []
    try:
        teams = SESSION.post(url=API_TEAM_URL, headers=HEADERS)
    except Exception as e:
        print(e)
        teams = {}
    for team in teams.json()['data']:
        if team['id'] == int(teamId):
            allTeams.append(team)
    return allTeams


def getTeamInfoWithGameId(game_Id: int):
    """
        通过gameID获取队伍信息
    """
    global HEADERS, SESSION, GZCTF_URL
    if not checkCookieExpired():
        getLogin()
    API_TEAM_URL = GZCTF_URL + f"/api/game/{str(game_Id)}/participations"
    try:
        team = SESSION.get(url=API_TEAM_URL, headers=HEADERS)
    except Exception as e:
        print(e)
        team = []
    return team.json()


def getScoreBoard(game_id: int):
    """
        获取排行榜
    """
    global HEADERS, SESSION, GZCTF_URL
    API_RANK_URL = GZCTF_URL + f"/api/game/{str(game_id)}/scoreboard"
    if not checkCookieExpired():
        getLogin()
    try:
        rank = SESSION.get(url=API_RANK_URL, headers=HEADERS)
    except Exception as e:
        print(e)
        rank = {}
    return rank.json()


def getRank(game_id: int):
    """
        获取总排行榜
    """
    if 'items' not in getScoreBoard(game_id):
        return getScoreBoard(game_id)
    rank = getScoreBoard(game_id)['items']
    allRank = []
    if not rank:
        return None
    for item in rank:
        Rank = {'teamName': item['name'], 'score': item['score'], 'rank': item['rank']}
        allRank.append(Rank)
    allRank.sort(key=lambda x: x["rank"])
    return allRank


def getRankWithOrg(game_id: int, org: str):
    """
        获取组织排行榜
    """
    rank = getScoreBoard(game_id)['items']
    allOrgRank = []
    for item in rank:
        if item.get('organization') is None:
            return None
        if item['organization'] == org:
            orgRank = {'teamName': item['name'], 'score': item['score'], 'rank': item['organizationRank']}
            allOrgRank.append(orgRank)
    allOrgRank.sort(key=lambda x: x["rank"])
    return allOrgRank


def getRankWithTeamId(game_id: int, team_id: int):
    """
        获取队伍排名
    """
    rank = getScoreBoard(game_id)['items']
    for item in rank:
        if item['id'] == team_id:
            teamRank = {'teamName': item['name'], 'score': item['score'], 'rank': item['rank']}
            if item.get('organizationRank') is not None:
                teamRank['organizationRank'] = item['organizationRank']
            return teamRank
    return None


def getChallengesInfoByName(game_id: int, challenge_name: str):
    """
        通过题目NAME获取题目信息
    """
    global HEADERS, SESSION, GZCTF_URL
    API_CHALLENGES_INFO_URL = GZCTF_URL + f"/api/game/{str(game_id)}/details"
    challenges = getChallenges(game_id)
    if not checkCookieExpired():
        getLogin()
    try:
        challenges_info = SESSION.get(url=API_CHALLENGES_INFO_URL, headers=HEADERS)
    except Exception as e:
        print(e)
        challenges_info = {}
    Info = {}
    for challenge in challenges:
        if challenge['title'] == challenge_name:
            Info['title'] = challenge_name
            Info['tag'] = challenge['tag']
            Info['isEnabled'] = challenge['isEnabled']
            Info['score'] = challenge['score']
            findChallenges = challenges_info.json()['challenges'][f"{Info['tag']}"]
            for findChallenge in findChallenges:
                if findChallenge['title'] == challenge_name:
                    Info['solved'] = findChallenge['solved']
                    Info['bloods'] = findChallenge['bloods']
                    return Info
    return None


def getUserWithName(userName: str):
    """
        通过用户名获取用户信息
    """
    global HEADERS, SESSION, GZCTF_URL
    if not checkCookieExpired():
        getLogin()
    API_USER_URL = GZCTF_URL + f"/api/admin/Users/Search?hint={userName}"
    try:
        user = SESSION.post(url=API_USER_URL, headers=HEADERS)
    except Exception as e:
        print(e)
        user = {}
    for item in user.json()['data']:
        if item['userName'] == userName:
            return item
    return False


def resetPwd(userName: str):
    """
        重置密码
    """
    global HEADERS, SESSION, GZCTF_URL
    if not checkCookieExpired():
        getLogin()
    if getUserWithName(userName):
        userId = getUserWithName(userName)['id']
    else:
        return False
    API_RESET_PWD_URL = GZCTF_URL + f"/api/admin/Users/{userId}/Password"
    try:
        reset = SESSION.delete(url=API_RESET_PWD_URL, headers=HEADERS)
        if reset.status_code == 200:
            return reset.text.strip('"')
    except Exception as e:
        print(e)
    return False


def addNotice(gameId: int, notice: str):
    """
        添加公告
    """
    global HEADERS, SESSION, GZCTF_URL
    if not checkCookieExpired():
        getLogin()
    API_ADD_NOTICE_URL = GZCTF_URL + f"/api/edit/games/{str(gameId)}/notices"
    data = {"content": notice}
    try:
        add = SESSION.post(url=API_ADD_NOTICE_URL, json=data)
        if add.status_code == 200:
            return True
    except Exception as e:
        print(e)
    return False


def addHint(gameId: int, challengeId: int, hint: str):
    """
        添加提示
    """
    global HEADERS, SESSION, GZCTF_URL
    if not checkCookieExpired():
        getLogin()
    API_ADD_HINT_URL = GZCTF_URL + f"/api/edit/games/{str(gameId)}/challenges/{str(challengeId)}"
    data = SESSION.get(url=API_ADD_HINT_URL, headers=HEADERS)
    if data.status_code != 200:
        return False
    datas = data.json()
    datas['hints'].append(hint)
    try:
        add = SESSION.put(url=API_ADD_HINT_URL, headers=HEADERS, json=datas)
        if add.status_code == 200:
            return True
    except Exception as e:
        print(e)
    return False
