@echo off
setlocal enabledelayedexpansion

:: 运行 BBDown.exe 并将输出重定向到一个临时文件
BBDown.exe %1 > temp.txt

:: 从临时文件中获取 AID 和 文件名
for /f "tokens=2 delims=: " %%a in ('findstr /r "获取aid结束:" temp.txt') do set AID=%%a
for /f "tokens=2 delims=: " %%a in ('findstr /r "视频标题:" temp.txt') do set FILENAME=%%a

:: 检查是否成功获取 AID 和 文件名
if not defined AID (
    echo 无法获取 AID。
    goto end
)

if not defined FILENAME (
    echo 无法获取 文件名。
    goto end
)

:: 输出获取到的 AID 和 文件名
echo AID: !AID!
echo 文件名: !FILENAME!.mp4

:: 运行 Upload_to_Youtube.py
python Upload_to_Youtube.py -f "!FILENAME!.mp4"  -d "转载自哔哩哔哩，原视频ID为!AID!"

:end
:: 删除临时文件
del temp.txt
