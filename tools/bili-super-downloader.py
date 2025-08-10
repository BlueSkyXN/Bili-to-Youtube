#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili 超级下载器 - 融合版本
结合 bup-scan-xlsx-bbdown-v3.py 和 bili-down-batch.py 的所有功能

功能特点:
- 完全兼容原有两个程序的所有功能
- 使用YAML配置文件管理
- 支持单用户(single)、批量(batch)两种模式
- 灵活的时间范围控制
- 多种数据存储格式
- 智能下载管理
- 完善的错误处理和日志系统
"""

import os
import sys
import logging
import time
import random
import argparse
import traceback
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field, asdict
from hashlib import md5
from functools import reduce
import concurrent.futures
import subprocess
# 简化版本：移除不必要的导入

# 第三方库导入
try:
    import yaml
    import pandas as pd
    import requests
    import urllib.parse
    from send2trash import send2trash
except ImportError as e:
    print(f"缺少必要的依赖库: {e}")
    print("请运行: pip install pyyaml pandas requests send2trash")
    sys.exit(1)

# 忽略SSL警告
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# =============================================================================
# 数据结构定义 (Data Structures)
# =============================================================================

@dataclass
class VideoInfo:
    """视频信息数据类 - 融合两个版本的字段"""
    # 基础字段 (v3版本兼容)
    bvid: str
    aid: int
    title: str
    description: str = ""
    author: str = ""
    mid: str = ""
    created: Union[int, str] = ""
    length: str = ""
    pic: str = ""
    
    # 统计字段 (v3版本兼容)
    play: int = 0  # 播放量
    comment: int = 0  # 评论数
    video_review: int = 0  # 弹幕数
    
    # 扩展字段
    tags: List[str] = field(default_factory=list)
    duration: int = 0  # 时长(秒)
    view_count: int = 0  # 观看数
    like_count: int = 0  # 点赞数
    coin_count: int = 0  # 硬币数
    favorite_count: int = 0  # 收藏数
    share_count: int = 0  # 分享数
    
    # 下载状态
    downloaded: bool = False
    download_path: str = ""
    download_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于数据存储"""
        data = asdict(self)
        # 处理特殊字段
        if isinstance(self.created, int):
            data['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.created))
        if self.download_time:
            data['download_time'] = self.download_time.isoformat()
        return data
    
    @classmethod
    def from_api_data(cls, api_data: Dict[str, Any]) -> 'VideoInfo':
        """从API数据创建VideoInfo实例"""
        return cls(
            bvid=api_data.get('bvid', ''),
            aid=api_data.get('aid', 0),
            title=api_data.get('title', ''),
            description=api_data.get('description', ''),
            author=api_data.get('author', ''),
            mid=str(api_data.get('mid', '')),
            created=api_data.get('created', 0),
            length=api_data.get('length', ''),
            pic=api_data.get('pic', ''),
            play=api_data.get('play', 0),
            comment=api_data.get('comment', 0),
            video_review=api_data.get('video_review', 0)
        )

@dataclass 
class UpInfo:
    """UP主信息数据类 - 简化版本，只保留必要字段"""
    name: str  # UP主名字 (用于文件夹名)
    mid: str   # UP主ID
    enabled: bool = True
    priority: int = 1
    # 运行时状态字段
    last_update: Optional[datetime] = None
    video_count: int = 0
    download_count: int = 0
    
    def get_folder_name(self, use_date: bool = False) -> str:
        """获取文件夹名称 - 简化版本"""
        base_name = f"Bili-{self.name}"  # 直接使用配置中的name
        if use_date:
            today = datetime.now().strftime('%Y%m%d')
            base_name += f"-{today}"
        return base_name

@dataclass
class TimeRange:
    """时间范围控制类 - 扩展batch版本"""
    start_time: int  # 起始时间戳
    end_time: int    # 结束时间戳
    mode: str = "days"  # 模式: days, hours, date_range, timestamp
    
    @classmethod
    def from_days(cls, days: int) -> 'TimeRange':
        """从最近的天数创建时间范围"""
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=days))
                        .replace(hour=0, minute=0, second=0).timestamp())
        return cls(start_time=start_time, end_time=end_time, mode="days")
    
    @classmethod
    def from_hours(cls, hours: int) -> 'TimeRange':
        """从最近的小时数创建时间范围"""
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(hours=hours)).timestamp())
        return cls(start_time=start_time, end_time=end_time, mode="hours")
    
    @classmethod
    def from_date_range(cls, start_date: Union[str, datetime], 
                       end_date: Optional[Union[str, datetime]] = None) -> 'TimeRange':
        """从日期范围创建时间范围"""
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        start_time = int(start_date.replace(hour=0, minute=0, second=0).timestamp())
        
        if end_date is None:
            end_time = int(datetime.now().timestamp())
        else:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_time = int(end_date.replace(hour=23, minute=59, second=59).timestamp())
            
        return cls(start_time=start_time, end_time=end_time, mode="date_range")
    
    @classmethod
    def from_timestamp(cls, start_timestamp: int, 
                      end_timestamp: Optional[int] = None) -> 'TimeRange':
        """从时间戳创建时间范围"""
        end_time = end_timestamp if end_timestamp is not None else int(datetime.now().timestamp())
        return cls(start_time=start_timestamp, end_time=end_time, mode="timestamp")
    
    @classmethod  
    def from_start_date(cls, start_date: str) -> 'TimeRange':
        """从开始日期创建时间范围 (兼容v3版本的START_DATE)"""
        if not start_date:
            # 如果没有指定开始日期，返回一个很早的时间
            return cls(start_time=0, end_time=int(datetime.now().timestamp()), mode="incremental")
        return cls.from_date_range(start_date)
    
    def is_in_range(self, timestamp: int) -> bool:
        """检查时间戳是否在范围内"""
        return self.start_time <= timestamp <= self.end_time
    
    def __str__(self) -> str:
        start_str = datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')
        end_str = datetime.fromtimestamp(self.end_time).strftime('%Y-%m-%d %H:%M:%S')
        return f"TimeRange({self.mode}: {start_str} -> {end_str})"

