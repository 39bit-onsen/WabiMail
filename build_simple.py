#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WabiMail シンプルビルドスクリプト

PyInstallerを使用してWabiMailの実行ファイルを生成します。
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent

def main():
    """メイン関数"""
    print("🌸 WabiMail ビルド開始")
    print("=" * 60)
    
    # クリーンビルドのため既存のディレクトリを削除
    build_dir = PROJECT_ROOT / "build"
    dist_dir = PROJECT_ROOT / "dist"
    
    if build_dir.exists():
        print("🧹 既存のbuildディレクトリを削除")
        shutil.rmtree(build_dir)
    
    if dist_dir.exists():
        print("🧹 既存のdistディレクトリを削除")
        shutil.rmtree(dist_dir)
    
    # アイコンディレクトリ作成（必要に応じて）
    icon_dir = PROJECT_ROOT / "resources" / "assets" / "icons"
    icon_dir.mkdir(parents=True, exist_ok=True)
    
    # 仮のアイコンファイル作成
    png_path = icon_dir / "wabimail.png"
    if not png_path.exists():
        # 1x1の透明PNGを作成
        png_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\x0bIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
            b'\x05\x18\x0d\x0c\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        with open(png_path, 'wb') as f:
            f.write(png_data)
        print("✅ 仮のアイコンファイルを作成")
    
    # PyInstallerコマンド（シンプル版）
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name", "WabiMail",
        "--onefile",  # 単一実行ファイル
        "--windowed",  # コンソールなし（GUI）
        "--icon", str(png_path),
        "--add-data", f"{PROJECT_ROOT / 'config.yaml'}{os.pathsep}.",
        "--hidden-import", "tkinter",
        "--hidden-import", "PIL",
        "--hidden-import", "yaml",
        "--hidden-import", "cryptography",
        "--clean",
        "--noconfirm",
        str(PROJECT_ROOT / "src" / "main.py")
    ]
    
    print("\n🔨 PyInstallerを実行中...")
    print(f"コマンド: {' '.join(cmd)}")
    
    try:
        # ビルド実行
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        
        if result.returncode == 0:
            print("\n✅ ビルド成功！")
            print(f"実行ファイルは dist/ ディレクトリに生成されました")
            
            # ビルド結果の確認
            if sys.platform == "win32":
                exe_path = dist_dir / "WabiMail.exe"
            else:
                exe_path = dist_dir / "WabiMail"
            
            if exe_path.exists():
                file_size = exe_path.stat().st_size / (1024 * 1024)
                print(f"📊 ファイルサイズ: {file_size:.2f} MB")
                print(f"📍 パス: {exe_path}")
            
            return True
        else:
            print("\n❌ ビルドエラーが発生しました")
            return False
            
    except FileNotFoundError:
        print("\n❌ PyInstallerがインストールされていません")
        print("以下のコマンドでインストールしてください:")
        print("pip install pyinstaller")
        return False
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)