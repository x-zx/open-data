import json
import requests
import os
from datetime import datetime

# 配置
JSON_PATH = 'lpr/lpr_history.json'
API_URL = 'https://www.chinamoney.com.cn/ags/ms/cm-u-bk-currency/LprHis?lang=CN'

def update_lpr():
    # 1. 准备请求头
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'https://www.chinamoney.com.cn',
        'Referer': 'https://www.chinamoney.com.cn/chinese/bklpr/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # 获取当前日期作为结束日期，一年前作为开始日期
    end_date = datetime.now().strftime('%Y-%m-%d')
    # 这里也可以根据需求固定日期，API 支持最长一年
    params = f"&strStartDate=2025-04-09&strEndDate={end_date}"

    try:
        # 2. 发起 POST 请求
        response = requests.post(API_URL + params, headers=headers, timeout=30)
        response.raise_for_status()
        new_records = response.json().get('records', [])
        
        # 3. 读取现有数据
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        else:
            history_data = []

        # 4. 数据转换与去重
        # 将现有数据转为字典，方便按日期索引
        data_dict = {item['date']: item for item in history_data}

        for rec in new_records:
            date_str = rec['showDateCN']
            # 存入/更新字典（去重关键点）
            data_dict[date_str] = {
                "date": date_str,
                "1Y": rec['1Y'],
                "5Y": rec['5Y']
            }

        # 5. 排序并写回文件 (按日期从新到旧排列)
        sorted_data = sorted(data_dict.values(), key=lambda x: x['date'], reverse=True)

        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, indent=2, ensure_ascii=False)
            
        print(f"成功更新！当前记录总数: {len(sorted_data)}")

    except Exception as e:
        print(f"更新失败: {e}")
        exit(1)

if __name__ == "__main__":
    update_lpr()