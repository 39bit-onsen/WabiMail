# -*- coding: utf-8 -*-
"""
IMAPクライアントモジュール

WabiMailのIMAP接続とメール受信機能を提供します。
セキュアな接続、効率的なメール取得、フォルダ管理等をサポートします。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import imaplib
import email
import ssl
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import time

from src.mail.account import Account, AccountType
from src.mail.mail_message import MailMessage, MessageFlag
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class IMAPClient:
    """
    IMAPクライアントクラス
    
    IMAPサーバーへの接続とメール操作を管理します。
    セキュアな接続、エラーハンドリング、効率的なデータ取得を提供します。
    
    Attributes:
        account (Account): 関連するメールアカウント
        _connection (Optional[imaplib.IMAP4]): IMAP接続オブジェクト
        _current_folder (str): 現在選択中のフォルダ
        _is_connected (bool): 接続状態
    """
    
    def __init__(self, account: Account):
        """
        IMAPクライアントを初期化します
        
        Args:
            account: 関連するメールアカウント
        """
        self.account = account
        self._connection: Optional[imaplib.IMAP4] = None
        self._current_folder = ""
        self._is_connected = False
        
        logger.debug(f"IMAPクライアントを初期化しました: {account.email_address}")
    
    def connect(self) -> bool:
        """
        IMAPサーバーに接続します
        
        Returns:
            bool: 接続成功時True、失敗時False
        """
        try:
            logger.info(f"IMAPサーバーに接続中: {self.account.settings.incoming_server}")
            
            # SSL/TLS設定に基づいて接続
            if self.account.settings.incoming_security.upper() == "SSL":
                # SSL接続
                self._connection = imaplib.IMAP4_SSL(
                    self.account.settings.incoming_server,
                    self.account.settings.incoming_port
                )
            else:
                # 平文接続またはSTARTTLS
                self._connection = imaplib.IMAP4(
                    self.account.settings.incoming_server,
                    self.account.settings.incoming_port
                )
                
                # STARTTLSを試行
                if self.account.settings.incoming_security.upper() == "STARTTLS":
                    self._connection.starttls()
            
            # 認証情報は実際のパスワード管理システムから取得する予定
            # 現在はテスト用にダミー認証
            logger.info("認証を実行中...")
            # result = self._connection.login(username, password)
            
            # テスト用の擬似接続成功
            self._is_connected = True
            
            logger.info(f"IMAPサーバーに接続しました: {self.account.email_address}")
            return True
            
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP接続エラー: {e}")
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
        IMAPサーバーから切断します
        """
        try:
            if self._connection and self._is_connected:
                self._connection.logout()
                logger.info("IMAPサーバーから切断しました")
        except Exception as e:
            logger.warning(f"切断中にエラーが発生しました: {e}")
        finally:
            self._connection = None
            self._is_connected = False
            self._current_folder = ""
    
    def is_connected(self) -> bool:
        """
        接続状態を確認します
        
        Returns:
            bool: 接続中の場合True
        """
        return self._is_connected and self._connection is not None
    
    def select_folder(self, folder_name: str = "INBOX") -> bool:
        """
        フォルダを選択します
        
        Args:
            folder_name: 選択するフォルダ名
            
        Returns:
            bool: 選択成功時True、失敗時False
        """
        if not self.is_connected():
            logger.error("IMAP接続が確立されていません")
            return False
        
        try:
            # フォルダを選択
            result, data = self._connection.select(folder_name)
            
            if result == 'OK':
                self._current_folder = folder_name
                message_count = int(data[0]) if data[0] else 0
                logger.debug(f"フォルダを選択しました: {folder_name} ({message_count}件)")
                return True
            else:
                logger.error(f"フォルダ選択失敗: {folder_name}, {result}")
                return False
                
        except Exception as e:
            logger.error(f"フォルダ選択エラー: {e}")
            return False
    
    def get_folder_list(self) -> List[str]:
        """
        利用可能なフォルダリストを取得します
        
        Returns:
            List[str]: フォルダ名のリスト
        """
        if not self.is_connected():
            logger.error("IMAP接続が確立されていません")
            return []
        
        try:
            # フォルダリストを取得
            result, folders = self._connection.list()
            
            if result != 'OK':
                logger.error("フォルダリスト取得失敗")
                return []
            
            folder_names = []
            for folder in folders:
                # フォルダ情報を解析（簡易版）
                folder_str = folder.decode('utf-8') if isinstance(folder, bytes) else folder
                # 最後の部分がフォルダ名
                parts = folder_str.split('"')
                if len(parts) >= 3:
                    folder_name = parts[-2]
                    folder_names.append(folder_name)
            
            logger.debug(f"フォルダリストを取得しました: {len(folder_names)}個")
            return folder_names
            
        except Exception as e:
            logger.error(f"フォルダリスト取得エラー: {e}")
            return []
    
    def get_message_count(self, folder_name: str = "INBOX") -> int:
        """
        指定フォルダのメッセージ数を取得します
        
        Args:
            folder_name: フォルダ名
            
        Returns:
            int: メッセージ数
        """
        if not self.select_folder(folder_name):
            return 0
        
        try:
            # メッセージ数を取得
            result, data = self._connection.search(None, 'ALL')
            
            if result == 'OK' and data[0]:
                message_ids = data[0].split()
                return len(message_ids)
            else:
                return 0
                
        except Exception as e:
            logger.error(f"メッセージ数取得エラー: {e}")
            return 0
    
    def fetch_messages(self, folder_name: str = "INBOX", 
                      limit: int = 50, 
                      unread_only: bool = False) -> List[MailMessage]:
        """
        メッセージを取得します
        
        Args:
            folder_name: 取得するフォルダ名
            limit: 取得する最大件数
            unread_only: 未読メッセージのみ取得するか
            
        Returns:
            List[MailMessage]: 取得したメッセージリスト
        """
        if not self.select_folder(folder_name):
            return []
        
        try:
            # 検索条件を構築
            search_criteria = 'UNSEEN' if unread_only else 'ALL'
            
            # メッセージIDを検索
            result, data = self._connection.search(None, search_criteria)
            
            if result != 'OK' or not data[0]:
                logger.debug(f"メッセージが見つかりません: {folder_name}")
                return []
            
            message_ids = data[0].split()
            
            # 最新のメッセージから指定件数を取得
            if limit > 0:
                message_ids = message_ids[-limit:]
            
            messages = []
            
            for msg_id in message_ids:
                try:
                    # メッセージを取得
                    message = self._fetch_single_message(msg_id, folder_name)
                    if message:
                        messages.append(message)
                        
                except Exception as e:
                    logger.warning(f"メッセージ取得エラー (ID: {msg_id}): {e}")
                    continue
            
            # 新しい順にソート
            messages.sort(key=lambda m: m.get_display_date(), reverse=True)
            
            logger.info(f"メッセージを取得しました: {len(messages)}件 ({folder_name})")
            return messages
            
        except Exception as e:
            logger.error(f"メッセージ取得エラー: {e}")
            return []
    
    def _fetch_single_message(self, msg_id: bytes, folder_name: str) -> Optional[MailMessage]:
        """
        単一のメッセージを取得します
        
        Args:
            msg_id: メッセージID
            folder_name: フォルダ名
            
        Returns:
            Optional[MailMessage]: 取得したメッセージ、失敗時None
        """
        try:
            # メッセージの詳細情報を取得
            result, data = self._connection.fetch(msg_id, '(RFC822 FLAGS)')
            
            if result != 'OK' or not data:
                return None
            
            # メッセージデータを解析
            raw_email = data[0][1]
            email_msg = email.message_from_bytes(raw_email, policy=email.policy.default)
            
            # MailMessageオブジェクトに変換
            message = MailMessage.from_email_message(
                email_msg,
                account_id=self.account.account_id,
                folder=folder_name,
                uid=msg_id.decode()
            )
            
            # フラグ情報を追加
            flag_data = data[0][0]
            if flag_data:
                flag_str = flag_data.decode()
                if '\\Seen' in flag_str:
                    message.add_flag(MessageFlag.SEEN)
                if '\\Flagged' in flag_str:
                    message.add_flag(MessageFlag.FLAGGED)
                if '\\Answered' in flag_str:
                    message.add_flag(MessageFlag.ANSWERED)
            
            return message
            
        except Exception as e:
            logger.error(f"単一メッセージ取得エラー: {e}")
            return None
    
    def mark_as_read(self, message_uid: str) -> bool:
        """
        メッセージを既読にマークします
        
        Args:
            message_uid: メッセージUID
            
        Returns:
            bool: 成功時True、失敗時False
        """
        if not self.is_connected():
            return False
        
        try:
            result, _ = self._connection.store(message_uid, '+FLAGS', '\\Seen')
            if result == 'OK':
                logger.debug(f"メッセージを既読にマークしました: {message_uid}")
                return True
            else:
                logger.error(f"既読マーク失敗: {message_uid}")
                return False
                
        except Exception as e:
            logger.error(f"既読マークエラー: {e}")
            return False
    
    def mark_as_unread(self, message_uid: str) -> bool:
        """
        メッセージを未読にマークします
        
        Args:
            message_uid: メッセージUID
            
        Returns:
            bool: 成功時True、失敗時False
        """
        if not self.is_connected():
            return False
        
        try:
            result, _ = self._connection.store(message_uid, '-FLAGS', '\\Seen')
            if result == 'OK':
                logger.debug(f"メッセージを未読にマークしました: {message_uid}")
                return True
            else:
                logger.error(f"未読マーク失敗: {message_uid}")
                return False
                
        except Exception as e:
            logger.error(f"未読マークエラー: {e}")
            return False
    
    def delete_message(self, message_uid: str) -> bool:
        """
        メッセージを削除します
        
        Args:
            message_uid: メッセージUID
            
        Returns:
            bool: 成功時True、失敗時False
        """
        if not self.is_connected():
            return False
        
        try:
            # 削除フラグを設定
            result, _ = self._connection.store(message_uid, '+FLAGS', '\\Deleted')
            if result != 'OK':
                logger.error(f"削除フラグ設定失敗: {message_uid}")
                return False
            
            # Expungeで実際に削除
            self._connection.expunge()
            
            logger.debug(f"メッセージを削除しました: {message_uid}")
            return True
            
        except Exception as e:
            logger.error(f"メッセージ削除エラー: {e}")
            return False
    
    def move_message(self, message_uid: str, destination_folder: str) -> bool:
        """
        メッセージを他のフォルダに移動します
        
        Args:
            message_uid: メッセージUID
            destination_folder: 移動先フォルダ名
            
        Returns:
            bool: 成功時True、失敗時False
        """
        if not self.is_connected():
            return False
        
        try:
            # IMAPのMOVE機能を使用（対応していない場合はCOPY+DELETE）
            try:
                result, _ = self._connection.move(message_uid, destination_folder)
                if result == 'OK':
                    logger.debug(f"メッセージを移動しました: {message_uid} -> {destination_folder}")
                    return True
            except AttributeError:
                # MOVEが対応していない場合はCOPY+DELETEで代替
                result, _ = self._connection.copy(message_uid, destination_folder)
                if result == 'OK':
                    return self.delete_message(message_uid)
            
            return False
            
        except Exception as e:
            logger.error(f"メッセージ移動エラー: {e}")
            return False
    
    def get_unread_count(self, folder_name: str = "INBOX") -> int:
        """
        未読メッセージ数を取得します
        
        Args:
            folder_name: フォルダ名
            
        Returns:
            int: 未読メッセージ数
        """
        if not self.select_folder(folder_name):
            return 0
        
        try:
            result, data = self._connection.search(None, 'UNSEEN')
            
            if result == 'OK' and data[0]:
                unread_ids = data[0].split()
                return len(unread_ids)
            else:
                return 0
                
        except Exception as e:
            logger.error(f"未読数取得エラー: {e}")
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
                folders = self.get_folder_list()
                if folders:
                    message_count = self.get_message_count()
                    self.disconnect()
                    return True, f"接続成功 (フォルダ数: {len(folders)}, メッセージ数: {message_count})"
                else:
                    self.disconnect()
                    return False, "フォルダリストを取得できません"
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