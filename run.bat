@echo off
echo 正在启动 WenDataStudio...
echo 请稍候...

if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate
    echo 安装依赖...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

echo 启动应用...
streamlit run app.py

pause