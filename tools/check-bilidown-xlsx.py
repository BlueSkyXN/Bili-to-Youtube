import os
import pandas as pd

# 预设全局变量
EXCEL_FILE_PATH = 'I:/bin/cache/bilibili_videos.xlsx'
DOWNLOAD_DIR = r"L:\BiliUP-Arch\Cache"

# 检查视频文件是否已存在
def is_video_downloaded(bvid, download_dir):
    for file_name in os.listdir(download_dir):
        if bvid in file_name:
            return True
    return False

def main():
    # 检查是否存在目标的 bilibili_videos.xlsx 文件
    if not os.path.exists(EXCEL_FILE_PATH):
        print(f"文件 {EXCEL_FILE_PATH} 不存在。请确保文件路径正确。")
        return

    # 读取保存的 Excel 文件并获取 bvid 列
    df = pd.read_excel(EXCEL_FILE_PATH)
    bvid_list = df['bvid'].tolist()

    # 初始化计数器
    existing_count = 0
    missing_count = 0
    missing_bvids = []

    # 检测每个 bvid 是否存在于下载目录中
    for bvid in bvid_list:
        if is_video_downloaded(bvid, DOWNLOAD_DIR):
            existing_count += 1
        else:
            missing_count += 1
            missing_bvids.append(bvid)

    # 打印结果
    print(f"已存在的视频文件数量: {existing_count}")
    print(f"不存在的视频文件数量: {missing_count}")
    print(f"不存在的具体BV号: {missing_bvids}")

if __name__ == "__main__":
    main()
