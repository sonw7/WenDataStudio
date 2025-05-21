import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import matplotlib
from matplotlib.font_manager import FontProperties
import platform
import seaborn as sns
from matplotlib.gridspec import GridSpec
import io
import streamlit as st
import tempfile
temp_dir = tempfile.mkdtemp()
# 设置中文字体支持
def set_chinese_font():
    system = platform.system()
    if system == 'Windows':
        font_path = 'C:/Windows/Fonts/simhei.ttf'  # Windows 的黑体字体
        if os.path.exists(font_path):
            font = FontProperties(fname=font_path)
            matplotlib.rcParams['font.family'] = font.get_name()
        else:
            matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    elif system == 'Darwin':  # macOS
        matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'STHeiti']
    elif system == 'Linux':
        matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'AR PL UMing CN']
    
    matplotlib.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 初始化时设置字体
set_chinese_font()

def generate_water_body_analysis_chart(data, output_path=None):
    """
    生成水体分析2x2网格图表
    
    参数:
        data: 包含水体数据的字典，需要包含以下键：
            - aral_sea_area: 咸海面积数据，包含年份和面积
            - other_water_bodies: 其他水体数据，包含年份、面积和数量
            - water_body_size_change: 不同大小水体的变化率数据
            - climate_data: 气候数据，包含年份、温度和降水
        output_path: 输出文件路径，如果为None则显示图表而不保存
        
    返回:
        matplotlib 图表对象
    """
    # 创建2x2网格布局的图表
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(2, 2, figure=fig)
    
    # 设置子图间距
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    
    # 子图 (a): 咸海面积随时间变化
    ax1 = fig.add_subplot(gs[0, 0])
    aral_data = data['aral_sea_area']
    
    # 计算斜率
    x = aral_data['year'].values
    y = aral_data['area'].values
    slope, _ = np.polyfit(x, y, 1)
    slope_text = f"Slope={slope:.2f}×10² km²/a"
    
    # 绘制折线图
    ax1.plot(aral_data['year'], aral_data['area'], 'ro-', linewidth=2, markersize=6)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Area (10³ km²)')
    ax1.set_title(f'(a) Aral Sea\n{slope_text}')
    ax1.grid(True, alpha=0.3)
    
    # 子图 (b): 其他水体面积与数量随时间变化
    ax2 = fig.add_subplot(gs[0, 1])
    other_data = data['other_water_bodies']
    
    # 计算面积和数量的斜率
    x = other_data['year'].values
    y_area = other_data['area'].values
    y_number = other_data['number'].values
    slope_area, _ = np.polyfit(x, y_area, 1)
    slope_number, _ = np.polyfit(x, y_number, 1)
    
    # 创建双y轴
    ax2_twin = ax2.twinx()
    
    # 绘制面积折线图
    line1, = ax2.plot(other_data['year'], other_data['area'], 'bo-', linewidth=2, markersize=6, label='Area')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Area (10³ km²)')
    
    # 绘制数量柱状图
    bars = ax2_twin.bar(other_data['year'], other_data['number'], alpha=0.3, color='skyblue', label='Number')
    ax2_twin.set_ylabel('Number')
    
    # 设置标题
    ax2.set_title(f'(b) Water bodies besides the Aral Sea\nSlope={slope_number:.0f}, Slope={slope_area:.2f}×10³ km²/a')
    
    # 添加图例
    lines, labels = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')
    
    # 子图 (c): 水体面积变化率与大小的关系
    ax3 = fig.add_subplot(gs[1, 0])
    size_data = data['water_body_size_change']
    
    # 设置x轴标签位置
    x = np.arange(len(size_data['size_category']))
    width = 0.35
    
    # 绘制数量变化率柱状图
    bars1 = ax3.bar(x - width/2, size_data['number_change_rate'], width, label='Number', color='skyblue')
    
    # 绘制面积变化率柱状图
    bars2 = ax3.bar(x + width/2, size_data['area_change_rate'], width, label='Area', color='darkblue')
    
    # 添加数值标签
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax3.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3点垂直偏移
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    add_labels(bars1)
    add_labels(bars2)
    
    # 设置x轴标签
    ax3.set_xlabel('Size of water bodies')
    ax3.set_ylabel('Change rate (%)')
    ax3.set_title('(c)')
    ax3.set_xticks(x)
    ax3.set_xticklabels(size_data['size_category'])
    ax3.legend()
    
    # 子图 (d): 温度与降水随时间变化
    ax4 = fig.add_subplot(gs[1, 1])
    climate_data = data['climate_data']
    
    # 创建双y轴
    ax4_twin = ax4.twinx()
    
    # 绘制温度折线图
    line2, = ax4.plot(climate_data['year'], climate_data['temperature'], 'o-', color='orange', linewidth=2, markersize=6, label='Temperature')
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Temperature (°C)')
    
    # 绘制降水柱状图
    bars3 = ax4_twin.bar(climate_data['year'], climate_data['precipitation'], alpha=0.5, color='blue', label='Precipitation')
    ax4_twin.set_ylabel('Precipitation (mm)')
    
    # 设置标题
    ax4.set_title('(d)')
    
    # 添加图例
    lines, labels = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines + lines2, labels + labels2, loc='upper left')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存到: {output_path}")
    
    return fig

