# -*- coding: utf-8 -*-
"""
メール作成ウィンドウテストモジュール

ComposeWindowクラスの機能をテストします。
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tempfile
import os
from pathlib import Path

# テスト対象をインポート
from src.ui.compose_window import ComposeWindow, show_compose_window
from src.mail.account import Account, AccountType, AuthType, AccountSettings
from src.mail.mail_message import MailMessage, MailAttachment, MessageFlag


class TestComposeWindow(unittest.TestCase):
    """メール作成ウィンドウテストクラス"""
    
    def setUp(self):
        """テスト前の準備"""
        # テスト用のアカウントを作成
        self.test_account = Account(
            account_id="test_account_001",
            name="テストアカウント",
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
        
        # テスト用のメッセージを作成
        self.test_message = MailMessage(
            subject="テストメッセージ",
            sender="sender@example.com",
            recipients=["test@example.com"],
            body_text="これはテスト用のメッセージです。",
            date_received=datetime.now()
        )
        
        # テスト用のGUIルート（非表示）
        self.root = None
        self.compose_window = None
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if self.compose_window and hasattr(self.compose_window, 'window'):
            if self.compose_window.window:
                self.compose_window.window.destroy()
        
        if self.root:
            self.root.destroy()
    
    def test_compose_window_initialization(self):
        """メール作成ウィンドウの初期化テスト"""
        # GUI環境でのみテスト実行
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # ウィンドウを隠す
            
            # 新規メール作成ウィンドウ
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account,
                message_type="new"
            )
            
            # 基本属性の確認
            self.assertEqual(self.compose_window.account, self.test_account)
            self.assertEqual(self.compose_window.message_type, "new")
            self.assertIsNone(self.compose_window.original_message)
            self.assertIsNotNone(self.compose_window.window)
            self.assertEqual(len(self.compose_window.attachments), 0)
            
        except tk.TclError:
            # ヘッドレス環境ではスキップ
            self.skipTest("GUI環境が利用できません")
    
    def test_reply_window_initialization(self):
        """返信ウィンドウの初期化テスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            # 返信ウィンドウ
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account,
                message_type="reply",
                original_message=self.test_message
            )
            
            # 返信設定の確認
            self.assertEqual(self.compose_window.message_type, "reply")
            self.assertEqual(self.compose_window.original_message, self.test_message)
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    def test_forward_window_initialization(self):
        """転送ウィンドウの初期化テスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            # 転送ウィンドウ
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account,
                message_type="forward",
                original_message=self.test_message
            )
            
            # 転送設定の確認
            self.assertEqual(self.compose_window.message_type, "forward")
            self.assertEqual(self.compose_window.original_message, self.test_message)
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    def test_create_quote_text(self):
        """引用テキスト作成テスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account
            )
            
            # 引用テキストを作成
            quote_text = self.compose_window._create_quote_text(self.test_message)
            
            # 引用形式の確認
            self.assertIn(self.test_message.sender, quote_text)
            self.assertIn("> これはテスト用のメッセージです。", quote_text)
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    def test_create_forward_text(self):
        """転送テキスト作成テスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account
            )
            
            # 転送テキストを作成
            forward_text = self.compose_window._create_forward_text(self.test_message)
            
            # 転送形式の確認
            self.assertIn("---------- 転送メッセージ ----------", forward_text)
            self.assertIn(f"差出人: {self.test_message.sender}", forward_text)
            self.assertIn(f"件名: {self.test_message.subject}", forward_text)
            self.assertIn(self.test_message.body_text, forward_text)
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    def test_text_to_html_conversion(self):
        """テキストからHTML変換テスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account
            )
            
            # テキストをHTMLに変換
            text = "これはテストです。\n改行があります。"
            html = self.compose_window._text_to_html(text)
            
            # HTML形式の確認
            self.assertIn("<!DOCTYPE html>", html)
            self.assertIn("<body>", html)
            self.assertIn("これはテストです。<br>", html)
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    def test_html_to_text_conversion(self):
        """HTMLからテキスト変換テスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account
            )
            
            # HTMLをテキストに変換
            html = "<p>これは<strong>テスト</strong>です。</p><br><p>改行があります。</p>"
            text = self.compose_window._html_to_text(html)
            
            # テキスト形式の確認
            self.assertNotIn("<p>", text)
            self.assertNotIn("<strong>", text)
            self.assertIn("これはテストです。", text)
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    def test_file_icon_selection(self):
        """ファイルアイコン選択テスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account
            )
            
            # 各ファイルタイプのアイコン確認
            self.assertEqual(self.compose_window._get_file_icon("image/jpeg"), "🖼️")
            self.assertEqual(self.compose_window._get_file_icon("text/plain"), "📄")
            self.assertEqual(self.compose_window._get_file_icon("application/pdf"), "📕")
            self.assertEqual(self.compose_window._get_file_icon("audio/mp3"), "🎵")
            self.assertEqual(self.compose_window._get_file_icon("video/mp4"), "🎬")
            self.assertEqual(self.compose_window._get_file_icon("application/zip"), "📦")
            self.assertEqual(self.compose_window._get_file_icon("application/octet-stream"), "📎")
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    def test_file_size_formatting(self):
        """ファイルサイズフォーマットテスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account
            )
            
            # 各サイズのフォーマット確認
            self.assertEqual(self.compose_window._format_file_size(0), "0 B")
            self.assertEqual(self.compose_window._format_file_size(512), "512 B")
            self.assertEqual(self.compose_window._format_file_size(1024), "1.0 KB")
            self.assertEqual(self.compose_window._format_file_size(1048576), "1.0 MB")
            self.assertEqual(self.compose_window._format_file_size(1073741824), "1.0 GB")
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    @patch('src.ui.compose_window.MailClientFactory')
    def test_message_validation(self, mock_factory):
        """メッセージ検証テスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account
            )
            
            # 空の宛先での検証（失敗するはず）
            self.compose_window.to_entry.delete(0, tk.END)
            self.compose_window.subject_entry.insert(0, "テスト件名")
            self.compose_window.body_text.insert(tk.END, "テスト本文")
            
            result = self.compose_window._validate_message()
            self.assertFalse(result)
            
            # 正常な入力での検証（成功するはず）
            self.compose_window.to_entry.insert(0, "test@example.com")
            
            result = self.compose_window._validate_message()
            self.assertTrue(result)
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    def test_create_message_data(self):
        """メッセージデータ作成テスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account
            )
            
            # フォームに入力
            self.compose_window.to_entry.insert(0, "recipient@example.com")
            self.compose_window.cc_entry.insert(0, "cc@example.com")
            self.compose_window.subject_entry.insert(0, "テスト件名")
            self.compose_window.body_text.insert(tk.END, "テスト本文")
            
            # メッセージデータを作成
            message_data = self.compose_window._create_message_data()
            
            # データの確認
            self.assertEqual(message_data.subject, "テスト件名")
            self.assertIn("recipient@example.com", message_data.recipients)
            self.assertIn("cc@example.com", message_data.cc_recipients)
            self.assertEqual(message_data.body_text, "テスト本文")
            self.assertEqual(message_data.account_id, self.test_account.account_id)
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    def test_show_compose_window_function(self):
        """show_compose_window関数テスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            # 新規メール作成
            window = show_compose_window(
                parent=self.root,
                account=self.test_account,
                message_type="new"
            )
            
            self.assertIsNotNone(window)
            self.assertIsInstance(window, ComposeWindow)
            
            # ウィンドウを閉じる
            if window and window.window:
                window.window.destroy()
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    def test_attachment_functionality(self):
        """添付ファイル機能テスト"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            
            self.compose_window = ComposeWindow(
                parent=self.root,
                account=self.test_account
            )
            
            # テスト用の添付ファイルを作成
            test_attachment = MailAttachment(
                filename="test.txt",
                content_type="text/plain",
                size=1024,
                data=b"test content"
            )
            
            # 添付ファイルを追加
            self.compose_window.attachments.append(test_attachment)
            self.compose_window._update_attachments_display()
            
            # 添付ファイルの確認
            self.assertEqual(len(self.compose_window.attachments), 1)
            self.assertEqual(self.compose_window.attachments[0].filename, "test.txt")
            
            # 添付ファイルを削除
            self.compose_window._remove_attachment(0)
            self.assertEqual(len(self.compose_window.attachments), 0)
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")


class TestComposeWindowIntegration(unittest.TestCase):
    """メール作成ウィンドウ統合テストクラス"""
    
    def setUp(self):
        """テスト前の準備"""
        self.test_account = Account(
            account_id="integration_test_001",
            name="統合テストアカウント",
            email_address="integration@example.com",
            account_type=AccountType.IMAP,
            auth_type=AuthType.PASSWORD,
            settings=AccountSettings(
                incoming_server="imap.example.com",
                incoming_port=993,
                incoming_security="SSL",
                outgoing_server="smtp.example.com",
                outgoing_port=587,
                outgoing_security="STARTTLS",
                requires_auth=True
            )
        )
    
    def test_compose_reply_integration(self):
        """返信統合テスト"""
        try:
            root = tk.Tk()
            root.withdraw()
            
            # 元メッセージ
            original_message = MailMessage(
                subject="元のメッセージ",
                sender="original@example.com",
                recipients=["integration@example.com"],
                body_text="これは元のメッセージです。",
                date_received=datetime.now()
            )
            
            # 返信ウィンドウを作成
            compose_window = ComposeWindow(
                parent=root,
                account=self.test_account,
                message_type="reply",
                original_message=original_message
            )
            
            # 返信設定の確認
            to_content = compose_window.to_entry.get()
            subject_content = compose_window.subject_entry.get()
            body_content = compose_window.body_text.get("1.0", tk.END)
            
            self.assertEqual(to_content, "original@example.com")
            self.assertTrue(subject_content.startswith("Re:"))
            self.assertIn("> これは元のメッセージです。", body_content)
            
            # クリーンアップ
            compose_window.window.destroy()
            root.destroy()
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")
    
    def test_compose_forward_integration(self):
        """転送統合テスト"""
        try:
            root = tk.Tk()
            root.withdraw()
            
            # 元メッセージ（添付ファイル付き）
            original_message = MailMessage(
                subject="転送元メッセージ",
                sender="forward@example.com",
                recipients=["integration@example.com"],
                body_text="これは転送元のメッセージです。",
                date_received=datetime.now()
            )
            
            # 添付ファイルを追加
            attachment = MailAttachment(
                filename="document.pdf",
                content_type="application/pdf",
                size=2048
            )
            original_message.attachments.append(attachment)
            
            # 転送ウィンドウを作成
            compose_window = ComposeWindow(
                parent=root,
                account=self.test_account,
                message_type="forward",
                original_message=original_message
            )
            
            # 転送設定の確認
            subject_content = compose_window.subject_entry.get()
            body_content = compose_window.body_text.get("1.0", tk.END)
            
            self.assertTrue(subject_content.startswith("Fwd:"))
            self.assertIn("---------- 転送メッセージ ----------", body_content)
            self.assertIn("forward@example.com", body_content)
            self.assertEqual(len(compose_window.attachments), 1)
            self.assertEqual(compose_window.attachments[0].filename, "document.pdf")
            
            # クリーンアップ
            compose_window.window.destroy()
            root.destroy()
            
        except tk.TclError:
            self.skipTest("GUI環境が利用できません")


if __name__ == '__main__':
    # テスト実行
    unittest.main(verbosity=2)