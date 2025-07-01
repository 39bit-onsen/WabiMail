# -*- coding: utf-8 -*-
"""
アプリケーション設定のテストモジュール

AppConfigクラスの動作確認テストを提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# テスト用にプロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.app_config import AppConfig


class TestAppConfig:
    """
    AppConfigクラスのテストケース
    """
    
    def setup_method(self):
        """
        各テストメソッド実行前の準備処理
        一時ディレクトリを作成してテスト用設定として使用
        """
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config_dir = Path(self.temp_dir) / ".wabimail_test"
    
    def teardown_method(self):
        """
        各テストメソッド実行後のクリーンアップ処理
        一時ディレクトリを削除
        """
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_初期化_デフォルト設定(self):
        """
        AppConfigの初期化でデフォルト設定が正しく設定されることをテスト
        """
        config = AppConfig(str(self.temp_config_dir))
        
        # デフォルト値の確認
        assert config.get("app.language") == "ja"
        assert config.get("app.theme") == "wabi_sabi_light"
        assert config.get("ui.font.family") == "Meiryo"
        assert config.get("mail.check_interval") == 300
    
    def test_設定値の取得と設定(self):
        """
        設定値の取得・設定が正しく動作することをテスト
        """
        config = AppConfig(str(self.temp_config_dir))
        
        # 設定値の変更
        config.set("ui.font.size", 14)
        assert config.get("ui.font.size") == 14
        
        # 存在しないキーのデフォルト値
        assert config.get("nonexistent.key", "default") == "default"
    
    def test_設定ファイルの保存と読み込み(self):
        """
        設定ファイルの保存・読み込みが正しく動作することをテスト
        """
        # 最初のインスタンスで設定を変更・保存
        config1 = AppConfig(str(self.temp_config_dir))
        config1.set("app.language", "en")
        config1.save_config()
        
        # 新しいインスタンスで設定を読み込み
        config2 = AppConfig(str(self.temp_config_dir))
        assert config2.get("app.language") == "en"
    
    def test_初回起動フラグ(self):
        """
        初回起動フラグの動作をテスト
        """
        config = AppConfig(str(self.temp_config_dir))
        
        # 初回起動のはず
        assert config.is_first_run() == True
        
        # セットアップ完了をマーク
        config.mark_setup_complete()
        assert config.is_first_run() == False
    
    def test_設定リセット(self):
        """
        設定のリセット機能をテスト
        """
        config = AppConfig(str(self.temp_config_dir))
        
        # 設定を変更
        config.set("ui.font.size", 16)
        config.set("app.language", "en")
        
        # リセット実行
        config.reset_to_default()
        
        # デフォルト値に戻っていることを確認
        assert config.get("ui.font.size") == 10  # デフォルト値
        assert config.get("app.language") == "ja"  # デフォルト値


if __name__ == "__main__":
    """
    テストスクリプトとして直接実行された場合
    """
    pytest.main([__file__, "-v"])