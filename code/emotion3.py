# -*- coding: utf-8 -*-
"""
豆瓣评论情感分析（《给阿嬷的情书》）
输入：合并去重_按点赞排序_豆瓣评论 的副本.xlsx
输出：情感分布图、情感趋势图、点赞数与情感关系图、分类结果Excel
"""

import pandas as pd
import matplotlib.pyplot as plt
from snownlp import SnowNLP
from datetime import datetime
import os
import numpy as np

# ================== 中文字体设置 ==================
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

# ================== 文件路径 ==================
# 请根据实际位置修改文件路径
file_path = r"合并去重_按点赞排序_豆瓣评论 的副本.xlsx"  # 默认当前目录，可改为绝对路径
output_dir = r"情感分析结果"  # 输出文件夹

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# ================== 读取数据 ==================
print("正在读取Excel数据...")
try:
    df = pd.read_excel(file_path, engine='openpyxl')
    print(f"数据形状：{df.shape}")
    print(f"列名：{df.columns.tolist()}")
except FileNotFoundError:
    print(f"错误：找不到文件 {file_path}，请检查路径")
    exit(1)
except Exception as e:
    print(f"读取Excel失败：{e}")
    exit(1)

# 检查必要的列
text_col = '评论内容'
time_col = '评论时间'
likes_col = '点赞数'

if text_col not in df.columns:
    print(f"错误：缺少'{text_col}'列，现有列：{df.columns.tolist()}")
    exit(1)
if time_col not in df.columns:
    print(f"警告：缺少'{time_col}'列，将跳过时间趋势分析")
    has_time = False
else:
    has_time = True
if likes_col not in df.columns:
    print(f"警告：缺少'{likes_col}'列，将跳过点赞数分析")
    has_likes = False
else:
    has_likes = True

# 提取必要列
df_text = df[[text_col, time_col] + ([likes_col] if has_likes else [])].copy()
df_text.rename(columns={text_col: '评论内容', time_col: '发布时间'}, inplace=True)
if has_likes:
    df_text.rename(columns={likes_col: '点赞数'}, inplace=True)

# 删除评论内容为空的记录
df_text.dropna(subset=['评论内容'], inplace=True)
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
df_text['情感分数'] = df_text['评论内容'].apply(get_sentiment)

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
colors = {'积极': '#2ca02c', '中性': '#ff7f0e', '消极': '#d62728'}
pie_colors = [colors[cat] for cat in category_counts.index]
plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%',
        startangle=90, colors=pie_colors, wedgeprops=dict(width=0.6))
plt.title('《给阿嬷的情书》豆瓣评论情感分布环形图', fontsize=14)
plt.savefig(os.path.join(output_dir, '情感分布环形图.png'), dpi=300, bbox_inches='tight')
plt.show()
print("情感分布环形图已保存")

# ================== 2. 情感随时间变化趋势 ==================
if has_time:
    # 解析评论时间（格式示例：2026-05-01 或 2026-05-01 12:00:00）
    def parse_date(date_str):
        try:
            if pd.isna(date_str):
                return None
            # 尝试多种格式
            date_str = str(date_str).strip()
            # 如果是 "2026-05-01" 格式
            if '-' in date_str:
                dt = datetime.strptime(date_str.split(' ')[0], "%Y-%m-%d")
            elif '年' in date_str:
                dt = datetime.strptime(date_str, "%Y年%m月%d日")
            else:
                # 尝试其他常见格式
                dt = datetime.strptime(date_str, "%Y/%m/%d")
            return dt
        except:
            return None

    df_text['日期'] = df_text['发布时间'].apply(parse_date)
    df_text.dropna(subset=['日期'], inplace=True)
    print(f"有效日期评论数：{len(df_text)}")

    # 按日期分组统计各类别数量
    daily_counts = df_text.groupby([df_text['日期'].dt.date, '情感类别']).size().unstack(fill_value=0)
    daily_counts.sort_index(inplace=True)
    for cat in ['积极', '中性', '消极']:
        if cat not in daily_counts.columns:
            daily_counts[cat] = 0

    # 2.1 折线图（标出每天日期）
    plt.figure(figsize=(12, 6))
    plt.plot(daily_counts.index, daily_counts['积极'], marker='o', label='积极', color='#2ca02c', linewidth=2)
    plt.plot(daily_counts.index, daily_counts['中性'], marker='s', label='中性', color='#ff7f0e', linewidth=2)
    plt.plot(daily_counts.index, daily_counts['消极'], marker='^', label='消极', color='#d62728', linewidth=2)
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('评论数量', fontsize=12)
    plt.title('《给阿嬷的情书》豆瓣评论情感随时间变化趋势（折线图）', fontsize=14)
    plt.xticks(rotation=45)
    # 设置x轴刻度为每天，若日期太多可自动旋转
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.DayLocator(interval=1))
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
    plt.title('《给阿嬷的情书》豆瓣评论情感堆叠面积图', fontsize=14)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '情感趋势堆叠面积图.png'), dpi=300, bbox_inches='tight')
    plt.show()
    print("堆叠面积图已保存")

