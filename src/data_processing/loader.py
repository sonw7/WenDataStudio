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
        if file_type.lower() == 'csv':
            # 尝试不同编码
            try:
                return pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                return pd.read_csv(file, encoding='gbk')
        elif file_type.lower() == 'xlsx':
            return pd.read_excel(file)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
    except Exception as e:
        raise Exception(f"加载文件时出错: {str(e)}")