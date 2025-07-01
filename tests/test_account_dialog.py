# -*- coding: utf-8 -*-
"""
アカウント設定ダイアログのテストモジュール

AccountDialogクラスと関連機能の動作確認テストを提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock

# テスト用にプロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ui.account_dialog import AccountDialog, show_account_dialog
from src.mail.account import Account, AccountType, AuthType
from src.mail.account_manager import AccountManager


class TestAccountDialog:
    """
    AccountDialogクラスのテストケース
    """
    
    @pytest.fixture
    def root_window(self):
        """
        テスト用のルートウィンドウを作成
        """
        root = tk.Tk()
        root.withdraw()  # ウィンドウを非表示
        yield root
        root.destroy()
    
    @pytest.fixture
    def temp_dir(self):
        """
        テスト用一時ディレクトリを作成
        """
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_account(self):
        """
        テスト用サンプルアカウントを作成
        """
        account = Account(
            name="テストアカウント",
            email_address="test@example.com",
            account_type=AccountType.IMAP,
            auth_type=AuthType.PASSWORD
        )
        account.apply_preset_settings()
        return account
    
    def test_ダイアログ作成_新規モード(self, root_window):
        """
        新規アカウント作成モードでのダイアログ作成をテスト
        """
        dialog = AccountDialog(root_window)
        
        assert dialog.account is None
        assert dialog.parent == root_window
        assert dialog.dialog is not None
        assert dialog.result_account is None
        
        # 初期値の確認
        assert dialog.account_type_var.get() == "gmail"
        assert dialog.incoming_port_var.get() == 993
        assert dialog.outgoing_port_var.get() == 587
        
        dialog._close_dialog()
    
    def test_ダイアログ作成_編集モード(self, root_window, sample_account):
        """
        アカウント編集モードでのダイアログ作成をテスト
        """
        dialog = AccountDialog(root_window, account=sample_account)
        
        assert dialog.account == sample_account
        assert dialog.name_var.get() == sample_account.name
        assert dialog.email_var.get() == sample_account.email_address
        assert dialog.account_type_var.get() == sample_account.account_type.value
        
        dialog._close_dialog()
    
    def test_アカウントタイプ変更_Gmail(self, root_window):
        """
        Gmailアカウントタイプへの変更をテスト
        """
        dialog = AccountDialog(root_window)
        
        dialog.account_type_var.set("gmail")
        dialog._on_account_type_change()
        
        # Gmail設定の確認
        assert dialog.incoming_server_var.get() == "imap.gmail.com"
        assert dialog.incoming_port_var.get() == 993
        assert dialog.incoming_security_var.get() == "SSL"
        assert dialog.outgoing_server_var.get() == "smtp.gmail.com"
        assert dialog.outgoing_port_var.get() == 587
        assert dialog.outgoing_security_var.get() == "STARTTLS"
        assert dialog.auth_type_var.get() == "oauth2"
        
        dialog._close_dialog()
    
    def test_アカウントタイプ変更_IMAP(self, root_window):
        """
        IMAPアカウントタイプへの変更をテスト
        """
        dialog = AccountDialog(root_window)
        
        dialog.account_type_var.set("imap")
        dialog._on_account_type_change()
        
        # IMAP設定の確認
        assert dialog.incoming_port_var.get() == 993
        assert dialog.incoming_security_var.get() == "SSL"
        assert dialog.outgoing_port_var.get() == 587
        assert dialog.outgoing_security_var.get() == "STARTTLS"
        assert dialog.auth_type_var.get() == "password"
        
        dialog._close_dialog()
    
    def test_アカウントタイプ変更_POP3(self, root_window):
        """
        POP3アカウントタイプへの変更をテスト
        """
        dialog = AccountDialog(root_window)
        
        dialog.account_type_var.set("pop3")
        dialog._on_account_type_change()
        
        # POP3設定の確認
        assert dialog.incoming_port_var.get() == 995
        assert dialog.incoming_security_var.get() == "SSL"
        assert dialog.outgoing_port_var.get() == 587
        assert dialog.outgoing_security_var.get() == "STARTTLS"
        assert dialog.auth_type_var.get() == "password"
        
        dialog._close_dialog()
    
    def test_メールアドレス変更_Gmail自動検出(self, root_window):
        """
        Gmailアドレス入力時の自動検出をテスト
        """
        dialog = AccountDialog(root_window)
        
        # Gmailアドレスを設定
        dialog.email_var.set("user@gmail.com")
        dialog._on_email_change(None)
        
        # 自動的にGmailタイプに変更されるか確認
        assert dialog.account_type_var.get() == "gmail"
        assert dialog.display_name_var.get() == "user"
        
        dialog._close_dialog()
    
    def test_メールアドレス変更_Googlemail自動検出(self, root_window):
        """
        GooglemailアドレスKeeperKeeperKeeperKeeperKeeperアドレス入力時の自動検出をテスト
        """
        dialog = AccountDialog(root_window)
        
        # Googlemailアドレスを設定
        dialog.email_var.set("user@googlemail.com")
        dialog._on_email_change(None)
        
        # 自動的にGmailタイプに変更されるか確認
        assert dialog.account_type_var.get() == "gmail"
        assert dialog.display_name_var.get() == "user"
        
        dialog._close_dialog()
    
    def test_フォームからアカウント作成_有効データ(self, root_window):
        """
        有効なフォームデータからのアカウント作成をテスト
        """
        dialog = AccountDialog(root_window)
        
        # フォームに有効なデータを設定
        dialog.name_var.set("テストアカウント")
        dialog.email_var.set("test@example.com")
        dialog.account_type_var.set("imap")
        dialog.auth_type_var.set("password")
        dialog.incoming_server_var.set("imap.example.com")
        dialog.incoming_port_var.set(993)
        dialog.outgoing_server_var.set("smtp.example.com")
        dialog.outgoing_port_var.set(587)
        
        account = dialog._create_account_from_form()
        
        assert account is not None
        assert account.name == "テストアカウント"
        assert account.email_address == "test@example.com"
        assert account.account_type == AccountType.IMAP
        assert account.auth_type == AuthType.PASSWORD
        assert account.settings.incoming_server == "imap.example.com"
        assert account.settings.incoming_port == 993
        
        dialog._close_dialog()
    
    def test_フォームからアカウント作成_無効データ(self, root_window):
        """
        無効なフォームデータでのアカウント作成をテスト
        """
        dialog = AccountDialog(root_window)
        
        # 空のアカウント名
        dialog.name_var.set("")
        dialog.email_var.set("test@example.com")
        
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            account = dialog._create_account_from_form()
            assert account is None
            mock_warning.assert_called_once()
        
        # 空のメールアドレス
        dialog.name_var.set("テストアカウント")
        dialog.email_var.set("")
        
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            account = dialog._create_account_from_form()
            assert account is None
            mock_warning.assert_called_once()
        
        dialog._close_dialog()
    
    @patch('src.auth.oauth2_manager.GmailOAuth2Manager.is_client_secret_available')
    def test_client_secret状態確認_利用可能(self, mock_is_available, root_window):
        """
        client_secret.jsonが利用可能な場合のテスト
        """
        mock_is_available.return_value = True
        
        dialog = AccountDialog(root_window)
        dialog._check_client_secret_status()
        
        assert dialog.oauth2_auth_button["state"] == "normal"
        
        dialog._close_dialog()
    
    @patch('src.auth.oauth2_manager.GmailOAuth2Manager.is_client_secret_available')
    def test_client_secret状態確認_利用不可能(self, mock_is_available, root_window):
        """
        client_secret.jsonが利用不可能な場合のテスト
        """
        mock_is_available.return_value = False
        
        dialog = AccountDialog(root_window)
        dialog._check_client_secret_status()
        
        assert dialog.oauth2_auth_button["state"] == "disabled"
        
        dialog._close_dialog()
    
    def test_タブ表示更新_Gmail(self, root_window):
        """
        Gmailアカウント時のタブ表示をテスト
        """
        dialog = AccountDialog(root_window)
        
        dialog.account_type_var.set("gmail")
        dialog._update_tab_visibility()
        
        # OAuth2タブが有効、手動設定タブが無効
        assert dialog.notebook.tab(0, "state") == "normal"
        assert dialog.notebook.tab(1, "state") == "disabled"
        
        dialog._close_dialog()
    
    def test_タブ表示更新_IMAP(self, root_window):
        """
        IMAPアカウント時のタブ表示をテスト
        """
        dialog = AccountDialog(root_window)
        
        dialog.account_type_var.set("imap")
        dialog._update_tab_visibility()
        
        # OAuth2タブが無効、手動設定タブが有効
        assert dialog.notebook.tab(0, "state") == "disabled"
        assert dialog.notebook.tab(1, "state") == "normal"
        
        dialog._close_dialog()


class TestAccountDialogIntegration:
    """
    AccountDialogの統合テスト
    """
    
    @pytest.fixture
    def root_window(self):
        """
        テスト用のルートウィンドウを作成
        """
        root = tk.Tk()
        root.withdraw()  # ウィンドウを非表示
        yield root
        root.destroy()
    
    @patch('src.mail.account_manager.AccountManager.add_account')
    def test_新規アカウント保存_成功(self, mock_add_account, root_window):
        """
        新規アカウント保存の成功ケースをテスト
        """
        mock_add_account.return_value = True
        
        dialog = AccountDialog(root_window)
        
        # フォームに有効なデータを設定
        dialog.name_var.set("テストアカウント")
        dialog.email_var.set("test@example.com")
        dialog.account_type_var.set("imap")
        
        with patch('tkinter.messagebox.showinfo') as mock_info:
            dialog._on_save()
            mock_info.assert_called_once()
            mock_add_account.assert_called_once()
        
        dialog._close_dialog()
    
    @patch('src.mail.account_manager.AccountManager.update_account')
    def test_既存アカウント更新_成功(self, mock_update_account, root_window):
        """
        既存アカウント更新の成功ケースをテスト
        """
        mock_update_account.return_value = True
        
        # 既存アカウント
        account = Account(
            name="既存アカウント",
            email_address="existing@example.com",
            account_type=AccountType.IMAP
        )
        
        dialog = AccountDialog(root_window, account=account)
        
        # アカウント名を変更
        dialog.name_var.set("更新されたアカウント")
        
        with patch('tkinter.messagebox.showinfo') as mock_info:
            dialog._on_save()
            mock_info.assert_called_once()
            mock_update_account.assert_called_once()
        
        dialog._close_dialog()
    
    def test_show_account_dialog関数(self, root_window):
        """
        show_account_dialog関数のテスト
        """
        # 新規作成モードでのテスト
        with patch.object(AccountDialog, 'show', return_value=None):
            result = show_account_dialog(root_window)
            assert result is None
        
        # サンプルアカウントを返すモック
        sample_account = Account(
            name="サンプル",
            email_address="sample@example.com",
            account_type=AccountType.IMAP
        )
        
        with patch.object(AccountDialog, 'show', return_value=sample_account):
            result = show_account_dialog(root_window)
            assert result == sample_account


if __name__ == "__main__":
    """
    テストスクリプトとして直接実行された場合
    """
    pytest.main([__file__, "-v"])