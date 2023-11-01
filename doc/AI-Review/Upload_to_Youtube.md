# YouTube 视频上传工具手册

## 简介

这是一个用Python编写的命令行工具，用于上传视频到YouTube。该工具支持通过SOCKS5代理进行上传，也支持自定义视频的标题、描述、分类ID和播放列表ID。

## 功能特点

- 支持通过SOCKS5代理上传
- 支持自定义视频标题、描述
- 支持设置视频分类ID
- 支持将视频添加到指定播放列表
- 自动保存和读取Google API凭证

## 依赖

- `socket`
- `socks`
- `os`
- `argparse`
- `googleapiclient`
- `google_auth_oauthlib`
- `pickle`

## 安装依赖

```bash
pip install google-api-python-client google-auth google-auth-oauthlib PySocks
```

## 使用前准备

1. 请先在[Google API Console](https://console.developers.google.com/)创建一个项目，并启用YouTube Data API v3。下载生成的`client_secrets.json`文件并放在与脚本相同的目录下。
2. 如果你想通过SOCKS5代理上传，确保你的代理服务器已经启动。

## 命令行参数

| 参数         | 描述                               | 示例                     |
| ------------ | ---------------------------------- | ------------------------ |
| `-f`, `--file`  | 要上传的视频文件的路径               | `--file="example.mp4"`   |
| `-s`, `--socks5` | SOCKS5代理地址和端口               | `--socks5="127.0.0.1:1080"` |
| `-t`, `--title`  | 上传视频的标题                     | `--title="My Video"`     |
| `-d`, `--description` | 上传视频的描述                   | `--description="This is a test video"` |
| `-g`, `--categoryId`  | 上传视频的分类ID                  | `--categoryId="22"`      |
| `-l`, `--playlist`    | 上传视频的播放列表ID               | `--playlist="PLabcdefgh"`|

## 使用示例

上传一个视频：

```bash
python script.py --file="example.mp4" --title="测试视频" --description="这是一个测试视频"
```

通过SOCKS5代理上传：

```bash
python script.py --file="example.mp4" --socks5="127.0.0.1:1080"
```

添加到指定分类和播放列表：

```bash
python script.py --file="example.mp4" --categoryId="22" --playlist="PLabcdefgh"
```

## 代码解析

1. `set_socks5_proxy(host, port)`: 设置SOCKS5代理。
2. `upload_video(args)`: 主要的视频上传函数。

首先，如果设置了SOCKS5代理，该函数会调用`set_socks5_proxy`来设置。

然后，该函数会检查是否存在有效的Google API凭证。如果不存在，它将启动一个本地服务器来完成OAuth 2.0授权。

最后，它使用Google API的`videos().insert()`方法来上传视频。

## 问题和解决方案

1. **代理不工作**: 确保你的SOCKS5代理服务器是可用的，并且`PySocks`库已经安装。
2. **API凭证问题**: 删除`token.pickle`文件，然后重新运行脚本以获取新的凭证。




