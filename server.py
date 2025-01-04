# 预览版
import os
import sys
import shutil
import json
import asyncio
import aiohttp
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from multiprocessing import Process, Event
import uvicorn
import re

app = FastAPI()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CACHE_DIR = "./cache/"

# 获取目录大小
def get_dir_size(dir_path: str) -> int:
    size = 0
    for root, dirs, files in os.walk(dir_path):
        size += sum(os.path.getsize(os.path.join(root, name)) for name in files)
    return size

# 初始化缓存目录并清理
def initialize_cache():
    if os.path.exists(CACHE_DIR):
        try:
            shutil.rmtree(CACHE_DIR)
            logging.info("缓存目录 './cache/' 已清理。")
        except Exception as e:
            logging.error(f"清理缓存目录失败: {e}")
    os.makedirs(CACHE_DIR, exist_ok=True)
    logging.info("缓存目录 './cache/' 已创建。")

# 文本提取函数
def extract_text(text: str, limit=1000) -> str:
    # 定义句子结束符
    sentence_endings = {'.', ';', '?', '。', '；', '？'}
    # 初始化
    extracted = []
    count = 0
    after_limit = 0
    max_after_limit = 100
    stop = False
    
    # 使用正则表达式分词
    token_pattern = re.compile(r'[A-Za-z]+|[\u4e00-\u9fff]|.', re.UNICODE)
    tokens = token_pattern.findall(text)
    
    for token in tokens:
        if re.match(r'[A-Za-z]+', token):
            count += 1  # 英文单词
        elif re.match(r'[\u4e00-\u9fff]', token):
            count += 1  # 中文字符
        else:
            count += 1  # 其他字符
        
        extracted.append(token)
        
        if count >= limit and not stop:
            # 达到限制后，开始寻找下一个句子结束符
            stop = True
        
        if stop:
            if token in sentence_endings:
                break
            after_limit += 1
            if after_limit >= max_after_limit:
                break
    
    return ''.join(extracted)

