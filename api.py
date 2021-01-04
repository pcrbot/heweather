from .weather import *
from . import *

import json
import requests
import os

from hoshino import logger


'''
城市信息查询返回格式:
id: 城市/地区id
name: 城市/地区名
country: 城市/地区所属国家名
adm1: 城市/地区所属一级行政区域
adm2: 城市/地区上级行政区划名称
'''
async def get_location_name(location, key):
    location_list = []
    url = 'https://geoapi.heweather.net/v2/city/lookup?key=' + key + '&location=' + location
    try:
        resp = requests.request('GET', url, timeout=5).json()
        if resp['code'] == '200':
            for item in resp['location']:
                location_list.append(
                    {
                        'id': item['id'],
                        'name': item['name'],
                        'country': item['country'],
                        'adm1': item['adm1'],
                        'adm2': item['adm2']
                    }
                )
        else:
            e = stauts_code(resp['code'])
            logger.error(f'城市信息搜索接口调用失败,{e}')
            location_list = (resp['code'], e)
        return location_list
    except Exception as e:
        logger.error(f'获取城市信息数据超时,错误信息为{e}')
        location_list = ('请求超时，请重试', f'错误信息为{e}')
    return location_list

'''
实况天气查询返回格式:
obsTime: 实况观测时间
temp: 实况温度
feelsLike: 实况体感温度
icon: 天气图标
text: 实况天气文字描述
wind360: 实况风向360角度
windDir: 实况风向
windScale: 实况风力等级
windSpeed: 实况风速
humidity: 实况相对湿度
precip: 实况降水量
pressure: 实况大气压强
vis: 实况能见度
cloud: 实况云量
dew: 实况露点温度
fxLink: 天气自适应网页
name: 城市名
'''
async def get_weather_now(location, key):
    imatenki_list = []
    location_info = await get_location_name(location, key)
    location = location_info[0]['id']
    url = 'https://devapi.heweather.net/v7/weather/now?key=' + key + '&location=' + location
    try:
        resp = requests.request('GET', url, timeout=5).json()
        if resp and resp['code'] == '200':
            resp['now']['fxLink'] = resp['fxLink']# 把网页链接给加上
            resp['now']['name'] = location_info[0]['name']# 加入城市名称
            imatenki_list.append(resp['now'])
        else:
            e = stauts_code(resp['code'])
            logger.error(f'实况天气获取接口调用失败,{e}')
            imatenki_list = (resp['code'], e)
        return imatenki_list
    except Exception as e:
        if not resp:
            logger.error(f'获取实况天气数据超时,错误信息为{e}')
            imatenki_list = ('请求超时，请重试', f'错误信息为{e}')
            
    return imatenki_list

'''
天气预报查询返回格式
返回3天内的天气
fxDate: 预报日期
sunrise: 日出时间
sunset: 日落时间
moonrise: 月升时间
moonset: 月落时间
moonPhase: 月相名称
tempMax: 预报当天最高温度
tempMin: 预报当天最低温度
iconDay: 预报白天天气图标
textDay: 预报白天天气文字描述
iconNight: 预报夜晚天气图标
textNight: 预报夜晚天气文字描述
wind360Day: 预报白天风向360角度
windDirDay: 预报白天风向
windScaleDay: 预报白天风力等级
windSpeedDay: 预报白天风速
wind360Night: 预报夜晚风向360角度
windDirNight: 预报夜晚风向
windScaleNight: 预报夜晚风力等级
windSpeedNight: 预报夜晚风速
humidity: 预报当天相对湿度
precip: 预报当天降水量
pressure: 预报当天大气压强
vis: 预报当天能见度
cloud: 预报当天云量
uvIndex: 预报当天紫外线强度指数
fxLink: 天气自适应网页
name: 城市名
'''
async def get_weather_forecast(location, key, day):         #day 表示获得未来3天或7天的天气
    tenkiyohou_list = []
    location_info = await get_location_name(location, key)
    location = location_info[0]['id']
    url = f'https://devapi.heweather.net/v7/weather/{day}d?key=' + key + '&location=' + location
    try:
        resp = requests.request('GET', url, timeout=5).json()
        if resp and resp['code'] == '200':
            for item in resp['daily']:
                tenkiyohou_list.append(
                    {
                        'fxDate': item['fxDate'],
                        'sunrise': item['sunrise'],
                        'sunset': item['sunset'],
                        'moonrise': item['moonrise'],
                        'moonset': item['moonset'],
                        'moonPhase': item['moonPhase'],
                        'tempMax': item['tempMax'],
                        'tempMin': item['tempMin'],
                        'iconDay': item['iconDay'],
                        'textDay': item['textDay'],
                        'iconNight': item['iconNight'],
                        'textNight': item['textNight'],
                        'wind360Day': item['wind360Day'],
                        'windDirDay': item['windDirDay'],
                        'windScaleDay': item['windScaleDay'],
                        'windSpeedDay': item['windSpeedDay'],
                        'wind360Night': item['wind360Night'],
                        'windDirNight': item['windDirNight'],
                        'windScaleNight': item['windScaleNight'],
                        'windSpeedNight': item['windSpeedNight'],
                        'humidity': item['humidity'],
                        'precip': item['precip'],
                        'pressure': item['pressure'],
                        'vis': item['vis'],
                        'cloud': item['cloud'],
                        'uvIndex': item['uvIndex'],
                        'fxLink': resp['fxLink'],
                        'name': location_info[0]['name']
                    }
                )
        else:
            e = stauts_code(resp['code'])
            logger.error(f'天气预报获取接口调用失败,{e}')
            tenkiyohou_list = (resp['code'], e)            
    except Exception as e:  
        logger.error(f'获取天气预报数据超时,错误信息为{e}')
        tenkiyohou_list = ('请求超时，请重试', f'错误信息为{e}')
    return tenkiyohou_list

