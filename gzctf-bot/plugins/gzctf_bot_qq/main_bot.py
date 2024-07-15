from nonebot import on_command
from nonebot.rule import Rule, to_me

get = on_command("get", rule=to_me())


@get.handle()
async def get_handle(bot, event):
    try:
        await bot.send(event, "Hello, World!")
    except Exception as e:
        print(e)
        await bot.send(event, "Error")
