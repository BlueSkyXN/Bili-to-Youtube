import socket
import socks
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle  # 导入 pickle 模块

def set_socks5_proxy():
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 10808)
    socket.socket = socks.socksocket

def upload_video(file_path):
    # 设置S5代理
    set_socks5_proxy()

    creds = None
    if os.path.exists('token.pickle'):  # 修改文件扩展名为 .pickle
        # 如果token.pickle文件存在，尝试从中加载凭据
        with open('token.pickle', 'rb') as token:  # 修改模式为 'rb'
            creds = pickle.load(token)  # 使用 pickle.load 加载凭据

    # 如果没有有效的凭据，执行OAuth 2.0授权流程
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json', 
            scopes=['https://www.googleapis.com/auth/youtube.upload']
        )
        creds = flow.run_local_server(port=58080)  # 修改端口号
        # 保存凭据以备后用
        with open('token.pickle', 'wb') as token:  # 修改模式为 'wb' 和文件扩展名为 .pickle
            pickle.dump(creds, token)  # 使用 pickle.dump 保存凭据

    # 创建YouTube服务客户端
    youtube = build('youtube', 'v3', credentials=creds)

    # 准备视频上传请求
    request = youtube.videos().insert(
        part='snippet,status',
        body={
            'snippet': {
                'categoryId': '22',
                'description': 'Test video upload',
                'title': 'Test Video'
            },
            'status': {
                'privacyStatus': 'unlisted'
            }
        },
        media_body=MediaFileUpload(file_path)
    )

    # 执行视频上传请求
    response = request.execute()
    print(response)

if __name__ == '__main__':
    upload_video('test.mp4')
