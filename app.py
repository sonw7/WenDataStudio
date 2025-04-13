import streamlit as st
# 首先设置页面配置 - 必须是第一个 Streamlit 命令
st.set_page_config(
    page_title="雯雯同学的数据工作室", 
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 然后导入其他模块
import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt  # matplotlib 绘图模块
import seaborn as sns  # 统计数据可视化模块
import platform
import numpy as np
import io  # 添加io模块导入
from src.data_processing.loader import load_data
from src.data_processing.cleaner import clean_data
from src.data_processing.transformer import transform_data
from src.visualization.charts import generate_chart
from src.utils.helpers import get_file_extension

# 添加CSS以改进中文显示
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans SC', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# 设置中文字体支持函数
def set_chinese_font():
    system = platform.system()
    if system == 'Windows':
        font_list = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    elif system == 'Darwin':  # macOS
        font_list = ['Arial Unicode MS', 'PingFang SC', 'STHeiti']
    elif system == 'Linux':
        font_list = ['WenQuanYi Micro Hei', 'AR PL UMing CN']
    else:
        font_list = ['Arial Unicode MS']
    
    matplotlib.rcParams['font.sans-serif'] = font_list
    matplotlib.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 初始化时设置字体
set_chinese_font()

st.title("Wen DataStudio")
st.subheader("表格数据处理与可视化工具")

# 侧边栏配置
st.sidebar.header("数据操作")
upload_option = st.sidebar.radio(
    "选择数据来源",
    ["上传文件", "使用示例数据"]
)

# 自定义上传按钮样式，使其更适合中文环境
st.markdown("""
<style>
.uploadedFile {
    font-family: 'Noto Sans SC', sans-serif;
}
.stButton>button {
    font-family: 'Noto Sans SC', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# 数据加载部分
df = None

if upload_option == "上传文件":
    st.sidebar.markdown("#### 文件上传说明")
    st.sidebar.info("请点击下方'浏览文件'按钮选择Excel(.xlsx)或CSV(.csv)格式的数据文件")
    uploaded_file = st.sidebar.file_uploader("选择文件上传", type=["xlsx", "csv"], help="支持Excel和CSV格式，请确保文件编码为UTF-8")
    if uploaded_file is not None:
        file_extension = get_file_extension(uploaded_file.name)
        try:
            df = load_data(uploaded_file, file_extension)
            st.sidebar.success(f"成功加载文件: {uploaded_file.name}")
        except Exception as e:
            st.sidebar.error(f"文件加载失败: {str(e)}")
else:
    sample_data_path = os.path.join("data", "sample", "sales_data.xlsx")
    if os.path.exists(sample_data_path):
        df = load_data(sample_data_path, "xlsx")
        st.sidebar.info("已加载示例数据")
    else:
        st.sidebar.error("示例数据文件不存在")

# 数据处理部分
if df is not None:
    st.header("数据预览")
    
    # 显示数据基本信息
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**数据维度**: {df.shape[0]} 行 × {df.shape[1]} 列")
    with col2:
        st.write(f"**数据类型**: {', '.join(df.dtypes.astype(str).unique())}")
    
    # 设置更灵活的数据预览
    # preview_rows = min(20, df.shape[0])  # 最多显示20行
    st.dataframe(df, height=400, use_container_width=True)
    
    # 添加数据概览选项卡
    tab1, tab2, tab3 = st.tabs(["数据统计", "缺失值分析", "数据分布"])
    
    with tab1:
        st.write("#### 数值型数据统计")
        
        # 添加统计指标解释
        with st.expander("统计指标说明"):
            st.markdown("""
            - **计数(count)**: 非缺失值的数量
            - **平均值(mean)**: 所有数值的算术平均值
            - **标准差(std)**: 数据分散程度的度量，值越小表示数据越集中在平均值附近
            - **最小值(min)**: 数据集中的最小值
            - **25%**: 第一四分位数，25%的数据小于这个值
            - **50%**: 中位数，50%的数据小于这个值
            - **75%**: 第三四分位数，75%的数据小于这个值
            - **最大值(max)**: 数据集中的最大值
            """)
        
        # 将统计结果转换为中文标签
        stats_df = df.describe()
        # 创建中文标签的映射字典
        chinese_labels = {
            'count': '计数',
            'mean': '平均值',
            'std': '标准差',
            'min': '最小值',
            '25%': '25%分位数',
            '50%': '中位数',
            '75%': '75%分位数', 
            'max': '最大值'
        }
        # 更新索引名称为中文
        stats_df.index = [chinese_labels.get(idx, idx) for idx in stats_df.index]
        st.dataframe(stats_df, use_container_width=True)
        
        if not df.select_dtypes(include=['object']).empty:
            st.write("#### 分类型数据统计")
            categorical_stats = pd.DataFrame({
                '唯一值数量': df.select_dtypes(include=['object']).nunique(),
                '最常见值': df.select_dtypes(include=['object']).apply(lambda x: x.value_counts().index[0] if not x.value_counts().empty else ''),
                '最常见值占比': df.select_dtypes(include=['object']).apply(lambda x: x.value_counts().iloc[0]/len(x) if not x.value_counts().empty else 0),
            })
            st.dataframe(categorical_stats, use_container_width=True)
    
    with tab2:
        # 计算每列的缺失值
        missing_data = pd.DataFrame({
            '缺失值数量': df.isnull().sum(),
            '缺失比例': df.isnull().sum() / len(df) * 100
        })
        missing_data = missing_data.sort_values('缺失比例', ascending=False)
        
        if missing_data['缺失值数量'].sum() > 0:
            st.write("#### 缺失值分析")
            st.dataframe(missing_data, use_container_width=True)
            
            # 可视化缺失值
            if st.checkbox("显示缺失值可视化"):
                import matplotlib.pyplot as plt
                import seaborn as sns
                
                plt.figure(figsize=(10, 6))
                plt.title('缺失值热力图')
                sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
                st.pyplot(plt)
        else:
            st.success("数据中没有缺失值")
    
    with tab3:
        # 数据分布分析
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if numeric_cols:
            selected_col = st.selectbox("选择要分析的数值列", numeric_cols)
            
            col1, col2 = st.columns(2)
            with col1:
                # 直方图
                plt.figure(figsize=(10, 4))
                sns.histplot(df[selected_col].dropna(), kde=True)
                plt.title(f"{selected_col} 分布直方图")
                plt.grid(True, alpha=0.3)
                st.pyplot(plt)
            
            with col2:
                # 箱线图
                plt.figure(figsize=(10, 4))
                sns.boxplot(x=df[selected_col].dropna())
                plt.title(f"{selected_col} 箱线图")
                plt.grid(True, alpha=0.3)
                st.pyplot(plt)
    
    # 数据清洗选项
    st.header("数据清洗")
    clean_na = st.checkbox("处理缺失值")
    remove_duplicates = st.checkbox("删除重复行")
    
    if clean_na or remove_duplicates:
        df_cleaned = clean_data(df, clean_na, remove_duplicates)
        st.success(f"数据清洗完成: 原始数据 {df.shape[0]} 行, 清洗后 {df_cleaned.shape[0]} 行")
        
        # 对比清洗前后
        col1, col2 = st.columns(2)
        with col1:
            st.write("**清洗前**")
            st.dataframe(df.head(5), use_container_width=True)
        with col2:
            st.write("**清洗后**")
            st.dataframe(df_cleaned.head(5), use_container_width=True)
        
        # 提供选项使用清洗后的数据
        if st.checkbox("使用清洗后的数据继续"):
            df = df_cleaned
    
    # 数据可视化部分
    st.header("数据可视化")
    
    col1, col2 = st.columns(2)
    
    with col1:
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if numeric_columns:
            chart_type = st.selectbox(
                "选择图表类型", 
                ["折线图", "柱状图", "散点图", "饼图", "热力图"]
            )
            
            x_axis = st.selectbox("选择X轴数据", df.columns.tolist())
            y_axis = st.selectbox("选择Y轴数据", numeric_columns)
            
            if st.button("生成图表"):
                with col2:
                    fig = generate_chart(df, chart_type, x_axis, y_axis)
                    st.pyplot(fig)
                    
    # 数据导出选项
    st.header("数据导出")
    export_format = st.radio("选择导出格式", ["Excel", "CSV"])
    
    if st.button("导出数据"):
        if export_format == "Excel":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            buffer.seek(0)
            
            st.download_button(
                label="下载Excel文件",
                data=buffer,
                file_name="processed_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="下载CSV文件",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv"
            )
else:
    st.info("请上传数据文件或选择示例数据以开始")