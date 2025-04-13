import pandas as pd

def clean_data(df, clean_na=True, remove_duplicates=True):
    """
    清洗数据
    
    参数:
        df: pandas DataFrame
        clean_na: 是否处理缺失值
        remove_duplicates: 是否删除重复行
        
    返回:
        清洗后的 pandas DataFrame
    """
    if clean_na:
        # 对数值列使用中位数填充
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            df[col] = df[col].fillna(df[col].median())
        
        # 对分类列使用众数填充
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "未知")
    
    if remove_duplicates:
        df = df.drop_duplicates()
    
    return df