'''
天气预报查询返回格式
逐小时预报（未来24小时）
fxTime:	    时间
temp:   	温度
icon:	    天气状况图标代码
text:	    天气状况文字描述
wind360:	风向360角度
windDir:	风向
windScale:	风力等级
windSpeed:	风速，公里/小时
humidity:	相对湿度，百分比数值
precip:	    降水量，默认单位：毫米
pop:	    降水概率，百分比数值，可能为空
pressure:	大气压强，默认单位：百帕
cloud:	    云量，百分比数值
dew:    	露点温度
'''
async def get_weather_hour(location, key):
    tenkiyohou_list = []
    location_info = await get_location_name(location, key)
    location = location_info[0]['id']
    url = f'https://devapi.qweather.com/v7/weather/24h?key=' + key + '&location=' + location
    try:
        resp = requests.request('GET', url, timeout=5).json()
        if resp and resp['code'] == '200':
            for item in resp['hourly']:
                tenkiyohou_list.append(
                    {
                        'fxTime': item['fxTime'],
                        'temp': item['temp'],
                        'icon': item['icon'],
                        'text': item['text'],
                        'wind360': item['wind360'],
                        'windDir': item['windDir'],
                        'windScale': item['windScale'],
                        'windSpeed': item['windSpeed'],
                        'humidity': item['humidity'],
                        'pop': item['pop'],
                        'precip': item['precip'],
                        'pressure': item['pressure'],
                        'cloud': item['cloud'],
                        'dew': item['dew'],
                        'fxLink': resp['fxLink'],
                        'name': location_info[0]['name']
                    }
                )
        else:
            e = stauts_code(resp['code'])
            logger.error(f'天气预报获取接口调用失败,{e}')
            tenkiyohou_list = (resp['code'], e)            
    except Exception as e:  
        logger.error(f'获取天气预报数据超时,错误信息为{e}')
        tenkiyohou_list = ('请求超时，请重试', f'错误信息为{e}')
    return tenkiyohou_list

def idx2lid(tmp, key, lidx):
    ldict = tmp[key]
    for idx in lidx:
        if idx in ldict:
            location = ldict[idx]
            lid = location['id']
            return lid
    
def stauts_code(code):
    code_list = config.STAUTS_CODE
    return code_list[code]

def tenki_text(text, time):
    if time == 'day':
        text_list = config.TENKI_DESC_DAY
    else:
        text_list = config.TENKI_DESC_NIGHT
    return text_list[text]

def uv_text(uv, day_text):
    text = f'{day_text}日紫外线强度指数为{uv}，'
    if 0 <= uv < 3:
        text += config.UV_LV1
    elif 3 <= uv < 5:
        text += config.UV_LV2
    elif 5 <= uv < 7:
        text += config.UV_LV3
    elif 7 <= uv < 10:
        text += config.UV_LV4
    elif uv >= 10:
        text += config.UV_LV5
    return(text)

def ymd2chs(ymd):
    ymd = ymd.split('-')
    chs = f'{ymd[0]}年{ymd[1]}月{ymd[2]}日'
    return chs

