from .api import *
from . import *
import json
from time import sleep
import hoshino

tmp = {}    # 'gid-uid': locationId

bot = hoshino.get_bot()

@sv.scheduled_job('cron', hour = '7')
async def schedule_weather():
    data = load_data()
    for lid in data:
        tenki = await get_weather_forecast(lid, apikey)
        for gid in data[lid]['enable_group']:
            if not isinstance(tenki, tuple):
                msg = weather_today_text(tenki[0])
                await bot.send_group_msg(group_id = gid, message = msg)
            else:
                code = tenki[0]
                e = tenki[1]
                await bot.send_group_msg(group_id = gid, message = f'\n查询出错...错误代码{code},{e},请联系管理员进行维护')
            sleep(1)

@sv.on_prefix(('添加城市预报','添加预报','添加播报'))
async def add_schedule(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    messag = ev.message.extract_plain_text().strip()
    lid, succeed = await get_location_id(key, messag, tmp)
    if succeed == False:
        await bot.send(ev, '请先发送“搜天气 城市”来选择地区哟', at_sender = True)
        return
    if messag:
        location_idx = messag
    else:
        location_idx = '0' #不填或者填错默认为匹配度最高的第一位
    msg = await add_city(ev['group_id'], lid, tmp[key][str(location_idx)])
    await bot.send(ev, msg, at_sender = True)

@sv.on_prefix(('取消城市预报','取消预报','取消播报'))
async def add_schedule(bot, ev):
    id = ev.message.extract_plain_text().strip()
    gid = ev['group_id']
    msg = await del_city(gid, id)
    await bot.send(ev, msg, at_sender = True)

@sv.on_fullmatch(('查看城市预报','查看预报','查看播报'))
async def watch_schedule(bot, ev):
    gid = ev['group_id']
    msg = await watch_city(gid)
    await bot.send(ev, msg, at_sender = True)

@sv.on_prefix(('搜天气','查天气','天气预报'))
async def location_find(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    tmp[key] = {}
    name = ev.message.extract_plain_text()
    if not name:
        await bot.send(ev, '请输入要查询的城市名哦~')
        return
    msg = ['请选择想要查询的城市~']
    location_list = await get_location_name(name, apikey)
    if not isinstance(location_list, tuple): #api报错判断
        for idx, location in enumerate(location_list):
            msg.append(
                f"{idx}.{location['country']} - {location['adm1']} - {location['adm2']} - {location['name']}"
            )
            tmp[key][str(idx)] = location   #点歌插件抄来的思路
        msg.append('可以发送“天气帮助”获取使用说明哦~')
        await bot.send(ev, '\n'.join(msg), at_sender = True)
    else:
        code = location_list[0]
        e = location_list[1]
        await bot.send(ev, f'\n查询出错...错误代码{code},{e},请联系管理员进行维护', at_sender = True)

@sv.on_prefix(('实时天气','实况天气','当前天气'))
async def weather_now(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    messag = ev.message.extract_plain_text().strip()
    lid, succeed = await get_location_id(key, messag, tmp)
    if succeed == False:
        await bot.send(ev, '请先发送“搜天气 城市”来选择地区哟', at_sender = True)
        return
    tenki = await get_weather_now(lid, apikey)
    if not isinstance(tenki, tuple):
        msg = weather_now_text(tenki[0])
        await bot.send(ev, f'\n{msg}', at_sender=True)
    else:
        code = tenki[0]
        e = tenki[1]
        await bot.send(ev, f'\n查询出错...错误代码{code},{e},请联系管理员进行维护', at_sender = True)

@sv.on_prefix(('今日天气'))
async def weather_tomorrow(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    messag = ev.message.extract_plain_text().strip()
    lid, succeed = await get_location_id(key, messag, tmp)
    if succeed == False:
        await bot.send(ev, '请先发送“搜天气 城市”来选择地区哟', at_sender = True)
        return
    tenki = await get_weather_forecast(lid, apikey)
    if not isinstance(tenki, tuple):
        msg = weather_today_text(tenki[0])
        await bot.send(ev, f'\n{msg}', at_sender=True)
    else:
        code = tenki[0]
        e = tenki[1]
        await bot.send(ev, f'\n查询出错...错误代码{code},{e},请联系管理员进行维护', at_sender = True)

@sv.on_prefix(('天气简报'))
async def weather_shortdesc(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    messag = ev.message.extract_plain_text().strip()
    lid, succeed = await get_location_id(key, messag, tmp)
    if succeed == False:
        await bot.send(ev, '请先发送“搜天气 城市”来选择地区哟', at_sender = True)
        return
    tenki = await get_weather_forecast(lid, apikey)
    city = tenki[0]['name']
    msg = [f'\n{city}近三日天气简报']
    if not isinstance(tenki, tuple):
        msg.extend(weather_forecast_text(tenki))
        await bot.send(ev, '\n'.join(msg), at_sender=True)
    else:
        code = tenki[0]
        e = tenki[1]
        await bot.send(ev, f'\n查询出错...错误代码{code},{e},请联系管理员进行维护', at_sender = True)
