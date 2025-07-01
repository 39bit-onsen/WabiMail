# -*- coding: utf-8 -*-
"""
SMTPクライアントモジュール

WabiMailのSMTP接続とメール送信機能を提供します。
セキュアな送信、HTML/テキスト対応、添付ファイル処理等をサポートします。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from typing import List, Optional, Tuple, Dict, Any
import os
from pathlib import Path

from src.mail.account import Account
from src.mail.mail_message import MailMessage, MailAttachment
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class SMTPClient:
    """
    SMTPクライアントクラス
    
    SMTPサーバーへの接続とメール送信を管理します。
    セキュアな接続、エラーハンドリング、添付ファイル処理を提供します。
    
    Attributes:
        account (Account): 関連するメールアカウント
        _connection (Optional[smtplib.SMTP]): SMTP接続オブジェクト
        _is_connected (bool): 接続状態
    """
    
    def __init__(self, account: Account):
        """
        SMTPクライアントを初期化します
        
        Args:
            account: 関連するメールアカウント
        """
        self.account = account
        self._connection: Optional[smtplib.SMTP] = None
        self._is_connected = False
        
        logger.debug(f"SMTPクライアントを初期化しました: {account.email_address}")
    
    def connect(self) -> bool:
        """
        SMTPサーバーに接続します
        
        Returns:
            bool: 接続成功時True、失敗時False
        """
        try:
            logger.info(f"SMTPサーバーに接続中: {self.account.settings.outgoing_server}")
            
            # SSL/TLS設定に基づいて接続
            if self.account.settings.outgoing_security.upper() == "SSL":
                # SSL接続
                self._connection = smtplib.SMTP_SSL(
                    self.account.settings.outgoing_server,
                    self.account.settings.outgoing_port
                )
            else:
                # 平文接続またはSTARTTLS
                self._connection = smtplib.SMTP(
                    self.account.settings.outgoing_server,
                    self.account.settings.outgoing_port
                )
                
                # STARTTLSを試行
                if self.account.settings.outgoing_security.upper() == "STARTTLS":
                    self._connection.starttls()
            
            # 認証が必要な場合
            if self.account.settings.requires_auth:
                # 認証情報は実際のパスワード管理システムから取得する予定
                # 現在はテスト用にダミー認証
                logger.info("SMTP認証を実行中...")
                # self._connection.login(username, password)
            
            # テスト用の擬似接続成功
            self._is_connected = True
            
            logger.info(f"SMTPサーバーに接続しました: {self.account.email_address}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP接続エラー: {e}")
            self._is_connected = False
            return False
        except ssl.SSLError as e:
            logger.error(f"SSL接続エラー: {e}")
            self._is_connected = False
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            self._is_connected = False
            return False
    
    def disconnect(self):
        """
        SMTPサーバーから切断します
        """
        try:
            if self._connection and self._is_connected:
                self._connection.quit()
                logger.info("SMTPサーバーから切断しました")
        except Exception as e:
            logger.warning(f"切断中にエラーが発生しました: {e}")
        finally:
            self._connection = None
            self._is_connected = False
    
    def is_connected(self) -> bool:
        """
        接続状態を確認します
        
        Returns:
            bool: 接続中の場合True
        """
        return self._is_connected and self._connection is not None
    
    def send_message(self, message: MailMessage, 
                    attachment_paths: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        メールメッセージを送信します
        
        Args:
            message: 送信するメールメッセージ
            attachment_paths: 添付ファイルのパスリスト
            
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        if not self.is_connected():
            return False, "SMTP接続が確立されていません"
        
        try:
            # MIMEメッセージを構築
            mime_message = self._build_mime_message(message, attachment_paths)
            
            # 送信者と受信者を設定
            sender = message.sender or self.account.email_address
            recipients = message.recipients + message.cc_recipients + message.bcc_recipients
            
            if not recipients:
                return False, "受信者が指定されていません"
            
            # メッセージを送信
            self._connection.send_message(mime_message, sender, recipients)
            
            logger.info(f"メールを送信しました: {message.subject} (宛先: {len(recipients)}件)")
            return True, "送信成功"
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP送信エラー: {e}")
            return False, f"送信エラー: {e}"
        except Exception as e:
            logger.error(f"メール送信エラー: {e}")
            return False, f"予期しないエラー: {e}"
    
    def _build_mime_message(self, message: MailMessage, 
                           attachment_paths: Optional[List[str]] = None) -> MIMEMultipart:
        """
        MIMEメッセージを構築します
        
        Args:
            message: メールメッセージ
            attachment_paths: 添付ファイルのパスリスト
            
        Returns:
            MIMEMultipart: 構築されたMIMEメッセージ
        """
        # マルチパートメッセージを作成
        mime_msg = MIMEMultipart('alternative')
        
        # ヘッダー情報を設定
        mime_msg['Subject'] = message.subject
        mime_msg['From'] = formataddr((
            message.sender or self.account.display_name or self.account.email_address,
            message.sender or self.account.email_address
        ))
        mime_msg['To'] = ', '.join(message.recipients)
        
        if message.cc_recipients:
            mime_msg['Cc'] = ', '.join(message.cc_recipients)
        
        if message.reply_to:
            mime_msg['Reply-To'] = message.reply_to
        
        # 優先度設定
        if message.priority == 'high':
            mime_msg['X-Priority'] = '1'
            mime_msg['X-MSMail-Priority'] = 'High'
        elif message.priority == 'low':
            mime_msg['X-Priority'] = '5'
            mime_msg['X-MSMail-Priority'] = 'Low'
        
        # 返信関連ヘッダー
        if message.in_reply_to:
            mime_msg['In-Reply-To'] = message.in_reply_to
        
        if message.references:
            mime_msg['References'] = ' '.join(message.references)
        
        # WabiMail識別ヘッダー
        mime_msg['X-Mailer'] = 'WabiMail 0.1.0'
        
        # 本文を追加
        if message.body_text:
            text_part = MIMEText(message.body_text, 'plain', 'utf-8')
            mime_msg.attach(text_part)
        
        if message.body_html:
            html_part = MIMEText(message.body_html, 'html', 'utf-8')
            mime_msg.attach(html_part)
        
        # 本文がない場合はデフォルトテキストを追加
        if not message.body_text and not message.body_html:
            default_text = MIMEText("", 'plain', 'utf-8')
            mime_msg.attach(default_text)
        
        # 署名を追加
        if self.account.signature:
            signature_text = f"\n\n--\n{self.account.signature}"
            if message.body_text:
                # テキスト本文に署名を追加
                for part in mime_msg.walk():
                    if part.get_content_type() == 'text/plain':
                        current_text = part.get_content()
                        part.set_content(current_text + signature_text)
                        break
        
        # 添付ファイルを追加
        if attachment_paths:
            self._add_attachments(mime_msg, attachment_paths)
        
        return mime_msg
    
    def _add_attachments(self, mime_msg: MIMEMultipart, attachment_paths: List[str]):
        """
        添付ファイルをMIMEメッセージに追加します
        
        Args:
            mime_msg: MIMEメッセージ
            attachment_paths: 添付ファイルのパスリスト
        """
        for file_path in attachment_paths:
            try:
                path_obj = Path(file_path)
                
                if not path_obj.exists():
                    logger.warning(f"添付ファイルが見つかりません: {file_path}")
                    continue
                
                # ファイルを読み込み
                with open(file_path, 'rb') as f:
                    attachment_data = f.read()
                
                # MIMEパートを作成
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_data)
                encoders.encode_base64(part)
                
                # ヘッダーを設定
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {path_obj.name}'
                )
                
                # メッセージに追加
                mime_msg.attach(part)
                
                logger.debug(f"添付ファイルを追加しました: {path_obj.name}")
                
            except Exception as e:
                logger.error(f"添付ファイル処理エラー ({file_path}): {e}")
                continue
    
    def send_simple_text(self, to_addresses: List[str], subject: str, 
                        body: str, cc_addresses: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        シンプルなテキストメールを送信します
        
        Args:
            to_addresses: 宛先アドレスリスト
            subject: 件名
            body: 本文
            cc_addresses: CCアドレスリスト
            
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        # MailMessageオブジェクトを作成
        message = MailMessage(
            subject=subject,
            sender=self.account.email_address,
            recipients=to_addresses,
            cc_recipients=cc_addresses or [],
            body_text=body,
            account_id=self.account.account_id
        )
        
        return self.send_message(message)
    
    def send_html_message(self, to_addresses: List[str], subject: str,
                         html_body: str, text_body: Optional[str] = None,
                         cc_addresses: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        HTMLメールを送信します
        
        Args:
            to_addresses: 宛先アドレスリスト
            subject: 件名
            html_body: HTML本文
            text_body: テキスト本文（フォールバック用）
            cc_addresses: CCアドレスリスト
            
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        # MailMessageオブジェクトを作成
        message = MailMessage(
            subject=subject,
            sender=self.account.email_address,
            recipients=to_addresses,
            cc_recipients=cc_addresses or [],
            body_html=html_body,
            body_text=text_body or "",
            account_id=self.account.account_id
        )
        
        return self.send_message(message)
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        接続テストを実行します
        
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        try:
            if self.connect():
                # 簡単なコマンドを実行してテスト
                if self._connection:
                    # NOOPコマンドでサーバーとの通信をテスト
                    response = self._connection.noop()
                    
                    self.disconnect()
                    
                    if response[0] == 250:  # 250 OK
                        return True, "接続成功"
                    else:
                        return False, f"サーバー応答エラー: {response}"
                else:
                    return False, "接続オブジェクトが無効です"
            else:
                return False, "サーバーに接続できません"
                
        except Exception as e:
            return False, f"接続テストエラー: {e}"
    
    def send_test_message(self, test_recipient: str) -> Tuple[bool, str]:
        """
        テストメールを送信します
        
        Args:
            test_recipient: テスト送信先アドレス
            
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        if not test_recipient:
            return False, "テスト送信先が指定されていません"
        
        # テストメッセージを作成
        test_subject = "WabiMail 接続テスト"
        test_body = """
WabiMail接続テストメールです。

このメールが正常に受信できていれば、
SMTPサーバーとの接続が正常に動作しています。

🌸 WabiMail - 侘び寂びメールクライアント
        """.strip()
        
        return self.send_simple_text([test_recipient], test_subject, test_body)
    
    def __enter__(self):
        """
        コンテキストマネージャーエントリー
        """
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        コンテキストマネージャーエグジット
        """
        self.disconnect()