"""
DocForge CLI - 命令行接口
"""

import argparse
import sys
import os
from pathlib import Path

from . import CoreAPI, __version__


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        prog='docforge',
        description='DocForge - 办公与数据处理自动化框架'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        help='可用命令'
    )
    
    # init 命令
    init_parser = subparsers.add_parser(
        'init',
        help='初始化新项目'
    )
    init_parser.add_argument(
        'name',
        help='项目名称'
    )
    init_parser.add_argument(
        '-p', '--path',
        default='.',
        help='项目路径（默认为当前目录）'
    )
    
    # run 命令
    run_parser = subparsers.add_parser(
        'run',
        help='执行工作流'
    )
    run_parser.add_argument(
        'workflow',
        help='工作流文件路径'
    )
    run_parser.add_argument(
        '-i', '--input',
        dest='input_files',
        nargs='+',
        help='输入文件列表'
    )
    run_parser.add_argument(
        '-t', '--template',
        dest='template_files',
        nargs='+',
        help='模板文件列表'
    )
    run_parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        default='./output',
        help='输出目录（默认为./output）'
    )
    
    # plugin 命令
    plugin_parser = subparsers.add_parser(
        'plugin',
        help='插件管理'
    )
    plugin_subparsers = plugin_parser.add_subparsers(
        dest='plugin_command',
        help='插件子命令'
    )
    
    # plugin list
    plugin_subparsers.add_parser(
        'list',
        help='列出所有插件'
    )
    
    # plugin reload
    plugin_subparsers.add_parser(
        'reload',
        help='重新加载插件'
    )
    
    # config 命令
    config_parser = subparsers.add_parser(
        'config',
        help='配置管理'
    )
    config_subparsers = config_parser.add_subparsers(
        dest='config_command',
        help='配置子命令'
    )
    
    # config show
    config_subparsers.add_parser(
        'show',
        help='显示当前配置'
    )
    
    # config set
    config_set_parser = config_subparsers.add_parser(
        'set',
        help='设置配置项'
    )
    config_set_parser.add_argument(
        'key',
        help='配置键'
    )
    config_set_parser.add_argument(
        'value',
        help='配置值'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'init':
            return cmd_init(args)
        elif args.command == 'run':
            return cmd_run(args)
        elif args.command == 'plugin':
            return cmd_plugin(args)
        elif args.command == 'config':
            return cmd_config(args)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1
    
    return 0


def cmd_init(args):
    """初始化项目"""
    api = CoreAPI()
    if not api.initialize():
        print("初始化框架失败", file=sys.stderr)
        return 1
    
    project_path = Path(args.path) / args.name
    if api.create_project(args.name, str(project_path)):
        print(f"项目 '{args.name}' 创建成功: {project_path}")
        return 0
    else:
        print(f"项目创建失败", file=sys.stderr)
        return 1


def cmd_run(args):
    """执行工作流"""
    api = CoreAPI()
    if not api.initialize():
        print("初始化框架失败", file=sys.stderr)
        return 1
    
    # 加载工作流
    if not api.load_workflow(args.workflow):
        print(f"加载工作流失败: {args.workflow}", file=sys.stderr)
        return 1
    
    # 设置输入文件
    if args.input_files:
        api.add_input_files(args.input_files)
    
    # 设置模板文件
    if args.template_files:
        api.add_template_files(args.template_files)
    
    # 设置输出目录
    api.set_output_directory(args.output_dir)
    
    # 执行工作流
    def on_progress(progress, message):
        print(f"[{progress*100:.1f}%] {message}")
    
    result = api.execute_workflow(
        Path(args.workflow).stem,
        progress_callback=on_progress
    )
    
    if result.success:
        print(f"\n✅ 执行成功!")
        print(f"   输出文件: {len(result.output_files)} 个")
        print(f"   执行时间: {result.execution_time:.2f} 秒")
        return 0
    else:
        print(f"\n❌ 执行失败!", file=sys.stderr)
        for error in result.errors:
            print(f"   错误: {error}", file=sys.stderr)
        return 1


def cmd_plugin(args):
    """插件管理"""
    api = CoreAPI()
    if not api.initialize():
        print("初始化框架失败", file=sys.stderr)
        return 1
    
    if args.plugin_command == 'list':
        plugins = api.get_plugin_list()
        if not plugins:
            print("没有加载任何插件")
            return 0
        
        print(f"已加载 {len(plugins)} 个插件:")
        for plugin in plugins:
            status = "✓" if plugin.get('enabled', True) else "✗"
            print(f"  {status} {plugin['name']} v{plugin['version']} - {plugin.get('description', '')}")
        return 0
    
    elif args.plugin_command == 'reload':
        results = api.reload_plugins()
        success_count = sum(1 for v in results.values() if v)
        print(f"重新加载完成: {success_count}/{len(results)} 成功")
        return 0
    
    else:
        print("请指定插件子命令: list 或 reload", file=sys.stderr)
        return 1


def cmd_config(args):
    """配置管理"""
    api = CoreAPI()
    if not api.initialize():
        print("初始化框架失败", file=sys.stderr)
        return 1
    
    if args.config_command == 'show':
        config = api.get_project_config()
        if not config:
            print("没有打开的项目")
            return 0
        
        import json
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return 0
    
    elif args.config_command == 'set':
        # 这里简化处理，实际应该修改配置文件
        print(f"设置配置: {args.key} = {args.value}")
        print("注意: 此功能需要在项目上下文中使用")
        return 0
    
    else:
        print("请指定配置子命令: show 或 set", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())