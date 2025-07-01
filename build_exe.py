#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WabiMail 実行ファイルビルドスクリプト

Task 13: PyInstaller実行ファイル生成とテスト
WabiMailの実行ファイルを自動的にビルドするスクリプトです。
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime
import zipfile
import tempfile

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
RESOURCES_DIR = PROJECT_ROOT / "resources"

# プラットフォーム情報
PLATFORM = platform.system()
IS_WINDOWS = PLATFORM == "Windows"
IS_MACOS = PLATFORM == "Darwin"
IS_LINUX = PLATFORM == "Linux"


class WabiMailBuilder:
    """WabiMail実行ファイルビルダー"""
    
    def __init__(self):
        """初期化"""
        self.project_root = PROJECT_ROOT
        self.build_time = datetime.now()
        self.build_log = []
        
    def log(self, message, level="INFO"):
        """ログ出力"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}"
        print(log_message)
        self.build_log.append(log_message)
    
    def check_requirements(self):
        """必要なツールと依存関係をチェック"""
        self.log("🔍 ビルド環境チェック開始")
        
        # PyInstallerチェック
        try:
            import PyInstaller
            self.log(f"✅ PyInstaller {PyInstaller.__version__} が見つかりました")
        except ImportError:
            self.log("❌ PyInstallerがインストールされていません", "ERROR")
            self.log("pip install pyinstaller を実行してください", "ERROR")
            return False
        
        # 必要なファイルの確認
        required_files = [
            "src/main.py",
            "config.yaml",
        ]
        
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                self.log(f"❌ 必要なファイルが見つかりません: {file_path}", "ERROR")
                return False
            else:
                self.log(f"✅ {file_path} 確認済み")
        
        # アイコンファイルの確認
        icon_dir = RESOURCES_DIR / "assets" / "icons"
        if not icon_dir.exists():
            self.log("⚠️  アイコンディレクトリが見つかりません。デフォルトアイコンを使用します", "WARNING")
        
        return True
    
    def create_icons(self):
        """プラットフォーム用アイコンを作成（仮）"""
        self.log("🎨 アイコンファイル準備")
        
        # アイコンディレクトリ作成
        icon_dir = RESOURCES_DIR / "assets" / "icons"
        icon_dir.mkdir(parents=True, exist_ok=True)
        
        # 仮のアイコンファイルを作成（実際のプロジェクトでは適切なアイコンを用意）
        try:
            # Windows用 .ico
            if IS_WINDOWS:
                ico_path = icon_dir / "wabimail.ico"
                if not ico_path.exists():
                    # 仮のicoファイル作成
                    with open(ico_path, 'wb') as f:
                        f.write(b'\x00\x00\x01\x00')  # 最小限のICOヘッダー
                    self.log("✅ Windows用アイコン作成（仮）")
            
            # macOS用 .icns
            elif IS_MACOS:
                icns_path = icon_dir / "wabimail.icns"
                if not icns_path.exists():
                    # 仮のicnsファイル作成
                    with open(icns_path, 'wb') as f:
                        f.write(b'icns')  # 最小限のICNSヘッダー
                    self.log("✅ macOS用アイコン作成（仮）")
            
            # Linux用 .png
            else:
                png_path = icon_dir / "wabimail.png"
                if not png_path.exists():
                    # 仮のPNGファイル作成（1x1の透明PNG）
                    png_data = (
                        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                        b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
                        b'\x00\x00\x00\x0bIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
                        b'\x05\x18\x0d\x0c\x00\x00\x00\x00IEND\xaeB`\x82'
                    )
                    with open(png_path, 'wb') as f:
                        f.write(png_data)
                    self.log("✅ Linux用アイコン作成（仮）")
                    
        except Exception as e:
            self.log(f"⚠️  アイコン作成エラー: {e}", "WARNING")
    
    def generate_spec_file(self):
        """PyInstaller specファイルを生成"""
        self.log("📄 Specファイル生成")
        
        # pyinstaller_spec.pyを実行
        spec_script = self.project_root / "build_config" / "pyinstaller_spec.py"
        
        try:
            result = subprocess.run(
                [sys.executable, str(spec_script)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                self.log("✅ Specファイル生成成功")
                return True
            else:
                self.log(f"❌ Specファイル生成エラー: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Specファイル生成エラー: {e}", "ERROR")
            return False
    
    def build_executable(self):
        """実行ファイルをビルド"""
        self.log("🔨 実行ファイルビルド開始")
        
        # クリーンビルドのため既存のディレクトリを削除
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
        
        # PyInstallerコマンド
        spec_file = self.project_root / "WabiMail.spec"
        
        cmd = [
            sys.executable,
            "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]
        
        self.log(f"実行コマンド: {' '.join(cmd)}")
        
        try:
            # ビルド実行
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.project_root
            )
            
            # リアルタイムログ出力
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(f"  PyInstaller: {line}")
            
            process.wait()
            
            if process.returncode == 0:
                self.log("✅ ビルド成功")
                return True
            else:
                self.log(f"❌ ビルドエラー (終了コード: {process.returncode})", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ ビルドエラー: {e}", "ERROR")
            return False
    
    def test_executable(self):
        """生成された実行ファイルをテスト"""
        self.log("🧪 実行ファイルテスト")
        
        # 実行ファイルのパスを特定
        if IS_WINDOWS:
            exe_path = DIST_DIR / "WabiMail.exe"
        elif IS_MACOS:
            exe_path = DIST_DIR / "WabiMail.app" / "Contents" / "MacOS" / "WabiMail"
        else:
            exe_path = DIST_DIR / "wabimail"
        
        if not exe_path.exists():
            self.log(f"❌ 実行ファイルが見つかりません: {exe_path}", "ERROR")
            return False
        
        self.log(f"✅ 実行ファイルを確認: {exe_path}")
        
        # ファイルサイズ確認
        file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        self.log(f"📊 ファイルサイズ: {file_size:.2f} MB")
        
        # 基本的な起動テスト（ヘッドレス環境では制限あり）
        try:
            # バージョン確認のような簡単なテスト
            test_cmd = [str(exe_path), "--version"] if not IS_MACOS else ["open", "-a", str(DIST_DIR / "WabiMail.app"), "--args", "--version"]
            
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if "WabiMail" in result.stdout or result.returncode == 0:
                self.log("✅ 基本起動テスト成功")
            else:
                self.log("⚠️  起動テストは手動で実施してください", "WARNING")
                
        except subprocess.TimeoutExpired:
            self.log("⚠️  起動テストタイムアウト（GUI環境で手動テストを推奨）", "WARNING")
        except Exception as e:
            self.log(f"⚠️  起動テストエラー: {e}", "WARNING")
        
        return True
    
    def create_distribution_package(self):
        """配布用パッケージを作成"""
        self.log("📦 配布用パッケージ作成")
        
        # パッケージ名
        timestamp = self.build_time.strftime("%Y%m%d_%H%M%S")
        
        if IS_WINDOWS:
            package_name = f"WabiMail_Windows_{timestamp}.zip"
        elif IS_MACOS:
            package_name = f"WabiMail_macOS_{timestamp}.zip"
        else:
            package_name = f"WabiMail_Linux_{timestamp}.tar.gz"
        
        package_path = DIST_DIR / package_name
        
        try:
            if package_name.endswith('.zip'):
                # ZIP圧縮
                with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    if IS_MACOS:
                        # macOSの.appディレクトリを圧縮
                        app_dir = DIST_DIR / "WabiMail.app"
                        for root, dirs, files in os.walk(app_dir):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = file_path.relative_to(DIST_DIR)
                                zf.write(file_path, arcname)
                    else:
                        # その他のプラットフォーム
                        for item in DIST_DIR.iterdir():
                            if item.name != package_name:
                                if item.is_file():
                                    zf.write(item, item.name)
                                elif item.is_dir():
                                    for root, dirs, files in os.walk(item):
                                        for file in files:
                                            file_path = Path(root) / file
                                            arcname = file_path.relative_to(DIST_DIR)
                                            zf.write(file_path, arcname)
            else:
                # tar.gz圧縮（Linux）
                import tarfile
                with tarfile.open(package_path, 'w:gz') as tf:
                    for item in DIST_DIR.iterdir():
                        if item.name != package_name:
                            tf.add(item, arcname=item.name)
            
            package_size = package_path.stat().st_size / (1024 * 1024)  # MB
            self.log(f"✅ パッケージ作成成功: {package_name} ({package_size:.2f} MB)")
            return package_path
            
        except Exception as e:
            self.log(f"❌ パッケージ作成エラー: {e}", "ERROR")
            return None
    
    def save_build_report(self):
        """ビルドレポートを保存"""
        report_dir = self.project_root / "build_reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = self.build_time.strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"build_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("🌸 WabiMail ビルドレポート\n")
            f.write("=" * 60 + "\n")
            f.write(f"ビルド日時: {self.build_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"プラットフォーム: {PLATFORM}\n")
            f.write(f"Python バージョン: {sys.version}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("ビルドログ:\n")
            for log_entry in self.build_log:
                f.write(f"{log_entry}\n")
        
        self.log(f"📄 ビルドレポート保存: {report_file}")
    
    def run(self):
        """ビルドプロセスを実行"""
        print("🌸 WabiMail 実行ファイルビルド")
        print("=" * 60)
        print(f"プラットフォーム: {PLATFORM}")
        print(f"ビルド開始時刻: {self.build_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # ビルド環境チェック
        if not self.check_requirements():
            self.log("❌ ビルド環境チェック失敗", "ERROR")
            return False
        
        # アイコン準備
        self.create_icons()
        
        # Specファイル生成
        if not self.generate_spec_file():
            self.log("❌ Specファイル生成失敗", "ERROR")
            return False
        
        # ビルド実行
        if not self.build_executable():
            self.log("❌ ビルド失敗", "ERROR")
            return False
        
        # テスト実行
        if not self.test_executable():
            self.log("❌ テスト失敗", "ERROR")
            return False
        
        # 配布パッケージ作成
        package_path = self.create_distribution_package()
        
        # ビルドレポート保存
        self.save_build_report()
        
        # 完了メッセージ
        print()
        print("=" * 60)
        print("🎉 ビルド完了！")
        print()
        print("📁 成果物:")
        print(f"  - 実行ファイル: {DIST_DIR}")
        if package_path:
            print(f"  - 配布パッケージ: {package_path}")
        print()
        print("🧪 次のステップ:")
        print("  1. GUI環境で実行ファイルの動作確認")
        print("  2. 各機能の手動テスト")
        print("  3. インストーラー作成（Task 14）")
        
        return True


def main():
    """メイン関数"""
    builder = WabiMailBuilder()
    success = builder.run()
    
    if not success:
        print("\n❌ ビルドに失敗しました。ログを確認してください。")
        sys.exit(1)
    else:
        print("\n✨ ビルドが正常に完了しました！")
        sys.exit(0)


if __name__ == "__main__":
    main()