from functools import reduce
from hashlib import md5
import urllib.parse
import time
import requests
import pandas as pd
import concurrent.futures
import subprocess
import os
import logging
import random
import shutil
import send2trash  # 需要安装 send2trash 库：pip install send2trash

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 预设全局变量
EXCEL_FILE_PATH = 'I:/bin/cache/bilibili_videos.xlsx' #下载完记得删除，如果中途失败直接重新运行即可不需要重新抓。目前不支持动态视频，只能是投稿的。
DOWNLOAD_DIR = r"L:\BiliUP-Arch\Cache" #目标下载地址，和bbdown设置一致，注意修改，自行配置bbdown的cookie。
CHECK_DOWNLOADED = True # 校验和硬跳过已下载
USE_RANDOM_UA = True  # 是否启用随机UA功能
CLEAN_SUBFOLDERS = True  # 是否清理子文件夹
DOWNLOAD_SWITCH = True  # 新增的开关变量， True 表示下载， False 表示仅抓取信息

# 生成随机的 User-Agent
def get_random_user_agent():
    random_digit = random.randint(0, 3)
    return f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.{random_digit} Safari/537.36'

# 获取 User-Agent
def get_user_agent():
    if USE_RANDOM_UA:
        return get_random_user_agent()
    else:
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'

# 清理下载目录下的子文件夹
def clean_subfolders(download_dir):
    for item in os.listdir(download_dir):
        item_path = os.path.join(download_dir, item)
        if os.path.isdir(item_path):
            logging.info(f"正在删除子文件夹及其内容: {item_path}")
            send2trash.send2trash(item_path)

# 获取最新的 img_key 和 sub_key
def get_wbi_keys():
    headers = {
        'User-Agent': get_user_agent(),
        'Referer': 'https://www.bilibili.com/'
    }
    try:
        resp = requests.get('https://api.biliapi.com/x/web-interface/nav', headers=headers, verify=False)
        resp.raise_for_status()
        json_content = resp.json()
        img_url = json_content['data']['wbi_img']['img_url']
        sub_url = json_content['data']['wbi_img']['sub_url']
        img_key = img_url.rsplit('/', 1)[1].split('.')[0]
        sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
        return img_key, sub_key
    except Exception as e:
        logging.error(f"获取 wbi keys 失败: {e}")
        return None, None

# 对 imgKey 和 subKey 进行字符顺序打乱编码
def get_mixin_key(orig):
    MIXIN_KEY_ENC_TAB = [
        46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
        33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
        61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
        36, 20, 34, 44, 52
    ]
    return reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, '')[:32]

# 为请求参数进行 wbi 签名
def enc_wbi(params, img_key, sub_key):
    mixin_key = get_mixin_key(img_key + sub_key)
    curr_time = round(time.time())
    params['wts'] = curr_time
    params = dict(sorted(params.items()))
    params = {k: ''.join(filter(lambda chr: chr not in "!'()*", str(v))) for k, v in params.items()}
    query = urllib.parse.urlencode(params)
    wbi_sign = md5((query + mixin_key).encode()).hexdigest()
    params['w_rid'] = wbi_sign
    return params

# 主函数：获取指定用户的投稿视频列表
def fetch_bilibili_videos(mid, max_pages=10, start_page=1, cookie=None, delay=0.1):
    # 获取最新的 img_key 和 sub_key
    img_key, sub_key = get_wbi_keys()
    if not img_key or not sub_key:
        logging.error("无法获取 wbi keys，退出抓取任务。")
        return []
    
    # 初始化结果列表
    all_videos = []
    current_page = start_page  # 从指定页开始
    
    while current_page < start_page + max_pages:
        # 设置请求参数
        params = {
            'mid': mid,
            'ps': '50',
            'tid': '0',
            'pn': current_page,
            'order': 'pubdate',
            'platform': 'web',
            'web_location': '1550101',
            'order_avoided': 'true'
        }
        
        # 生成签名参数
        signed_params = enc_wbi(params, img_key, sub_key)
        
        # 构造完整的 URL
        url = 'https://api.biliapi.net/x/space/wbi/arc/search?' + urllib.parse.urlencode(signed_params)
        
        # 设置请求头
        headers = {
            'User-Agent': get_user_agent(),
            'Referer': 'https://message.bilibili.com/',
        }

        if cookie:
            headers['Cookie'] = cookie
        
        try:
            # 发送请求并获取响应
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"请求失败: {e}")
            break
        
        result = response.json()
        
        # 检查是否有更多视频
        if 'data' not in result or 'list' not in result['data'] or not result['data']['list']['vlist']:
            break
        
        # 提取视频信息
        vlist = result['data']['list']['vlist']
        for video in vlist:
            video_info = {
                'title': video['title'],
                'description': video['description'],
                'play': video['play'],
                'comment': video['comment'],
                'author': video['author'],
                'created': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(video['created'])),
                'length': video['length'],
                'video_review': video['video_review'],
                'bvid': video['bvid'],
                'aid': video['aid'],
                'pic': video['pic'],
                'mid': video['mid']
            }
            all_videos.append(video_info)
        
        current_page += 1
        
        # 等待指定的间隔时间
        time.sleep(delay)
    
    return all_videos

