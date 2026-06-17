import requests
import time
import pandas as pd
from lxml import etree

# ==================== 配置区域 ====================
base_url = "https://s.weibo.com/weibo"

# 你要爬的新URL参数
params = {
    "q": "#电影给阿嬷的情书#",
    "typeall": "1",
    "suball": "1",
    "timescope": "custom:2026-05-02-0:2026-05-02-23",
    "Refer": "g"
}

# 请求头（你必须自己更新这里的cookie！）
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "cookie": "SCF=Am-Ulk9b88kquOgbMFctzWzS32oyz9OVDDLtugMByXNEkECqsCty2Utzov_QGPXcdvcLJvapVLpe9YnHj0BbWYA.; SUB=_2A25HHI6eDeRhGeBO7FsT-SnOwj-IHXVkU45WrDV8PUNbmtANLRjakW9NRapQelivQz-Gg3kWpfPJz6qlYN-LvaEK; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWbodBFlLwYjaalxysSYhfU5JpX5KzhUgL.Foq7S0.E1KME1Ke2dJLoIEBLxKqLBo-L1h-LxKnLB-qLB-BLxK.LB.zL1KnLxKnLBK-LB.qt; ALF=02_1782614990; _s_tentry=weibo.com; Apache=515186429630.80066.1780023033297; SINAGLOBAL=515186429630.80066.1780023033297; ULV=1780023033298:1:1:1:515186429630.80066.1780023033297:",
    "referer": "https://s.weibo.com/",
    "sec-ch-ua": '"Chromium";v="148","Microsoft Edge";v="99","Not=A?Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0"
}

csv_columns = [
    "帖子链接", "用户昵称", "用户ID", "博文ID",
    "发布时间", "博文正文", "转发数", "评论数", "点赞数"
]
all_data = []

# ==================== 工具函数 ====================
def get_digit(text_list):
    if not text_list:
        return "0"
    raw = "".join(text_list).strip()
    return "".join([c for c in raw if c.isdigit()]) or "0"

# ===================== 新增：获取展开全文 =====================
def get_full_content(url):
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        tree = etree.HTML(resp.text)
        full_text = tree.xpath('//div[@node-type="feed_list_content"]//text()')
        return "".join([t.strip() for t in full_text if t.strip()])
    except:
        return ""

def parse_page(html):
    if "登录" in html or "请登录" in html:
        print("❌ 当前是登录页，Cookie 失效，爬不到数据")
        return

    tree = etree.HTML(html)
    card_list = tree.xpath('//div[@class="card-wrap" and @action-type="feed_list_item"]')

    for card in card_list:
        item = {}
        item["博文ID"] = card.get("mid", "")

        time_a = card.xpath('.//div[@class="from"]/a[1]')
        if time_a:
            post_href = time_a[0].get("href", "")
            item["帖子链接"] = f"https:{post_href}" if post_href else ""
            item["发布时间"] = time_a[0].text.strip() if time_a[0].text else ""

        name_a = card.xpath('.//a[@class="name"]')
        if name_a:
            item["用户昵称"] = name_a[0].text.strip() if name_a[0].text else ""
            user_href = name_a[0].get("href", "")
            if "/u/" in user_href:
                item["用户ID"] = user_href.split("/u/")[-1].split("?")[0]
            else:
                item["用户ID"] = user_href.split("/")[-1].split("?")[0]

        # ===================== 关键修改：自动取展开全文 =====================
        content_text = card.xpath('.//p[@class="txt" and @node-type="feed_list_content"]//text()')
        short_content = "".join([t.strip() for t in content_text if t.strip()])
        item["博文正文"] = short_content

        # 如果有“展开”，就去拿完整内容
        if "展开" in short_content and item["帖子链接"]:
            full = get_full_content(item["帖子链接"])
            if full:
                item["博文正文"] = full

        # 互动数据
        forward_text = card.xpath('.//a[@action-type="feed_list_forward"]//text()')
        comment_text = card.xpath('.//a[@action-type="feed_list_comment"]//text()')
        like_text = card.xpath('.//span[@class="woo-like-count"]//text()')

        item["转发数"] = get_digit(forward_text)
        item["评论数"] = get_digit(comment_text)
        item["点赞数"] = get_digit(like_text)

        if item["用户昵称"] and item["博文正文"]:
            all_data.append(item)

# ==================== 主逻辑 ====================
if __name__ == "__main__":
    page = 1
    while True:
        print(f"正在爬取第 {page} 页")
        current_params = params.copy()
        if page > 1:
            current_params["page"] = page

        try:
            resp = requests.get(base_url, headers=headers, params=current_params, timeout=20)
            resp.raise_for_status()
        except Exception as e:
            print(f"请求异常：{e}")
            break

        parse_page(resp.text)

        next_page = etree.HTML(resp.text).xpath('//a[@class="next"]/@href')
        if not next_page:
            print("已到最后一页")
            break

        page += 1
        time.sleep(3)

    df = pd.DataFrame(all_data, columns=csv_columns)
    df.to_csv("weibo_5.02_0-5.02_23数据.csv", index=False, encoding="utf-8-sig")
    print(f"完成，共 {len(all_data)} 条数据")
