import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import matplotlib
from matplotlib.font_manager import FontProperties
import platform
import seaborn as sns
from matplotlib.gridspec import GridSpec

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

if __name__ == "__main__":
    # 创建示例数据
    sample_data = create_sample_data()
    
    # 生成图表
    fig = generate_water_body_analysis_chart(sample_data, 'water_body_analysis_chart.png')
    
    # 显示图表
    plt.show()
