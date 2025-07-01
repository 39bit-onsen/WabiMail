#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メール通信機能のデモンストレーション

WabiMailのメール通信機能（IMAP、SMTP、POP）を実際に試すためのデモスクリプトです。
各種クライアントの生成、設定検証、接続テスト等を確認します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mail.account import Account, AccountType, AuthType
from src.mail.account_manager import AccountManager
from src.mail.mail_message import MailMessage, MessageFlag, MailAttachment
from src.mail.mail_client_factory import MailClientFactory, ClientType
from src.config.app_config import AppConfig
from src.utils.logger import setup_logger


def create_sample_message() -> MailMessage:
    """
    サンプルメールメッセージを作成します
    
    Returns:
        MailMessage: サンプルメッセージ
    """
    message = MailMessage(
        subject="🌸 WabiMail テストメッセージ - 侘び寂びの美しさ",
        sender="dev@wabimail.example.com",
        recipients=["user@example.com", "test@example.com"],
        cc_recipients=["cc@example.com"],
        body_text="""WabiMailからの贈り物

こんにちは。

WabiMail開発チームです。
このメールは、WabiMailのメール通信機能をテストするためのサンプルメッセージです。

🌸 侘び寂びの精神
- シンプルさの中に美しさを見出す
- 余計な装飾を排除した静かな体験
- 本質的な機能に集中した設計

WabiMailは、メールという日常的なコミュニケーションツールに
日本の美意識を取り入れることで、より心地よい体験を提供します。

どうぞよろしくお願いいたします。

--
WabiMail 開発チーム
🌸 静寂の中の美しさを追求して""",
        body_html="""<html>
<body style="font-family: 'Yu Gothic', 'Meiryo', sans-serif; color: #333; background: #fefefe;">
<h2 style="color: #666; border-bottom: 1px solid #eee;">🌸 WabiMailからの贈り物</h2>

<p>こんにちは。</p>

<p>WabiMail開発チームです。<br>
このメールは、WabiMailのメール通信機能をテストするためのサンプルメッセージです。</p>

<h3 style="color: #888;">🌸 侘び寂びの精神</h3>
<ul style="color: #555;">
<li>シンプルさの中に美しさを見出す</li>
<li>余計な装飾を排除した静かな体験</li>
<li>本質的な機能に集中した設計</li>
</ul>

<p style="background: #f9f9f9; padding: 15px; border-left: 3px solid #ddd;">
WabiMailは、メールという日常的なコミュニケーションツールに<br>
日本の美意識を取り入れることで、より心地よい体験を提供します。
</p>

<p>どうぞよろしくお願いいたします。</p>

<hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
<p style="color: #888; font-size: 0.9em;">
WabiMail 開発チーム<br>
🌸 静寂の中の美しさを追求して
</p>
</body>
</html>""",
        priority="normal"
    )
    
    # フラグを設定
    message.add_flag(MessageFlag.FLAGGED)  # 重要マーク
    
    # サンプル添付ファイル情報
    attachment1 = MailAttachment(
        filename="wabimail_guide.pdf",
        content_type="application/pdf",
        size=2048,
        is_inline=False
    )
    
    attachment2 = MailAttachment(
        filename="cherry_blossom.jpg",
        content_type="image/jpeg",
        size=1024,
        is_inline=True,
        content_id="<cherry@wabimail>"
    )
    
    message.attachments.extend([attachment1, attachment2])
    
    return message


def demo_message_operations():
    """
    メールメッセージ操作のデモ
    """
    print("\n" + "="*60)
    print("📧 メールメッセージ操作デモ")
    print("="*60)
    
    # サンプルメッセージを作成
    message = create_sample_message()
    
    print(f"\n📨 メッセージ基本情報:")
    print(f"  件名: {message.subject}")
    print(f"  送信者: {message.sender}")
    print(f"  受信者: {', '.join(message.recipients)}")
    print(f"  CC: {', '.join(message.cc_recipients)}")
    print(f"  優先度: {message.priority}")
    print(f"  メッセージID: {message.message_id}")
    
    print(f"\n📎 添付ファイル情報:")
    if message.has_attachments():
        print(f"  添付ファイル数: {message.get_attachment_count()}")
        for i, attachment in enumerate(message.attachments, 1):
            print(f"  {i}. {attachment}")
    else:
        print("  添付ファイルなし")
    
    print(f"\n🏷️ メッセージフラグ:")
    flags_status = [
        f"既読: {'✅' if message.is_read() else '❌'}",
        f"重要: {'⭐' if message.is_flagged() else '❌'}",
        f"返信済み: {'✅' if message.has_flag(MessageFlag.ANSWERED) else '❌'}"
    ]
    print(f"  {' | '.join(flags_status)}")
    
    print(f"\n📝 本文プレビュー:")
    preview = message.get_body_preview(150)
    print(f"  {preview}")
    
    print(f"\n📊 文字列表現:")
    print(f"  {message}")
    
    # フラグ操作デモ
    print(f"\n🔄 フラグ操作デモ:")
    print(f"  元の状態: {message}")
    
    message.mark_as_read()
    print(f"  既読マーク後: {message}")
    
    message.add_flag(MessageFlag.ANSWERED)
    print(f"  返信済みマーク後: {message}")


