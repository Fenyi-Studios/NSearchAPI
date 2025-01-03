from flask import Flask, request
import requests,os,sys,shutil,json
from bs4 import BeautifulSoup

app = Flask(__name__)

# 百度结果
def get_search_results(keyword,pages=2):
    """
    获得搜索结果
    Args:
        keyword: STR 搜索关键字
        pages: INT 页数
    Returns:
        [
            {S
                "title": "标题",
                "link": "https://链接/",
                "description": "介绍"
            }
        ]
    """
    # 发送 HTTP 请求
    results = []
    if os.path.exists("./cache/answer_"+keyword.replace("_","0")+"_"+str(pages)+".nsc"):
        with open("./cache/answer_"+keyword.replace("_","0")+"_"+str(pages)+".nsc","r",encoding="utf-8") as f:
            results = json.loads(f.read())
        return str(results)
    for i in range(pages):
        page = i * 10 
        url = f"https://cn.bing.com/search?q={keyword}&first={page}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.95 Safari/537.36"
        }
        response = requests.get(url, headers=headers) 
        # 解析 HTML 页面
        soup = BeautifulSoup(response.text, "html.parser")
        # 提取搜索结果
        for result in soup.find_all("li", class_="b_algo"):
            #print(result)
            title = result.find("a", target="_blank").text
            link = result.find("a", target="_blank").get("href")
            try:
                description = result.find("p", class_="b_lineclamp2").text
            except:
                try:
                    description = result.find("p", class_="b_lineclamp3").text
                except:
                    try:
                        description = result.find("p", class_="b_lineclamp4").text
                    except:
                        description = "ERROR"

            results.append({
            "title": str(title),
            "link": str(link),
            "description": str(description[2:])
            })
    with open("./cache/answer_"+keyword.replace("_","0")+"_"+str(pages)+".nsc","w",encoding="utf-8") as f:
        f.write(json.dumps(results))
    return json.dumps(results)

# 搜索
@app.route("/nsearch", methods=["GET"])
def search():
    return get_search_results(request.args.get("s"))

# 信息
@app.route("/")
def info():
    return "<!doctype html><html><head><title>NSearch API</title><meta charset='utf-8'/></head><body>NSearch API</body></html>"

# 获取目录大小
def get_dir_size(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size

# 缓存
if not os.path.exists("./cache/"):
    os.mkdir("./cache/")
if len(sys.argv) > 1:
    if sys.argv[1] == "-QUICKMODE":
        os.system("cls")
        print(">>> [ NSearch 服务器 ] 使用 Flask 架构，使用 Ctrl+C 退出。 <<<")
        if __name__ == "__main__":
            app.run(host="0.0.0.0", port=99)
        input(">>> 服务器关闭，按回车键退出。 <<<")
        sys.exit()
    else:
        print("检测到您使用了启动参数。但暂未找到与之匹配的指令。")
        print("-QUICKMODE | 直接启动服务器。")
        input()
        sys.exit()
while True:
    os.system("cls")
    print("\033[32m纷易计算工作室 · NSearch 服务器")
    print("\033[32m版本 v1.0.0 (d1a_02)\033[0m")
    print("\n◜----- [ 操作列表 ] -----◝")
    print("| START     | 启动服务器  |")
    print("| CLRCACHE  | 清除缓存    |")
    print("| CACHEINFO | 缓存信息    |")
    print("| END       | 关闭命令行  |")
    command = input("◟------------------------◞\n>")
    if command == "START":
        os.system("cls")
        print("\033[31m\033[1m>>> [ NSearch 服务器 ] 使用 Flask 架构，使用 Ctrl+C 退出。 <<<\033[0m")
        if __name__ == "__main__":
            app.run(host="0.0.0.0", port=99)
    elif command == "CLRCACHE":
        shutil.rmtree("./cache/")
        os.mkdir("./cache/")
        print("完成！")
    elif command == "CACHEINFO":
        cachesize = get_dir_size("./cache/")
        print("缓存目录：./cache/")
        print("缓存大小："+str(round(cachesize/1000/1000,3))+" MB")
        diskinfo_total, diskinfo_used, diskinfo_free = shutil.disk_usage("/")
        print("磁盘占用："+str(round(cachesize/1000/1000,3))+"MB/"+str(round(diskinfo_total/1000/1000,3))+"MB ("+str(round(cachesize/diskinfo_total,2)*100)+"%)")
    elif command == "END":
        sys.exit()
    else:
        print("\033[31m\033[1m错误的命令。请检查是否使用大写字母与命令完整性。\033[0m")
    input("按回车键继续...")