#!/bin/bash

cd /root/GZCTF-BOT-QQ

if [ -z "$SUPER" ]; then
    echo "未设置SUPER"
    exit 1
else
    sed -i "s|SAPT|$SUPER|g" ./.env
    if [ -z "$SEND_LIST" ]; then
        echo "未设置SEND_LIST"
        exit 1
    else
        sed -i "s|SENDL|$SEND_LIST|g" ./gzctf-bot/plugins/gzctf_bot_qq/config.py
        sed -i "s|GAMEL|$GAME_LIST|g" ./gzctf-bot/plugins/gzctf_bot_qq/config.py
        if [ -z "$GZCTF_URL" ]; then
            echo "未设置GZCTF_URL"
            exit 1
        else
            sed -i "s|GZURL|$GZCTF_URL|g" ./gzctf-bot/plugins/gzctf_bot_qq/config.py
            if [ -z "$GZ_USER" ]; then
                echo "未设置GZ_USER"
                exit 1
            else
                sed -i "s|GZUSER|$GZ_USER|g" ./gzctf-bot/plugins/gzctf_bot_qq/config.py
                if [ -z "$GZ_PASS" ]; then
                    echo "未设置GZ_PASS"
                    exit 1
                else
                    sed -i "s|GZP|$GZ_PASS|g" ./gzctf-bot/plugins/gzctf_bot_qq/config.py
                fi
            fi
        fi
    fi
fi

python3 bot.py