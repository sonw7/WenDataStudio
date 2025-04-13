import os
import pandas as pd

def get_file_extension(filename):
    """获取文件扩展名"""
    return os.path.splitext(filename)[1][1:].lower()

def save_dataframe(df, file_path, file_type="xlsx"):
    """保存DataFrame到文件"""
    try:
        if file_type.lower() == "xlsx":
            df.to_excel(file_path, index=False)
        elif file_type.lower() == "csv":
            df.to_csv(file_path, index=False, encoding="utf-8")
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
        return True
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")
        return False