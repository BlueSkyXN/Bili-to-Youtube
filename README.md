# Bili-to-Youtube
B2Y，简化从哔哩哔哩视频下载到上传到Youtube的快速操作

# 目录

- [Bili-to-Youtube](#bili-to-youtube)
- [模块化设计文档](#模块化设计文档)
- [使用限制、提醒和声明](#使用限制提醒和声明)
  - [Youtube 相关](#youtube-相关)
    - [Youtube API 配额问题](#youtube-api-配额问题)
    - [Youtube 安全性限制](#youtube-安全性限制)
    - [Youtube 地区和版权受限问题](#youtube-地区和版权受限问题)
  - [哔哩哔哩 相关](#哔哩哔哩-相关)
    - [哔哩哔哩下载参考项目](#哔哩哔哩下载参考项目)
    - [哔哩哔哩下载分辨率问题](#哔哩哔哩下载分辨率问题)


# 模块化设计综述

由于模块化设计，除了哔哩哔哩也可以上传任意来源的视频进行操作，基本上只需要简单的修改即可。

整体模块由哔哩哔哩下载和YouTube上传两部分组成

如果需要使用其他哔哩哔哩下载或者ydl等其他来源或者已经准备好视频的，可直接调用Youtube上传单文件即可。

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

```
python B2Y.py  https://www.bilibili.com/video/BV1kj411a7w9/
```
```
python B2Y.py  BV1kj411a7w9
```

## Google Youtube API 的配置

请阅读 [YoutubeAPI相关信息](doc\youtube-api.md)

# 使用限制、提醒和声明

## Youtube 相关

### Youtube API 配额问题

根据 [Youtube 官方文档](https://developers.google.com/youtube/v3/getting-started?hl=zh-cn#quota)

默认情况下，分配每日10000的API配额（似乎跟随项目而不是账号）。而根据文档介绍，上传一次需要1600点配额，计算可得每日6个视频。如果要更多配额可向Google申请。因此本程序设计中需要你自行解决API权限和申请。除非谷歌给我特批。

### Youtube 安全性限制

由于Youtube安全检测的问题，API上传的视频可能不可直接公开可用，尤其是发送TEST视频的时候。

参考提示如下

```
我们的团队已经审查了您的内容，我们认为您可能需要进行更改，以确保它不违反我们的垃圾邮件、欺诈行为和欺诈活动政策。与此同时，我们已将以下内容设为私密：

我们尚未对您的频道施加惩罚，如果您进行更改，或者如果您认为我们犯了错误，您可以请求将您的内容重新公开。但是，有些情况下YouTube可能会保持您的内容私密。

“锁定为私密”是什么意思

被锁定为私密的内容不会出现在您的频道或搜索结果中，其他用户也无法看到它。了解更多关于这是如何工作的信息。
```

### Youtube 地区和版权受限问题

Youtube在某些受限地区（可能包括中国大陆、朝鲜、俄罗斯联邦等）可能会进行严格的审查或者阻止等行为。本工具的可用性取决于API的可用性。

在某些国家或地区（可能包括中国大陆、伊朗等）可能会对访问Youtube进行实际上的阻止或者法律限制。请自行遵循对应的法律规定，你应当知道所有行为的后果和责任均由使用人自行承担。

## 哔哩哔哩 相关

更多信息请访问 [哔哩哔哩下载相关信息](doc\bilibili-dl.md)


### 哔哩哔哩下载参考项目

本列表中的项目可用性未知，可能也没有进行任何测试，请自行检查

- https://github.com/ytdl-org/youtube-dl
- https://github.com/nilaoda/BBDown
- https://github.com/niuhuan/bili-cli-rs
- https://github.com/develon2015/Youtube-dl-REST
- https://github.com/yt-dlp/yt-dlp

### 哔哩哔哩下载分辨率问题

由于哔哩哔哩本身的限制，哔哩哔哩下载出来的视频（未登录）是限制到了360P左右
像 ``ytdl-org/youtube-dl`` 等软件在没有解决登录问题的情况下是无法下载高清视频的。