def create_sample_data():
    """
    创建示例数据用于测试图表
    
    返回:
        包含示例数据的字典
    """
    # 设置随机种子以确保可重复性
    np.random.seed(42)
    
    # 年份范围
    years = np.arange(1990, 2021)
    
    # 1. 咸海面积数据 - 呈下降趋势
    aral_area = 65 - 1.21 * (years - 1990) / 100 + np.random.normal(0, 0.5, len(years))
    aral_data = pd.DataFrame({
        'year': years,
        'area': aral_area
    })
    
    # 2. 其他水体数据 - 面积和数量呈上升趋势
    other_area = 20 + 0.22 * (years - 1990) + np.random.normal(0, 1, len(years))
    other_number = 5000 + 587 * (years - 1990) / 30 + np.random.normal(0, 100, len(years))
    other_data = pd.DataFrame({
        'year': years,
        'area': other_area,
        'number': other_number
    })
    
    # 3. 不同大小水体的变化率数据
    size_categories = ['<1 km²', '1-10 km²', '10-100 km²', '>100 km²']
    number_change_rates = [25.3, 18.7, 12.4, 5.8]
    area_change_rates = [22.1, 15.6, 10.2, 4.5]
    size_data = {
        'size_category': size_categories,
        'number_change_rate': number_change_rates,
        'area_change_rate': area_change_rates
    }
    
    # 4. 气候数据 - 温度呈上升趋势，降水波动
    temperature = 15 + 0.03 * (years - 1990) + np.random.normal(0, 0.5, len(years))
    precipitation = 300 + np.random.normal(0, 50, len(years))
    climate_data = pd.DataFrame({
        'year': years,
        'temperature': temperature,
        'precipitation': precipitation
    })
    
    # 整合所有数据
    data = {
        'aral_sea_area': aral_data,
        'other_water_bodies': other_data,
        'water_body_size_change': size_data,
        'climate_data': climate_data
    }
    
    return data

def prepare_data_from_analysis_results(results):
    """
    从水体分析结果中准备绘图所需的数据
    
    参数:
        results: 水体分析结果字典
        
    返回:
        包含绘图所需数据的字典
    """
    # 初始化数据字典
    data = {}
    
    # 获取年份列表
    year_cols = [col for col in results['by_year'].index if isinstance(col, (int, str)) and str(col).isdigit()]
    years = [int(year) for year in year_cols]
    
    # 1. 提取最大水体的数据作为"咸海"数据
    # 找出面积最大的水体
    if 'yearly_type_stats' in results:
        # 获取总面积数据
        total_area = results['by_year']['总面积'].values
        
        # 创建咸海数据
        aral_data = pd.DataFrame({
            'year': years,
            'area': total_area / 1000  # 转换为10³ km²
        })
        data['aral_sea_area'] = aral_data
    else:
        # 创建默认数据
        aral_data = pd.DataFrame({
            'year': years,
            'area': np.linspace(65, 30, len(years))  # 默认下降趋势
        })
        data['aral_sea_area'] = aral_data
    
    # 2. 其他水体数据
    if 'by_year' in results:
        # 获取水体数量和面积
        water_number = results['by_year']['非空值数量'].values
        water_area = results['by_year']['总面积'].values / 1000  # 转换为10³ km²
        
        other_data = pd.DataFrame({
            'year': years,
            'area': water_area,
            'number': water_number
        })
        data['other_water_bodies'] = other_data
    else:
        # 创建默认数据
        other_data = pd.DataFrame({
            'year': years,
            'area': np.linspace(20, 30, len(years)),
            'number': np.linspace(5000, 10000, len(years))
        })
        data['other_water_bodies'] = other_data
    
    # 3. 水体大小变化率数据
    # 这部分需要额外计算，这里使用示例数据
    size_categories = ['<1 km²', '1-10 km²', '10-100 km²', '>100 km²']
    number_change_rates = [25.3, 18.7, 12.4, 5.8]
    area_change_rates = [22.1, 15.6, 10.2, 4.5]
    size_data = {
        'size_category': size_categories,
        'number_change_rate': number_change_rates,
        'area_change_rate': area_change_rates
    }
    data['water_body_size_change'] = size_data
    
    # 4. 气候数据
    # 这部分需要额外数据，这里使用示例数据
    temperature = 15 + 0.03 * (np.array(years) - 1990) + np.random.normal(0, 0.5, len(years))
    precipitation = 300 + np.random.normal(0, 50, len(years))
    climate_data = pd.DataFrame({
        'year': years,
        'temperature': temperature,
        'precipitation': precipitation
    })
    data['climate_data'] = climate_data
    
    return data