# ================== 3. 点赞数与情感的可视化分析 ==================
if has_likes:
    # 将点赞数转为数值，无效值填充0
    df_text['点赞数'] = pd.to_numeric(df_text['点赞数'], errors='coerce').fillna(0)
    # 去除点赞数为0的噪音（可选）
    df_likes_valid = df_text[df_text['点赞数'] > 0].copy()
    
    if len(df_likes_valid) > 0:
        # 3.1 箱线图：不同情感类别的点赞数分布
        plt.figure(figsize=(10, 6))
        # 按情感类别分组绘制箱线图
        data_to_plot = [df_likes_valid[df_likes_valid['情感类别'] == cat]['点赞数'].values 
                        for cat in ['积极', '中性', '消极'] if cat in df_likes_valid['情感类别'].unique()]
        positions = [1, 2, 3]
        bp = plt.boxplot(data_to_plot, positions=positions, widths=0.6,
                         patch_artist=True,
                         boxprops=dict(facecolor='lightblue', color='black'),
                         medianprops=dict(color='red', linewidth=2),
                         whiskerprops=dict(color='black'),
                         capprops=dict(color='black'))
        plt.xticks(positions, ['积极', '中性', '消极'])
        plt.xlabel('情感类别', fontsize=12)
        plt.ylabel('点赞数', fontsize=12)
        plt.title('不同情感类别的豆瓣评论点赞数分布（箱线图）', fontsize=14)
        plt.yscale('log')  # 点赞数通常跨度大，使用对数刻度
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '点赞数_箱线图.png'), dpi=300, bbox_inches='tight')
        plt.show()
        print("点赞数箱线图已保存")
        
        # 3.2 散点图：情感分数 vs 点赞数
        plt.figure(figsize=(10, 6))
        # 根据情感类别设置不同颜色
        colors_map = {'积极': '#2ca02c', '中性': '#ff7f0e', '消极': '#d62728'}
        for cat, group in df_likes_valid.groupby('情感类别'):
            plt.scatter(group['情感分数'], group['点赞数'], 
                        label=cat, color=colors_map[cat], alpha=0.6, s=30)
        plt.xlabel('情感分数（越接近1越积极）', fontsize=12)
        plt.ylabel('点赞数', fontsize=12)
        plt.title('豆瓣评论情感分数与点赞数的关系', fontsize=14)
        plt.yscale('log')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '点赞数_散点图.png'), dpi=300, bbox_inches='tight')
        plt.show()
        print("点赞数散点图已保存")
        
        # 可选：计算各情感类别的平均点赞数
        mean_likes = df_likes_valid.groupby('情感类别')['点赞数'].mean().sort_values(ascending=False)
        print("\n各情感类别平均点赞数：")
        print(mean_likes)
    else:
        print("没有点赞数大于0的记录，跳过点赞数分析")
else:
    print("Excel中没有点赞数列，跳过点赞数分析")

# ================== 4. 选取典型评论示例 ==================
positive_df = df_text[df_text['情感类别'] == '积极'].sort_values('情感分数', ascending=False)
negative_df = df_text[df_text['情感类别'] == '消极'].sort_values('情感分数', ascending=True)

pos_samples = positive_df.head(5)
neg_samples = negative_df.head(5)

print("\n========== 典型积极评论示例 ==========")
for i, (idx, row) in enumerate(pos_samples.iterrows(), 1):
    print(f"示例{i} | 情感分数: {row['情感分数']:.4f}")
    content = row['评论内容'][:300] + ('...' if len(row['评论内容']) > 300 else '')
    print(f"内容: {content}")
    print("-" * 50)

print("\n========== 典型消极评论示例 ==========")
for i, (idx, row) in enumerate(neg_samples.iterrows(), 1):
    print(f"示例{i} | 情感分数: {row['情感分数']:.4f}")
    content = row['评论内容'][:300] + ('...' if len(row['评论内容']) > 300 else '')
    print(f"内容: {content}")
    print("-" * 50)

# 保存示例到文本文件
with open(os.path.join(output_dir, '典型评论示例.txt'), 'w', encoding='utf-8') as f:
    f.write("典型积极评论示例：\n")
    for i, (idx, row) in enumerate(pos_samples.iterrows(), 1):
        f.write(f"示例{i} | 分数: {row['情感分数']:.4f}\n")
        f.write(f"内容: {row['评论内容']}\n")
        f.write("-" * 50 + "\n")
    f.write("\n典型消极评论示例：\n")
    for i, (idx, row) in enumerate(neg_samples.iterrows(), 1):
        f.write(f"示例{i} | 分数: {row['情感分数']:.4f}\n")
        f.write(f"内容: {row['评论内容']}\n")
        f.write("-" * 50 + "\n")

# ================== 5. 保存分类结果 ==================
output_excel = os.path.join(output_dir, '豆瓣评论_情感分析结果.xlsx')
df_text.to_excel(output_excel, index=False, engine='openpyxl')
print(f"\n情感分析结果已保存至：{output_excel}")
print(f"所有图表和文件已保存至文件夹：{output_dir}")