# =============================================================================
# 配置管理器 (Configuration Manager)
# =============================================================================

class BiliConfig:
    """配置管理器 - 处理YAML配置和命令行参数"""
    
    def __init__(self, config_path: str = "bili-config.yaml"):
        self.config_path = config_path
        self.config = {}
        self.actual_config_path = None
        self.load_config()
    
    def find_config_file(self, config_filename: str) -> Optional[str]:
        """
        智能查找配置文件
        1. 优先检查当前工作目录
        2. 其次检查程序文件所在目录
        3. 都没有则返回None
        """
        # 1. 检查当前工作目录
        current_dir_config = os.path.join(os.getcwd(), config_filename)
        if os.path.exists(current_dir_config):
            return current_dir_config
        
        # 2. 检查程序文件所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_dir_config = os.path.join(script_dir, config_filename)
        if os.path.exists(script_dir_config):
            return script_dir_config
        
        # 3. 都没找到
        return None
    
    def validate_required_config(self) -> bool:
        """验证必填配置项"""
        required_checks = []
        
        # 检查Cookie（必填）
        cookie = self.get('auth.cookie', '')
        if not cookie or cookie.strip() == '':
            required_checks.append("auth.cookie (B站Cookie)")
        
        # 检查模式配置
        mode = self.get('base.mode', '')
        if mode not in ['single', 'batch']:
            required_checks.append("base.mode (必须是 'single' 或 'batch')")
        
        # 根据模式检查特定配置
        if mode == 'single':
            single_mid = self.get('uploader.single_mid', '')
            if not single_mid or single_mid.strip() == '':
                required_checks.append("uploader.single_mid (single模式需要UP主ID)")
        elif mode == 'batch':
            batch_list = self.get('uploader.batch_list', {})
            if not batch_list or len(batch_list) == 0:
                required_checks.append("uploader.batch_list (batch模式需要UP主列表)")
        
        # 检查下载目录
        download_dir = self.get('base.download_dir', '')
        if not download_dir or download_dir.strip() == '':
            required_checks.append("base.download_dir (下载目录)")
        
        if required_checks:
            print("\n❌ 配置文件验证失败，缺少以下必填参数：")
            for item in required_checks:
                print(f"  - {item}")
            print("\n请检查配置文件并补充必填参数。")
            return False
        
        return True
    
    def load_config(self):
        """加载配置文件"""
        try:
            # 如果提供的是绝对路径，直接使用
            if os.path.isabs(self.config_path):
                if os.path.exists(self.config_path):
                    self.actual_config_path = self.config_path
                else:
                    self._handle_config_not_found()
                    return
            else:
                # 智能查找配置文件
                found_config = self.find_config_file(self.config_path)
                if found_config:
                    self.actual_config_path = found_config
                else:
                    self._handle_config_not_found()
                    return
            
            # 加载配置文件
            with open(self.actual_config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            
            print(f"✅ 配置文件加载成功: {self.actual_config_path}")
            
            # 验证必填参数
            if not self.validate_required_config():
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            sys.exit(1)
    
    def _handle_config_not_found(self):
        """处理配置文件未找到的情况"""
        print(f"❌ 配置文件未找到: {self.config_path}")
        print("\n已检查以下位置:")
        print(f"  1. 当前工作目录: {os.path.join(os.getcwd(), self.config_path)}")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"  2. 程序所在目录: {os.path.join(script_dir, self.config_path)}")
        
        print(f"\n解决方案:")
        print(f"  1. 在当前目录创建配置文件: {self.config_path}")
        print(f"  2. 使用 --generate-config 生成默认配置文件")
        print(f"  3. 使用 --config 参数指定配置文件路径")
        
        sys.exit(1)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'base': {
                'mode': 'batch',
                'data_dir': './data',
                'download_dir': './downloads',
                'excel_file_path': './data/bilibili_videos.xlsx',
                'log_level': 'INFO'
            },
            'auth': {
                'cookie': ''
            },
            'uploader': {
                'single_mid': '23318408',
                'batch_list': {
                    '示例UP主': '23318408'
                }
            },
            'time': {
                'start_date': '',
                'batch_time_range': '7'
            },
            'download': {
                'enabled': True,
                'check_downloaded': True,
                'max_workers': 1,
                'clean_subfolders': True,
                'clean_temp_files': True
            },
            'network': {
                'use_random_ua': True,
                'delay': 0.5,
                'max_pages': 100,
                'page_size': 50,
                'timeout': 10,
                'verify_ssl': False
            },
            'data': {
                'format': 'excel',
                'sheet_name': 'Videos',
                'include_index': False
            }
        }
    
    def get(self, key_path: str, default=None):
        """使用点号分隔的路径获取配置值"""
        keys = key_path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value):
        """使用点号分隔的路径设置配置值"""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
    
    def update_from_args(self, args: argparse.Namespace):
        """从命令行参数更新配置"""
        # 兼容v3版本的参数映射
        arg_mapping = {
            'excel_file_path': 'base.excel_file_path',
            'download_dir': 'base.download_dir',
            'mid': 'uploader.single_mid',
            'delay': 'network.delay',
            'max_pages': 'network.max_pages',
            'max_workers': 'download.max_workers',
            'check_downloaded': 'download.check_downloaded',
            'use_random_ua': 'network.use_random_ua',
            'clean_subfolders': 'download.clean_subfolders',
            'download_switch': 'download.enabled',
            'start_date': 'time.start_date'
        }
        
        for arg_name, config_path in arg_mapping.items():
            arg_value = getattr(args, arg_name, None)
            if arg_value is not None:
                self.set(config_path, arg_value)
                logging.info(f"命令行参数覆盖配置: {config_path} = {arg_value}")
    
    def get_time_range(self) -> TimeRange:
        """根据配置获取时间范围"""
        mode = self.get('base.mode', 'single')
        
        if mode == 'single':
            # 单用户模式：使用START_DATE (v3版本逻辑)
            start_date = self.get('time.start_date', '')
            if start_date:
                return TimeRange.from_start_date(start_date)
            else:
                # 没有指定日期，获取所有
                return TimeRange(start_time=0, end_time=int(datetime.now().timestamp()), mode="incremental")
        else:
            # 批量模式：使用时间范围 (batch版本逻辑)
            days = int(self.get('time.batch_time_range', 7))
            return TimeRange.from_days(days)
    
    def get_up_list(self) -> List[UpInfo]:
        """获取UP主列表"""
        mode = self.get('base.mode', 'single')
        up_list = []
        
        if mode == 'single':
            # 单用户模式配置
            single_mid = str(self.get('uploader.single_mid', ''))
            if single_mid:
                up_info = UpInfo(
                    name=f"UP-{single_mid}",  # 文件夹: Bili-UP-{ID}
                    mid=single_mid,
                    enabled=True,
                    priority=1
                )
                up_list.append(up_info)
        
        if mode == 'batch':
            # 批量模式配置 - 字典格式
            batch_dict = self.get('uploader.batch_list', {})
            for name, mid in batch_dict.items():
                if name and mid:
                    up_info = UpInfo(
                        name=name,  # 文件夹: Bili-{name}
                        mid=str(mid),
                        enabled=True,
                        priority=1
                    )
                    up_list.append(up_info)
        
        return up_list
    
    def save_config(self, path: Optional[str] = None):
        """保存配置到文件"""
        save_path = path or self.config_path
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            logging.info(f"配置已保存到: {save_path}")
        except Exception as e:
            logging.error(f"保存配置失败: {e}")

