<h1 align="center">
    NSearchAPI
</h1>
<h4 align="center">
    为搜索而生， <br/>
    爬虫 Bing 搜索结果接口方便开发。
</h4>
<h4 align="center">
    简体中文 | 
    <a href="#">繁體中文</a> | 
    <a href="#">English</a> | 
    <a href="#">しろうと</a> | 
    <a href="#">Русский язык</a> | 
    <a href="#">Deutsch</a> | 
    <a href="#">Français</a> 
</h4>
<h6 align="center"><i>* 只有简体中文其他都是装的</i></h6>
<br><br>

# 有什么优势？

-   操作简单易用，适合开发还未接入官方 API 的阶段。
-   基于 HTTP 协议，大部分场景都能接入使用。
-   _玩原神很快_ (bushi

# 怎么用？

1.  下载 Release(正式版) ，点击打开，输入指令“START”。  
    或用 Windows 终端 打开时在后方添加启动参数 `-QUICKMODE`。
2.  访问 `http://localhost:99/` ，如显示 `NSearch API` 则表示 HTTP 部署成功。
3.  场景调用 `http://localhost:99/nsearch?s=<关键词>`，如正常，会按以下格式回复：

```json
[
	{
		"title": "标题",
		"link": "http://链接/",
		"description": "描述"
	},
	{
		"title": "标题2",
		"link": "http://链接2/",
		"description": "描述2"
	}
]
```
