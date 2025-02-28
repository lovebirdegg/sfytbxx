import requests
# import pandas as pd
from bs4 import BeautifulSoup
import time
import json
import notify
import urllib.parse
import os  # 用于导入系统变量
import datetime
push_config = {
    'HITOKOTO': False,                  # 启用一言（随机句子）

    'BARK_PUSH': 'https://api.day.app/h9pruUjgra99mHLV3TiRJB',                    # bark IP 或设备码，例：https://api.day.app/DxHcxxxxxRxxxxxxcm/
    'BARK_ARCHIVE': '',                 # bark 推送是否存档
    'BARK_GROUP': '',                   # bark 推送分组
    'BARK_SOUND': '',                   # bark 推送声音
    'BARK_ICON': '',                    # bark 推送图标
}
def bark(title: str, content: str) -> None:
    """
    使用 bark 推送消息。
    """
    if not push_config.get("BARK_PUSH"):
        print("bark 服务的 BARK_PUSH 未设置!!\n取消推送")
        return
    print("bark 服务启动")

    if push_config.get("BARK_PUSH").startswith("http"):
        url = f'{push_config.get("BARK_PUSH")}/{urllib.parse.quote_plus(title)}/{urllib.parse.quote_plus(content)}'
    else:
        url = f'https://api.day.app/{push_config.get("BARK_PUSH")}/{urllib.parse.quote_plus(title)}/{urllib.parse.quote_plus(content)}'

    bark_params = {
        "BARK_ARCHIVE": "isArchive",
        "BARK_GROUP": "group",
        "BARK_SOUND": "sound",
        "BARK_ICON": "icon",
    }
    params = ""
    for pair in filter(
        lambda pairs: pairs[0].startswith("BARK_")
        and pairs[0] != "BARK_PUSH"
        and pairs[1]
        and bark_params.get(pairs[0]),
        push_config.items(),
    ):
        params += f"{bark_params.get(pair[0])}={pair[1]}&"
    if params:
        url = url + "?" + params.rstrip("&")
    response = requests.get(url).json()

    if response["code"] == 200:
        print("bark 推送成功！")
    else:
        print("bark 推送失败！")

def dingding_bot(title: str, content: str) -> None:
    """
    使用 钉钉机器人 推送消息。
    """

    url = 'https://oapi.dingtalk.com/robot/send?access_token=b07e0cdc205d61349c9e5bad7e108b67a90fb0b4fa417f5f3bb33c637a9d57dc'
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {
        "msgtype": "markdown", 
        "markdown": {
            "title": f"{title}",
            "text":f"{content}"}
            }
    print(data)
    response = requests.post(url=url, data=json.dumps(data), headers=headers, timeout=15).json()

    if not response["errcode"]:
        print("钉钉机器人 推送成功！")
    else:
        print("钉钉机器人 推送失败！",response)

def convert_table_to_markdown(table_data):
    """
    Convert a 2D list to Markdown table format.
    :param table_data: List of lists representing rows of the table.
    :return: Markdown formatted table string.
    """
    if not table_data:
        return ""
    
    # Generate header and separator
    header = " | ".join(table_data[0])
    separator = " | ".join(["---"] * len(table_data[0]))
    
    # Generate table rows
    rows = [f" | ".join(row) for row in table_data[1:]]
    
    # Combine all parts
    markdown_table = "\n".join(["| " + header + " |", "| " + separator + " |"] + ["| " + row + " |" for row in rows])
    
    return markdown_table


def fetch_procurement_info():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    base_url = 'http://sdgp.sdcz.gov.cn/sdgp2017/site/listnew.jsp'
    
    # 存储结果的列表
    results = [["名称","链接"]]
    # 获取当前日期（不包含时间）
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    previous_date = today - one_day

    # 格式化日期
    formatted_date = previous_date.strftime("%Y-%m-%d") # 例如："2023-04-
    # 可能需要处理分页，示例先获取第一页
    # formatted_date ="2025-02-25"

    unit_name     = ''
    if 'UNIT_NAME' in os.environ:  # 判断 JD_COOKIE是否存在于环境变量
        unit_name = os.environ['UNIT_NAME']# 读取系统变量 以 & 分割变量
    else:  # 判断分支
        print.info("未添加JD_COOKIE变量")  # 标准日志输出
        sys.exit(0)  # 脚本退出

    params = {"subject": "",
            "pdate": formatted_date,
            "kindof": "",
            "areacode":  "",
            "unitname":  unit_name,
            "projectname": "",
            "projectcode": "",
            "colcode": "0303",
            "curpage": 1,
            "grade": "city",
            "region": "",
            "firstpage": 1
    }

    print(params)

    try:
        response = requests.post(base_url, headers=headers, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 根据实际网页结构解析数据，这里需要自行调整
        items = soup.select('.news_list2 > li')  # 假设列表项的CSS选择器
        print(items)
        for item in items:
            title = item.select_one('.title').text.strip()
            link = 'http://sdgp.sdcz.gov.cn'+item.select_one('a')['href']

            results.append([title,link])
        if(len(results) > 1):
            markdown_table = convert_table_to_markdown(results)
            dingding_bot("招标信息",markdown_table)
        bark("市妇幼招标数：",formatted_date+"【"+str(len(results)-1)+"】")
        print("运行成功")

    except Exception as e:
        bark("sfy_error",f"抓取失败: {str(e)}")
        print(f"抓取失败: {str(e)}")

if __name__ == "__main__":
    fetch_procurement_info()
    time.sleep(1)  # 礼貌性延迟
