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
os.makedirs(output_dir, exist_ok=True)

# ================== 读取数据 ==================
print("正在读取数据...")
df = pd.read_csv(file_path, encoding='utf-8-sig')
df_text = df[['博文正文', '发布时间']].copy()
df_text.dropna(subset=['博文正文'], inplace=True)

# ================== 情感分析 ==================
def get_sentiment(text):
    if pd.isna(text) or str(text).strip() == "":
        return 0.5
    try:
        return SnowNLP(str(text)).sentiments
    except:
        return 0.5

print("正在进行情感分析...")
df_text['情感分数'] = df_text['博文正文'].apply(get_sentiment)

def sentiment_category(score):
    return '积极' if score > 0.6 else ('消极' if score < 0.4 else '中性')

df_text['情感类别'] = df_text['情感分数'].apply(sentiment_category)

# ================== 按日期分组统计 ==================
def parse_date(date_str):
    try:
        if pd.isna(date_str):
            return None
        parts = str(date_str).split(' ')
        month_day = parts[0]  # "05月22日"
        return datetime.strptime(f"2026{month_day}", "%Y%m月%d日")
    except:
        return None

df_text['日期'] = df_text['发布时间'].apply(parse_date)
df_text.dropna(subset=['日期'], inplace=True)

# 按日期分组，统计每日各类别数量
daily_counts = df_text.groupby([df_text['日期'].dt.date, '情感类别']).size().unstack(fill_value=0)
daily_counts.sort_index(inplace=True)

# 确保三类都存在
for cat in ['积极', '中性', '消极']:
    if cat not in daily_counts.columns:
        daily_counts[cat] = 0

# ================== 绘制折线图（每天日期全部显示） ==================
plt.figure(figsize=(14, 6))

# 绘制三条折线
plt.plot(daily_counts.index, daily_counts['积极'], marker='o', label='积极', color='#2ca02c', linewidth=2)
plt.plot(daily_counts.index, daily_counts['中性'], marker='s', label='中性', color='#ff7f0e', linewidth=2)
plt.plot(daily_counts.index, daily_counts['消极'], marker='^', label='消极', color='#d62728', linewidth=2)

# 设置 x 轴：所有日期都显示，格式为 "月-日"（不显示年份）
# 日期索引是 datetime.date 对象，转换为 "MM-DD" 格式
date_labels = [d.strftime('%m-%d') for d in daily_counts.index]
plt.xticks(ticks=daily_counts.index, labels=date_labels, rotation=45, fontsize=8)

plt.xlabel('日期 (月-日)', fontsize=12)
plt.ylabel('评论数量', fontsize=12)
plt.title('《给阿嬷的情书》评论情感随时间变化趋势（每天标注）', fontsize=14)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# 保存图片
save_path = os.path.join(output_dir, '情感趋势折线图_每天标注.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
plt.show()

print(f"折线图已保存至：{save_path}")