# =============================================================================
# 网络管理器 (Network Manager)
# =============================================================================

class NetworkManager:
    """网络请求管理器 - 封装WBI签名和API请求"""
    
    def __init__(self, config: BiliConfig):
        self.config = config
        self.cookie = config.get('auth.cookie', '')
        self.session = requests.Session()
        self.session.verify = config.get('network.verify_ssl', False)
        
        # 设置默认请求头
        self.session.headers.update({
            'User-Agent': self._get_user_agent(),
            'Referer': 'https://space.bilibili.com/',
            'Cookie': self.cookie
        })
    
    def _get_user_agent(self) -> str:
        """获取User-Agent"""
        if self.config.get('network.use_random_ua', True):
            random_digit = random.randint(0, 999)
            return f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.{random_digit} Safari/537.36'
        else:
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    
    def get_wbi_keys(self) -> tuple:
        """获取WBI签名密钥"""
        try:
            resp = self.session.get(
                'https://api.bilibili.com/x/web-interface/nav',
                timeout=self.config.get('network.timeout', 10)
            )
            resp.raise_for_status()
            data = resp.json()['data']['wbi_img']
            img_key = data['img_url'].rsplit('/', 1)[1].split('.')[0]
            sub_key = data['sub_url'].rsplit('/', 1)[1].split('.')[0]
            return img_key, sub_key
        except Exception as e:
            logging.error(f"获取WBI密钥失败: {e}")
            return None, None
    
    def get_mixin_key(self, orig: str) -> str:
        """混合WBI密钥"""
        MIXIN_KEY_ENC_TAB = [
            46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3,
            45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39,
            12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17,
            0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63,
            57, 62, 11, 36, 20, 34, 44, 52
        ]
        return reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, '')[:32]
    
    def enc_wbi(self, params: dict, img_key: str, sub_key: str) -> dict:
        """WBI签名"""
        mixin_key = self.get_mixin_key(img_key + sub_key)
        curr_time = round(time.time())
        params['wts'] = curr_time
        params = dict(sorted(params.items()))
        params = {k: ''.join(filter(lambda chr: chr not in "!'()*", str(v))) 
                 for k, v in params.items()}
        query = urllib.parse.urlencode(params)
        wbi_sign = md5((query + mixin_key).encode()).hexdigest()
        params['w_rid'] = wbi_sign
        return params
    
    def request_with_retry(self, url: str, params: dict = None, max_retries: int = 3) -> requests.Response:
        """带重试机制的请求"""
        for attempt in range(max_retries):
            try:
                delay = self.config.get('network.delay', 0.5)
                if attempt > 0:
                    delay *= (attempt + 1)  # 指数退避
                time.sleep(delay)
                
                response = self.session.get(
                    url, 
                    params=params,
                    timeout=self.config.get('network.timeout', 10)
                )
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logging.warning(f"请求失败，第{attempt + 1}次重试: {e}")
        
        raise Exception("达到最大重试次数")

