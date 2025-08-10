# 将Python脚本的输出保存到变量中
$urls = python "BATCH_BBDOWN_B23LINK.py" "BATCH_BBDOWN_B23LINK.txt" bbdown

# 对每个URL执行命令
foreach ($url in $urls) {
    # 执行你的命令
    Invoke-Expression $url
}
