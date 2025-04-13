#!/bin/bash
echo "正在启动 WenDataStudio..."
echo "请稍候..."

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "安装依赖..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "启动应用..."
streamlit run app.py