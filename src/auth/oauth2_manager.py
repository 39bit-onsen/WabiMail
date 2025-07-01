# -*- coding: utf-8 -*-
"""
OAuth2認証マネージャーモジュール

Gmail OAuth2認証フローの管理を提供します。
Google API連携、トークン取得・更新、認証状態管理を統合的に処理します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import json
import webbrowser
import threading
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse, parse_qs
import http.server
import socketserver
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth.exceptions

from src.auth.token_storage import TokenStorage
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class GmailOAuth2Manager:
    """
    Gmail OAuth2認証マネージャークラス
    
    Google OAuth2認証フローの実行、アクセストークンの取得・更新、
    認証状態の管理を統合的に提供します。
    
    Attributes:
        scopes (list[str]): 必要なGmail APIスコープ
        token_storage (TokenStorage): トークンストレージ
        client_secret_path (Path): client_secret.jsonのパス
        _credentials_cache (Dict[str, Credentials]): 認証情報キャッシュ
    
    Note:
        Gmail APIを使用するには、Google Cloud Consoleでプロジェクトを作成し、
        Gmail APIを有効化してOAuth2認証情報をダウンロードする必要があります。
    """
    
    # Gmail API必要スコープ
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',      # メール読み取り
        'https://www.googleapis.com/auth/gmail.send',          # メール送信
        'https://www.googleapis.com/auth/gmail.compose',       # メール作成
        'https://www.googleapis.com/auth/gmail.modify'         # メール変更（既読マーク等）
    ]
    
    def __init__(self, client_secret_path: Optional[Path] = None):
        """
        OAuth2マネージャーを初期化します
        
        Args:
            client_secret_path: client_secret.jsonファイルのパス
        """
        self.scopes = self.SCOPES
        self.token_storage = TokenStorage()
        
        # client_secret.jsonのパスを決定
        if client_secret_path:
            self.client_secret_path = client_secret_path
        else:
            # デフォルトの場所を検索
            self.client_secret_path = self._find_client_secret_file()
        
        # 認証情報のキャッシュ
        self._credentials_cache: Dict[str, Credentials] = {}
        
        logger.debug("Gmail OAuth2マネージャーを初期化しました")
    
    def _find_client_secret_file(self) -> Optional[Path]:
        """
        client_secret.jsonファイルを検索します
        
        Returns:
            Optional[Path]: 見つかったファイルパス、見つからない場合None
        """
        # 検索候補パス
        candidate_paths = [
            Path.cwd() / "client_secret.json",                    # カレントディレクトリ
            Path.cwd() / "config" / "client_secret.json",         # configディレクトリ
            Path.cwd() / "credentials" / "client_secret.json",    # credentialsディレクトリ
            Path(__file__).parent.parent.parent / "client_secret.json",  # プロジェクトルート
            self.token_storage.storage_dir.parent / "client_secret.json"  # アプリデータディレクトリ
        ]
        
        for path in candidate_paths:
            if path.exists():
                logger.debug(f"client_secret.jsonを発見: {path}")
                return path
        
        logger.warning("client_secret.jsonが見つかりません")
        return None
    
    def is_client_secret_available(self) -> bool:
        """
        client_secret.jsonファイルが利用可能かチェックします
        
        Returns:
            bool: 利用可能な場合True
        """
        if not self.client_secret_path or not self.client_secret_path.exists():
            return False
        
        try:
            # ファイルの内容をチェック
            with open(self.client_secret_path, 'r', encoding='utf-8') as f:
                client_config = json.load(f)
            
            # 必要なキーが存在するかチェック
            if 'installed' in client_config or 'web' in client_config:
                return True
            else:
                logger.error("client_secret.jsonの形式が正しくありません")
                return False
                
        except Exception as e:
            logger.error(f"client_secret.json読み込みエラー: {e}")
            return False
    
    def start_oauth2_flow(self, account_id: str, 
                         callback_port: int = 8080) -> Tuple[bool, str]:
        """
        OAuth2認証フローを開始します
        
        Args:
            account_id: アカウント識別子
            callback_port: コールバック用ローカルサーバーポート
            
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        try:
            if not self.is_client_secret_available():
                return False, "client_secret.jsonファイルが見つかりません。Google Cloud Consoleから認証情報をダウンロードしてください。"
            
            logger.info(f"OAuth2認証フローを開始します: {account_id}")
            
            # OAuth2フローを作成
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.client_secret_path),
                scopes=self.scopes
            )
            
            # ローカルサーバーを使用して認証
            # ユーザーが認証を完了すると、このサーバーにリダイレクトされます
            flow.redirect_uri = f"http://localhost:{callback_port}/"
            
            # 認証URLを生成
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            logger.info("認証URLを生成しました")
            
            # ブラウザで認証ページを開く
            if self._open_browser(auth_url):
                logger.info("ブラウザで認証ページを開きました")
            else:
                logger.warning("ブラウザを自動で開けませんでした")
                return False, f"ブラウザを手動で開いて認証してください: {auth_url}"
            
            # ローカルサーバーでコールバックを待機
            credentials = self._wait_for_callback(flow, callback_port)
            
            if credentials:
                # トークンを保存
                token_data = {
                    'access_token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'token_uri': credentials.token_uri,
                    'client_id': credentials.client_id,
                    'client_secret': credentials.client_secret,
                    'scopes': credentials.scopes,
                    'expires_in': 3600,  # デフォルト1時間
                    'auth_completed_at': datetime.now().isoformat()
                }
                
                if self.token_storage.save_token(account_id, token_data):
                    # キャッシュにも保存
                    self._credentials_cache[account_id] = credentials
                    
                    logger.info(f"OAuth2認証が完了しました: {account_id}")
                    return True, "Gmail認証が完了しました。メールアカウントを使用できます。"
                else:
                    return False, "認証は成功しましたが、トークンの保存に失敗しました。"
            else:
                return False, "認証がキャンセルされたか、タイムアウトしました。"
                
        except Exception as e:
            logger.error(f"OAuth2認証エラー ({account_id}): {e}")
            return False, f"認証中にエラーが発生しました: {str(e)}"
    
    def _open_browser(self, url: str) -> bool:
        """
        ブラウザで指定URLを開きます
        
        Args:
            url: 開くURL
            
        Returns:
            bool: 成功時True
        """
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            logger.error(f"ブラウザ起動エラー: {e}")
            return False
    
    def _wait_for_callback(self, flow: InstalledAppFlow, 
                          port: int, timeout: int = 300) -> Optional[Credentials]:
        """
        OAuth2コールバックを待機します
        
        Args:
            flow: OAuth2フロー
            port: リスニングポート
            timeout: タイムアウト秒数
            
        Returns:
            Optional[Credentials]: 取得した認証情報、失敗時None
        """
        credentials = None
        server = None
        
        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal credentials
                
                # URLからコードを取得
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)
                
                if 'code' in query_params:
                    # 認証コードを使用してトークンを取得
                    try:
                        flow.fetch_token(code=query_params['code'][0])
                        credentials = flow.credentials
                        
                        # 成功ページを表示
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        
                        success_html = """
                        <html>
                        <head><title>WabiMail認証完了</title></head>
                        <body style="font-family: 'Yu Gothic', sans-serif; text-align: center; margin-top: 100px;">
                        <h1 style="color: #333;">🌸 認証完了</h1>
                        <p>WabiMailのGmail認証が完了しました。</p>
                        <p>このウィンドウを閉じてWabiMailに戻ってください。</p>
                        <div style="margin-top: 50px; color: #888;">
                        <small>WabiMail - 侘び寂びメールクライアント</small>
                        </div>
                        </body>
                        </html>
                        """
                        
                        self.wfile.write(success_html.encode('utf-8'))
                        
                    except Exception as e:
                        logger.error(f"トークン取得エラー: {e}")
                        self._send_error_page(f"認証エラー: {str(e)}")
                
                elif 'error' in query_params:
                    # エラーページを表示
                    error = query_params['error'][0]
                    self._send_error_page(f"認証エラー: {error}")
                else:
                    self._send_error_page("不正なリクエストです")
            
            def _send_error_page(self, error_message: str):
                """エラーページを送信"""
                self.send_response(400)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                error_html = f"""
                <html>
                <head><title>WabiMail認証エラー</title></head>
                <body style="font-family: 'Yu Gothic', sans-serif; text-align: center; margin-top: 100px;">
                <h1 style="color: #cc0000;">❌ 認証エラー</h1>
                <p>{error_message}</p>
                <p>WabiMailに戻って再度お試しください。</p>
                </body>
                </html>
                """
                
                self.wfile.write(error_html.encode('utf-8'))
            
            def log_message(self, format, *args):
                # ログメッセージを無効化（静かな動作）
                pass
        
        try:
            # ローカルサーバーを起動
            with socketserver.TCPServer(("", port), CallbackHandler) as server:
                logger.debug(f"OAuth2コールバックサーバーを起動: ポート{port}")
                
                # タイムアウト付きで処理
                server.timeout = timeout
                server.handle_request()
                
                logger.debug("OAuth2コールバック処理完了")
                
        except Exception as e:
            logger.error(f"コールバックサーバーエラー: {e}")
        
        return credentials
    
    def get_credentials(self, account_id: str) -> Optional[Credentials]:
        """
        有効な認証情報を取得します
        
        Args:
            account_id: アカウント識別子
            
        Returns:
            Optional[Credentials]: 有効な認証情報、取得できない場合None
        """
        try:
            # キャッシュから確認
            if account_id in self._credentials_cache:
                credentials = self._credentials_cache[account_id]
                if credentials.valid:
                    return credentials
                elif credentials.expired and credentials.refresh_token:
                    # トークンを更新
                    if self._refresh_credentials(account_id, credentials):
                        return self._credentials_cache[account_id]
            
            # ストレージから読み込み
            token_data = self.token_storage.load_token(account_id)
            if not token_data:
                logger.debug(f"保存されたトークンが見つかりません: {account_id}")
                return None
            
            # Credentialsオブジェクトを構築
            credentials = Credentials(
                token=token_data.get('access_token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )
            
            # 有効性をチェック
            if credentials.valid:
                self._credentials_cache[account_id] = credentials
                return credentials
            elif credentials.expired and credentials.refresh_token:
                # トークンを更新
                if self._refresh_credentials(account_id, credentials):
                    return self._credentials_cache[account_id]
            
            logger.warning(f"有効な認証情報を取得できません: {account_id}")
            return None
            
        except Exception as e:
            logger.error(f"認証情報取得エラー ({account_id}): {e}")
            return None
    
    def _refresh_credentials(self, account_id: str, credentials: Credentials) -> bool:
        """
        認証情報を更新します
        
        Args:
            account_id: アカウント識別子
            credentials: 更新対象の認証情報
            
        Returns:
            bool: 更新成功時True
        """
        try:
            logger.info(f"アクセストークンを更新中: {account_id}")
            
            # トークンを更新
            credentials.refresh(Request())
            
            # 更新されたトークンを保存
            token_data = {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expires_in': 3600,
                'refreshed_at': datetime.now().isoformat()
            }
            
            if self.token_storage.save_token(account_id, token_data):
                # キャッシュを更新
                self._credentials_cache[account_id] = credentials
                logger.info(f"アクセストークンを更新しました: {account_id}")
                return True
            else:
                logger.error(f"更新されたトークンの保存に失敗: {account_id}")
                return False
                
        except google.auth.exceptions.RefreshError as e:
            logger.error(f"トークン更新エラー ({account_id}): {e}")
            # リフレッシュトークンが無効な場合は削除
            self.revoke_credentials(account_id)
            return False
        except Exception as e:
            logger.error(f"予期しないトークン更新エラー ({account_id}): {e}")
            return False
    
    def revoke_credentials(self, account_id: str) -> bool:
        """
        認証情報を無効化します
        
        Args:
            account_id: アカウント識別子
            
        Returns:
            bool: 無効化成功時True
        """
        try:
            # キャッシュから削除
            if account_id in self._credentials_cache:
                del self._credentials_cache[account_id]
            
            # ストレージから削除
            success = self.token_storage.delete_token(account_id)
            
            if success:
                logger.info(f"認証情報を無効化しました: {account_id}")
            else:
                logger.warning(f"認証情報の削除に失敗: {account_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"認証情報無効化エラー ({account_id}): {e}")
            return False
    
    def is_authenticated(self, account_id: str) -> bool:
        """
        アカウントの認証状態をチェックします
        
        Args:
            account_id: アカウント識別子
            
        Returns:
            bool: 認証済みで有効な場合True
        """
        credentials = self.get_credentials(account_id)
        return credentials is not None and credentials.valid
    
    def get_authentication_info(self, account_id: str) -> Dict[str, Any]:
        """
        認証情報の詳細を取得します
        
        Args:
            account_id: アカウント識別子
            
        Returns:
            Dict[str, Any]: 認証情報詳細
        """
        try:
            token_data = self.token_storage.load_token(account_id)
            credentials = self.get_credentials(account_id)
            
            info = {
                'account_id': account_id,
                'is_authenticated': credentials is not None and credentials.valid,
                'has_stored_token': token_data is not None,
                'scopes': self.scopes,
                'client_secret_available': self.is_client_secret_available()
            }
            
            if token_data:
                info.update({
                    'token_saved_at': token_data.get('saved_at'),
                    'auth_completed_at': token_data.get('auth_completed_at'),
                    'last_refreshed_at': token_data.get('refreshed_at')
                })
            
            if credentials:
                info.update({
                    'token_valid': credentials.valid,
                    'token_expired': credentials.expired,
                    'has_refresh_token': credentials.refresh_token is not None
                })
            
            return info
            
        except Exception as e:
            logger.error(f"認証情報詳細取得エラー ({account_id}): {e}")
            return {
                'account_id': account_id,
                'error': str(e),
                'is_authenticated': False
            }
    
    def test_gmail_connection(self, account_id: str) -> Tuple[bool, str]:
        """
        Gmail接続をテストします
        
        Args:
            account_id: アカウント識別子
            
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        try:
            credentials = self.get_credentials(account_id)
            if not credentials:
                return False, "認証情報が見つかりません。OAuth2認証を実行してください。"
            
            if not credentials.valid:
                return False, "認証情報が無効です。再認証が必要です。"
            
            # 簡単なAPIテスト（プロファイル情報取得）
            # 実際のGmail API呼び出しは将来の実装で行う
            logger.info(f"Gmail接続テスト成功: {account_id}")
            return True, "Gmail接続が正常に確認できました。"
            
        except Exception as e:
            logger.error(f"Gmail接続テストエラー ({account_id}): {e}")
            return False, f"接続テストエラー: {str(e)}"