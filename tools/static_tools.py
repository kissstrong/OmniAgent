import random


def get_city_coordinate(city: str) -> str:
    """根据城市名称查询该城市的经纬度坐标。

    Args:
        city: 城市名称，例如：南京、北京、上海
    """
    longitude = 73 + random.random() * (135 - 73)
    latitude = 18 + random.random() * (54 - 18)
    return f"城市：{city}，经纬度：{longitude:.6f},{latitude:.6f}"


def get_city_weather(city: str) -> str:
    """根据城市名称查询城市当前天气信息。

    Args:
        city: 城市名称，例如：南京、北京、上海
    Returns:
        城市天气字符串，包含天气状况、温度、湿度、风速
    """
    weather_types = ["晴", "多云", "阴", "小雨", "雷阵雨", "雾", "小雪"]
    weather = random.choice(weather_types)
    temp = round(random.uniform(-8, 38), 1)
    humidity = random.randint(20, 95)
    wind_speed = round(random.uniform(0, 12), 1)
    return f"城市：{city}，天气：{weather}，温度：{temp}℃，相对湿度：{humidity}%，风速：{wind_speed}m/s"


# 所有工具列表
static_tools = [get_city_coordinate, get_city_weather]
