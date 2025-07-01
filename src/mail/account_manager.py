# -*- coding: utf-8 -*-
"""
アカウント管理モジュール

複数のメールアカウントを一元管理するためのマネージャークラスです。
アカウントの追加、削除、更新、暗号化保存機能を提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import yaml

from src.mail.account import Account, AccountType, AuthType
from src.utils.logger import get_logger
from src.config.app_config import AppConfig

# ロガーを取得
logger = get_logger(__name__)


class AccountManager:
    """
    メールアカウント管理クラス
    
    WabiMailのすべてのメールアカウントを管理します。
    アカウントの追加、削除、更新、暗号化保存、読み込み機能を提供します。
    
    Attributes:
        _accounts (List[Account]): 管理対象のアカウントリスト
        _config (AppConfig): アプリケーション設定
        _accounts_file (Path): アカウント情報保存ファイル
    """
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        AccountManagerを初期化します
        
        Args:
            config (AppConfig, optional): アプリケーション設定
                                        Noneの場合は新規作成
        """
        self._accounts: List[Account] = []
        self._config = config or AppConfig()
        
        # アカウント情報保存ディレクトリ・ファイルパス
        self._accounts_dir = Path(self._config.config_dir) / "accounts"
        self._accounts_dir.mkdir(exist_ok=True)
        self._accounts_file = self._accounts_dir / "accounts.yaml"
        
        # 既存アカウントを読み込み
        self.load_accounts()
        
        logger.info(f"アカウントマネージャーを初期化しました: {len(self._accounts)}個のアカウント")
    
    def add_account(self, account: Account) -> bool:
        """
        アカウントを追加します
        
        Args:
            account (Account): 追加するアカウント
            
        Returns:
            bool: 追加成功時True、失敗時False
        """
        try:
            # アカウント情報の妥当性確認
            is_valid, errors = account.validate()
            if not is_valid:
                logger.error(f"アカウント追加失敗 - 検証エラー: {errors}")
                return False
            
            # 同じメールアドレスのアカウントが既に存在するかチェック
            if self.get_account_by_email(account.email_address):
                logger.error(f"アカウント追加失敗 - 既に存在: {account.email_address}")
                return False
            
            # 初回追加の場合はデフォルトアカウントに設定
            if len(self._accounts) == 0:
                account.is_default = True
            
            # アカウントタイプに応じてプリセット設定を適用
            account.apply_preset_settings()
            
            # アカウントを追加
            self._accounts.append(account)
            
            # ファイルに保存
            self.save_accounts()
            
            logger.info(f"アカウントを追加しました: {account.name} <{account.email_address}>")
            return True
            
        except Exception as e:
            logger.error(f"アカウント追加中にエラーが発生しました: {e}")
            return False
    
    def remove_account(self, account_id: str) -> bool:
        """
        アカウントを削除します
        
        Args:
            account_id (str): 削除するアカウントのID
            
        Returns:
            bool: 削除成功時True、失敗時False
        """
        try:
            account = self.get_account_by_id(account_id)
            if not account:
                logger.error(f"アカウント削除失敗 - アカウントが見つかりません: {account_id}")
                return False
            
            # デフォルトアカウントを削除する場合の処理
            was_default = account.is_default
            
            # アカウントを削除
            self._accounts = [acc for acc in self._accounts if acc.account_id != account_id]
            
            # デフォルトアカウントが削除された場合、他のアカウントをデフォルトに設定
            if was_default and self._accounts:
                self._accounts[0].is_default = True
                logger.info(f"新しいデフォルトアカウント: {self._accounts[0].name}")
            
            # ファイルに保存
            self.save_accounts()
            
            logger.info(f"アカウントを削除しました: {account.name} <{account.email_address}>")
            return True
            
        except Exception as e:
            logger.error(f"アカウント削除中にエラーが発生しました: {e}")
            return False
    
    def update_account(self, account_id: str, updated_account: Account) -> bool:
        """
        アカウント情報を更新します
        
        Args:
            account_id (str): 更新するアカウントのID
            updated_account (Account): 更新後のアカウント情報
            
        Returns:
            bool: 更新成功時True、失敗時False
        """
        try:
            # 更新対象のアカウントを検索
            for i, account in enumerate(self._accounts):
                if account.account_id == account_id:
                    # 妥当性確認
                    is_valid, errors = updated_account.validate()
                    if not is_valid:
                        logger.error(f"アカウント更新失敗 - 検証エラー: {errors}")
                        return False
                    
                    # IDは変更不可
                    updated_account.account_id = account_id
                    
                    # アカウント情報を更新
                    self._accounts[i] = updated_account
                    
                    # ファイルに保存
                    self.save_accounts()
                    
                    logger.info(f"アカウントを更新しました: {updated_account.name}")
                    return True
            
            logger.error(f"アカウント更新失敗 - アカウントが見つかりません: {account_id}")
            return False
            
        except Exception as e:
            logger.error(f"アカウント更新中にエラーが発生しました: {e}")
            return False
    
    def get_account_by_id(self, account_id: str) -> Optional[Account]:
        """
        アカウントIDでアカウントを取得します
        
        Args:
            account_id (str): アカウントID
            
        Returns:
            Optional[Account]: 見つかったアカウント、存在しない場合None
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
            Optional[Account]: 見つかったアカウント、存在しない場合None
        """
        for account in self._accounts:
            if account.email_address.lower() == email_address.lower():
                return account
        return None
    
    def get_all_accounts(self) -> List[Account]:
        """
        すべてのアカウントを取得します
        
        Returns:
            List[Account]: アカウントリスト（コピー）
        """
        return self._accounts.copy()
    
    def get_active_accounts(self) -> List[Account]:
        """
        有効なアカウントのみを取得します
        
        Returns:
            List[Account]: 有効なアカウントリスト
        """
        return [account for account in self._accounts if account.is_active]
    
    def get_default_account(self) -> Optional[Account]:
        """
        デフォルトアカウントを取得します
        
        Returns:
            Optional[Account]: デフォルトアカウント、存在しない場合None
        """
        for account in self._accounts:
            if account.is_default:
                return account
        return None
    
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
                logger.error(f"デフォルトアカウント設定失敗 - アカウントが見つかりません: {account_id}")
                return False
            
            # 全アカウントのデフォルトフラグをクリア
            for account in self._accounts:
                account.is_default = False
            
            # 指定されたアカウントをデフォルトに設定
            target_account.is_default = True
            
            # ファイルに保存
            self.save_accounts()
            
            logger.info(f"デフォルトアカウントを設定しました: {target_account.name}")
            return True
            
        except Exception as e:
            logger.error(f"デフォルトアカウント設定中にエラーが発生しました: {e}")
            return False
    
    def update_last_sync(self, account_id: str, sync_time: Optional[datetime] = None) -> bool:
        """
        アカウントの最終同期時刻を更新します
        
        Args:
            account_id (str): アカウントID
            sync_time (datetime, optional): 同期時刻（Noneの場合は現在時刻）
            
        Returns:
            bool: 更新成功時True、失敗時False
        """
        try:
            account = self.get_account_by_id(account_id)
            if not account:
                return False
            
            account.last_sync = sync_time or datetime.now()
            self.save_accounts()
            
            logger.debug(f"最終同期時刻を更新しました: {account.name}")
            return True
            
        except Exception as e:
            logger.error(f"最終同期時刻更新中にエラーが発生しました: {e}")
            return False
    
    def get_accounts_by_type(self, account_type: AccountType) -> List[Account]:
        """
        指定されたタイプのアカウントを取得します
        
        Args:
            account_type (AccountType): アカウントタイプ
            
        Returns:
            List[Account]: 指定タイプのアカウントリスト
        """
        return [account for account in self._accounts if account.account_type == account_type]
    
    def save_accounts(self):
        """
        アカウント情報をファイルに保存します
        
        Note:
            現在は平文で保存していますが、将来的には暗号化保存を実装予定です。
            パスワード等の機密情報は別途安全に管理される予定です。
        """
        try:
            # アカウント情報をディクショナリ形式に変換
            accounts_data = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "accounts": [account.to_dict() for account in self._accounts]
            }
            
            # YAMLファイルに保存
            with open(self._accounts_file, 'w', encoding='utf-8') as f:
                yaml.dump(
                    accounts_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2
                )
            
            logger.debug(f"アカウント情報を保存しました: {self._accounts_file}")
            
        except Exception as e:
            logger.error(f"アカウント情報保存中にエラーが発生しました: {e}")
            raise
    
    def load_accounts(self):
        """
        ファイルからアカウント情報を読み込みます
        
        Note:
            ファイルが存在しない場合は空のアカウントリストで初期化されます。
        """
        try:
            if not self._accounts_file.exists():
                logger.info("アカウントファイルが見つかりません。新規作成します。")
                self._accounts = []
                return
            
            # YAMLファイルから読み込み
            with open(self._accounts_file, 'r', encoding='utf-8') as f:
                accounts_data = yaml.safe_load(f) or {}
            
            # アカウントリストを復元
            accounts_list = accounts_data.get("accounts", [])
            self._accounts = []
            
            for account_data in accounts_list:
                try:
                    account = Account.from_dict(account_data)
                    self._accounts.append(account)
                except Exception as e:
                    logger.warning(f"アカウント読み込みエラー（スキップ）: {e}")
                    continue
            
            logger.info(f"アカウント情報を読み込みました: {len(self._accounts)}個")
            
        except Exception as e:
            logger.error(f"アカウント情報読み込み中にエラーが発生しました: {e}")
            self._accounts = []
    
    def export_accounts(self, export_path: str, include_sensitive: bool = False) -> bool:
        """
        アカウント情報をエクスポートします
        
        Args:
            export_path (str): エクスポート先ファイルパス
            include_sensitive (bool): 機密情報を含めるかどうか
            
        Returns:
            bool: エクスポート成功時True、失敗時False
        """
        try:
            export_data = {
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "wabimail_export": True,
                "include_sensitive": include_sensitive,
                "accounts": []
            }
            
            for account in self._accounts:
                account_data = account.to_dict()
                
                # 機密情報を含めない場合は除外
                if not include_sensitive:
                    # パスワード等の機密情報は除外
                    # （現在の実装では認証情報は別管理のため、特に除外する項目なし）
                    pass
                
                export_data["accounts"].append(account_data)
            
            # JSONファイルとして保存（可読性重視）
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"アカウント情報をエクスポートしました: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"アカウントエクスポート中にエラーが発生しました: {e}")
            return False
    
    def get_account_count(self) -> int:
        """
        管理対象のアカウント数を取得します
        
        Returns:
            int: アカウント数
        """
        return len(self._accounts)
    
    def get_account_statistics(self) -> Dict[str, Any]:
        """
        アカウントの統計情報を取得します
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        total = len(self._accounts)
        active = len(self.get_active_accounts())
        
        # タイプ別の統計
        type_stats = {}
        for account_type in AccountType:
            type_stats[account_type.value] = len(self.get_accounts_by_type(account_type))
        
        return {
            "total_accounts": total,
            "active_accounts": active,
            "inactive_accounts": total - active,
            "type_statistics": type_stats,
            "has_default": self.get_default_account() is not None
        }