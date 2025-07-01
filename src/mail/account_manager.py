# -*- coding: utf-8 -*-
"""
アカウント管理モジュール（更新版）

複数のメールアカウントを一元管理するためのマネージャークラスです。
アカウントの追加、削除、更新、暗号化保存機能を提供します。

Author: WabiMail Development Team
Created: 2025-07-01
Updated: 2025-07-01 - 新しいストレージシステムに対応
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import yaml

from src.mail.account import Account, AccountType, AuthType
from src.storage.account_storage import AccountStorage
from src.utils.logger import get_logger
from src.config.app_config import AppConfig

# ロガーを取得
logger = get_logger(__name__)


class AccountManager:
    """
    メールアカウント管理クラス
    
    WabiMailのすべてのメールアカウントを管理します。
    アカウントの追加、削除、更新、暗号化保存、読み込み機能を提供します。
    新しいAccountStorageシステムを使用して、暗号化された安全なストレージを実現します。
    
    Attributes:
        _accounts (List[Account]): 管理対象のアカウントリスト（メモリキャッシュ）
        _config (AppConfig): アプリケーション設定
        _storage (AccountStorage): アカウントストレージシステム
    """
    
    def __init__(self, config: Optional[AppConfig] = None, storage_dir: Optional[str] = None):
        """
        AccountManagerを初期化します
        
        Args:
            config (AppConfig, optional): アプリケーション設定
            storage_dir (str, optional): カスタムストレージディレクトリ（テスト用）
        """
        self._accounts: List[Account] = []
        self._config = config or AppConfig()
        
        # 新しいストレージシステムを初期化
        self._storage = AccountStorage(storage_dir)
        
        # 既存アカウントを読み込み
        self.load_accounts()
        
        logger.info(f"アカウントマネージャーを初期化しました: {len(self._accounts)}個のアカウント")
    
    def add_account(self, account: Account) -> Tuple[bool, str]:
        """
        アカウントを追加します
        
        Args:
            account (Account): 追加するアカウント
            
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        try:
            # アカウント情報の妥当性確認
            is_valid, errors = account.validate()
            if not is_valid:
                error_msg = f"アカウント検証エラー: {', '.join(errors)}"
                logger.error(error_msg)
                return False, error_msg
            
            # 同じメールアドレスのアカウントが既に存在するかチェック
            existing_account = self.get_account_by_email(account.email_address)
            if existing_account:
                error_msg = f"メールアドレス '{account.email_address}' は既に登録されています"
                logger.error(error_msg)
                return False, error_msg
            
            # 初回追加の場合はデフォルトアカウントに設定
            if len(self._accounts) == 0:
                account.is_default = True
            
            # アカウントタイプに応じてプリセット設定を適用
            account.apply_preset_settings()
            
            # 新しいストレージシステムで保存
            success, message = self._storage.save_account(account)
            if not success:
                return False, message
            
            # メモリキャッシュに追加
            self._accounts.append(account)
            
            logger.info(f"アカウントを追加しました: {account.name} <{account.email_address}>")
            return True, "アカウントを正常に追加しました"
            
        except Exception as e:
            error_msg = f"アカウント追加エラー: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def update_account(self, account: Account) -> Tuple[bool, str]:
        """
        アカウント情報を更新します
        
        Args:
            account (Account): 更新するアカウント
            
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        try:
            # アカウント情報の妥当性確認
            is_valid, errors = account.validate()
            if not is_valid:
                error_msg = f"アカウント検証エラー: {', '.join(errors)}"
                logger.error(error_msg)
                return False, error_msg
            
            # 既存アカウントの確認
            existing_account = self.get_account_by_id(account.account_id)
            if not existing_account:
                error_msg = f"更新対象のアカウントが見つかりません: {account.account_id}"
                logger.error(error_msg)
                return False, error_msg
            
            # ストレージで更新
            success, message = self._storage.update_account(account)
            if not success:
                return False, message
            
            # メモリキャッシュを更新
            for i, cached_account in enumerate(self._accounts):
                if cached_account.account_id == account.account_id:
                    self._accounts[i] = account
                    break
            
            logger.info(f"アカウントを更新しました: {account.name} <{account.email_address}>")
            return True, "アカウントを正常に更新しました"
            
        except Exception as e:
            error_msg = f"アカウント更新エラー: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def remove_account(self, account_id: str) -> Tuple[bool, str]:
        """
        アカウントを削除します
        
        Args:
            account_id (str): 削除するアカウントのID
            
        Returns:
            Tuple[bool, str]: (成功可否, メッセージ)
        """
        try:
            # 削除対象のアカウントを確認
            account = self.get_account_by_id(account_id)
            if not account:
                error_msg = f"削除対象のアカウントが見つかりません: {account_id}"
                logger.error(error_msg)
                return False, error_msg
            
            # ストレージから削除
            success, message = self._storage.delete_account(account_id)
            if not success:
                return False, message
            
            # メモリキャッシュから削除
            self._accounts = [a for a in self._accounts if a.account_id != account_id]
            
            logger.info(f"アカウントを削除しました: {account.name} <{account.email_address}>")
            return True, "アカウントを正常に削除しました"
            
        except Exception as e:
            error_msg = f"アカウント削除エラー: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_accounts(self) -> List[Account]:
        """
        すべてのアカウントを取得します
        
        Returns:
            List[Account]: アカウントリスト
        """
        return self._accounts.copy()
    
    def get_account_by_id(self, account_id: str) -> Optional[Account]:
        """
        アカウントIDでアカウントを取得します
        
        Args:
            account_id (str): アカウントID
            
        Returns:
            Optional[Account]: 見つかったアカウント、見つからない場合はNone
        """
        for account in self._accounts:
            if account.account_id == account_id:
                return account
        return None
    
    def get_account_by_email(self, email_address: str) -> Optional[Account]:
        """
        メールアドレスでアカウントを取得します
        
        Args:
            email_address (str): メールアドレス
            
        Returns:
            Optional[Account]: 見つかったアカウント、見つからない場合はNone
        """
        for account in self._accounts:
            if account.email_address.lower() == email_address.lower():
                return account
        return None
    
    def get_accounts_by_type(self, account_type: AccountType) -> List[Account]:
        """
        アカウントタイプでフィルタリングしたアカウントリストを取得します
        
        Args:
            account_type (AccountType): アカウントタイプ
            
        Returns:
            List[Account]: フィルタリングされたアカウントリスト
        """
        return [account for account in self._accounts if account.account_type == account_type]
    
    def get_default_account(self) -> Optional[Account]:
        """
        デフォルトアカウントを取得します
        
        Returns:
            Optional[Account]: デフォルトアカウント、設定されていない場合はNone
        """
        for account in self._accounts:
            if getattr(account, 'is_default', False):
                return account
        
        # デフォルトが設定されていない場合は最初のアカウントを返す
        return self._accounts[0] if self._accounts else None
    
    def set_default_account(self, account_id: str) -> bool:
        """
        デフォルトアカウントを設定します
        
        Args:
            account_id (str): デフォルトに設定するアカウントのID
            
        Returns:
            bool: 設定成功時True、失敗時False
        """
        try:
            # 指定されたアカウントが存在するかチェック
            target_account = self.get_account_by_id(account_id)
            if not target_account:
                logger.error(f"デフォルト設定対象のアカウントが見つかりません: {account_id}")
                return False
            
            # すべてのアカウントのデフォルトフラグをクリア
            for account in self._accounts:
                account.is_default = False
            
            # 指定されたアカウントをデフォルトに設定
            target_account.is_default = True
            
            # 変更を保存
            self.save_accounts()
            
            logger.info(f"デフォルトアカウントを設定しました: {target_account.name}")
            return True
            
        except Exception as e:
            logger.error(f"デフォルトアカウント設定エラー: {e}")
            return False
    
    def load_accounts(self):
        """
        ストレージからアカウントを読み込みます
        """
        try:
            self._accounts = self._storage.load_all_accounts()
            logger.info(f"ストレージからアカウントを読み込みました: {len(self._accounts)}個")
            
        except Exception as e:
            logger.error(f"アカウント読み込みエラー: {e}")
            self._accounts = []
    
    def save_accounts(self):
        """
        すべてのアカウントをストレージに保存します
        """
        try:
            for account in self._accounts:
                self._storage.save_account(account)
            logger.debug("すべてのアカウントを保存しました")
            
        except Exception as e:
            logger.error(f"アカウント保存エラー: {e}")
    
    def save_oauth2_token(self, account_id: str, token_data: Dict[str, Any]) -> bool:
        """
        OAuth2トークンを保存します
        
        Args:
            account_id (str): アカウントID
            token_data (Dict[str, Any]): トークンデータ
            
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
        OAuth2トークンを読み込みます
        
        Args:
            account_id (str): アカウントID
            
        Returns:
            Optional[Dict[str, Any]]: トークンデータ
        """
        try:
            return self._storage.load_oauth2_token(account_id)
        except Exception as e:
            logger.error(f"OAuth2トークン読み込みエラー: {e}")
            return None
    
    def get_account_count(self) -> int:
        """
        登録されているアカウント数を取得します
        
        Returns:
            int: アカウント数
        """
        return len(self._accounts)
    
    def is_email_registered(self, email_address: str) -> bool:
        """
        指定されたメールアドレスが既に登録されているかチェックします
        
        Args:
            email_address (str): チェックするメールアドレス
            
        Returns:
            bool: 登録済みの場合True
        """
        return self.get_account_by_email(email_address) is not None
    
    def validate_account_settings(self, account: Account) -> Tuple[bool, List[str]]:
        """
        アカウント設定の妥当性を検証します
        
        Args:
            account (Account): 検証するアカウント
            
        Returns:
            Tuple[bool, List[str]]: (検証結果, エラーメッセージリスト)
        """
        try:
            return account.validate()
        except Exception as e:
            logger.error(f"アカウント検証エラー: {e}")
            return False, [str(e)]
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        ストレージ情報を取得します
        
        Returns:
            Dict[str, Any]: ストレージ情報
        """
        try:
            storage_info = self._storage.get_storage_info()
            storage_info['memory_cache_count'] = len(self._accounts)
            return storage_info
        except Exception as e:
            logger.error(f"ストレージ情報取得エラー: {e}")
            return {}
    
    def backup_accounts(self, backup_path: str) -> bool:
        """
        アカウントデータをバックアップします
        
        Args:
            backup_path (str): バックアップファイルパス
            
        Returns:
            bool: バックアップ成功可否
        """
        try:
            return self._storage.backup_accounts(backup_path)
        except Exception as e:
            logger.error(f"アカウントバックアップエラー: {e}")
            return False
    
    def refresh_accounts(self):
        """
        ストレージからアカウント情報を再読み込みします
        """
        try:
            self.load_accounts()
            logger.info("アカウント情報を再読み込みしました")
        except Exception as e:
            logger.error(f"アカウント再読み込みエラー: {e}")
    
    def close(self):
        """
        リソースを解放します
        """
        try:
            if self._storage:
                self._storage.close()
            logger.debug("AccountManagerのリソースを解放しました")
        except Exception as e:
            logger.error(f"リソース解放エラー: {e}")
    
    def __enter__(self):
        """コンテキストマネージャー開始"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了"""
        self.close()