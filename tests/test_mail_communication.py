# -*- coding: utf-8 -*-
"""
メール通信機能のテストモジュール

MailMessage、各種クライアント、ファクトリークラスの動作確認テストを提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
from datetime import datetime
import email
from email.mime.text import MIMEText

# テスト用にプロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mail.account import Account, AccountType, AuthType
from src.mail.mail_message import MailMessage, MessageFlag, MailAttachment
from src.mail.imap_client import IMAPClient
from src.mail.smtp_client import SMTPClient
from src.mail.pop_client import POPClient
from src.mail.mail_client_factory import MailClientFactory, ClientType


class TestMailMessage:
    """
    MailMessageクラスのテストケース
    """
    
    def test_メッセージ初期化_デフォルト値(self):
        """
        メールメッセージのデフォルト初期化をテスト
        """
        message = MailMessage()
        
        # デフォルト値の確認
        assert message.message_id != ""  # UUIDが生成されている
        assert message.subject == ""
        assert message.sender == ""
        assert message.recipients == []
        assert message.body_text == ""
        assert message.body_html == ""
        assert message.attachments == []
        assert message.flags == []
        assert message.folder == "INBOX"
        assert message.priority == "normal"
        assert isinstance(message.date_received, datetime)
    
    def test_メッセージ初期化_値指定(self):
        """
        値を指定したメールメッセージの初期化をテスト
        """
        recipients = ["test1@example.com", "test2@example.com"]
        message = MailMessage(
            subject="テストメール",
            sender="sender@example.com",
            recipients=recipients,
            body_text="これはテストメールです。",
            priority="high"
        )
        
        assert message.subject == "テストメール"
        assert message.sender == "sender@example.com"
        assert message.recipients == recipients
        assert message.body_text == "これはテストメールです。"
        assert message.priority == "high"
    
    def test_フラグ操作(self):
        """
        メッセージフラグの操作をテスト
        """
        message = MailMessage()
        
        # 初期状態は未読
        assert not message.is_read()
        assert not message.has_flag(MessageFlag.SEEN)
        
        # 既読にマーク
        message.mark_as_read()
        assert message.is_read()
        assert message.has_flag(MessageFlag.SEEN)
        
        # 未読に戻す
        message.mark_as_unread()
        assert not message.is_read()
        assert not message.has_flag(MessageFlag.SEEN)
        
        # 重要マーク
        assert not message.is_flagged()
        message.add_flag(MessageFlag.FLAGGED)
        assert message.is_flagged()
        
        message.remove_flag(MessageFlag.FLAGGED)
        assert not message.is_flagged()
    
    def test_添付ファイル操作(self):
        """
        添付ファイル情報の操作をテスト
        """
        message = MailMessage()
        
        # 初期状態
        assert not message.has_attachments()
        assert message.get_attachment_count() == 0
        
        # 添付ファイルを追加
        attachment1 = MailAttachment(
            filename="document.pdf",
            content_type="application/pdf",
            size=1024
        )
        attachment2 = MailAttachment(
            filename="image.jpg",
            content_type="image/jpeg",
            size=2048,
            is_inline=True
        )
        
        message.attachments.append(attachment1)
        message.attachments.append(attachment2)
        
        assert message.has_attachments()
        assert message.get_attachment_count() == 2
    
    def test_本文プレビュー取得(self):
        """
        本文プレビューテキストの取得をテスト
        """
        # テキスト本文のみ
        message1 = MailMessage(body_text="これは長いテストメッセージです。" * 10)
        preview1 = message1.get_body_preview(50)
        assert len(preview1) <= 53  # "..." を含めて
        assert preview1.endswith("...")
        
        # HTML本文のみ
        message2 = MailMessage(body_html="<p>HTMLメッセージ</p><br><strong>太字テキスト</strong>")
        preview2 = message2.get_body_preview()
        assert "HTMLメッセージ" in preview2
        assert "太字テキスト" in preview2
        assert "<p>" not in preview2  # HTMLタグは除去される
        
        # 本文なし
        message3 = MailMessage()
        preview3 = message3.get_body_preview()
        assert preview3 == "[本文なし]"
    
    def test_emailメッセージからの変換(self):
        """
        email.messageからMailMessageへの変換をテスト
        """
        # テスト用のemail.messageを作成（英語で問題を回避）
        email_text = """From: sender@example.com
