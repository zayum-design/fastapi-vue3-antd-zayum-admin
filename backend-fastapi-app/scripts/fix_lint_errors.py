#!/usr/bin/env python3
"""
批量修复后端 Python 文件的 lint 和类型检查错误

此脚本可以修复：
1. Ruff 检查错误（自动修复）
2. 格式化代码
3. 可选：修复 mypy 类型错误

使用方法：
    cd backend-fastapi-app
    python scripts/fix_lint_errors.py

选项：
    --dry-run: 只显示将要修改的内容，不实际修改
    --fix-mypy: 尝试修复 mypy 类型错误（添加类型注解）
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """运行命令并返回是否成功"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    print(f"命令: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode != 0:
            print(f"⚠️  命令返回非零退出码: {result.returncode}")
            return False
        return True
    except FileNotFoundError as e:
        print(f"❌ 命令未找到: {e}")
        print("请确保 ruff 和 mypy 已安装: pip install ruff mypy")
        return False
    except Exception as e:
        print(f"❌ 运行命令时出错: {e}")
        return False


def check_ruff_installation() -> bool:
    """检查 ruff 是否已安装"""
    try:
        subprocess.run(["python3", "-m", "ruff", "--version"], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    parser = argparse.ArgumentParser(
        description="批量修复 Python 文件的 lint 和类型检查错误"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="只显示将要修改的内容，不实际修改"
    )
    parser.add_argument(
        "--fix-mypy",
        action="store_true", 
        help="显示 mypy 错误（需要手动修复）"
    )
    parser.add_argument(
        "--path",
        default="app",
        help="要检查和修复的路径 (默认: app)"
    )
    
    args = parser.parse_args()
    
    # 检查是否在正确的目录
    if not Path("pyproject.toml").exists():
        print("❌ 错误: 未找到 pyproject.toml")
        print("请确保在 backend-fastapi-app 目录下运行此脚本")
        sys.exit(1)
    
    # 检查 ruff 是否安装
    if not check_ruff_installation():
        print("❌ 错误: ruff 未安装")
        print("请运行: pip install ruff mypy")
        sys.exit(1)
    
    print("🚀 开始批量修复 lint 错误...")
    print(f"目标路径: {args.path}")
    print(f"模式: {'预览' if args.dry_run else '修复'}")
    
    success = True
    
    # 1. 检查 Ruff 错误
    if not run_command(
        ["python3", "-m", "ruff", "check", args.path],
        "步骤 1/4: 检查 Ruff 错误"
    ):
        success = False
    
    # 2. 自动修复 Ruff 错误
    fix_flag = "--diff" if args.dry_run else "--fix"
    if not run_command(
        ["python3", "-m", "ruff", "check", fix_flag, args.path],
        f"步骤 2/4: {'预览' if args.dry_run else '修复'} Ruff 错误"
    ):
        success = False
    
    # 3. 格式化代码
    check_flag = "--check" if args.dry_run else ""
    format_cmd = ["python3", "-m", "ruff", "format"]
    if check_flag:
        format_cmd.append(check_flag)
    format_cmd.append(args.path)
    
    if not run_command(
        format_cmd,
        f"步骤 3/4: {'检查' if args.dry_run else '格式化'}代码"
    ):
        success = False
    
    # 4. 检查 MyPy 错误（可选）
    if args.fix_mypy:
        if not run_command(
            ["python3", "-m", "mypy", args.path, "--ignore-missing-imports"],
            "步骤 4/4: MyPy 类型检查（需要手动修复）"
        ):
            success = False
    
    print(f"\n{'='*60}")
    if success:
        print("✅ 处理完成!")
        if args.dry_run:
            print("\n提示: 这是预览模式，使用 --fix 参数实际修复")
    else:
        print("⚠️  处理完成，但有一些问题需要手动修复")
    print(f"{'='*60}")
    
    # 提供后续建议
    print("\n📋 后续建议:")
    print("1. 在 VS Code 中安装 Ruff 插件以获得实时提示")
    print("2. 保存文件时自动格式化: 在 VS Code 设置中添加:")
    print('   "editor.formatOnSave": true')
    print('   "editor.defaultFormatter": "charliermarsh.ruff"')
    print("3. 对于 mypy 错误，建议逐步添加类型注解")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