# 获取搜索结果（同步函数）
def get_search_results_sync(keyword: str, pages: int = 2) -> List[Dict[str, Any]]:
    import requests  # 避免与异步环境冲突
    results = []
    cache_filename = f"{CACHE_DIR}answer_{keyword.replace('_','0')}_{pages}.nsc"

    # 检查缓存
    if os.path.exists(cache_filename):
        try:
            with open(cache_filename, "r", encoding="utf-8") as f:
                results = json.load(f)
            logging.info(f"使用缓存文件: {cache_filename}")
            return results
        except Exception as e:
            logging.error(f"读取缓存文件失败: {e}")

    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/108.0.5359.95 Safari/537.36"),
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.bing.com/"
    }

    for i in range(pages):
        first = 1 + i * 10  # 修正分页参数
        url = f"https://cn.bing.com/search?q={keyword}&first={first}"
        logging.info(f"请求 URL: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"HTTP 请求失败: {e}")
            continue

        # 解析 HTML
        soup = BeautifulSoup(response.text, "lxml")

        # 提取搜索结果
        b_algo_elements = soup.find_all("li", class_="b_algo")
        logging.info(f"找到 {len(b_algo_elements)} 个 b_algo 元素")

        for index, result in enumerate(b_algo_elements, start=1):
            try:
                # 初始化字段
                title = "无标题"
                link = "无链接"
                description = "无描述"

                # 获取标题和链接
                h2 = result.find("h2")
                if h2:
                    a_tag = h2.find("a")
                    if a_tag and a_tag.get("href"):
                        title = a_tag.get_text(strip=True)
                        link = a_tag.get("href").strip()
                    else:
                        logging.warning(f"b_algo 块 {index}: h2 标签中未找到有效的 a 标签或 href")
                else:
                    a_tag = result.find("a", class_="tilk")
                    if a_tag and a_tag.get("href"):
                        title = a_tag.get_text(strip=True)
                        link = a_tag.get("href").strip()
                    else:
                        a_tag = result.find("a", href=True)
                        if a_tag:
                            title = a_tag.get_text(strip=True)
                            link = a_tag.get("href").strip()
                        else:
                            logging.warning(f"b_algo 块 {index}: 未找到任何有效的 a 标签")

                # 获取描述
                description_found = False
                p_tags = result.find_all("p")
                for p in p_tags:
                    classes = p.get("class", [])
                    if any("b_lineclamp" in cls for cls in classes):
                        description = p.get_text(strip=True)
                        description_found = True
                        break

                if not description_found:
                    caption_div = result.find("div", class_="b_caption")
                    if caption_div:
                        p = caption_div.find("p")
                        if p:
                            description = p.get_text(strip=True)
                            description_found = True

                if not description_found:
                    additional_desc = result.find("div", class_="b_attribution")
                    if additional_desc:
                        description = additional_desc.get_text(strip=True)
                        description_found = True

                # 记录结果
                results.append({
                    "title": title,
                    "link": link,
                    "description": description
                })
                logging.info(f"b_algo 块 {index}: 解析成功")

            except Exception as e:
                logging.error(f"b_algo 块 {index}: 解析失败 - {e}")
                results.append({
                    "title": "解析失败",
                    "link": "解析失败",
                    "description": f"解析失败: {e}"
                })
                continue

    # 缓存结果
    try:
        with open(cache_filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logging.info(f"缓存文件已保存: {cache_filename}")
    except Exception as e:
        logging.error(f"写入缓存文件失败: {e}")

    return results

# 异步获取搜索结果
async def get_search_results(keyword: str, pages: int = 2) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(get_search_results_sync, keyword, pages)

# 异步爬取网站内容
async def fetch_content(session: aiohttp.ClientSession, url: str) -> str:
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                return f"请求失败，状态码: {response.status}"
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            # 提取文本内容
            #pure_text = extract_text(text, limit=1000)
            pure_text = soup.get_text(separator=' ', strip=True)
            pure_text = extract_text(pure_text, limit=1000)
            return pure_text
    except Exception as e:
        return f"爬取失败: {e}"


# 主搜索和爬取逻辑
@app.get("/nsearch")
async def search(s: str = Query(..., description="搜索关键词"), pages: int = Query(2, description="搜索页数")):
    if not s:
        raise HTTPException(status_code=400, detail="缺少搜索参数 's'")

    # 获取搜索结果
    search_results = await get_search_results(s, pages)

    # 准备异步爬取任务
    async with aiohttp.ClientSession() as session:
        tasks = []
        for result in search_results:
            url = result.get("link")
            if url and url.startswith("http"):
                tasks.append(asyncio.create_task(fetch_content(session, url)))
            else:
                tasks.append(asyncio.create_task(asyncio.sleep(0, result="无效的链接")))

        # 设置10秒超时
        try:
            crawled_contents = await asyncio.wait_for(asyncio.gather(*tasks), timeout=10)
        except asyncio.TimeoutError:
            # 如果超时，取消所有任务
            for task in tasks:
                task.cancel()
            crawled_contents = ["爬取超时"] * len(tasks)

    # 将爬取内容添加到搜索结果中
    for idx, content in enumerate(crawled_contents):
        if idx < len(search_results):
            if isinstance(content, str):
                search_results[idx]["content"] = content
            else:
                search_results[idx]["content"] = "爬取失败"

    return JSONResponse(content=search_results)

# 信息接口
@app.get("/")
async def info():
    return {
        "title": "NSearch API",
        "description": "基于 FastAPI 的搜索和爬取 API",
        "version": "v1.0.0"
    }

# 缓存信息接口
@app.get("/cacheinfo")
async def cache_info():
    try:
        cachesize = get_dir_size(CACHE_DIR)
        diskinfo_total, diskinfo_used, diskinfo_free = shutil.disk_usage("/")
        used_mb = round(cachesize / 1_000_000, 3)
        total_mb = round(diskinfo_total / 1_000_000, 3)
        usage_percent = round((cachesize / diskinfo_total) * 100, 2)
        return {
            "cache_directory": CACHE_DIR,
            "cache_size_MB": used_mb,
            "disk_usage_MB": f"{used_mb} MB / {round(total_mb, 3)} MB ({usage_percent}%)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存信息失败: {e}")

# 清除缓存接口
@app.get("/clrcache")
async def clear_cache():
    try:
        shutil.rmtree(CACHE_DIR)
        os.makedirs(CACHE_DIR, exist_ok=True)
        logging.info("缓存已清除。")
        return {"message": "缓存已清除。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {e}")

# Lifespan 事件处理器
async def lifespan(app: FastAPI):
    # 启动时清理缓存
    initialize_cache()
    yield
    # 关闭时可以执行其他清理操作（如果需要）
    logging.info("应用关闭，执行清理操作。")

app.router.lifespan = lifespan

# 函数：运行 Uvicorn 服务器
def run_server(stop_event: Event):
    config = uvicorn.Config(app, host="0.0.0.0", port=99, log_level="warning")
    server = uvicorn.Server(config)

    # 启动服务器
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run():
        await server.serve()

    loop.run_until_complete(run())

    # 等待停止事件
    stop_event.wait()
    # 关闭服务器
    server.should_exit = True
    loop.stop()

# 命令行界面函数
def command_line_interface():
    server_process = None
    stop_event = Event()
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("\033[32m纷易计算工作室 · NSearch 服务器")
        print("\033[32m版本 v1.0.0 (d1a_02)\033[0m")
        print("\n◜----- [ 操作列表 ] -----◝")
        print("| START     | 启动服务器  |")
        #print("| STOP      | 停止服务器  |")
        print("| CLRCACHE  | 清除缓存    |")
        print("| CACHEINFO | 缓存信息    |")
        #print("| END       | 关闭命令行  |")
        command = input("◟------------------------◞\n按下Ctrl+C即可退出程序\n> ").strip().upper()

        if command == "START":
            if server_process and server_process.is_alive():
                print("服务器已启动。")
            else:
                print("\033[31m\033[1m>>> [ NSearch Server ] 使用 FastAPI 架构，使用 Ctrl+C 退出。 <<<\033[0m")
                server_process = Process(target=run_server, args=(stop_event,), daemon=True)
                server_process.start()
                print("服务器已启动。")
        elif command == "STOP":
            if server_process and server_process.is_alive():
                print("正在停止服务器...")
                stop_event.set()
                server_process.join()
                print("服务器已停止。")
            else:
                print("服务器未启动。")
        elif command == "CLRCACHE":
            try:
                shutil.rmtree(CACHE_DIR)
                os.makedirs(CACHE_DIR, exist_ok=True)
                print("缓存已清除。")
            except Exception as e:
                print(f"清除缓存失败: {e}")
        elif command == "CACHEINFO":
            try:
                cachesize = get_dir_size(CACHE_DIR)
                diskinfo_total, diskinfo_used, diskinfo_free = shutil.disk_usage("/")
                used_mb = round(cachesize / 1_000_000, 3)
                total_mb = round(diskinfo_total / 1_000_000, 3)
                usage_percent = round((cachesize / diskinfo_total) * 100, 2)
                print(f"缓存目录：{CACHE_DIR}")
                print(f"缓存大小：{used_mb} MB")
                print(f"磁盘占用：{used_mb} MB / {round(total_mb, 3)} MB ({usage_percent}%)")
            except Exception as e:
                print(f"获取缓存信息失败: {e}")
        elif command == "END":
            if server_process and server_process.is_alive():
                print("正在停止服务器...")
                stop_event.set()
                server_process.join()
                print("服务器已停止。")
            print("关闭命令行。")
            os._exit(0)
        else:
            print("\033[31m\033[1m错误的命令。请检查是否使用大写字母与命令完整性。\033[0m")

        input("按回车键继续...")

# 主函数
def main():
    # 初始化缓存
    initialize_cache()

    # 检查启动参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "-QUICKMODE":
            # 直接启动服务器
            logging.info("使用 QUICKMODE 启动服务器...")
            run_server(Event())
        else:
            print("检测到您使用了启动参数。但暂未找到与之匹配的指令。")
            print("-QUICKMODE | 直接启动服务器。")
            input("按回车键退出。")
            sys.exit()
    else:
        # 启动命令行界面
        command_line_interface()

if __name__ == "__main__":
    main()
