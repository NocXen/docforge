"""
测试工作流运行脚本
使用DocForge框架执行工作流
"""

import sys
import json
from pathlib import Path
import os

from docforge.api import CoreAPI

def main():
    print("=" * 50)
    print("DocForge 工作流实例")
    print("=" * 50)
    
    # 初始化CoreAPI - 使用实例目录的配置文件
    api = CoreAPI()
    config_path = Path(__file__).parent / "config.json"
    if not api.initialize(str(config_path)):
        print("框架初始化失败")
        return
    
    # 加载工作流配置
    workflow_path = Path(__file__).parent / "workflow.json"
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow_config = json.load(f)
    
    print(f"\n工作流名称: {workflow_config['name']}")
    print(f"工作流描述: {workflow_config['description']}")
    print(f"步骤数量: {len(workflow_config['steps'])}")
    
    # 准备输入文件
    input_path = Path(__file__).parent / "input"
    input_file = []
    for root, ds, fs in os.walk(input_path):
        for f in fs:
            if f.endswith('.xlsx'):
                input_file.append(os.path.join(root, f))

    if not input_path.exists():
        print(f"\n错误: 输入路径不存在: {input_path}")
        return
    
    print(f"\n输入文件: {input_file}")
    
    # 准备模板文件
    template_path = Path(__file__).parent / "template"
    template_file = []
    for root, ds, fs in os.walk(template_path):
        for f in fs:
            if f.endswith('.docx'):
                template_file.append(os.path.join(root, f))
    
    if not template_path.exists():
        print(f"错误: 模板路径不存在: {template_path}")
        return
    
    print(f"模板文件: {template_file}")
    
    # 设置输出目录
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    print(f"输出目录: {output_dir}")
    
    # 创建测试项目
    project_dir = Path(__file__).parent / "instance"
    if not api.create_project("测试项目", str(project_dir)):
        print("创建项目失败")
        return
    
    # 添加输入文件
    if not api.add_input_files(input_file):
        print("添加输入文件失败")
        return
    
    # 添加模板文件
    if not api.add_template_files(template_file):
        print("添加模板文件失败")
        return
    
    # 设置输出目录
    if not api.set_output_directory(str(output_dir)):
        print("设置输出目录失败")
        return
    
    # 加载工作流
    if not api.load_workflow(str(workflow_path)):
        print("加载工作流失败")
        return
    
    # 执行工作流
    print("\n" + "-" * 50)
    print("开始执行工作流...")
    print("-" * 50)
    
    try:
        # 使用CoreAPI的execute_workflow方法执行整个工作流
        result = api.execute_workflow(
            workflow_name=workflow_config['name'],
            progress_callback=lambda progress, msg: print(f"[{progress*100:.1f}%] {msg}")
        )
        
        if result.success:
            print(f"\n✓ 工作流执行成功")
            if result.output_files:
                print(f"  输出文件: {result.output_files}")
            if result.data:
                print(f"  提取的数据: {list(result.data.keys())}")
        else:
            print(f"\n✗ 工作流执行失败")
            if result.errors:
                for error in result.errors:
                    print(f"  - {error}")
        
        print("\n" + "=" * 50)
        print("工作流执行完成!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 工作流执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()