def demo_client_factory():
    """
    クライアントファクトリーのデモ
    """
    print("\n" + "="*60)
    print("🏭 メールクライアントファクトリーデモ")
    print("="*60)
    
    # 各種アカウントを準備
    accounts = []
    
    # Gmailアカウント
    gmail_account = Account(
        name="仕事用Gmail",
        email_address="work@gmail.com",
        account_type=AccountType.GMAIL,
        auth_type=AuthType.OAUTH2
    )
    gmail_account.apply_preset_settings()
    accounts.append(("Gmail", gmail_account))
    
    # IMAPアカウント
    imap_account = Account(
        name="プライベートIMAP",
        email_address="private@example.com",
        account_type=AccountType.IMAP,
        auth_type=AuthType.PASSWORD
    )
    imap_account.settings.incoming_server = "imap.example.com"
    imap_account.settings.incoming_port = 993
    imap_account.settings.incoming_security = "SSL"
    imap_account.settings.outgoing_server = "smtp.example.com"
    imap_account.settings.outgoing_port = 587
    imap_account.settings.outgoing_security = "STARTTLS"
    accounts.append(("IMAP", imap_account))
    
    # POP3アカウント
    pop_account = Account(
        name="レガシーPOP3",
        email_address="legacy@example.com",
        account_type=AccountType.POP3,
        auth_type=AuthType.PASSWORD
    )
    pop_account.settings.incoming_server = "pop.example.com"
    pop_account.settings.incoming_port = 995
    pop_account.settings.incoming_security = "SSL"
    pop_account.settings.outgoing_server = "smtp.example.com"
    pop_account.settings.outgoing_port = 25
    pop_account.settings.outgoing_security = "NONE"
    accounts.append(("POP3", pop_account))
    
    # 各アカウントでクライアント生成をテスト
    for account_type, account in accounts:
        print(f"\n📧 {account_type}アカウント: {account.name}")
        print(f"  メールアドレス: {account.email_address}")
        
        # サポートされているクライアントタイプを確認
        supported_types = MailClientFactory.get_supported_client_types(account)
        print(f"  サポートクライアント: {[t.value.upper() for t in supported_types]}")
        
        # 受信クライアント生成
        receive_client = MailClientFactory.create_receive_client(account)
        if receive_client:
            client_type = type(receive_client).__name__
            print(f"  ✅ 受信クライアント: {client_type}")
        else:
            print(f"  ❌ 受信クライアント生成失敗")
        
        # 送信クライアント生成
        send_client = MailClientFactory.create_send_client(account)
        if send_client:
            client_type = type(send_client).__name__
            print(f"  ✅ 送信クライアント: {client_type}")
        else:
            print(f"  ❌ 送信クライアント生成失敗")
        
        # 接続設定の詳細表示
        print(f"  📡 接続設定:")
        print(f"    受信: {account.settings.incoming_server}:{account.settings.incoming_port} ({account.settings.incoming_security})")
        print(f"    送信: {account.settings.outgoing_server}:{account.settings.outgoing_port} ({account.settings.outgoing_security})")


def demo_client_connection_test():
    """
    クライアント接続テストのデモ
    """
    print("\n" + "="*60)
    print("🔌 接続テストデモ")
    print("="*60)
    
    # Gmailアカウントでテスト
    gmail_account = Account(
        name="テスト用Gmail",
        email_address="test@gmail.com",
        account_type=AccountType.GMAIL
    )
    gmail_account.apply_preset_settings()
    
    print(f"\n📧 接続テスト対象: {gmail_account.email_address}")
    print(f"  アカウントタイプ: {gmail_account.account_type.value}")
    print(f"  認証方式: {gmail_account.auth_type.value}")
    
    # ファクトリーを使用した総合接続テスト
    print(f"\n🧪 総合接続テスト実行中...")
    success, message, details = MailClientFactory.test_account_connection(gmail_account)
    
    print(f"\n📊 テスト結果:")
    print(f"  全体結果: {'✅ 成功' if success else '❌ 失敗'}")
    print(f"  詳細: {message}")
    
    print(f"\n📋 詳細テスト結果:")
    for test_type, result in details.items():
        status_icon = "✅" if result['success'] else "❌"
        client_type = result.get('client_type', '').upper()
        test_message = result.get('message', 'メッセージなし')
        print(f"  {status_icon} {test_type}({client_type}): {test_message}")
    
    # 注意事項の表示
    print(f"\n💡 注意事項:")
    print(f"  このデモでは実際の認証は行われません。")
    print(f"  実際の接続には適切な認証情報が必要です。")
    print(f"  現在はクライアント生成と設定検証のテストを実行しています。")


def main():
    """
    メール通信機能のデモンストレーション
    """
    # ログを設定
    logger = setup_logger()
    logger.info("🌸 WabiMail メール通信機能デモを開始します")
    
    try:
        print("\n" + "="*60)
        print("🌸 WabiMail メール通信機能デモ")
        print("="*60)
        print("📨 IMAP・SMTP・POP3クライアントとメッセージ管理機能")
        print("🏭 ファクトリーパターンによる統一されたクライアント管理")
        print("🔌 接続テストと設定検証機能")
        
        # メッセージ操作デモ
        demo_message_operations()
        
        # クライアントファクトリーデモ
        demo_client_factory()
        
        # 接続テストデモ
        demo_client_connection_test()
        
        print(f"\n" + "="*60)
        print("🎯 デモのポイント")
        print("="*60)
        print("✨ 統一されたインターフェース: すべてのプロトコルを同じ方法で操作")
        print("🏭 ファクトリーパターン: アカウント設定に応じた自動クライアント選択") 
        print("🔍 設定検証機能: 無効な設定での早期エラー検出")
        print("📧 リッチなメッセージ表現: フラグ、添付ファイル、プレビュー対応")
        print("🌸 侘び寂び設計: シンプルで美しいAPI設計")
        
        print(f"\n🌸 デモ完了！メール通信機能の基盤が整いました")
        print("="*60)
        
    except Exception as e:
        logger.error(f"デモ実行中にエラーが発生しました: {e}")
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()