To: recipient@example.com
Subject: Test Subject
Date: Wed, 01 Jul 2025 12:00:00 +0900
Message-ID: <test@example.com>

This is a test message body.
"""
        
        email_msg = email.message_from_string(email_text, policy=email.policy.default)
        
        # MailMessageに変換
        mail_message = MailMessage.from_email_message(
            email_msg,
            account_id="test-account",
            folder="INBOX",
            uid="123"
        )
        
        assert mail_message.subject == "Test Subject"
        assert mail_message.sender == "sender@example.com"
        assert "recipient@example.com" in mail_message.recipients
        assert mail_message.body_text.strip() == "This is a test message body."
        assert mail_message.account_id == "test-account"
        assert mail_message.folder == "INBOX"
        assert mail_message.uid == "123"
    
    def test_辞書変換(self):
        """
        メッセージ情報の辞書変換をテスト
        """
        message = MailMessage(
            subject="テスト件名",
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            body_text="テスト本文",
            priority="high"
        )
        
        # 添付ファイルを追加
        attachment = MailAttachment(filename="test.txt", size=100)
        message.attachments.append(attachment)
        
        # 辞書に変換
        message_dict = message.to_dict()
        
        assert message_dict["subject"] == "テスト件名"
        assert message_dict["sender"] == "sender@example.com"
        assert message_dict["recipients"] == ["recipient@example.com"]
        assert message_dict["body_text"] == "テスト本文"
        assert message_dict["priority"] == "high"
        assert message_dict["has_attachments"] == True
        assert len(message_dict["attachments"]) == 1
    
    def test_文字列表現(self):
        """
        メッセージの文字列表現をテスト
        """
        message = MailMessage(
            subject="重要なお知らせ",
            sender="info@example.com"
        )
        
        # 既読マークと重要マークを追加
        message.mark_as_read()
        message.add_flag(MessageFlag.FLAGGED)
        
        message_str = str(message)
        
        assert "重要なお知らせ" in message_str
        assert "info@example.com" in message_str
        assert "📖" in message_str  # 既読アイコン
        assert "⭐" in message_str  # 重要アイコン


class TestMailAttachment:
    """
    MailAttachmentクラスのテストケース
    """
    
    def test_添付ファイル初期化(self):
        """
        添付ファイル情報の初期化をテスト
        """
        attachment = MailAttachment(
            filename="document.pdf",
            content_type="application/pdf",
            size=2048,
            is_inline=False
        )
        
        assert attachment.filename == "document.pdf"
        assert attachment.content_type == "application/pdf"
        assert attachment.size == 2048
        assert attachment.is_inline == False
    
    def test_添付ファイル文字列表現(self):
        """
        添付ファイルの文字列表現をテスト
        """
        attachment = MailAttachment(
            filename="image.jpg",
            content_type="image/jpeg",
            size=1024,
            is_inline=True
        )
        
        attachment_str = str(attachment)
        
        assert "image.jpg" in attachment_str
        assert "image/jpeg" in attachment_str
        assert "1,024バイト" in attachment_str
        assert "(インライン)" in attachment_str


class TestMailClientFactory:
    """
    MailClientFactoryクラスのテストケース
    """
    
    def test_IMAPクライアント生成(self):
        """
        IMAPクライアントの生成をテスト
        """
        # Gmailアカウント
        gmail_account = Account(
            name="Gmail Account",
            email_address="test@gmail.com",
            account_type=AccountType.GMAIL
        )
        gmail_account.apply_preset_settings()
        
        imap_client = MailClientFactory.create_imap_client(gmail_account)
        assert imap_client is not None
        assert isinstance(imap_client, IMAPClient)
        assert imap_client.account == gmail_account
    
    def test_SMTPクライアント生成(self):
        """
        SMTPクライアントの生成をテスト
        """
        # Gmailアカウント
        gmail_account = Account(
            name="Gmail Account",
            email_address="test@gmail.com",
            account_type=AccountType.GMAIL
        )
        gmail_account.apply_preset_settings()
        
        smtp_client = MailClientFactory.create_smtp_client(gmail_account)
        assert smtp_client is not None
        assert isinstance(smtp_client, SMTPClient)
        assert smtp_client.account == gmail_account
    
    def test_POPクライアント生成(self):
        """
        POPクライアントの生成をテスト
        """
        # POP3アカウント
        pop_account = Account(
            name="POP3 Account",
            email_address="test@example.com",
            account_type=AccountType.POP3
        )
        # POP3設定を手動で設定
        pop_account.settings.incoming_server = "pop.example.com"
        pop_account.settings.incoming_port = 995
        pop_account.settings.incoming_security = "SSL"
        
        pop_client = MailClientFactory.create_pop_client(pop_account)
        assert pop_client is not None
        assert isinstance(pop_client, POPClient)
        assert pop_client.account == pop_account
    
    def test_受信クライアント生成(self):
        """
        受信用クライアントの生成をテスト
        """
        # Gmailアカウント → IMAPクライアント
        gmail_account = Account(
            name="Gmail Account",
            email_address="test@gmail.com",
            account_type=AccountType.GMAIL
        )
        gmail_account.apply_preset_settings()
        
        receive_client = MailClientFactory.create_receive_client(gmail_account)
        assert receive_client is not None
        assert isinstance(receive_client, IMAPClient)
        
        # POP3アカウント → POPクライアント
        pop_account = Account(
            name="POP3 Account",
            email_address="test@example.com",
            account_type=AccountType.POP3
        )
        pop_account.settings.incoming_server = "pop.example.com"
        pop_account.settings.incoming_port = 995
        pop_account.settings.incoming_security = "SSL"
        
        receive_client = MailClientFactory.create_receive_client(pop_account)
        assert receive_client is not None
        assert isinstance(receive_client, POPClient)
    
    def test_送信クライアント生成(self):
        """
        送信用クライアントの生成をテスト
        """
        gmail_account = Account(
            name="Gmail Account",
            email_address="test@gmail.com",
            account_type=AccountType.GMAIL
        )
        gmail_account.apply_preset_settings()
        
        send_client = MailClientFactory.create_send_client(gmail_account)
        assert send_client is not None
        assert isinstance(send_client, SMTPClient)
    
    def test_サポートされているクライアントタイプ取得(self):
        """
        サポートされているクライアントタイプの取得をテスト
        """
        # Gmailアカウント
        gmail_account = Account(
            name="Gmail Account",
            email_address="test@gmail.com",
            account_type=AccountType.GMAIL
        )
        gmail_account.apply_preset_settings()
        
        supported_types = MailClientFactory.get_supported_client_types(gmail_account)
        assert ClientType.IMAP in supported_types
        assert ClientType.SMTP in supported_types
        
        # POP3アカウント
        pop_account = Account(
            name="POP3 Account",
            email_address="test@example.com",
            account_type=AccountType.POP3
        )
        pop_account.settings.incoming_server = "pop.example.com"
        pop_account.settings.incoming_port = 995
        pop_account.settings.incoming_security = "SSL"
        pop_account.settings.outgoing_server = "smtp.example.com"
        pop_account.settings.outgoing_port = 587
        pop_account.settings.outgoing_security = "STARTTLS"
        
        supported_types = MailClientFactory.get_supported_client_types(pop_account)
        assert ClientType.POP3 in supported_types
        assert ClientType.SMTP in supported_types
    
    def test_無効な設定でのクライアント生成(self):
        """
        無効な設定でのクライアント生成失敗をテスト
        """
        # サーバー情報が不完全なアカウント
        invalid_account = Account(
            name="Invalid Account",
            email_address="test@example.com",
            account_type=AccountType.IMAP
        )
        # サーバー設定を空のまま
        
        imap_client = MailClientFactory.create_imap_client(invalid_account)
        assert imap_client is None
        
        smtp_client = MailClientFactory.create_smtp_client(invalid_account)
        assert smtp_client is None


if __name__ == "__main__":
    """
    テストスクリプトとして直接実行された場合
    """
    pytest.main([__file__, "-v"])