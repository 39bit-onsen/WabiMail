# -*- coding: utf-8 -*-
"""
OAuth2設定モジュール

Gmail OAuth2認証に関する設定定数と設定管理を提供します。
Google Cloud Console プロジェクトの設定値やAPIスコープを管理します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

from pathlib import Path
from typing import Dict, Any, List

# Gmail API OAuth2 設定
class OAuth2Config:
    """
    OAuth2認証設定クラス
    
    Gmail API OAuth2認証に関する設定値を管理します。
    Google Cloud Console プロジェクトの設定に合わせて調整してください。
    """
    
    # Gmail API必要スコープ
    GMAIL_SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',      # メール読み取り
        'https://www.googleapis.com/auth/gmail.send',          # メール送信  
        'https://www.googleapis.com/auth/gmail.compose',       # メール作成
        'https://www.googleapis.com/auth/gmail.modify'         # メール変更（既読マーク等）
    ]
    
    # OAuth2フロー設定
    CALLBACK_PORT_RANGE = (8080, 8090)  # コールバック用ポート範囲
    DEFAULT_CALLBACK_PORT = 8080         # デフォルトコールバックポート
    AUTH_TIMEOUT_SECONDS = 300           # 認証タイムアウト（5分）
    
    # client_secret.json 検索パス
    CLIENT_SECRET_SEARCH_PATHS = [
        "client_secret.json",                    # カレントディレクトリ
        "config/client_secret.json",             # configディレクトリ
        "credentials/client_secret.json",        # credentialsディレクトリ
        "../client_secret.json",                 # 親ディレクトリ
        "~/WabiMail/client_secret.json"          # ホームディレクトリ
    ]
    
    # セキュリティ設定
    TOKEN_REFRESH_MARGIN_MINUTES = 5     # トークン期限の余裕時間（分）
    MAX_RETRY_ATTEMPTS = 3               # 認証リトライ回数
    
    # UI設定
    AUTH_BROWSER_TIMEOUT = 30            # ブラウザ起動タイムアウト（秒）
    
    @classmethod
    def get_client_secret_paths(cls) -> List[Path]:
        """
        client_secret.json の検索パス一覧を取得します
        
        Returns:
            List[Path]: 検索パスのリスト
        """
        paths = []
        for path_str in cls.CLIENT_SECRET_SEARCH_PATHS:
            path = Path(path_str).expanduser()
            paths.append(path)
        return paths
    
    @classmethod
    def validate_scopes(cls, requested_scopes: List[str]) -> bool:
        """
        要求されたスコープが有効かチェックします
        
        Args:
            requested_scopes: チェック対象のスコープリスト
            
        Returns:
            bool: すべてのスコープが有効な場合True
        """
        valid_scopes = set(cls.GMAIL_SCOPES)
        requested_scopes_set = set(requested_scopes)
        
        return requested_scopes_set.issubset(valid_scopes)
    
    @classmethod
    def get_minimal_scopes(cls) -> List[str]:
        """
        最小限必要なスコープを取得します
        
        Returns:
            List[str]: 最小スコープリスト
        """
        return [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send'
        ]
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """
        設定値を辞書形式で取得します
        
        Returns:
            Dict[str, Any]: 設定値辞書
        """
        return {
            'scopes': cls.GMAIL_SCOPES,
            'callback_port_range': cls.CALLBACK_PORT_RANGE,
            'default_callback_port': cls.DEFAULT_CALLBACK_PORT,
            'auth_timeout_seconds': cls.AUTH_TIMEOUT_SECONDS,
            'client_secret_search_paths': [str(p) for p in cls.get_client_secret_paths()],
            'token_refresh_margin_minutes': cls.TOKEN_REFRESH_MARGIN_MINUTES,
            'max_retry_attempts': cls.MAX_RETRY_ATTEMPTS,
            'auth_browser_timeout': cls.AUTH_BROWSER_TIMEOUT
        }


# OAuth2エラーメッセージ（日本語）
class OAuth2Messages:
    """
    OAuth2認証関連のメッセージクラス
    
    エラーメッセージと情報メッセージを日本語で提供します。
    """
    
    # 成功メッセージ
    AUTH_SUCCESS = "Gmail認証が完了しました。メールアカウントを使用できます。"
    TOKEN_REFRESHED = "アクセストークンを更新しました。"
    CONNECTION_TEST_SUCCESS = "Gmail接続が正常に確認できました。"
    
    # エラーメッセージ
    CLIENT_SECRET_NOT_FOUND = """
client_secret.jsonファイルが見つかりません。

以下の手順でGoogle Cloud Consoleから認証情報をダウンロードしてください：
1. Google Cloud Console (https://console.cloud.google.com/) にアクセス
2. プロジェクトを選択または作成
3. 「APIとサービス」→「認証情報」に移動
4. 「認証情報を作成」→「OAuth 2.0 クライアント ID」を選択
5. アプリケーションの種類で「デスクトップアプリケーション」を選択
6. 名前を入力して「作成」をクリック
7. ダウンロードボタンをクリックしてJSONファイルを保存
8. ファイル名を「client_secret.json」に変更してWabiMailフォルダに配置
"""
    
    CLIENT_SECRET_INVALID = "client_secret.jsonファイルの形式が正しくありません。Google Cloud Consoleから再ダウンロードしてください。"
    
    AUTH_CANCELLED = "認証がキャンセルされました。"
    AUTH_TIMEOUT = "認証がタイムアウトしました。再度お試しください。"
    AUTH_ERROR = "認証中にエラーが発生しました。"
    
    TOKEN_EXPIRED = "アクセストークンの有効期限が切れています。再認証が必要です。"
    TOKEN_INVALID = "保存されているトークンが無効です。再認証してください。"
    REFRESH_FAILED = "トークンの更新に失敗しました。再認証が必要です。"
    
    CONNECTION_FAILED = "Gmail接続に失敗しました。ネットワーク接続とアカウント設定を確認してください。"
    
    # 情報メッセージ
    AUTH_STARTING = "ブラウザでGmail認証ページを開きます..."
    AUTH_WAITING = "認証完了をお待ちください..."
    TOKEN_CHECKING = "保存されているトークンを確認中..."
    
    @classmethod
    def get_scope_description(cls, scope: str) -> str:
        """
        スコープの説明を取得します
        
        Args:
            scope: APIスコープ
            
        Returns:
            str: スコープの日本語説明
        """
        descriptions = {
            'https://www.googleapis.com/auth/gmail.readonly': 'メールの読み取り',
            'https://www.googleapis.com/auth/gmail.send': 'メールの送信',
            'https://www.googleapis.com/auth/gmail.compose': 'メールの作成',
            'https://www.googleapis.com/auth/gmail.modify': 'メールの変更（既読マーク等）'
        }
        return descriptions.get(scope, scope)
    
    @classmethod
    def format_scopes_list(cls, scopes: List[str]) -> str:
        """
        スコープリストを読みやすい形式にフォーマットします
        
        Args:
            scopes: スコープリスト
            
        Returns:
            str: フォーマットされたスコープ説明
        """
        descriptions = [cls.get_scope_description(scope) for scope in scopes]
        return "、".join(descriptions)


# デフォルト設定インスタンス
default_oauth2_config = OAuth2Config()
oauth2_messages = OAuth2Messages()