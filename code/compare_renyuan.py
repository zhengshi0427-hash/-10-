import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 文件列表及对应的类型名称
files = [
    ('account_蓝V.csv', '蓝V'),
    ('account_黄V橙V.csv', '黄V/橙V'),
    ('account_无认证.csv', '无认证')
]

# 存储各类型的数据
all_data = []

for file, label in files:
    df = pd.read_csv(file, encoding='utf-8-sig')
    # 解析时间（格式：05月22日 16:31）
    df['发布时间'] = pd.to_datetime(df['发布时间'], format='%m月%d日 %H:%M', errors='coerce')
    # 提取日期
    df['日期'] = df['发布时间'].dt.date
    # 按日期统计总条数（不去重）
    daily = df.groupby('日期').size().reset_index(name='总微博数')
    daily['日期'] = pd.to_datetime(daily['日期'])
    daily['类型'] = label
    all_data.append(daily)

# 合并所有类型的数据
combined = pd.concat(all_data, ignore_index=True)

# 绘图
plt.figure(figsize=(14, 6))
# 为每种类型画线
for label in combined['类型'].unique():
    subset = combined[combined['类型'] == label].sort_values('日期')
    plt.plot(subset['日期'], subset['总微博数'], marker='o', linestyle='-', label=label)

# 设置x轴：每天一个刻度，格式为月-日
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
plt.xticks(rotation=45)

plt.title('不同认证类型每天发微博总条数对比', fontsize=14)
plt.xlabel('日期（月-日）', fontsize=12)
plt.ylabel('总微博数', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('三种认证类型每天发博总条数对比.png', dpi=300)
plt.show()