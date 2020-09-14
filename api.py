from .weather import *
from . import *

import json
import requests

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
async def get_weather_forecast(location, key):
    tenkiyohou_list = []
    location_info = await get_location_name(location, key)
    location = location_info[0]['id']
    url = 'https://devapi.heweather.net/v7/weather/3d?key=' + key + '&location=' + location
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

def uv_text(uv):
    text = f'今日紫外线强度指数为{uv}，'
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




'''
搜天气 北京

返回json处理完排序发出来

天气选择 + 序号 确定location的id

返回对应location的天气然后处理json

查天气 兰德索尔（彩蛋
'''