# 将Python脚本的输出保存到变量中
$urls = python "BATCH_BBDOWN_B23LINK.py" "BATCH_BBDOWN_B23LINK.txt" bbdown
$maxConcurrentJobs = 10

$jobQueue = [System.Collections.Queue]::new()

foreach ($url in $urls) {
    # 检查当前运行的作业数量，如果达到最大并发数，则等待
    while ((Get-Job -State Running).Count -ge $maxConcurrentJobs) {
        Start-Sleep -Seconds 1
    }

    # 启动新作业
    $job = Start-Job -ScriptBlock {
        param($url)
        Invoke-Expression $url
    } -ArgumentList $url

    # 将作业加入队列
    $jobQueue.Enqueue($job)
}

# 等待所有作业完成
while ($jobQueue.Count -gt 0) {
    $job = $jobQueue.Dequeue()
    $job | Wait-Job
    $job | Receive-Job
    $job | Remove-Job
}

# 可选：输出一些结束消息或执行后续操作
Write-Host "所有下载任务已完成"
