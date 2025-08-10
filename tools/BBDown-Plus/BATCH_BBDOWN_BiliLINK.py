import re
import sys

def extract_urls(file_path, mode='default'):
    # 更新的正则表达式以包括新的域名
    url_pattern = r'https://(b23\.tv/[^\s]+|www\.bilibili\.com/[^\s]+|m\.bilibili\.com/[^\s]+)'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        urls = re.findall(url_pattern, content)
        if mode == 'bbdown':
            urls = ['bbdown ' + url for url in urls]
        return urls

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python BATCH_GET_B23LINK.py <file_path> [mode]")
        sys.exit(1)

    file_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'default'
    urls = extract_urls(file_path, mode)
    for url in urls:
        print(url)
