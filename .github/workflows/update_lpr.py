import json
import urllib.request
import urllib.parse
import os
from datetime import datetime, timedelta

# 配置
JSON_PATH = 'lpr/lpr_history.json'
API_URL = 'https://www.chinamoney.com.cn/ags/ms/cm-u-bk-currency/LprHis'

def update_lpr():
    # 1. 准备参数和 Header
    end_date = datetime.now()
    start_date = end_date - timedelta(days=360) # 查询近 360 天，避免超过一年限制

    params = {
        'lang': 'CN',
        'strStartDate': start_date.strftime('%Y-%m-%d'),
        'strEndDate': end_date.strftime('%Y-%m-%d')
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'https://www.chinamoney.com.cn',
        'Referer': 'https://www.chinamoney.com.cn/chinese/bklpr/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        # 2. 发起 POST 请求 (data=b'' 表示这是一个 POST)
        req = urllib.request.Request(url, data=b'', headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            new_records = res_data.get('records', [])
        
        # 3. 读取现有数据
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        else:
            history_data = []

        # 4. 数据转换与去重
        data_dict = {item['date']: item for item in history_data}
        for rec in new_records:
            date_str = rec['showDateCN']
            data_dict[date_str] = {
                "date": date_str,
                "1Y": rec['1Y'],
                "5Y": rec['5Y']
            }

        # 5. 排序并保存
        sorted_data = sorted(data_dict.values(), key=lambda x: x['date'], reverse=True)
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, indent=2, ensure_ascii=False)
            
        print(f"成功更新！记录总数: {len(sorted_data)}")

    except Exception as e:
        print(f"更新失败: {e}")
        exit(1)

if __name__ == "__main__":
    update_lpr()