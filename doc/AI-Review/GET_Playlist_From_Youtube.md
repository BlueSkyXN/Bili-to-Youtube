# YouTube 播放列表列出工具 程序手册

## 简介

这是一个用于获取YouTube上认证用户所有可用播放列表的Python工具。该工具具有通过SOCKS5代理连接以及限制返回的播放列表数量的选项。

## 功能

1. **SOCKS5代理支持**: 通过`-s`或`--socks5`选项，你可以设置SOCKS5代理。
2. **限制返回的播放列表数量**: 通过`-m`或`--maxResults`选项，你可以限制返回的播放列表的数量。
3. **OAuth2认证**: 使用Google的API和OAuth2进行身份验证。

## 环境依赖

- Python 3.x
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client`, `socks`, `argparse`等Python库。

安装依赖：

```bash
pip install google-auth google-auth-oauthlib google-api-python-client PySocks argparse
```

## 使用方式

1. **准备 Google OAuth2 认证文件**

    在使用之前，你需要有一个`client_secrets.json`文件，这个文件包含了Google API的认证信息。

2. **运行程序**

    ```bash
    python your_script_name.py [-s host:port] [-m maxResults]
    ```

    - `-s` 或 `--socks5`: 设置SOCKS5代理，格式为`host:port`。
    - `-m` 或 `--maxResults`: 设置返回的最大播放列表数量。

### 示例

```bash
python your_script_name.py -s 127.0.0.1:1080 -m 10
```

这将通过`127.0.0.1:1080`的SOCKS5代理获取最多10个播放列表。

## 代码结构

### `set_socks5_proxy(host, port)`

设置SOCKS5代理。

### `list_playlists(args)`

主要功能函数，获取并列出播放列表。

- **参数**: 接受一个`argparse.Namespace`对象，其中包含所有命令行参数。
- **认证**: 使用`token.pickle`文件或`client_secrets.json`进行OAuth2认证。
- **API调用**: 使用`youtube.playlists().list()`方法获取播放列表。

### `if __name__ == '__main__':`

命令行参数解析和程序入口。

## 错误处理和日志

程序基本上没有专门的错误处理和日志功能，因此如果遇到问题，可能需要查看控制台输出来进行调试。

## 贡献和反馈

如果你在使用过程中遇到任何问题或有任何建议，欢迎通过GitHub提出。
