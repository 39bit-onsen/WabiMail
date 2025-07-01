# -*- coding: utf-8 -*-
"""
メールアカウント管理モジュール

WabiMailでサポートするメールアカウントの情報を管理します。
Gmail、IMAP、SMTP、POPアカウントに対応し、認証情報の安全な管理を行います。

Author: WabiMail Development Team
Created: 2025-07-01
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class AccountType(Enum):
    """
    アカウントタイプ列挙型
    
    WabiMailでサポートするメールサービスのタイプを定義します。
    各タイプに応じて異なる認証方式や設定が適用されます。
    """
    GMAIL = "gmail"          # Gmail（OAuth2認証）
    IMAP = "imap"           # 一般的なIMAPサーバー
    SMTP = "smtp"           # 一般的なSMTPサーバー
    POP3 = "pop3"           # POP3サーバー
    EXCHANGE = "exchange"    # Microsoft Exchange（将来拡張用）


class AuthType(Enum):
    """
    認証タイプ列挙型
    
    メールサーバーへの認証方式を定義します。
    セキュリティレベルに応じて適切な認証方式を選択します。
    """
    PASSWORD = "password"    # ユーザー名・パスワード認証
    OAUTH2 = "oauth2"       # OAuth2認証（Gmail等）
    APP_PASSWORD = "app_password"  # アプリ専用パスワード
    NONE = "none"           # 認証なし（テスト用）


@dataclass
class AccountSettings:
    """
    アカウント設定データクラス
    
    メールアカウントの接続設定を管理します。
    サーバー情報、ポート、暗号化設定等を含みます。
    
    Attributes:
        incoming_server (str): 受信サーバーアドレス
        incoming_port (int): 受信サーバーポート
        incoming_security (str): 受信時の暗号化方式（SSL/TLS/STARTTLS）
        outgoing_server (str): 送信サーバーアドレス
        outgoing_port (int): 送信サーバーポート
        outgoing_security (str): 送信時の暗号化方式
        requires_auth (bool): 送信時認証が必要かどうか
    """
    incoming_server: str = ""
    incoming_port: int = 993
    incoming_security: str = "SSL"  # SSL, TLS, STARTTLS, NONE
    outgoing_server: str = ""
    outgoing_port: int = 587
    outgoing_security: str = "STARTTLS"
    requires_auth: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        設定をディクショナリ形式に変換します
        
        Returns:
            Dict[str, Any]: 設定ディクショナリ
        """
        return {
            "incoming_server": self.incoming_server,
            "incoming_port": self.incoming_port,
            "incoming_security": self.incoming_security,
            "outgoing_server": self.outgoing_server,
            "outgoing_port": self.outgoing_port,
            "outgoing_security": self.outgoing_security,
            "requires_auth": self.requires_auth
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountSettings':
        """
        ディクショナリから設定オブジェクトを作成します
        
        Args:
            data (Dict[str, Any]): 設定ディクショナリ
            
        Returns:
            AccountSettings: 設定オブジェクト
        """
        return cls(
            incoming_server=data.get("incoming_server", ""),
            incoming_port=data.get("incoming_port", 993),
            incoming_security=data.get("incoming_security", "SSL"),
            outgoing_server=data.get("outgoing_server", ""),
            outgoing_port=data.get("outgoing_port", 587),
            outgoing_security=data.get("outgoing_security", "STARTTLS"),
            requires_auth=data.get("requires_auth", True)
        )


@dataclass
class Account:
    """
    メールアカウント情報クラス
    
    WabiMailで管理する個々のメールアカウント情報を格納します。
    アカウントの基本情報、認証情報、サーバー設定を管理します。
    
    Attributes:
        account_id (str): アカウントの一意識別子（UUID）
        name (str): アカウント表示名（例: "仕事用Gmail"）
        email_address (str): メールアドレス
        account_type (AccountType): アカウントタイプ
        auth_type (AuthType): 認証タイプ
        settings (AccountSettings): サーバー設定
        is_active (bool): アカウントが有効かどうか
        is_default (bool): デフォルトアカウントかどうか
        created_at (datetime): アカウント作成日時
        last_sync (Optional[datetime]): 最後の同期日時
        sync_enabled (bool): 自動同期が有効かどうか
        signature (str): メール署名
        display_name (str): 送信者表示名
    """
    account_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email_address: str = ""
    account_type: AccountType = AccountType.IMAP
    auth_type: AuthType = AuthType.PASSWORD
    settings: AccountSettings = field(default_factory=AccountSettings)
    is_active: bool = True
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_sync: Optional[datetime] = None
    sync_enabled: bool = True
    signature: str = ""
    display_name: str = ""
    
    def __post_init__(self):
        """
        初期化後の処理
        
        表示名が空の場合はメールアドレスから自動設定します。
        """
        if not self.display_name and self.email_address:
            # メールアドレスの@より前の部分を表示名として設定
            self.display_name = self.email_address.split('@')[0]
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        アカウント情報の妥当性を検証します
        
        Returns:
            tuple[bool, list[str]]: (検証結果, エラーメッセージリスト)
        """
        errors = []
        
        # 必須項目の確認
        if not self.name.strip():
            errors.append("アカウント名が必要です")
        
        if not self.email_address.strip():
            errors.append("メールアドレスが必要です")
        else:
            # 簡単なメールアドレス形式チェック
            if '@' not in self.email_address or '.' not in self.email_address.split('@')[-1]:
                errors.append("有効なメールアドレスを入力してください")
        
        # アカウントタイプ別の設定確認
        if self.account_type in [AccountType.IMAP, AccountType.POP3]:
            if not self.settings.incoming_server.strip():
                errors.append("受信サーバーが必要です")
        
        if self.account_type in [AccountType.IMAP, AccountType.SMTP]:
            if not self.settings.outgoing_server.strip():
                errors.append("送信サーバーが必要です")
        
        # ポート番号の確認
        if not (1 <= self.settings.incoming_port <= 65535):
            errors.append("受信ポートは1〜65535の範囲で指定してください")
        
        if not (1 <= self.settings.outgoing_port <= 65535):
            errors.append("送信ポートは1〜65535の範囲で指定してください")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def get_preset_settings(self) -> AccountSettings:
        """
        アカウントタイプに基づいてプリセット設定を取得します
        
        Returns:
            AccountSettings: プリセット設定
            
        Note:
            Gmailやよく知られたプロバイダーの設定を自動で適用します
        """
        if self.account_type == AccountType.GMAIL:
            return AccountSettings(
                incoming_server="imap.gmail.com",
                incoming_port=993,
                incoming_security="SSL",
                outgoing_server="smtp.gmail.com",
                outgoing_port=587,
                outgoing_security="STARTTLS",
                requires_auth=True
            )
        
        # 一般的なIMAPの設定例
        elif self.account_type == AccountType.IMAP:
            return AccountSettings(
                incoming_server="",
                incoming_port=993,
                incoming_security="SSL",
                outgoing_server="",
                outgoing_port=587,
                outgoing_security="STARTTLS",
                requires_auth=True
            )
        
        # POP3の設定例
        elif self.account_type == AccountType.POP3:
            return AccountSettings(
                incoming_server="",
                incoming_port=995,
                incoming_security="SSL",
                outgoing_server="",
                outgoing_port=587,
                outgoing_security="STARTTLS",
                requires_auth=True
            )
        
        return AccountSettings()
    
    def apply_preset_settings(self):
        """
        アカウントタイプに基づいてプリセット設定を適用します
        """
        preset = self.get_preset_settings()
        if preset.incoming_server:  # プリセット設定がある場合のみ適用
            self.settings = preset
            logger.debug(f"プリセット設定を適用しました: {self.account_type.value}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        アカウント情報をディクショナリ形式に変換します
        
        Returns:
            Dict[str, Any]: アカウント情報ディクショナリ
            
        Note:
            パスワード等の機密情報は含まれません。
            設定ファイル保存時に使用されます。
        """
        return {
            "account_id": self.account_id,
            "name": self.name,
            "email_address": self.email_address,
            "account_type": self.account_type.value,
            "auth_type": self.auth_type.value,
            "settings": self.settings.to_dict(),
            "is_active": self.is_active,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat(),
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "sync_enabled": self.sync_enabled,
            "signature": self.signature,
            "display_name": self.display_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        """
        ディクショナリからアカウントオブジェクトを作成します
        
        Args:
            data (Dict[str, Any]): アカウント情報ディクショナリ
            
        Returns:
            Account: アカウントオブジェクト
        """
        # 日時の復元
        created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        last_sync = None
        if data.get("last_sync"):
            last_sync = datetime.fromisoformat(data["last_sync"])
        
        return cls(
            account_id=data.get("account_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            email_address=data.get("email_address", ""),
            account_type=AccountType(data.get("account_type", "imap")),
            auth_type=AuthType(data.get("auth_type", "password")),
            settings=AccountSettings.from_dict(data.get("settings", {})),
            is_active=data.get("is_active", True),
            is_default=data.get("is_default", False),
            created_at=created_at,
            last_sync=last_sync,
            sync_enabled=data.get("sync_enabled", True),
            signature=data.get("signature", ""),
            display_name=data.get("display_name", "")
        )
    
    def __str__(self) -> str:
        """
        文字列表現を返します
        
        Returns:
            str: アカウントの文字列表現
        """
        status = "有効" if self.is_active else "無効"
        default = " (デフォルト)" if self.is_default else ""
        return f"{self.name} <{self.email_address}> [{self.account_type.value}] {status}{default}"