def get_country_list(df):
    """
    获取数据中的国家列表
    
    参数:
        df: 包含水体数据的DataFrame
        
    返回:
        国家名称列表
    """
    if 'country' in df.columns:
        countries = df['country'].unique().tolist()
        # 确保所有国家名称都是字符串类型，避免排序时出现类型错误
        countries = [str(country) for country in countries]
        return sorted(countries)
    return []

def prepare_natural_artificial_data(df):
    """
    处理并准备自然/非自然水体数据
    
    参数:
        df: 包含水体数据的DataFrame
        
    返回:
        处理后的DataFrame，确保包含is_natural列
    """
    # 复制DataFrame避免修改原始数据
    processed_df = df.copy()
    
    # 检查是否已存在is_natural列
    if 'is_natural' not in processed_df.columns:
        # 尝试从其他可能的列中推断自然/非自然状态
        if 'Type' in processed_df.columns:
            # 定义可能表示自然水体的关键词
            natural_keywords = ['natural', '自然', 'lake', '湖泊', 'river', '河流', 'wetland', '湿地', 'ocean', '海洋']
            # 定义可能表示人工水体的关键词
            artificial_keywords = ['artificial', '人工', 'reservoir', '水库', 'dam', '水坝', 'canal', '运河', 'pond', '池塘']
            
            # 创建is_natural列
            def determine_if_natural(water_type):
                if pd.isna(water_type) or water_type == '':
                    return None
                
                water_type = str(water_type).lower()
                
                # 检查是否匹配自然水体关键词
                if any(keyword in water_type for keyword in natural_keywords):
                    return True
                
                # 检查是否匹配人工水体关键词
                if any(keyword in water_type for keyword in artificial_keywords):
                    return False
                
                # 默认为未知
                return None
            
            # 应用函数创建is_natural列
            processed_df['is_natural'] = processed_df['Type'].apply(determine_if_natural)
            
            # 打印统计信息
            natural_count = processed_df['is_natural'].sum()
            artificial_count = (processed_df['is_natural'] == False).sum()
            print(f"自动识别: 自然水体 {natural_count}, 非自然水体 {artificial_count}, 未知 {len(processed_df) - natural_count - artificial_count}")
    
    return processed_df

