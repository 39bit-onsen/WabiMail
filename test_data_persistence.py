#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ永続化機能テスト

Task 11: データ永続化システムの基本動作確認
- SecureStorageクラスの基本機能テスト
- AccountStorageクラスの機能テスト
- MailStorageクラスの機能テスト
- 暗号化・復号処理テスト
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.storage.secure_storage import SecureStorage
from src.storage.account_storage import AccountStorage
from src.storage.mail_storage import MailStorage
from src.mail.account import Account, AccountType, AuthType, AccountSettings
from src.mail.mail_message import MailMessage, MailAttachment


def test_secure_storage():
    """SecureStorage基本機能テスト"""
    print("🔒 SecureStorage 基本機能テスト")
    print("-" * 40)
    
    try:
        # テスト用一時ディレクトリ
        test_dir = tempfile.mkdtemp()
        
        with SecureStorage(test_dir) as storage:
            # 暗号化・復号テスト
            test_data = {
                "username": "test@example.com",
                "password": "secret123",
                "settings": {
                    "server": "mail.example.com",
                    "port": 993
                }
            }
            
            print("✅ 暗号化テスト")
            encrypted = storage.encrypt_data(test_data)
            assert isinstance(encrypted, str)
            assert len(encrypted) > 0
            
            print("✅ 復号テスト")
            decrypted = storage.decrypt_data(encrypted)
            assert decrypted == test_data
            
            # アプリケーション設定保存・読み込みテスト
            print("✅ アプリケーション設定テスト")
            storage.save_app_setting("ui.theme", "wabi_sabi_light")
            storage.save_app_setting("mail.check_interval", 300)
            
            theme = storage.load_app_setting("ui.theme")
            interval = storage.load_app_setting("mail.check_interval")
            
            assert theme == "wabi_sabi_light"
            assert interval == 300
            
            # ストレージ情報取得テスト
            print("✅ ストレージ情報取得テスト")
            info = storage.get_storage_info()
            assert "storage_dir" in info
            assert "database_size_bytes" in info
            assert info["encryption_enabled"] == True
        
        # テスト用ディレクトリクリーンアップ
        shutil.rmtree(test_dir)
        
        print("✅ SecureStorage基本機能テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ SecureStorageテストエラー: {e}")
        return False


