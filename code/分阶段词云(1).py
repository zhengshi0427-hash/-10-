import pandas as pd
import jieba
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# ====================== 配置区域 ======================
csv_file_path = "account.csv"
content_col_name = "博文正文"
time_col_name = "发布时间"

# 分阶段：5月8日 及以前 = 第一阶段
split_month = 5
split_day = 8

font_path = "C:/Windows/Fonts/msyh.ttc"
background_color = "white"
colormap = "coolwarm"
# ======================================================

# ---------------------- 1. 读取数据 ----------------------
try:
    df = pd.read_csv(csv_file_path, encoding="gbk")
except:
    df = pd.read_csv(csv_file_path, encoding="utf-8")

df = df[df[content_col_name].notna()].copy()
df = df[df[time_col_name].notna()].copy()

# ---------------------- 2. 解析 05月22日 16:31 格式 ----------------------
def parse_month_day(time_str):
    try:
        month = int(time_str[:2])
        day = int(time_str[3:5])
        return month, day
    except:
        return 0, 0

df["月"], df["日"] = zip(*df[time_col_name].apply(parse_month_day))

# ---------------------- 3. 自动分两个阶段 ----------------------
def is_before_or_equal(row):
    m = row["月"]
    d = row["日"]
    if m < split_month:
        return True
    if m == split_month and d <= split_day:
        return True
    return False

df["阶段"] = df.apply(is_before_or_equal, axis=1)

df_stage1 = df[df["阶段"] == True].copy()  # 5.8前
df_stage2 = df[df["阶段"] == False].copy() # 5.8后

print(f"✅ 第一阶段（5.8及以前）：{len(df_stage1)} 条")
print(f"✅ 第二阶段（5.8以后）：{len(df_stage2)} 条")

# ---------------------- 停用词 ----------------------
stop_words = {
    "的", "了", "是", "我", "在", "和", "就", "都", "也", "有", "不", "很",
    "你", "他", "她", "这", "那", "什么", "怎么", "我们", "你们", "他们",
    "可以", "但是", "因为", "所以", "一下", "一个", "自己", "没有", "还是"
}

# ---------------------- 清洗 + 分词 ----------------------
def clean_text(text):
    text = re.sub(r'https?://\S+|www.\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#.*?#', '', text)
    text = re.sub(r'[^\u4e00-\u9fa5]', ' ', text)
    return text.strip()

def process_words(text):
    words = jieba.lcut(text)
    return [w for w in words if w not in stop_words and len(w) > 1]

# ---------------------- 处理阶段 ----------------------
def process(df, name):
    if len(df) == 0:
        print(f"⚠️ {name} 无数据，跳过")
        return ""
    
    df["清洗后"] = df[content_col_name].apply(clean_text)
    df["分词"] = df["清洗后"].apply(process_words)
    df["分词文本"] = df["分词"].apply(lambda x: " ".join(x))
    
    # 保存分词结果
    df[["博文正文", "发布时间", "分词文本"]].to_csv(
        f"{name}_分词结果.csv", index=False, encoding="utf-8-sig"
    )
    
    all_words = []
    for w in df["分词"]:
        all_words.extend(w)
    
    if not all_words:
        print(f"⚠️ {name} 无有效词语")
        return ""
    
    # 保存词频
    freq = Counter(all_words).most_common()
    pd.DataFrame(freq, columns=["关键词", "次数"]).to_csv(
        f"{name}_词频.csv", index=False, encoding="utf-8-sig"
    )
    
    return " ".join(df["分词文本"])

# ---------------------- 执行 ----------------------
words1 = process(df_stage1, "第一阶段_5.8前")
words2 = process(df_stage2, "第二阶段_5.8后")

# ---------------------- 画词云（防错版） ----------------------
def draw(words, title, filename):
    if not words:
        return
    wc = WordCloud(
        font_path=font_path,
        background_color=background_color,
        width=1600, height=900,
        colormap=colormap, scale=2
    ).generate(words)
    wc.to_file(filename)
    
    plt.figure(figsize=(12,7))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title(title, fontsize=18)
    plt.show()

draw(words1, "第一阶段（5.8及以前）", "第一阶段_词云图.png")
draw(words2, "第二阶段（5.8以后）", "第二阶段_词云图.png")

print("\n🎉 全部完成！")