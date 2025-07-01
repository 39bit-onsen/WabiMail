#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OAuth2認証機能のデモンストレーション

WabiMailのOAuth2認証機能（Gmail API連携）を実際に試すためのデモスクリプトです。
トークン管理、認証フロー、Gmail接続等の機能を確認します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.auth.oauth2_manager import GmailOAuth2Manager
from src.auth.token_storage import TokenStorage
from src.config.oauth2_config import OAuth2Config, OAuth2Messages
from src.mail.account import Account, AccountType, AuthType
from src.mail.account_manager import AccountManager
from src.utils.logger import setup_logger


def demo_token_storage():
    """
    トークンストレージのデモ
    """
    print("\n" + "="*60)
    print("🔐 トークンストレージ機能デモ")
    print("="*60)
    
    # TokenStorageインスタンスを作成
    token_storage = TokenStorage()
    
    print(f"\n📁 ストレージ情報:")
    storage_info = token_storage.get_storage_info()
    print(f"  保存ディレクトリ: {storage_info['storage_directory']}")
    print(f"  暗号化有効: {storage_info['encryption_enabled']}")
    print(f"  保存済みアカウント数: {storage_info['stored_account_count']}")
    
    # デモ用トークンデータ
    demo_account_id = "demo-gmail-account"
    demo_token_data = {
        'access_token': 'demo_access_token_1234567890',
        'refresh_token': 'demo_refresh_token_0987654321',
        'expires_in': 3600,
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': 'demo_client_id.apps.googleusercontent.com',
        'client_secret': 'demo_client_secret',
        'scopes': [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
    }
    
    print(f"\n💾 トークン保存デモ:")
    print(f"  アカウントID: {demo_account_id}")
    print(f"  スコープ数: {len(demo_token_data['scopes'])}")
    
    # トークンを保存
    success = token_storage.save_token(demo_account_id, demo_token_data)
    if success:
        print(f"  ✅ トークン保存成功")
        
        # トークンを読み込み
        loaded_token = token_storage.load_token(demo_account_id)
        if loaded_token:
            print(f"  ✅ トークン読み込み成功")
            print(f"    保存日時: {loaded_token.get('saved_at')}")
            print(f"    アクセストークン: {loaded_token['access_token'][:20]}...")
            print(f"    リフレッシュトークン: {loaded_token['refresh_token'][:20]}...")
            
            # 期限チェック
            is_expired = token_storage.is_token_expired(loaded_token)
            print(f"    期限状態: {'期限切れ' if is_expired else '有効'}")
        else:
            print(f"  ❌ トークン読み込み失敗")
    else:
        print(f"  ❌ トークン保存失敗")
    
    # 保存済みトークンリスト
    stored_tokens = token_storage.list_stored_tokens()
    print(f"\n📋 保存済みトークン:")
    if stored_tokens:
        for i, account_id in enumerate(stored_tokens, 1):
            print(f"  {i}. {account_id}")
    else:
        print(f"  保存済みトークンはありません")
    
    # クリーンアップ（デモ用トークンを削除）
    print(f"\n🧹 クリーンアップ:")
    if demo_account_id in stored_tokens:
        success = token_storage.delete_token(demo_account_id)
        print(f"  デモトークン削除: {'成功' if success else '失敗'}")


def demo_oauth2_config():
    """
    OAuth2設定のデモ
    """
    print("\n" + "="*60)
    print("⚙️ OAuth2設定機能デモ")
    print("="*60)
    
    print(f"\n🔧 基本設定:")
    print(f"  デフォルトポート: {OAuth2Config.DEFAULT_CALLBACK_PORT}")
    print(f"  ポート範囲: {OAuth2Config.CALLBACK_PORT_RANGE}")
    print(f"  認証タイムアウト: {OAuth2Config.AUTH_TIMEOUT_SECONDS}秒")
    print(f"  トークン更新余裕時間: {OAuth2Config.TOKEN_REFRESH_MARGIN_MINUTES}分")
    
    print(f"\n📜 Gmail APIスコープ:")
    for i, scope in enumerate(OAuth2Config.GMAIL_SCOPES, 1):
        description = OAuth2Messages.get_scope_description(scope)
        print(f"  {i}. {description}")
        print(f"     {scope}")
    
    print(f"\n🔍 client_secret.json 検索パス:")
    search_paths = OAuth2Config.get_client_secret_paths()
    for i, path in enumerate(search_paths, 1):
        exists = "✅" if path.exists() else "❌"
        print(f"  {i}. {exists} {path}")
    
    print(f"\n✅ スコープ検証デモ:")
    # 有効なスコープ
    valid_scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    is_valid = OAuth2Config.validate_scopes(valid_scopes)
    print(f"  有効スコープ: {is_valid}")
    
    # 無効なスコープ
    invalid_scopes = ['invalid_scope']
    is_valid = OAuth2Config.validate_scopes(invalid_scopes)
    print(f"  無効スコープ: {is_valid}")
    
    # 最小スコープ
    minimal_scopes = OAuth2Config.get_minimal_scopes()
    print(f"\n📋 最小必要スコープ:")
    for scope in minimal_scopes:
        description = OAuth2Messages.get_scope_description(scope)
        print(f"  • {description}")


def demo_oauth2_manager():
    """
    OAuth2マネージャーのデモ
    """
    print("\n" + "="*60)
    print("🔐 OAuth2マネージャー機能デモ")
    print("="*60)
    
    # OAuth2Managerインスタンスを作成
    oauth2_manager = GmailOAuth2Manager()
    
    print(f"\n🔧 マネージャー設定:")
    print(f"  対象スコープ数: {len(oauth2_manager.scopes)}")
    print(f"  client_secret.json利用可能: {oauth2_manager.is_client_secret_available()}")
    
    if oauth2_manager.client_secret_path:
        print(f"  client_secret.jsonパス: {oauth2_manager.client_secret_path}")
    else:
        print(f"  client_secret.jsonパス: 見つかりません")
        print(f"\n💡 client_secret.json設定方法:")
        print(OAuth2Messages.CLIENT_SECRET_NOT_FOUND)
    
    # デモ用アカウント
    demo_accounts = [
        "demo-gmail-1@gmail.com",
        "demo-gmail-2@gmail.com", 
        "demo-work@company.com"
    ]
    
    print(f"\n📧 認証状態チェック:")
    for account_id in demo_accounts:
        is_authenticated = oauth2_manager.is_authenticated(account_id)
        status = "✅ 認証済み" if is_authenticated else "❌ 未認証"
        print(f"  {account_id}: {status}")
        
        # 認証情報詳細
        auth_info = oauth2_manager.get_authentication_info(account_id)
        print(f"    トークン保存: {'あり' if auth_info['has_stored_token'] else 'なし'}")
        
        # Gmail接続テスト
        if is_authenticated:
            success, message = oauth2_manager.test_gmail_connection(account_id)
            print(f"    接続テスト: {'成功' if success else '失敗'} - {message}")
    
    print(f"\n🔄 OAuth2フローシミュレーション:")
    print(f"  ※実際の認証には client_secret.json が必要です")
    print(f"  1. ブラウザでGoogle認証ページを開く")
    print(f"  2. ユーザーがアクセス許可を承認")
    print(f"  3. 認証コードをローカルサーバーで受信")
    print(f"  4. アクセストークン・リフレッシュトークンを取得")
    print(f"  5. トークンを暗号化して安全に保存")
    print(f"  6. Gmail API使用可能状態になる")


def demo_account_integration():
    """
    アカウント統合のデモ
    """
    print("\n" + "="*60)
    print("📧 アカウント統合機能デモ")
    print("="*60)
    
    # OAuth2対応アカウントを作成
    oauth2_accounts = []
    
    # Gmail アカウント
    gmail_account = Account(
        name="メイン Gmail",
        email_address="main@gmail.com",
        account_type=AccountType.GMAIL
    )
    gmail_account.apply_preset_settings()
    oauth2_accounts.append(gmail_account)
    
    # 仕事用 Gmail
    work_gmail = Account(
        name="仕事用 Gmail",
        email_address="work@company.com",
        account_type=AccountType.GMAIL
    )
    work_gmail.apply_preset_settings()
    oauth2_accounts.append(work_gmail)
    
    # OAuth2設定済みIMAPアカウント
    oauth2_imap = Account(
        name="OAuth2対応プロバイダ",
        email_address="user@oauth2provider.com",
        account_type=AccountType.IMAP,
        auth_type=AuthType.OAUTH2
    )
    oauth2_imap.settings.incoming_server = "imap.oauth2provider.com"
    oauth2_imap.settings.incoming_port = 993
    oauth2_imap.settings.incoming_security = "SSL"
    oauth2_accounts.append(oauth2_imap)
    
    print(f"\n📋 OAuth2対応アカウント一覧:")
    for i, account in enumerate(oauth2_accounts, 1):
        print(f"\n  {i}. {account}")
        print(f"     OAuth2必要: {account.requires_oauth2()}")
        print(f"     認証方式: {account.get_authentication_display_name()}")
        
        # 必要スコープ
        scopes = account.get_oauth2_scope_requirements()
        if scopes:
            print(f"     必要スコープ:")
            for scope in scopes:
                description = OAuth2Messages.get_scope_description(scope)
                print(f"       • {description}")
        
        # 設定情報
        if account.account_type == AccountType.GMAIL:
            print(f"     受信サーバー: {account.settings.incoming_server}:{account.settings.incoming_port}")
            print(f"     送信サーバー: {account.settings.outgoing_server}:{account.settings.outgoing_port}")
    
    # 通常のパスワード認証アカウントとの比較
    print(f"\n🔒 認証方式比較:")
    
    password_account = Account(
        name="パスワード認証アカウント",
        email_address="user@example.com",
        account_type=AccountType.IMAP,
        auth_type=AuthType.PASSWORD
    )
    
    comparison_data = [
        ("認証方式", "OAuth2認証", "パスワード認証"),
        ("セキュリティ", "高（トークンベース）", "中（パスワード）"),
        ("設定の簡単さ", "簡単（自動設定）", "手動設定必要"),
        ("トークン管理", "自動更新", "なし"),
        ("API制限対応", "あり", "なし"),
        ("多要素認証", "対応", "プロバイダ依存")
    ]
    
    print(f"  {'項目':15} {'OAuth2':20} {'パスワード':15}")
    print(f"  {'-'*15} {'-'*20} {'-'*15}")
    for item, oauth2_val, password_val in comparison_data:
        print(f"  {item:15} {oauth2_val:20} {password_val:15}")


def demo_security_features():
    """
    セキュリティ機能のデモ
    """
    print("\n" + "="*60)
    print("🛡️ セキュリティ機能デモ")
    print("="*60)
    
    print(f"\n🔐 暗号化機能:")
    print(f"  • トークンデータの AES暗号化")
    print(f"  • プラットフォーム別セキュアストレージ")
    print(f"  • ファイルパーミッション制限（Unix系）")
    print(f"  • 暗号化キーの安全な管理")
    
    print(f"\n🔄 トークン管理:")
    print(f"  • 自動トークンリフレッシュ")
    print(f"  • 期限切れ検出（5分マージン）")
    print(f"  • 無効トークンの自動削除")
    print(f"  • バックアップ・復元機能")
    
    print(f"\n🌐 ネットワークセキュリティ:")
    print(f"  • HTTPS通信の強制")
    print(f"  • ローカルサーバーコールバック")
    print(f"  • CSRF攻撃対策")
    print(f"  • タイムアウト制御")
    
    print(f"\n📁 ストレージセキュリティ:")
    token_storage = TokenStorage()
    storage_info = token_storage.get_storage_info()
    
    print(f"  保存場所: {storage_info['storage_directory']}")
    print(f"  暗号化: {'有効' if storage_info['encryption_enabled'] else '無効'}")
    
    # プラットフォーム別の保存場所説明
    import os
    if os.name == 'nt':  # Windows
        print(f"  📂 Windows: %APPDATA%/WabiMail/tokens/")
        print(f"     ユーザー専用領域に保存")
    elif 'darwin' in os.uname().sysname.lower():  # macOS
        print(f"  📂 macOS: ~/Library/Application Support/WabiMail/tokens/")
        print(f"     システム推奨領域に保存")
    else:  # Linux
        print(f"  📂 Linux: ~/.local/share/WabiMail/tokens/")
        print(f"     XDG Base Directory準拠")
    
    print(f"\n⚠️ セキュリティ注意事項:")
    print(f"  • client_secret.jsonは適切に保護してください")
    print(f"  • トークンファイルを手動で編集しないでください")
    print(f"  • 定期的なトークン更新を確認してください")
    print(f"  • 不要なアカウントは削除してください")


def main():
    """
    OAuth2認証機能のデモンストレーション
    """
    # ログを設定
    logger = setup_logger()
    logger.info("🔐 WabiMail OAuth2認証機能デモを開始します")
    
    try:
        print("\n" + "="*60)
        print("🔐 WabiMail OAuth2認証機能デモ")
        print("="*60)
        print("🔒 Gmail API連携によるセキュアな認証システム")
        print("💾 暗号化トークンストレージ")
        print("🌸 侘び寂び設計思想による簡潔な認証フロー")
        
        # トークンストレージデモ
        demo_token_storage()
        
        # OAuth2設定デモ
        demo_oauth2_config()
        
        # OAuth2マネージャーデモ
        demo_oauth2_manager()
        
        # アカウント統合デモ
        demo_account_integration()
        
        # セキュリティ機能デモ
        demo_security_features()
        
        print(f"\n" + "="*60)
        print("🎯 デモのポイント")
        print("="*60)
        print("🔐 セキュア認証：OAuth2による安全なGmail連携")
        print("💾 暗号化保存：AES暗号化によるトークン保護")
        print("🔄 自動更新：トークンの自動リフレッシュ機能")
        print("🌸 侘び寂び：シンプルで美しい認証体験")
        print("📧 統合管理：複数Gmailアカウントの一元管理")
        print("🛡️ プライバシー：ローカル暗号化によるデータ保護")
        
        print(f"\n🔐 OAuth2認証機能実装完了！次はアカウント設定画面の実装に進みます")
        print("="*60)
        
    except Exception as e:
        logger.error(f"デモ実行中にエラーが発生しました: {e}")
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()