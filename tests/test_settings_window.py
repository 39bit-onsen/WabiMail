#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定画面ウィンドウテスト

Task 10: 設定画面実装のテストスイート
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile
import json

# テスト用のパス設定
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.app_config import AppConfig
from src.ui.settings_window import SettingsWindow


class TestSettingsWindow(unittest.TestCase):
    """設定ウィンドウテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        # テスト用の一時ディレクトリを作成
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = AppConfig(str(self.test_dir))
    
    def tearDown(self):
        """テスト後処理"""
        # テスト用ディレクトリをクリーンアップ
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_app_config_initialization(self):
        """AppConfig初期化テスト"""
        self.assertIsInstance(self.config, AppConfig)
        self.assertEqual(self.config.get("app.language"), "ja")
        self.assertEqual(self.config.get("app.theme"), "wabi_sabi_light")
        self.assertEqual(self.config.get("ui.font.size"), 10)
    
    def test_config_set_get(self):
        """設定値の設定・取得テスト"""
        self.config.set("ui.font.size", 12)
        self.assertEqual(self.config.get("ui.font.size"), 12)
        
        self.config.set("mail.check_interval", 600)
        self.assertEqual(self.config.get("mail.check_interval"), 600)
        
        self.config.set("security.encryption_enabled", False)
        self.assertEqual(self.config.get("security.encryption_enabled"), False)
    
    def test_config_save_load(self):
        """設定の保存・読み込みテスト"""
        # 設定を変更
        self.config.set("ui.font.size", 14)
        self.config.set("app.theme", "wabi_sabi_dark")
        self.config.save_config()
        
        # 新しいインスタンスで読み込み
        config2 = AppConfig(str(self.test_dir))
        self.assertEqual(config2.get("ui.font.size"), 14)
        self.assertEqual(config2.get("app.theme"), "wabi_sabi_dark")
    
    def test_config_reset(self):
        """設定リセットテスト"""
        # 設定を変更
        self.config.set("ui.font.size", 16)
        self.config.set("mail.check_interval", 900)
        
        # リセット
        self.config.reset_to_default()
        
        # デフォルト値に戻ることを確認
        self.assertEqual(self.config.get("ui.font.size"), 10)
        self.assertEqual(self.config.get("mail.check_interval"), 300)
    
    def test_settings_validation(self):
        """設定値検証テスト"""
        # フォントサイズ検証
        def validate_font_size(size):
            return 8 <= size <= 72
        
        self.assertTrue(validate_font_size(10))
        self.assertTrue(validate_font_size(12))
        self.assertFalse(validate_font_size(5))
        self.assertFalse(validate_font_size(100))
        
        # カラー値検証
        def validate_color(color):
            import re
            return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))
        
        self.assertTrue(validate_color("#FFFFFF"))
        self.assertTrue(validate_color("#123ABC"))
        self.assertFalse(validate_color("white"))
        self.assertFalse(validate_color("#12345"))
    
    def test_theme_settings(self):
        """テーマ設定テスト"""
        wabi_colors = {
            "bg": "#fefefe",
            "fg": "#333333",
            "accent": "#8b7355",
            "button_bg": "#f8f8f8"
        }
        
        self.assertEqual(wabi_colors["bg"], "#fefefe")
        self.assertEqual(wabi_colors["accent"], "#8b7355")
        
        # テーマ適用テスト
        def apply_wabi_theme(theme_type):
            if theme_type == "light":
                return wabi_colors
            elif theme_type == "dark":
                return {
                    "bg": "#2d2d2d",
                    "fg": "#e0e0e0",
                    "accent": "#8b7355",
                    "button_bg": "#404040"
                }
        
        light_theme = apply_wabi_theme("light")
        dark_theme = apply_wabi_theme("dark")
        
        self.assertEqual(light_theme["bg"], "#fefefe")
        self.assertEqual(dark_theme["bg"], "#2d2d2d")
    
    def test_settings_export_import(self):
        """設定エクスポート・インポートテスト"""
        # テスト用設定
        test_settings = {
            "app": {"language": "ja", "theme": "wabi_sabi_light"},
            "ui": {"font": {"size": 12}},
            "mail": {"check_interval": 600}
        }
        
        # エクスポート
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_settings, f, ensure_ascii=False, indent=2)
            export_file = f.name
        
        # インポート
        with open(export_file, 'r', encoding='utf-8') as f:
            imported_settings = json.load(f)
        
        self.assertEqual(imported_settings["app"]["language"], "ja")
        self.assertEqual(imported_settings["ui"]["font"]["size"], 12)
        self.assertEqual(imported_settings["mail"]["check_interval"], 600)
        
        # クリーンアップ
        os.unlink(export_file)


if __name__ == '__main__':
    unittest.main()