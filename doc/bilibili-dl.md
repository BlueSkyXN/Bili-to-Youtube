# 哔哩哔哩下载模块

## 我测试或使用的哔哩哔哩下载模块

### BBDown项目

在开发中，我使用了 [BBDown](https://github.com/nilaoda/BBDown) 作为哔哩哔哩下载器 

该项目需要自备ffmpeg（添加到环境变量）才可以使用

参考命令 ``BBDown.exe https://www.bilibili.com/video/BV15j411e7fJ``

具体介绍可访问  [BBDown 使用教程](BBDown.md) 

官方参考额访问 https://github.com/nilaoda/BBDown


## 哔哩哔哩下载参考项目

本列表中的项目可用性未知，可能也没有进行任何测试，请自行检查

- https://github.com/ytdl-org/youtube-dl
- https://github.com/nilaoda/BBDown
- https://github.com/niuhuan/bili-cli-rs
- https://github.com/develon2015/Youtube-dl-REST
- https://github.com/yt-dlp/yt-dlp

## 哔哩哔哩下载分辨率问题

由于哔哩哔哩本身的限制，哔哩哔哩下载出来的视频（未登录）是限制到了360P左右
像 ``ytdl-org/youtube-dl`` 等软件在没有解决登录问题的情况下是无法下载高清视频的。

受影响的程序包括但不限于
- https://github.com/ytdl-org/youtube-dl