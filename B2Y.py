import subprocess
import re
import sys

def get_aid_and_filename(cmd_args):
    cmd = ["BBDown.exe"]
    cmd.extend(cmd_args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    
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

def upload_video(filename, aid):
    upload_cmd = [
        "python", "Upload_to_Youtube.py",
        "-f", filename,
        "-d", f"转载自哔哩哔哩，原视频ID为{aid}"
    ]
    subprocess.run(upload_cmd)

# 获取命令行参数
cmd_args = sys.argv[1:]

# 获取AID和文件名
aid, filename = get_aid_and_filename(cmd_args)

if aid and filename:
    print(f"AID: {aid}")
    print(f"文件名: {filename}")
    
    # 执行上传操作
    upload_video(filename, aid)
else:
    print("无法获取AID或文件名。")
