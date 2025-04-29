import pandas as pd
import numpy as np
import os

def create_water_body_sample():
    """创建水体数据示例文件"""
    # 确保目录存在
    os.makedirs("data/sample", exist_ok=True)
    
    # 设置随机种子以确保可重复性
    np.random.seed(42)
    
    # 创建国家列表
    countries = [
        "中国", "美国", "俄罗斯", "加拿大", "巴西", "澳大利亚", 
        "印度", "阿根廷", "哈萨克斯坦", "阿尔及利亚", "刚果", "沙特阿拉伯"
    ]
    
    # 创建类型列表
    types = ["nature", "non-nature"]
    
    # 创建年份列表（1990-2020）
    years = list(range(1990, 2021))
    
    # 生成数据
    n_samples = 100  # 样本数量
    
    # 创建基础数据
    data = {
        'country': np.random.choice(countries, size=n_samples),
        'Type': np.random.choice(types, size=n_samples, p=[0.6, 0.4])  # 60% 自然, 40% 非自然
    }
    
    # 为每个国家创建多个水体记录
    for country in countries:
        country_count = np.sum(data['country'] == country)
        if country_count > 1:
            # 为同一国家的不同记录添加编号
            country_indices = np.where(data['country'] == country)[0]
            for i, idx in enumerate(country_indices):
                data['country'][idx] = f"{country}_{i+1}"
    
    # 添加年份数据
    for year in years:
        # 生成一些随机的水体面积数据
        # 使用一些随机缺失值（约15%）
        values = np.random.uniform(10, 1000, size=n_samples).round(2)
        mask = np.random.random(size=n_samples) < 0.15
        values[mask] = np.nan
        
        # 添加到数据字典
        data[str(year)] = values
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 保存到Excel文件
    output_path = "data/sample/water_body_data.xlsx"
    df.to_excel(output_path, index=False)
    print(f"示例水体数据已创建: {output_path}")
    
    return output_path

if __name__ == "__main__":
    create_water_body_sample()
