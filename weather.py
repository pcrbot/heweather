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

@sv.on_rex('^添加(城市)?([预播])报\s*(\d*)\s*$')
async def add_schedule(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    messag = None if ev['match'].group(3) == '' else ev['match'].group(3)
    if messag != None:
        if int(messag) + 1 > len(tmp[key]):
            await bot.send(ev, '序号超范围啦！你是要查询外太空的天气吗？', at_sender = True)
            return
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

@sv.on_rex('^(取消|删除)(城市)?[播预]报\s*(\d*)\s*$')
async def add_schedule(bot, ev):
    id = ev['match'].group(3)
    gid = ev['group_id']
    msg = await del_city(gid, id)
    await bot.send(ev, msg, at_sender = True)

@sv.on_rex('^查看(城市)?[播预]报$')
async def watch_schedule(bot, ev):
    gid = ev['group_id']
    msg = await watch_city(gid)
    await bot.send(ev, msg, at_sender = True)

@sv.on_rex('^([搜查]天气|天气预报)\s(.*)\s*$')
async def location_find(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    tmp[key] = {}
    name = ev['match'].group(2)
    if not name:
        await bot.send(ev, '请输入要查询的城市名哦~')
        return
    if name == '兰德索尔':
        await bot.send(ev, '兰德索尔的今日天气是骑士君的形状~', at_sender = True)
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

@sv.on_rex('^(实[况时]|当前)天气\s*(\d*)\s*$')
async def weather_now(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    messag = None if ev['match'].group(2) == '' else ev['match'].group(2)
    if messag != None:
        if int(messag) + 1 > len(tmp[key]):
            await bot.send(ev, '序号超范围啦！你是要查询外太空的天气吗？', at_sender = True)
            return
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

@sv.on_rex('^([今明后])[日天]天气\s*(\d*)\s*$')
async def weather_tomorrow(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    messag = None if ev['match'].group(2) == '' else ev['match'].group(2)
    if ev['match'].group(1) == '今':
        day = 0
    elif ev['match'].group(1) == '明':
        day = 1
    else:
        day = 2
    if messag != None:
        if int(messag) + 1 > len(tmp[key]):
            await bot.send(ev, '序号超范围啦！你是要查询外太空的天气吗？', at_sender = True)
            return
    lid, succeed = await get_location_id(key, messag, tmp)
    if succeed == False:
        await bot.send(ev, '请先发送“搜天气 城市”来选择地区哟', at_sender = True)
        return
    tenki = await get_weather_forecast(lid, apikey, 3)
    if not isinstance(tenki, tuple):
        msg = weather_today_text(tenki[day], ev['match'].group(1))
        await bot.send(ev, f'\n{msg}', at_sender=True)
    else:
        code = tenki[0]
        e = tenki[1]
        await bot.send(ev, f'\n查询出错...错误代码{code},{e},请联系管理员进行维护', at_sender = True)

@sv.on_rex('^([三七37])天天气(简报)?\s*(\d*)\s*$')
async def weather_shortdesc(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    messag = None if ev['match'].group(3) == '' else ev['match'].group(3)
    if messag != None:
        if int(messag) + 1 > len(tmp[key]):
            await bot.send(ev, '序号超范围啦！你是要查询外太空的天气吗？', at_sender = True)
            return
    day = 3 if ev['match'].group(1) == '三' or ev['match'].group(1) == '3' else 7
    lid, succeed = await get_location_id(key, messag, tmp)
    if succeed == False:
        await bot.send(ev, '请先发送“搜天气 城市”来选择地区哟', at_sender = True)
        return
    tenki = await get_weather_forecast(lid, apikey, day)
    city = tenki[0]['name']
    text_day = '三' if day == 3 else '七'
    msg = [f'\n{city}近{text_day}日天气简报']
    if not isinstance(tenki, tuple):
        msg.extend(weather_forecast_text(tenki))
        await bot.send(ev, '\n'.join(msg), at_sender=True)
    else:
        code = tenki[0]
        e = tenki[1]
        await bot.send(ev, f'\n查询出错...错误代码{code},{e},请联系管理员进行维护', at_sender = True)

@sv.on_rex('^(未来)?(24|二十四)小时(实时)?天气([简速]报)?\s*(\d*)\s*$')
async def weather_shortdesc(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    messag = None if ev['match'].group(5) == '' else ev['match'].group(5)
    if messag != None:
        if int(messag) + 1 > len(tmp[key]):
            await bot.send(ev, '序号超范围啦！你是要查询外太空的天气吗？', at_sender = True)
            return
    day = 3 if ev['match'].group(1) == '三' or ev['match'].group(1) == '3' else 7
    lid, succeed = await get_location_id(key, messag, tmp)
    if succeed == False:
        await bot.send(ev, '请先发送“搜天气 城市”来选择地区哟', at_sender = True)
        return
    tenki = await get_weather_hour(lid, apikey)
    city = tenki[0]['name']
    text_day = '三' if day == 3 else '七'
    msg = [f'\n{city}未来24小时天气简报']
    if not isinstance(tenki, tuple):
        msg.extend(weather_hour_text(tenki))
        await bot.send(ev, '\n'.join(msg), at_sender=True)
    else:
        code = tenki[0]
        e = tenki[1]
        await bot.send(ev, f'\n查询出错...错误代码{code},{e},请联系管理员进行维护', at_sender = True)
