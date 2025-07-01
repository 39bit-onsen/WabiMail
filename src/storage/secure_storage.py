# -*- coding: utf-8 -*-
"""
セキュアストレージモジュール

WabiMailの統合的な暗号化データストレージシステムです。
機密情報（アカウント情報、パスワード、トークン）の安全な保存・読み込みを提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from cryptography.fernet import Fernet
import base64
import platform

from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class SecureStorage:
    """
    セキュアストレージクラス
    
    WabiMailの機密データを暗号化して安全に保存・管理します。
    プラットフォーム別のセキュアディレクトリに暗号化されたデータベースを作成し、
    アカウント情報、設定、トークンなどを統合的に管理します。
    
    Attributes:
        storage_dir (Path): データ保存ディレクトリ
        db_path (Path): SQLiteデータベースファイルパス
        encryption_key (bytes): 暗号化キー
        _fernet (Fernet): 暗号化オブジェクト
        _conn (sqlite3.Connection): データベース接続
    
    Note:
        データは暗号化されてプラットフォーム別のアプリケーションディレクトリに保存されます。
        Windows: %APPDATA%/WabiMail/
        macOS: ~/Library/Application Support/WabiMail/
        Linux: ~/.local/share/WabiMail/
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        セキュアストレージを初期化します
        
        Args:
            storage_dir: カスタムストレージディレクトリ（テスト用）
        """
        # ストレージディレクトリを決定
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = self._get_app_data_dir()
        
        # ディレクトリを作成
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # データベースファイルパス
        self.db_path = self.storage_dir / "wabimail_data.db"
        
        # 暗号化キーの初期化
        self.encryption_key = self._get_or_create_encryption_key()
        self._fernet = Fernet(self.encryption_key)
        
        # データベース接続とテーブル作成
        self._conn = None
        self._init_database()
        
        logger.info(f"セキュアストレージを初期化しました: {self.storage_dir}")
    
    def _get_app_data_dir(self) -> Path:
        """
        プラットフォーム別のアプリケーションデータディレクトリを取得
        
        Returns:
            Path: アプリケーションデータディレクトリ
        """
        system = platform.system()
        
        if system == "Windows":
            # Windows: %APPDATA%/WabiMail/
            app_data = Path(os.environ.get("APPDATA", ""))
            return app_data / "WabiMail"
        elif system == "Darwin":
            # macOS: ~/Library/Application Support/WabiMail/
            return Path.home() / "Library" / "Application Support" / "WabiMail"
        else:
            # Linux/Unix: ~/.local/share/WabiMail/
            xdg_data_home = os.environ.get("XDG_DATA_HOME")
            if xdg_data_home:
                return Path(xdg_data_home) / "WabiMail"
            else:
                return Path.home() / ".local" / "share" / "WabiMail"
    
    def _get_or_create_encryption_key(self) -> bytes:
        """
        暗号化キーを取得または新規作成
        
        Returns:
            bytes: 暗号化キー
        """
        key_file = self.storage_dir / ".encryption_key"
        
        try:
            if key_file.exists():
                # 既存のキーを読み込み
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # 新しいキーを生成
                key = Fernet.generate_key()
                
                # キーファイルを作成（読み取り専用）
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # セキュリティのためファイル権限を設定（Unix系のみ）
                if platform.system() != "Windows":
                    os.chmod(key_file, 0o600)
                
                logger.info("新しい暗号化キーを生成しました")
                return key
                
        except Exception as e:
            logger.error(f"暗号化キーの取得エラー: {e}")
            raise
    
    def _init_database(self):
        """
        データベースとテーブルを初期化
        """
        try:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row  # 辞書形式でアクセス可能
            
            # テーブル作成
            self._create_tables()
            
            logger.debug("データベースを初期化しました")
            
        except Exception as e:
            logger.error(f"データベース初期化エラー: {e}")
            raise
    
    def _create_tables(self):
        """
        必要なテーブルを作成
        """
        cursor = self._conn.cursor()
        
        # アカウント情報テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email_address TEXT NOT NULL UNIQUE,
                account_type TEXT NOT NULL,
                auth_type TEXT NOT NULL,
                encrypted_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # OAuth2トークンテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oauth2_tokens (
                account_id TEXT PRIMARY KEY,
                encrypted_token TEXT NOT NULL,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        
        # アプリケーション設定テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                encrypted_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # メールローカルキャッシュテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mail_cache (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                folder TEXT NOT NULL,
                uid TEXT NOT NULL,
                encrypted_message TEXT NOT NULL,
                flags TEXT,
                date_received TIMESTAMP,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id),
                UNIQUE(account_id, folder, uid)
            )
        """)
        
        # インデックス作成
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_email ON accounts(email_address)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mail_cache_account ON mail_cache(account_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mail_cache_folder ON mail_cache(account_id, folder)")
        
        self._conn.commit()
        logger.debug("データベーステーブルを作成しました")
    
    def encrypt_data(self, data: Union[str, dict, list]) -> str:
        """
        データを暗号化
        
        Args:
            data: 暗号化するデータ
            
        Returns:
            str: 暗号化されたデータ（Base64エンコード済み）
        """
        try:
            # データをJSON文字列に変換
            if isinstance(data, str):
                json_data = data
            else:
                json_data = json.dumps(data, ensure_ascii=False)
            
            # 暗号化
            encrypted_bytes = self._fernet.encrypt(json_data.encode('utf-8'))
            
            # Base64エンコードして文字列として返す
            return base64.b64encode(encrypted_bytes).decode('utf-8')
            
        except Exception as e:
            logger.error(f"データ暗号化エラー: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str, return_type: str = 'auto') -> Union[str, dict, list]:
        """
        暗号化されたデータを復号
        
        Args:
            encrypted_data: 暗号化されたデータ
            return_type: 戻り値の型 ('auto', 'str', 'dict', 'list')
            
        Returns:
            復号されたデータ
        """
        try:
            # Base64デコード
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # 復号
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            json_data = decrypted_bytes.decode('utf-8')
            
            # 戻り値の型に応じて変換
            if return_type == 'str':
                return json_data
            elif return_type in ('auto', 'dict', 'list'):
                try:
                    parsed_data = json.loads(json_data)
                    return parsed_data
                except json.JSONDecodeError:
                    return json_data
            else:
                return json_data
                
        except Exception as e:
            logger.error(f"データ復号エラー: {e}")
            raise
    
    def save_account(self, account_data: Dict[str, Any]) -> bool:
        """
        アカウント情報を暗号化して保存
        
        Args:
            account_data: アカウントデータ
            
        Returns:
            bool: 保存成功可否
        """
        try:
            # 機密情報を暗号化
            sensitive_data = {
                'settings': account_data.get('settings', {}),
                'credentials': account_data.get('credentials', {}),
                'display_name': account_data.get('display_name', ''),
                'signature': account_data.get('signature', '')
            }
            
            encrypted_data = self.encrypt_data(sensitive_data)
            
            cursor = self._conn.cursor()
            
            # アカウント情報を保存（UPSERT）
            cursor.execute("""
                INSERT OR REPLACE INTO accounts 
                (id, name, email_address, account_type, auth_type, encrypted_data, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                account_data['id'],
                account_data['name'],
                account_data['email_address'],
                account_data['account_type'],
                account_data['auth_type'],
                encrypted_data,
                datetime.now()
            ))
            
            self._conn.commit()
            logger.info(f"アカウント情報を保存しました: {account_data['email_address']}")
            return True
            
        except Exception as e:
            logger.error(f"アカウント保存エラー: {e}")
            return False
    
    def load_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        アカウント情報を読み込み
        
        Args:
            account_id: アカウントID
            
        Returns:
            Optional[Dict]: アカウントデータ
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                SELECT * FROM accounts WHERE id = ?
            """, (account_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # 暗号化データを復号
            decrypted_data = self.decrypt_data(row['encrypted_data'])
            
            # アカウントデータを再構築
            account_data = {
                'id': row['id'],
                'name': row['name'],
                'email_address': row['email_address'],
                'account_type': row['account_type'],
                'auth_type': row['auth_type'],
                'settings': decrypted_data.get('settings', {}),
                'credentials': decrypted_data.get('credentials', {}),
                'display_name': decrypted_data.get('display_name', ''),
                'signature': decrypted_data.get('signature', ''),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            
            return account_data
            
        except Exception as e:
            logger.error(f"アカウント読み込みエラー: {e}")
            return None
    
    def list_accounts(self) -> List[Dict[str, Any]]:
        """
        すべてのアカウント情報を取得
        
        Returns:
            List[Dict]: アカウントリスト
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                SELECT id, name, email_address, account_type, auth_type, created_at, updated_at
                FROM accounts
                ORDER BY created_at
            """)
            
            accounts = []
            for row in cursor.fetchall():
                accounts.append({
                    'id': row['id'],
                    'name': row['name'],
                    'email_address': row['email_address'],
                    'account_type': row['account_type'],
                    'auth_type': row['auth_type'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            return accounts
            
        except Exception as e:
            logger.error(f"アカウントリスト取得エラー: {e}")
            return []
    
    def delete_account(self, account_id: str) -> bool:
        """
        アカウント情報を削除
        
        Args:
            account_id: アカウントID
            
        Returns:
            bool: 削除成功可否
        """
        try:
            cursor = self._conn.cursor()
            
            # 関連データを削除
            cursor.execute("DELETE FROM oauth2_tokens WHERE account_id = ?", (account_id,))
            cursor.execute("DELETE FROM mail_cache WHERE account_id = ?", (account_id,))
            cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            
            self._conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"アカウントを削除しました: {account_id}")
                return True
            else:
                logger.warning(f"削除対象のアカウントが見つかりません: {account_id}")
                return False
                
        except Exception as e:
            logger.error(f"アカウント削除エラー: {e}")
            return False
    
    def save_oauth2_token(self, account_id: str, token_data: Dict[str, Any]) -> bool:
        """
        OAuth2トークンを暗号化して保存
        
        Args:
            account_id: アカウントID
            token_data: トークンデータ
            
        Returns:
            bool: 保存成功可否
        """
        try:
            encrypted_token = self.encrypt_data(token_data)
            
            # 有効期限の計算
            expires_at = None
            if 'expires_in' in token_data:
                expires_at = datetime.now().timestamp() + token_data['expires_in']
                expires_at = datetime.fromtimestamp(expires_at)
            
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO oauth2_tokens 
                (account_id, encrypted_token, expires_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (account_id, encrypted_token, expires_at, datetime.now()))
            
            self._conn.commit()
            logger.info(f"OAuth2トークンを保存しました: {account_id}")
            return True
            
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
            cursor = self._conn.cursor()
            cursor.execute("""
                SELECT encrypted_token, expires_at FROM oauth2_tokens 
                WHERE account_id = ?
            """, (account_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # トークンデータを復号
            token_data = self.decrypt_data(row['encrypted_token'])
            
            # 有効期限チェック
            if row['expires_at']:
                expires_at = datetime.fromisoformat(row['expires_at'])
                if datetime.now() > expires_at:
                    logger.warning(f"OAuth2トークンが期限切れです: {account_id}")
                    return None
            
            return token_data
            
        except Exception as e:
            logger.error(f"OAuth2トークン読み込みエラー: {e}")
            return None
    
    def save_app_setting(self, key: str, value: Any) -> bool:
        """
        アプリケーション設定を暗号化して保存
        
        Args:
            key: 設定キー
            value: 設定値
            
        Returns:
            bool: 保存成功可否
        """
        try:
            encrypted_value = self.encrypt_data(value)
            
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO app_settings 
                (key, encrypted_value, updated_at)
                VALUES (?, ?, ?)
            """, (key, encrypted_value, datetime.now()))
            
            self._conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"設定保存エラー: {e}")
            return False
    
    def load_app_setting(self, key: str, default: Any = None) -> Any:
        """
        アプリケーション設定を読み込み
        
        Args:
            key: 設定キー
            default: デフォルト値
            
        Returns:
            設定値
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                SELECT encrypted_value FROM app_settings WHERE key = ?
            """, (key,))
            
            row = cursor.fetchone()
            if not row:
                return default
            
            return self.decrypt_data(row['encrypted_value'])
            
        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}")
            return default
    
    def close(self):
        """
        データベース接続を閉じる
        """
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.debug("データベース接続を閉じました")
    
    def __enter__(self):
        """コンテキストマネージャー開始"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了"""
        self.close()
    
    def backup_data(self, backup_path: str) -> bool:
        """
        データベースをバックアップ
        
        Args:
            backup_path: バックアップファイルパス
            
        Returns:
            bool: バックアップ成功可否
        """
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"データベースをバックアップしました: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"バックアップエラー: {e}")
            return False
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        ストレージ情報を取得
        
        Returns:
            Dict: ストレージ情報
        """
        try:
            cursor = self._conn.cursor()
            
            # 各テーブルのレコード数を取得
            cursor.execute("SELECT COUNT(*) as count FROM accounts")
            accounts_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM oauth2_tokens")
            tokens_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM app_settings")
            settings_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM mail_cache")
            mail_cache_count = cursor.fetchone()['count']
            
            # データベースファイルサイズ
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            return {
                'storage_dir': str(self.storage_dir),
                'database_path': str(self.db_path),
                'database_size_bytes': db_size,
                'accounts_count': accounts_count,
                'tokens_count': tokens_count,
                'settings_count': settings_count,
                'mail_cache_count': mail_cache_count,
                'encryption_enabled': True
            }
            
        except Exception as e:
            logger.error(f"ストレージ情報取得エラー: {e}")
            return {}