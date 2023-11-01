# 定义用于获取AID和文件名的函数
Function Get-AidAndFilename {
    param(
        [string]$url
    )
    $output = & BBDown.exe $url
    $aid = $output -match "获取aid结束: (\d+)"
    $aid = $matches[1]
    $filename = $output -match "视频标题: (.+)"
    $filename = ($matches[1] + ".mp4")
    return $aid, $filename
}

# 定义用于上传视频的函数
Function Upload-Video {
    param(
        [string]$filename,
        [string]$aid
    )
    python Upload_to_Youtube.py -f $filename  -d ("转载自哔哩哔哩，原视频ID为" + $aid) "
}

# 主程序
$cmd_args = $args[0]
$aid, $filename = Get-AidAndFilename $cmd_args

if ($aid -ne $null -and $filename -ne $null) {
    Write-Host "AID: $aid"
    Write-Host "文件名: $filename"
    Upload-Video -filename $filename -aid $aid
} else {
    Write-Host "无法获取AID或文件名。"
}
