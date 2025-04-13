import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
from matplotlib.font_manager import FontProperties
import os
import platform

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
def generate_chart(df, chart_type, x_column, y_column):
    """
    生成图表
    
    参数:
        df: pandas DataFrame
        chart_type: 图表类型
        x_column: X轴列名
        y_column: Y轴列名
        
    返回:
        matplotlib 图表对象
    """
    plt.figure(figsize=(10, 6))
    
    if chart_type == "折线图":
        sns.lineplot(data=df, x=x_column, y=y_column)
        plt.title(f"{y_column} 随 {x_column} 变化折线图")
        
    elif chart_type == "柱状图":
        sns.barplot(data=df, x=x_column, y=y_column)
        plt.title(f"{x_column} vs {y_column} 柱状图")
        
    elif chart_type == "散点图":
        sns.scatterplot(data=df, x=x_column, y=y_column)
        plt.title(f"{x_column} vs {y_column} 散点图")
        
    elif chart_type == "饼图":
        if len(df[x_column].unique()) <= 10:  # 限制类别数量
            plt.pie(df.groupby(x_column)[y_column].sum(), 
                   labels=df.groupby(x_column)[y_column].sum().index, 
                   autopct='%1.1f%%')
            plt.title(f"{x_column} 的 {y_column} 分布")
        else:
            plt.text(0.5, 0.5, "类别过多，不适合使用饼图", 
                    horizontalalignment='center', verticalalignment='center')
            
    elif chart_type == "热力图":
        corr_matrix = df.select_dtypes(include=['float64', 'int64']).corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
        plt.title("数值变量相关性热力图")
    
    plt.tight_layout()
    return plt.gcf()