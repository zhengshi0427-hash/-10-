import pandas as pd
import matplotlib.pyplot as plt
from snownlp import SnowNLP
from datetime import datetime
import os

# ================== 中文字体设置 ==================
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

# ================== 文件路径 ==================
file_path = r"E:\可视化\期末作业\account.csv"
output_dir = r"E:\可视化\期末作业"

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# ================== 读取数据 ==================
print("正在读取数据...")
df = pd.read_csv(file_path, encoding='utf-8-sig')
print(f"数据形状：{df.shape}")
print(f"列名：{df.columns.tolist()}")

# 提取必要列：博文正文、发布时间
df_text = df[['博文正文', '发布时间']].copy()
df_text.dropna(subset=['博文正文'], inplace=True)
print(f"有效评论数：{len(df_text)}")

# ================== 情感分析函数 ==================
def get_sentiment(text):
    if pd.isna(text) or str(text).strip() == "":
        return 0.5
    try:
        s = SnowNLP(str(text))
        return s.sentiments
    except:
        return 0.5

print("正在进行情感分析（可能需要几分钟），请稍候...")
df_text['情感分数'] = df_text['博文正文'].apply(get_sentiment)

# ================== 情感分类 ==================
def sentiment_category(score):
    if score > 0.6:
        return '积极'
    elif score < 0.4:
        return '消极'
    else:
        return '中性'

df_text['情感类别'] = df_text['情感分数'].apply(sentiment_category)

# 统计分布
category_counts = df_text['情感类别'].value_counts()
print("\n情感分布统计：")
print(category_counts)

# ================== 1. 情感分布环形图 ==================
plt.figure(figsize=(8, 6))
# 环形图：通过 wedgeprops 设置宽度
colors = {'积极': '#2ca02c', '中性': '#ff7f0e', '消极': '#d62728'}
pie_colors = [colors[cat] for cat in category_counts.index]
plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%',
        startangle=90, colors=pie_colors, wedgeprops=dict(width=0.6))
plt.title('《给阿嬷的情书》评论情感分布环形图', fontsize=14)
plt.savefig(os.path.join(output_dir, '情感分布环形图.png'), dpi=300, bbox_inches='tight')
plt.show()
print("情感分布环形图已保存")

# ================== 2. 情感随时间变化趋势 ==================
# 解析发布时间中的日期（格式如 "05月22日 16:31"）
def parse_date(date_str):
    try:
        if pd.isna(date_str):
            return None
        parts = str(date_str).split(' ')
        month_day = parts[0]  # "05月22日"
        # 假设年份为2026
        dt = datetime.strptime(f"2026{month_day}", "%Y%m月%d日")
        return dt
    except:
        return None

df_text['日期'] = df_text['发布时间'].apply(parse_date)
df_text.dropna(subset=['日期'], inplace=True)
print(f"有效日期评论数：{len(df_text)}")

# 按日期分组，统计每日各类别数量
daily_counts = df_text.groupby([df_text['日期'].dt.date, '情感类别']).size().unstack(fill_value=0)
daily_counts.sort_index(inplace=True)

# 确保所有类别都存在
for cat in ['积极', '中性', '消极']:
    if cat not in daily_counts.columns:
        daily_counts[cat] = 0

# 2.1 折线图
plt.figure(figsize=(12, 6))
plt.plot(daily_counts.index, daily_counts['积极'], marker='o', label='积极', color='#2ca02c')
plt.plot(daily_counts.index, daily_counts['中性'], marker='s', label='中性', color='#ff7f0e')
plt.plot(daily_counts.index, daily_counts['消极'], marker='^', label='消极', color='#d62728')
plt.xlabel('日期', fontsize=12)
plt.ylabel('评论数量', fontsize=12)
plt.title('《给阿嬷的情书》评论情感随时间变化趋势（折线图）', fontsize=14)
plt.xticks(rotation=45)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '情感趋势折线图.png'), dpi=300, bbox_inches='tight')
plt.show()
print("情感趋势折线图已保存")

# 2.2 堆叠面积图
plt.figure(figsize=(12, 6))
plt.stackplot(daily_counts.index,
              daily_counts['积极'], daily_counts['中性'], daily_counts['消极'],
              labels=['积极', '中性', '消极'],
              colors=['#2ca02c', '#ff7f0e', '#d62728'], alpha=0.7)
plt.xlabel('日期', fontsize=12)
plt.ylabel('评论数量', fontsize=12)
plt.title('《给阿嬷的情书》评论情感堆叠面积图', fontsize=14)
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '情感趋势堆叠面积图.png'), dpi=300, bbox_inches='tight')
plt.show()
print("堆叠面积图已保存")

# ================== 3. 选取典型评论示例 ==================
positive_df = df_text[df_text['情感类别'] == '积极'].sort_values('情感分数', ascending=False)
negative_df = df_text[df_text['情感类别'] == '消极'].sort_values('情感分数', ascending=True)

# 取前5条（若不足则全部）
pos_samples = positive_df.head(5)
neg_samples = negative_df.head(5)

print("\n========== 典型积极评论示例 ==========")
for i, (idx, row) in enumerate(pos_samples.iterrows(), 1):
    print(f"示例{i} | 情感分数: {row['情感分数']:.4f}")
    content = row['博文正文'][:300] + ('...' if len(row['博文正文']) > 300 else '')
    print(f"内容: {content}")
    print("-" * 50)

print("\n========== 典型消极评论示例 ==========")
for i, (idx, row) in enumerate(neg_samples.iterrows(), 1):
    print(f"示例{i} | 情感分数: {row['情感分数']:.4f}")
    content = row['博文正文'][:300] + ('...' if len(row['博文正文']) > 300 else '')
    print(f"内容: {content}")
    print("-" * 50)

# 保存示例到文本文件
with open(os.path.join(output_dir, '典型评论示例.txt'), 'w', encoding='utf-8') as f:
    f.write("典型积极评论示例：\n")
    for i, (idx, row) in enumerate(pos_samples.iterrows(), 1):
        f.write(f"示例{i} | 分数: {row['情感分数']:.4f}\n")
        f.write(f"内容: {row['博文正文']}\n")
        f.write("-" * 50 + "\n")
    f.write("\n典型消极评论示例：\n")
    for i, (idx, row) in enumerate(neg_samples.iterrows(), 1):
        f.write(f"示例{i} | 分数: {row['情感分数']:.4f}\n")
        f.write(f"内容: {row['博文正文']}\n")
        f.write("-" * 50 + "\n")

print(f"\n所有结果已保存至：{output_dir}")