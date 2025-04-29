import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from src.data_processing.loader import load_data
from src.utils.helpers import save_dataframe
from src.visualization.charts import set_chinese_font

# 设置中文字体
set_chinese_font()

def load_water_body_data(file_path):
    """
    加载水体数据
    
    参数:
        file_path: Excel文件路径
        
    返回:
        pandas DataFrame
    """
    print(f"正在加载数据: {file_path}")
    file_type = os.path.splitext(file_path)[1][1:].lower()
    df = load_data(file_path, file_type)
    print(f"数据加载完成，共 {df.shape[0]} 行 × {df.shape[1]} 列")
    return df

def analyze_water_body_data(df):
    """
    分析水体数据
    
    参数:
        df: 包含水体数据的DataFrame
        
    返回:
        包含各种统计结果的字典
    """
    # 检查并处理必要的列
    required_cols = ['Type', 'country']
    for col in required_cols:
        if col not in df.columns:
            print(f"警告: 数据中缺少列 '{col}'，尝试自动识别或创建替代列")
            
            # 尝试识别可能的替代列
            if col.lower() == 'type':
                # 查找可能包含类型信息的列
                possible_type_cols = [c for c in df.columns if 'type' in c.lower() or 'nature' in c.lower() or 'kind' in c.lower() or 'class' in c.lower()]
                if possible_type_cols:
                    print(f"使用列 '{possible_type_cols[0]}' 作为 'Type' 列的替代")
                    df['Type'] = df[possible_type_cols[0]]
                else:
                    # 如果找不到替代列，创建默认值
                    print("未找到合适的替代列，创建默认 'Type' 列 (全部设为 'unknown')")
                    df['Type'] = 'unknown'
            
            elif col.lower() == 'country':
                # 查找可能包含国家信息的列
                possible_country_cols = [c for c in df.columns if 'country' in c.lower() or 'nation' in c.lower() or 'region' in c.lower() or 'area' in c.lower() or 'location' in c.lower()]
                if possible_country_cols:
                    print(f"使用列 '{possible_country_cols[0]}' 作为 'country' 列的替代")
                    df['country'] = df[possible_country_cols[0]]
                else:
                    # 如果找不到替代列，创建默认值
                    print("未找到合适的替代列，创建默认 'country' 列 (全部设为 'unknown')")
                    df['country'] = 'unknown'
    
    # 获取年份列（1990-2020）
    year_cols = []
    for col in df.columns:
        # 处理整数类型的列名
        if isinstance(col, int) and 1990 <= col <= 2020:
            year_cols.append(col)
        # 处理字符串类型的列名
        elif isinstance(col, str) and col.isdigit() and 1990 <= int(col) <= 2020:
            year_cols.append(col)
    
    if not year_cols:
        print("警告: 数据中未找到标准年份列（1990-2020），尝试识别可能的年份列")
        
        # 尝试识别可能的年份列（包含年份数字的列名）
        possible_year_cols = []
        for col in df.columns:
            col_str = str(col)
            # 检查列名中是否包含1990-2020之间的年份
            for year in range(1990, 2021):
                if str(year) in col_str:
                    possible_year_cols.append(col)
                    break
        
        if possible_year_cols:
            print(f"找到 {len(possible_year_cols)} 个可能的年份列: {', '.join(map(str, possible_year_cols))}")
            year_cols = possible_year_cols
        else:
            # 如果仍然找不到年份列，使用所有数值列作为替代
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            numeric_cols = [col for col in numeric_cols if col not in ['Type', 'country']]
            if numeric_cols:
                print(f"未找到年份列，使用所有数值列作为替代: {', '.join(map(str, numeric_cols))}")
                year_cols = numeric_cols
            else:
                raise ValueError("数据中没有可用于分析的数值列")
    
    print(f"找到 {len(year_cols)} 个年份列: {', '.join(map(str, year_cols))}")
    
    # 初始化结果字典
    results = {
        'total': {},
        'by_type': {},
        'by_year': {}
    }
    
    # 1. 总和统计
    # 计算每个国家的水体总面积（所有年份的非空值总和）
    country_total_area = pd.DataFrame()
    country_total_area['总面积'] = df[year_cols].sum(axis=1)
    country_total_area['country'] = df['country']
    country_stats = country_total_area.groupby('country').agg(
        总面积=('总面积', 'sum'),
        水体数量=('总面积', 'count')
    ).reset_index()
    results['total']['country'] = country_stats
    
    # 2. 按Type（自然/非自然）统计
    type_stats = df.groupby('Type').agg(
        水体数量=('country', 'count')
    ).reset_index()
    
    # 计算每种类型每年的总面积
    type_year_area = {}
    for year in year_cols:
        # 使用更安全的方法处理NaN值
        grouped = df.groupby('Type')
        type_year_area[year] = grouped[year].apply(lambda x: x[~pd.isna(x)].sum())
    
    type_year_df = pd.DataFrame(type_year_area)
    results['by_type']['counts'] = type_stats
    results['by_type']['areas'] = type_year_df
    
    # 3. 按年份统计
    year_stats = {}
    for year in year_cols:
        # 计算该年份的非空值数量
        non_empty_count = df[year].count()
        # 计算该年份的非空值总和
        total_area = df[year][~pd.isna(df[year])].sum()
        
        year_stats[year] = {
            '非空值数量': non_empty_count,
            '总面积': total_area
        }
    
    year_df = pd.DataFrame(year_stats).T
    year_df.index.name = '年份'
    results['by_year'] = year_df
    
    # 添加年度自然/非自然水体统计
    yearly_type_stats = {}
    for year in year_cols:
        # 计算每种类型在该年份的非空值数量
        type_counts = df.groupby('Type')[year].count()
        # 计算每种类型在该年份的总面积
        type_areas = df.groupby('Type')[year].sum()
        
        yearly_type_stats[year] = pd.DataFrame({
            '水体数量': type_counts,
            '总面积': type_areas
        })
    
    # 将统计结果转换为更易读的格式
    yearly_stats_df = pd.DataFrame()
    for year in year_cols:
        stats = yearly_type_stats[year]
        for type_name in stats.index:
            yearly_stats_df.loc[year, f'{type_name}_数量'] = stats.loc[type_name, '水体数量']
            yearly_stats_df.loc[year, f'{type_name}_面积'] = stats.loc[type_name, '总面积']
    
    yearly_stats_df.index.name = '年份'
    results['yearly_type_stats'] = yearly_stats_df
    
    return results

