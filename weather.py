from .api import *
from . import *

tmp = {}    # 'gid-uid': locationId

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
    if key not in tmp:
        await bot.send(ev, '请先发送“搜天气 城市”来选择地区哟')
        return
    location_dict = tmp[key]
    if ev.message.extract_plain_text().strip():
        location_idx = ev.message.extract_plain_text().strip()
    else:
        location_idx = '0' #不填或者填错默认为匹配度最高的第一位
    lid = idx2lid(tmp, key, location_idx)
    tenki = await get_weather_now(lid, apikey)
    if not isinstance(tenki, tuple):
        tenki = tenki[0]
        msg = f'''
==={tenki['name']}实时天气===
当地观测时间:{tenki['obsTime'].split('+')[0].replace('T',' ')}
当前气象:{tenki['text']}
当前温度:{tenki['temp']}°C
当前体感温度:{tenki['feelsLike']}°C
当前风力等级:{tenki['windScale']}级
当前风速:{tenki['windSpeed']}km/h
当前相对湿度:{tenki['humidity']}%
当前大气压强:{tenki['pressure']}hpa
当前能见度:{tenki['vis']}km
当前云量:{tenki['cloud']}%
也可以进入{tenki['fxLink']}查看当前城市天气详情
        '''.strip()
        await bot.send(ev, f'\n{msg}', at_sender=True)
    else:
        code = tenki[0]
        e = tenki[1]
        await bot.send(ev, f'\n查询出错...错误代码{code},{e},请联系管理员进行维护', at_sender = True)

@sv.on_prefix(('今日天气'))
async def weather_tomorrow(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    if key not in tmp:
        await bot.send(ev, '请先发送“搜天气 城市”来选择地区哟')
        return
    location_dict = tmp[key]
    if ev.message.extract_plain_text().strip():
        location_idx = ev.message.extract_plain_text().strip()
    else:
        location_idx = '0' #不填或者填错默认为匹配度最高的第一位
    lid = idx2lid(tmp, key, location_idx)
    tenki = await get_weather_forecast(lid, apikey)
    if not isinstance(tenki, tuple):
        tenki = tenki[0]
        textDay = tenki_text(tenki['textDay'], 'day') # 将文字描述转换成句子，后续将移入config方便自定义
        textNight = tenki_text(tenki['textNight'], 'night')
        textUV = uv_text(int(tenki['uvIndex']))
        msg = f'''
==={ymd2chs(tenki['fxDate'])}{tenki['name']}天气预报===
今天{textDay}
今日最低温度为{tenki['tempMin']}°C，最高温度是{tenki['tempMax']}°C
白天的风力等级为{tenki['windScaleDay']}级，风向是{tenki['windDirDay']}哟
{textUV}
今天{textNight}
夜间风力等级为{tenki['windScaleNight']}级，风向是{tenki['windDirNight']}的说
日出时间为{hm2chs(tenki['sunrise'])}，日落时间则为{hm2chs(tenki['sunset'])}哒
今晚的{tenki['moonPhase']}将在{hm2chs(tenki['moonrise'])}升起，{hm2chs(tenki['moonset'])}落下
今日的相对湿度为{tenki['humidity']}%，大气压强为{tenki['pressure']}hpa
能见度为{tenki['vis']}km，云量为{tenki['cloud']}%，总降水量为{tenki['precip']}mm
也可以进入{tenki['fxLink']}查看当前城市天气详情哦~
        '''.strip()
        await bot.send(ev, f'\n{msg}', at_sender=True)
    else:
        code = tenki[0]
        e = tenki[1]
        await bot.send(ev, f'\n查询出错...错误代码{code},{e},请联系管理员进行维护', at_sender = True)

@sv.on_prefix(('天气简报'))
async def weather_shortdesc(bot, ev):
    key = f'{ev.group_id}-{ev.user_id}'
    if key not in tmp:
        await bot.send(ev, '请先发送“搜天气 城市”来选择地区哟')
        return
    if ev.message.extract_plain_text().strip():
        location_idx = ev.message.extract_plain_text().strip()
    else:
        location_idx = '0' #不填或者填错默认为匹配度最高的第一位
    lid = idx2lid(tmp, key, location_idx)
    tenki = await get_weather_forecast(lid, apikey)
    city = tenki[0]['name']
    msg = [f'\n{city}近三日天气简报']
    if not isinstance(tenki, tuple):
        for desc in tenki:
            if desc['textDay'] == desc['textNight']:
                textTrans = desc['textDay']
            else:
                textTrans = f"{desc['textDay']}转{desc['textNight']}"
            if desc['tempMax'] == desc['tempMin']:
                tempTrans = desc['tempMax']
            else:
                tempTrans = f"{desc['tempMax']}°C~{desc['tempMin']}°C"
            msg.append(
                f"{'='*15}\n{ymd2chs(desc['fxDate'])}\n{textTrans}\n{tempTrans}"
            )
        await bot.send(ev, '\n'.join(msg), at_sender=True)
    else:
        code = tenki[0]
        e = tenki[1]
        await bot.send(ev, f'\n查询出错...错误代码{code},{e},请联系管理员进行维护', at_sender = True)