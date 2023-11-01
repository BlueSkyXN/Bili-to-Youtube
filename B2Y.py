import subprocess
import re

def get_aid_and_filename(url):
    # 运行BBDown.exe并捕获输出
    result = subprocess.run(["BBDown.exe", url], capture_output=True, text=True)
    
    # 提取AID和文件名
    aid_pattern = r"获取aid结束: (\d+)"
    filename_pattern = r"视频标题: (.+)"
    
    aid_match = re.search(aid_pattern, result.stdout)
    filename_match = re.search(filename_pattern, result.stdout)
    
    if aid_match and filename_match:
        aid = aid_match.group(1)
        filename = filename_match.group(1) + ".mp4"
        return aid, filename
    else:
        return None, None

# 使用示例
url = "https://www.bilibili.com/video/BV1kj411a7w9/"
aid, filename = get_aid_and_filename(url)
print(f"AID: {aid}")
print(f"文件名: {filename}")
