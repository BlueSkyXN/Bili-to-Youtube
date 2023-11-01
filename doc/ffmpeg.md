# ffmpeg

## 可参考我的博客

- [FFmpeg + NVIDIA AV1 硬编码 视频转码压制入门教程](https://www.blueskyxn.com/202301/6785.html)
- [FFmpeg 视频转码压制进阶教程（一）：常用参数和场景解读，并使用QuickCut帮助理解](https://www.blueskyxn.com/202301/6798.html)
- [FFmpeg 视频转码压制进阶教程（二）：码率实验&CQP/CRF NVENC参数对比&常见码率](https://www.blueskyxn.com/202301/6814.html)

## 快速部署

Windows 用户从这里下载编译好的二进制包即可  https://www.gyan.dev/ffmpeg/builds/ 然后放入环境变量

它包括发布包编译和月度编译版本

- https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-2023-10-26-git-2b300eb533-full_build.7z
- https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z

我之前试过 https://github.com/BtbN/FFmpeg-Builds 但是当时不支持AV1硬件编码，不知道后来改了没

本次测试使用了20231026版本，以及20230105版本