import socket
import socks
import os
import argparse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

def set_socks5_proxy(host, port):
    socks.set_default_proxy(socks.SOCKS5, host, port)
    socket.socket = socks.socksocket

def list_playlists(args):
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
            scopes=['https://www.googleapis.com/auth/youtube.readonly']
        )
        creds = flow.run_local_server(port=58080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    youtube = build('youtube', 'v3', credentials=creds)
    request = youtube.playlists().list(
        part="id,snippet",
        mine=True,
        maxResults=args.maxResults
    )

    response = request.execute()
    for item in response.get("items", []):
        print(f"Playlist Name: {item['snippet']['title']}, Playlist ID: {item['id']}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List all available YouTube playlists for the authenticated user.')
    parser.add_argument('-s', '--socks5', help='SOCKS5 proxy in format host:port.')
    parser.add_argument('-m', '--maxResults', type=int, default=25, help='Maximum number of playlists to return.')
    args = parser.parse_args()
    list_playlists(args)
