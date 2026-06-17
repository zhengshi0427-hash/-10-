# -*- coding: utf-8 -*-
"""
《给阿嬷的情书》微博帖子主题分类与可视化
所有扇区依次突出的浅蓝色饼图
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 1. 读取数据 ====================
file_path = 'account.csv'
try:
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    print(f"成功读取数据，共 {len(df)} 条帖子")
except FileNotFoundError:
    print("错误：找不到 account.csv 文件，请将文件放在脚本同目录下")
    exit(1)

if '博文正文' not in df.columns:
    print("错误：CSV文件中没有'博文正文'列")
    exit(1)

df['text'] = df['博文正文'].fillna('').astype(str)

# ==================== 2. 分类关键词 ====================
categories = {
    '剧情/故事': ['剧情', '故事', '情节', '反转', '结局', '剧透', '彩蛋', '细节', '信件', '侨批', '情书', '书信', '家书'],
    '角色人物': ['南枝', '淑柔', '木生', '谢南枝', '叶淑柔', '郑木生', '角色', '人物', '阿嬷', '阿公', '番客', '老姨', '泽华'],
    '演员/表演': ['李思潼', '王彦桐', '吴少卿', '王晓慧', '演员', '演技', '素人', '主演', '选角', '表演'],
    '城市/文化': ['潮汕', '汕头', '揭阳', '潮州', '南洋', '泰国', '暹罗', '民俗', '工夫茶', '英歌', '美食', '无米粿', '橄榄', '木棉花', '侨批文化', '潮汕话'],
    '票房/口碑': ['票房', '评分', '豆瓣', '口碑', '黑马', '破亿', '逆袭', '排片', '数据', '预测', '爆款'],
    '幕后/制作': ['导演', '拍摄', '剧组', '采访', '路演', '花絮', '幕后', '成本', '赞助', '制片', '编剧'],
    '观众/反响': ['推荐', '安利', '泪崩', '感动', '自来水', '共鸣', '影评', '反应', '观众', '网友', '好评', '哭', '泪目', '破防'],
    '其他': []
}

def classify_by_keywords(text):
    if not isinstance(text, str):
        return '其他'
    text_lower = text.lower()
    scores = {}
    for cat, keywords in categories.items():
        if cat == '其他':
            continue
        count = sum(1 for kw in keywords if kw.lower() in text_lower)
        scores[cat] = count
    if not scores:
        return '其他'
    max_cat = max(scores, key=scores.get)
    if scores[max_cat] == 0:
        return '其他'
    return max_cat

df['category'] = df['text'].apply(classify_by_keywords)
cat_counts = df['category'].value_counts()
print("\n分类统计结果：")
print(cat_counts)

# ==================== 3. 绘制所有扇区依次突出的浅蓝色饼图 ====================
def plot_all_explode_light_blue_pie(data, title, save_path=None):
    labels = data.index
    sizes = data.values
    
    # 更浅的蓝色范围：0.2 到 0.6（非常柔和）
    colors = cm.Blues(np.linspace(0.2, 0.6, len(sizes)))[::-1]
    
    # 所有扇区都突出，但幅度不宜过大，依次突出（每个扇区偏移相同值即可，按顺序突出）
    # 如果需要依次突出一圈，可以设置不同的偏移量；但通常“依次突出”是指每个扇区都有偏移，大小相同
    explode = [0.04] * len(sizes)  # 每个扇区都突出0.04
    
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
    
    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        pctdistance=0.80,      # 调整百分比文字距离中心稍近，因为扇区突出了
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.2, 'width': 0.55},
        shadow=True,
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )
    
    # 百分比文字样式
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')
        autotext.set_bbox(dict(boxstyle="round,pad=0.2", facecolor="#5A8FBB", alpha=0.7))
    
    # 类别标签颜色
    for text in texts:
        text.set_color('#2A5A8A')
        text.set_fontsize(10)
        text.set_fontweight('bold')
    
    # 中心圆环（白色，带浅蓝边框）
    centre_circle = plt.Circle((0, 0), 0.4, fc='white', edgecolor='#A8CBE5', linewidth=1.5, alpha=0.95)
    ax.add_artist(centre_circle)
    
    # 中心文字
    ax.text(0, 0, '主题\n分布', ha='center', va='center', fontsize=13, 
            fontweight='bold', color='#2A5A8A', linespacing=1.5)
    
    ax.set_title(title, fontsize=15, fontweight='bold', color='#2A5A8A', pad=20)
    ax.legend(wedges, labels, title="帖子类别", loc="center left", 
              bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9, title_fontsize=10)
    ax.axis('equal')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches='tight', facecolor='white')
        print(f"饼图已保存为: {save_path}")
    plt.show()

plot_all_explode_light_blue_pie(cat_counts, 
                                '《给阿嬷的情书》微博帖子主题分类占比',
                                save_path='category_pie_all_explode_light_blue.png')

# 保存分类结果
df.to_csv('classified_posts.csv', index=False, encoding='utf-8-sig')
print("\n分类结果已保存至 classified_posts.csv")