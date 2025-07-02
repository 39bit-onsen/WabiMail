#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WabiMail Inno Setup インストーラービルドスクリプト

Task 14: Inno Setupインストーラー作成
Windows用インストーラーパッケージを生成します。
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent.parent
INSTALLER_DIR = PROJECT_ROOT / "installer"
DIST_DIR = PROJECT_ROOT / "dist"
INSTALLER_OUTPUT_DIR = DIST_DIR / "installer"

# Inno Setup設定
INNO_SETUP_COMPILER = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
ISS_FILE = INSTALLER_DIR / "wabimail_installer.iss"

# アセット設定
ASSETS_DIR = PROJECT_ROOT / "resources"
ICONS_DIR = ASSETS_DIR / "assets" / "icons"
INSTALLER_ASSETS_DIR = ASSETS_DIR / "installer"


class WabiMailInstallerBuilder:
    """WabiMail インストーラービルダー"""
    
    def __init__(self):
        """初期化"""
        self.build_start_time = datetime.now()
        self.build_log = []
        
    def log(self, message):
        """ログ出力"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.build_log.append(log_message)
    
    def check_requirements(self):
        """ビルド要件チェック"""
        self.log("🔍 インストーラービルド要件チェック")
        
        # Inno Setup の確認
        if not Path(INNO_SETUP_COMPILER).exists():
            self.log("❌ Inno Setup 6 が見つかりません")
            self.log("   インストール URL: https://jrsoftware.org/isdl.php")
            return False
        
        self.log("✅ Inno Setup 6 が見つかりました")
        
        # 実行ファイルの確認
        exe_path = DIST_DIR / "WabiMail.exe"
        if not exe_path.exists():
            self.log("❌ WabiMail.exe が見つかりません")
            self.log("   先にPyInstallerでビルドしてください: python build_exe.py")
            return False
        
        self.log("✅ WabiMail.exe 確認済み")
        
        # 必要なファイルの確認
        required_files = [
            PROJECT_ROOT / "config.yaml",
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "LICENSE"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                self.log(f"❌ 必要なファイルが見つかりません: {file_path}")
                return False
        
        self.log("✅ 必要なファイル確認済み")
        return True
    
    def prepare_installer_assets(self):
        """インストーラー用アセット準備"""
        self.log("🎨 インストーラー用アセット準備")
        
        # インストーラーアセットディレクトリ作成
        INSTALLER_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        
        # アイコンファイルの準備
        icon_source = ICONS_DIR / "wabimail.png"
        icon_ico = ASSETS_DIR / "assets" / "icons" / "wabimail.ico"
        
        if not icon_ico.exists() and icon_source.exists():
            try:
                from PIL import Image
                # PNGからICOに変換
                img = Image.open(icon_source)
                img.save(icon_ico, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
                self.log("✅ アイコンファイル変換完了")
            except ImportError:
                self.log("⚠️  Pillowが必要です: pip install pillow")
                # 仮のアイコンファイル作成
                icon_ico.touch()
        
        # インストーラー用画像の準備
        self._create_installer_images()
        
        self.log("✅ アセット準備完了")
    
    def _create_installer_images(self):
        """インストーラー用画像作成"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # ウィザード大画像 (164x314)
            wizard_large = Image.new('RGB', (164, 314), '#F5F5DC')  # Beige背景
            draw = ImageDraw.Draw(wizard_large)
            
            # シンプルなグラデーション効果
            for y in range(314):
                alpha = int(255 * (y / 314) * 0.1)
                color = (47, 79, 79, alpha)  # DarkSlateGray
                draw.line([(0, y), (164, y)], fill=color[:3])
            
            wizard_large.save(INSTALLER_ASSETS_DIR / "wizard-large.bmp")
            
            # ウィザード小画像 (55x55)
            wizard_small = Image.new('RGB', (55, 55), '#F5F5DC')
            draw_small = ImageDraw.Draw(wizard_small)
            
            # 円形のアクセント
            draw_small.ellipse([10, 10, 45, 45], fill='#2F4F4F', outline='#5F9EA0')
            
            wizard_small.save(INSTALLER_ASSETS_DIR / "wizard-small.bmp")
            
            self.log("✅ インストーラー画像作成完了")
            
        except ImportError:
            self.log("⚠️  Pillowがないため、デフォルト画像を使用")
            # 空の画像ファイル作成
            (INSTALLER_ASSETS_DIR / "wizard-large.bmp").touch()
            (INSTALLER_ASSETS_DIR / "wizard-small.bmp").touch()
    
    def build_installer(self):
        """インストーラービルド"""
        self.log("🔨 Inno Setup インストーラービルド開始")
        
        # 出力ディレクトリ作成
        INSTALLER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Inno Setup コンパイル実行
        try:
            cmd = [str(INNO_SETUP_COMPILER), str(ISS_FILE)]
            self.log(f"実行コマンド: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分タイムアウト
            )
            
            if result.returncode == 0:
                self.log("✅ インストーラービルド成功")
                return True
            else:
                self.log("❌ インストーラービルド失敗")
                self.log(f"エラー出力: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("❌ ビルドタイムアウト（5分超過）")
            return False
        except FileNotFoundError:
            self.log("❌ Inno Setup コンパイラーが見つかりません")
            return False
    
    def test_installer(self):
        """インストーラーテスト"""
        self.log("🧪 インストーラーテスト")
        
        # 生成されたインストーラーファイル確認
        installer_pattern = INSTALLER_OUTPUT_DIR / "WabiMail-Setup-*.exe"
        installer_files = list(INSTALLER_OUTPUT_DIR.glob("WabiMail-Setup-*.exe"))
        
        if not installer_files:
            self.log("❌ インストーラーファイルが見つかりません")
            return False
        
        installer_file = installer_files[0]
        file_size_mb = installer_file.stat().st_size / (1024 * 1024)
        
        self.log(f"✅ インストーラーファイル: {installer_file.name}")
        self.log(f"📊 ファイルサイズ: {file_size_mb:.2f} MB")
        
        # サイズチェック（適切な範囲）
        if file_size_mb < 20:
            self.log("⚠️  ファイルサイズが小さすぎる可能性があります")
        elif file_size_mb > 100:
            self.log("⚠️  ファイルサイズが大きすぎる可能性があります")
        else:
            self.log("✅ ファイルサイズは適切です")
        
        return True
    
    def generate_build_report(self):
        """ビルドレポート生成"""
        build_time = datetime.now() - self.build_start_time
        
        report = f"""🌸 WabiMail インストーラービルドレポート
============================================================
ビルド日時: {self.build_start_time.strftime('%Y-%m-%d %H:%M:%S')}
ビルド時間: {build_time.total_seconds():.1f}秒
プラットフォーム: Windows
============================================================

ビルドログ:
"""
        
        for log_entry in self.build_log:
            report += f"{log_entry}\n"
        
        report += f"""
============================================================
📁 成果物:
  - インストーラー: {INSTALLER_OUTPUT_DIR}
  - ISS スクリプト: {ISS_FILE}

🧪 次のステップ:
  1. Windows環境でのインストールテスト
  2. アンインストール動作確認
  3. 複数環境での互換性テスト

✨ インストーラービルドが完了しました！
"""
        
        # レポートファイル保存
        report_dir = PROJECT_ROOT / "build_reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = self.build_start_time.strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"installer_build_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.log(f"📄 ビルドレポート保存: {report_file}")
        print(report)
    
    def run(self):
        """メインビルド処理"""
        print("🌸 WabiMail インストーラービルド")
        print("=" * 60)
        print(f"ビルド開始: {self.build_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. 要件チェック
        if not self.check_requirements():
            return False
        
        # 2. アセット準備
        self.prepare_installer_assets()
        
        # 3. インストーラービルド
        if not self.build_installer():
            return False
        
        # 4. テスト
        if not self.test_installer():
            return False
        
        # 5. レポート生成
        self.generate_build_report()
        
        return True


def main():
    """メイン関数"""
    builder = WabiMailInstallerBuilder()
    
    try:
        success = builder.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        builder.log("❌ ビルドが中断されました")
        sys.exit(1)
    except Exception as e:
        builder.log(f"❌ 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()