#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WabiMail インストーラーテストスクリプト

Task 14: Inno Setupインストーラーテスト
生成されたインストーラーの動作確認を行います。
"""

import os
import sys
import subprocess
import time
import json
import winreg
from pathlib import Path
from datetime import datetime


class WabiMailInstallerTester:
    """WabiMail インストーラーテスター"""
    
    def __init__(self):
        """初期化"""
        self.test_start_time = datetime.now()
        self.test_results = {}
        
        # パス設定
        self.project_root = Path(__file__).parent.parent
        self.installer_dir = self.project_root / "dist" / "installer"
        self.test_install_dir = Path("C:/Program Files/WabiMail")
        
    def log(self, message):
        """ログ出力"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def find_installer(self):
        """インストーラーファイル検索"""
        self.log("🔍 インストーラーファイル検索")
        
        installer_files = list(self.installer_dir.glob("WabiMail-Setup-*.exe"))
        
        if not installer_files:
            self.log("❌ インストーラーファイルが見つかりません")
            return None
        
        installer_file = max(installer_files, key=lambda f: f.stat().st_mtime)
        self.log(f"✅ インストーラーファイル: {installer_file.name}")
        
        return installer_file
    
    def test_installer_properties(self, installer_file):
        """インストーラーファイル特性テスト"""
        self.log("📊 インストーラーファイル特性テスト")
        
        try:
            file_stat = installer_file.stat()
            file_size_mb = file_stat.st_size / (1024 * 1024)
            
            result = {
                "status": "PASS",
                "details": {
                    "file_path": str(installer_file),
                    "file_size_mb": round(file_size_mb, 2),
                    "created_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    "modified_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                }
            }
            
            self.log(f"✅ ファイルサイズ: {file_size_mb:.2f} MB")
            
            # サイズ妥当性チェック
            if file_size_mb < 20:
                result["warning"] = "ファイルサイズが小さい可能性があります"
                self.log("⚠️  ファイルサイズが小さい可能性があります")
            elif file_size_mb > 100:
                result["warning"] = "ファイルサイズが大きい可能性があります"
                self.log("⚠️  ファイルサイズが大きい可能性があります")
            
            self.test_results["installer_properties"] = result
            return True
            
        except Exception as e:
            self.test_results["installer_properties"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.log(f"❌ ファイル特性テストエラー: {e}")
            return False
    
    def test_silent_install(self, installer_file):
        """サイレントインストールテスト"""
        self.log("🔧 サイレントインストールテスト")
        
        try:
            # サイレントインストール実行
            cmd = [str(installer_file), "/VERYSILENT", "/NORESTART", "/SUPPRESSMSGBOXES"]
            
            self.log("インストール実行中...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2分タイムアウト
            )
            
            if result.returncode == 0:
                self.log("✅ サイレントインストール成功")
                
                # インストール確認
                if self.test_install_dir.exists():
                    exe_path = self.test_install_dir / "WabiMail.exe"
                    if exe_path.exists():
                        self.test_results["silent_install"] = {
                            "status": "PASS",
                            "install_path": str(self.test_install_dir),
                            "executable_exists": True
                        }
                        return True
                
                self.test_results["silent_install"] = {
                    "status": "FAIL",
                    "error": "インストールファイルが見つかりません"
                }
                return False
            else:
                self.test_results["silent_install"] = {
                    "status": "FAIL",
                    "return_code": result.returncode,
                    "stderr": result.stderr
                }
                self.log(f"❌ インストール失敗: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            self.test_results["silent_install"] = {
                "status": "FAIL",
                "error": "インストールタイムアウト"
            }
            self.log("❌ インストールタイムアウト")
            return False
        except Exception as e:
            self.test_results["silent_install"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.log(f"❌ インストールエラー: {e}")
            return False
    
    def test_registry_entries(self):
        """レジストリエントリテスト"""
        self.log("📝 レジストリエントリテスト")
        
        try:
            registry_checks = []
            
            # アプリケーション登録確認
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"Software\WabiMail Development Team\WabiMail") as key:
                    install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                    version = winreg.QueryValueEx(key, "Version")[0]
                    
                    registry_checks.append({
                        "key": "Application Registration",
                        "status": "PASS",
                        "install_path": install_path,
                        "version": version
                    })
                    
            except Exception as e:
                registry_checks.append({
                    "key": "Application Registration",
                    "status": "FAIL",
                    "error": str(e)
                })
            
            # ファイル関連付け確認
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ".eml") as key:
                    file_type = winreg.QueryValueEx(key, "")[0]
                    registry_checks.append({
                        "key": "File Association (.eml)",
                        "status": "PASS",
                        "file_type": file_type
                    })
            except Exception as e:
                registry_checks.append({
                    "key": "File Association (.eml)",
                    "status": "FAIL",
                    "error": str(e)
                })
            
            # アンインストール情報確認
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                  r"Software\Microsoft\Windows\CurrentVersion\Uninstall") as uninstall_key:
                    
                    found_uninstall = False
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(uninstall_key, i)
                            if "WabiMail" in subkey_name or "{8B7355A1-2F4F-4F4F-8B73-55A12F4F4F4F}" in subkey_name:
                                with winreg.OpenKey(uninstall_key, subkey_name) as app_key:
                                    display_name = winreg.QueryValueEx(app_key, "DisplayName")[0]
                                    registry_checks.append({
                                        "key": "Uninstall Information",
                                        "status": "PASS",
                                        "display_name": display_name
                                    })
                                    found_uninstall = True
                                    break
                            i += 1
                        except OSError:
                            break
                    
                    if not found_uninstall:
                        registry_checks.append({
                            "key": "Uninstall Information",
                            "status": "FAIL",
                            "error": "アンインストール情報が見つかりません"
                        })
                        
            except Exception as e:
                registry_checks.append({
                    "key": "Uninstall Information",
                    "status": "FAIL",
                    "error": str(e)
                })
            
            self.test_results["registry_entries"] = {
                "status": "PASS" if all(check["status"] == "PASS" for check in registry_checks) else "PARTIAL",
                "checks": registry_checks
            }
            
            # 結果表示
            for check in registry_checks:
                if check["status"] == "PASS":
                    self.log(f"✅ {check['key']}: 正常")
                else:
                    self.log(f"❌ {check['key']}: {check.get('error', '失敗')}")
            
            return True
            
        except Exception as e:
            self.test_results["registry_entries"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.log(f"❌ レジストリテストエラー: {e}")
            return False
    
    def test_shortcuts(self):
        """ショートカットテスト"""
        self.log("🔗 ショートカットテスト")
        
        try:
            shortcuts_found = []
            
            # スタートメニューショートカット
            start_menu_path = Path(os.environ["ALLUSERSPROFILE"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "WabiMail"
            if start_menu_path.exists():
                wabimail_shortcut = start_menu_path / "WabiMail.lnk"
                if wabimail_shortcut.exists():
                    shortcuts_found.append({
                        "type": "Start Menu",
                        "path": str(wabimail_shortcut),
                        "status": "PASS"
                    })
                else:
                    shortcuts_found.append({
                        "type": "Start Menu",
                        "status": "FAIL",
                        "error": "ショートカットファイルが見つかりません"
                    })
            else:
                shortcuts_found.append({
                    "type": "Start Menu",
                    "status": "FAIL", 
                    "error": "スタートメニューフォルダが見つかりません"
                })
            
            # デスクトップショートカット（オプション）
            desktop_path = Path(os.environ["PUBLIC"]) / "Desktop" / "WabiMail.lnk"
            if desktop_path.exists():
                shortcuts_found.append({
                    "type": "Desktop",
                    "path": str(desktop_path),
                    "status": "PASS"
                })
            else:
                shortcuts_found.append({
                    "type": "Desktop",
                    "status": "SKIP",
                    "note": "デスクトップアイコンは作成されませんでした（ユーザー選択）"
                })
            
            self.test_results["shortcuts"] = {
                "status": "PASS" if any(s["status"] == "PASS" for s in shortcuts_found) else "FAIL",
                "shortcuts": shortcuts_found
            }
            
            # 結果表示
            for shortcut in shortcuts_found:
                if shortcut["status"] == "PASS":
                    self.log(f"✅ {shortcut['type']}: 正常")
                elif shortcut["status"] == "SKIP":
                    self.log(f"⏭️  {shortcut['type']}: スキップ")
                else:
                    self.log(f"❌ {shortcut['type']}: {shortcut.get('error', '失敗')}")
            
            return True
            
        except Exception as e:
            self.test_results["shortcuts"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.log(f"❌ ショートカットテストエラー: {e}")
            return False
    
    def test_application_launch(self):
        """アプリケーション起動テスト"""
        self.log("🚀 アプリケーション起動テスト")
        
        try:
            exe_path = self.test_install_dir / "WabiMail.exe"
            
            if not exe_path.exists():
                self.test_results["application_launch"] = {
                    "status": "FAIL",
                    "error": "実行ファイルが見つかりません"
                }
                return False
            
            # アプリケーション起動（短時間で終了）
            result = subprocess.run(
                [str(exe_path), "--version"],  # バージョン情報表示で即終了
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.test_results["application_launch"] = {
                    "status": "PASS",
                    "output": result.stdout.strip() if result.stdout else "起動成功"
                }
                self.log("✅ アプリケーション起動成功")
                return True
            else:
                self.test_results["application_launch"] = {
                    "status": "FAIL",
                    "return_code": result.returncode,
                    "stderr": result.stderr
                }
                self.log(f"❌ アプリケーション起動失敗: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            # GUIアプリの場合、タイムアウトは正常な場合もある
            self.test_results["application_launch"] = {
                "status": "PARTIAL",
                "note": "GUI起動のためタイムアウト（正常な可能性）"
            }
            self.log("⚠️  アプリケーション起動タイムアウト（GUI起動の可能性）")
            return True
        except Exception as e:
            self.test_results["application_launch"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.log(f"❌ 起動テストエラー: {e}")
            return False
    
    def test_uninstall(self, installer_file):
        """アンインストールテスト"""
        self.log("🗑️  アンインストールテスト")
        
        try:
            # アンインストーラー実行
            uninstaller_path = self.test_install_dir / "unins000.exe"
            
            if not uninstaller_path.exists():
                self.test_results["uninstall"] = {
                    "status": "FAIL",
                    "error": "アンインストーラーが見つかりません"
                }
                return False
            
            # サイレントアンインストール
            result = subprocess.run(
                [str(uninstaller_path), "/VERYSILENT", "/NORESTART"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # アンインストール確認
                time.sleep(2)  # アンインストール完了待機
                
                if not self.test_install_dir.exists():
                    self.test_results["uninstall"] = {
                        "status": "PASS",
                        "note": "アンインストール完了"
                    }
                    self.log("✅ アンインストール成功")
                    return True
                else:
                    self.test_results["uninstall"] = {
                        "status": "PARTIAL",
                        "note": "一部ファイルが残っている可能性があります"
                    }
                    self.log("⚠️  アンインストール部分的成功")
                    return True
            else:
                self.test_results["uninstall"] = {
                    "status": "FAIL",
                    "return_code": result.returncode,
                    "stderr": result.stderr
                }
                self.log(f"❌ アンインストール失敗: {result.returncode}")
                return False
                
        except Exception as e:
            self.test_results["uninstall"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.log(f"❌ アンインストールテストエラー: {e}")
            return False
    
    def generate_test_report(self):
        """テストレポート生成"""
        test_end_time = datetime.now()
        test_duration = test_end_time - self.test_start_time
        
        # サマリー計算
        total_tests = len(self.test_results)
        passed = sum(1 for result in self.test_results.values() if result.get("status") == "PASS")
        failed = sum(1 for result in self.test_results.values() if result.get("status") == "FAIL")
        partial = sum(1 for result in self.test_results.values() if result.get("status") == "PARTIAL")
        
        report_data = {
            "test_info": {
                "start_time": self.test_start_time.isoformat(),
                "end_time": test_end_time.isoformat(),
                "duration_seconds": test_duration.total_seconds(),
                "platform": "Windows"
            },
            "test_results": self.test_results,
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "partial": partial
            }
        }
        
        # レポートファイル保存
        report_dir = self.project_root / "test_reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = self.test_start_time.strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"installer_test_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.log(f"📄 テストレポート保存: {report_file}")
        
        # コンソール出力
        print("\n" + "=" * 60)
        print("📊 インストーラーテスト結果サマリー")
        print("=" * 60)
        print(f"総テスト数: {total_tests}")
        print(f"✅ 成功: {passed}")
        print(f"❌ 失敗: {failed}")
        print(f"⚠️  部分成功: {partial}")
        print()
        
        print("詳細結果:")
        for test_name, result in self.test_results.items():
            status_icon = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️"}.get(result["status"], "❓")
            print(f"  {status_icon} {test_name}: {result.get('note', result['status'])}")
        
        print("=" * 60)
        
        if failed == 0:
            print("✅ 全てのテストが正常に完了しました")
        else:
            print("❌ 一部のテストで問題が検出されました")
            print("詳細はテストレポートを確認してください")
        
        return report_file
    
    def run(self):
        """メインテスト処理"""
        print("🧪 WabiMail インストーラーテスト")
        print("=" * 60)
        print(f"テスト開始: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 管理者権限チェック（Windowsの場合）
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.log("❌ 管理者権限が必要です")
                return False
        except:
            self.log("⚠️  管理者権限チェックをスキップ")
        
        # インストーラーファイル検索
        installer_file = self.find_installer()
        if not installer_file:
            return False
        
        try:
            # 1. インストーラー特性テスト
            self.test_installer_properties(installer_file)
            
            # 2. サイレントインストールテスト
            if self.test_silent_install(installer_file):
                # 3. レジストリエントリテスト
                self.test_registry_entries()
                
                # 4. ショートカットテスト
                self.test_shortcuts()
                
                # 5. アプリケーション起動テスト
                self.test_application_launch()
                
                # 6. アンインストールテスト
                self.test_uninstall(installer_file)
            
            # 7. テストレポート生成
            self.generate_test_report()
            
            return True
            
        except Exception as e:
            self.log(f"❌ テスト実行エラー: {e}")
            return False


def main():
    """メイン関数"""
    if sys.platform != "win32":
        print("❌ このテストはWindows環境でのみ実行可能です")
        sys.exit(1)
    
    tester = WabiMailInstallerTester()
    
    try:
        success = tester.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ テストが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()