# =============================================================================
# 数据管理器 (Data Manager)
# =============================================================================

class DataManager:
    """数据存储管理器 - 支持多种数据格式"""
    
    def __init__(self, config: BiliConfig):
        self.config = config
        self.data_dir = Path(config.get('base.data_dir', './data'))
        # 对标原版：不在初始化时创建目录，只在需要时创建
        
        self.primary_format = config.get('data.format', 'excel')
        # 备份格式暂时移除，保持简化
        
    def save_videos(self, videos: List[VideoInfo], up_info = None, up_name: str = "default") -> bool:
        """保存视频数据 - 支持按UP主分表"""
        try:
            # 转换为字典格式
            video_data = [video.to_dict() for video in videos]
            
            # 如果提供了UP主信息且开启分表，使用UP主信息
            if up_info and self.config.get('data.split_by_uploader', False):
                success = self._save_primary_format(video_data, up_info.name, up_info.mid)
            else:
                # 兼容原有调用方式
                success = self._save_primary_format(video_data, up_name)
            
            return success
        except Exception as e:
            logging.error(f"保存视频数据失败: {e}")
            return False
    
    def _save_primary_format(self, video_data: List[Dict], up_name: str, up_mid: str = None) -> bool:
        """保存主要格式 - 支持按UP主分表"""
        if self.primary_format == 'excel':
            return self._save_excel(video_data, up_name, up_mid)
        elif self.primary_format == 'json':
            return self._save_json(video_data, up_name, up_mid)
        elif self.primary_format == 'csv':
            return self._save_csv(video_data, up_name, up_mid)
        else:
            logging.error(f"不支持的主要格式: {self.primary_format}")
            return False
    
    # 简化版本：移除备份格式功能
    
    def _save_excel(self, video_data: List[Dict], up_name: str, up_mid: str = None, is_backup: bool = False) -> bool:
        """保存Excel格式"""
        try:
            # 按UP主分表或兼容v3版本的Excel文件路径
            if not is_backup and self.config.get('base.mode') == 'single':
                # 检查是否启用分表功能
                if self.config.get('data.split_by_uploader', False) and up_mid:
                    # 使用分表模式
                    file_path = self._get_file_path('excel', up_name, up_mid, is_backup)
                else:
                    # 兼容v3版本的固定路径
                    excel_path = self.config.get('base.excel_file_path')
                    if excel_path:
                        file_path = Path(excel_path)
                    else:
                        file_path = self._get_file_path('excel', up_name, up_mid, is_backup)
            else:
                file_path = self._get_file_path('excel', up_name, up_mid, is_backup)
            
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取现有数据（如果存在）
            existing_data = []
            if file_path.exists():
                try:
                    existing_df = pd.read_excel(file_path)
                    existing_data = existing_df.to_dict('records')
                except Exception as e:
                    logging.warning(f"读取现有Excel文件失败: {e}")
            
            # 合并数据并去重
            all_data = existing_data + video_data
            df = pd.DataFrame(all_data)
            
            if not df.empty and 'bvid' in df.columns:
                # 按bvid去重，保留最新的数据
                df = df.drop_duplicates(subset=['bvid'], keep='last')
            
            # 保存到Excel
            sheet_name = self.config.get('data.sheet_name', 'Videos')
            include_index = self.config.get('data.include_index', False)
            
            df.to_excel(file_path, sheet_name=sheet_name, index=include_index)
            logging.info(f"Excel数据已保存: {file_path}")
            return True
            
        except Exception as e:
            logging.error(f"保存Excel文件失败: {e}")
            return False
    
    def _save_json(self, video_data: List[Dict], up_name: str, up_mid: str = None, is_backup: bool = False) -> bool:
        """保存JSON格式"""
        try:
            file_path = self._get_file_path('json', up_name, up_mid, is_backup)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取现有数据
            existing_data = []
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except Exception as e:
                    logging.warning(f"读取现有JSON文件失败: {e}")
            
            # 合并数据并去重
            all_data = existing_data + video_data
            # 按bvid去重
            unique_data = {}
            for video in all_data:
                unique_data[video.get('bvid')] = video
            final_data = list(unique_data.values())
            
            # 保存JSON - 简化配置
            pretty_print = True
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if pretty_print:
                    json.dump(final_data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(final_data, f, ensure_ascii=False)
            
            logging.info(f"JSON数据已保存: {file_path}")
            return True
            
        except Exception as e:
            logging.error(f"保存JSON文件失败: {e}")
            return False
    
    def _save_csv(self, video_data: List[Dict], up_name: str, up_mid: str = None, is_backup: bool = False) -> bool:
        """保存CSV格式"""
        try:
            file_path = self._get_file_path('csv', up_name, up_mid, is_backup)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            df = pd.DataFrame(video_data)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            logging.info(f"CSV数据已保存: {file_path}")
            return True
            
        except Exception as e:
            logging.error(f"保存CSV文件失败: {e}")
            return False
    
    def _get_file_path(self, format_type: str, up_name: str, up_mid: str = None, is_backup: bool = False) -> Path:
        """获取文件路径 - 支持按UP主分表"""
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 检查是否启用按UP主分表
        if self.config.get('data.split_by_uploader', False) and up_mid:
            # 使用配置的分表文件命名模式
            pattern = self.config.get('data.excel_pattern', 'bilibili_videos_{mid}_{date}.xlsx')
            if format_type == 'json':
                pattern = pattern.replace('.xlsx', '.json')
            elif format_type == 'csv':
                pattern = pattern.replace('.xlsx', '.csv')
            
            filename = pattern.format(mid=up_mid, date=timestamp, uploader=up_name)
            logging.info(f"使用分表模式，UP主{up_name}({up_mid})的数据文件: {filename}")
        else:
            # 原有的统一文件命名模式
            if format_type == 'excel':
                pattern = 'bilibili_videos_{date}.xlsx'
            elif format_type == 'json':
                pattern = 'bilibili_videos_{date}.json'
            else:
                pattern = f'bilibili_videos_{{date}}.{format_type}'
            
            filename = pattern.format(date=timestamp, uploader=up_name)
        
        if is_backup:
            backup_dir = self.data_dir / 'backup'
            backup_dir.mkdir(exist_ok=True)
            return backup_dir / filename
        else:
            return self.data_dir / filename

# =============================================================================
# 下载管理器 (Download Manager)
# =============================================================================

class DownloadManager:
    """下载管理器 - 处理视频下载逻辑"""
    
    def __init__(self, config: BiliConfig):
        self.config = config
        self.base_dir = Path(config.get('base.download_dir', './downloads'))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_workers = config.get('download.max_workers', 1)
        self.check_downloaded = config.get('download.check_downloaded', True)
        self.use_date_folder = False  # 简化：不使用日期文件夹
        
    def get_up_folder(self, up: UpInfo) -> Path:
        """获取UP主的下载文件夹路径"""
        folder_name = up.get_folder_name(self.use_date_folder)
        folder_path = self.base_dir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path
    
    def clean_folder(self, folder: Path):
        """清理文件夹 - Windows兼容版本"""
        try:
            folder = folder.resolve()  # 标准化路径
            
            # 清理子文件夹
            if self.config.get('download.clean_subfolders', True):
                for item in folder.iterdir():
                    if item.is_dir():
                        try:
                            # Windows兼容性：检查路径访问权限
                            if item.exists():
                                # 在Windows下，尝试访问权限检查
                                try:
                                    os.access(item, os.W_OK)
                                    send2trash(str(item))
                                    logging.info(f"清理子文件夹: {item}")
                                except (OSError, PermissionError):
                                    logging.warning(f"无权限清理子文件夹: {item}, 跳过")
                        except Exception as e:
                            logging.error(f"清理子文件夹失败: {item}, 错误: {e}")
            
            # 清理临时文件
            if self.config.get('download.clean_temp_files', True):
                temp_patterns = ['*.download', '*.part', '*.tmp', '*.temp']
                for pattern in temp_patterns:
                    try:
                        for file_path in folder.glob(pattern):
                            try:
                                if file_path.exists():
                                    # Windows兼容性：先尝试访问
                                    try:
                                        os.access(file_path, os.W_OK)
                                        send2trash(str(file_path))
                                        logging.info(f"清理临时文件: {file_path}")
                                    except (OSError, PermissionError):
                                        logging.warning(f"无权限清理临时文件: {file_path}, 跳过")
                            except Exception as e:
                                logging.error(f"清理临时文件失败: {file_path}, 错误: {e}")
                    except Exception as e:
                        logging.error(f"匹配临时文件模式失败: {pattern}, 错误: {e}")
                            
        except Exception as e:
            logging.error(f"清理文件夹失败: {folder}, 错误: {e}")
    
    def is_video_downloaded(self, folder: Path, bvid: str) -> bool:
        """检查视频是否已下载"""
        if not self.check_downloaded:
            return False
            
        try:
            for file_path in folder.iterdir():
                if file_path.is_file() and bvid in file_path.name:
                    # 排除临时文件
                    if not file_path.suffix in ['.download', '.part', '.tmp', '.temp']:
                        # 检查文件大小
                        if file_path.stat().st_size > 0:
                            return True
            return False
        except Exception as e:
            logging.error(f"检查下载状态失败: {e}")
            return False
    
    def download_video(self, video: VideoInfo, folder: Path) -> bool:
        """下载单个视频"""
        if self.is_video_downloaded(folder, video.bvid):
            logging.info(f"视频已存在，跳过下载: {video.title}")
            return True
        
        try:
            # 构建bbdown命令 - 根据模式对标原版
            mode = self.config.get('base.mode', 'batch')
            ua = self._get_user_agent()
            
            if mode == 'single':
                # 对标v3版本：不使用work-dir，需要切换工作目录
                command = ['bbdown', '-ua', ua, video.bvid]
                
                # 保存当前目录，切换到下载目录（对标v3版本行为）
                original_cwd = os.getcwd()
                try:
                    os.chdir(str(folder))
                    logging.info(f"开始下载: {video.title}")
                    logging.debug(f"下载命令: {' '.join(command)}")
                    
                    # 执行下载
                    subprocess.run(
                        command, 
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=3600  # 1小时超时
                    )
                finally:
                    # 恢复原工作目录
                    os.chdir(original_cwd)
            else:
                # 对标batch版本：使用work-dir参数
                command = ['bbdown', '--work-dir', str(folder), '-ua', ua, video.bvid]
                
                logging.info(f"开始下载: {video.title}")
                logging.debug(f"下载命令: {' '.join(command)}")
                
                # 执行下载
                subprocess.run(
                    command, 
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1小时超时
                )
            
            logging.info(f"下载成功: {video.title}")
            
            # 更新视频状态
            video.downloaded = True
            video.download_path = str(folder)
            video.download_time = datetime.now()
            
            return True
            
        except subprocess.CalledProcessError as e:
            logging.error(f"下载失败: {video.title}")
            logging.error(f"错误输出: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            logging.error(f"下载超时: {video.title}")
            return False
        except Exception as e:
            logging.error(f"下载异常: {video.title}, 错误: {e}")
            return False
    
    def _get_user_agent(self) -> str:
        """获取User-Agent"""
        if self.config.get('network.use_random_ua', True):
            random_digit = random.randint(0, 999)
            return f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.{random_digit} Safari/537.36'
        else:
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    
    def download_videos_batch(self, videos: List[VideoInfo], folder: Path) -> Dict[str, int]:
        """批量下载视频"""
        if not videos:
            return {'total': 0, 'success': 0, 'skipped': 0, 'failed': 0}
        
        # 过滤需要下载的视频
        videos_to_download = [v for v in videos if not self.is_video_downloaded(folder, v.bvid)]
        
        stats = {
            'total': len(videos),
            'success': 0,
            'skipped': len(videos) - len(videos_to_download),
            'failed': 0
        }
        
        if not videos_to_download:
            logging.info("所有视频均已下载，无需下载")
            return stats
        
        logging.info(f"开始批量下载，共 {len(videos_to_download)} 个视频")
        
        # 使用线程池下载
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_video = {
                executor.submit(self.download_video, video, folder): video 
                for video in videos_to_download
            }
            
            for future in concurrent.futures.as_completed(future_to_video):
                video = future_to_video[future]
                try:
                    if future.result():
                        stats['success'] += 1
                    else:
                        stats['failed'] += 1
                except Exception as e:
                    logging.error(f"下载任务异常: {video.title}, 错误: {e}")
                    stats['failed'] += 1
        
        logging.info(f"批量下载完成: 成功 {stats['success']}, 跳过 {stats['skipped']}, 失败 {stats['failed']}")
        return stats

# =============================================================================
# 主下载器类 (Main Downloader Class)
# =============================================================================

class BiliSuperDownloader:
    """Bilibili 超级下载器 - 主要下载器类"""
    
    def __init__(self, config_path: str = "bili-config.yaml"):
        """初始化下载器"""
        # 加载配置
        self.config = BiliConfig(config_path)
        
        # 设置日志
        self._setup_logging()
        
        # 初始化管理器
        self.network_manager = NetworkManager(self.config)
        self.download_manager = DownloadManager(self.config)
        
        # 数据管理器只在single模式下初始化（对标v3版本）
        mode = self.config.get('base.mode', 'batch')
        if mode == 'single':
            self.data_manager = DataManager(self.config)
        else:
            self.data_manager = None
        
        # 获取时间范围和UP主列表
        self.time_range = self.config.get_time_range()
        self.up_list = self.config.get_up_list()
        
        logging.info(f"超级下载器初始化完成")
        logging.info(f"工作模式: {self.config.get('base.mode')}")
        logging.info(f"时间范围: {self.time_range}")
        logging.info(f"UP主数量: {len(self.up_list)}")
    
    def _setup_logging(self):
        """设置日志"""
        log_level = self.config.get('base.log_level', 'INFO')
        log_file = self.config.get('base.log_file')
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        root_logger.handlers.clear()
        root_logger.addHandler(console_handler)
        
        # 文件输出（如果配置了）
        if log_file:
            try:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_path, encoding='utf-8')
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
                logging.info(f"日志文件: {log_path}")
            except Exception as e:
                logging.warning(f"设置日志文件失败: {e}")
    
    def get_new_videos(self, up: UpInfo) -> List[VideoInfo]:
        """获取UP主的新视频列表"""
        # 获取WBI密钥
        img_key, sub_key = self.network_manager.get_wbi_keys()
        if not img_key or not sub_key:
            raise Exception("无法获取WBI密钥")
        
        videos = []
        page = 1
        max_pages = self.config.get('network.max_pages', 100)
        page_size = self.config.get('network.page_size', 50)
        
        logging.info(f"开始获取UP主 {up.name} 的视频列表")
        
        while page <= max_pages:
            try:
                # 构建请求参数
                params = {
                    'mid': up.mid,
                    'ps': str(page_size),
                    'pn': str(page),
                    'order': 'pubdate',
                    'platform': 'web',
                    'web_location': '1550101',
                    'order_avoided': 'true'
                }
                
                # 签名参数
                signed_params = self.network_manager.enc_wbi(params, img_key, sub_key)
                url = 'https://api.bilibili.com/x/space/wbi/arc/search?' + \
                      urllib.parse.urlencode(signed_params)
                
                # 发送请求
                response = self.network_manager.request_with_retry(url)
                data = response.json()
                
                # 检查响应
                if data.get('code') != 0:
                    logging.error(f"API返回错误: {data.get('message', '未知错误')}")
                    break
                
                vlist = data.get('data', {}).get('list', {}).get('vlist', [])
                if not vlist:
                    logging.info(f"第{page}页无更多视频，停止获取")
                    break
                
                # 处理视频列表
                page_videos = 0
                for video_data in vlist:
                    # 检查时间范围
                    if self.time_range.is_in_range(video_data['created']):
                        video = VideoInfo.from_api_data(video_data)
                        videos.append(video)
                        page_videos += 1
                    elif video_data['created'] < self.time_range.start_time:
                        # 发现更早的视频，停止获取
                        logging.info(f"发现超出时间范围的视频，停止获取")
                        return videos
                
                logging.info(f"第{page}页获取到 {page_videos} 个符合条件的视频")
                page += 1
                
                # 请求间隔
                delay = self.config.get('network.delay', 0.5)
                time.sleep(delay)
                
            except Exception as e:
                logging.error(f"获取第{page}页视频失败: {e}")
                break
        
        logging.info(f"UP主 {up.name} 共获取到 {len(videos)} 个新视频")
        return videos
    
    def process_single_up(self, up: UpInfo) -> Dict[str, Any]:
        """处理单个UP主"""
        logging.info(f"===== 开始处理 UP主: {up.name} ({up.mid}) =====")
        
        result = {
            'up_name': up.name,
            'up_mid': up.mid,
            'success': False,
            'videos_found': 0,
            'videos_downloaded': 0,
            'videos_skipped': 0,
            'videos_failed': 0,
            'error': None
        }
        
        try:
            # 获取下载文件夹
            download_folder = self.download_manager.get_up_folder(up)
            logging.info(f"下载目录: {download_folder}")
            
            # 清理文件夹
            self.download_manager.clean_folder(download_folder)
            
            # 获取新视频
            videos = self.get_new_videos(up)
            result['videos_found'] = len(videos)
            
            if not videos:
                logging.info(f"UP主 {up.name} 没有新视频")
                result['success'] = True
                return result
            
            # 保存视频数据（只在single模式下，对标v3版本）
            if self.data_manager and self.config.get('data.format'):
                self.data_manager.save_videos(videos, up_info=up, up_name=up.name)
            
            # 下载视频（如果启用了下载）
            if self.config.get('download.enabled', True):
                download_stats = self.download_manager.download_videos_batch(
                    videos, download_folder
                )
                result.update({
                    'videos_downloaded': download_stats['success'],
                    'videos_skipped': download_stats['skipped'],
                    'videos_failed': download_stats['failed']
                })
            else:
                logging.info("下载功能已禁用，仅保存视频信息")
                result['videos_skipped'] = len(videos)
            
            # 更新UP主信息
            up.last_update = datetime.now()
            up.video_count = len(videos)
            up.download_count = result['videos_downloaded']
            
            result['success'] = True
            logging.info(f"UP主 {up.name} 处理完成")
            
        except Exception as e:
            error_msg = f"处理UP主 {up.name} 失败: {e}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            result['error'] = str(e)
            
        finally:
            logging.info(f"===== UP主 {up.name} 处理结束 =====\n")
            
        return result
    
    def run_single_mode(self) -> Dict[str, Any]:
        """运行单用户模式（完全兼容v3版本）"""
        logging.info("运行单用户模式")
        
        # 直接使用single_mid，完全对标v3版本逻辑
        single_mid = str(self.config.get('uploader.single_mid', ''))
        if not single_mid:
            raise ValueError("single模式需要配置uploader.single_mid")
        
        # 创建UP主信息，文件夹命名对标v3版本（直接使用MID）
        single_up = UpInfo(
            name=f"UP-{single_mid}",  # 对标v3版本的文件夹命名
            mid=single_mid,
            enabled=True,
            priority=1
        )
        
        return self.process_single_up(single_up)
    
    def run_batch_mode(self) -> List[Dict[str, Any]]:
        """运行批量模式（兼容batch版本）"""
        logging.info("运行批量模式")
        
        results = []
        enabled_ups = [up for up in self.up_list if up.enabled]
        
        logging.info(f"共有 {len(enabled_ups)} 个启用的UP主")
        
        # 串行处理UP主（避免并发请求过多）
        for i, up in enumerate(enabled_ups, 1):
            logging.info(f"处理进度: {i}/{len(enabled_ups)}")
            result = self.process_single_up(up)
            results.append(result)
            
            # UP主间的延迟
            if i < len(enabled_ups):
                delay = self.config.get('network.delay', 0.5) * 2
                time.sleep(delay)
        
        return results
    
    # hybrid模式已移除，现在只支持single和batch两种模式
    
    def run(self) -> Dict[str, Any]:
        """运行下载器"""
        mode = self.config.get('base.mode', 'batch')
        logging.info(f"启动Bilibili超级下载器，模式: {mode}")
        
        start_time = datetime.now()
        
        try:
            if mode == 'single':
                results = self.run_single_mode()
            elif mode == 'batch':
                results = self.run_batch_mode()
            # hybrid模式已移除
            else:
                raise ValueError(f"不支持的模式: {mode}")
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            logging.info(f"下载器运行完成，耗时: {duration}")
            
            return {
                'success': True,
                'mode': mode,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration': str(duration),
                'results': results
            }
            
        except Exception as e:
            error_msg = f"下载器运行失败: {e}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            
            return {
                'success': False,
                'mode': mode,
                'error': str(e),
                'start_time': start_time.isoformat()
            }

# =============================================================================
# 命令行界面 (Command Line Interface)
# =============================================================================

def create_argument_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Bilibili 超级下载器 - 融合版本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 使用默认配置
  python bili-super-downloader-final.py
  
  # 指定配置文件
  python bili-super-downloader-final.py --config custom-config.yaml
  
  # 单用户模式
  python bili-super-downloader-final.py --mode single --mid 23318408
  
  # 批量模式
  python bili-super-downloader-final.py --mode batch
  
  # 仅抓取信息，不下载
  python bili-super-downloader-final.py --no-download
  
  # 指定时间范围
  python bili-super-downloader-final.py --time-range recent  # 最近24小时
  python bili-super-downloader-final.py --start-date 2024-01-01
  
兼容性:
  本程序完全兼容 bup-scan-xlsx-bbdown-v3.py 和 bili-down-batch.py 的参数
        """
    )
    
    # 基础配置参数
    parser.add_argument('--config', '-c', default='bili-config.yaml',
                       help='配置文件路径 (默认: bili-config.yaml)')
    parser.add_argument('--mode', choices=['single', 'batch'],
                       help='运行模式: single(单用户), batch(批量)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别')
    
    # v3版本兼容参数
    parser.add_argument('--excel_file_path', type=str,
                       help='Excel文件保存路径 (兼容v3)')
    parser.add_argument('--download_dir', type=str,
                       help='视频下载目录路径 (兼容v3)')
    parser.add_argument('--mid', type=str,
                       help='Bilibili用户ID (兼容v3)')
    parser.add_argument('--delay', type=float,
                       help='请求间延迟时间(秒) (兼容v3)')
    parser.add_argument('--max_pages', type=int,
                       help='最大抓取页数 (兼容v3)')
    parser.add_argument('--max_workers', type=int,
                       help='多线程下载的最大线程数 (兼容v3)')
    parser.add_argument('--check_downloaded', type=bool,
                       help='是否检查已下载视频 (兼容v3)')
    parser.add_argument('--use_random_ua', type=bool,
                       help='是否启用随机User-Agent (兼容v3)')
    parser.add_argument('--clean_subfolders', type=bool,
                       help='是否清理下载目录中的子文件夹 (兼容v3)')
    parser.add_argument('--download_switch', type=bool,
                       help='是否进行视频下载 (兼容v3)')
    parser.add_argument('--start_date', type=str,
                       help='增量下载的开始日期，格式为YYYY-MM-DD (兼容v3)')
    
    # 新增功能参数
    parser.add_argument('--no-download', action='store_true',
                       help='仅抓取信息，不下载视频')
    parser.add_argument('--time-range', choices=['recent', 'daily', 'weekly', 'monthly'],
                       help='预设时间范围')
    parser.add_argument('--data-format', choices=['excel', 'json', 'csv'],
                       help='数据保存格式')
    parser.add_argument('--clean-only', action='store_true',
                       help='仅清理文件夹，不执行其他操作')
    parser.add_argument('--generate-config', action='store_true',
                       help='生成默认配置文件')
    parser.add_argument('--validate-config', action='store_true',
                       help='验证配置文件')
    
    return parser

def main():
    """主函数"""
    # 解析命令行参数
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        # 生成配置文件
        if args.generate_config:
            # 直接创建默认配置，不进行验证
            temp_config = BiliConfig.__new__(BiliConfig)
            temp_config.config = temp_config._get_default_config()
            temp_config.save_config(args.config)
            print(f"✅ 默认配置文件已生成: {args.config}")
            print("请编辑配置文件并设置必填参数（如Cookie等）后使用。")
            return
        
        # 验证配置文件
        if args.validate_config:
            try:
                config = BiliConfig(args.config)
                print("✅ 配置文件验证通过")
                return
            except SystemExit:
                # 配置验证失败，程序已经显示错误信息并退出
                return
            except Exception as e:
                print(f"❌ 配置文件验证失败: {e}")
                sys.exit(1)
        
        # 创建下载器
        downloader = BiliSuperDownloader(args.config)
        
        # 更新配置
        downloader.config.update_from_args(args)
        
        # 处理特殊参数
        if args.mode:
            downloader.config.set('base.mode', args.mode)
        if args.log_level:
            downloader.config.set('base.log_level', args.log_level)
        if args.no_download:
            downloader.config.set('download.enabled', False)
        if args.time_range:
            downloader.config.set('time.current', args.time_range)
        if args.data_format:
            downloader.config.set('data.storage.primary_format', args.data_format)
        
        # 重新初始化时间范围
        downloader.time_range = downloader.config.get_time_range()
        
        # 仅清理模式
        if args.clean_only:
            logging.info("执行清理模式")
            for up in downloader.up_list:
                if up.enabled:
                    folder = downloader.download_manager.get_up_folder(up)
                    downloader.download_manager.clean_folder(folder)
            logging.info("清理完成")
            return
        
        # 运行下载器
        result = downloader.run()
        
        # 输出结果摘要
        if result['success']:
            print("\n" + "="*50)
            print("下载任务完成")
            print(f"模式: {result['mode']}")
            print(f"耗时: {result['duration']}")
            print("="*50)
        else:
            print(f"\n下载任务失败: {result.get('error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
        print("\n程序已中断")
    except Exception as e:
        logging.error(f"程序运行失败: {e}")
        logging.error(traceback.format_exc())
        print(f"\n程序运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()