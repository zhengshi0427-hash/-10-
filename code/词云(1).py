import pandas as pd
import numpy as np
import jieba
import re
from wordcloud import WordCloud
from PIL import Image
import matplotlib.pyplot as plt
from collections import Counter

# ====================== 配置区域（只改这里就行）======================
xlsx_file_path = "豆瓣评论.xlsx"       # 你的 Excel 文件
content_col_name = "评论内容"            # 评论内容所在列名（不确定就不用改，代码会自动识别）
sheet_name = 0                           # Excel 里的工作表（0=第一个表，也可以写表名，比如"评论表"）
font_path = "C:/Windows/Fonts/msyh.ttc" # Windows 中文字体（正常不用改）
background_color = "white"               # 词云背景色
colormap = "coolwarm"                    # 配色方案
mask_image_path = None                   # 形状蒙版图片（不需要就留 None）
# =================================================================

# ---------------------- 1. 读取 XLSX 文件（自动识别列名 + 无报错）----------------------
try:
    # 读取 Excel 文件
    df = pd.read_excel(
        xlsx_file_path,
        sheet_name=sheet_name,
        engine="openpyxl"
    )
except Exception as e:
    print(f"读取失败，错误信息：{e}")
    exit()

# 自动打印你文件里的真实列名，再也不会报 KeyError！
print("📋 你 Excel 里的真实列名是：", list(df.columns))

# 自动选择第一列作为评论列（如果你的评论列不是第一列，把这里改成列名就行）
if content_col_name not in df.columns:
    content_col_name = df.columns[0]
    print(f"⚠️  未找到指定列名，已自动使用第一列：{content_col_name}")

# 去掉空评论
df = df[df[content_col_name].notna()].copy()
print(f"✅ 成功读取 {len(df)} 条有效评论")

# ---------------------- 2. 文本清洗 ----------------------
def clean_text(text):
    text = str(text)
    text = re.sub(r'https?://\S+|www.\S+', '', text)    # 去掉网址
    text = re.sub(r'@[\w\u4e00-\u9fa5]+', '', text)     # 去掉@用户
    text = re.sub(r'#.*?#', '', text)                   # 去掉话题
    text = re.sub(r'[^\u4e00-\u9fa5]', ' ', text)       # 只保留中文
    text = re.sub(r'\s+', ' ', text).strip()            # 多余空格清理
    return text

df["清洗后正文"] = df[content_col_name].apply(clean_text)

# ---------------------- 3. 分词 + 去停用词 ----------------------
# 停用词表（可自行增删）
stop_words = {
    "的", "了", "是", "我", "在", "和", "就", "都", "也", "有", "不", "很",
    "你", "他", "她", "这", "那", "什么", "怎么", "我们", "你们", "他们",
    "可以", "但是", "因为", "所以", "一下", "一个", "自己", "没有", "还是",
    "看", "说", "会", "要", "能", "太", "更", "对", "让", "来", "去", "上", "下",
    "这个", "那个", "真的", "感觉", "觉得","一部","电影","豆瓣"
}

def get_words(text):
    words = jieba.lcut(text)
    # 过滤：不在停用词里 + 长度大于1
    words = [w.strip() for w in words if w not in stop_words and len(w) > 1]
    return words

# 开始分词
df["分词结果"] = df["清洗后正文"].apply(get_words)
df["分词结果_文本"] = df["分词结果"].apply(lambda x: " ".join(x))

# ---------------------- 4. 保存分词结果 ----------------------
df_result = df[[content_col_name, "清洗后正文", "分词结果_文本"]].copy()
df_result.columns = ["原始评论", "清洗后评论", "分词结果"]
df_result.to_excel("豆瓣评论分词结果.xlsx", index=False, engine="openpyxl")
print("✅ 分词结果已保存：豆瓣评论分词结果.xlsx")

# ---------------------- 5. 生成词云图 ----------------------
all_words = " ".join(df["分词结果_文本"].dropna().tolist())

wc = WordCloud(
    font_path=font_path,
    background_color=background_color,
    width=1600,
    height=900,
    max_words=500,
    colormap=colormap,
    mask=mask_image_path,
    prefer_horizontal=0.9,
    scale=2,
    contour_width=0
).generate(all_words)

# 显示词云
plt.figure(figsize=(12, 7), dpi=150)
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()

# 保存词云图片
wc.to_file("豆瓣词云图.png")
print("✅ 词云图已保存：豆瓣词云图.png")

# ---------------------- 6. 词频统计并保存 ----------------------
word_list = []
for words in df["分词结果"]:
    word_list.extend(words)

word_count = Counter(word_list)
word_freq_df = pd.DataFrame(word_count.most_common(), columns=["关键词", "出现次数"])
word_freq_df.to_excel("豆瓣词频统计结果.xlsx", index=False, engine="openpyxl")
print("✅ 词频统计已保存：豆瓣词频统计结果.xlsx")

print("\n🎉 全部分析完成！")