import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# ========== 中文字体设置 ==========
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

# ========== 1. 读取Excel数据（忽略日期列） ==========
file_path = r"E:\可视化\期末作业\票房排片.xlsx"
df_raw = pd.read_excel(file_path, engine='openpyxl')

# 清理列名
df_raw.columns = df_raw.columns.str.strip()
print("原始列名:", df_raw.columns.tolist())

# 只保留需要的数值列，丢弃日期列（如果有）
# 需要的列：票房（万）、排片场次、票房占比、拍片占比
keep_cols = []
for col in ['票房（万）', '排片场次', '票房占比', '拍片占比']:
    if col in df_raw.columns:
        keep_cols.append(col)
    else:
        print(f"警告：列 '{col}' 不存在，请检查Excel列名")
if not keep_cols:
    raise KeyError("未找到必需的数值列")

df = df_raw[keep_cols].copy()

# 转换数值列
for col in ['票房（万）', '排片场次']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 处理百分比列（票房占比和拍片占比），可能包含 "<0.1%" 等特殊值
def parse_percent(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if s == '<0.1%':
        return 0.001   # 视为0.1%
    if '%' in s:
        s = s.replace('%', '')
        try:
            return float(s) / 100.0
        except:
            return np.nan
    try:
        return float(s) / 100.0 if float(s) > 1 else float(s)
    except:
        return np.nan

if '票房占比' in df.columns:
    df['票房占比'] = df['票房占比'].apply(parse_percent)
if '拍片占比' in df.columns:
    df['排片占比'] = df['拍片占比'].apply(parse_percent)
    df.drop(columns=['拍片占比'], inplace=True)

# 删除关键数据缺失的行（票房或排片场次为空）
df = df.dropna(subset=['票房（万）', '排片场次'])
print("有效数据行数:", len(df))

# ========== 2. 生成日期标签（从4月17日开始连续） ==========
start_date = datetime(2026, 4, 17)
date_labels = []
for i in range(len(df)):
    current = start_date + timedelta(days=i)
    date_labels.append(current.strftime('%m月%d日'))  # 例如 "04月17日"

print("生成的日期标签:", date_labels)

# 确定点映期和零点场的索引位置（根据实际日期判断）
# 点映期：4月17日 – 4月28日（共12天）
# 零点场：4月29日
point_indices = []
zero_indices = []
for i, label in enumerate(date_labels):
    # label格式 "04月17日"
    month = int(label.split('月')[0])
    day = int(label.split('月')[1].replace('日', ''))
    if month == 4 and 17 <= day <= 28:
        point_indices.append(i)
    elif month == 4 and day == 29:
        zero_indices.append(i)

print(f"点映期索引: {point_indices} 对应日期: {[date_labels[i] for i in point_indices]}")
print(f"零点场索引: {zero_indices} 对应日期: {[date_labels[i] for i in zero_indices]}")

# ========== 3. 绘图 ==========
x = range(len(df))
x_labels = date_labels

def add_annotations(ax, point_idx, zero_idx):
    if point_idx:
        start = point_idx[0]
        end = point_idx[-1]
        ax.axvspan(start - 0.5, end + 0.5, alpha=0.2, color='gray', label='点映期 (4.17-4.28)')
    if zero_idx:
        for i, idx in enumerate(zero_idx):
            label = '零点场' if i == 0 else ''
            ax.axvline(x=idx, color='orange', linestyle='--', linewidth=2, alpha=0.8, label=label)

# 图1：票房走势（柱状图 + 票房占比折线）
fig, ax1 = plt.subplots(figsize=(14, 6))
ax1.bar(x, df['票房（万）'], color='steelblue', alpha=0.7, label='票房（万）')
ax1.set_xticks(x)
ax1.set_xticklabels(x_labels, rotation=45, ha='right')
ax1.set_xlabel('日期', fontsize=12)
ax1.set_ylabel('票房（万元）', fontsize=12, color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')

if '票房占比' in df.columns:
    ax2 = ax1.twinx()
    ax2.plot(x, df['票房占比'] * 100, color='red', marker='o', linestyle='-', linewidth=2, label='票房占比 (%)')
    ax2.set_ylabel('票房占比 (%)', fontsize=12, color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    add_annotations(ax1, point_indices, zero_indices)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
else:
    add_annotations(ax1, point_indices, zero_indices)
    ax1.legend(loc='upper left')

plt.title('电影每日票房及票房占比走势（点映期及零点场已标注）', fontsize=14)
plt.tight_layout()
plt.savefig(r"E:\可视化\期末作业\票房走势图.png", dpi=150)
plt.show()

# 图2：排片走势（柱状图 + 排片占比折线）
fig, ax1 = plt.subplots(figsize=(14, 6))
ax1.bar(x, df['排片场次'], color='green', alpha=0.7, label='排片场次')
ax1.set_xticks(x)
ax1.set_xticklabels(x_labels, rotation=45, ha='right')
ax1.set_xlabel('日期', fontsize=12)
ax1.set_ylabel('排片场次', fontsize=12, color='green')
ax1.tick_params(axis='y', labelcolor='green')

if '排片占比' in df.columns:
    ax2 = ax1.twinx()
    ax2.plot(x, df['排片占比'] * 100, color='purple', marker='s', linestyle='-', linewidth=2, label='排片占比 (%)')
    ax2.set_ylabel('排片占比 (%)', fontsize=12, color='purple')
    ax2.tick_params(axis='y', labelcolor='purple')
    add_annotations(ax1, point_indices, zero_indices)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
else:
    add_annotations(ax1, point_indices, zero_indices)
    ax1.legend(loc='upper left')

plt.title('电影每日排片场次及排片占比走势（点映期及零点场已标注）', fontsize=14)
plt.tight_layout()
plt.savefig(r"E:\可视化\期末作业\排片走势图.png", dpi=150)
plt.show()

# 图3：票房与排片对比（柱状图 + 排片场次折线）
fig, ax1 = plt.subplots(figsize=(14, 6))
ax1.bar(x, df['票房（万）'], color='steelblue', alpha=0.6, label='票房（万）')
ax1.set_xticks(x)
ax1.set_xticklabels(x_labels, rotation=45, ha='right')
ax1.set_xlabel('日期', fontsize=12)
ax1.set_ylabel('票房（万元）', fontsize=12, color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')

ax2 = ax1.twinx()
ax2.plot(x, df['排片场次'], color='darkorange', marker='o', linestyle='-', linewidth=2, label='排片场次')
ax2.set_ylabel('排片场次', fontsize=12, color='darkorange')
ax2.tick_params(axis='y', labelcolor='darkorange')

add_annotations(ax1, point_indices, zero_indices)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
plt.title('每日票房与排片场次对比（点映期及零点场已标注）', fontsize=14)
plt.tight_layout()
plt.savefig(r"E:\可视化\期末作业\票房排片对比图.png", dpi=150)
plt.show()

print("三张图表已成功生成并保存到 E:\\可视化\\期末作业\\")