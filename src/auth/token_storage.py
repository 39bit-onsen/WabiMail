# -*- coding: utf-8 -*-
"""
トークンストレージモジュール

OAuth2トークンの安全な保存・読み込み・管理を提供します。
暗号化による機密情報の保護と、リフレッシュトークンの適切な管理を行います。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64

from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class TokenStorage:
    """
    OAuth2トークンストレージクラス
    
    OAuth2アクセストークン・リフレッシュトークンの安全な保存・読み込みを管理します。
    暗号化による機密情報の保護と、トークンの有効期限管理を提供します。
    
    Attributes:
        storage_dir (Path): トークン保存ディレクトリ
        encryption_key (bytes): 暗号化キー
        _fernet (Fernet): 暗号化オブジェクト
    
    Note:
        トークンは暗号化されてユーザーのアプリケーションデータディレクトリに保存されます。
        Windows: %APPDATA%/WabiMail/tokens/
        macOS: ~/Library/Application Support/WabiMail/tokens/
        Linux: ~/.local/share/WabiMail/tokens/
    """
    
    def __init__(self):
        """
        トークンストレージを初期化します
        """
        # プラットフォーム別のアプリケーションデータディレクトリを取得
        self.storage_dir = self._get_app_data_dir() / "tokens"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 暗号化キーの初期化
        self.encryption_key = self._get_or_create_encryption_key()
        self._fernet = Fernet(self.encryption_key)
        
        logger.debug(f"トークンストレージを初期化しました: {self.storage_dir}")
    
    def _get_app_data_dir(self) -> Path:
        """
        プラットフォーム別のアプリケーションデータディレクトリを取得します
        
        Returns:
            Path: アプリケーションデータディレクトリ
        """
        if os.name == 'nt':  # Windows
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            return Path(app_data) / "WabiMail"
        elif os.name == 'posix':
            if 'darwin' in os.uname().sysname.lower():  # macOS
                return Path.home() / "Library" / "Application Support" / "WabiMail"
            else:  # Linux
                xdg_data_home = os.environ.get('XDG_DATA_HOME', Path.home() / ".local" / "share")
                return Path(xdg_data_home) / "WabiMail"
        else:
            # その他のプラットフォーム
            return Path.home() / ".wabimail"
    
    def _get_or_create_encryption_key(self) -> bytes:
        """
        暗号化キーを取得または作成します
        
        Returns:
            bytes: 暗号化キー
        """
        key_file = self.storage_dir / ".encryption_key"
        
        try:
            if key_file.exists():
                # 既存のキーを読み込み
                with open(key_file, 'rb') as f:
                    key = f.read()
                logger.debug("既存の暗号化キーを読み込みました")
                return key
            else:
                # 新しいキーを生成
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # キーファイルのパーミッションを制限（Unix系）
                if os.name == 'posix':
                    os.chmod(key_file, 0o600)
                
                logger.info("新しい暗号化キーを生成しました")
                return key
                
        except Exception as e:
            logger.error(f"暗号化キーの処理エラー: {e}")
            raise
    
    def save_token(self, account_id: str, token_data: Dict[str, Any]) -> bool:
        """
        OAuth2トークンを暗号化して保存します
        
        Args:
            account_id: アカウント識別子
            token_data: トークンデータ（access_token, refresh_token, expires_in等）
            
        Returns:
            bool: 保存成功時True、失敗時False
        """
        try:
            # トークンデータに保存日時を追加
            token_data_with_metadata = {
                **token_data,
                'saved_at': datetime.now().isoformat(),
                'account_id': account_id
            }
            
            # JSON形式でシリアライズ
            token_json = json.dumps(token_data_with_metadata, ensure_ascii=False, indent=2)
            token_bytes = token_json.encode('utf-8')
            
            # 暗号化
            encrypted_token = self._fernet.encrypt(token_bytes)
            
            # ファイルに保存
            token_file = self.storage_dir / f"{account_id}_token.enc"
            with open(token_file, 'wb') as f:
                f.write(encrypted_token)
            
            # ファイルパーミッションを制限（Unix系）
            if os.name == 'posix':
                os.chmod(token_file, 0o600)
            
            logger.info(f"トークンを保存しました: {account_id}")
            return True
            
        except Exception as e:
            logger.error(f"トークン保存エラー ({account_id}): {e}")
            return False
    
    def load_token(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        OAuth2トークンを読み込み・復号化します
        
        Args:
            account_id: アカウント識別子
            
        Returns:
            Optional[Dict[str, Any]]: トークンデータ、見つからない場合None
        """
        try:
            token_file = self.storage_dir / f"{account_id}_token.enc"
            
            if not token_file.exists():
                logger.debug(f"トークンファイルが見つかりません: {account_id}")
                return None
            
            # 暗号化されたトークンを読み込み
            with open(token_file, 'rb') as f:
                encrypted_token = f.read()
            
            # 復号化
            token_bytes = self._fernet.decrypt(encrypted_token)
            token_json = token_bytes.decode('utf-8')
            
            # JSONデシリアライズ
            token_data = json.loads(token_json)
            
            logger.debug(f"トークンを読み込みました: {account_id}")
            return token_data
            
        except Exception as e:
            logger.error(f"トークン読み込みエラー ({account_id}): {e}")
            return None
    
    def delete_token(self, account_id: str) -> bool:
        """
        OAuth2トークンを削除します
        
        Args:
            account_id: アカウント識別子
            
        Returns:
            bool: 削除成功時True、失敗時False
        """
        try:
            token_file = self.storage_dir / f"{account_id}_token.enc"
            
            if token_file.exists():
                token_file.unlink()
                logger.info(f"トークンを削除しました: {account_id}")
                return True
            else:
                logger.debug(f"削除対象のトークンファイルが見つかりません: {account_id}")
                return False
                
        except Exception as e:
            logger.error(f"トークン削除エラー ({account_id}): {e}")
            return False
    
    def is_token_expired(self, token_data: Dict[str, Any]) -> bool:
        """
        トークンの有効期限をチェックします
        
        Args:
            token_data: トークンデータ
            
        Returns:
            bool: 期限切れの場合True、有効な場合False
        """
        try:
            # expires_in（秒）と保存日時から有効期限を計算
            expires_in = token_data.get('expires_in', 3600)  # デフォルト1時間
            saved_at_str = token_data.get('saved_at')
            
            if not saved_at_str:
                logger.warning("トークンの保存日時が見つかりません")
                return True
            
            saved_at = datetime.fromisoformat(saved_at_str)
            expires_at = saved_at + timedelta(seconds=expires_in)
            
            # 5分のマージンを設けて期限をチェック
            now = datetime.now()
            is_expired = now >= (expires_at - timedelta(minutes=5))
            
            if is_expired:
                logger.debug(f"トークンが期限切れです: 有効期限 {expires_at}, 現在時刻 {now}")
            
            return is_expired
            
        except Exception as e:
            logger.error(f"トークン期限チェックエラー: {e}")
            return True
    
    def list_stored_tokens(self) -> list[str]:
        """
        保存されているトークンのアカウントIDリストを取得します
        
        Returns:
            list[str]: アカウントIDのリスト
        """
        try:
            account_ids = []
            
            for token_file in self.storage_dir.glob("*_token.enc"):
                account_id = token_file.stem.replace("_token", "")
                account_ids.append(account_id)
            
            logger.debug(f"保存済みトークン数: {len(account_ids)}")
            return account_ids
            
        except Exception as e:
            logger.error(f"トークンリスト取得エラー: {e}")
            return []
    
    def backup_tokens(self, backup_path: Path) -> bool:
        """
        すべてのトークンをバックアップします
        
        Args:
            backup_path: バックアップファイルパス
            
        Returns:
            bool: バックアップ成功時True、失敗時False
            
        Note:
            バックアップファイルも暗号化されます
        """
        try:
            all_tokens = {}
            
            for account_id in self.list_stored_tokens():
                token_data = self.load_token(account_id)
                if token_data:
                    all_tokens[account_id] = token_data
            
            if not all_tokens:
                logger.info("バックアップ対象のトークンがありません")
                return True
            
            # バックアップデータを暗号化
            backup_json = json.dumps(all_tokens, ensure_ascii=False, indent=2)
            backup_bytes = backup_json.encode('utf-8')
            encrypted_backup = self._fernet.encrypt(backup_bytes)
            
            # バックアップファイルに保存
            with open(backup_path, 'wb') as f:
                f.write(encrypted_backup)
            
            logger.info(f"トークンバックアップを作成しました: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"トークンバックアップエラー: {e}")
            return False
    
    def restore_tokens(self, backup_path: Path) -> bool:
        """
        バックアップからトークンを復元します
        
        Args:
            backup_path: バックアップファイルパス
            
        Returns:
            bool: 復元成功時True、失敗時False
        """
        try:
            if not backup_path.exists():
                logger.error(f"バックアップファイルが見つかりません: {backup_path}")
                return False
            
            # バックアップファイルを読み込み・復号化
            with open(backup_path, 'rb') as f:
                encrypted_backup = f.read()
            
            backup_bytes = self._fernet.decrypt(encrypted_backup)
            backup_json = backup_bytes.decode('utf-8')
            all_tokens = json.loads(backup_json)
            
            # 各トークンを復元
            restored_count = 0
            for account_id, token_data in all_tokens.items():
                if self.save_token(account_id, token_data):
                    restored_count += 1
            
            logger.info(f"トークンを復元しました: {restored_count}個のアカウント")
            return restored_count > 0
            
        except Exception as e:
            logger.error(f"トークン復元エラー: {e}")
            return False
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        ストレージ情報を取得します
        
        Returns:
            Dict[str, Any]: ストレージ情報
        """
        try:
            stored_tokens = self.list_stored_tokens()
            
            info = {
                'storage_directory': str(self.storage_dir),
                'stored_account_count': len(stored_tokens),
                'stored_accounts': stored_tokens,
                'encryption_enabled': True,
                'last_accessed': datetime.now().isoformat()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"ストレージ情報取得エラー: {e}")
            return {
                'error': str(e),
                'storage_directory': str(self.storage_dir),
                'encryption_enabled': True
            }