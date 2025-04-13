import pandas as pd
import numpy as np

def transform_data(df, transformations=None):
    """
    转换数据
    
    参数:
        df: pandas DataFrame
        transformations: 要应用的转换列表
        
    返回:
        转换后的 pandas DataFrame
    """
    if transformations is None:
        return df
        
    df_transformed = df.copy()
    
    for transform in transformations:
        transform_type = transform.get('type')
        column = transform.get('column')
        
        if transform_type == 'normalize':
            df_transformed[column] = (df_transformed[column] - df_transformed[column].min()) / \
                                    (df_transformed[column].max() - df_transformed[column].min())
                                    
        elif transform_type == 'standardize':
            df_transformed[column] = (df_transformed[column] - df_transformed[column].mean()) / \
                                    df_transformed[column].std()
                                    
        elif transform_type == 'log':
            # 确保数据为正
            if (df_transformed[column] <= 0).any():
                df_transformed[column] = df_transformed[column] - df_transformed[column].min() + 1
            df_transformed[column] = np.log(df_transformed[column])
            
    return df_transformed