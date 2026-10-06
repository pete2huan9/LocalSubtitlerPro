#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Subtitler Pro (v0.2.0) - One-Click PyInstaller Build & Release Automation
Packages the PyQt6 application into an independent Windows green distribution
and generates a portable zip release archive.
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path

VERSION = "0.2.0"
PROJECT_DIR = Path(__file__).resolve().parent
DIST_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"
SPEC_FILE = PROJECT_DIR / "LocalSubtitlerPro.spec"
OUTPUT_FOLDER = DIST_DIR / "LocalSubtitlerPro"
ZIP_OUTPUT = DIST_DIR / f"LocalSubtitlerPro-v{VERSION}-Windows-x64.zip"


def clean_previous_builds():
    print("------------------------------------------------------------")
    print("🧹 [1/4] 清理旧构建目录...")
    for p in [BUILD_DIR, OUTPUT_FOLDER]:
        if p.exists():
            print(f" -> 移除: {p}")
            shutil.rmtree(p, ignore_errors=True)
    if ZIP_OUTPUT.exists():
        ZIP_OUTPUT.unlink()


def run_pyinstaller():
    print("------------------------------------------------------------")
    print(f"🔨 [2/4] 调用 PyInstaller 构建 Local Subtitler Pro v{VERSION}...")
    pyinstaller_exe = PROJECT_DIR / "venv" / "Scripts" / "pyinstaller.exe"
    if not pyinstaller_exe.exists():
        pyinstaller_exe = shutil.which("pyinstaller")
        if not pyinstaller_exe:
            raise FileNotFoundError("未在虚拟环境或系统 PATH 中找到 pyinstaller.exe")

    cmd = [
        str(pyinstaller_exe),
        "--clean",
        "--noconfirm",
        str(SPEC_FILE)
    ]
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=str(PROJECT_DIR))


def copy_accessories():
    print("------------------------------------------------------------")
    print("📦 [3/4] 复制周边说明文档与配置文件...")
    files_to_copy = ["README.md", "README_EN.md", "LICENSE", "config.json"]
    for f_name in files_to_copy:
        src = PROJECT_DIR / f_name
        if src.exists():
            dest = OUTPUT_FOLDER / f_name
            shutil.copy2(src, dest)
            print(f" -> 复制: {f_name} -> {OUTPUT_FOLDER.name}/")


def create_release_zip():
    print("------------------------------------------------------------")
    print(f"🗜️ [4/4] 打包生成便携绿色发布压缩包: {ZIP_OUTPUT.name}...")
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(OUTPUT_FOLDER):
            for file in files:
                abs_path = Path(root) / file
                rel_path = abs_path.relative_to(DIST_DIR)
                zf.write(abs_path, rel_path)

    zip_size_mb = ZIP_OUTPUT.stat().st_size / (1024 * 1024)
    exe_path = OUTPUT_FOLDER / "LocalSubtitlerPro.exe"
    exe_size_mb = exe_path.stat().st_size / (1024 * 1024) if exe_path.exists() else 0

    print("============================================================")
    print("🎉 构建与打包全部完成！")
    print(f" • 独立可执行程序: {exe_path} ({exe_size_mb:.2f} MB)")
    print(f" • 便携绿色发布包: {ZIP_OUTPUT} ({zip_size_mb:.2f} MB)")
    print("============================================================")


def main():
    try:
        clean_previous_builds()
        run_pyinstaller()
        copy_accessories()
        create_release_zip()
    except Exception as e:
        print(f"\n❌ [构建失败] 发生异常: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
