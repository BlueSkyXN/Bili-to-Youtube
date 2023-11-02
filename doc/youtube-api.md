# Google Youtube API 的配置

1，访问 https://console.cloud.google.com/apis/credentials 创建新的项目，下面没提的都随便.公开私有都可以。

2，创建新的Oauth凭据，类型是 Web 应用，并且保存JSON，命名为 ``client_secrets.json`` ，和``Upload_to_Youtube.py``源代码一致

```
已获授权的重定向 URI=http://localhost:58080/ 
已获授权的 JavaScript 来源=https://accounts.google.com
```
回调URL的设定和``Upload_to_Youtube.py``源代码中的端口一致

3，不需要服务账号SA，也不需要API 密钥

4，根据官方文档 https://support.google.com/youtube/answer/3070500?hl=zh-Hans 可找到 https://developers.google.com/youtube/v3/guides/uploading_a_video?hl=zh-cn ，在这里面的``向 Google 注册您的应用，以便它可以使用 OAuth 2.0 协议来授权访问用户数据。``就是API的入口。API的名字是 YouTube Data API。链接是 https://console.developers.google.com/apis/api/youtube.googleapis.com/overview

# 认证

2020 年 7 月 28 日 之后创建的未经验证的 API 项目通过 videos.insert 端点上传的所有视频将仅限于私人观看模式。要解除此限制，每个项目都必须 接受审核 以验证是否遵守 服务条款 。

使用未经验证的 API 客户端上传视频的创作者将收到一封电子邮件，说明其视频被锁定为私有，并且他们可以通过使用官方或经过审核的客户端来避免限制。

2020 年 7 月 28 日之前创建的 API 项目目前不受此更改的影响。不过，我们强烈建议所有开发者对其项目 完成合规性审核 ，以确保持续访问 YouTube API 服务。

# 示例

认证信息最后类似

```
{
    "web": {
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "client_id": "XXXXX.apps.googleusercontent.com",
        "client_secret": "XXXXXX",
        "javascript_origins": [
            "https://accounts.google.com"
        ],
        "project_id": "youtube-uploader",
        "redirect_uris": [
            "http://localhost:58080/"
        ],
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

```

# 配额用量

https://developers.google.com/youtube/v3/getting-started?hl=zh-cn#quota


YouTube Data API 使用配额来确保开发者按预期使用服务，并且不会创建不公平地降低服务质量或限制他人访问的应用。所有 API 请求（包括无效请求）都会产生至少 1 分的配额费用。您可以在 API Console 中找到您的应用可用的配额。

启用了 YouTube Data API 的项目每天的默认配额分配为 10,000 个单元，这个配额足以满足绝大多数 API 用户的需求。默认配额可能会发生变化，这有助于我们优化配额分配，并以对 API 用户更有意义的方式扩缩基础架构。您可以在 API 控制台的配额页面上查看配额使用情况。

注意：如果您达到配额限制，可以填写 YouTube API 服务的配额增加申请表单来申请更多配额。

## 计算配额用量

Google 通过为每个请求指定费用来计算您的配额用量。不同类型的操作具有不同的配额费用。例如：

用于检索资源列表（频道、视频和播放列表）的读取操作通常需要 1 个单元。
创建、更新或删除资源的写入操作通常需要 50 单位。
搜索请求的费用为 100 单位。
一次视频上传需要 1600 单元。
API 请求的配额费用表格显示了每种 API 方法的配额费用。了解这些规则后，您就可以估算您的应用每天在不超出配额的情况下可以发送的请求数。

## YouTube API 服务 - 审核和配额增加表单

https://support.google.com/youtube/contact/yt_api_form?hl=zh-Hans
