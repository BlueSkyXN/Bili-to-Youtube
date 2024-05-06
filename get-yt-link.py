from bs4 import BeautifulSoup

def extract_youtube_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('https://www.youtube.com/watch?v='):
            links.add(href)
    return links

# 加载你的 HTML 文件内容
with open('path_to_your_html_file.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# 调用函数
youtube_links = extract_youtube_links(html_content)

# 输出找到的 YouTube 链接
for link in youtube_links:
    print(link)