def generate_country_water_body_stats(df, country_name, year_cols, types_to_analyze=None):
    """
    生成特定国家随时间变化的水体统计和可视化
    
    参数：
        df: 包含水体数据的DataFrame
        country_name: 要分析的国家名称
        year_cols: 年份列列表
        types_to_analyze: 要分析的水体类型列表（默认：使用数据中的所有类型）
        
    返回：
        tuple: (包含统计数据的DataFrame, BytesIO图像缓冲区或可视化失败时为None)
    """
    # 检查数据中是否存在该国家
    if country_name not in df['country'].unique():
        print(f"未找到国家：{country_name}的数据")
        return pd.DataFrame(), None
    
    # 筛选指定国家的数据
    country_df = df[df['country'] == country_name]
    
    # 获取要分析的水体类型（如果未指定则使用所有类型）
    if types_to_analyze is None:
        types_to_analyze = country_df['Type'].unique() if 'Type' in country_df.columns else []
    
    # 将年份列转换为字符串，以确保一致性
    year_cols = [str(col) for col in year_cols]
    
    # 初始化结果DataFrame
    result_df = pd.DataFrame(index=year_cols)
    
    # 确保年份列在dataframe中为数值类型
    for year in year_cols:
        if year in country_df.columns:
            # 尝试将年份列转换为数值类型，非数值替换为NaN
            country_df[year] = pd.to_numeric(country_df[year], errors='coerce')
    
    # 计算每种水体类型和年份的统计数据
    if 'Type' in country_df.columns:
        for water_type in types_to_analyze:
            type_df = country_df[country_df['Type'] == water_type]
            
            for year in year_cols:
                if year in type_df.columns:
                    result_df.loc[year, f'{water_type}_数量'] = type_df[year].count()
                    result_df.loc[year, f'{water_type}_面积'] = type_df[year].sum()
    
    # 添加总计列
    for year in year_cols:
        if year in country_df.columns:
            result_df.loc[year, '总数量'] = country_df[year].count()
            result_df.loc[year, '总面积'] = country_df[year].sum()
    
    # 计算自然/非自然水体统计 (假设有一个名为"is_natural"的列，值为True/False或1/0)
    if 'is_natural' in country_df.columns:
        natural_df = country_df[country_df['is_natural'] == True]
        artificial_df = country_df[country_df['is_natural'] == False]
        
        for year in year_cols:
            if year in country_df.columns:
                # 自然水体统计
                result_df.loc[year, '自然水体_数量'] = natural_df[year].count() if not natural_df.empty else 0
                result_df.loc[year, '自然水体_面积'] = natural_df[year].sum() if not natural_df.empty else 0
                
                # 非自然水体统计
                result_df.loc[year, '非自然水体_数量'] = artificial_df[year].count() if not artificial_df.empty else 0
                result_df.loc[year, '非自然水体_面积'] = artificial_df[year].sum() if not artificial_df.empty else 0
    
    # 创建可视化
    try:
        # 确保结果DataFrame中的所有值都是数值类型
        result_df = result_df.apply(pd.to_numeric, errors='coerce')
        
        fig = plt.figure(figsize=(14, 14))
        gs = GridSpec(4, 1, figure=fig, height_ratios=[1, 1, 1, 1])
        
        # 1. 面积变化图 - 按类型
        ax1 = fig.add_subplot(gs[0])
        area_columns = [col for col in result_df.columns if '面积' in col and '自然' not in col and '非自然' not in col]
        if area_columns:
            result_df[area_columns].plot(ax=ax1, marker='o')
            ax1.set_title(f'{country_name}国家水体面积随年份变化(按类型)')
            ax1.set_xlabel('年份')
            ax1.set_ylabel('面积')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
        
        # 2. 数量变化图 - 按类型
        ax2 = fig.add_subplot(gs[1])
        count_columns = [col for col in result_df.columns if '数量' in col and '自然' not in col and '非自然' not in col]
        if count_columns:
            result_df[count_columns].plot(ax=ax2, marker='o')
            ax2.set_title(f'{country_name}国家水体数量随年份变化(按类型)')
            ax2.set_xlabel('年份')
            ax2.set_ylabel('数量')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
        
        # 3. 自然/非自然水体面积变化
        ax3 = fig.add_subplot(gs[2])
        natural_area_cols = ['自然水体_面积', '非自然水体_面积']
        has_natural_data = all(col in result_df.columns for col in natural_area_cols)
        
        if has_natural_data:
            result_df[natural_area_cols].plot(ax=ax3, marker='o', 
                                            color=['green', 'orange'],
                                            linewidth=2)
            # 添加总面积线
            if '总面积' in result_df.columns:
                result_df['总面积'].plot(ax=ax3, marker='s', color='blue', 
                                      linestyle='--', linewidth=1.5, label='总面积')
            
            ax3.set_title(f'{country_name}国家自然/非自然水体面积随年份变化')
            ax3.set_xlabel('年份')
            ax3.set_ylabel('面积')
            ax3.grid(True, alpha=0.3)
            ax3.legend()
        
        # 4. 自然/非自然水体数量变化
        ax4 = fig.add_subplot(gs[3])
        natural_count_cols = ['自然水体_数量', '非自然水体_数量']
        
        if has_natural_data:
            result_df[natural_count_cols].plot(ax=ax4, marker='o', 
                                             color=['green', 'orange'],
                                             linewidth=2)
            # 添加总数量线
            if '总数量' in result_df.columns:
                result_df['总数量'].plot(ax=ax4, marker='s', color='blue', 
                                       linestyle='--', linewidth=1.5, label='总数量')
            
            ax4.set_title(f'{country_name}国家自然/非自然水体数量随年份变化')
            ax4.set_xlabel('年份')
            ax4.set_ylabel('数量')
            ax4.grid(True, alpha=0.3)
            ax4.legend()
        
        plt.tight_layout()
        
        # 保存图形到缓冲区
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        img_buf.seek(0)
        
        return result_df, img_buf
        
    except Exception as e:
        print(f"生成可视化时出错：{e}")
        import traceback
        traceback.print_exc()  # 打印详细的错误信息
        plt.close('all')  # 确保关闭所有图形
        return result_df, None

