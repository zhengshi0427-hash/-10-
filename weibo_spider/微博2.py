import requests
import pandas as pd
import time
import json
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ------------------- 配置区 -------------------
COOKIE = (
    "SCF=Am-Ulk9b88kquOgbMFctzWzS32oyz9OVDDLtugMByXNEkECqsCty2Utzov_QGPXcdvcLJvapVLpe9YnHj0BbWYA.; "
    "SINAGLOBAL=515186429630.80066.1780023033297; "
    "PC_TOKEN=3ca6747edd; "
    "ALF=1783254488; "
    "SUB=_2A25HJrCIDeRhGeBO7FsT-SnOwj-IHXVkWkxArDV8PUJbkNANLU7ikW1NRapQejQ2ovPnXYwSALgBaAS6pgSMLelo; "
    "SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWbodBFlLwYjaalxysSYhfU5JpX5KMhUgL.Foq7S0.E1KME1Ke2dJLoIEBLxKqLBo-L1h-LxKnLB-qLB-BLxK.LB.zL1KnLxKnLBK-LB.qt; "
    "_s_tentry=weibo.com; "
    "Apache=1890194193944.2446.1780662500877; "
    "ULV=1780662500880:3:1:2:1890194193944.2446.1780662500877:1780214090017"
)

INPUT_FILE = "输入.csv"
OUTPUT_FILE = "输出.csv"
REQUEST_DELAY = 3  # 每次请求间隔秒数（反爬）

# ---------------------------------------------------------------------

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Cookie": COOKIE,
    "Referer": "https://weibo.com/",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/plain, */*",
}

def extract_mid(post_url):
    """从帖子链接提取 mid"""
    try:
        clean_url = post_url.split("?")[0].strip().rstrip("/")
        return clean_url.split("/")[-1]
    except:
        return None

def parse_post(post_url):
    """爬取单条微博详情：正文、转发、评论、点赞、用户信息"""
    mid = extract_mid(post_url)
    if not mid:
        print(f"❌ 无效链接：{post_url}")
        return None

    api_url = f"https://weibo.com/ajax/statuses/show?id={mid}&locale=zh-CN&isGetLongText=true"
    print(f"🔗 正在爬取：{api_url}")

    try:
        resp = requests.get(api_url, headers=headers, timeout=20, verify=False)
        if resp.status_code != 200:
            print(f"❌ 请求失败，状态码：{resp.status_code}")
            return None

        data = resp.json()
        if data.get("ok") != 1:
            print(f"❌ 接口返回错误")
            return None

        status = data
        user = status.get("user", {})

        # 你要的字段
        return {
            "用户昵称": user.get("screen_name", ""),
            "用户ID": user.get("idstr", ""),
            "发布时间": status.get("created_at", ""),
            "博文正文": status.get("text_raw", "").replace("\n", " ").strip(),
            "转发数": status.get("reposts_count", 0),
            "评论数": status.get("comments_count", 0),
            "点赞数": status.get("attitudes_count", 0),
        }

    except Exception as e:
        print(f"❌ 爬取失败：{str(e)[:50]}")
        return None

if __name__ == "__main__":
    # 读取输入
    try:
        df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    except:
        df = pd.read_csv(INPUT_FILE, encoding="gbk")

    if "帖子链接" not in df.columns:
        print("❌ 必须包含【帖子链接】列")
        exit()

    results = []
    for idx, row in df.iterrows():
        print(f"\n===== 第 {idx+1}/{len(df)} 条 =====")
        post_url = row["帖子链接"]
        res = parse_post(post_url)
        combined = row.to_dict()

        if res:
            combined.update(res)
            print("✅ 成功")

        results.append(combined)
        time.sleep(REQUEST_DELAY)

    # 输出
    df_out = pd.DataFrame(results)
    df_out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\n🎉 全部完成！共处理 {len(results)} 条")
    print(f"📁 文件已保存到：{OUTPUT_FILE}")
