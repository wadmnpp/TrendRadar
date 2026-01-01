# -*- coding: utf-8 -*-
import os
import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom

# 配置项（仅需修改RSS_LINK为你的GitHub Pages地址）
RSS_TITLE = "TrendRadar 热点聚合"
RSS_DESCRIPTION = "TrendRadar抓取的全网热点资讯聚合（支持微博、今日头条等平台）"
RSS_LINK = "https://wadmnpp.github.io/TrendRadar"  # 后续替换关键参数
RSS_FILE_PATH = "./output/trendradar_rss.xml"  # RSS文件生成路径
OUTPUT_DATA_PATH = "./output/hot_news.json"  # TrendRadar抓取的热点数据文件路径

def load_hot_news():
    """加载TrendRadar抓取的热点数据"""
    if not os.path.exists(OUTPUT_DATA_PATH):
        return []
    try:
        import json
        with open(OUTPUT_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载热点数据失败：{e}")
        return []

def prettify_xml(elem):
    """格式化XML，避免乱码和格式混乱，符合RSS标准"""
    rough_string = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8")

def generate_rss_feed():
    """生成标准RSS 2.0格式订阅源，兼容NetNewsWire/Fluent Reader"""
    # 1. 创建RSS根节点，指定版本
    rss = ET.Element("rss")
    rss.set("version", "2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")  # 兼容Atom协议，提升阅读器兼容性

    # 2. 创建频道核心节点
    channel = ET.SubElement(rss, "channel")

    # 3. 填充频道基础信息（符合RSS 2.0标准）
    ET.SubElement(channel, "title").text = RSS_TITLE
    ET.SubElement(channel, "description").text = RSS_DESCRIPTION
    ET.SubElement(channel, "link").text = RSS_LINK
    ET.SubElement(channel, "language").text = "zh-CN"  # 中文语言，阅读器可识别并分类
    current_time = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    ET.SubElement(channel, "pubDate").text = current_time  # 发布时间（UTC格式，RSS强制要求）
    ET.SubElement(channel, "lastBuildDate").text = current_time  # 最后更新时间
    ET.SubElement(channel, "generator").text = "TrendRadar RSS Generator"

    # 4. 加载热点数据，生成每个资讯项
    hot_news_list = load_hot_news()
    for news in hot_news_list[:20]:  # 取前20条热点，避免文件过大影响阅读器加载
        item = ET.SubElement(channel, "item")
        # 资讯标题
        news_title = news.get("title", "无标题热点")
        ET.SubElement(item, "title").text = news_title
        # 资讯描述（拼接平台、热度、摘要，提升阅读体验）
        news_platform = news.get("platform", "未知平台")
        news_heat = news.get("heat", "0")
        news_summary = news.get("summary", news_title)
        news_description = f"【{news_platform}】热度：{news_heat}\n\n{news_summary}"
        ET.SubElement(item, "description").text = news_description
        # 资讯链接（若无原始链接，使用GitHub Pages地址）
        news_link = news.get("url", RSS_LINK)
        ET.SubElement(item, "link").text = news_link
        # 唯一标识（避免阅读器重复加载相同内容）
        news_guid = f"{news_link}-{datetime.datetime.utcnow().timestamp()}"
        guid = ET.SubElement(item, "guid")
        guid.set("isPermaLink", "false")
        guid.text = news_guid
        # 资讯发布时间（符合RSS标准格式）
        ET.SubElement(item, "pubDate").text = current_time

    # 5. 创建output文件夹（若不存在），保存RSS XML文件
    os.makedirs(os.path.dirname(RSS_FILE_PATH), exist_ok=True)
    with open(RSS_FILE_PATH, "wb") as f:
        f.write(prettify_xml(rss))

    print(f"RSS订阅源生成完成，路径：{RSS_FILE_PATH}")
    print(f"RSS文件公开访问地址：{RSS_LINK}/output/trendradar_rss.xml")

if __name__ == "__main__":
    generate_rss_feed()
