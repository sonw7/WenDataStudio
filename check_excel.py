import pandas as pd
import sys

def check_excel_file(file_path):
    """
    检查Excel文件的结构，打印列名和数据类型信息
    
    参数:
        file_path: Excel文件路径
    """
    try:
        print(f"尝试读取文件: {file_path}")
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 打印基本信息
        print(f"\n文件读取成功!")
        print(f"数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
        
        # 打印列名信息
        print("\n列名信息:")
        for i, col in enumerate(df.columns):
            print(f"列 {i}: 名称='{col}', 类型={type(col).__name__}")
        
        # 打印前5行数据
        print("\n数据预览 (前5行):")
        print(df.head())
        
        # 打印数据类型信息
        print("\n数据类型信息:")
        print(df.dtypes)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        check_excel_file(file_path)
    else:
        print("请提供Excel文件路径作为参数")
