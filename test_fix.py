import os
import sys
from src.data_processing.loader import load_data
from water_body_analysis import analyze_water_body_data

def test_load_and_analyze():
    """
    测试修复后的代码能否正确加载和分析Excel文件
    """
    file_path = "data/sample/WAalb area interpolation.xlsx"
    
    try:
        print(f"尝试加载文件: {file_path}")
        file_type = os.path.splitext(file_path)[1][1:]
        print(f"文件类型: {file_type}, 类型: {type(file_type)}")
        
        # 测试加载数据
        df = load_data(file_path, file_type)
        print(f"数据加载成功! 形状: {df.shape[0]} 行 × {df.shape[1]} 列")
        
        # 测试分析数据
        print("\n尝试分析数据...")
        results = analyze_water_body_data(df)
        print("数据分析成功!")
        
        # 打印部分结果
        print("\n分析结果摘要:")
        if 'total' in results and 'country' in results['total']:
            print(f"- 国家统计: {len(results['total']['country'])} 条记录")
        if 'by_type' in results and 'counts' in results['by_type']:
            print(f"- 类型统计: {len(results['by_type']['counts'])} 条记录")
        if 'by_year' in results:
            print(f"- 年份统计: {len(results['by_year'])} 条记录")
        
        print("\n测试成功完成!")
        return True
        
    except Exception as e:
        print(f"错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    test_load_and_analyze()
