# -*- coding: utf-8 -*-
"""
OAuth2認証機能のテストモジュール

OAuth2Manager、TokenStorage、関連機能の動作確認テストを提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# テスト用にプロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.auth.token_storage import TokenStorage
from src.auth.oauth2_manager import GmailOAuth2Manager
from src.config.oauth2_config import OAuth2Config, OAuth2Messages
from src.mail.account import Account, AccountType, AuthType


class TestTokenStorage:
    """
    TokenStorageクラスのテストケース
    """
    
    @pytest.fixture
    def temp_dir(self):
        """
        テスト用一時ディレクトリを作成
        """
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def token_storage(self, temp_dir):
        """
        テスト用TokenStorageインスタンスを作成
        """
        with patch.object(TokenStorage, '_get_app_data_dir', return_value=Path(temp_dir)):
            storage = TokenStorage()
            return storage
    
    def test_初期化(self, token_storage):
        """
        TokenStorageの初期化をテスト
        """
        assert token_storage.storage_dir.exists()
        assert token_storage.encryption_key is not None
        assert token_storage._fernet is not None
    
    def test_トークン保存_読み込み(self, token_storage):
        """
        トークンの保存・読み込みをテスト
        """
        account_id = "test-account"
        token_data = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_in': 3600,
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'scopes': ['https://www.googleapis.com/auth/gmail.readonly']
        }
        
        # 保存
        success = token_storage.save_token(account_id, token_data)
        assert success == True
        
        # 読み込み
        loaded_token = token_storage.load_token(account_id)
        assert loaded_token is not None
        assert loaded_token['access_token'] == 'test_access_token'
        assert loaded_token['refresh_token'] == 'test_refresh_token'
        assert loaded_token['account_id'] == account_id
        assert 'saved_at' in loaded_token
    
    def test_存在しないトークン読み込み(self, token_storage):
        """
        存在しないトークンの読み込みをテスト
        """
        loaded_token = token_storage.load_token("nonexistent-account")
        assert loaded_token is None
    
    def test_トークン削除(self, token_storage):
        """
        トークンの削除をテスト
        """
        account_id = "test-account"
        token_data = {'access_token': 'test_token'}
        
        # 保存
        token_storage.save_token(account_id, token_data)
        assert token_storage.load_token(account_id) is not None
        
        # 削除
        success = token_storage.delete_token(account_id)
        assert success == True
        assert token_storage.load_token(account_id) is None
    
    def test_トークン期限チェック(self, token_storage):
        """
        トークンの期限チェックをテスト
        """
        # 有効なトークン
        valid_token = {
            'expires_in': 3600,
            'saved_at': datetime.now().isoformat()
        }
        assert token_storage.is_token_expired(valid_token) == False
        
        # 期限切れトークン
        expired_token = {
            'expires_in': 3600,
            'saved_at': (datetime.now() - timedelta(hours=2)).isoformat()
        }
        assert token_storage.is_token_expired(expired_token) == True
        
        # 保存日時なしトークン
        invalid_token = {
            'expires_in': 3600
        }
        assert token_storage.is_token_expired(invalid_token) == True
    
    def test_保存済みトークンリスト取得(self, token_storage):
        """
        保存済みトークンリストの取得をテスト
        """
        # 初期状態
        account_list = token_storage.list_stored_tokens()
        assert len(account_list) == 0
        
        # トークンを保存
        token_storage.save_token("account1", {'access_token': 'token1'})
        token_storage.save_token("account2", {'access_token': 'token2'})
        
        # リスト取得
        account_list = token_storage.list_stored_tokens()
        assert len(account_list) == 2
        assert "account1" in account_list
        assert "account2" in account_list
    
    def test_ストレージ情報取得(self, token_storage):
        """
        ストレージ情報の取得をテスト
        """
        # トークンを保存
        token_storage.save_token("test-account", {'access_token': 'token'})
        
        info = token_storage.get_storage_info()
        
        assert 'storage_directory' in info
        assert info['stored_account_count'] == 1
        assert 'test-account' in info['stored_accounts']
        assert info['encryption_enabled'] == True


class TestOAuth2Config:
    """
    OAuth2Configクラスのテストケース
    """
    
    def test_設定値確認(self):
        """
        OAuth2設定値をテスト
        """
        assert len(OAuth2Config.GMAIL_SCOPES) > 0
        assert 'https://www.googleapis.com/auth/gmail.readonly' in OAuth2Config.GMAIL_SCOPES
        assert OAuth2Config.DEFAULT_CALLBACK_PORT == 8080
        assert OAuth2Config.AUTH_TIMEOUT_SECONDS > 0
    
    def test_スコープ検証(self):
        """
        スコープの検証をテスト
        """
        # 有効なスコープ
        valid_scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        assert OAuth2Config.validate_scopes(valid_scopes) == True
        
        # 無効なスコープ
        invalid_scopes = ['invalid_scope']
        assert OAuth2Config.validate_scopes(invalid_scopes) == False
        
        # 混在スコープ
        mixed_scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'invalid_scope'
        ]
        assert OAuth2Config.validate_scopes(mixed_scopes) == False
    
    def test_最小スコープ取得(self):
        """
        最小スコープの取得をテスト
        """
        minimal_scopes = OAuth2Config.get_minimal_scopes()
        assert len(minimal_scopes) >= 2
        assert 'https://www.googleapis.com/auth/gmail.readonly' in minimal_scopes
        assert 'https://www.googleapis.com/auth/gmail.send' in minimal_scopes
    
    def test_設定辞書取得(self):
        """
        設定辞書の取得をテスト
        """
        config_dict = OAuth2Config.get_config_dict()
        
        assert 'scopes' in config_dict
        assert 'callback_port_range' in config_dict
        assert 'default_callback_port' in config_dict
        assert isinstance(config_dict['scopes'], list)
        assert isinstance(config_dict['callback_port_range'], tuple)


class TestOAuth2Messages:
    """
    OAuth2Messagesクラスのテストケース
    """
    
    def test_メッセージ定数(self):
        """
        メッセージ定数をテスト
        """
        assert len(OAuth2Messages.AUTH_SUCCESS) > 0
        assert "Gmail" in OAuth2Messages.AUTH_SUCCESS
        assert len(OAuth2Messages.CLIENT_SECRET_NOT_FOUND) > 0
        assert "client_secret.json" in OAuth2Messages.CLIENT_SECRET_NOT_FOUND
    
    def test_スコープ説明(self):
        """
        スコープ説明の取得をテスト
        """
        readonly_scope = 'https://www.googleapis.com/auth/gmail.readonly'
        description = OAuth2Messages.get_scope_description(readonly_scope)
        assert "読み取り" in description
        
        # 不明なスコープ
        unknown_scope = 'unknown_scope'
        description = OAuth2Messages.get_scope_description(unknown_scope)
        assert description == unknown_scope
    
    def test_スコープリストフォーマット(self):
        """
        スコープリストのフォーマットをテスト
        """
        scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send'
        ]
        formatted = OAuth2Messages.format_scopes_list(scopes)
        assert "読み取り" in formatted
        assert "送信" in formatted
        assert "、" in formatted


class TestGmailOAuth2Manager:
    """
    GmailOAuth2Managerクラスのテストケース
    """
    
    @pytest.fixture
    def temp_dir(self):
        """
        テスト用一時ディレクトリを作成
        """
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_client_secret_file(self, temp_dir):
        """
        テスト用client_secret.jsonファイルを作成
        """
        client_secret_content = {
            "installed": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
            }
        }
        
        client_secret_path = Path(temp_dir) / "client_secret.json"
        with open(client_secret_path, 'w', encoding='utf-8') as f:
            json.dump(client_secret_content, f)
        
        return client_secret_path
    
    @pytest.fixture
    def oauth2_manager(self, temp_dir, mock_client_secret_file):
        """
        テスト用OAuth2Managerインスタンスを作成
        """
        with patch.object(TokenStorage, '_get_app_data_dir', return_value=Path(temp_dir)):
            manager = GmailOAuth2Manager(client_secret_path=mock_client_secret_file)
            return manager
    
    def test_初期化(self, oauth2_manager):
        """
        OAuth2Managerの初期化をテスト
        """
        assert oauth2_manager.scopes == GmailOAuth2Manager.SCOPES
        assert oauth2_manager.token_storage is not None
        assert oauth2_manager.client_secret_path is not None
        assert oauth2_manager._credentials_cache == {}
    
    def test_client_secret_利用可能性チェック(self, oauth2_manager):
        """
        client_secret.jsonの利用可能性チェックをテスト
        """
        # 有効なファイル
        assert oauth2_manager.is_client_secret_available() == True
        
        # 存在しないファイル
        oauth2_manager.client_secret_path = Path("/nonexistent/path")
        assert oauth2_manager.is_client_secret_available() == False
    
    def test_認証情報取得_キャッシュなし(self, oauth2_manager):
        """
        認証情報取得（キャッシュなし）をテスト
        """
        account_id = "test-account"
        
        # トークンが保存されていない場合
        credentials = oauth2_manager.get_credentials(account_id)
        assert credentials is None
    
    def test_認証状態チェック(self, oauth2_manager):
        """
        認証状態のチェックをテスト
        """
        account_id = "test-account"
        
        # 認証されていない場合
        assert oauth2_manager.is_authenticated(account_id) == False
    
    def test_認証情報削除(self, oauth2_manager):
        """
        認証情報の削除をテスト
        """
        account_id = "test-account"
        
        # 存在しないトークンの削除
        success = oauth2_manager.revoke_credentials(account_id)
        assert success == False  # ファイルが存在しないため
    
    def test_認証情報詳細取得(self, oauth2_manager):
        """
        認証情報詳細の取得をテスト
        """
        account_id = "test-account"
        
        info = oauth2_manager.get_authentication_info(account_id)
        
        assert 'account_id' in info
        assert info['account_id'] == account_id
        assert 'is_authenticated' in info
        assert 'has_stored_token' in info
        assert 'scopes' in info
        assert 'client_secret_available' in info
    
    def test_Gmail接続テスト(self, oauth2_manager):
        """
        Gmail接続テストをテスト
        """
        account_id = "test-account"
        
        # 認証情報がない場合
        success, message = oauth2_manager.test_gmail_connection(account_id)
        assert success == False
        assert "認証情報が見つかりません" in message


class TestAccountOAuth2Integration:
    """
    AccountクラスとOAuth2機能の統合テスト
    """
    
    def test_oauth2要求判定(self):
        """
        OAuth2要求の判定をテスト
        """
        # Gmailアカウント
        gmail_account = Account(
            name="Gmail Test",
            email_address="test@gmail.com",
            account_type=AccountType.GMAIL
        )
        gmail_account.apply_preset_settings()
        
        assert gmail_account.requires_oauth2() == True
        assert gmail_account.auth_type == AuthType.OAUTH2
        
        # 通常のIMAPアカウント
        imap_account = Account(
            name="IMAP Test",
            email_address="test@example.com",
            account_type=AccountType.IMAP,
            auth_type=AuthType.PASSWORD
        )
        
        assert imap_account.requires_oauth2() == False
    
    def test_oauth2スコープ要求(self):
        """
        OAuth2スコープ要求の取得をテスト
        """
        # Gmailアカウント
        gmail_account = Account(
            name="Gmail Test",
            email_address="test@gmail.com",
            account_type=AccountType.GMAIL
        )
        
        scopes = gmail_account.get_oauth2_scope_requirements()
        assert len(scopes) > 0
        assert 'https://www.googleapis.com/auth/gmail.readonly' in scopes
        assert 'https://www.googleapis.com/auth/gmail.send' in scopes
        
        # 通常のIMAPアカウント
        imap_account = Account(
            name="IMAP Test", 
            email_address="test@example.com",
            account_type=AccountType.IMAP
        )
        
        scopes = imap_account.get_oauth2_scope_requirements()
        assert len(scopes) == 0
    
    def test_認証表示名取得(self):
        """
        認証表示名の取得をテスト
        """
        # OAuth2アカウント
        oauth2_account = Account(
            name="OAuth2 Test",
            email_address="test@example.com",
            auth_type=AuthType.OAUTH2
        )
        
        display_name = oauth2_account.get_authentication_display_name()
        assert display_name == "OAuth2認証"
        
        # パスワードアカウント
        password_account = Account(
            name="Password Test",
            email_address="test@example.com",
            auth_type=AuthType.PASSWORD
        )
        
        display_name = password_account.get_authentication_display_name()
        assert display_name == "パスワード認証"
    
    def test_アカウント文字列表現(self):
        """
        アカウントの文字列表現をテスト
        """
        gmail_account = Account(
            name="Gmail Test",
            email_address="test@gmail.com",
            account_type=AccountType.GMAIL
        )
        gmail_account.apply_preset_settings()
        
        account_str = str(gmail_account)
        assert "Gmail Test" in account_str
        assert "test@gmail.com" in account_str
        assert "gmail" in account_str
        assert "OAuth2認証" in account_str
        assert "有効" in account_str


if __name__ == "__main__":
    """
    テストスクリプトとして直接実行された場合
    """
    pytest.main([__file__, "-v"])