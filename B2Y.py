import subprocess
import re
import sys

def get_aid_and_filename(cmd_args):
    # 构造命令行参数列表，首个元素为 "BBDown.exe"
    cmd = ["BBDown.exe"]
    cmd.extend(cmd_args)
    
    # 运行BBDown.exe并捕获输出
    result = subprocess.run(cmd, capture_output=True, text=True)
    
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

# 获取命令行参数
cmd_args = sys.argv[1:]

# 使用示例
aid, filename = get_aid_and_filename(cmd_args)
if aid and filename:
    print(f"AID: {aid}")
    print(f"文件名: {filename}")
else:
    print("无法获取AID或文件名。")
