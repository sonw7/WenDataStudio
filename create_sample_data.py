import pandas as pd
import numpy as np
import os

def create_sample_data():
    # 确保目录存在
    os.makedirs("data/sample", exist_ok=True)

    # 创建示例销售数据
    np.random.seed(42)  # 设置随机种子以确保可重复性

    # 生成日期范围
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')

    # 创建产品和地区列表
    products = ['笔记本电脑', '智能手机', '平板电脑', '耳机', '智能手表']
    regions = ['北京', '上海', '广州', '深圳', '成都', '杭州']

    # 创建数据框
    data = {
        '日期': np.random.choice(dates, size=1000),
        '产品': np.random.choice(products, size=1000),
        '地区': np.random.choice(regions, size=1000),
        '销量': np.random.randint(1, 100, size=1000),
        '单价': np.random.uniform(1000, 10000, size=1000).round(2),
        '成本': np.random.uniform(500, 8000, size=1000).round(2),
        '客户评分': np.random.uniform(1, 5, size=1000).round(1),
    }

    # 计算总收入和利润
    df = pd.DataFrame(data)
    df['总收入'] = df['销量'] * df['单价']
    df['利润'] = df['总收入'] - (df['销量'] * df['成本'])

    # 添加一些缺失值，以便演示数据清洗功能
    mask = np.random.random(size=len(df)) < 0.05  # 5%的行
    df.loc[mask, '客户评分'] = np.nan

    # 保存到Excel文件
    df.to_excel("data/sample/sales_data.xlsx", index=False)
    print("示例数据已创建: data/sample/sales_data.xlsx")

if __name__ == "__main__":
    create_sample_data()