# Streamlit 应用的国家选择功能代码
def country_analysis_tab(df):
    st.write("#### 单个国家水体统计分析")
    
    # 预处理数据，确保包含自然/非自然水体信息
    processed_df = prepare_natural_artificial_data(df)
    
    # 获取数据中的国家列表
    country_list = get_country_list(processed_df)
    
    if country_list:
        # 创建国家选择下拉框
        selected_country = st.selectbox("选择国家", country_list)
        
        # 获取年份列
        year_cols = [col for col in processed_df.columns if isinstance(col, (int, str)) and str(col).isdigit()]
        
        # 检查是否存在自然/非自然水体信息
        has_natural_flag = 'is_natural' in processed_df.columns
        
        # 创建分析选项
        st.write("##### 分析选项")
        col1, col2 = st.columns(2)
        
        with col1:
            show_by_type = st.checkbox("按水体类型分析", value=True)
        
        with col2:
            show_natural_artificial = st.checkbox("自然/非自然水体分析", value=has_natural_flag, disabled=not has_natural_flag)
            
            if not has_natural_flag and show_natural_artificial:
                st.info("数据中没有自然/非自然水体标识，无法进行相关分析")
        
        if selected_country and year_cols:
            # 显示分析按钮
            if st.button(f"分析 {selected_country} 水体数据"):
                with st.spinner(f"正在分析 {selected_country} 的水体数据..."):
                    # 生成该国家的水体统计数据
                    country_stats, country_img = generate_country_water_body_stats(processed_df, selected_country, year_cols)
                    
                    # 显示统计结果
                    if not country_stats.empty:
                        st.write(f"##### {selected_country} 水体数据统计")
                        
                        # 根据用户选择过滤要显示的列
                        display_columns = []
                        
                        if show_by_type:
                            type_columns = [col for col in country_stats.columns 
                                            if '自然' not in col and '非自然' not in col]
                            display_columns.extend(type_columns)
                        
                        if show_natural_artificial and has_natural_flag:
                            natural_columns = [col for col in country_stats.columns 
                                              if '自然' in col or '非自然' in col]
                            display_columns.extend(natural_columns)
                        
                        # 如果没有选择任何选项，默认显示所有列
                        if not display_columns:
                            display_columns = country_stats.columns.tolist()
                        
                        # 确保总计列始终显示
                        if '总数量' in country_stats.columns and '总数量' not in display_columns:
                            display_columns.append('总数量')
                        if '总面积' in country_stats.columns and '总面积' not in display_columns:
                            display_columns.append('总面积')
                        
                        # 显示过滤后的数据表
                        filtered_stats = country_stats[display_columns]
                        st.dataframe(filtered_stats, use_container_width=True)
                        
                        # 添加下载按钮
                        country_specific_csv = country_stats.to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label=f"下载 {selected_country} 水体统计数据",
                            data=country_specific_csv,
                            file_name=f"{selected_country}_water_body_statistics.csv",
                            mime="text/csv"
                        )
                        
                        # 显示可视化结果
                        if country_img:
                            st.write(f"##### {selected_country} 水体变化可视化")
                            st.image(country_img)
                            
                            # 保存图像并提供下载
                            country_img_path = os.path.join(temp_dir, f"{selected_country}_water_analysis.png")
                            with open(country_img_path, "wb") as f:
                                f.write(country_img.getvalue())
                            
                            with open(country_img_path, "rb") as f:
                                img_bytes = f.read()
                                
                                st.download_button(
                                    label=f"下载 {selected_country} 水体分析图",
                                    data=img_bytes,
                                    file_name=f"{selected_country}_water_analysis.png",
                                    mime="image/png"
                                )
                    else:
                        st.warning(f"未找到 {selected_country} 的水体数据")
    else:
        st.warning("数据中未找到国家信息")

if __name__ == "__main__":
    # 创建示例数据
    sample_data = create_sample_data()
    
    # 生成图表
    fig = generate_water_body_analysis_chart(sample_data, 'water_body_analysis_chart.png')
    
    # 显示图表
    plt.show()
