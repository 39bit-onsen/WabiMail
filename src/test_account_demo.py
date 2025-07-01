#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アカウント管理機能のデモンストレーション

WabiMailのアカウント管理機能を実際に試すためのデモスクリプトです。
Gmailアカウントやその他のアカウントを追加し、管理機能を確認します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mail.account import Account, AccountType, AuthType
from src.mail.account_manager import AccountManager
from src.config.app_config import AppConfig
from src.utils.logger import setup_logger


def main():
    """
    アカウント管理機能のデモンストレーション
    """
    # ログを設定
    logger = setup_logger()
    logger.info("🌸 WabiMail アカウント管理デモを開始します")
    
    try:
        # アプリケーション設定とアカウントマネージャーを初期化
        config = AppConfig()
        account_manager = AccountManager(config)
        
        print("\n" + "="*60)
        print("🌸 WabiMail アカウント管理デモ")
        print("="*60)
        
        # 既存アカウントの表示
        print(f"\n📊 現在のアカウント数: {account_manager.get_account_count()}")
        if account_manager.get_account_count() > 0:
            print("\n📧 既存のアカウント:")
            for account in account_manager.get_all_accounts():
                print(f"  • {account}")
        
        # デモ用のGmailアカウントを追加
        print("\n➕ デモ用Gmailアカウントを追加中...")
        gmail_account = Account(
            name="仕事用Gmail",
            email_address="work@gmail.com",
            account_type=AccountType.GMAIL,
            auth_type=AuthType.OAUTH2,
            display_name="山田太郎",
            signature="山田太郎\nWabiMail開発チーム"
        )
        
        if account_manager.add_account(gmail_account):
            print("  ✅ Gmailアカウントが追加されました")
        else:
            print("  ⚠️ Gmailアカウントの追加に失敗しました（既に存在する可能性があります）")
        
        # デモ用のIMAPアカウントを追加
        print("\n➕ デモ用IMAPアカウントを追加中...")
        imap_account = Account(
            name="プライベート用メール",
            email_address="private@example.com",
            account_type=AccountType.IMAP,
            auth_type=AuthType.PASSWORD,
            display_name="山田花子"
        )
        # IMAPアカウントの設定
        imap_account.settings.incoming_server = "imap.example.com"
        imap_account.settings.incoming_port = 993
        imap_account.settings.incoming_security = "SSL"
        imap_account.settings.outgoing_server = "smtp.example.com"
        imap_account.settings.outgoing_port = 587
        imap_account.settings.outgoing_security = "STARTTLS"
        
        if account_manager.add_account(imap_account):
            print("  ✅ IMAPアカウントが追加されました")
        else:
            print("  ⚠️ IMAPアカウントの追加に失敗しました（既に存在する可能性があります）")
        
        # 全アカウントの表示
        print(f"\n📧 全アカウント一覧 (総数: {account_manager.get_account_count()}):")
        for i, account in enumerate(account_manager.get_all_accounts(), 1):
            status_icon = "🟢" if account.is_active else "🔴"
            default_icon = "⭐" if account.is_default else "  "
            print(f"  {i}. {status_icon}{default_icon} {account}")
        
        # デフォルトアカウントの表示
        default_account = account_manager.get_default_account()
        if default_account:
            print(f"\n⭐ デフォルトアカウント: {default_account.name}")
        
        # アカウントタイプ別の統計
        print("\n📊 アカウントタイプ別統計:")
        for account_type in AccountType:
            accounts = account_manager.get_accounts_by_type(account_type)
            if accounts:
                print(f"  • {account_type.value.upper()}: {len(accounts)}個")
        
        # アカウント詳細統計
        stats = account_manager.get_account_statistics()
        print(f"\n📈 詳細統計:")
        print(f"  • 総アカウント数: {stats['total_accounts']}")
        print(f"  • 有効アカウント数: {stats['active_accounts']}")
        print(f"  • 無効アカウント数: {stats['inactive_accounts']}")
        print(f"  • デフォルトアカウント設定: {'あり' if stats['has_default'] else 'なし'}")
        
        # Gmail固有の機能デモ
        gmail_accounts = account_manager.get_accounts_by_type(AccountType.GMAIL)
        if gmail_accounts:
            print(f"\n🔍 Gmail アカウント詳細:")
            for gmail in gmail_accounts:
                print(f"  • 名前: {gmail.name}")
                print(f"  • メールアドレス: {gmail.email_address}")
                print(f"  • 認証方式: {gmail.auth_type.value}")
                print(f"  • サーバー設定:")
                print(f"    - 受信: {gmail.settings.incoming_server}:{gmail.settings.incoming_port} ({gmail.settings.incoming_security})")
                print(f"    - 送信: {gmail.settings.outgoing_server}:{gmail.settings.outgoing_port} ({gmail.settings.outgoing_security})")
                if gmail.signature:
                    print(f"  • 署名:\n{gmail.signature}")
        
        # アカウント検索のデモ
        print(f"\n🔍 アカウント検索デモ:")
        search_email = "work@gmail.com"
        found_account = account_manager.get_account_by_email(search_email)
        if found_account:
            print(f"  ✅ '{search_email}' が見つかりました: {found_account.name}")
        else:
            print(f"  ❌ '{search_email}' は見つかりませんでした")
        
        print(f"\n🌸 デモ完了！アカウント情報は {config.config_dir}/accounts/ に保存されています")
        print("="*60)
        
    except Exception as e:
        logger.error(f"デモ実行中にエラーが発生しました: {e}")
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()