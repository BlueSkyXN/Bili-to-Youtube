# Bili-to-Youtube

B2Y，简化从哔哩哔哩视频下载到上传到Youtube的快速操作

## 目录

- [Bili-to-Youtube](#bili-to-youtube)
- [模块化设计综述](#模块化设计综述)
- [上手流程](#上手流程)
- [Google Youtube API 的配置](#google-youtube-api-的配置)
- [使用限制、提醒和声明](#使用限制提醒和声明)
  - [Youtube 相关](#youtube-相关)
    - [Youtube API 配额问题](#youtube-api-配额问题)
    - [Youtube 安全性限制](#youtube-安全性限制)
    - [Youtube 地区和版权受限问题](#youtube-地区和版权受限问题)
  - [哔哩哔哩 相关](#哔哩哔哩-相关)
    - [哔哩哔哩下载参考项目](#哔哩哔哩下载参考项目)
    - [哔哩哔哩下载分辨率问题](#哔哩哔哩下载分辨率问题)
- [项目目录结构详解](#项目目录结构详解)
  - [目录结构](#目录结构)
  - [核心程序说明](#核心程序说明)
  - [辅助工具详解](#辅助工具详解)

## 模块化设计综述

由于模块化设计，除了哔哩哔哩也可以上传任意来源的视频进行操作，基本上只需要简单的修改即可。

整体模块由哔哩哔哩下载和YouTube上传两部分组成

如果需要使用其他哔哩哔哩下载或者ydl等其他来源或者已经准备好视频的，可直接调用Youtube上传单文件即可。

更多文档请访问 [AI-Review文档](https://github.com/BlueSkyXN/Bili-to-Youtube/tree/main/doc/AI-Review) 对每个文件的解读
以及 [项目文档](https://github.com/BlueSkyXN/Bili-to-Youtube/tree/main/doc) 中提到的包括BBDown和其他相关信息的文档

## 上手流程

1，准备符合条件的Google Youtube API

2，准备认证信息的JSON，来自OAuth生成。

3，准备Python运行环境。

4，微调配置，如果有需求的话。

5，准备好几个可执行文件，包括下载哔哩哔哩视频的BBDown和它需要的ffmpeg

## 运行流程

1，先完成上手流程

2，如果Token失效，则删除运行目录的token文件，会重新通过OAuth认证打开浏览器进行认证和回调

3，微调后（比如S5代理等）运行 B2Y.py，具体参数和BBDown一致

```bash
python B2Y.py  https://www.bilibili.com/video/BV1kj411a7w9/
```

```bash
python B2Y.py  BV1kj411a7w9
```

## Google Youtube API 的配置

请阅读 [YoutubeAPI相关信息](doc/youtube-api.md)

# 使用限制、提醒和声明

## Youtube 相关

### Youtube API 配额问题

根据 [Youtube 官方文档](https://developers.google.com/youtube/v3/getting-started?hl=zh-cn#quota)

默认情况下，分配每日10000的API配额（似乎跟随项目而不是账号）。而根据文档介绍，上传一次需要1600点配额，计算可得每日6个视频。如果要更多配额可向Google申请。因此本程序设计中需要你自行解决API权限和申请。除非谷歌给我特批。

### Youtube 安全性限制

由于Youtube安全检测的问题，API上传的视频可能不可直接公开可用，尤其是发送TEST视频的时候。

参考提示如下

```text
我们的团队已经审查了您的内容，我们认为您可能需要进行更改，以确保它不违反我们的垃圾邮件、欺诈行为和欺诈活动政策。与此同时，我们已将以下内容设为私密：

我们尚未对您的频道施加惩罚，如果您进行更改，或者如果您认为我们犯了错误，您可以请求将您的内容重新公开。但是，有些情况下YouTube可能会保持您的内容私密。

"锁定为私密"是什么意思

被锁定为私密的内容不会出现在您的频道或搜索结果中，其他用户也无法看到它。了解更多关于这是如何工作的信息。
```

### Youtube 地区和版权受限问题

Youtube在某些受限地区（可能包括中国大陆、朝鲜、俄罗斯联邦等）可能会进行严格的审查或者阻止等行为。本工具的可用性取决于API的可用性。

在某些国家或地区（可能包括中国大陆、伊朗等）可能会对访问Youtube进行实际上的阻止或者法律限制。请自行遵循对应的法律规定，你应当知道所有行为的后果和责任均由使用人自行承担。

## 哔哩哔哩 相关

更多信息请访问 [哔哩哔哩下载相关信息](doc/bilibili-dl.md)

### 哔哩哔哩下载参考项目

本列表中的项目可用性未知，可能也没有进行任何测试，请自行检查

- [youtube-dl](https://github.com/ytdl-org/youtube-dl)
- [BBDown](https://github.com/nilaoda/BBDown)
- [bili-cli-rs](https://github.com/niuhuan/bili-cli-rs)
- [Youtube-dl-REST](https://github.com/develon2015/Youtube-dl-REST)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

### 哔哩哔哩下载分辨率问题

由于哔哩哔哩本身的限制，哔哩哔哩下载出来的视频（未登录）是限制到了360P左右
像 `ytdl-org/youtube-dl` 等软件在没有解决登录问题的情况下是无法下载高清视频的。

---

# 项目目录结构详解

## 目录结构

```text
Bili-to-Youtube/
├── B2Y.py                           # 🎯 主程序入口
├── Upload_to_Youtube.py             # 📤 YouTube上传模块
├── GET_Playlist_From_Youtube.py     # 📋 YouTube播放列表管理
├── tools/                           # 🛠️ 辅助工具集
│   ├── bili-super-downloader.py    # 🚀 B站超级下载器(融合版)
│   ├── bili-config.yaml            # ⚙️ 超级下载器配置文件
│   ├── biliapi-proxy.py            # 🌐 哔哩哔哩API代理服务器
│   ├── bup-scan-xlsx-bbdown.py     # 📊 批量视频抓取和下载工具
│   ├── check-bilidown-xlsx.py      # ✅ 下载状态检查工具
│   ├── get-yt-link.py              # 🔗 YouTube链接提取器
│   ├── yt-dl.py                    # ⬇️ YouTube批量下载器
│   └── BBDown-Plus/                # 📦 批处理脚本集合
│       ├── BATCH_BBDOWN_B23LINK.py
│       ├── BATCH_BBDOWN_BiliLINK.py
│       └── ...
├── script/                          # 🚀 跨平台启动脚本
│   ├── B2Y.bat                     # Windows批处理
│   ├── B2Y.ps1                     # PowerShell脚本
│   └── B2Y.sh                      # Linux/macOS脚本
├── doc/                             # 📚 项目文档
├── bin/                             # 📦 可执行文件目录
└── ...
```

## 核心程序说明

### B2Y.py - 主工作流控制器

**一键式B站到YouTube转载工具**

- 🔄 **自动化工作流**：调用BBDown下载 → 解析视频信息 → 自动上传YouTube
- 📝 **智能信息提取**：自动获取视频AID和标题，生成合适的YouTube描述
- 🎯 **简单易用**：支持B站视频链接和BV号两种输入方式
- 🔗 **无缝对接**：与Upload_to_Youtube.py完美集成

```bash
python B2Y.py https://www.bilibili.com/video/BV1kj411a7w9/
python B2Y.py BV1kj411a7w9
```

### Upload_to_Youtube.py - YouTube上传核心引擎

**独立的专业级YouTube上传工具**

- 🔐 **OAuth 2.0认证**：完整的Google API认证流程，支持token持久化
- 🌍 **代理支持**：内置SOCKS5代理，解决地域访问限制
- 🎨 **丰富元数据**：支持标题、描述、分类、播放列表等完整视频信息
- 🔧 **高度可配置**：可独立使用，支持任意来源的视频上传
- 🛡️ **隐私优先**：默认设置为私有，避免意外公开

```bash
python Upload_to_Youtube.py -f video.mp4 -t "视频标题" -d "视频描述"
```

### GET_Playlist_From_Youtube.py - 播放列表管理助手

**YouTube频道内容组织工具**

- 📋 **播放列表查询**：获取用户的所有YouTube播放列表
- 🔍 **ID提取**：为视频上传提供准确的播放列表ID
- 🎯 **频道管理**：帮助规划和组织YouTube频道结构

## 辅助工具详解

### 🚀 bili-super-downloader.py - B站超级下载器(融合版)

**新一代全功能B站下载解决方案**

- 🎯 **双模式操作**：Single模式深度抓取单个UP主 + Batch模式批量快更多个UP主
- 📊 **多格式数据管理**：Excel/JSON/CSV三格式支持，按UP主智能分表存储
- ⚡ **智能下载引擎**：集成BBDown，支持多线程并发，智能去重和断点续传
- 🔐 **WBI签名认证**：完整实现B站WBI签名算法，绕过反爬虫检测
- ⚙️ **YAML配置管理**：专业配置文件管理，支持命令行参数覆盖
- 🕒 **灵活时间控制**：支持增量下载、最近N天过滤等多种时间策略
- 🧹 **智能清理系统**：自动清理临时文件和子文件夹，保持目录整洁

**🚨 重要安全提醒**：
- bili-config.yaml配置文件包含敏感的B站Cookie认证信息
- 请确保不要将配置文件提交到公共代码仓库
- 建议使用环境变量或加密存储管理敏感信息

```bash
# 批量模式（默认）
python bili-super-downloader.py

# 单用户模式
python bili-super-downloader.py --mode single --mid 23318408

# 仅获取信息，不下载
python bili-super-downloader.py --no-download

# 生成默认配置文件
python bili-super-downloader.py --generate-config
```

**技术特点**：
- 融合了 `bup-scan-xlsx-bbdown-v3.py` 和 `bili-down-batch.py` 的所有功能
- 完全向后兼容旧版本程序的参数和配置
- 企业级错误处理和日志系统
- 支持代理访问和SSL配置
- 多平台兼容 (Windows/Linux/macOS)

### 🌐 biliapi-proxy.py - API稳定性保障工具

**企业级API代理解决方案**

- 🔄 **多域名负载均衡**：支持多个API域名，自动故障转移
- 🔁 **智能重试机制**：3次重试策略，提高API访问成功率
- 📊 **详细日志记录**：记录请求状态和响应时间，便于问题诊断
- 🚀 **Flask Web服务**：标准HTTP接口，易于集成和部署
- 🎯 **特定路径优化**：针对playurl接口进行专门优化

```bash
python biliapi-proxy.py  # 启动代理服务器 (端口5001)
```

### 📊 bup-scan-xlsx-bbdown.py - 企业级批量处理方案

**最强大的B站批量下载工具**

- 🔐 **WBI签名算法**：完整实现哔哩哔哩WBI签名，确保API访问合规
- 📈 **Excel数据管理**：结构化存储视频信息，便于数据分析和处理
- ⚡ **增量更新机制**：支持基于日期的增量下载，避免重复处理
- 🚀 **多线程并发**：可配置线程数，大幅提升批量处理效率
- 🎭 **随机User-Agent**：UA池轮换，降低被检测和限制的风险
- 🧹 **智能清理**：自动清理临时文件和子文件夹
- ⚙️ **高度可配置**：支持命令行参数覆盖，适应不同使用场景

```bash
python bup-scan-xlsx-bbdown.py --mid 356010767 --max_workers 4
```

### ✅ check-bilidown-xlsx.py - 轻量级状态监控工具

**快速下载进度检查器**

- 📊 **进度统计**：快速统计已下载和未下载视频数量
- 🔍 **详细报告**：列出具体的未下载BV号
- 📋 **Excel驱动**：与bup-scan-xlsx-bbdown.py无缝配合
- ⚡ **轻量快速**：纯检查功能，运行速度极快

### 🔗 get-yt-link.py - YouTube链接提取器

**HTML数据预处理工具**

- 🌐 **HTML解析**：使用BeautifulSoup强大的解析能力
- 🎯 **精准提取**：专门识别YouTube watch链接
- 🔄 **自动去重**：使用set数据结构自动去除重复链接
- 📝 **批量处理**：为批量下载工具提供数据源

### ⬇️ yt-dl.py - 专业级YouTube下载解决方案

**基于yt-dlp的高性能下载器**

- 🎥 **最佳质量**：自动选择最佳视频和音频流进行合并
- 🍪 **Cookie集成**：从Chrome浏览器导入认证信息，解决登录限制
- 🌍 **代理支持**：SOCKS5代理支持，突破地域限制
- ⚡ **高并发架构**：30线程并发 + 10片段并发，下载速度极快
- 📁 **智能命名**：使用视频标题作为文件名，便于管理

```bash
python yt-dl.py  # 从YouTube_Links.txt批量下载
```

### 📦 BBDown-Plus批处理套件 - 多场景适配方案

**跨平台批处理解决方案**

- 🔗 **B23链接优化**：专门处理B站短链接格式
- 💻 **多语言支持**：PowerShell和Python双重实现
- ⚡ **性能版本**：10x版本提供更高的并发处理能力
- 🌍 **跨平台兼容**：支持Windows、Linux、macOS
