import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
df = pd.read_csv('account.csv', encoding='utf-8-sig')

# 解析发布时间（格式：05月22日 16:31）
df['发布时间'] = pd.to_datetime(df['发布时间'], format='%m月%d日 %H:%M', errors='coerce')
df['日期'] = df['发布时间'].dt.date

# 定义地域分组：广东 vs 其他（发布地点可能为空或非广东）
df['地域'] = df['发布地点'].apply(lambda x: '广东' if x == '广东' else '其他')

# 按日期和地域统计微博条数（不去重）
daily = df.groupby(['日期', '地域']).size().reset_index(name='微博数')
daily['日期'] = pd.to_datetime(daily['日期'])

# 拆分广东和其他数据
guangdong = daily[daily['地域'] == '广东'].sort_values('日期')
other = daily[daily['地域'] == '其他'].sort_values('日期')

# 绘图
plt.figure(figsize=(14, 6))
plt.plot(guangdong['日期'], guangdong['微博数'], marker='o', linestyle='-', label='广东', color='red')
plt.plot(other['日期'], other['微博数'], marker='s', linestyle='--', label='其他省份', color='blue')

# 设置x轴：每天一个刻度，格式为月-日
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
plt.xticks(rotation=45)

plt.title('广东 vs 其他省份每天发微博总条数对比（不去重）', fontsize=14)
plt.xlabel('日期（月-日）', fontsize=12)
plt.ylabel('微博数', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('广东与其他省份每天发博总条数对比.png', dpi=300)
plt.show()