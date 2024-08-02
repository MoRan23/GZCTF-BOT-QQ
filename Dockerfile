FROM python:3.10-slim-bookworm

COPY gz-bot /root/GZCTF-BOT-QQ

RUN mv /root/GZCTF-BOT-QQ/start.sh /start.sh && \
    chmod +x /start.sh && \
    chmod 777 /start.sh && \
    cd /root/GZCTF-BOT-QQ && \
    pip install -i https://mirrors.ustc.edu.cn/pypi/web/simple pip -U && \
    pip config set global.index-url https://mirrors.ustc.edu.cn/pypi/web/simple && \
    pip install -r requirements.txt  && \
    nb plugin install nonebot_plugin_apscheduler

WORKDIR /root/GZCTF-BOT-QQ

EXPOSE 8988

CMD /start.sh