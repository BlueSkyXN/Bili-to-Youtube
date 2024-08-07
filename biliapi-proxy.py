from flask import Flask, request, redirect, Response
import requests
import random
from datetime import datetime
import os

app = Flask(__name__)

# 配置日志记录开关
LOGGING_ENABLED = os.getenv('LOGGING_ENABLED', 'true').lower() == 'true'
RETRY_COUNT = 3
TIMEOUT = 5  # 请求超时时间，单位：秒

# 目标URL列表
api_urls = [
    'https://api.bilibili.com/x/player/wbi/playurl',
    'https://api.biliapi.net/x/player/wbi/playurl',
    'https://api.biliapi.com/x/player/wbi/playurl'
]

# 备选域名列表
redirect_domains = [
    'https://api.biliapi.net',
    'https://api.biliapi.com'
]

def proxy_request(url, headers, data, method):
    for _ in range(RETRY_COUNT):
        try:
            resp = requests.request(method, url, headers=headers, data=data, cookies=request.cookies, timeout=TIMEOUT)
            return resp
        except requests.RequestException:
            continue
    return None

def log_request_info(log_info):
    if LOGGING_ENABLED:
        with open('proxy.log', 'a') as log_file:
            log_file.write(f"{log_info}\n")

@app.route('/x/player/wbi/playurl', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_specific_path():
    query_string = request.query_string.decode('utf-8')
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}
    data = request.get_data()
    method = request.method
    
    response = None
    success = False
    
    log_info = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "url": f"{request.base_url}?{query_string}",
        "results": [],
        "final_decision": None
    }
    
    for base_url in api_urls:
        url = f"{base_url}?{query_string}"
        response = proxy_request(url, headers, data, method)
        
        if response and response.status_code == 200:
            content = response.content
            if b'"result":"suee"' in content:
                log_info["results"].append(f"{base_url} - Normal")
                success = True
                break
            else:
                log_info["results"].append(f"{base_url} - Exception: No valid result found")
                response = None  # 认为这是一次失败，继续尝试下一个 URL
                continue
        else:
            log_info["results"].append(f"{base_url} - Failed")
            response = None  # 确保继续尝试下一个 URL

    if success:
        log_info["final_decision"] = "Normal"
        log_request_info(log_info)
        proxy_response = Response(response.content, status=response.status_code)
        for key, value in response.headers.items():
            if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
                proxy_response.headers[key] = value
        return proxy_response
    else:
        log_info["final_decision"] = "Failed"
        log_request_info(log_info)
        proxy_response = Response(response.content if response else 'Service Unavailable', status=response.status_code if response else 503)
        for key, value in (response.headers.items() if response else []):
            if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
                proxy_response.headers[key] = value
        return proxy_response

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_all_requests(path):
    base_url = random.choice(redirect_domains)
    target_url = f"{base_url}/{path}"
    
    if request.query_string:
        target_url += f"?{request.query_string.decode('utf-8')}"
    
    return redirect(target_url, code=302)

if __name__ == '__main__':
    app.run(port=5001)