def test_account_storage():
    """AccountStorage機能テスト"""
    print("\n📧 AccountStorage 機能テスト")
    print("-" * 40)
    
    try:
        # テスト用一時ディレクトリ
        test_dir = tempfile.mkdtemp()
        
        with AccountStorage(test_dir) as account_storage:
            # テスト用アカウント作成
            test_account = Account(
                account_id="test_001",
                name="テストアカウント",
                email_address="test@wabimail.example.com",
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
            
            # アカウント保存テスト
            print("✅ アカウント保存テスト")
            success, message = account_storage.save_account(test_account)
            assert success == True
            assert "正常に保存" in message
            
            # アカウント読み込みテスト
            print("✅ アカウント読み込みテスト")
            loaded_account = account_storage.load_account("test_001")
            assert loaded_account is not None
            assert loaded_account.name == "テストアカウント"
            assert loaded_account.email_address == "test@wabimail.example.com"
            assert loaded_account.account_type == AccountType.GMAIL
            
            # メールアドレスによる検索テスト
            print("✅ メールアドレス検索テスト")
            found_account = account_storage.load_account_by_email("test@wabimail.example.com")
            assert found_account is not None
            assert found_account.account_id == "test_001"
            
            # アカウントリスト取得テスト
            print("✅ アカウントリスト取得テスト")
            account_list = account_storage.list_accounts()
            assert len(account_list) == 1
            assert account_list[0]["email_address"] == "test@wabimail.example.com"
            
            # OAuth2トークン保存・読み込みテスト
            print("✅ OAuth2トークンテスト")
            token_data = {
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "expires_in": 3600
            }
            
            token_saved = account_storage.save_oauth2_token("test_001", token_data)
            assert token_saved == True
            
            loaded_token = account_storage.load_oauth2_token("test_001")
            assert loaded_token is not None
            assert loaded_token["access_token"] == "test_access_token"
            
            # アカウント更新テスト
            print("✅ アカウント更新テスト")
            test_account.name = "更新されたテストアカウント"
            success, message = account_storage.update_account(test_account)
            assert success == True
            
            updated_account = account_storage.load_account("test_001")
            assert updated_account.name == "更新されたテストアカウント"
            
            # アカウント削除テスト
            print("✅ アカウント削除テスト")
            success, message = account_storage.delete_account("test_001")
            assert success == True
            
            deleted_account = account_storage.load_account("test_001")
            assert deleted_account is None
        
        # テスト用ディレクトリクリーンアップ
        shutil.rmtree(test_dir)
        
        print("✅ AccountStorage機能テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ AccountStorageテストエラー: {e}")
        return False


def test_mail_storage():
    """MailStorage機能テスト"""
    print("\n📬 MailStorage 機能テスト")
    print("-" * 40)
    
    try:
        # テスト用一時ディレクトリ
        test_dir = tempfile.mkdtemp()
        
        with MailStorage(test_dir) as mail_storage:
            # テスト用メッセージ作成
            test_message = MailMessage(
                subject="テストメッセージ",
                sender="sender@example.com",
                recipients=["recipient@example.com"],
                body_text="これはテスト用のメールメッセージです。",
                date_received=datetime.now()
            )
            
            # 添付ファイル付きメッセージ
            attachment = MailAttachment(
                filename="test.txt",
                content_type="text/plain",
                size=100,
                data=b"test file content"
            )
            test_message.attachments.append(attachment)
            
            # メッセージキャッシュテスト
            print("✅ メッセージキャッシュテスト")
            cached = mail_storage.cache_message("test_account", "INBOX", test_message)
            assert cached == True
            
            # メッセージ読み込みテスト
            print("✅ メッセージ読み込みテスト")
            # UIDを設定（キャッシュ時に生成される）
            test_message.uid = "test_uid_001"
            mail_storage.cache_message("test_account", "INBOX", test_message)
            
            loaded_message = mail_storage.load_cached_message("test_account", "INBOX", "test_uid_001")
            assert loaded_message is not None
            assert loaded_message.subject == "テストメッセージ"
            assert loaded_message.sender == "sender@example.com"
            assert len(loaded_message.attachments) == 1
            
            # メッセージリスト取得テスト
            print("✅ メッセージリスト取得テスト")
            message_list = mail_storage.list_cached_messages("test_account", "INBOX")
            assert len(message_list) >= 1
            
            # メッセージ検索テスト
            print("✅ メッセージ検索テスト")
            search_results = mail_storage.search_cached_messages("test_account", "テスト")
            assert len(search_results) >= 1
            assert search_results[0].subject == "テストメッセージ"
            
            # キャッシュ統計テスト
            print("✅ キャッシュ統計テスト")
            stats = mail_storage.get_cache_stats("test_account")
            assert "total_messages" in stats
            assert stats["total_messages"] >= 1
            
            # メッセージ削除テスト
            print("✅ メッセージ削除テスト")
            deleted = mail_storage.delete_cached_message("test_account", "INBOX", "test_uid_001")
            assert deleted == True
            
            deleted_message = mail_storage.load_cached_message("test_account", "INBOX", "test_uid_001")
            assert deleted_message is None
        
        # テスト用ディレクトリクリーンアップ
        shutil.rmtree(test_dir)
        
        print("✅ MailStorage機能テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ MailStorageテストエラー: {e}")
        return False


def test_integration():
    """統合テスト"""
    print("\n🔗 統合テスト")
    print("-" * 40)
    
    try:
        # テスト用一時ディレクトリ
        test_dir = tempfile.mkdtemp()
        
        # すべてのストレージシステムが同じディレクトリを使用
        account_storage = AccountStorage(test_dir)
        mail_storage = MailStorage(test_dir)
        
        # アカウント作成とメールキャッシュの連携テスト
        test_account = Account(
            account_id="integration_test",
            name="統合テストアカウント",
            email_address="integration@wabimail.example.com",
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
        
        print("✅ アカウント・メール連携テスト")
        # アカウント保存
        success, _ = account_storage.save_account(test_account)
        assert success == True
        
        # そのアカウントのメールをキャッシュ
        test_message = MailMessage(
            subject="統合テストメール",
            sender="sender@example.com",
            recipients=["integration@wabimail.example.com"],
            body_text="統合テスト用のメールです。",
            date_received=datetime.now()
        )
        test_message.uid = "integration_001"
        
        cached = mail_storage.cache_message("integration_test", "INBOX", test_message)
        assert cached == True
        
        # ストレージ情報確認
        print("✅ ストレージ情報統合確認")
        account_info = account_storage.get_storage_info()
        mail_stats = mail_storage.get_cache_stats("integration_test")
        
        assert account_info["accounts_count"] >= 1
        assert mail_stats["total_messages"] >= 1
        
        # クリーンアップ
        account_storage.close()
        mail_storage.close()
        shutil.rmtree(test_dir)
        
        print("✅ 統合テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 統合テストエラー: {e}")
        return False


def main():
    """メイン関数"""
    print("🌸 WabiMail データ永続化機能テスト")
    print("=" * 50)
    
    test_results = []
    
    # 各テストを実行
    test_results.append(test_secure_storage())
    test_results.append(test_account_storage())
    test_results.append(test_mail_storage())
    test_results.append(test_integration())
    
    # 結果サマリー
    print("\n📊 テスト結果サマリー")
    print("=" * 50)
    
    passed_count = sum(test_results)
    total_count = len(test_results)
    
    print(f"✅ 成功: {passed_count}/{total_count} テスト")
    
    if passed_count == total_count:
        print("🎉 全てのテストが成功しました！")
        print("\n🔒 データ永続化システムの基本実装が完了")
        print("✨ 次のステップ: 実際のアプリケーションでの動作確認")
        return True
    else:
        failed_count = total_count - passed_count
        print(f"❌ 失敗: {failed_count}/{total_count} テスト")
        return False


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        exit(1)