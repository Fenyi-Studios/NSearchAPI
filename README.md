<h1 align="center">
    <img width="48" height="48" style="border-radius: 10px;" alt="NSearch Logo" src="https://github.com/user-attachments/assets/817e1db4-5c8e-4e67-9d5f-db895327c618">
    NSearchAPI
</h1>
<h4 align="center">
    ✨为搜索而生， <br/>
    爬虫 Bing 搜索结果接口方便开发。
</h4>


<div align="center"><img width="225" alt="413554183-21142d43-9074-43f1-9a94-60d2bb003672" src="https://github.com/user-attachments/assets/33332958-3340-43a7-bb49-89e62faccd27" />
<br><img width="200" alt="image" src="https://github.com/user-attachments/assets/1165a6cf-d40e-4f42-af8a-10c8cf1ddea5" /><br><img width="272" alt="image" src="https://github.com/user-attachments/assets/f6ec5580-46e1-4ad7-9324-72945cf39a00" />

</div>

<h4 align="center">
    简体中文 | 
    <a href="#">繁體中文</a> | 
    <a href="#">English</a> | 
    <a href="#">しろうと</a> | 
    <a href="#">Русский язык</a> | 
    <a href="#">Deutsch</a> | 
    <a href="#">Français</a> 
</h4>
<h6 align="center"><i>* 文档只有简体中文其他都是装的，其它也都是装的</i><br><i>* 别喷，我们盐豆不盐了（doge</i></h6>
<br>

# 📚 功能特点

- 🚀 基于 FastAPI 的高性能异步架构
- 🔍 自动爬取 Bing 搜索结果
- 📝 智能提取网页内容
- 💾 本地缓存搜索结果
- 🌐 HTTP API 接口易于集成
- ⚡ 支持快速启动模式
- 🛠 提供命令行管理界面

# 🎯 使用场景

- 开发测试阶段的搜索功能实现
- 需要 Bing 搜索结果的应用开发
- 网页内容批量采集
- API 服务搭建

# 🚀 快速开始

## 安装运行

1. 从 Release 页面下载最新版本
2. 运行方式有两种：
   - 普通模式：直接运行程序，输入 `START` 启动服务器
   - 快速模式：使用命令行参数 `-QUICKMODE` 直接启动
   ```bash
   nsearch.exe -QUICKMODE
   ```

## 验证部署

访问 `http://localhost:99/` 查看服务状态，如显示以下内容则表示部署成功：

```json
{
    "title": "NSearch API",
    "description": "基于 FastAPI 的搜索和爬取 API",
    "version": "v1.0.0"
}
```

# 📖 API 文档

## 搜索接口

### 基础搜索
```http
GET /nsearch?s={关键词}&pages={页数}
```

参数说明：
- `s`: 搜索关键词（必填）
- `pages`: 获取结果页数，默认为 2

返回格式：
```json
[
    {
        "title": "搜索结果标题",
        "link": "http://结果链接",
        "description": "结果描述",
        "content": "网页正文内容（如果成功爬取）"
    }
]
```

### 缓存管理

#### 查看缓存信息
```http
GET /cacheinfo
```

返回示例：
```json
{
    "cache_directory": "./cache/",
    "cache_size_MB": 1.234,
    "disk_usage_MB": "1.234 MB / 1000.000 MB (0.12%)"
}
```

#### 清除缓存
```http
GET /clrcache
```

# 💻 命令行操作

程序提供以下命令行指令：

- `START`: 启动服务器
- `CLRCACHE`: 清除本地缓存
- `CACHEINFO`: 查看缓存使用情况
- `Ctrl+C`: 退出程序

# ⚙️ 技术细节

- 搜索结果缓存：自动缓存搜索结果到本地，减少重复请求
- 智能提取：使用优化算法提取网页正文内容
- 异步处理：采用异步架构处理并发请求
- 超时控制：网页爬取设置 10 秒超时限制
- 内容限制：提取的内容默认限制在 1000 字以内

# 🔒 使用限制

- 默认端口：99
- 缓存位置：./cache/
- 单次爬取超时：10秒
- 内容提取上限：1000字符

# 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来完善项目。在提交之前，请确保：

1. 描述清晰具体的问题或改进
2. 提供必要的复现步骤
3. 遵循项目代码规范

# 📄 开源协议

本项目采用 [MIT 许可证](LICENSE)。

# 🎉 致谢

感谢所有贡献者对项目的支持！

<img width="134" alt="image" src="https://github.com/user-attachments/assets/fd03c058-8185-4a4a-95db-6169ceb8117e" />

---

> 本项目仅供学习研究使用，请勿用于非法用途。