def generate_charts(results, output_dir='output'):
    """
    生成图表
    
    参数:
        results: 分析结果字典
        output_dir: 输出目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 国家水体面积柱状图（前10个国家）
    plt.figure(figsize=(12, 6))
    top_countries = results['total']['country'].sort_values('总面积', ascending=False).head(10)
    sns.barplot(data=top_countries, x='country', y='总面积')
    plt.title('各国水体总面积（前10名）')
    plt.xlabel('国家')
    plt.ylabel('总面积')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '各国水体总面积.png'), dpi=300)
    plt.close()
    
    # 2. 自然/非自然水体数量对比
    plt.figure(figsize=(8, 6))
    sns.barplot(data=results['by_type']['counts'], x='Type', y='水体数量')
    plt.title('自然/非自然水体数量对比')
    plt.xlabel('类型')
    plt.ylabel('水体数量')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '自然非自然水体数量对比.png'), dpi=300)
    plt.close()
    
    # 3. 自然/非自然水体面积随年份变化
    plt.figure(figsize=(12, 6))
    results['by_type']['areas'].T.plot(kind='line', marker='o')
    plt.title('自然/非自然水体面积随年份变化')
    plt.xlabel('年份')
    plt.ylabel('总面积')
    plt.grid(True, alpha=0.3)
    plt.legend(title='类型')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '自然非自然水体面积年份变化.png'), dpi=300)
    plt.close()
    
    # 4. 年份水体数量变化
    plt.figure(figsize=(12, 6))
    results['by_year']['非空值数量'].plot(kind='line', marker='o')
    plt.title('各年份水体数量变化')
    plt.xlabel('年份')
    plt.ylabel('水体数量')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '各年份水体数量变化.png'), dpi=300)
    plt.close()
    
    # 5. 年份水体总面积变化
    plt.figure(figsize=(12, 6))
    results['by_year']['总面积'].plot(kind='line', marker='o')
    plt.title('各年份水体总面积变化')
    plt.xlabel('年份')
    plt.ylabel('总面积')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '各年份水体总面积变化.png'), dpi=300)
    plt.close()
    
    print(f"图表已保存到 {output_dir} 目录")

def save_results_to_excel(results, output_path='output/water_body_statistics.xlsx'):
    """
    将结果保存到Excel文件
    
    参数:
        results: 分析结果字典
        output_path: 输出文件路径
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 创建Excel写入器
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # 1. 保存国家统计
        results['total']['country'].to_excel(writer, sheet_name='国家统计', index=False)
        
        # 2. 保存类型统计
        results['by_type']['counts'].to_excel(writer, sheet_name='类型统计_数量', index=False)
        results['by_type']['areas'].to_excel(writer, sheet_name='类型统计_面积')
        
        # 3. 保存年份统计
        results['by_year'].to_excel(writer, sheet_name='年份统计')
        
        # 4. 保存年度自然/非自然水体统计
        results['yearly_type_stats'].to_excel(writer, sheet_name='年度自然非自然统计')
    
    print(f"统计结果已保存到: {output_path}")

def main():
    """主函数"""
    # 创建输出目录
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # 提示用户输入文件路径
    print("水体数据分析工具")
    print("=" * 50)
    
    # 获取文件路径
    file_path = input("请输入Excel文件路径: ")
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        return
    
    try:
        # 加载数据
        df = load_water_body_data(file_path)
        
        # 显示数据预览
        print("\n数据预览:")
        print(df.head())
        
        # 分析数据
        print("\n正在分析数据...")
        results = analyze_water_body_data(df)
        
        # 生成图表
        print("\n正在生成图表...")
        generate_charts(results, output_dir)
        
        # 保存结果到Excel
        print("\n正在保存结果到Excel...")
        save_results_to_excel(results, os.path.join(output_dir, 'water_body_statistics.xlsx'))
        
        print("\n分析完成!")
        print(f"结果已保存到 {output_dir} 目录")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()
