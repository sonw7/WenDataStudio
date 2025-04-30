import os
import matplotlib.pyplot as plt
from src.visualization.water_body_charts import create_sample_data, generate_water_body_analysis_chart

def test_water_body_charts():
    """测试水体分析图表生成功能"""
    print("正在测试水体分析图表生成功能...")
    
    # 创建输出目录
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建示例数据
    print("创建示例数据...")
    sample_data = create_sample_data()
    
    # 生成图表
    print("生成水体分析图表...")
    output_path = os.path.join(output_dir, 'water_body_analysis_chart.png')
    fig = generate_water_body_analysis_chart(sample_data, output_path)
    
    print(f"图表已保存到: {output_path}")
    
    # 显示图表
    plt.show()
    
    return True

if __name__ == "__main__":
    test_water_body_charts()