def hm2chs(hm):
    chs = hm.replace(':','时')+'分'
    return chs

async def get_location_id(key, messag, tmp):
    if key not in tmp:
        return -1, False
    location_dict = tmp[key]
    if messag:
        location_idx = messag
    else:
        location_idx = '0' #不填或者填错默认为匹配度最高的第一位
    lid = idx2lid(tmp, key, location_idx)
    return lid, True

async def add_city(gid, id, city):
    data = load_data()
    if (data == None):
        data = {}
    if id in data:
        if gid in data[id]['enable_group']:
            msg = f'本群已经添加了这个城市的播报啦'
            return msg
    else:
        data[id] = {}
        data[id]['enable_group'] = []
        data[id]['describe'] = f"{city['country']} - {city['adm1']} - {city['adm2']} - {city['name']}"
    data[id]['enable_group'].append(gid)
    save_data(data)
    msg = f'这座城市，多位了关心的人'
    return msg

async def del_city(gid, id):
    data = load_data()
    if id == None or id == '':
        msg = f'你怎么不告诉我删除哪个呢？'
    elif id not in data or gid not in data[id]['enable_group']:
        msg = f'这序号你想删个锤子哦'
    else:
        data[id]['enable_group'].remove(gid)
        if (len(data[id]['enable_group']) == 0):
            data.pop(id)
        save_data(data)
        msg = f'这座城市……少了位关心的人'
    return msg

async def watch_city(gid):
    data = load_data()
    msg = '' 
    for id, group in data.items():
        if gid in group['enable_group']:
            msg += f"{id} - {group['describe']}\n"
    if len(msg) == 0:
        msg = '本群没有预报的城市哦'
    else:
        msg = f'本群添加预报的城市有：\n' + msg + f'要删除请回复 取消城市预报 <序号> 哦'
    return msg

def weather_today_text(tenki, day_text):
    textDay = tenki_text(tenki['textDay'], 'day') # 将文字描述转换成句子，后续将移入config方便自定义
    textNight = tenki_text(tenki['textNight'], 'night')
    textUV = uv_text(int(tenki['uvIndex']), day_text)
    msg = f'''
==={ymd2chs(tenki['fxDate'])}{tenki['name']}天气预报===
{day_text}天{textDay}
{day_text}日最低温度为{tenki['tempMin']}°C，最高温度是{tenki['tempMax']}°C
白天的风力等级为{tenki['windScaleDay']}级，风向是{tenki['windDirDay']}哟
{textUV}
{day_text}天{textNight}
夜间风力等级为{tenki['windScaleNight']}级，风向是{tenki['windDirNight']}的说
日出时间为{hm2chs(tenki['sunrise'])}，日落时间则为{hm2chs(tenki['sunset'])}哒
{day_text}晚的{tenki['moonPhase']}将在{hm2chs(tenki['moonrise'])}升起，{hm2chs(tenki['moonset'])}落下
{day_text}日的相对湿度为{tenki['humidity']}%，大气压强为{tenki['pressure']}hpa
能见度为{tenki['vis']}km，云量为{tenki['cloud']}%，总降水量为{tenki['precip']}mm
也可以进入{tenki['fxLink']}查看当前城市天气详情哦~
    '''.strip()
    return msg

def weather_now_text(tenki):
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
    return msg

def weather_forecast_text(tenki):
    msg = []
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
    return msg

def weather_hour_text(tenki):
    msg = []
    for desc in tenki:
        pos = desc['fxTime'].find('T')
        msg.append(f'''
{'='*15}
{ymd2chs(desc['fxTime'][0:pos])}{desc['fxTime'][pos+1:pos+3]}时
温度:{desc['temp']}°C
天气:{desc['text']}
风力等级:{desc['windScale']}级
降雨概率:{desc['pop']}%
'''.strip()
        )
    return msg

def load_data():     #摘自zyujs的pcr_calender
    path = os.path.join(os.path.dirname(__file__), 'data.json')
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding='utf8') as f:
            group_data = {}
            data = json.load(f)
            for k, v in data.items():
                group_data[k] = v
            return group_data
    except:
        traceback.print_exc()

def save_data(args):     #摘自zyujs的pcr_calender
    path = os.path.join(os.path.dirname(__file__), 'data.json')
    try:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(args , f, ensure_ascii=False, indent=2)
    except:
        traceback.print_exc()




'''
搜天气 北京

返回json处理完排序发出来

天气选择 + 序号 确定location的id

返回对应location的天气然后处理json

查天气 兰德索尔（彩蛋
'''