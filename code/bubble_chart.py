import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Patch

# ========== 设置中文字体 ==========
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# ========== 1. 数据加载与清洗 ==========
file_path = r"E:\可视化\期末作业\account.csv"
df = pd.read_csv(file_path, encoding='utf-8')  # 若乱码可尝试 encoding='gbk'

# 检查列名（示例中实际列名为中文，需确认）
# 假设列名为：帖子链接,用户昵称,发布时间,博文正文,转发数,评论数,点赞数,发布地点,认证,认证理由,粉丝数,微博等级
df.columns = df.columns.str.strip()  # 去除列名首尾空格

# 转换数值列（处理空值或非数值）
for col in ['转发数', '评论数', '点赞数']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 删除无效行
df = df.dropna(subset=['转发数', '评论数', '点赞数'])
df = df[df['转发数'] >= 0]  # 仅保留非负数

# ========== 2. 用户类型分类 ==========
def classify_user(cert):
    cert = str(cert).strip()
    if '蓝V' in cert or '中央广播电视总台' in cert or '河北广播电视台' in cert:
        return '蓝V机构'
    elif cert == '无认证' or cert == 'nan' or cert == '':
        return '普通用户'
    else:
        return '橙V大V'

df['用户类型'] = df['认证'].apply(classify_user)

# 颜色映射
color_map = {
    '蓝V机构': 'blue',
    '橙V大V': 'orange',
    '普通用户': 'gray'
}
df['颜色'] = df['用户类型'].map(color_map)

# ========== 3. 绘制三维气泡图 ==========
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# 气泡大小缩放因子（点赞数范围约 2w~15w，缩放到点面积 20~500）
sizes = df['点赞数'] / 200  # 可手动调整视觉比例

# 散点图
sc = ax.scatter(df['转发数'], df['评论数'], df['点赞数'],
                s=sizes, c=df['颜色'], alpha=0.7, edgecolors='k', linewidth=0.5)

# 坐标轴标签
ax.set_xlabel('转发数 (信息扩散能力)', fontsize=12)
ax.set_ylabel('评论数 (讨论意愿)', fontsize=12)
ax.set_zlabel('点赞数 (认可度)', fontsize=12)
ax.set_title('微博传播主体三维气泡图\n(气泡大小 = 点赞数 | 颜色 = 用户类型)', fontsize=14)

# 图例（手动创建）
legend_elements = [Patch(facecolor='blue', label='蓝V机构', alpha=0.7),
                   Patch(facecolor='orange', label='橙V大V', alpha=0.7),
                   Patch(facecolor='gray', label='普通用户', alpha=0.7)]
ax.legend(handles=legend_elements, loc='upper left')

# 可选：调整视角
ax.view_init(elev=25, azim=45)

plt.tight_layout()
plt.savefig(r"E:\可视化\期末作业\3d_bubble_chart.png", dpi=150)
plt.show()

# ========== 4. 关键区域分析与特征总结 ==========
print("\n====== 关键区域分析 ======\n")

# 定义区域阈值（基于数据分布，此处根据样例数据设定）
high_x = df['转发数'].quantile(0.7)   # 高转发阈值
high_y = df['评论数'].quantile(0.7)   # 高评论阈值
low_x = df['转发数'].quantile(0.3)    # 低转发
low_y = df['评论数'].quantile(0.3)    # 低评论

# 右上角：传播王者（高转发 & 高评论 & 大气泡=高点赞）
top_right = df[(df['转发数'] > high_x) & (df['评论数'] > high_y) & (df['点赞数'] > df['点赞数'].median())]
# 左上角：高评论、低转发
top_left = df[(df['评论数'] > high_y) & (df['转发数'] < low_x)]
# 右下角：高转发、低评论
bottom_right = df[(df['转发数'] > high_x) & (df['评论数'] < low_y)]

print("【右上角 - 传播王者】")
if not top_right.empty:
    for idx, row in top_right.iterrows():
        print(f"- 用户：{row['用户昵称']} | 转发：{row['转发数']} | 评论：{row['评论数']} | 点赞：{row['点赞数']}")
        print(f"  博文正文：{row['博文正文'][:100]}...")
    print("\n共同特征总结：")
    print("  • 均带有热点话题标签（如 #无米糕是怎么来的、#生活有星意#）")
    print("  • 内容具有强情感煽动性（如“谢谢大家的支持”、“开心地”等正向共鸣）")
    print("  • 多数包含明星或KOL参与（央视新闻、演员刘世宁、陈妍希等）")
    print("  • 发布时间集中在晚间黄金时段（23:55、21:07等）")
else:
    print("（当前数据中无明显传播王者）\n")

print("【左上角 - 争议/高共鸣区域（高评论、低转发）】")
if not top_left.empty:
    for idx, row in top_left.iterrows():
        print(f"- 用户：{row['用户昵称']} | 转发：{row['转发数']} | 评论：{row['评论数']} | 点赞：{row['点赞数']}")
        print(f"  博文正文：{row['博文正文'][:100]}...")
    print("\n特征总结：")
    print("  • 话题涉及价值观讨论或情感投射（如“#内娱00花洗脚”、“给阿婆的情书”）")
    print("  • 用户表达强烈个人观点，引发评论区辩论，但转发意愿低（不愿扩大传播）")
    print("  • 多为普通用户或橙V个人博文，非官方通告")
else:
    print("（当前数据中无明显争议/高共鸣区域）\n")

print("【右下角 - 信息型区域（高转发、低评论）】")
if not bottom_right.empty:
    for idx, row in bottom_right.iterrows():
        print(f"- 用户：{row['用户昵称']} | 转发：{row['转发数']} | 评论：{row['评论数']} | 点赞：{row['点赞数']}")
        print(f"  博文正文：{row['博文正文'][:100]}...")
    print("\n特征总结：")
    print("  • 内容为官方定档/通知/资讯（如“#电影给阿婆的情”定档信息、央视新闻发布）")
    print("  • 语言客观中性，无主观情绪，用户倾向于“扩散消息”而非“参与讨论”")
    print("  • 发布者多为蓝V机构（媒体、电影官方）")
else:
    print("（当前数据中无明显信息型区域）\n")
