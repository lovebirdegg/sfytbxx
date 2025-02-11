import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

from datetime import date


def fetch_procurement_info():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    base_url = 'http://sdgp.sdcz.gov.cn/sdgp2017/site/listnew.jsp'
    
    # 存储结果的列表
    results = []
    # 获取当前日期（不包含时间）
    today = date.today()
    # 格式化日期
    formatted_date = today.strftime("%Y-%m-%d") # 例如："2023-04-
    # 可能需要处理分页，示例先获取第一页
    # formatted_date ="2024-12-25"
    params = {"subject":"",
    "unitname":"济南市妇幼保健院",
    "pdate":formatted_date,
    "colcode":"2504",
    "curpage":1,
    "grade":"",
    "region":"",
    "firstpage":1
    }

    print(params)

    try:
        response = requests.post(base_url, headers=headers, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 根据实际网页结构解析数据，这里需要自行调整
        items = soup.select('.news_list2 > li')  # 假设列表项的CSS选择器

        for item in items:
            title = item.select_one('.title').text.strip()
            link = item.select_one('a')['href']
            
            results.append({
                '标题': title,
                '链接': link
            })

        # 将结果转为DataFrame并保存
        df = pd.DataFrame(results)
        df.to_excel('采购信息.xlsx', index=False)
        print("数据已保存为 采购信息.xlsx")

    except Exception as e:
        print(f"抓取失败: {str(e)}")

if __name__ == "__main__":
    fetch_procurement_info()
    time.sleep(1)  # 礼貌性延迟