# 解析返回的数据并保存为Excel文件
def save_to_excel(videos, file_path):
    # 转换为DataFrame
    df = pd.DataFrame(videos)
    
    # 保存为Excel文件
    df.to_excel(file_path, index=False)

# 检查视频文件是否已存在
def is_video_downloaded(bvid, download_dir):
    for file_name in os.listdir(download_dir):
        if bvid in file_name:
            return True
    return False

# 下载视频函数
def download_video(bvid):
    ua = get_user_agent()
    command = f'bbdown -ua "{ua}" {bvid}'
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"视频下载失败: {bvid}, 错误: {e}")

# 多线程下载视频
def download_videos(bvid_list, download_dir, max_workers):
    bvids_to_download = [bvid for bvid in bvid_list if not is_video_downloaded(bvid, download_dir)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(download_video, bvids_to_download)

# 整合下载检查逻辑
def check_and_download_videos(mid, EXCEL_FILE_PATH, download_dir, cookie, max_workers):
    if not os.path.exists(EXCEL_FILE_PATH):
        logging.info(f"文件 {EXCEL_FILE_PATH} 不存在，开始获取数据...")
        videos = fetch_bilibili_videos(mid, max_pages=100, cookie=cookie, delay=0.5)
        save_to_excel(videos, EXCEL_FILE_PATH)
        logging.info(f"数据已保存到 {EXCEL_FILE_PATH}")
    
    # 读取保存的 Excel 文件并获取 bvid 列
    df = pd.read_excel(EXCEL_FILE_PATH)
    bvid_list = df['bvid'].tolist()

    # 初始化计数器
    existing_count = 0
    missing_count = 0
    missing_bvids = []

    # 检测每个 bvid 是否存在于下载目录中
    for bvid in bvid_list:
        if is_video_downloaded(bvid, download_dir):
            existing_count += 1
        else:
            missing_count += 1
            missing_bvids.append(bvid)

    # 打印并记录结果
    logging.info(f"已存在的视频文件数量: {existing_count}")
    logging.info(f"不存在的视频文件数量: {missing_count}")
    logging.info(f"不存在的具体BV号: {missing_bvids}")

    # 多线程下载未下载的视频
    download_videos(missing_bvids, download_dir, max_workers)

# 示例使用
mid = 'uid'
cookie = '''ck'''
#可从bbdown的ck缓存复制全部，可哔哩哔哩网页版ck复制，可iOS等手机app抓包复制。

if CLEAN_SUBFOLDERS:
    # 清理下载目录下的子文件夹
    clean_subfolders(DOWNLOAD_DIR)

if DOWNLOAD_SWITCH:
    if CHECK_DOWNLOADED:
        # 检查并下载未下载的视频
        check_and_download_videos(mid, EXCEL_FILE_PATH, DOWNLOAD_DIR, cookie, max_workers=3)
    else:
        # 获取数据，从第一页开始，抓取100页
        videos = fetch_bilibili_videos(mid, max_pages=100, cookie=cookie, delay=1)
        # 保存到 Excel 文件（覆盖）
        save_to_excel(videos, EXCEL_FILE_PATH)
        logging.info(f"数据已保存到 {EXCEL_FILE_PATH}")
else:
    # 获取数据，从第一页开始，抓取100页
    videos = fetch_bilibili_videos(mid, max_pages=100, cookie=cookie, delay=1)
    # 保存到 Excel 文件（覆盖）
    save_to_excel(videos, EXCEL_FILE_PATH)
    logging.info(f"数据已保存到 {EXCEL_FILE_PATH}")
