# -*- coding: utf-8 -*-
"""
アカウント管理のテストモジュール

AccountクラスとAccountManagerクラスの動作確認テストを提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
from datetime import datetime

# テスト用にプロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mail.account import Account, AccountType, AuthType, AccountSettings
from src.mail.account_manager import AccountManager
from src.config.app_config import AppConfig


class TestAccount:
    """
    Accountクラスのテストケース
    """
    
    def test_アカウント初期化_デフォルト値(self):
        """
        アカウントのデフォルト初期化をテスト
        """
        account = Account()
        
        # デフォルト値の確認
        assert account.account_id != ""  # UUIDが生成されている
        assert account.name == ""
        assert account.email_address == ""
        assert account.account_type == AccountType.IMAP
        assert account.auth_type == AuthType.PASSWORD
        assert account.is_active == True
        assert account.is_default == False
        assert account.sync_enabled == True
        assert isinstance(account.created_at, datetime)
        assert account.last_sync is None
    
    def test_アカウント初期化_表示名自動設定(self):
        """
        メールアドレスから表示名の自動設定をテスト
        """
        account = Account(email_address="test@example.com")
        assert account.display_name == "test"
        
        # 表示名を明示的に設定した場合は変更されない
        account = Account(email_address="test@example.com", display_name="カスタム名")
        assert account.display_name == "カスタム名"
    
    def test_アカウント検証_正常ケース(self):
        """
        正常なアカウント情報の検証をテスト
        """
        account = Account(
            name="テストアカウント",
            email_address="test@example.com",
            account_type=AccountType.IMAP
        )
        account.settings.incoming_server = "imap.example.com"
        account.settings.outgoing_server = "smtp.example.com"
        
        is_valid, errors = account.validate()
        assert is_valid == True
        assert len(errors) == 0
    
    def test_アカウント検証_必須項目エラー(self):
        """
        必須項目が不足している場合の検証をテスト
        """
        account = Account()
        
        is_valid, errors = account.validate()
        assert is_valid == False
        assert "アカウント名が必要です" in errors
        assert "メールアドレスが必要です" in errors
    
    def test_アカウント検証_メールアドレス形式エラー(self):
        """
        無効なメールアドレス形式の検証をテスト
        """
        account = Account(
            name="テストアカウント",
            email_address="invalid-email"
        )
        
        is_valid, errors = account.validate()
        assert is_valid == False
        assert "有効なメールアドレスを入力してください" in errors
    
    def test_プリセット設定_Gmail(self):
        """
        Gmailのプリセット設定をテスト
        """
        account = Account(account_type=AccountType.GMAIL)
        preset = account.get_preset_settings()
        
        assert preset.incoming_server == "imap.gmail.com"
        assert preset.incoming_port == 993
        assert preset.incoming_security == "SSL"
        assert preset.outgoing_server == "smtp.gmail.com"
        assert preset.outgoing_port == 587
        assert preset.outgoing_security == "STARTTLS"
    
    def test_プリセット設定適用(self):
        """
        プリセット設定の適用をテスト
        """
        account = Account(account_type=AccountType.GMAIL)
        account.apply_preset_settings()
        
        assert account.settings.incoming_server == "imap.gmail.com"
        assert account.settings.outgoing_server == "smtp.gmail.com"
    
    def test_辞書変換_往復変換(self):
        """
        アカウント情報の辞書変換をテスト
        """
        original = Account(
            name="テストアカウント",
            email_address="test@example.com",
            account_type=AccountType.GMAIL,
            auth_type=AuthType.OAUTH2,
            is_default=True,
            signature="テスト署名"
        )
        
        # 辞書に変換
        account_dict = original.to_dict()
        
        # 辞書からアカウントを復元
        restored = Account.from_dict(account_dict)
        
        # 内容が同じであることを確認
        assert restored.name == original.name
        assert restored.email_address == original.email_address
        assert restored.account_type == original.account_type
        assert restored.auth_type == original.auth_type
        assert restored.is_default == original.is_default
        assert restored.signature == original.signature
    
    def test_文字列表現(self):
        """
        アカウントの文字列表現をテスト
        """
        account = Account(
            name="テストアカウント",
            email_address="test@example.com",
            account_type=AccountType.GMAIL,
            is_active=True,
            is_default=True
        )
        
        account_str = str(account)
        assert "テストアカウント" in account_str
        assert "test@example.com" in account_str
        assert "gmail" in account_str
        assert "有効" in account_str
        assert "デフォルト" in account_str


class TestAccountManager:
    """
    AccountManagerクラスのテストケース
    """
    
    def setup_method(self):
        """
        各テストメソッド実行前の準備処理
        """
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config = AppConfig(self.temp_dir)
        self.manager = AccountManager(self.temp_config)
    
    def teardown_method(self):
        """
        各テストメソッド実行後のクリーンアップ処理
        """
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_初期化_空のアカウントリスト(self):
        """
        AccountManagerの初期化をテスト
        """
        assert self.manager.get_account_count() == 0
        assert self.manager.get_default_account() is None
        assert len(self.manager.get_all_accounts()) == 0
    
    def test_アカウント追加_正常ケース(self):
        """
        正常なアカウント追加をテスト
        """
        account = Account(
            name="テストアカウント",
            email_address="test@example.com",
            account_type=AccountType.GMAIL
        )
        
        result = self.manager.add_account(account)
        assert result == True
        assert self.manager.get_account_count() == 1
        
        # 初回追加はデフォルトアカウントになる
        assert account.is_default == True
        assert self.manager.get_default_account() == account
    
    def test_アカウント追加_重複メールアドレス(self):
        """
        重複するメールアドレスのアカウント追加をテスト
        """
        # 最初のアカウントを追加
        account1 = Account(
            name="アカウント1",
            email_address="test@example.com",
            account_type=AccountType.GMAIL  # Gmailはプリセット設定が適用される
        )
        self.manager.add_account(account1)
        
        # 同じメールアドレスのアカウントを追加（失敗するはず）
        account2 = Account(
            name="アカウント2",
            email_address="test@example.com",
            account_type=AccountType.GMAIL
        )
        result = self.manager.add_account(account2)
        
        assert result == False
        assert self.manager.get_account_count() == 1
    
    def test_アカウント取得_メールアドレス(self):
        """
        メールアドレスでのアカウント取得をテスト
        """
        account = Account(
            name="テストアカウント",
            email_address="test@example.com",
            account_type=AccountType.GMAIL
        )
        self.manager.add_account(account)
        
        # 大文字小文字を区別しない検索
        found = self.manager.get_account_by_email("TEST@EXAMPLE.COM")
        assert found is not None
        assert found.email_address == "test@example.com"
        
        # 存在しないメールアドレス
        not_found = self.manager.get_account_by_email("notfound@example.com")
        assert not_found is None
    
    def test_アカウント削除(self):
        """
        アカウント削除をテスト
        """
        account = Account(
            name="テストアカウント",
            email_address="test@example.com",
            account_type=AccountType.GMAIL
        )
        self.manager.add_account(account)
        assert self.manager.get_account_count() == 1
        
        # アカウントを削除
        result = self.manager.remove_account(account.account_id)
        assert result == True
        assert self.manager.get_account_count() == 0
        assert self.manager.get_account_by_id(account.account_id) is None
    
    def test_デフォルトアカウント管理(self):
        """
        デフォルトアカウントの管理をテスト
        """
        # 複数のアカウントを追加
        account1 = Account(name="アカウント1", email_address="test1@example.com", account_type=AccountType.GMAIL)
        account2 = Account(name="アカウント2", email_address="test2@example.com", account_type=AccountType.GMAIL)
        
        self.manager.add_account(account1)
        self.manager.add_account(account2)
        
        # 最初のアカウントがデフォルト
        assert account1.is_default == True
        assert account2.is_default == False
        
        # デフォルトアカウントを変更
        result = self.manager.set_default_account(account2.account_id)
        assert result == True
        assert account1.is_default == False
        assert account2.is_default == True
        assert self.manager.get_default_account() == account2
    
    def test_アカウントタイプ別取得(self):
        """
        アカウントタイプ別の取得をテスト
        """
        gmail_account = Account(
            name="Gmail",
            email_address="gmail@example.com",
            account_type=AccountType.GMAIL
        )
        imap_account = Account(
            name="IMAP",
            email_address="imap@example.com",
            account_type=AccountType.IMAP
        )
        # IMAPアカウントにサーバー設定を追加
        imap_account.settings.incoming_server = "imap.example.com"
        imap_account.settings.outgoing_server = "smtp.example.com"
        
        self.manager.add_account(gmail_account)
        self.manager.add_account(imap_account)
        
        gmail_accounts = self.manager.get_accounts_by_type(AccountType.GMAIL)
        assert len(gmail_accounts) == 1
        assert gmail_accounts[0] == gmail_account
        
        imap_accounts = self.manager.get_accounts_by_type(AccountType.IMAP)
        assert len(imap_accounts) == 1
        assert imap_accounts[0] == imap_account
    
    def test_統計情報取得(self):
        """
        アカウント統計情報の取得をテスト
        """
        # 複数のアカウントを追加
        gmail_account = Account(
            name="Gmail",
            email_address="gmail@example.com",
            account_type=AccountType.GMAIL,
            is_active=True
        )
        imap_account = Account(
            name="IMAP",
            email_address="imap@example.com",
            account_type=AccountType.IMAP,
            is_active=False
        )
        # IMAPアカウントにサーバー設定を追加
        imap_account.settings.incoming_server = "imap.example.com"
        imap_account.settings.outgoing_server = "smtp.example.com"
        
        self.manager.add_account(gmail_account)
        self.manager.add_account(imap_account)
        
        stats = self.manager.get_account_statistics()
        
        assert stats["total_accounts"] == 2
        assert stats["active_accounts"] == 1
        assert stats["inactive_accounts"] == 1
        assert stats["type_statistics"]["gmail"] == 1
        assert stats["type_statistics"]["imap"] == 1
        assert stats["has_default"] == True
    
    def test_ファイル保存読み込み(self):
        """
        アカウント情報のファイル保存・読み込みをテスト
        """
        # アカウントを追加
        account = Account(
            name="テストアカウント",
            email_address="test@example.com",
            account_type=AccountType.GMAIL
        )
        self.manager.add_account(account)
        
        # 新しいマネージャーで同じ設定ディレクトリから読み込み
        new_manager = AccountManager(self.temp_config)
        
        # アカウントが正しく読み込まれることを確認
        assert new_manager.get_account_count() == 1
        loaded_account = new_manager.get_account_by_email("test@example.com")
        assert loaded_account is not None
        assert loaded_account.name == "テストアカウント"
        assert loaded_account.account_type == AccountType.GMAIL


if __name__ == "__main__":
    """
    テストスクリプトとして直接実行された場合
    """
    pytest.main([__file__, "-v"])