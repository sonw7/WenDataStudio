#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from water_body_analysis import load_water_body_data, analyze_water_body_data, generate_charts, save_results_to_excel
from create_water_body_sample import create_water_body_sample

def main():
    """水体数据分析工具命令行界面"""
    parser = argparse.ArgumentParser(description='水体数据分析工具')
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建示例数据命令
    create_parser = subparsers.add_parser('create-sample', help='创建示例水体数据')
    
    # 分析数据命令
    analyze_parser = subparsers.add_parser('analyze', help='分析水体数据')
    analyze_parser.add_argument('file', help='Excel文件路径')
    analyze_parser.add_argument('-o', '--output', default='output', help='输出目录路径')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 如果没有提供命令，显示帮助信息
    if not args.command:
        parser.print_help()
        return
    
    # 处理命令
    if args.command == 'create-sample':
        print("正在创建示例水体数据...")
        output_path = create_water_body_sample()
        print(f"示例数据已创建: {output_path}")
        print(f"您可以使用以下命令分析此示例数据:")
        print(f"python {sys.argv[0]} analyze {output_path}")
        
    elif args.command == 'analyze':
        # 检查文件是否存在
        if not os.path.exists(args.file):
            print(f"错误: 文件 {args.file} 不存在")
            return
        
        try:
            # 创建输出目录
            os.makedirs(args.output, exist_ok=True)
            
            print(f"正在分析水体数据: {args.file}")
            
            # 加载数据
            df = load_water_body_data(args.file)
            
            # 显示数据预览
            print("\n数据预览:")
            print(df.head())
            
            # 分析数据
            print("\n正在分析数据...")
            results = analyze_water_body_data(df)
            
            # 生成图表
            print("\n正在生成图表...")
            generate_charts(results, args.output)
            
            # 保存结果到Excel
            excel_output = os.path.join(args.output, 'water_body_statistics.xlsx')
            print("\n正在保存结果到Excel...")
            save_results_to_excel(results, excel_output)
            
            print("\n分析完成!")
            print(f"结果已保存到 {args.output} 目录")
            
        except Exception as e:
            print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()
