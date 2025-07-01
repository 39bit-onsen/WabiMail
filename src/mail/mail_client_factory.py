# -*- coding: utf-8 -*-
"""
メールクライアントファクトリーモジュール

アカウントタイプに応じて適切なメールクライアントを生成するファクトリークラスです。
IMAP、SMTP、POP3の各クライアントを統一的に管理します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

from typing import Optional, Union, Tuple, Any
from enum import Enum

from src.mail.account import Account, AccountType
from src.mail.imap_client import IMAPClient
from src.mail.smtp_client import SMTPClient
from src.mail.pop_client import POPClient
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class ClientType(Enum):
    """
    クライアントタイプ列挙型
    
    生成するクライアントの種類を指定します。
    """
    IMAP = "imap"
    SMTP = "smtp"
    POP3 = "pop3"


class MailClientFactory:
    """
    メールクライアントファクトリークラス
    
    アカウント設定に基づいて適切なメールクライアントインスタンスを生成します。
    クライアントの生成ロジックを一元化し、設定の検証も行います。
    
    Static Methods:
        create_imap_client: IMAPクライアントを生成
        create_smtp_client: SMTPクライアントを生成  
        create_pop_client: POPクライアントを生成
        create_receive_client: 受信用クライアントを生成
        create_send_client: 送信用クライアントを生成
        test_account_connection: アカウント接続テスト
    """
    
    @staticmethod
    def create_imap_client(account: Account) -> Optional[IMAPClient]:
        """
        IMAPクライアントを生成します
        
        Args:
            account: メールアカウント情報
            
        Returns:
            Optional[IMAPClient]: IMAPクライアント、生成失敗時None
        """
        try:
            # アカウント設定の妥当性を確認
            if not MailClientFactory._validate_imap_settings(account):
                return None
            
            # IMAPクライアントを生成
            client = IMAPClient(account)
            
            logger.debug(f"IMAPクライアントを生成しました: {account.email_address}")
            return client
            
        except Exception as e:
            logger.error(f"IMAPクライアント生成エラー: {e}")
            return None
    
    @staticmethod
    def create_smtp_client(account: Account) -> Optional[SMTPClient]:
        """
        SMTPクライアントを生成します
        
        Args:
            account: メールアカウント情報
            
        Returns:
            Optional[SMTPClient]: SMTPクライアント、生成失敗時None
        """
        try:
            # アカウント設定の妥当性を確認
            if not MailClientFactory._validate_smtp_settings(account):
                return None
            
            # SMTPクライアントを生成
            client = SMTPClient(account)
            
            logger.debug(f"SMTPクライアントを生成しました: {account.email_address}")
            return client
            
        except Exception as e:
            logger.error(f"SMTPクライアント生成エラー: {e}")
            return None
    
    @staticmethod
    def create_pop_client(account: Account) -> Optional[POPClient]:
        """
        POPクライアントを生成します
        
        Args:
            account: メールアカウント情報
            
        Returns:
            Optional[POPClient]: POPクライアント、生成失敗時None
        """
        try:
            # アカウント設定の妥当性を確認
            if not MailClientFactory._validate_pop_settings(account):
                return None
            
            # POPクライアントを生成
            client = POPClient(account)
            
            logger.debug(f"POPクライアントを生成しました: {account.email_address}")
            return client
            
        except Exception as e:
            logger.error(f"POPクライアント生成エラー: {e}")
            return None
    
    @staticmethod
    def create_receive_client(account: Account) -> Optional[Union[IMAPClient, POPClient]]:
        """
        受信用クライアントを生成します
        
        Args:
            account: メールアカウント情報
            
        Returns:
            Optional[Union[IMAPClient, POPClient]]: 受信用クライアント、生成失敗時None
            
        Note:
            アカウントタイプに応じて適切な受信クライアントを選択します。
            Gmail、IMAPアカウント → IMAPClient
            POP3アカウント → POPClient
        """
        if account.account_type in [AccountType.GMAIL, AccountType.IMAP]:
            return MailClientFactory.create_imap_client(account)
        elif account.account_type == AccountType.POP3:
            return MailClientFactory.create_pop_client(account)
        else:
            logger.error(f"サポートされていない受信アカウントタイプ: {account.account_type}")
            return None
    
    @staticmethod
    def create_send_client(account: Account) -> Optional[SMTPClient]:
        """
        送信用クライアントを生成します
        
        Args:
            account: メールアカウント情報
            
        Returns:
            Optional[SMTPClient]: 送信用クライアント、生成失敗時None
            
        Note:
            すべてのアカウントタイプでSMTPクライアントを使用します。
        """
        return MailClientFactory.create_smtp_client(account)
    
    @staticmethod
    def create_client_by_type(account: Account, 
                             client_type: ClientType) -> Optional[Union[IMAPClient, SMTPClient, POPClient]]:
        """
        指定されたタイプのクライアントを生成します
        
        Args:
            account: メールアカウント情報
            client_type: 生成するクライアントタイプ
            
        Returns:
            Optional[Union[IMAPClient, SMTPClient, POPClient]]: クライアント、生成失敗時None
        """
        if client_type == ClientType.IMAP:
            return MailClientFactory.create_imap_client(account)
        elif client_type == ClientType.SMTP:
            return MailClientFactory.create_smtp_client(account)
        elif client_type == ClientType.POP3:
            return MailClientFactory.create_pop_client(account)
        else:
            logger.error(f"サポートされていないクライアントタイプ: {client_type}")
            return None
    
    @staticmethod
    def test_account_connection(account: Account) -> Tuple[bool, str, dict]:
        """
        アカウントの接続テストを実行します
        
        Args:
            account: テストするメールアカウント
            
        Returns:
            Tuple[bool, str, dict]: (全体成功可否, メッセージ, 詳細結果)
            
        Note:
            受信・送信の両方向で接続テストを実行し、結果を返します。
        """
        results = {
            'receive': {'success': False, 'message': '', 'client_type': ''},
            'send': {'success': False, 'message': '', 'client_type': 'smtp'}
        }
        
        overall_success = True
        messages = []
        
        try:
            # 受信テスト
            receive_client = MailClientFactory.create_receive_client(account)
            if receive_client:
                if isinstance(receive_client, IMAPClient):
                    results['receive']['client_type'] = 'imap'
                    success, message = receive_client.test_connection()
                elif isinstance(receive_client, POPClient):
                    results['receive']['client_type'] = 'pop3'
                    success, message = receive_client.test_connection()
                else:
                    success, message = False, "不明な受信クライアントタイプ"
                
                results['receive']['success'] = success
                results['receive']['message'] = message
                
                if success:
                    messages.append(f"受信({results['receive']['client_type'].upper()}): {message}")
                else:
                    messages.append(f"受信エラー({results['receive']['client_type'].upper()}): {message}")
                    overall_success = False
            else:
                results['receive']['message'] = "受信クライアントを生成できません"
                messages.append("受信エラー: クライアント生成失敗")
                overall_success = False
            
            # 送信テスト
            send_client = MailClientFactory.create_send_client(account)
            if send_client:
                success, message = send_client.test_connection()
                results['send']['success'] = success
                results['send']['message'] = message
                
                if success:
                    messages.append(f"送信(SMTP): {message}")
                else:
                    messages.append(f"送信エラー(SMTP): {message}")
                    overall_success = False
            else:
                results['send']['message'] = "送信クライアントを生成できません"
                messages.append("送信エラー: クライアント生成失敗")
                overall_success = False
            
            # 結果をまとめる
            summary_message = " | ".join(messages)
            
            if overall_success:
                logger.info(f"アカウント接続テスト成功: {account.email_address}")
            else:
                logger.warning(f"アカウント接続テスト失敗: {account.email_address}")
            
            return overall_success, summary_message, results
            
        except Exception as e:
            error_message = f"接続テスト中にエラーが発生しました: {e}"
            logger.error(error_message)
            return False, error_message, results
    
    @staticmethod
    def _validate_imap_settings(account: Account) -> bool:
        """
        IMAP設定の妥当性を確認します
        
        Args:
            account: メールアカウント
            
        Returns:
            bool: 設定が有効な場合True
        """
        if not account.settings.incoming_server:
            logger.error("IMAPサーバーが設定されていません")
            return False
        
        if not (1 <= account.settings.incoming_port <= 65535):
            logger.error(f"無効なIMAPポート番号: {account.settings.incoming_port}")
            return False
        
        if account.settings.incoming_security not in ['SSL', 'STARTTLS', 'NONE']:
            logger.error(f"無効なIMAP暗号化設定: {account.settings.incoming_security}")
            return False
        
        return True
    
    @staticmethod
    def _validate_smtp_settings(account: Account) -> bool:
        """
        SMTP設定の妥当性を確認します
        
        Args:
            account: メールアカウント
            
        Returns:
            bool: 設定が有効な場合True
        """
        if not account.settings.outgoing_server:
            logger.error("SMTPサーバーが設定されていません")
            return False
        
        if not (1 <= account.settings.outgoing_port <= 65535):
            logger.error(f"無効なSMTPポート番号: {account.settings.outgoing_port}")
            return False
        
        if account.settings.outgoing_security not in ['SSL', 'STARTTLS', 'NONE']:
            logger.error(f"無効なSMTP暗号化設定: {account.settings.outgoing_security}")
            return False
        
        return True
    
    @staticmethod
    def _validate_pop_settings(account: Account) -> bool:
        """
        POP設定の妥当性を確認します
        
        Args:
            account: メールアカウント
            
        Returns:
            bool: 設定が有効な場合True
        """
        if not account.settings.incoming_server:
            logger.error("POPサーバーが設定されていません")
            return False
        
        if not (1 <= account.settings.incoming_port <= 65535):
            logger.error(f"無効なPOPポート番号: {account.settings.incoming_port}")
            return False
        
        if account.settings.incoming_security not in ['SSL', 'NONE']:
            logger.error(f"無効なPOP暗号化設定: {account.settings.incoming_security}")
            return False
        
        return True
    
    @staticmethod
    def get_supported_client_types(account: Account) -> list[ClientType]:
        """
        アカウントでサポートされているクライアントタイプを取得します
        
        Args:
            account: メールアカウント
            
        Returns:
            list[ClientType]: サポートされているクライアントタイプのリスト
        """
        supported_types = []
        
        # 受信クライアント
        if account.account_type in [AccountType.GMAIL, AccountType.IMAP]:
            if MailClientFactory._validate_imap_settings(account):
                supported_types.append(ClientType.IMAP)
        elif account.account_type == AccountType.POP3:
            if MailClientFactory._validate_pop_settings(account):
                supported_types.append(ClientType.POP3)
        
        # 送信クライアント
        if MailClientFactory._validate_smtp_settings(account):
            supported_types.append(ClientType.SMTP)
        
        return supported_types