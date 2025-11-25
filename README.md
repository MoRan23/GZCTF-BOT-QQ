# GZCTF-BOT-QQ 

## 介绍

GZCTF对接的qq机器人，基于NapCat+Nonebot框架  
3血播报，赛题新提示播报，新赛题上线播报，新公告播报，自动封禁作弊者及播报等等...  
注: 赛事不要使用相同的比赛名以及相同的赛题名，机器人没有考虑这个情况，可能会有各种问题  
所有功能只在已开放的赛事运作，未开放的赛事无法运作  
目前已经全量完成功能！  
有想要的功能或者有bug可以提issues，提供详细错误日志  

## 适配须知

`v2.3`版本适配  
GZCTF版本`v1.3.2`  
Build at: 2025-05-05T09:52:15+08:00

## 开发计划

| 功能                   | 状态   |
| ---------------------- | ------ |
| 3血播报                | 已完成 |
| 赛题新提示播报         | 已完成 |
| 新赛题上线播报         | 已完成 |
| 新公告播报             | 已完成 |
| 自动封禁作弊者及播报   | 已完成 |
| 用户自助解锁队伍       | 已完成 |
| 排行榜查询             | 已完成 |
| 队伍当前排名及分数查询 | 已完成 |
| 题目当前解出信息查询   | 已完成 |
| 用户查询所有开放赛题   | 已完成 |
| 查询队伍               | 已完成 |
| 管理员查看所有赛题     | 已完成 |
| 管理员ban队伍          | 已完成 |
| 管理员重置用户密码     | 已完成 |
| 管理员开放/关闭赛题    | 已完成 |
| 管理员添加赛题提示     | 已完成 |
| 管理员添加赛事公告     | 已完成 |
| 分群分赛事播报         | 已完成 |

## 使用方法

环境: Ubuntu 22.04

### docker compose安装机器人

```yaml
version: "3.7"
services:
  napcat:
    image: mlikiowa/napcat-docker:latest
    restart: always
    ports:
      - "6099:6099"
    environment:
      - "ACCOUNT=your_account"  #机器人的qq号
      - "WEBUI_TOKEN=your_token"  #webui登录token
      - "WEBUI_PREFIX=/webui"  #webui访问前缀
    volumes:
      - "./napcat/config:/app/napcat/config"
    depends_on:
      - bot

  bot:
    image: registry.cn-hangzhou.aliyuncs.com/moran233/nn:GZBOT
    restart: always
    environment:
      - "SEND_LIST=123456,1234567"  #监听qq群号
      - "GAME_LIST=\"123\",\"1234\""  #监听赛事名
      - "GZCTF_URL=http://xx.xx.xx.xx/"  #GZCTF网址
      - "GZ_USER=your_admin"  #GZCTF管理员用户名
      - "GZ_PASS=your_password"  #GZCTF管理员密码
      - "SUPER=\"123123123\",\"234234234\""  #机器人管理员qq号
```

将上述内容保存为`docker-compose.yml`文件  

```bash
docker compose up -d
```

随后访问`http://[此处替换为本机IP]:6099/webui`  
输入设置的token进入后台  

![](https://raw.githubusercontent.com/MoRan23/moran/main/image-20250528160323449.png)

选择扫码登录账号

![image-20250528160421160](https://raw.githubusercontent.com/MoRan23/moran/main/image-20250528160421160.png)

进入后台后选择网络配置

![image-20250528160518889](https://raw.githubusercontent.com/MoRan23/moran/main/image-20250528160518889.png)

点击新建

![](https://raw.githubusercontent.com/MoRan23/moran/main/image-20250528160537187.png)

选择`Websocket`客户端

![image-20250528160602078](https://raw.githubusercontent.com/MoRan23/moran/main/image-20250528160602078.png)

设置如图`ws://bot:8988/onebot/v11/ws/`

![image-20250528160659240](https://raw.githubusercontent.com/MoRan23/moran/main/image-20250528160659240.png)

保存后即可

#### 更新

```bash
docker compose down
docker compose pull
docker compose up -d
```

随后再次执行登录操作

#### 附：配置机器人

配置文件在`gzctf-bot/plugins/gzctf_bot_qq/config.py`中  

```python
CONFIG: dict = {
        "SEND_LIST": [],
        "GAME_LIST": [],
        "GZCTF_URL": "",
        "GZ_USER": "",
        "GZ_PASS": "",
    }
```

`SEND_LIST`存放监听/发送消息的群号  
示例:

```python
SEND_LIST = [123456789, 987654321]
```

`GAME_LIST`存放需要监听的比赛名称，为空则监控所有比赛  
示例:

```python
GAME_LIST = ["GZCTF2022","GZCTF2023"]
```

`GZCTF_URL`存放GZCTF的网站URL  
示例:

```python
GZCTF_URL = "http://gzctf.cn"
```

`GZ_USER`和`GZ_PASS`存放GZCTF的管理员账号密码  
示例:

```python
GZ_USER = "admin"
GZ_PASS = "Test123."
```

机器人管理员权限配置文件为`.env`文件

```
//.env
HOST=0.0.0.0
PORT=8988
COMMAND_START=["/"]
COMMAND_SEP=["."]
ONEBOT_ACCESS_TOKEN=XXX
SUPERUSERS='[""]'
```

管理员qq号填入`SUPERUSERS`中  
示例:

```
SUPERUSERS='["123456789","987654321"]'
```

## 赞助鸣谢

### DKDUN

<img src="https://raw.githubusercontent.com/MoRan23/moran/main/QQ%E5%9B%BE%E7%89%8720240630210148.png" alt="DKDUN 图标" width="150" height="150">
官网：https://www.dkdun.cn/  

ctf专区群: 727077055  
<img src="https://raw.githubusercontent.com/MoRan23/moran/main/20240630210630.png" alt="DKDUN-CTF QQ群" width="150" height="150">  
公众号：DK盾

dkdun 推出 ctfer 赞助计划  
为各位热爱 ctf 的师傅提供优惠服务器  
详情查看：https://mp.weixin.qq.com/s/38xWMM1Z0sO6znfg9TIklw

更多服务器优惠请入群查看！