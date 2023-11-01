import socket
import socks
import os
import argparse
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

def set_socks5_proxy(host, port):
    socks.set_default_proxy(socks.SOCKS5, host, port)
    socket.socket = socks.socksocket

def upload_video(args):
    if args.socks5:
        host, port = args.socks5.split(":")
        set_socks5_proxy(host, int(port))

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json', 
            scopes=['https://www.googleapis.com/auth/youtube.upload']
        )
        creds = flow.run_local_server(port=58080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    youtube = build('youtube', 'v3', credentials=creds)

    title = args.title if args.title else os.path.splitext(os.path.basename(args.file))[0]
    description = args.description if args.description else os.path.basename(args.file)
    body_dict = {
        'snippet': {
            'description': description,
            'title': title
        },
        'status': {
            'privacyStatus': 'unlisted'
        }
    }
    if args.categoryId:
        body_dict['snippet']['categoryId'] = args.categoryId
    if args.playlist:
        body_dict['snippet']['playlistId'] = args.playlist
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=body_dict,
        media_body=MediaFileUpload(args.file)
    )

    response = request.execute()
    print(response)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload a video to YouTube.')
    parser.add_argument('-f', '--file', default='test.mp4', help='Path to the video file.')
    parser.add_argument('-s', '--socks5', help='SOCKS5 proxy in format host:port.')
    parser.add_argument('-t', '--title', help='Title of the uploaded video.')
    parser.add_argument('-d', '--description', help='Description of the uploaded video.')
    parser.add_argument('-g', '--categoryId', help='Category ID of the uploaded video.')
    parser.add_argument('-l', '--playlist', help='Playlist ID for the uploaded video.')
    args = parser.parse_args()
    upload_video(args)
