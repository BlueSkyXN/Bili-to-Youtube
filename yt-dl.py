import subprocess
import concurrent.futures

# 设置下载目录和代理
output_dir = 'H:\Youtube'
proxy = 'socks5://127.0.0.1:10808'
download_list_path = 'F:/Download/YouTube_Links.txt'

# 读取所有的 YouTube 链接
with open(download_list_path, 'r') as file:
    links = [line.strip() for line in file if line.strip()]

# 下载单个视频的函数
def download_video(link):
    cookies_path = r'C:\Users\SKY\AppData\Local\Google\Chrome\User Data\Default'
    command = [
        'yt-dlp',
        '--format', 'bestvideo+bestaudio',
        '--merge-output-format', 'mp4',
        '-o', f'{output_dir}/%(title)s.%(ext)s',
        '--proxy', proxy,
        '--cookies-from-browser', f'chrome:{cookies_path}',
        '--concurrent-fragments', '10',  # 添加 --concurrent-fragments 参数
        link
    ]
    subprocess.run(command, stdout=subprocess.PIPE)


# 使用 ThreadPoolExecutor 来并发下载视频
def download_videos_concurrently(links, max_workers=30):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_video, link) for link in links]
        for future in concurrent.futures.as_completed(futures):
            future.result()

# 调用函数开始下载
if __name__ == '__main__':
    download_videos_concurrently(links)
