# -*- coding: utf-8 -*-
"""
GUI機能のテストモジュール

WabiMailのGUI関連機能の動作確認テストを提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import tkinter as tk
from unittest.mock import Mock, patch

# テスト用にプロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ui.main_window import WabiMailMainWindow
from src.mail.account import Account, AccountType, AuthType
from src.mail.mail_message import MailMessage, MessageFlag


class TestWabiMailMainWindow:
    """
    WabiMailMainWindowクラスのテストケース
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
    def mock_root(self):
        """
        モックのTkinterルートウィンドウを作成
        """
        root = Mock(spec=tk.Tk)
        root.winfo_screenwidth.return_value = 1920
        root.winfo_screenheight.return_value = 1080
        root.winfo_width.return_value = 1200
        root.winfo_height.return_value = 750
        return root
    
    def test_main_window_初期化(self, mock_root):
        """
        メインウィンドウの初期化をテスト
        """
        with patch('tkinter.Tk', return_value=mock_root):
            with patch('src.ui.main_window.ttk.Style'):
                # WabiMailMainWindowのインスタンス化をテスト
                # 実際のTkinterウィンドウは作成せずにモックを使用
                app = WabiMailMainWindow()
                
                # 基本的な属性が初期化されているか確認
                assert app.root == mock_root
                assert app.config is not None
                assert app.account_manager is not None
                assert app.current_account is None
                assert app.current_folder == "INBOX"
                assert app.current_messages == []
                assert app.selected_message is None
    
    def test_sample_messages_作成(self, mock_root):
        """
        サンプルメッセージの作成をテスト
        """
        with patch('tkinter.Tk', return_value=mock_root):
            with patch('src.ui.main_window.ttk.Style'):
                app = WabiMailMainWindow()
                
                # テスト用アカウントを設定
                test_account = Account(
                    name="テストアカウント",
                    email_address="test@example.com",
                    account_type=AccountType.GMAIL
                )
                app.current_account = test_account
                
                # サンプルメッセージを作成
                messages = app._create_sample_messages()
                
                # メッセージが作成されているか確認
                assert len(messages) == 3
                assert all(isinstance(msg, MailMessage) for msg in messages)
                
                # 最初のメッセージの内容確認
                first_message = messages[0]
                assert "WabiMail" in first_message.subject
                assert first_message.is_flagged()  # 重要マーク付き
                assert test_account.email_address in first_message.recipients
    
    def test_account_tree_追加(self, mock_root):
        """
        アカウントツリーへの追加をテスト
        """
        with patch('tkinter.Tk', return_value=mock_root):
            with patch('src.ui.main_window.ttk.Style'):
                # TreeviewのモックとWabiMailMainWindowの組み合わせ
                mock_treeview = Mock()
                mock_treeview.insert.return_value = "item1"
                
                with patch('src.ui.main_window.ttk.Treeview', return_value=mock_treeview):
                    app = WabiMailMainWindow()
                    app.account_tree = mock_treeview
                    
                    # テストアカウント
                    test_account = Account(
                        name="Gmail Test",
                        email_address="test@gmail.com",
                        account_type=AccountType.GMAIL
                    )
                    
                    # アカウントをツリーに追加
                    app._add_account_to_tree(test_account)
                    
                    # insertが呼ばれたか確認
                    assert mock_treeview.insert.call_count >= 6  # アカウント + 5つのフォルダ
    
    def test_status_更新(self, mock_root):
        """
        ステータス更新をテスト
        """
        with patch('tkinter.Tk', return_value=mock_root):
            with patch('src.ui.main_window.ttk.Style'):
                app = WabiMailMainWindow()
                
                # モックのステータスラベル
                mock_status_label = Mock()
                app.status_label = mock_status_label
                
                # ステータス更新
                test_message = "テストステータスメッセージ"
                app._update_status(test_message)
                
                # configメソッドが正しい引数で呼ばれたか確認
                mock_status_label.config.assert_called_once_with(text=test_message)
    
    def test_connection_status_更新(self, mock_root):
        """
        接続状態更新をテスト
        """
        with patch('tkinter.Tk', return_value=mock_root):
            with patch('src.ui.main_window.ttk.Style'):
                app = WabiMailMainWindow()
                
                # モックの接続状態ラベル
                mock_connection_label = Mock()
                app.connection_label = mock_connection_label
                
                # 接続状態更新
                test_status = "接続中..."
                app._update_connection_status(test_status)
                
                # configメソッドが正しい引数で呼ばれたか確認
                mock_connection_label.config.assert_called_once_with(text=test_status)
    
    def test_message_display(self, mock_root):
        """
        メッセージ表示をテスト
        """
        with patch('tkinter.Tk', return_value=mock_root):
            with patch('src.ui.main_window.ttk.Style'):
                app = WabiMailMainWindow()
                
                # モックのテキストウィジェット
                mock_text = Mock()
                app.message_text = mock_text
                
                # テストメッセージ
                test_message = MailMessage(
                    subject="テスト件名",
                    sender="sender@example.com",
                    recipients=["recipient@example.com"],
                    body_text="テスト本文"
                )
                
                # メッセージ表示
                app._display_message(test_message)
                
                # テキストウィジェットのメソッドが呼ばれたか確認
                mock_text.config.assert_called()
                mock_text.delete.assert_called()
                mock_text.insert.assert_called()
    
    def test_message_list_更新(self, mock_root):
        """
        メッセージリスト更新をテスト
        """
        with patch('tkinter.Tk', return_value=mock_root):
            with patch('src.ui.main_window.ttk.Style'):
                app = WabiMailMainWindow()
                
                # モックのTreeviewとラベル
                mock_message_list = Mock()
                mock_message_list.get_children.return_value = []
                mock_title_label = Mock()
                
                app.message_list = mock_message_list
                app.list_title_label = mock_title_label
                
                # テストメッセージリスト
                test_messages = [
                    MailMessage(
                        subject="メッセージ1",
                        sender="sender1@example.com",
                        recipients=["recipient@example.com"]
                    ),
                    MailMessage(
                        subject="メッセージ2",
                        sender="sender2@example.com", 
                        recipients=["recipient@example.com"]
                    )
                ]
                test_messages[0].mark_as_read()  # 1つ目を既読に
                test_messages[1].add_flag(MessageFlag.FLAGGED)  # 2つ目を重要に
                
                # メッセージリスト更新
                app._update_message_list(test_messages)
                
                # insertが呼ばれたか確認（2つのメッセージ分）
                assert mock_message_list.insert.call_count == 2
                
                # タイトルが更新されたか確認
                mock_title_label.config.assert_called_once()
    
    def test_wabi_sabi_style_設定(self, mock_root):
        """
        侘び寂びスタイル設定をテスト
        """
        with patch('tkinter.Tk', return_value=mock_root):
            with patch('src.ui.main_window.ttk.Style') as mock_style_class:
                mock_style = Mock()
                mock_style_class.return_value = mock_style
                
                app = WabiMailMainWindow()
                
                # スタイル設定メソッドが呼ばれているか確認
                mock_style.configure.assert_called()
                mock_style.map.assert_called()
                
                # ルートウィンドウの背景色が設定されているか確認
                mock_root.configure.assert_called_with(bg="#fefefe")
    
    def test_pane_size_調整(self, mock_root):
        """
        ペインサイズ調整をテスト
        """
        with patch('tkinter.Tk', return_value=mock_root):
            with patch('src.ui.main_window.ttk.Style'):
                app = WabiMailMainWindow()
                
                # モックのPanedWindow
                mock_main_paned = Mock()
                mock_content_paned = Mock()
                app.main_paned = mock_main_paned
                app.content_paned = mock_content_paned
                
                # ペインサイズ調整
                app._adjust_pane_sizes()
                
                # sashposメソッドが呼ばれたか確認
                mock_main_paned.sashpos.assert_called()
                mock_content_paned.sashpos.assert_called()


class TestGUIIntegration:
    """
    GUI統合テスト
    """
    
    def test_menu_actions(self, mock_root=None):
        """
        メニューアクションをテスト
        """
        # 実際のGUI操作は統合テストで確認
        # ここでは基本的なメソッド存在確認
        app_methods = [
            '_create_new_message',
            '_add_account', 
            '_refresh_current_folder',
            '_expand_all_folders',
            '_collapse_all_folders',
            '_reply_message',
            '_forward_message',
            '_delete_message',
            '_show_about'
        ]
        
        # メソッドが存在するか確認
        for method_name in app_methods:
            assert hasattr(WabiMailMainWindow, method_name)
    
    def test_event_handlers(self):
        """
        イベントハンドラーをテスト
        """
        # イベントハンドラーメソッドの存在確認
        event_handlers = [
            '_on_account_tree_select',
            '_on_account_tree_double_click',
            '_on_message_select',
            '_on_message_double_click',
            '_on_search',
            '_on_closing'
        ]
        
        for handler_name in event_handlers:
            assert hasattr(WabiMailMainWindow, handler_name)


if __name__ == "__main__":
    """
    テストスクリプトとして直接実行された場合
    """
    pytest.main([__file__, "-v"])