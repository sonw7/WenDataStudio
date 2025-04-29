# 该文件定义了数据加载函数，用于从不同类型的文件（如CSV和Excel）加载数据到 pandas DataFrame。
import pandas as pd
import io

def load_data(file, file_type):
    """
    加载数据文件
    
    参数:
        file: 文件对象或文件路径
        file_type: 文件类型 ('csv' 或 'xlsx')
        
    返回:
        pandas DataFrame 对象
    """
    try:
        # 确保file_type是字符串类型
        file_type_str = str(file_type).lower()
        
        if file_type_str == 'csv':
            # 如果文件类型是 CSV
            # 尝试使用 UTF-8 编码读取 CSV 文件
            try:
                return pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                # 如果 UTF-8 解码失败，则尝试使用 GBK 编码
                return pd.read_csv(file, encoding='gbk')
        elif file_type_str == 'xlsx':
            # 如果文件类型是 Excel，则使用 pandas 读取 Excel 文件
            return pd.read_excel(file)
        else:
            # 如果文件类型不受支持，则引发 ValueError 异常
            raise ValueError(f"不支持的文件类型: {file_type_str}")
    except Exception as e:
        # 捕获加载文件时可能发生的任何异常，并重新引发一个包含详细错误消息的异常
        raise Exception(f"加载文件时出错: {str(e)}")
