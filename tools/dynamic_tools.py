# -*- coding: utf-8 -*-
import json
import random
from pathlib import Path


def query_news(topic: str) -> str:
    """根据主题查询相关新闻。

    Args:
        topic: 新闻主题，例如：科技、财经、体育
    """
    news_titles = [
        f"{topic}行业迎来新的发展机遇，多家机构发布最新分析",
        f"聚焦{topic}: 最新行业动态解读",
        f"{topic}领域重大进展，引发广泛讨论",
        f"市场观察｜{topic}相关政策落地，影响深远",
        f"{topic}热点事件持续发酵，各方观点汇总"
    ]
    random_title = random.choice(news_titles)
    random_content = f"这是【{topic}】主题新闻模拟内容，发布时间2026-09-23，摘要：{random_title}，相关资讯持续更新中。"
    return random_content


dynamic_tools = [query_news]

path = Path(__file__).resolve().parent


def load_json_file():
    with open(path / "tools_config.json", "r", encoding="utf-8") as f:
        data = json.load(f)  # json.load 读文件对象，直接转python dict/list
    return data


def update_json_file(data):
    with open(path / "tools_config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def reset():
    """重置need_reload值为False"""
    data = load_json_file()
    data['need_reload'] = 'False'
    update_json_file(data)


def need_reload() -> bool:
    """"查询工具是否需要重新加载"""
    data = load_json_file()
    if data['need_reload'] == 'True':
        return True
    return False
