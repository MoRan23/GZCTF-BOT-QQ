#!/bin/bash

start(){
    sudo apt-get -y update
    sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y --no-install-recommends -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"
    sudo DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install apt-transport-https ca-certificates curl software-properties-common dnsutils debian-keyring debian-archive-keyring git
    curl -fsSL http://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository -y "deb [arch=amd64] http://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get -y update
    sudo DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install docker-ce docker-compose-plugin
    sudo git clone https://cdn.moran233.xyz/https://github.com/MoRan23/GZCTF-BOT-QQ.git
}

change_Source(){
    echo "正在自动换源..."
    if [ -f /etc/os-release ]; then
    . /etc/os-release
    VERSION_ID=$(echo "$VERSION_ID" | tr -d '"')
    major=$(echo "$VERSION_ID" | cut -d '.' -f 1)
    minor=$(echo "$VERSION_ID" | cut -d '.' -f 2)
    if [ "$major" -lt 24 ] || { [ "$major" -eq 24 ] && [ "$minor" -lt 4 ]; }; then
        sudo sed -i 's@//.*archive.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list
        echo "换源成功！"
    else
        sudo sed -i 's@//.*archive.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list.d/ubuntu.sources
        echo "换源成功！"
    fi
    else
        echo "/etc/os-release 文件不存在，无法确定系统版本信息。"
        echo "换源失败，请手动换源！"
    fi
}

# shellcheck disable=SC2162
read -p "输入docker镜像源（默认内置源）: " source_add
if [ -z "$source_add" ]; then
    source_add="https://hub.hk1.dkdun.com/"
fi
echo "使用的镜像源是: $source_add"
wget -O daemon.json https://cdn.moran233.xyz/https://raw.githubusercontent.com/MoRan23/GZCTF-Auto/main/config-auto/docker/daemon.json
sed -i "s|\[\"[^\"]*\"\]|\[\"$source_add\"\]|g" ./daemon.json

# shellcheck disable=SC2162
read -p "输入qq号: " qq
if [ -z "$qq" ]; then
    # shellcheck disable=SC2242
    exit "未输入qq号"
fi

# shellcheck disable=SC2162
read -p "输入需要监听的qq群，多个可以用英文,隔开: " qqg
if [ -z "$qqg" ]; then
    # shellcheck disable=SC2242
    exit "未输入qq群"
fi

read -p "输入管理员qq号, 多个可以用英文,隔开: " admin
if [ -z "$admin" ]; then
    # shellcheck disable=SC2242
    exit "未输入管理员qq号"
fi
IFS=',' read -ra array <<< "$admin"

read -p "输入GZCTF平台地址: " url
if [ -z "$url" ]; then
    # shellcheck disable=SC2242
    exit "未输入GZCTF平台地址"
fi

read -p "输入GZCTF平台管理员用户名: " admin_name
if [ -z "$admin_name" ]; then
    # shellcheck disable=SC2242
    exit "未输入GZCTF平台管理员用户名"
fi

read -p "输入GZCTF平台管理员密码: " admin_pass
if [ -z "$admin_pass" ]; then
    # shellcheck disable=SC2242
    exit "未输入GZCTF平台管理员密码"
fi

read -p '输入GZCTF需要监测的比赛名，多个使用`隔开，为空则监听所有开放比赛: ' game
IFS='`' read -ra arraya <<< "$game"

change_Source

start

mv daemon.json /etc/docker/daemon.json
sudo systemctl daemon-reload && sudo systemctl restart docker

cd GZCTF-BOT-QQ || exit
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
apt -y update
apt install -y python3.10
sudo apt install -y python3.10-venv
sudo apt install -y libgbm1 libasound2
python3 -m venv bot
source bot/bin/activate
pip install -i https://mirrors.ustc.edu.cn/pypi/web/simple -r requirements.txt
nb plugin install nonebot_plugin_apscheduler

public_ip=$(curl -s https://api.ipify.org)

docker run -d \
-e ACCOUNT=3766745185 \
-e WSR_ENABLE=true \
-e WS_URLS='["ws://'+"$public_ip"+':8988/onebot/v11/ws/"]' \
-v ./napcat/app:/usr/src/app/napcat \
-v ./napcat/config:/usr/src/app/napcat/config \
-p 6099:6099 \
--name napcat \
--restart=always \
mlikiowa/napcat-docker:latest

echo "请扫码登录QQ\n或者通过 napcat/app/qrcode.png 扫码登录\n或者打开网站 http://$public_ip:6099/webui 扫码登录\n"

while true; do
    docker logs napcat
    read -p "是否登录成功(y/n): " Y

    case $Y in
        y)
            echo "登录成功，下一步......"
            break
            ;;
        n)
            echo "重新获取二维码......"
            ;;
        *)
            echo "无效的选择，请重新输入！"
            ;;
    esac
done

token=$(< /dev/urandom tr -dc 'a-zA-Z0-9' | head -c 32)

sed -i "s|GZCTFBOT XXX|$token|g" ./.env
super_admin='["'
for element in "${array[@]}"
do
    super_admin="$super_admin$element\",\""
done
super_admin=$(echo "$super_admin" | sed 's/,"\?$//')
super_admin="$super_admin\"]"
sed -i "s|[""]|$super_admin|g" ./.env
sed -i "s|\"token\": \"\"|\"token\": \"$token\"|g" ./napcat/config/onebot11_$qq.json
sed -i "s|\"SEND_LIST\": []|\"SEND_LIST\": [$qqg]|g" ./gzctf-bot/plugins/gzctf_bot_qq/config.py
games='["'
for element in "${arraya[@]}"
do
    games="$games$element\",\""
done
games=$(echo "$games" | sed 's/,"\?$//')
games="$games\"]"
sed -i "s|\"GAME_LIST\": []|\"GAME_LIST\": $games|g" ./gzctf-bot/plugins/gzctf_bot_qq/config.py
sed -i "s|\"GZCTF_URL\": \"\"|\"GZCTF_URL\": \"$url\"|g" ./gzctf-bot/plugins/gzctf_bot_qq/config.py
sed -i "s|\"GZ_USER\": \"\"|\"GZ_USER\": \"$admin_name\"|g" ./gzctf-bot/plugins/gzctf_bot_qq/config.py
sed -i "s|\"GZ_PASS\": \"\"|\"GZ_PASS\": \"$admin_pass\"|g" ./gzctf-bot/plugins/gzctf_bot_qq/config.py

nohup python3 bot.py >bot.log 2>&1 &

echo "部署成功！"