#!/bin/bash

# 运行 BBDown 并保存输出到变量中
output=$(BBDown "$1")

# 使用正则表达式从输出中提取 AID 和 文件名
aid=$(echo "$output" | grep -oP "获取aid结束: \K\d+")
filename=$(echo "$output" | grep -oP "视频标题: \K.+")

# 检查是否成功获取 AID 和 文件名
if [[ -z "$aid" ]]; then
    echo "无法获取 AID。"
    exit 1
fi

if [[ -z "$filename" ]]; then
    echo "无法获取 文件名。"
    exit 1
fi

# 输出获取到的 AID 和 文件名
echo "AID: $aid"
echo "文件名: $filename.mp4"

# 运行 Upload_to_Youtube.py
python Upload_to_Youtube.py -f "$filename.mp4" -d "转载自哔哩哔哩，原视频ID为$aid" 
