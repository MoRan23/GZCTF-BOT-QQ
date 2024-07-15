import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OnebotAdapter

nonebot.init()
nonebot.init(apscheduler_autostart=True)
nonebot.init(apscheduler_config={
    "apscheduler.timezone": "Asia/Shanghai"
})

driver = nonebot.get_driver()
driver.register_adapter(OnebotAdapter)

nonebot.load_builtin_plugins("echo")
nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_plugins("gzctf-bot/plugins")

if __name__ == "__main__":
    nonebot.run()