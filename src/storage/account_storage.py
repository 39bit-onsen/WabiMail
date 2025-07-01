# -*- coding: utf-8 -*-
"""
アカウントストレージモジュール

WabiMailのアカウント情報専用ストレージシステムです。
SecureStorageを基盤として、アカウント関連データの高レベルな操作を提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import uuid

from src.mail.account import Account, AccountType, AuthType, AccountSettings
from src.storage.secure_storage import SecureStorage
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class AccountStorage:
    """
    アカウントストレージクラス
    
    WabiMailのアカウント情報を安全に管理します。
    SecureStorageを基盤として、Account オブジェクトとの変換、
    アカウント固有の操作、検証機能を提供します。
    
    Attributes:
        _storage (SecureStorage): 基盤ストレージシステム
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        アカウントストレージを初期化
        
        Args:
            storage_dir: カスタムストレージディレクトリ（テスト用）
        """
        self._storage = SecureStorage(storage_dir)
        logger.info("アカウントストレージを初期化しました")
    
    def save_account(self, account: Account) -> Tuple[bool, str]:
        """
        アカウントオブジェクトを保存
        
        Args:
            account: 保存するAccountオブジェクト
            
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        try:
            # アカウントデータの検証
            validation_result = self._validate_account(account)
            if not validation_result[0]:
                return validation_result
            
            # Account オブジェクトを辞書に変換
            account_data = self._account_to_dict(account)
            
            # 重複チェック
            existing_accounts = self.list_accounts()
            for existing in existing_accounts:
                if (existing['email_address'] == account.email_address and 
                    existing['id'] != account.account_id):
                    return False, f"メールアドレス '{account.email_address}' は既に登録されています"
            
            # ストレージに保存
            success = self._storage.save_account(account_data)
            
            if success:
                logger.info(f"アカウントを保存しました: {account.name} ({account.email_address})")
                return True, "アカウントを正常に保存しました"
            else:
                return False, "アカウントの保存に失敗しました"
                
        except Exception as e:
            error_msg = f"アカウント保存エラー: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def load_account(self, account_id: str) -> Optional[Account]:
        """
        アカウントIDでアカウントを読み込み
        
        Args:
            account_id: アカウントID
            
        Returns:
            Optional[Account]: Accountオブジェクト
        """
        try:
            account_data = self._storage.load_account(account_id)
            if not account_data:
                return None
            
            # 辞書から Account オブジェクトに変換
            account = self._dict_to_account(account_data)
            return account
            
        except Exception as e:
            logger.error(f"アカウント読み込みエラー: {e}")
            return None
    
    def load_account_by_email(self, email_address: str) -> Optional[Account]:
        """
        メールアドレスでアカウントを読み込み
        
        Args:
            email_address: メールアドレス
            
        Returns:
            Optional[Account]: Accountオブジェクト
        """
        try:
            accounts = self.list_accounts()
            for account_info in accounts:
                if account_info['email_address'] == email_address:
                    return self.load_account(account_info['id'])
            
            return None
            
        except Exception as e:
            logger.error(f"メールアドレスによるアカウント読み込みエラー: {e}")
            return None
    
    def list_accounts(self) -> List[Dict[str, Any]]:
        """
        すべてのアカウント情報を取得
        
        Returns:
            List[Dict]: アカウント基本情報のリスト
        """
        try:
            return self._storage.list_accounts()
        except Exception as e:
            logger.error(f"アカウントリスト取得エラー: {e}")
            return []
    
    def load_all_accounts(self) -> List[Account]:
        """
        すべてのAccountオブジェクトを読み込み
        
        Returns:
            List[Account]: Accountオブジェクトのリスト
        """
        try:
            accounts = []
            account_list = self.list_accounts()
            
            for account_info in account_list:
                account = self.load_account(account_info['id'])
                if account:
                    accounts.append(account)
            
            return accounts
            
        except Exception as e:
            logger.error(f"全アカウント読み込みエラー: {e}")
            return []
    
    def update_account(self, account: Account) -> Tuple[bool, str]:
        """
        アカウント情報を更新
        
        Args:
            account: 更新するAccountオブジェクト
            
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        try:
            # 既存アカウントの確認
            existing_account = self.load_account(account.account_id)
            if not existing_account:
                return False, f"更新対象のアカウントが見つかりません: {account.account_id}"
            
            # 更新実行（save_accountと同じ処理）
            return self.save_account(account)
            
        except Exception as e:
            error_msg = f"アカウント更新エラー: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def delete_account(self, account_id: str) -> Tuple[bool, str]:
        """
        アカウントを削除
        
        Args:
            account_id: アカウントID
            
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        try:
            # 削除前に存在確認
            account = self.load_account(account_id)
            if not account:
                return False, f"削除対象のアカウントが見つかりません: {account_id}"
            
            # ストレージから削除
            success = self._storage.delete_account(account_id)
            
            if success:
                logger.info(f"アカウントを削除しました: {account.name} ({account.email_address})")
                return True, "アカウントを正常に削除しました"
            else:
                return False, "アカウントの削除に失敗しました"
                
        except Exception as e:
            error_msg = f"アカウント削除エラー: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def save_oauth2_token(self, account_id: str, token_data: Dict[str, Any]) -> bool:
        """
        OAuth2トークンを保存
        
        Args:
            account_id: アカウントID
            token_data: トークンデータ
            
        Returns:
            bool: 保存成功可否
        """
        try:
            return self._storage.save_oauth2_token(account_id, token_data)
        except Exception as e:
            logger.error(f"OAuth2トークン保存エラー: {e}")
            return False
    
    def load_oauth2_token(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        OAuth2トークンを読み込み
        
        Args:
            account_id: アカウントID
            
        Returns:
            Optional[Dict]: トークンデータ
        """
        try:
            return self._storage.load_oauth2_token(account_id)
        except Exception as e:
            logger.error(f"OAuth2トークン読み込みエラー: {e}")
            return None
    
    def get_accounts_by_type(self, account_type: AccountType) -> List[Account]:
        """
        アカウントタイプでフィルタリング
        
        Args:
            account_type: アカウントタイプ
            
        Returns:
            List[Account]: フィルタリングされたアカウントリスト
        """
        try:
            all_accounts = self.load_all_accounts()
            filtered_accounts = [
                account for account in all_accounts 
                if account.account_type == account_type
            ]
            return filtered_accounts
            
        except Exception as e:
            logger.error(f"アカウントタイプフィルタリングエラー: {e}")
            return []
    
    def get_accounts_by_auth_type(self, auth_type: AuthType) -> List[Account]:
        """
        認証タイプでフィルタリング
        
        Args:
            auth_type: 認証タイプ
            
        Returns:
            List[Account]: フィルタリングされたアカウントリスト
        """
        try:
            all_accounts = self.load_all_accounts()
            filtered_accounts = [
                account for account in all_accounts 
                if account.auth_type == auth_type
            ]
            return filtered_accounts
            
        except Exception as e:
            logger.error(f"認証タイプフィルタリングエラー: {e}")
            return []
    
    def _validate_account(self, account: Account) -> Tuple[bool, str]:
        """
        アカウントデータの検証
        
        Args:
            account: 検証するAccountオブジェクト
            
        Returns:
            Tuple[bool, str]: (検証結果, エラーメッセージ)
        """
        try:
            # 必須フィールドの確認
            if not account.name or not account.name.strip():
                return False, "アカウント名は必須です"
            
            if not account.email_address or not account.email_address.strip():
                return False, "メールアドレスは必須です"
            
            # メールアドレスの形式チェック（簡易）
            if '@' not in account.email_address:
                return False, "有効なメールアドレスを入力してください"
            
            # アカウントタイプの確認
            if not isinstance(account.account_type, AccountType):
                return False, "無効なアカウントタイプです"
            
            # 認証タイプの確認
            if not isinstance(account.auth_type, AuthType):
                return False, "無効な認証タイプです"
            
            # 設定の確認
            if not account.settings:
                return False, "アカウント設定は必須です"
            
            # サーバー設定の確認
            settings = account.settings
            if not settings.incoming_server or not settings.incoming_server.strip():
                return False, "受信サーバーは必須です"
            
            if not settings.outgoing_server or not settings.outgoing_server.strip():
                return False, "送信サーバーは必須です"
            
            if not isinstance(settings.incoming_port, int) or settings.incoming_port <= 0:
                return False, "有効な受信ポート番号を入力してください"
            
            if not isinstance(settings.outgoing_port, int) or settings.outgoing_port <= 0:
                return False, "有効な送信ポート番号を入力してください"
            
            return True, "検証成功"
            
        except Exception as e:
            return False, f"検証エラー: {e}"
    
    def _account_to_dict(self, account: Account) -> Dict[str, Any]:
        """
        Account オブジェクトを辞書に変換
        
        Args:
            account: Accountオブジェクト
            
        Returns:
            Dict[str, Any]: アカウントデータ辞書
        """
        return {
            'id': account.account_id,
            'name': account.name,
            'email_address': account.email_address,
            'account_type': account.account_type.value,
            'auth_type': account.auth_type.value,
            'settings': {
                'incoming_server': account.settings.incoming_server,
                'incoming_port': account.settings.incoming_port,
                'incoming_security': account.settings.incoming_security,
                'outgoing_server': account.settings.outgoing_server,
                'outgoing_port': account.settings.outgoing_port,
                'outgoing_security': account.settings.outgoing_security,
                'requires_auth': account.settings.requires_auth
            },
            'credentials': getattr(account, 'credentials', {}),
            'display_name': getattr(account, 'display_name', ''),
            'signature': getattr(account, 'signature', '')
        }
    
    def _dict_to_account(self, account_data: Dict[str, Any]) -> Account:
        """
        辞書から Account オブジェクトに変換
        
        Args:
            account_data: アカウントデータ辞書
            
        Returns:
            Account: Accountオブジェクト
        """
        # AccountSettings オブジェクトを作成
        settings_data = account_data.get('settings', {})
        settings = AccountSettings(
            incoming_server=settings_data.get('incoming_server', ''),
            incoming_port=settings_data.get('incoming_port', 993),
            incoming_security=settings_data.get('incoming_security', 'SSL'),
            outgoing_server=settings_data.get('outgoing_server', ''),
            outgoing_port=settings_data.get('outgoing_port', 587),
            outgoing_security=settings_data.get('outgoing_security', 'STARTTLS'),
            requires_auth=settings_data.get('requires_auth', True)
        )
        
        # Account オブジェクトを作成
        account = Account(
            account_id=account_data['id'],
            name=account_data['name'],
            email_address=account_data['email_address'],
            account_type=AccountType(account_data['account_type']),
            auth_type=AuthType(account_data['auth_type']),
            settings=settings
        )
        
        # 追加属性を設定
        account.credentials = account_data.get('credentials', {})
        account.display_name = account_data.get('display_name', '')
        account.signature = account_data.get('signature', '')
        
        return account
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        ストレージ情報を取得
        
        Returns:
            Dict[str, Any]: ストレージ情報
        """
        try:
            return self._storage.get_storage_info()
        except Exception as e:
            logger.error(f"ストレージ情報取得エラー: {e}")
            return {}
    
    def backup_accounts(self, backup_path: str) -> bool:
        """
        アカウントデータをバックアップ
        
        Args:
            backup_path: バックアップファイルパス
            
        Returns:
            bool: バックアップ成功可否
        """
        try:
            return self._storage.backup_data(backup_path)
        except Exception as e:
            logger.error(f"アカウントバックアップエラー: {e}")
            return False
    
    def close(self):
        """
        ストレージ接続を閉じる
        """
        if self._storage:
            self._storage.close()
    
    def __enter__(self):
        """コンテキストマネージャー開始"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了"""
        self.close()