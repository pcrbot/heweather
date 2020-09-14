import hoshino
from hoshino import Service

sv = Service('heweather')

try:
    config = hoshino.config.heweather.heweather_config
except:
    hoshino.logger.error('HeWeather无配置文件!请仔细阅读README')

apikey = config.API_KEY

from .weather import *
from .api import *

@sv.on_fullmatch(('天气帮助','天气预报帮助','帮助天气','搜天气帮助','查天气帮助'))
async def tenki_help_chat(bot, ev):
    msg = config.TENKI_HELP
    await bot.send(ev, msg, at_sender=True)