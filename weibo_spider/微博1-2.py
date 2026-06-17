import requests
import pandas as pd
import time
import json
import random
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ------------------- 配置区（已替换最新Cookie） -------------------
COOKIE = (
    "SCF=Am-Ulk9b88kquOgbMFctzWzS32oyz9OVDDLtugMByXNEkECqsCty2Utzov_QGPXcdvcLJvapVLpe9YnHj0BbWYA.; "
    "SINAGLOBAL=515186429630.80066.1780023033297; ALF=1783254488; "
    "SUB=_2A25HJrCIDeRhGeBO7FsT-SnOwj-IHXVkWkxArDV8PUJbkNANLU7ikW1NRapQejQ2ovPnXYwSALgBaAS6pgSMLelo; "
    "SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWbodBFlLwYjaalxysSYhfU5JpX5KMhUgL.Foq7S0.E1KME1Ke2dJLoIEBLxKqLBo-L1h-LxKnLB-qLB-BLxK.LB.zL1KnLxKnLBK-LB.qt; "
    "ULV=1780662500880:3:1:2:1890194193944.2446.1780662500877:1780214090017; "
    "PC_TOKEN=879fa16eba; XSRF-TOKEN=UG2_-Nmyc3rP3vS1W74qDKxh; "
    "WBPSESS=9AA25YPxQAQfkhMOxY5QX1L2Y0mRppODR2aC-VM1dFCNMFBdR_lKw74jD19d5GDxxQ1xnCCNs9iPDJBMSR67GaziWepkTyC38bITTpQ3nac2Hc-dP9RNCmm-Pisb6D6hQT5IatOkX7FQR19YyRlbLw=="
)

INPUT_FILE = "副本a1.csv"
OUTPUT_FILE = "副本a1_爬取结果.csv"  # 不和原文件同名，防止覆盖
MIN_DELAY = 4    # 最小延迟(秒)
MAX_DELAY = 6   # 最大延迟(秒)
# ---------------------------------------------------------------------

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Cookie": COOKIE,
    "Referer": "https://weibo.com/",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua": '"Not A;Brand";v="99", "Chromium";v="148", "Google Chrome";v="148"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "accept-language": "zh-CN,zh;q=0.9"
}

# 使用Session保持会话，模拟真实浏览器
session = requests.Session()
session.headers.update(headers)

def extract_mid(post_url):
    """从链接中提取微博ID"""
    try:
        clean_url = post_url.split("?")[0].strip().rstrip("/")
        return clean_url.split("/")[-1]
    except:
        return None

def get_user_info(uid):
    """通过用户ID获取粉丝数和认证理由"""
    try:
        url = f"https://weibo.com/ajax/profile/info?uid={uid}"
        resp = session.get(url, timeout=15, verify=False)
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return None
        if data.get("ok") == 1:
            u = data["data"]["user"]
            return {
                "followers_count": u.get("followers_count", 0),
                "followers_count_str": u.get("followers_count_str", ""),
                "verified_reason": u.get("verified_reason", ""),
                "verified_type": u.get("verified_type", -1)
            }
    except Exception as e:
        print(f"用户接口异常: {str(e)[:30]}")
    return None

def parse_post(post_url):
    """爬取单条微博的详细数据"""
    mid = extract_mid(post_url)
    if not mid:
        print(f"❌ 无效链接：{post_url}")
        return None

    api_url = f"https://weibo.com/ajax/statuses/show?id={mid}&locale=zh-CN&isGetLongText=true"
    print(f"🔗 请求接口: {api_url}")

    try:
        resp = session.get(api_url, timeout=20, verify=False)
        print(f"📊 响应状态码: {resp.status_code}")

        if resp.status_code != 200:
            print(f"❌ 状态码异常，跳过本条")
            return None

        # 捕获非JSON返回（跳转登录页）
        try:
            data = resp.json()
        except json.JSONDecodeError:
            print("❌ 返回非JSON，账号登录失效/被拦截")
            return None

        if data.get("ok") != 1:
            print(f"❌ 接口拒绝: {data.get('msg','无提示信息')}")
            return None

        status = data
        user = status.get("user", {})
        uid = user.get("idstr", "")

        verified_reason = user.get("verified_reason", "")
        followers_count = user.get("followers_count", 0)

        # 字段缺失则补全用户信息
        if (not verified_reason) or (followers_count == 0):
            user_ext = get_user_info(uid)
            if user_ext:
                if not verified_reason:
                    verified_reason = user_ext["verified_reason"]
                if followers_count == 0:
                    followers_count = user_ext["followers_count"]

        # 认证标签判断
        vtype = user.get("verified_type", -1)
        if vtype == 3:
            verify_tag = "蓝V"
        elif vtype == 0:
            verify_tag = "黄V"
        elif vtype == 220:
            verify_tag = "橙V"
        else:
            verify_tag = "无认证"

        return {
            "博文正文": status.get("text_raw", "").replace("\n", " ").strip(),
            "转发数": status.get("reposts_count", 0),
            "评论数": status.get("comments_count", 0),
            "点赞数": status.get("attitudes_count", 0),
            "发布地点": status.get("region_name", "").replace("发布于 ", "").strip(),
            "认证": verify_tag,
            "认证理由": verified_reason,
            "粉丝数": followers_count,
            "微博等级": user.get("mbrank", user.get("urank", 0))
        }

    except Exception as e:
        print(f"❌ 爬取异常: {str(e)[:50]}")
        return None

if __name__ == "__main__":
    # 兼容编码读取CSV
    try:
        df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    except:
        df = pd.read_csv(INPUT_FILE, encoding="gbk")

    if "帖子链接" not in df.columns:
        print("❌ CSV 缺少【帖子链接】列，请检查文件！")
        exit()

    results = []
    total = len(df)
    for idx, row in df.iterrows():
        # 随机延时，规避风控（第一条不延时）
        if idx > 0:
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            time.sleep(delay)
            print(f"⏱ 随机延时 {delay:.1f}s")

        print(f"\n===== 第 {idx+1}/{total} 条 =====")
        post_url = row["帖子链接"]
        res = parse_post(post_url)

        combined = row.to_dict()
        if res:
            combined.update(res)
            print("✅ 本条爬取成功")
        results.append(combined)

    # 拼接列并导出
    output_columns = df.columns.tolist() + [
        "博文正文", "转发数", "评论数", "点赞数", "发布地点",
        "认证", "认证理由", "粉丝数", "微博等级"
    ]
    df_out = pd.DataFrame(results)[output_columns]
    df_out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\n🎉 全部处理完成！共 {total} 条")
    print(f"📁 结果已保存至: {OUTPUT_FILE}")
