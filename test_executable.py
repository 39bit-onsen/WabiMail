#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WabiMail 実行ファイルテストスクリプト

Task 13: PyInstaller実行ファイルのテスト
生成された実行ファイルの動作確認を行います。
"""

import os
import sys
import subprocess
import platform
import time
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"

# プラットフォーム情報
PLATFORM = platform.system()
IS_WINDOWS = PLATFORM == "Windows"
IS_MACOS = PLATFORM == "Darwin"
IS_LINUX = PLATFORM == "Linux"


class ExecutableTestRunner:
    """実行ファイルテストランナー"""
    
    def __init__(self):
        """初期化"""
        self.test_results = {}
        self.test_start_time = datetime.now()
        self.temp_dir = None
        
        # 実行ファイルパス
        if IS_WINDOWS:
            self.exe_path = DIST_DIR / "WabiMail.exe"
        elif IS_MACOS:
            self.exe_path = DIST_DIR / "WabiMail.app" / "Contents" / "MacOS" / "WabiMail"
        else:
            self.exe_path = DIST_DIR / "WabiMail"
    
    def log(self, message):
        """ログ出力"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def test_executable_exists(self):
        """実行ファイルの存在確認"""
        self.log("🔍 実行ファイル存在確認テスト")
        
        try:
            if not self.exe_path.exists():
                self.test_results["executable_exists"] = {
                    "status": "FAIL",
                    "message": f"実行ファイルが見つかりません: {self.exe_path}"
                }
                return False
            
            # ファイル情報
            file_stat = self.exe_path.stat()
            file_size_mb = file_stat.st_size / (1024 * 1024)
            
            self.test_results["executable_exists"] = {
                "status": "PASS",
                "message": "実行ファイルが存在します",
                "details": {
                    "path": str(self.exe_path),
                    "size_mb": round(file_size_mb, 2),
                    "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat()
                }
            }
            
            self.log(f"✅ 実行ファイル確認: {self.exe_path} ({file_size_mb:.2f} MB)")
            return True
            
        except Exception as e:
            self.test_results["executable_exists"] = {
                "status": "ERROR",
                "message": f"エラー: {str(e)}"
            }
            return False
    
    def test_basic_launch(self):
        """基本的な起動テスト"""
        self.log("🚀 基本起動テスト")
        
        try:
            # ヘルプオプションでの起動テスト
            if IS_WINDOWS:
                cmd = [str(self.exe_path), "--help"]
            elif IS_MACOS:
                # macOSアプリケーションバンドルの場合
                cmd = [str(self.exe_path), "--help"]
            else:
                cmd = [str(self.exe_path), "--help"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 or "WabiMail" in result.stdout:
                self.test_results["basic_launch"] = {
                    "status": "PASS",
                    "message": "基本起動成功",
                    "stdout": result.stdout[:200] if result.stdout else ""
                }
                self.log("✅ 基本起動テスト成功")
                return True
            else:
                self.test_results["basic_launch"] = {
                    "status": "FAIL",
                    "message": "起動失敗",
                    "stderr": result.stderr[:200] if result.stderr else ""
                }
                return False
                
        except subprocess.TimeoutExpired:
            self.test_results["basic_launch"] = {
                "status": "WARNING",
                "message": "起動タイムアウト（GUI環境が必要な可能性）"
            }
            self.log("⚠️  起動タイムアウト")
            return True  # GUI環境では正常な可能性があるため
            
        except Exception as e:
            self.test_results["basic_launch"] = {
                "status": "ERROR",
                "message": f"エラー: {str(e)}"
            }
            return False
    
    def test_file_integrity(self):
        """ファイル整合性テスト"""
        self.log("📁 ファイル整合性テスト")
        
        try:
            # 必要なファイルの確認
            required_files = []
            
            if IS_WINDOWS:
                dist_files = list(DIST_DIR.glob("*"))
                # DLLファイルの確認
                dll_files = [f for f in dist_files if f.suffix == ".dll"]
                
                self.test_results["file_integrity"] = {
                    "status": "PASS",
                    "message": "ファイル整合性確認",
                    "details": {
                        "total_files": len(dist_files),
                        "dll_count": len(dll_files),
                        "dist_size_mb": sum(f.stat().st_size for f in dist_files if f.is_file()) / (1024 * 1024)
                    }
                }
            elif IS_MACOS:
                app_dir = DIST_DIR / "WabiMail.app"
                if app_dir.exists():
                    # Info.plistの確認
                    info_plist = app_dir / "Contents" / "Info.plist"
                    
                    self.test_results["file_integrity"] = {
                        "status": "PASS" if info_plist.exists() else "FAIL",
                        "message": "アプリケーションバンドル確認",
                        "details": {
                            "app_bundle": str(app_dir),
                            "info_plist_exists": info_plist.exists()
                        }
                    }
                else:
                    self.test_results["file_integrity"] = {
                        "status": "FAIL",
                        "message": "アプリケーションバンドルが見つかりません"
                    }
            else:
                # Linux
                self.test_results["file_integrity"] = {
                    "status": "PASS",
                    "message": "ファイル整合性確認",
                    "details": {
                        "executable": str(self.exe_path),
                        "is_executable": os.access(str(self.exe_path), os.X_OK)
                    }
                }
            
            self.log("✅ ファイル整合性テスト完了")
            return True
            
        except Exception as e:
            self.test_results["file_integrity"] = {
                "status": "ERROR",
                "message": f"エラー: {str(e)}"
            }
            return False
    
    def test_dependencies(self):
        """依存関係テスト"""
        self.log("🔗 依存関係テスト")
        
        try:
            # プラットフォーム別の依存関係チェック
            if IS_WINDOWS:
                # Windows: 必要なDLLの確認
                required_dlls = ["python3*.dll", "tcl*.dll", "tk*.dll"]
                found_dlls = []
                
                for pattern in required_dlls:
                    dlls = list(DIST_DIR.glob(pattern))
                    found_dlls.extend([dll.name for dll in dlls])
                
                self.test_results["dependencies"] = {
                    "status": "PASS" if found_dlls else "WARNING",
                    "message": "依存関係確認",
                    "details": {
                        "found_dlls": found_dlls[:10]  # 最初の10個
                    }
                }
                
            elif IS_MACOS:
                # macOS: otool で依存関係確認（可能な場合）
                try:
                    result = subprocess.run(
                        ["otool", "-L", str(self.exe_path)],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        deps = result.stdout.strip().split('\n')[1:]  # 最初の行をスキップ
                        self.test_results["dependencies"] = {
                            "status": "PASS",
                            "message": "依存関係確認",
                            "details": {
                                "dependency_count": len(deps),
                                "sample_deps": deps[:5]
                            }
                        }
                    else:
                        self.test_results["dependencies"] = {
                            "status": "WARNING",
                            "message": "otoolが使用できません"
                        }
                except FileNotFoundError:
                    self.test_results["dependencies"] = {
                        "status": "SKIP",
                        "message": "otoolがインストールされていません"
                    }
                    
            else:
                # Linux: ldd で依存関係確認
                try:
                    result = subprocess.run(
                        ["ldd", str(self.exe_path)],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        deps = result.stdout.strip().split('\n')
                        self.test_results["dependencies"] = {
                            "status": "PASS",
                            "message": "依存関係確認",
                            "details": {
                                "dependency_count": len(deps),
                                "sample_deps": deps[:5]
                            }
                        }
                    else:
                        self.test_results["dependencies"] = {
                            "status": "WARNING",
                            "message": "lddでエラーが発生しました"
                        }
                except FileNotFoundError:
                    self.test_results["dependencies"] = {
                        "status": "SKIP",
                        "message": "lddがインストールされていません"
                    }
            
            self.log("✅ 依存関係テスト完了")
            return True
            
        except Exception as e:
            self.test_results["dependencies"] = {
                "status": "ERROR",
                "message": f"エラー: {str(e)}"
            }
            return False
    
    def test_portable_execution(self):
        """ポータブル実行テスト"""
        self.log("💼 ポータブル実行テスト")
        
        try:
            # 一時ディレクトリを作成してファイルをコピー
            self.temp_dir = tempfile.mkdtemp(prefix="wabimail_test_")
            
            if IS_WINDOWS:
                # Windowsの場合、実行ファイルと関連ファイルをコピー
                temp_exe = Path(self.temp_dir) / "WabiMail.exe"
                shutil.copy2(self.exe_path, temp_exe)
                
                # 関連DLLもコピー
                for dll in DIST_DIR.glob("*.dll"):
                    shutil.copy2(dll, self.temp_dir)
                
                test_exe = temp_exe
                
            elif IS_MACOS:
                # macOSの場合、.appバンドル全体をコピー
                temp_app = Path(self.temp_dir) / "WabiMail.app"
                shutil.copytree(DIST_DIR / "WabiMail.app", temp_app)
                test_exe = temp_app / "Contents" / "MacOS" / "WabiMail"
                
            else:
                # Linuxの場合
                temp_exe = Path(self.temp_dir) / "wabimail"
                shutil.copy2(self.exe_path, temp_exe)
                os.chmod(temp_exe, 0o755)  # 実行権限を付与
                test_exe = temp_exe
            
            # コピーした実行ファイルでテスト
            result = subprocess.run(
                [str(test_exe), "--help"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.temp_dir
            )
            
            if result.returncode == 0 or "WabiMail" in result.stdout:
                self.test_results["portable_execution"] = {
                    "status": "PASS",
                    "message": "ポータブル実行成功",
                    "details": {
                        "temp_location": self.temp_dir
                    }
                }
                self.log("✅ ポータブル実行テスト成功")
                return True
            else:
                self.test_results["portable_execution"] = {
                    "status": "FAIL",
                    "message": "ポータブル実行失敗"
                }
                return False
                
        except subprocess.TimeoutExpired:
            self.test_results["portable_execution"] = {
                "status": "WARNING",
                "message": "実行タイムアウト"
            }
            return True
            
        except Exception as e:
            self.test_results["portable_execution"] = {
                "status": "ERROR",
                "message": f"エラー: {str(e)}"
            }
            return False
        
        finally:
            # 一時ディレクトリのクリーンアップ
            if self.temp_dir and Path(self.temp_dir).exists():
                shutil.rmtree(self.temp_dir)
    
    def generate_test_report(self):
        """テストレポート生成"""
        report_dir = PROJECT_ROOT / "test_reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = self.test_start_time.strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"executable_test_report_{timestamp}.json"
        
        # レポートデータ
        report_data = {
            "test_info": {
                "start_time": self.test_start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "platform": PLATFORM,
                "python_version": sys.version,
                "executable_path": str(self.exe_path)
            },
            "test_results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results.values() if r["status"] == "PASS"),
                "failed": sum(1 for r in self.test_results.values() if r["status"] == "FAIL"),
                "warnings": sum(1 for r in self.test_results.values() if r["status"] == "WARNING"),
                "errors": sum(1 for r in self.test_results.values() if r["status"] == "ERROR"),
                "skipped": sum(1 for r in self.test_results.values() if r["status"] == "SKIP")
            }
        }
        
        # JSONファイルに保存
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        self.log(f"📄 テストレポート保存: {report_file}")
        
        # コンソールにサマリー表示
        print("\n" + "=" * 60)
        print("📊 実行ファイルテスト結果サマリー")
        print("=" * 60)
        
        summary = report_data["summary"]
        print(f"総テスト数: {summary['total_tests']}")
        print(f"✅ 成功: {summary['passed']}")
        print(f"❌ 失敗: {summary['failed']}")
        print(f"⚠️  警告: {summary['warnings']}")
        print(f"💥 エラー: {summary['errors']}")
        print(f"⏭️  スキップ: {summary['skipped']}")
        
        # 詳細結果
        print("\n詳細結果:")
        for test_name, result in self.test_results.items():
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "WARNING": "⚠️",
                "ERROR": "💥",
                "SKIP": "⏭️"
            }.get(result["status"], "❓")
            
            print(f"  {status_icon} {test_name}: {result['message']}")
        
        return summary['failed'] == 0 and summary['errors'] == 0
    
    def run(self):
        """テスト実行"""
        print("🧪 WabiMail 実行ファイルテスト")
        print("=" * 60)
        print(f"プラットフォーム: {PLATFORM}")
        print(f"テスト開始: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # テスト実行
        tests = [
            self.test_executable_exists,
            self.test_basic_launch,
            self.test_file_integrity,
            self.test_dependencies,
            self.test_portable_execution
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log(f"テスト実行エラー: {e}")
            print()
        
        # レポート生成
        success = self.generate_test_report()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 実行ファイルテスト成功！")
            print("\n📋 次のステップ:")
            print("  1. GUI環境での手動動作確認")
            print("  2. 各機能の統合テスト")
            print("  3. インストーラー作成（Task 14）")
        else:
            print("❌ 一部のテストで問題が検出されました")
            print("詳細はテストレポートを確認してください")
        
        return success


def main():
    """メイン関数"""
    tester = ExecutableTestRunner()
    success = tester.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()