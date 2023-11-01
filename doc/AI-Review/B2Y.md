# B2Y 使用手册

## 简介

这个 Python 程序是一个自动化脚本，用于从哔哩哔哩（Bilibili）下载视频并上传到 YouTube。该程序依赖于两个外部工具：

1. `BBDown.exe`：用于从哔哩哔哩下载视频。
2. `Upload_to_Youtube.py`：用于将视频上传到 YouTube。

该程序首先使用 `BBDown.exe` 获取视频的 AID（哔哩哔哩上的视频ID）和文件名，然后使用这些信息调用 `Upload_to_Youtube.py` 来上传视频到 YouTube。

## 安装依赖

在使用该程序之前，请确保您已经安装了以下依赖：

1. **Python 3.x**：该程序是用 Python 编写的，因此需要 Python 的运行时环境。
2. **BBDown.exe**：请从其官方 GitHub 仓库下载并安装。
3. **Upload_to_Youtube.py**：确保您有这个脚本以及其依赖。

## 参数

该程序接受与 `BBDown.exe` 相同的命令行参数。这些参数会被直接传递给 `BBDown.exe`。

例如：

```bash
python main.py -i https://www.bilibili.com/video/BV1Kb411W75N
```

其中，`-i` 和 `https://www.bilibili.com/video/BV1Kb411W75N` 是传递给 `BBDown.exe` 的参数。

## 功能流程

1. **获取 AID 和文件名**：程序首先调用 `BBDown.exe`，通过正则表达式匹配从其输出中获取 AID 和文件名。
2. **上传视频**：程序然后调用 `Upload_to_Youtube.py`，传递文件名和 AID 作为参数进行视频上传。

## 返回结果

该程序在控制台输出获取到的 AID 和文件名。如果成功，您将看到如下输出：

```
AID: 1234567
文件名: example.mp4
```

如果程序不能获取到 AID 或文件名，它将输出：

```
无法获取AID或文件名。
```

## 异常处理

- 如果 `BBDown.exe` 或 `Upload_to_Youtube.py` 运行失败，程序将直接终止，因为它依赖这两个工具。
- 如果无法获取 AID 或文件名，程序也会终止。

## 使用示例

```bash
# 下载并上传哔哩哔哩视频
python main.py -i https://www.bilibili.com/video/BV1Kb411W75N
```

## 注意事项

- 确保您有权将从哔哩哔哩下载的视频上传到 YouTube。
- 确保 `BBDown.exe` 和 `Upload_to_Youtube.py` 在 PATH 环境变量中，或与本程序在同一目录下。

## 后续改进建议

- 添加更多的错误检查和异常处理。
- 支持多线程或异步以提高下载和上传的速度。
- 添加一个配置文件以存储常用的设置和参数。

## 开发者信息

该程序由一名来自中国的计算机工程师开发，主要使用 Python 编程语言。

## 许可证

请参阅附带的 LICENSE 文件以获取有关许可信息。

这就是一个初步的程序手册，如果您有更多的问题或需要进一步的澄清，请随时联系开发者。希望这份手册能帮助您更好地理解和使用这个程序。