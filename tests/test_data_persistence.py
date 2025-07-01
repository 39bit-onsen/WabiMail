#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ永続化テストスイート

Task 11: データ永続化システムのユニットテスト
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
from datetime import datetime

# テスト用のパス設定
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage.secure_storage import SecureStorage
from src.storage.account_storage import AccountStorage
from src.storage.mail_storage import MailStorage
from src.mail.account import Account, AccountType, AuthType, AccountSettings
from src.mail.mail_message import MailMessage, MailAttachment


class TestSecureStorage(unittest.TestCase):
    """SecureStorageテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.test_dir = tempfile.mkdtemp()
        self.storage = SecureStorage(self.test_dir)
    
    def tearDown(self):
        """テスト後処理"""
        self.storage.close()
        shutil.rmtree(self.test_dir)
    
    def test_encryption_decryption(self):
        """暗号化・復号テスト"""
        test_data = {"password": "secret", "token": "abc123"}
        
        encrypted = self.storage.encrypt_data(test_data)
        self.assertIsInstance(encrypted, str)
        
        decrypted = self.storage.decrypt_data(encrypted)
        self.assertEqual(decrypted, test_data)
    
    def test_app_settings(self):
        """アプリケーション設定テスト"""
        self.storage.save_app_setting("test_key", "test_value")
        value = self.storage.load_app_setting("test_key")
        self.assertEqual(value, "test_value")
        
        # デフォルト値テスト
        default_value = self.storage.load_app_setting("nonexistent", "default")
        self.assertEqual(default_value, "default")


class TestAccountStorage(unittest.TestCase):
    """AccountStorageテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.test_dir = tempfile.mkdtemp()
        self.account_storage = AccountStorage(self.test_dir)
        
        # テスト用アカウント
        self.test_account = Account(
            account_id="test_123",
            name="Test Account",
            email_address="test@example.com",
            account_type=AccountType.GMAIL,
            auth_type=AuthType.OAUTH2,
            settings=AccountSettings(
                incoming_server="imap.gmail.com",
                incoming_port=993,
                incoming_security="SSL",
                outgoing_server="smtp.gmail.com",
                outgoing_port=587,
                outgoing_security="STARTTLS",
                requires_auth=True
            )
        )
    
    def tearDown(self):
        """テスト後処理"""
        self.account_storage.close()
        shutil.rmtree(self.test_dir)
    
    def test_save_load_account(self):
        """アカウント保存・読み込みテスト"""
        # 保存テスト
        success, message = self.account_storage.save_account(self.test_account)
        self.assertTrue(success)
        
        # 読み込みテスト
        loaded_account = self.account_storage.load_account("test_123")
        self.assertIsNotNone(loaded_account)
        self.assertEqual(loaded_account.name, "Test Account")
        self.assertEqual(loaded_account.email_address, "test@example.com")
    
    def test_load_account_by_email(self):
        """メールアドレスによるアカウント検索テスト"""
        self.account_storage.save_account(self.test_account)
        
        found_account = self.account_storage.load_account_by_email("test@example.com")
        self.assertIsNotNone(found_account)
        self.assertEqual(found_account.account_id, "test_123")
    
    def test_oauth2_token_operations(self):
        """OAuth2トークン操作テスト"""
        token_data = {
            "access_token": "access123",
            "refresh_token": "refresh456",
            "expires_in": 3600
        }
        
        # トークン保存
        saved = self.account_storage.save_oauth2_token("test_123", token_data)
        self.assertTrue(saved)
        
        # トークン読み込み
        loaded_token = self.account_storage.load_oauth2_token("test_123")
        self.assertIsNotNone(loaded_token)
        self.assertEqual(loaded_token["access_token"], "access123")


class TestMailStorage(unittest.TestCase):
    """MailStorageテストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        self.test_dir = tempfile.mkdtemp()
        self.mail_storage = MailStorage(self.test_dir)
        
        # テスト用メッセージ
        self.test_message = MailMessage(
            subject="Test Message",
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            body_text="This is a test message.",
            date_received=datetime.now()
        )
        self.test_message.uid = "test_uid_001"
    
    def tearDown(self):
        """テスト後処理"""
        self.mail_storage.close()
        shutil.rmtree(self.test_dir)
    
    def test_cache_load_message(self):
        """メッセージキャッシュ・読み込みテスト"""
        # キャッシュテスト
        cached = self.mail_storage.cache_message("test_account", "INBOX", self.test_message)
        self.assertTrue(cached)
        
        # 読み込みテスト
        loaded_message = self.mail_storage.load_cached_message("test_account", "INBOX", "test_uid_001")
        self.assertIsNotNone(loaded_message)
        self.assertEqual(loaded_message.subject, "Test Message")
    
    def test_search_messages(self):
        """メッセージ検索テスト"""
        self.mail_storage.cache_message("test_account", "INBOX", self.test_message)
        
        # 検索テスト
        results = self.mail_storage.search_cached_messages("test_account", "Test")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].subject, "Test Message")
    
    def test_cache_stats(self):
        """キャッシュ統計テスト"""
        self.mail_storage.cache_message("test_account", "INBOX", self.test_message)
        
        stats = self.mail_storage.get_cache_stats("test_account")
        self.assertIn("total_messages", stats)
        self.assertGreaterEqual(stats["total_messages"], 1)


class TestDataPersistenceIntegration(unittest.TestCase):
    """データ永続化統合テスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """テスト後処理"""
        shutil.rmtree(self.test_dir)
    
    def test_full_integration(self):
        """完全統合テスト"""
        # 各ストレージシステムを初期化
        account_storage = AccountStorage(self.test_dir)
        mail_storage = MailStorage(self.test_dir)
        
        try:
            # アカウント作成
            test_account = Account(
                account_id="integration_test",
                name="Integration Test",
                email_address="integration@example.com",
                account_type=AccountType.IMAP,
                auth_type=AuthType.PASSWORD,
                settings=AccountSettings(
                    incoming_server="mail.example.com",
                    incoming_port=993,
                    incoming_security="SSL",
                    outgoing_server="smtp.example.com",
                    outgoing_port=587,
                    outgoing_security="STARTTLS",
                    requires_auth=True
                )
            )
            
            # アカウント保存
            success, _ = account_storage.save_account(test_account)
            self.assertTrue(success)
            
            # メッセージキャッシュ
            test_message = MailMessage(
                subject="Integration Test Mail",
                sender="sender@example.com",
                recipients=["integration@example.com"],
                body_text="Integration test message.",
                date_received=datetime.now()
            )
            test_message.uid = "integration_001"
            
            cached = mail_storage.cache_message("integration_test", "INBOX", test_message)
            self.assertTrue(cached)
            
            # データ整合性確認
            loaded_account = account_storage.load_account("integration_test")
            self.assertIsNotNone(loaded_account)
            
            loaded_message = mail_storage.load_cached_message("integration_test", "INBOX", "integration_001")
            self.assertIsNotNone(loaded_message)
            
        finally:
            account_storage.close()
            mail_storage.close()


if __name__ == '__main__':
    unittest.main()