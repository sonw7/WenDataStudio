import streamlit as st
# 首先设置页面配置 - 必须是第一个 Streamlit 命令
st.set_page_config(
    page_title="雯雯同学的数据工作室", 
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if 'water_body_results' not in st.session_state:
    st.session_state.water_body_results = None
if 'water_body_temp_dir' not in st.session_state:
    st.session_state.water_body_temp_dir = None

# 然后导入其他模块
import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt  # matplotlib 绘图模块
import seaborn as sns  # 统计数据可视化模块
import platform
import numpy as np
import io  # 添加io模块导入
import zipfile  # 用于创建ZIP文件
from src.data_processing.loader import load_data
from src.data_processing.cleaner import clean_data
from src.data_processing.transformer import transform_data
from src.visualization.charts import generate_chart
from src.utils.helpers import get_file_extension
from water_body_analysis import analyze_water_body_data, generate_charts, save_results_to_excel
from src.visualization.water_body_charts import generate_water_body_analysis_chart, prepare_data_from_analysis_results, create_sample_data

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

# 添加导航菜单
app_mode = st.sidebar.selectbox(
    "选择功能模式",
    ["通用数据分析", "水体数据分析"]
)

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

# 初始化df变量
df = None

if app_mode == "通用数据分析":
    # 数据加载部分
    if upload_option == "上传文件":
        st.sidebar.markdown("#### 文件上传说明")
        st.sidebar.info("请点击下方'浏览文件'按钮选择Excel(.xlsx)或CSV(.csv)格式的数据文件")
        uploaded_file = st.sidebar.file_uploader("选择文件上传", type=["xlsx", "csv"], help="支持Excel和CSV格式，请确保文件编码为UTF-8", key="general_uploader")
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
elif app_mode == "水体数据分析":
    st.header("水体数据分析")
    
    # 添加说明
    st.markdown("""
    ### 功能说明
    本功能用于分析水体数据，包括自然和非自然水体的面积统计、不同年份的水体数量和面积变化等。
    
    #### 数据要求
    输入的Excel表格需要包含以下列：
    - `Type`列：包含"nature"和"non-nature"值，表示水体类型
    - `country`列：表示国家名称，可能有重复值（代表同一国家的不同水体）
    - `1990`-`2020`年份列：每一列代表该年份的水体面积值，空值（缺失值）不进行统计
    
    > 注意：如果您的数据不完全符合上述格式，系统将尝试自动识别相关列。
    """)
    
    # 文件上传
    uploaded_file = st.file_uploader("上传水体数据文件", type=["xlsx", "csv"], help="支持Excel和CSV格式", key="water_body_uploader")
    
    if uploaded_file is not None:
        # 加载数据
        file_extension = get_file_extension(uploaded_file.name)
        try:
            df = load_data(uploaded_file, file_extension)
            st.success(f"成功加载文件: {uploaded_file.name}")
            
            # 显示数据预览
            st.subheader("数据预览")
            st.dataframe(df.head(10), height=300, use_container_width=True)
            
            # 检查会话状态中是否有保存的结果
            if st.session_state.water_body_results is not None and st.button("显示上次分析结果"):
                results = st.session_state.water_body_results
                temp_dir = st.session_state.water_body_temp_dir
                st.success("已加载上次分析结果")
                
                # 显示结果
                st.subheader("分析结果")
                
                # 创建选项卡
                tabs = st.tabs(["国家统计", "类型统计", "年份统计", "图表展示", "水体分析图表", "下载结果"])
                
                # 国家统计选项卡
                with tabs[0]:
                    st.write("#### 各国水体统计")
                    st.dataframe(results['total']['country'], use_container_width=True)
                    
                    # 添加下载按钮
                    country_csv = results['total']['country'].to_csv(index=True).encode('utf-8')
                    st.download_button(
                        label="下载各国水体统计数据",
                        data=country_csv,
                        file_name="country_water_body_statistics.csv",
                        mime="text/csv"
                    )
                
                # 类型统计选项卡
                with tabs[1]:
                    st.write("#### 自然/非自然水体数量")
                    st.dataframe(results['by_type']['counts'], use_container_width=True)
                    
                    # 添加下载按钮
                    type_counts_csv = results['by_type']['counts'].to_csv(index=True).encode('utf-8')
                    st.download_button(
                        label="下载自然/非自然水体数量统计",
                        data=type_counts_csv,
                        file_name="water_body_type_counts.csv",
                        mime="text/csv"
                    )
                    
                    st.write("#### 自然/非自然水体面积随年份变化")
                    st.dataframe(results['by_type']['areas'], use_container_width=True)
                    
                    # 添加下载按钮
                    type_areas_csv = results['by_type']['areas'].to_csv(index=True).encode('utf-8')
                    st.download_button(
                        label="下载自然/非自然水体面积统计",
                        data=type_areas_csv,
                        file_name="water_body_type_areas.csv",
                        mime="text/csv"
                    )
                
                # 年份统计选项卡
                with tabs[2]:
                    st.write("#### 各年份水体数量和面积")
                    st.dataframe(results['by_year'], use_container_width=True)
                    
                    # 添加下载按钮
                    by_year_csv = results['by_year'].to_csv(index=True).encode('utf-8')
                    st.download_button(
                        label="下载各年份水体统计数据",
                        data=by_year_csv,
                        file_name="yearly_water_body_statistics.csv",
                        mime="text/csv"
                    )
                    
                    st.write("#### 各年份自然/非自然水体统计")
                    # 格式化列名以提高可读性
                    yearly_type_stats = results['yearly_type_stats'].copy()
                    column_mapping = {
                        'nature_数量': '自然水体数量',
                        'nature_面积': '自然水体面积',
                        'non-nature_数量': '非自然水体数量',
                        'non-nature_面积': '非自然水体面积'
                    }
                    yearly_type_stats.rename(columns=column_mapping, inplace=True)
                    st.dataframe(yearly_type_stats, use_container_width=True)
                    
                    # 添加下载按钮
                    yearly_type_csv = yearly_type_stats.to_csv(index=True).encode('utf-8')
                    st.download_button(
                        label="下载各年份自然/非自然水体统计",
                        data=yearly_type_csv,
                        file_name="yearly_type_water_body_statistics.csv",
                        mime="text/csv"
                    )
                
                # 图表展示选项卡
                with tabs[3]:
                    st.write("#### 各国水体总面积（前10名）")
                    st.image(os.path.join(temp_dir, "各国水体总面积.png"))
                    
                    st.write("#### 自然/非自然水体数量对比")
                    st.image(os.path.join(temp_dir, "自然非自然水体数量对比.png"))
                    
                    st.write("#### 自然/非自然水体面积随年份变化")
                    st.image(os.path.join(temp_dir, "自然非自然水体面积年份变化.png"))
                    
                    st.write("#### 各年份水体数量变化")
                    st.image(os.path.join(temp_dir, "各年份水体数量变化.png"))
                    
                    st.write("#### 各年份水体总面积变化")
                    st.image(os.path.join(temp_dir, "各年份水体总面积变化.png"))
                
                # 水体分析图表选项卡
                with tabs[4]:
                    st.write("#### 水体分析综合图表")
                    st.write("这个图表展示了水体数据的综合分析，包括面积变化趋势、数量变化、大小分布和气候因素。")
                    
                    # 准备数据
                    chart_data = prepare_data_from_analysis_results(results)
                    
                    # 生成图表
                    water_body_chart_path = os.path.join(temp_dir, "water_body_analysis_chart.png")
                    generate_water_body_analysis_chart(chart_data, water_body_chart_path)
                    
                    # 显示图表
                    st.image(water_body_chart_path)
                    
                    # 添加图表说明
                    with st.expander("图表说明"):
                        st.markdown("""
                        #### 图表解释
                        
                        **子图 (a)**: 展示了咸海面积随时间的变化趋势，包括斜率信息。
                        
                        **子图 (b)**: 展示了除咸海外的水体面积和数量随时间的变化趋势，左侧Y轴表示面积，右侧Y轴表示数量。
                        
                        **子图 (c)**: 展示了不同大小水体的面积和数量变化率，浅蓝色柱状图表示数量变化率，深蓝色柱状图表示面积变化率。
                        
                        **子图 (d)**: 展示了温度和降水随时间的变化趋势，橙色线表示温度，蓝色柱状图表示降水。
                        """)
                
                # 下载结果选项卡
                with tabs[5]:
                    st.write("#### 下载分析结果")
                    
                    # 提供Excel下载
                    excel_path = os.path.join(temp_dir, "water_body_statistics.xlsx")
                    with open(excel_path, "rb") as file:
                        excel_bytes = file.read()
                        
                    st.download_button(
                        label="下载Excel统计结果",
                        data=excel_bytes,
                        file_name="water_body_statistics.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    # 提供图表打包下载
                    # 创建一个ZIP文件
                    zip_path = os.path.join(temp_dir, "water_body_charts.zip")
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for chart_file in os.listdir(temp_dir):
                            if chart_file.endswith('.png'):
                                zipf.write(os.path.join(temp_dir, chart_file), chart_file)
                    
                    # 提供ZIP下载
                    with open(zip_path, "rb") as file:
                        zip_bytes = file.read()
                        
                    st.download_button(
                        label="下载所有图表 (ZIP)",
                        data=zip_bytes,
                        file_name="water_body_charts.zip",
                        mime="application/zip"
                    )
            # 分析按钮
            elif st.button("分析水体数据"):
                # 创建进度条
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 更新进度
                status_text.text("正在分析数据...")
                progress_bar.progress(20)
                
                # 分析数据
                try:
                    results = analyze_water_body_data(df)
                    
                    # 更新进度
                    status_text.text("正在生成图表...")
                    progress_bar.progress(50)
                    
                    # 创建临时目录用于存储图表
                    temp_dir = "temp_output"
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    # 生成图表
                    generate_charts(results, temp_dir)
                    
                    # 更新进度
                    status_text.text("正在保存结果...")
                    progress_bar.progress(80)
                    
                    # 保存结果到Excel
                    excel_path = os.path.join(temp_dir, "water_body_statistics.xlsx")
                    save_results_to_excel(results, excel_path)
                    
                    # 保存结果到会话状态
                    st.session_state.water_body_results = results
                    st.session_state.water_body_temp_dir = temp_dir
                    
                    # 完成进度
                    progress_bar.progress(100)
                    status_text.text("分析完成!")
                    
                    # 显示结果
                    st.subheader("分析结果")
                    
                    # 创建选项卡
                    tabs = st.tabs(["国家统计", "类型统计", "年份统计", "图表展示", "水体分析图表", "下载结果"])
                    
                    # 国家统计选项卡
                    with tabs[0]:
                        st.write("#### 各国水体统计")
                        st.dataframe(results['total']['country'], use_container_width=True)
                        
                        # 添加下载按钮
                        country_csv = results['total']['country'].to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label="下载各国水体统计数据",
                            data=country_csv,
                            file_name="country_water_body_statistics.csv",
                            mime="text/csv"
                        )
                    
                    # 类型统计选项卡
                    with tabs[1]:
                        st.write("#### 自然/非自然水体数量")
                        st.dataframe(results['by_type']['counts'], use_container_width=True)
                        
                        # 添加下载按钮
                        type_counts_csv = results['by_type']['counts'].to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label="下载自然/非自然水体数量统计",
                            data=type_counts_csv,
                            file_name="water_body_type_counts.csv",
                            mime="text/csv"
                        )
                        
                        st.write("#### 自然/非自然水体面积随年份变化")
                        st.dataframe(results['by_type']['areas'], use_container_width=True)
                        
                        # 添加下载按钮
                        type_areas_csv = results['by_type']['areas'].to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label="下载自然/非自然水体面积统计",
                            data=type_areas_csv,
                            file_name="water_body_type_areas.csv",
                            mime="text/csv"
                        )
                    
                    # 年份统计选项卡
                    with tabs[2]:
                        st.write("#### 各年份水体数量和面积")
                        st.dataframe(results['by_year'], use_container_width=True)
                        
                        # 添加下载按钮
                        by_year_csv = results['by_year'].to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label="下载各年份水体统计数据",
                            data=by_year_csv,
                            file_name="yearly_water_body_statistics.csv",
                            mime="text/csv"
                        )
                        
                        st.write("#### 各年份自然/非自然水体统计")
                        # 格式化列名以提高可读性
                        yearly_type_stats = results['yearly_type_stats'].copy()
                        column_mapping = {
                            'nature_数量': '自然水体数量',
                            'nature_面积': '自然水体面积',
                            'non-nature_数量': '非自然水体数量',
                            'non-nature_面积': '非自然水体面积'
                        }
                        yearly_type_stats.rename(columns=column_mapping, inplace=True)
                        st.dataframe(yearly_type_stats, use_container_width=True)
                        
                        # 添加下载按钮
                        yearly_type_csv = yearly_type_stats.to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label="下载各年份自然/非自然水体统计",
                            data=yearly_type_csv,
                            file_name="yearly_type_water_body_statistics.csv",
                            mime="text/csv"
                        )
                    
                    # 图表展示选项卡
                    with tabs[3]:
                        st.write("#### 各国水体总面积（前10名）")
                        st.image(os.path.join(temp_dir, "各国水体总面积.png"))
                        
                        st.write("#### 自然/非自然水体数量对比")
                        st.image(os.path.join(temp_dir, "自然非自然水体数量对比.png"))
                        
                        st.write("#### 自然/非自然水体面积随年份变化")
                        st.image(os.path.join(temp_dir, "自然非自然水体面积年份变化.png"))
                        
                        st.write("#### 各年份水体数量变化")
                        st.image(os.path.join(temp_dir, "各年份水体数量变化.png"))
                        
                        st.write("#### 各年份水体总面积变化")
                        st.image(os.path.join(temp_dir, "各年份水体总面积变化.png"))
                    
                    # 水体分析图表选项卡
                    with tabs[4]:
                        st.write("#### 水体分析综合图表")
                        st.write("这个图表展示了水体数据的综合分析，包括面积变化趋势、数量变化、大小分布和气候因素。")
                        
                        # 准备数据
                        chart_data = prepare_data_from_analysis_results(results)
                        
                        # 生成图表
                        water_body_chart_path = os.path.join(temp_dir, "water_body_analysis_chart.png")
                        generate_water_body_analysis_chart(chart_data, water_body_chart_path)
                        
                        # 显示图表
                        st.image(water_body_chart_path)
                        
                        # 添加图表说明
                        with st.expander("图表说明"):
                            st.markdown("""
                            #### 图表解释
                            
                            **子图 (a)**: 展示了咸海面积随时间的变化趋势，包括斜率信息。
                            
                            **子图 (b)**: 展示了除咸海外的水体面积和数量随时间的变化趋势，左侧Y轴表示面积，右侧Y轴表示数量。
                            
                            **子图 (c)**: 展示了不同大小水体的面积和数量变化率，浅蓝色柱状图表示数量变化率，深蓝色柱状图表示面积变化率。
                            
                            **子图 (d)**: 展示了温度和降水随时间的变化趋势，橙色线表示温度，蓝色柱状图表示降水。
                            """)
                    
                    # 下载结果选项卡
                    with tabs[5]:
                        st.write("#### 下载分析结果")
                        
                        # 提供Excel下载
                        with open(excel_path, "rb") as file:
                            excel_bytes = file.read()
                            
                        st.download_button(
                            label="下载Excel统计结果",
                            data=excel_bytes,
                            file_name="water_body_statistics.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        # 提供图表打包下载
                        # 创建一个ZIP文件
                        zip_path = os.path.join(temp_dir, "water_body_charts.zip")
                        with zipfile.ZipFile(zip_path, 'w') as zipf:
                            for chart_file in os.listdir(temp_dir):
                                if chart_file.endswith('.png'):
                                    zipf.write(os.path.join(temp_dir, chart_file), chart_file)
                        
                        # 提供ZIP下载
                        with open(zip_path, "rb") as file:
                            zip_bytes = file.read()
                            
                        st.download_button(
                            label="下载所有图表 (ZIP)",
                            data=zip_bytes,
                            file_name="water_body_charts.zip",
                            mime="application/zip"
                        )
                        
                except Exception as e:
                    st.error(f"分析过程中出错: {str(e)}")
                    # 重置进度条
                    progress_bar.progress(0)
                    status_text.text("分析失败")
        except Exception as e:
            st.error(f"文件加载失败: {str(e)}")
    else:
        # 提供示例数据选项
        if upload_option == "使用示例数据":
            sample_data_path = os.path.join("data", "sample", "water_body_data.xlsx")
            if os.path.exists(sample_data_path):
                st.info("使用水体数据示例")
                df = load_data(sample_data_path, "xlsx")
                
                # 显示数据预览
                st.subheader("数据预览")
                st.dataframe(df.head(10), height=300, use_container_width=True)
                
                # 检查会话状态中是否有保存的结果
                if st.session_state.water_body_results is not None and st.button("显示上次分析结果"):
                    results = st.session_state.water_body_results
                    temp_dir = st.session_state.water_body_temp_dir
                    st.success("已加载上次分析结果")
                    
                    # 显示结果
                    st.subheader("分析结果")
                    
                    # 创建选项卡
                    tabs = st.tabs(["国家统计", "类型统计", "年份统计", "图表展示", "水体分析图表", "下载结果"])
                    
                    # 国家统计选项卡
                    with tabs[0]:
                        st.write("#### 各国水体统计")
                        st.dataframe(results['total']['country'], use_container_width=True)
                        
                        # 添加下载按钮
                        country_csv = results['total']['country'].to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label="下载各国水体统计数据",
                            data=country_csv,
                            file_name="country_water_body_statistics.csv",
                            mime="text/csv"
                        )
                    
                    # 类型统计选项卡
                    with tabs[1]:
                        st.write("#### 自然/非自然水体数量")
                        st.dataframe(results['by_type']['counts'], use_container_width=True)
                        
                        # 添加下载按钮
                        type_counts_csv = results['by_type']['counts'].to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label="下载自然/非自然水体数量统计",
                            data=type_counts_csv,
                            file_name="water_body_type_counts.csv",
                            mime="text/csv"
                        )
                        
                        st.write("#### 自然/非自然水体面积随年份变化")
                        st.dataframe(results['by_type']['areas'], use_container_width=True)
                        
                        # 添加下载按钮
                        type_areas_csv = results['by_type']['areas'].to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label="下载自然/非自然水体面积统计",
                            data=type_areas_csv,
                            file_name="water_body_type_areas.csv",
                            mime="text/csv"
                        )
                    
                    # 年份统计选项卡
                    with tabs[2]:
                        st.write("#### 各年份水体数量和面积")
                        st.dataframe(results['by_year'], use_container_width=True)
                        
                        # 添加下载按钮
                        by_year_csv = results['by_year'].to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label="下载各年份水体统计数据",
                            data=by_year_csv,
                            file_name="yearly_water_body_statistics.csv",
                            mime="text/csv"
                        )
                        
                        st.write("#### 各年份自然/非自然水体统计")
                        # 格式化列名以提高可读性
                        yearly_type_stats = results['yearly_type_stats'].copy()
                        column_mapping = {
                            'nature_数量': '自然水体数量',
                            'nature_面积': '自然水体面积',
                            'non-nature_数量': '非自然水体数量',
                            'non-nature_面积': '非自然水体面积'
                        }
                        yearly_type_stats.rename(columns=column_mapping, inplace=True)
                        st.dataframe(yearly_type_stats, use_container_width=True)
                        
                        # 添加下载按钮
                        yearly_type_csv = yearly_type_stats.to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label="下载各年份自然/非自然水体统计",
                            data=yearly_type_csv,
                            file_name="yearly_type_water_body_statistics.csv",
                            mime="text/csv"
                        )
                    
                    # 图表展示选项卡
                    with tabs[3]:
                        st.write("#### 各国水体总面积（前10名）")
                        st.image(os.path.join(temp_dir, "各国水体总面积.png"))
                        
                        st.write("#### 自然/非自然水体数量对比")
                        st.image(os.path.join(temp_dir, "自然非自然水体数量对比.png"))
                        
                        st.write("#### 自然/非自然水体面积随年份变化")
                        st.image(os.path.join(temp_dir, "自然非自然水体面积年份变化.png"))
                        
                        st.write("#### 各年份水体数量变化")
                        st.image(os.path.join(temp_dir, "各年份水体数量变化.png"))
                        
                        st.write("#### 各年份水体总面积变化")
                        st.image(os.path.join(temp_dir, "各年份水体总面积变化.png"))
                    
                    # 水体分析图表选项卡
                    with tabs[4]:
                        st.write("#### 水体分析综合图表")
                        st.write("这个图表展示了水体数据的综合分析，包括面积变化趋势、数量变化、大小分布和气候因素。")
                        
                        # 准备数据
                        chart_data = prepare_data_from_analysis_results(results)
                        
                        # 生成图表
                        water_body_chart_path = os.path.join(temp_dir, "water_body_analysis_chart.png")
                        generate_water_body_analysis_chart(chart_data, water_body_chart_path)
                        
                        # 显示图表
                        st.image(water_body_chart_path)
                        
                        # 添加图表说明
                        with st.expander("图表说明"):
                            st.markdown("""
                            #### 图表解释
                            
                            **子图 (a)**: 展示了咸海面积随时间的变化趋势，包括斜率信息。
                            
                            **子图 (b)**: 展示了除咸海外的水体面积和数量随时间的变化趋势，左侧Y轴表示面积，右侧Y轴表示数量。
                            
                            **子图 (c)**: 展示了不同大小水体的面积和数量变化率，浅蓝色柱状图表示数量变化率，深蓝色柱状图表示面积变化率。
                            
                            **子图 (d)**: 展示了温度和降水随时间的变化趋势，橙色线表示温度，蓝色柱状图表示降水。
                            """)
                    
                    # 下载结果选项卡
                    with tabs[5]:
                        st.write("#### 下载分析结果")
                        
                        # 提供Excel下载
                        excel_path = os.path.join(temp_dir, "water_body_statistics.xlsx")
                        with open(excel_path, "rb") as file:
                            excel_bytes = file.read()
                            
                        st.download_button(
                            label="下载Excel统计结果",
                            data=excel_bytes,
                            file_name="water_body_statistics.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        # 提供图表打包下载
                        # 创建一个ZIP文件
                        zip_path = os.path.join(temp_dir, "water_body_charts.zip")
                        with zipfile.ZipFile(zip_path, 'w') as zipf:
                            for chart_file in os.listdir(temp_dir):
                                if chart_file.endswith('.png'):
                                    zipf.write(os.path.join(temp_dir, chart_file), chart_file)
                        
                        # 提供ZIP下载
                        with open(zip_path, "rb") as file:
                            zip_bytes = file.read()
                            
                        st.download_button(
                            label="下载所有图表 (ZIP)",
                            data=zip_bytes,
                            file_name="water_body_charts.zip",
                            mime="application/zip"
                        )
                # 分析按钮
                elif st.button("分析示例水体数据"):
                    # 创建进度条
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 更新进度
                    status_text.text("正在分析数据...")
                    progress_bar.progress(20)
                    
                    # 分析数据
                    try:
                        results = analyze_water_body_data(df)
                        
                        # 更新进度
                        status_text.text("正在生成图表...")
                        progress_bar.progress(50)
                        
                        # 创建临时目录用于存储图表
                        temp_dir = "temp_output"
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        # 生成图表
                        generate_charts(results, temp_dir)
                        
                        # 更新进度
                        status_text.text("正在保存结果...")
                        progress_bar.progress(80)
                        
                        # 保存结果到Excel
                        excel_path = os.path.join(temp_dir, "water_body_statistics.xlsx")
                        save_results_to_excel(results, excel_path)
                        
                        # 保存结果到会话状态
                        st.session_state.water_body_results = results
                        st.session_state.water_body_temp_dir = temp_dir
                        
                        # 完成进度
                        progress_bar.progress(100)
                        status_text.text("分析完成!")
                        
                        # 显示结果
                        st.subheader("分析结果")
                        
                        # 创建选项卡
                        tabs = st.tabs(["国家统计", "类型统计", "年份统计", "图表展示", "水体分析图表", "下载结果"])
                        
                        # 国家统计选项卡
                        with tabs[0]:
                            st.write("#### 各国水体统计")
                            st.dataframe(results['total']['country'], use_container_width=True)
                            
                            # 添加下载按钮
                            country_csv = results['total']['country'].to_csv(index=True).encode('utf-8')
                            st.download_button(
                                label="下载各国水体统计数据",
                                data=country_csv,
                                file_name="country_water_body_statistics.csv",
                                mime="text/csv"
                            )
                        
                        # 类型统计选项卡
                        with tabs[1]:
                            st.write("#### 自然/非自然水体数量")
                            st.dataframe(results['by_type']['counts'], use_container_width=True)
                            
                            # 添加下载按钮
                            type_counts_csv = results['by_type']['counts'].to_csv(index=True).encode('utf-8')
                            st.download_button(
                                label="下载自然/非自然水体数量统计",
                                data=type_counts_csv,
                                file_name="water_body_type_counts.csv",
                                mime="text/csv"
                            )
                            
                            st.write("#### 自然/非自然水体面积随年份变化")
                            st.dataframe(results['by_type']['areas'], use_container_width=True)
                            
                            # 添加下载按钮
                            type_areas_csv = results['by_type']['areas'].to_csv(index=True).encode('utf-8')
                            st.download_button(
                                label="下载自然/非自然水体面积统计",
                                data=type_areas_csv,
                                file_name="water_body_type_areas.csv",
                                mime="text/csv"
                            )
                        
                        # 年份统计选项卡
                        with tabs[2]:
                            st.write("#### 各年份水体数量和面积")
                            st.dataframe(results['by_year'], use_container_width=True)
                            
                            # 添加下载按钮
                            by_year_csv = results['by_year'].to_csv(index=True).encode('utf-8')
                            st.download_button(
                                label="下载各年份水体统计数据",
                                data=by_year_csv,
                                file_name="yearly_water_body_statistics.csv",
                                mime="text/csv"
                            )
                            
                            st.write("#### 各年份自然/非自然水体统计")
                            # 格式化列名以提高可读性
                            yearly_type_stats = results['yearly_type_stats'].copy()
                            column_mapping = {
                                'nature_数量': '自然水体数量',
                                'nature_面积': '自然水体面积',
                                'non-nature_数量': '非自然水体数量',
                                'non-nature_面积': '非自然水体面积'
                            }
                            yearly_type_stats.rename(columns=column_mapping, inplace=True)
                            st.dataframe(yearly_type_stats, use_container_width=True)
                            
                            # 添加下载按钮
                            yearly_type_csv = yearly_type_stats.to_csv(index=True).encode('utf-8')
                            st.download_button(
                                label="下载各年份自然/非自然水体统计",
                                data=yearly_type_csv,
                                file_name="yearly_type_water_body_statistics.csv",
                                mime="text/csv"
                            )
                        
                        # 图表展示选项卡
                        with tabs[3]:
                            st.write("#### 各国水体总面积（前10名）")
                            st.image(os.path.join(temp_dir, "各国水体总面积.png"))
                            
                            st.write("#### 自然/非自然水体数量对比")
                            st.image(os.path.join(temp_dir, "自然非自然水体数量对比.png"))
                            
                            st.write("#### 自然/非自然水体面积随年份变化")
                            st.image(os.path.join(temp_dir, "自然非自然水体面积年份变化.png"))
                            
                            st.write("#### 各年份水体数量变化")
                            st.image(os.path.join(temp_dir, "各年份水体数量变化.png"))
                            
                            st.write("#### 各年份水体总面积变化")
                            st.image(os.path.join(temp_dir, "各年份水体总面积变化.png"))
                    
                        # 水体分析图表选项卡
                        with tabs[4]:
                            st.write("#### 水体分析综合图表")
                            st.write("这个图表展示了水体数据的综合分析，包括面积变化趋势、数量变化、大小分布和气候因素。")
                        
                            # 准备数据
                            chart_data = prepare_data_from_analysis_results(results)
                            
                            # 生成图表
                            water_body_chart_path = os.path.join(temp_dir, "water_body_analysis_chart.png")
                            generate_water_body_analysis_chart(chart_data, water_body_chart_path)
                            
                            # 显示图表
                            st.image(water_body_chart_path)
                            
                            # 添加图表说明
                            with st.expander("图表说明"):
                                st.markdown("""
                                #### 图表解释
                                
                                **子图 (a)**: 展示了咸海面积随时间的变化趋势，包括斜率信息。
                                
                                **子图 (b)**: 展示了除咸海外的水体面积和数量随时间的变化趋势，左侧Y轴表示面积，右侧Y轴表示数量。
                                
                                **子图 (c)**: 展示了不同大小水体的面积和数量变化率，浅蓝色柱状图表示数量变化率，深蓝色柱状图表示面积变化率。
                                
                                **子图 (d)**: 展示了温度和降水随时间的变化趋势，橙色线表示温度，蓝色柱状图表示降水。
                                """)
                    
                        # 下载结果选项卡
                        with tabs[5]:
                            st.write("#### 下载分析结果")
                            
                            # 提供Excel下载
                            with open(excel_path, "rb") as file:
                                excel_bytes = file.read()
                                
                            st.download_button(
                                label="下载Excel统计结果",
                                data=excel_bytes,
                                file_name="water_body_statistics.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                            
                            # 提供图表打包下载
                            # 创建一个ZIP文件
                            zip_path = os.path.join(temp_dir, "water_body_charts.zip")
                            with zipfile.ZipFile(zip_path, 'w') as zipf:
                                for chart_file in os.listdir(temp_dir):
                                    if chart_file.endswith('.png'):
                                        zipf.write(os.path.join(temp_dir, chart_file), chart_file)
                            
                            # 提供ZIP下载
                            with open(zip_path, "rb") as file:
                                zip_bytes = file.read()
                                
                            st.download_button(
                                label="下载所有图表 (ZIP)",
                                data=zip_bytes,
                                file_name="water_body_charts.zip",
                                mime="application/zip"
                            )
                    except Exception as e:
                        st.error(f"分析过程中出错: {str(e)}")
                        # 重置进度条
                        progress_bar.progress(0)
                        status_text.text("分析失败")
            else:
                st.error("示例水体数据文件不存在，请先运行 create_water_body_sample.py 创建示例数据")
                if st.button("创建示例水体数据"):
                    try:
                        from create_water_body_sample import create_water_body_sample
                        output_path = create_water_body_sample()
                        st.success(f"示例水体数据已创建: {output_path}")
                        st.info("请刷新页面以加载示例数据")
                    except Exception as e:
                        st.error(f"创建示例数据失败: {str(e)}")
        else:
            st.info("请上传水体数据文件或选择使用示例数据以开始分析")
else:
    st.info("请上传数据文件或选择示例数据以开始")
