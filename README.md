# HeWeather

这是一个使用[和风天气](https://dev.heweather.com/)所提供的API进行查询,适用于HoshinoV2的天气搜索插件。

## 安装

0. 注册[和风天气开发者账号](https://console.heweather.com),在控制台的应用管理中创建KEY类型为WebAPI的新应用,保存你的KEY,后续填入配置文件中

1. [下载](https://github.com/pcrbot/heweather/archive/master.zip)或[克隆](https://github.com/pcrbot/heweather.git)本仓库 https://github.com/pcrbot/heweather

```bash
cd ~/hoshino/modules/ && git clone https://github.com/pcrbot/heweather.git
```

2. 参考注释修改配置模板 `heweather.py.example` 将其移动至Hoshino的统一配置目录之下后进行重命名

```bash
vim ./heweather.py.example
mv ./heweather.py.example ~/hoshino/config/heweather.py
```

3. 在```~/hoshino/config/__bot__.py```里加入`heweather`模块

```python
MODULES_ON = {
    heweather,
}
```

4. 重启Bot,发送```天气帮助```开始使用

### 功能列表

目前只计划接入个人开发者可使用的API

七日预报和24小时逐时预报由于突发的账号问题（无法使用API）而暂时搁置，已提交工单给官方进行反馈等待回复

- [x] 搜索全球城市信息,支持多语言以及经纬度查询
- [x] 查询实时天气信息
- [x] 查询本日天气预报
- [x] 查询三天内天气简报
- [x] 自定义部分简述文本
- [ ] 查询三天内任意一天的天气预报
- [ ] 查询七天内天气预报/简报
- [ ] 24小时内逐小时预报
