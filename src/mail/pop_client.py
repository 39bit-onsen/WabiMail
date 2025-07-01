# -*- coding: utf-8 -*-
"""
POPクライアントモジュール

WabiMailのPOP3接続とメール受信機能を提供します。
レガシーシステム対応として、シンプルなメール受信機能をサポートします。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import poplib
import email
import ssl
from typing import List, Optional, Tuple
from datetime import datetime

from src.mail.account import Account
from src.mail.mail_message import MailMessage, MessageFlag
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class POPClient:
    """
    POPクライアントクラス
    
    POP3サーバーへの接続とメール受信を管理します。
    シンプルなメール取得機能を提供し、レガシーシステムとの互換性を保ちます。
    
    Attributes:
        account (Account): 関連するメールアカウント
        _connection (Optional[poplib.POP3]): POP3接続オブジェクト
        _is_connected (bool): 接続状態
    
    Note:
        POP3はIMAPと異なり、フォルダ概念がなく、基本的にサーバーから
        メールをダウンロードして削除する仕組みです。
        WabiMailでは非破壊的な使用を推奨します。
    """
    
    def __init__(self, account: Account):
        """
        POPクライアントを初期化します
        
        Args:
            account: 関連するメールアカウント
        """
        self.account = account
        self._connection: Optional[poplib.POP3] = None
        self._is_connected = False
        
        logger.debug(f"POPクライアントを初期化しました: {account.email_address}")
    
    def connect(self) -> bool:
        """
        POP3サーバーに接続します
        
        Returns:
            bool: 接続成功時True、失敗時False
        """
        try:
            logger.info(f"POP3サーバーに接続中: {self.account.settings.incoming_server}")
            
            # SSL/TLS設定に基づいて接続
            if self.account.settings.incoming_security.upper() == "SSL":
                # SSL接続
                self._connection = poplib.POP3_SSL(
                    self.account.settings.incoming_server,
                    self.account.settings.incoming_port
                )
            else:
                # 平文接続（POP3はSTARTTLSをサポートしていない場合が多い）
                self._connection = poplib.POP3(
                    self.account.settings.incoming_server,
                    self.account.settings.incoming_port
                )
            
            # 認証情報は実際のパスワード管理システムから取得する予定
            # 現在はテスト用にダミー認証
            logger.info("POP3認証を実行中...")
            # result = self._connection.user(username)
            # result = self._connection.pass_(password)
            
            # テスト用の擬似接続成功
            self._is_connected = True
            
            logger.info(f"POP3サーバーに接続しました: {self.account.email_address}")
            return True
            
        except poplib.error_proto as e:
            logger.error(f"POP3プロトコルエラー: {e}")
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
        POP3サーバーから切断します
        """
        try:
            if self._connection and self._is_connected:
                self._connection.quit()
                logger.info("POP3サーバーから切断しました")
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
    
    def get_message_count(self) -> int:
        """
        サーバー上のメッセージ数を取得します
        
        Returns:
            int: メッセージ数
        """
        if not self.is_connected():
            return 0
        
        try:
            # メッセージ数とメールボックスサイズを取得
            response = self._connection.stat()
            message_count = response[0]
            
            logger.debug(f"POP3メッセージ数: {message_count}")
            return message_count
            
        except Exception as e:
            logger.error(f"メッセージ数取得エラー: {e}")
            return 0
    
    def fetch_messages(self, limit: int = 50, 
                      delete_after_fetch: bool = False) -> List[MailMessage]:
        """
        メッセージを取得します
        
        Args:
            limit: 取得する最大件数（0で全件取得）
            delete_after_fetch: 取得後にサーバーから削除するか
            
        Returns:
            List[MailMessage]: 取得したメッセージリスト
            
        Warning:
            delete_after_fetchをTrueにすると、サーバーからメールが削除されます。
            通常はFalseのままにして、必要に応じて別途削除処理を行ってください。
        """
        if not self.is_connected():
            return []
        
        try:
            # メッセージ数を取得
            message_count = self.get_message_count()
            if message_count == 0:
                logger.debug("POP3サーバーにメッセージがありません")
                return []
            
            # 取得するメッセージ範囲を決定
            if limit > 0:
                start = max(1, message_count - limit + 1)
            else:
                start = 1
            
            messages = []
            
            for msg_num in range(start, message_count + 1):
                try:
                    # 単一のメッセージを取得
                    message = self._fetch_single_message(msg_num)
                    if message:
                        messages.append(message)
                        
                        # 削除が指定されている場合
                        if delete_after_fetch:
                            self._connection.dele(msg_num)
                            logger.debug(f"POP3メッセージを削除しました: {msg_num}")
                        
                except Exception as e:
                    logger.warning(f"メッセージ取得エラー (番号: {msg_num}): {e}")
                    continue
            
            # 削除を実行した場合はコミット
            if delete_after_fetch and messages:
                # POP3では明示的なコミットは不要（quit時に自動実行）
                logger.info(f"POP3メッセージを削除しました: {len(messages)}件")
            
            # 新しい順にソート
            messages.sort(key=lambda m: m.get_display_date(), reverse=True)
            
            logger.info(f"POP3メッセージを取得しました: {len(messages)}件")
            return messages
            
        except Exception as e:
            logger.error(f"メッセージ取得エラー: {e}")
            return []
    
    def _fetch_single_message(self, msg_num: int) -> Optional[MailMessage]:
        """
        単一のメッセージを取得します
        
        Args:
            msg_num: メッセージ番号（1から開始）
            
        Returns:
            Optional[MailMessage]: 取得したメッセージ、失敗時None
        """
        try:
            # メッセージの全体を取得
            response, lines, octets = self._connection.retr(msg_num)
            
            # バイト列を結合してメールデータを構築
            raw_email = b'\r\n'.join(lines)
            
            # emailモジュールでパース
            email_msg = email.message_from_bytes(raw_email, policy=email.policy.default)
            
            # MailMessageオブジェクトに変換
            message = MailMessage.from_email_message(
                email_msg,
                account_id=self.account.account_id,
                folder="INBOX",  # POP3では常にINBOX
                uid=str(msg_num)  # POP3ではメッセージ番号をUIDとして使用
            )
            
            # POP3で取得したメッセージは基本的に未読として扱う
            # （サーバー側に既読情報は保存されない）
            message.remove_flag(MessageFlag.SEEN)
            
            return message
            
        except Exception as e:
            logger.error(f"単一メッセージ取得エラー: {e}")
            return None
    
    def get_message_headers(self, limit: int = 10) -> List[dict]:
        """
        メッセージのヘッダー情報のみを取得します
        
        Args:
            limit: 取得する最大件数
            
        Returns:
            List[dict]: ヘッダー情報のリスト
            
        Note:
            大量のメールがある場合、全文取得前にヘッダーで確認できます。
        """
        if not self.is_connected():
            return []
        
        try:
            message_count = self.get_message_count()
            if message_count == 0:
                return []
            
            # 最新のメッセージから指定件数を取得
            start = max(1, message_count - limit + 1)
            
            headers = []
            
            for msg_num in range(start, message_count + 1):
                try:
                    # ヘッダーのみを取得（TOPコマンド使用）
                    response, lines, octets = self._connection.top(msg_num, 0)
                    
                    # バイト列を結合
                    header_data = b'\r\n'.join(lines)
                    
                    # ヘッダーをパース
                    email_msg = email.message_from_bytes(header_data, policy=email.policy.default)
                    
                    header_info = {
                        'message_number': msg_num,
                        'subject': email_msg.get('Subject', ''),
                        'from': email_msg.get('From', ''),
                        'date': email_msg.get('Date', ''),
                        'size': octets
                    }
                    
                    headers.append(header_info)
                    
                except Exception as e:
                    logger.warning(f"ヘッダー取得エラー (番号: {msg_num}): {e}")
                    continue
            
            logger.debug(f"POP3ヘッダーを取得しました: {len(headers)}件")
            return headers
            
        except Exception as e:
            logger.error(f"ヘッダー取得エラー: {e}")
            return []
    
    def delete_message(self, msg_num: int) -> bool:
        """
        指定されたメッセージを削除マークします
        
        Args:
            msg_num: メッセージ番号
            
        Returns:
            bool: 成功時True、失敗時False
            
        Note:
            実際の削除はquit()時に実行されます。
        """
        if not self.is_connected():
            return False
        
        try:
            self._connection.dele(msg_num)
            logger.debug(f"POP3メッセージを削除マークしました: {msg_num}")
            return True
            
        except Exception as e:
            logger.error(f"メッセージ削除エラー: {e}")
            return False
    
    def reset_deletions(self) -> bool:
        """
        削除マークをリセットします
        
        Returns:
            bool: 成功時True、失敗時False
            
        Note:
            RSET コマンドで削除マークを取り消します。
        """
        if not self.is_connected():
            return False
        
        try:
            self._connection.rset()
            logger.debug("POP3削除マークをリセットしました")
            return True
            
        except Exception as e:
            logger.error(f"削除リセットエラー: {e}")
            return False
    
    def get_mailbox_size(self) -> int:
        """
        メールボックスの総サイズを取得します
        
        Returns:
            int: メールボックスサイズ（バイト）
        """
        if not self.is_connected():
            return 0
        
        try:
            response = self._connection.stat()
            mailbox_size = response[1]  # (メッセージ数, サイズ)
            
            logger.debug(f"POP3メールボックスサイズ: {mailbox_size}バイト")
            return mailbox_size
            
        except Exception as e:
            logger.error(f"メールボックスサイズ取得エラー: {e}")
            return 0
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        接続テストを実行します
        
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        try:
            if self.connect():
                # 基本的な操作をテスト
                message_count = self.get_message_count()
                mailbox_size = self.get_mailbox_size()
                
                self.disconnect()
                
                return True, f"接続成功 (メッセージ数: {message_count}, サイズ: {mailbox_size:,}バイト)"
            else:
                return False, "サーバーに接続できません"
                
        except Exception as e:
            return False, f"接続テストエラー: {e}"
    
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